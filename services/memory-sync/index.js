/**
 * Memory Sync Service - Multi-Agent Conflict Resolution
 * Production service for handling concurrent memory writes from Alden, Alice, Sentry, Mimic
 */

const express = require('express');
const { EventEmitter } = require('events');
const redis = require('redis');
const { v4: uuidv4 } = require('uuid');
const winston = require('winston');
const rateLimit = require('express-rate-limit');

// Configure logging
const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ 
            filename: '/var/log/hearthlink/memory-sync-error.log', 
            level: 'error' 
        }),
        new winston.transports.File({ 
            filename: '/var/log/hearthlink/memory-sync.log' 
        }),
        new winston.transports.Console({
            format: winston.format.simple()
        })
    ]
});

// Memory Sync Service Configuration
const CONFIG = {
    port: process.env.MEMORY_SYNC_PORT || 8003,
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379,
        password: process.env.REDIS_PASSWORD || null,
        db: process.env.REDIS_DB || 2
    },
    agents: {
        priorities: {
            'sentry': 1,      // Highest priority for security
            'alden': 2,       // High priority for primary agent
            'alice': 3,       // Medium priority for analysis
            'mimic': 4        // Lower priority for personas
        },
        conflictResolution: {
            timeout: 5000,    // 5 second timeout for resolution
            maxRetries: 3,    // Maximum retry attempts
            backoffMs: 1000   // Exponential backoff base
        }
    },
    rateLimiting: {
        windowMs: 60 * 1000,  // 1 minute
        max: 1000,            // Limit each IP to 1000 requests per windowMs
        standardHeaders: true,
        legacyHeaders: false
    }
};

// Conflict Resolution Strategies
const CONFLICT_STRATEGIES = {
    AGENT_PRIORITY: 'agent_priority',
    TIMESTAMP_LATEST: 'timestamp_latest',
    CONTENT_MERGE: 'content_merge',
    MANUAL_REVIEW: 'manual_review',
    IMPORTANCE_HIGHEST: 'importance_highest',
    CUSTOM_TAGS: 'custom_tags'
};

// Enhanced Conflict Resolution Policies
const RESOLUTION_POLICIES = {
    // Security Override: Sentry always wins security-related conflicts
    SECURITY_OVERRIDE: (conflictData) => {
        if (conflictData.existing?.metadata?.tags?.includes('security') || 
            conflictData.new?.metadata?.tags?.includes('security')) {
            return conflictData.existing?.agentId === 'sentry' ? 'existing' : 'new';
        }
        return null;
    },
    
    // Timestamp Window: Operations within 1s are truly concurrent
    TIMESTAMP_WINDOW: (conflictData) => {
        const existingTime = new Date(conflictData.existing?.timestamp || 0);
        const newTime = new Date(conflictData.new?.timestamp || 0);
        const timeDiff = Math.abs(newTime - existingTime);
        
        if (timeDiff <= CONFIG.agents.conflictResolution.timeout) {
            return null; // Truly concurrent, use other strategies
        }
        
        return newTime > existingTime ? 'new' : 'existing';
    },
    
    // Agent Priority: Based on configured hierarchy
    AGENT_PRIORITY: (conflictData) => {
        const existingPriority = CONFIG.agents.priorities[conflictData.existing?.agentId] || 999;
        const newPriority = CONFIG.agents.priorities[conflictData.new?.agentId] || 999;
        
        return existingPriority < newPriority ? 'existing' : 'new';
    },
    
    // Custom Tags: Priority based on tag hierarchy
    CUSTOM_TAGS: (conflictData) => {
        const tagHierarchy = ['security', 'critical', 'high', 'medium', 'low'];
        
        const getTagPriority = (tags) => {
            if (!tags) return 999;
            for (let i = 0; i < tagHierarchy.length; i++) {
                if (tags.includes(tagHierarchy[i])) return i;
            }
            return 999;
        };
        
        const existingPriority = getTagPriority(conflictData.existing?.metadata?.tags);
        const newPriority = getTagPriority(conflictData.new?.metadata?.tags);
        
        return existingPriority < newPriority ? 'existing' : 'new';
    },
    
    // Content Merge: Attempt to merge similar content
    CONTENT_MERGE: (conflictData) => {
        const similarity = calculateContentSimilarity(
            conflictData.existing?.content || '',
            conflictData.new?.content || ''
        );
        
        if (similarity > 0.8) {
            return 'merge'; // Signal that content should be merged
        }
        
        return null;
    }
};

