/**
 * Enhanced Conflict Resolution Policies for Memory Sync Service
 * Multi-agent priority, custom tags, and intelligent merging strategies
 */

const winston = require('winston');
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [new winston.transports.Console()]
});

// Agent priority configuration
const AGENT_PRIORITIES = {
    'sentry': 1,  // Highest - Security operations
    'alden': 2,   // High - Primary productivity agent
    'alice': 3,   // Medium - Cognitive-behavioral analysis
    'mimic': 4    // Lowest - Persona adaptation
};

// Critical tag hierarchy for conflict resolution
const TAG_HIERARCHY = {
    'security_incident': 1,
    'system_alert': 2,
    'therapeutic_response': 3,
    'memory_corruption': 4,
    'emergency_override': 5,
    'critical': 6,
    'high': 7,
    'medium': 8,
    'low': 9,
    'persona_adaptation': 10
};

// Time-based conflict resolution settings
const CONFLICT_TIMING = {
    CONCURRENT_WINDOW_MS: 5000,     // 5 seconds for truly concurrent operations
    RECENCY_BIAS_MINUTES: 5,        // Recent content gets preference
    STALE_THRESHOLD_HOURS: 24       // Old content becomes stale
};

class ConflictResolutionPolicies {
    constructor() {
        this.resolutionStats = {
            totalConflicts: 0,
            resolutionMethods: {},
            agentOverrides: {},
            mergeAttempts: 0,
            mergeSuccesses: 0
        };
    }