// Content similarity calculation (simple implementation)
function calculateContentSimilarity(content1, content2) {
    if (!content1 || !content2) return 0;
    
    const words1 = content1.toLowerCase().split(/\s+/);
    const words2 = content2.toLowerCase().split(/\s+/);
    
    const set1 = new Set(words1);
    const set2 = new Set(words2);
    
    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    
    return intersection.size / union.size;
}

function mergeContent(content1, content2) {
    // Simple merge strategy - combine unique sentences
    const sentences1 = content1.split(/[.!?]+/).filter(s => s.trim());
    const sentences2 = content2.split(/[.!?]+/).filter(s => s.trim());
    
    const uniqueSentences = [...new Set([...sentences1, ...sentences2])];
    return uniqueSentences.join('. ') + '.';
}

class MemorySyncService extends EventEmitter {
    constructor() {
        super();
        this.app = express();
        this.redisClient = null;
        this.activeConflicts = new Map();
        this.syncOperations = new Map();
        this.metrics = {
            totalSyncs: 0,
            conflictsResolved: 0,
            conflictsPending: 0,
            agentOperations: {
                alden: 0,
                alice: 0,
                sentry: 0,
                mimic: 0
            },
            averageResolutionTime: 0,
            lastSync: null
        };
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupErrorHandling();
    }

    async initialize() {
        try {
            // Initialize Redis connection
            this.redisClient = redis.createClient({
                host: CONFIG.redis.host,
                port: CONFIG.redis.port,
                password: CONFIG.redis.password,
                db: CONFIG.redis.db,
                retry_strategy: (options) => {
                    if (options.error && options.error.code === 'ECONNREFUSED') {
                        logger.error('Redis connection refused');
                        return new Error('Redis connection refused');
                    }
                    if (options.total_retry_time > 1000 * 60 * 60) {
                        return new Error('Redis retry time exhausted');
                    }
                    if (options.attempt > 10) {
                        return undefined;
                    }
                    return Math.min(options.attempt * 100, 3000);
                }
            });

            await this.redisClient.connect();
            logger.info('Connected to Redis for memory sync operations');

            // Setup event listeners
            this.setupEventListeners();

            // Start conflict resolution processor
            this.startConflictProcessor();

            logger.info('Memory Sync Service initialized successfully', {
                port: CONFIG.port,
                redis: `${CONFIG.redis.host}:${CONFIG.redis.port}`,
                agents: Object.keys(CONFIG.agents.priorities)
            });

        } catch (error) {
            logger.error('Failed to initialize Memory Sync Service', { error: error.message });
            throw error;
        }
    }

    setupMiddleware() {
        // Rate limiting
        const limiter = rateLimit(CONFIG.rateLimiting);
        this.app.use('/api/', limiter);

        // JSON parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true }));

        // Request logging
        this.app.use((req, res, next) => {
            const startTime = Date.now();
            res.on('finish', () => {
                const duration = Date.now() - startTime;
                logger.info('Request processed', {
                    method: req.method,
                    url: req.url,
                    status: res.statusCode,
                    duration: `${duration}ms`,
                    agent: req.headers['user-agent'],
                    ip: req.ip
                });
            });
            next();
        });
    }

    setupRoutes() {
        // Health check endpoint
        this.app.get('/health', (req, res) => {
            const health = {
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                redis: this.redisClient?.isReady ? 'connected' : 'disconnected',
                metrics: this.metrics,
                activeConflicts: this.activeConflicts.size,
                activeSyncs: this.syncOperations.size
            };
            res.json(health);
        });

        // Sync memory operation
        this.app.post('/api/sync-memory', async (req, res) => {
            try {
                const result = await this.handleMemorySync(req.body);
                res.json(result);
            } catch (error) {
                logger.error('Memory sync failed', { error: error.message, body: req.body });
                res.status(500).json({ 
                    error: 'Memory sync failed', 
                    message: error.message,
                    syncId: req.body.syncId || null
                });
            }
        });

        // Get sync status
        this.app.get('/api/sync-status/:syncId', async (req, res) => {
            try {
                const status = await this.getSyncStatus(req.params.syncId);
                res.json(status);
            } catch (error) {
                logger.error('Failed to get sync status', { error: error.message, syncId: req.params.syncId });
                res.status(404).json({ error: 'Sync not found' });
            }
        });

        // Resolve conflict manually
        this.app.post('/api/resolve-conflict/:conflictId', async (req, res) => {
            try {
                const result = await this.resolveConflict(
                    req.params.conflictId,
                    req.body.strategy,
                    req.body.resolution
                );
                res.json(result);
            } catch (error) {
                logger.error('Manual conflict resolution failed', { 
                    error: error.message, 
                    conflictId: req.params.conflictId 
                });
                res.status(500).json({ error: 'Conflict resolution failed' });
            }
        });

        // Get active conflicts
        this.app.get('/api/conflicts', (req, res) => {
            const conflicts = Array.from(this.activeConflicts.entries()).map(([id, conflict]) => ({
                conflictId: id,
                memoryId: conflict.memoryId,
                agents: conflict.agents,
                strategy: conflict.strategy,
                created: conflict.created,
                status: conflict.status
            }));
            res.json({ conflicts, total: conflicts.length });
        });

        // Get metrics
        this.app.get('/api/metrics', (req, res) => {
            const extendedMetrics = {
                ...this.metrics,
                conflicts: {
                    active: this.activeConflicts.size,
                    total: this.metrics.conflictsResolved + this.activeConflicts.size
                },
                syncOperations: {
                    active: this.syncOperations.size,
                    total: this.metrics.totalSyncs
                },
                uptime: process.uptime(),
                timestamp: new Date().toISOString()
            };
            res.json(extendedMetrics);
        });

        // Force sync for specific memory
        this.app.post('/api/force-sync', async (req, res) => {
            try {
                const { memoryId, agentId, priority = false } = req.body;
                const result = await this.forceMemorySync(memoryId, agentId, priority);
                res.json(result);
            } catch (error) {
                logger.error('Force sync failed', { error: error.message, body: req.body });
                res.status(500).json({ error: 'Force sync failed' });
            }
        });
    }

    async handleMemorySync(syncData) {
        const syncId = syncData.syncId || uuidv4();
        const startTime = Date.now();

        logger.info('Processing memory sync', {
            syncId,
            agentId: syncData.agentId,
            memoryId: syncData.memoryId,
            operation: syncData.operation
        });

        try {
            // Validate sync data
            this.validateSyncData(syncData);

            // Check for existing sync operations
            const existingSync = await this.checkExistingSync(syncData.memoryId);
            if (existingSync) {
                return await this.handleSyncConflict(syncData, existingSync, syncId);
            }

            // Register sync operation
            this.syncOperations.set(syncId, {
                ...syncData,
                syncId,
                startTime,
                status: 'processing'
            });

            // Acquire memory lock
            const lockAcquired = await this.acquireMemoryLock(syncData.memoryId, syncData.agentId, syncId);
            if (!lockAcquired) {
                throw new Error('Failed to acquire memory lock');
            }

            // Process the sync operation
            const result = await this.processSyncOperation(syncData, syncId);

            // Release memory lock
            await this.releaseMemoryLock(syncData.memoryId, syncId);

            // Update metrics
            this.updateMetrics(syncData.agentId, Date.now() - startTime);

            // Clean up sync operation
            this.syncOperations.delete(syncId);

            logger.info('Memory sync completed', {
                syncId,
                agentId: syncData.agentId,
                memoryId: syncData.memoryId,
                duration: Date.now() - startTime
            });

            return {
                success: true,
                syncId,
                result,
                duration: Date.now() - startTime
            };

        } catch (error) {
            logger.error('Memory sync error', {
                syncId,
                error: error.message,
                agentId: syncData.agentId,
                memoryId: syncData.memoryId
            });

            // Clean up on error
            await this.releaseMemoryLock(syncData.memoryId, syncId);
            this.syncOperations.delete(syncId);

            throw error;
        }
    }