    /**
     * Main conflict resolution entry point
     */
    async resolveConflict(newSyncData, existingSync, syncId) {
        const conflictId = `conflict_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.resolutionStats.totalConflicts++;
        
        logger.info('🔄 Resolving memory sync conflict', {
            conflictId,
            newAgent: newSyncData.agentId,
            existingAgent: existingSync.agentId,
            syncId,
            timestamp: new Date().toISOString()
        });

        // Apply resolution policies in priority order
        const resolutionResult = await this.applyResolutionPolicies(newSyncData, existingSync, conflictId);
        
        // Update statistics
        this.updateResolutionStats(resolutionResult);
        
        logger.info('✅ Conflict resolved', {
            conflictId,
            resolution: resolutionResult.resolution,
            winner: resolutionResult.winner,
            reason: resolutionResult.reason
        });

        return resolutionResult;
    }

    /**
     * Apply resolution policies in priority order
     */
    async applyResolutionPolicies(newSyncData, existingSync, conflictId) {
        const policies = [
            this.securityOverridePolicy,
            this.emergencyTagPolicy,
            this.agentPriorityPolicy,
            this.customTagPolicy,
            this.recencyBiasPolicy,
            this.timestampPolicy,
            this.weightedImportancePolicy,
            this.sessionContinuityPolicy,
            this.contentMergePolicy,
            this.stabilityFallbackPolicy
        ];

        for (const policy of policies) {
            const result = await policy.call(this, newSyncData, existingSync, conflictId);
            if (result && result.winner !== 'continue') {
                return {
                    ...result,
                    conflictId,
                    timestamp: new Date().toISOString(),
                    appliedPolicy: policy.name
                };
            }
        }

        // Should never reach here due to stabilityFallbackPolicy
        throw new Error('No conflict resolution policy could handle this conflict');
    }

    /**
     * Policy 1: Security Override - Sentry always wins security-related conflicts
     */
    async securityOverridePolicy(newSyncData, existingSync, conflictId) {
        const newTags = newSyncData.metadata?.tags || [];
        const existingTags = existingSync.metadata?.tags || [];
        const securityTags = ['security_incident', 'threat_detection', 'access_violation', 'security_alert'];
        
        const newHasSecurity = newTags.some(tag => securityTags.includes(tag));
        const existingHasSecurity = existingTags.some(tag => securityTags.includes(tag));
        
        // If new data is from Sentry with security tags, it always wins
        if (newSyncData.agentId === 'sentry' && newHasSecurity) {
            return {
                resolution: 'security_override',
                winner: 'new',
                action: 'replace',
                reason: 'Sentry security override with security tags',
                metadata: { 
                    securityOverride: true, 
                    securityTags: newTags.filter(tag => securityTags.includes(tag))
                }
            };
        }
        
        // If existing data is from Sentry with security tags, it's protected
        if (existingSync.agentId === 'sentry' && existingHasSecurity && newSyncData.agentId !== 'sentry') {
            return {
                resolution: 'security_protection',
                winner: 'existing',
                action: 'reject',
                reason: 'Protecting existing Sentry security content',
                metadata: { 
                    securityProtection: true,
                    protectedTags: existingTags.filter(tag => securityTags.includes(tag))
                }
            };
        }
        
        return { winner: 'continue' }; // Continue to next policy
    }

    /**
     * Policy 2: Emergency Tag Policy - Critical system tags take precedence
     */
    async emergencyTagPolicy(newSyncData, existingSync, conflictId) {
        const newTags = newSyncData.metadata?.tags || [];
        const existingTags = existingSync.metadata?.tags || [];
        const emergencyTags = ['emergency_override', 'system_alert', 'memory_corruption'];
        
        const newHasEmergency = newTags.some(tag => emergencyTags.includes(tag));
        const existingHasEmergency = existingTags.some(tag => emergencyTags.includes(tag));
        
        if (newHasEmergency && !existingHasEmergency) {
            return {
                resolution: 'emergency_override',
                winner: 'new',
                action: 'replace',
                reason: `Emergency tag detected: ${newTags.filter(tag => emergencyTags.includes(tag)).join(', ')}`,
                metadata: { emergencyTags: newTags.filter(tag => emergencyTags.includes(tag)) }
            };
        } else if (existingHasEmergency && !newHasEmergency) {
            return {
                resolution: 'emergency_protection',
                winner: 'existing',
                action: 'reject',
                reason: `Protecting emergency content: ${existingTags.filter(tag => emergencyTags.includes(tag)).join(', ')}`,
                metadata: { protectedEmergencyTags: existingTags.filter(tag => emergencyTags.includes(tag)) }
            };
        }
        
        return { winner: 'continue' };
    }

    /**
     * Policy 3: Agent Priority - Based on configured hierarchy
     */
    async agentPriorityPolicy(newSyncData, existingSync, conflictId) {
        const newPriority = AGENT_PRIORITIES[newSyncData.agentId] || 99;
        const existingPriority = AGENT_PRIORITIES[existingSync.agentId] || 99;
        
        if (newPriority < existingPriority) {
            return {
                resolution: 'agent_priority_override',
                winner: 'new',
                action: 'replace',
                reason: `Agent priority ${newPriority} overrides priority ${existingPriority}`,
                metadata: { 
                    newPriority, 
                    existingPriority,
                    priorityDiff: existingPriority - newPriority
                }
            };
        } else if (existingPriority < newPriority) {
            return {
                resolution: 'agent_priority_protection',
                winner: 'existing',
                action: 'reject',
                reason: `Agent priority ${existingPriority} blocks priority ${newPriority}`,
                metadata: { 
                    newPriority, 
                    existingPriority,
                    priorityDiff: newPriority - existingPriority
                }
            };
        }
        
        return { winner: 'continue' }; // Same priority, continue to next policy
    }

    /**
     * Policy 4: Custom Tag Priority - Based on tag hierarchy
     */
    async customTagPolicy(newSyncData, existingSync, conflictId) {
        const newTags = newSyncData.metadata?.tags || [];
        const existingTags = existingSync.metadata?.tags || [];
        
        const getHighestTagPriority = (tags) => {
            let highestPriority = 999;
            for (const tag of tags) {
                if (TAG_HIERARCHY[tag] && TAG_HIERARCHY[tag] < highestPriority) {
                    highestPriority = TAG_HIERARCHY[tag];
                }
            }
            return highestPriority;
        };
        
        const newTagPriority = getHighestTagPriority(newTags);
        const existingTagPriority = getHighestTagPriority(existingTags);
        
        if (newTagPriority < existingTagPriority) {
            return {
                resolution: 'tag_priority_override',
                winner: 'new',
                action: 'replace',
                reason: `Tag priority ${newTagPriority} overrides ${existingTagPriority}`,
                metadata: { newTagPriority, existingTagPriority, newTags, existingTags }
            };
        } else if (existingTagPriority < newTagPriority) {
            return {
                resolution: 'tag_priority_protection',
                winner: 'existing',
                action: 'reject',
                reason: `Tag priority ${existingTagPriority} blocks ${newTagPriority}`,
                metadata: { newTagPriority, existingTagPriority, newTags, existingTags }
            };
        }
        
        return { winner: 'continue' };
    }

    /**
     * Policy 5: Recency Bias - Recent content gets preference
     */
    async recencyBiasPolicy(newSyncData, existingSync, conflictId) {
        const newTimestamp = new Date(newSyncData.timestamp || Date.now());
        const existingTimestamp = new Date(existingSync.timestamp || 0);
        const timeDiffMinutes = (newTimestamp - existingTimestamp) / (1000 * 60);
        
        // If content is very recent (within configured window), prefer newer
        if (timeDiffMinutes > 0 && timeDiffMinutes < CONFLICT_TIMING.RECENCY_BIAS_MINUTES) {
            return {
                resolution: 'recency_bias',
                winner: 'new',
                action: 'replace',
                reason: `Recent content (${timeDiffMinutes.toFixed(1)} min old) takes precedence`,
                metadata: { timeDiffMinutes, recencyThreshold: CONFLICT_TIMING.RECENCY_BIAS_MINUTES }
            };
        }
        
        return { winner: 'continue' };
    }

    /**
     * Policy 6: Standard Timestamp Resolution
     */
    async timestampPolicy(newSyncData, existingSync, conflictId) {
        const newTimestamp = new Date(newSyncData.timestamp || Date.now());
        const existingTimestamp = new Date(existingSync.timestamp || 0);
        
        if (newTimestamp > existingTimestamp) {
            return {
                resolution: 'timestamp_newer',
                winner: 'new',
                action: 'replace',
                reason: `Newer timestamp ${newTimestamp.toISOString()} wins`,
                metadata: { 
                    newTimestamp: newTimestamp.toISOString(),
                    existingTimestamp: existingTimestamp.toISOString(),
                    timeDiff: newTimestamp - existingTimestamp
                }
            };
        }
        
        return { winner: 'continue' };
    }

    /**
     * Policy 7: Weighted Importance - Agent-specific importance multipliers
     */
    async weightedImportancePolicy(newSyncData, existingSync, conflictId) {
        const importanceMultipliers = {
            'sentry': 1.3,  // Security content boost
            'alden': 1.1,   // Productivity content boost
            'alice': 1.0,   // CBT content normal weight
            'mimic': 0.9    // Persona adaptation lower weight
        };
        
        const newImportance = newSyncData.importance || 0.5;
        const existingImportance = existingSync.importance || 0.5;
        
        const newWeighted = newImportance * (importanceMultipliers[newSyncData.agentId] || 1.0);
        const existingWeighted = existingImportance * (importanceMultipliers[existingSync.agentId] || 1.0);
        
        if (Math.abs(newWeighted - existingWeighted) > 0.2) {
            const winner = newWeighted > existingWeighted ? 'new' : 'existing';
            return {
                resolution: 'weighted_importance',
                winner,
                action: winner === 'new' ? 'replace' : 'reject',
                reason: `Weighted importance ${Math.max(newWeighted, existingWeighted).toFixed(2)} takes precedence`,
                metadata: { 
                    newWeighted: newWeighted.toFixed(2), 
                    existingWeighted: existingWeighted.toFixed(2),
                    threshold: 0.2
                }
            };
        }
        
        return { winner: 'continue' };
    }

    /**
     * Policy 8: Session Continuity - Same session prefers newer content
     */
    async sessionContinuityPolicy(newSyncData, existingSync, conflictId) {
        const newSessionId = newSyncData.metadata?.sessionId;
        const existingSessionId = existingSync.metadata?.sessionId;
        
        if (newSessionId && existingSessionId && newSessionId === existingSessionId) {
            return {
                resolution: 'session_continuity',
                winner: 'new',
                action: 'replace',
                reason: 'Same session context - maintaining conversation continuity',
                metadata: { sessionId: newSessionId, continuityPreference: true }
            };
        }
        
        return { winner: 'continue' };
    }

    /**
     * Policy 9: Content Merge - Attempt intelligent merging for compatible content
     */
    async contentMergePolicy(newSyncData, existingSync, conflictId) {
        if (await this.canMergeContent(newSyncData, existingSync)) {
            const mergedContent = await this.mergeContent(newSyncData, existingSync);
            return {
                resolution: 'intelligent_merge',
                winner: 'merged',
                action: 'merge',
                mergedContent,
                reason: 'Compatible content merged with context preservation',
                metadata: { 
                    mergeStrategy: 'context_aware',
                    originalContentLength: (existingSync.content || '').length,
                    newContentLength: (newSyncData.content || '').length,
                    mergedContentLength: (mergedContent || '').length
                }
            };
        }
        
        return { winner: 'continue' };
    }

    /**
     * Policy 10: Stability Fallback - Default behavior to maintain stability
     */
    async stabilityFallbackPolicy(newSyncData, existingSync, conflictId) {
        return {
            resolution: 'stability_preference',
            winner: 'existing',
            action: 'reject',
            reason: 'No clear resolution criteria met - maintaining memory stability',
            metadata: { 
                fallbackPolicy: true,
                analysisDetails: {
                    agentEqual: newSyncData.agentId === existingSync.agentId,
                    priorityEqual: AGENT_PRIORITIES[newSyncData.agentId] === AGENT_PRIORITIES[existingSync.agentId],
                    timestampDiff: new Date(newSyncData.timestamp || 0) - new Date(existingSync.timestamp || 0)
                }
            }
        };
    }

    /**
     * Check if content can be merged
     */
    async canMergeContent(newSyncData, existingSync) {
        // Simple compatibility check - can be enhanced with more sophisticated logic
        const newContent = newSyncData.content || '';
        const existingContent = existingSync.content || '';
        
        // Don't merge if content is too different in length
        const lengthRatio = Math.min(newContent.length, existingContent.length) / 
                           Math.max(newContent.length, existingContent.length);
        if (lengthRatio < 0.3) return false;
        
        // Check for semantic similarity (simplified)
        const similarity = this.calculateContentSimilarity(newContent, existingContent);
        return similarity > 0.6;
    }

    /**
     * Merge compatible content
     */
    async mergeContent(newSyncData, existingSync) {
        this.resolutionStats.mergeAttempts++;
        
        try {
            const newContent = newSyncData.content || '';
            const existingContent = existingSync.content || '';
            
            // Simple merge strategy - combine unique sentences
            const sentences1 = existingContent.split(/[.!?]+/).filter(s => s.trim());
            const sentences2 = newContent.split(/[.!?]+/).filter(s => s.trim());
            
            const uniqueSentences = [...new Set([...sentences1, ...sentences2])];
            const mergedContent = uniqueSentences.join('. ') + '.';
            
            this.resolutionStats.mergeSuccesses++;
            return mergedContent;
        } catch (error) {
            logger.error('Content merge failed', { error: error.message });
            return existingSync.content; // Fallback to existing content
        }
    }

    /**
     * Calculate content similarity (simple implementation)
     */
    calculateContentSimilarity(content1, content2) {
        if (!content1 || !content2) return 0;
        
        const words1 = content1.toLowerCase().split(/\s+/);
        const words2 = content2.toLowerCase().split(/\s+/);
        
        const set1 = new Set(words1);
        const set2 = new Set(words2);
        
        const intersection = new Set([...set1].filter(x => set2.has(x)));
        const union = new Set([...set1, ...set2]);
        
        return intersection.size / union.size;
    }

    /**
     * Update resolution statistics
     */
    updateResolutionStats(resolutionResult) {
        const method = resolutionResult.resolution;
        this.resolutionStats.resolutionMethods[method] = (this.resolutionStats.resolutionMethods[method] || 0) + 1;
        
        if (resolutionResult.winner === 'new') {
            const agent = resolutionResult.metadata?.newAgent || 'unknown';
            this.resolutionStats.agentOverrides[agent] = (this.resolutionStats.agentOverrides[agent] || 0) + 1;
        }
    }

    /**
     * Get resolution statistics
     */
    getResolutionStats() {
        return {
            ...this.resolutionStats,
            mergeSuccessRate: this.resolutionStats.mergeAttempts > 0 
                ? (this.resolutionStats.mergeSuccesses / this.resolutionStats.mergeAttempts * 100).toFixed(2) + '%'
                : '0%',
            lastUpdated: new Date().toISOString()
        };
    }
}

module.exports = ConflictResolutionPolicies;