    async handleSyncConflict(newSyncData, existingSync, syncId) {
        const conflictId = uuidv4();
        
        logger.warn('Memory sync conflict detected', {
            conflictId,
            newSyncId: syncId,
            existingSyncId: existingSync.syncId,
            memoryId: newSyncData.memoryId,
            newAgent: newSyncData.agentId,
            existingAgent: existingSync.agentId
        });

        // Create conflict record
        const conflict = {
            conflictId,
            memoryId: newSyncData.memoryId,
            agents: [existingSync.agentId, newSyncData.agentId],
            syncOperations: [existingSync, { ...newSyncData, syncId }],
            created: new Date().toISOString(),
            status: 'pending',
            strategy: this.determineResolutionStrategy(existingSync.agentId, newSyncData.agentId)
        };

        this.activeConflicts.set(conflictId, conflict);
        this.metrics.conflictsPending++;

        // Attempt automatic resolution
        const resolution = await this.attemptAutoResolution(conflict);
        
        if (resolution.success) {
            this.activeConflicts.delete(conflictId);
            this.metrics.conflictsPending--;
            this.metrics.conflictsResolved++;
            
            return {
                success: true,
                syncId,
                conflictId,
                resolution: resolution.strategy,
                result: resolution.result
            };
        }

        // If auto-resolution fails, queue for manual review
        conflict.status = 'manual_review';
        
        return {
            success: false,
            syncId,
            conflictId,
            status: 'conflict_pending',
            message: 'Memory sync conflict requires manual resolution',
            resolution_url: `/api/resolve-conflict/${conflictId}`
        };
    }

    determineResolutionStrategy(agent1, agent2) {
        const priorities = CONFIG.agents.priorities;
        
        // If one agent has higher priority, use agent priority strategy
        if (priorities[agent1] !== priorities[agent2]) {
            return CONFLICT_STRATEGIES.AGENT_PRIORITY;
        }
        
        // If same priority, use timestamp-based resolution
        return CONFLICT_STRATEGIES.TIMESTAMP_LATEST;
    }

    async attemptAutoResolution(conflict) {
        try {
            const { syncOperations } = conflict;
            const [existingSync, newSync] = syncOperations;
            
            const conflictData = {
                existing: existingSync,
                new: newSync
            };
            
            // Apply resolution policies in order of precedence
            const policyOrder = [
                'SECURITY_OVERRIDE',
                'TIMESTAMP_WINDOW', 
                'AGENT_PRIORITY',
                'CUSTOM_TAGS',
                'CONTENT_MERGE'
            ];
            
            for (const policyName of policyOrder) {
                const policy = RESOLUTION_POLICIES[policyName];
                const decision = policy(conflictData);
                
                if (decision === 'existing') {
                    return {
                        success: true,
                        strategy: policyName,
                        result: existingSync,
                        chosen: 'existing'
                    };
                } else if (decision === 'new') {
                    return {
                        success: true,
                        strategy: policyName,
                        result: newSync,
                        chosen: 'new'
                    };
                } else if (decision === 'merge') {
                    const merged = await this.mergeMemoryContent(existingSync, newSync);
                    return {
                        success: true,
                        strategy: policyName,
                        result: merged,
                        chosen: 'merged'
                    };
                }
                // If policy returns null, continue to next policy
            }
            
            // Fallback: Use legacy resolution methods
            const { strategy } = conflict;
            
            switch (strategy) {
                case CONFLICT_STRATEGIES.AGENT_PRIORITY:
                    return await this.resolveByAgentPriority(syncOperations);
                
                case CONFLICT_STRATEGIES.TIMESTAMP_LATEST:
                    return await this.resolveByTimestamp(syncOperations);
                
                case CONFLICT_STRATEGIES.IMPORTANCE_HIGHEST:
                    return await this.resolveByImportance(syncOperations);
                
                default:
                    return { success: false, reason: 'Unknown strategy' };
            }
        } catch (error) {
            logger.error('Auto-resolution failed', {
                conflictId: conflict.conflictId,
                error: error.message
            });
            return { success: false, reason: error.message };
        }
    }

    async resolveByAgentPriority(syncOperations) {
        const priorities = CONFIG.agents.priorities;
        
        // Sort by agent priority (lower number = higher priority)
        const sortedOps = syncOperations.sort((a, b) => 
            priorities[a.agentId] - priorities[b.agentId]
        );
        
        const winningOp = sortedOps[0];
        const result = await this.processSyncOperation(winningOp, winningOp.syncId);
        
        logger.info('Conflict resolved by agent priority', {
            winningAgent: winningOp.agentId,
            memoryId: winningOp.memoryId
        });
        
        return {
            success: true,
            strategy: CONFLICT_STRATEGIES.AGENT_PRIORITY,
            winningOperation: winningOp,
            result
        };
    }

    async resolveByTimestamp(syncOperations) {
        // Sort by timestamp (most recent wins)
        const sortedOps = syncOperations.sort((a, b) => 
            new Date(b.timestamp || b.startTime) - new Date(a.timestamp || a.startTime)
        );
        
        const winningOp = sortedOps[0];
        const result = await this.processSyncOperation(winningOp, winningOp.syncId);
        
        logger.info('Conflict resolved by timestamp', {
            winningAgent: winningOp.agentId,
            timestamp: winningOp.timestamp || winningOp.startTime,
            memoryId: winningOp.memoryId
        });
        
        return {
            success: true,
            strategy: CONFLICT_STRATEGIES.TIMESTAMP_LATEST,
            winningOperation: winningOp,
            result
        };
    }

    async resolveByImportance(syncOperations) {
        // Sort by importance score (higher wins)
        const sortedOps = syncOperations.sort((a, b) => 
            (b.importance || 0.5) - (a.importance || 0.5)
        );
        
        const winningOp = sortedOps[0];
        const result = await this.processSyncOperation(winningOp, winningOp.syncId);
        
        logger.info('Conflict resolved by importance', {
            winningAgent: winningOp.agentId,
            importance: winningOp.importance,
            memoryId: winningOp.memoryId
        });
        
        return {
            success: true,
            strategy: CONFLICT_STRATEGIES.IMPORTANCE_HIGHEST,
            winningOperation: winningOp,
            result
        };
    }

    async mergeMemoryContent(existingSync, newSync) {
        /**
         * Merge memory content from two sync operations
         * Creates a hybrid memory entry combining both sources
         */
        
        const mergedContent = mergeContent(
            existingSync.content || '',
            newSync.content || ''
        );
        
        // Combine metadata from both sources
        const mergedMetadata = {
            ...existingSync.metadata,
            ...newSync.metadata,
            mergedFrom: [existingSync.agentId, newSync.agentId],
            mergedAt: new Date().toISOString(),
            originalSyncIds: [existingSync.syncId, newSync.syncId]
        };
        
        // Use higher importance score
        const mergedImportance = Math.max(
            existingSync.importance || 0.5,
            newSync.importance || 0.5
        );
        
        // Combine tags from both sources
        const existingTags = existingSync.metadata?.tags || [];
        const newTags = newSync.metadata?.tags || [];
        const mergedTags = [...new Set([...existingTags, ...newTags, 'merged'])];
        
        const mergedSync = {
            ...newSync, // Use new sync as base
            content: mergedContent,
            importance: mergedImportance,
            metadata: {
                ...mergedMetadata,
                tags: mergedTags
            },
            syncId: uuidv4() // Generate new sync ID for merged result
        };
        
        logger.info('Memory content merged successfully', {
            memoryId: mergedSync.memoryId,
            mergedFrom: [existingSync.agentId, newSync.agentId],
            contentLength: mergedContent.length,
            importance: mergedImportance
        });
        
        // Process the merged sync operation
        const result = await this.processSyncOperation(mergedSync, mergedSync.syncId);
        
        return {
            success: true,
            strategy: 'CONTENT_MERGE',
            mergedOperation: mergedSync,
            result
        };
    }

    async processSyncOperation(syncData, syncId) {
        // Simulate memory sync operation
        // In production, this would interface with the actual memory storage
        
        const operation = {
            syncId,
            memoryId: syncData.memoryId,
            agentId: syncData.agentId,
            operation: syncData.operation,
            content: syncData.content,
            timestamp: new Date().toISOString(),
            status: 'completed'
        };

        // Store operation in Redis for tracking
        await this.redisClient.setEx(
            `sync_operation:${syncId}`,
            3600, // 1 hour TTL
            JSON.stringify(operation)
        );

        return operation;
    }

    async acquireMemoryLock(memoryId, agentId, syncId) {
        const lockKey = `memory_lock:${memoryId}`;
        const lockValue = `${agentId}:${syncId}:${Date.now()}`;
        
        try {
            // Try to acquire lock with 30 second TTL
            const result = await this.redisClient.set(lockKey, lockValue, {
                EX: 30,
                NX: true
            });
            
            if (result === 'OK') {
                logger.debug('Memory lock acquired', { memoryId, agentId, syncId });
                return true;
            }
            
            logger.debug('Memory lock acquisition failed', { memoryId, agentId, syncId });
            return false;
            
        } catch (error) {
            logger.error('Lock acquisition error', { error: error.message, memoryId, agentId });
            return false;
        }
    }

    async releaseMemoryLock(memoryId, syncId) {
        const lockKey = `memory_lock:${memoryId}`;
        
        try {
            await this.redisClient.del(lockKey);
            logger.debug('Memory lock released', { memoryId, syncId });
        } catch (error) {
            logger.error('Lock release error', { error: error.message, memoryId, syncId });
        }
    }

    async checkExistingSync(memoryId) {
        // Check if there's an active sync for this memory
        for (const [syncId, sync] of this.syncOperations) {
            if (sync.memoryId === memoryId && sync.status === 'processing') {
                return sync;
            }
        }
        return null;
    }

    validateSyncData(syncData) {
        const required = ['agentId', 'memoryId', 'operation'];
        const missing = required.filter(field => !syncData[field]);
        
        if (missing.length > 0) {
            throw new Error(`Missing required fields: ${missing.join(', ')}`);
        }

        const validAgents = Object.keys(CONFIG.agents.priorities);
        if (!validAgents.includes(syncData.agentId)) {
            throw new Error(`Invalid agent ID: ${syncData.agentId}. Valid agents: ${validAgents.join(', ')}`);
        }

        const validOperations = ['create', 'update', 'delete', 'read'];
        if (!validOperations.includes(syncData.operation)) {
            throw new Error(`Invalid operation: ${syncData.operation}. Valid operations: ${validOperations.join(', ')}`);
        }
    }

    updateMetrics(agentId, duration) {
        this.metrics.totalSyncs++;
        this.metrics.agentOperations[agentId]++;
        this.metrics.lastSync = new Date().toISOString();
        
        // Update average resolution time
        if (this.metrics.averageResolutionTime === 0) {
            this.metrics.averageResolutionTime = duration;
        } else {
            this.metrics.averageResolutionTime = (
                (this.metrics.averageResolutionTime + duration) / 2
            );
        }
    }

    async getSyncStatus(syncId) {
        // Check active sync operations
        if (this.syncOperations.has(syncId)) {
            return this.syncOperations.get(syncId);
        }

        // Check Redis for completed operations
        try {
            const operation = await this.redisClient.get(`sync_operation:${syncId}`);
            if (operation) {
                return JSON.parse(operation);
            }
        } catch (error) {
            logger.error('Failed to get sync status from Redis', { error: error.message, syncId });
        }

        throw new Error('Sync operation not found');
    }

    async forceMemorySync(memoryId, agentId, priority = false) {
        const syncId = uuidv4();
        
        logger.info('Force sync initiated', { syncId, memoryId, agentId, priority });

        // If priority sync, clear existing locks
        if (priority) {
            await this.releaseMemoryLock(memoryId, 'force-sync');
        }

        const syncData = {
            syncId,
            memoryId,
            agentId,
            operation: 'force_sync',
            timestamp: new Date().toISOString(),
            priority: true
        };

        return await this.handleMemorySync(syncData);
    }

    setupEventListeners() {
        // Handle Redis connection events
        this.redisClient.on('error', (error) => {
            logger.error('Redis error', { error: error.message });
        });

        this.redisClient.on('connect', () => {
            logger.info('Redis connected');
        });

        this.redisClient.on('disconnect', () => {
            logger.warn('Redis disconnected');
        });

        // Handle process events
        process.on('SIGTERM', async () => {
            logger.info('SIGTERM received, shutting down gracefully');
            await this.shutdown();
            process.exit(0);
        });

        process.on('SIGINT', async () => {
            logger.info('SIGINT received, shutting down gracefully');
            await this.shutdown();
            process.exit(0);
        });
    }

    startConflictProcessor() {
        // Process pending conflicts every 10 seconds
        setInterval(async () => {
            try {
                await this.processActiveConflicts();
            } catch (error) {
                logger.error('Conflict processor error', { error: error.message });
            }
        }, 10000);
    }

    async processActiveConflicts() {
        for (const [conflictId, conflict] of this.activeConflicts) {
            if (conflict.status === 'pending') {
                const resolution = await this.attemptAutoResolution(conflict);
                
                if (resolution.success) {
                    this.activeConflicts.delete(conflictId);
                    this.metrics.conflictsPending--;
                    this.metrics.conflictsResolved++;
                    
                    logger.info('Conflict auto-resolved', {
                        conflictId,
                        strategy: resolution.strategy
                    });
                }
            }
        }
    }

    setupErrorHandling() {
        this.app.use((error, req, res, next) => {
            logger.error('Unhandled request error', {
                error: error.message,
                stack: error.stack,
                url: req.url,
                method: req.method
            });

            res.status(500).json({
                error: 'Internal server error',
                message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
            });
        });
    }

    async shutdown() {
        logger.info('Starting Memory Sync Service shutdown...');

        try {
            // Close Redis connection
            if (this.redisClient) {
                await this.redisClient.quit();
                logger.info('Redis connection closed');
            }

            // Clear active operations
            this.syncOperations.clear();
            this.activeConflicts.clear();

            logger.info('Memory Sync Service shutdown completed');
        } catch (error) {
            logger.error('Error during shutdown', { error: error.message });
        }
    }

    start() {
        return new Promise((resolve, reject) => {
            this.initialize()
                .then(() => {
                    this.app.listen(CONFIG.port, () => {
                        logger.info(`Memory Sync Service listening on port ${CONFIG.port}`);
                        resolve();
                    });
                })
                .catch(reject);
        });
    }
}

// Create and start the service
const memorySyncService = new MemorySyncService();

if (require.main === module) {
    memorySyncService.start()
        .then(() => {
            logger.info('Memory Sync Service started successfully');
        })
        .catch((error) => {
            logger.error('Failed to start Memory Sync Service', { error: error.message });
            process.exit(1);
        });
}

module.exports = { MemorySyncService, CONFLICT_STRATEGIES, CONFIG };