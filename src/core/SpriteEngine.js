/**
 * Core Sprite Engine - Conversational AI Orchestration
 * 
 * Handles intelligent routing between Micro-LLM Sprites and Heavy-LLM reasoning engines
 * based on natural language interpretation and confidence thresholds.
 * 
 * Architecture:
 * - Sprites interpret natural language requests and route to appropriate personas
 * - Heavy-LLM handles complex reasoning when Sprite confidence is low
 * - Memory isolation and hot-swapping for security and performance
 */

import { Vault } from '../vault/vault.js';

// Sentry telemetry integration for model activation and power metrics
class SentryTelemetry {
  constructor() {
    this.startTime = Date.now();
    this.modelActivations = new Map();
    this.powerMetrics = {
      totalModelLoads: 0,
      totalModelSwaps: 0,
      totalComputeTime: 0,
      averageLoadTime: 0,
      peakMemoryUsage: 0,
      thermalEvents: []
    };
  }

  recordModelActivation(engineId, engineData, loadDuration) {
    const activation = {
      engineId,
      engineName: engineData.name,
      model: engineData.model,
      loadDuration,
      activatedAt: Date.now(),
      computeTime: 0,
      requestCount: 0
    };

    this.modelActivations.set(engineId, activation);
    this.powerMetrics.totalModelLoads++;
    this.powerMetrics.totalModelSwaps++;
    
    // Update average load time
    this.powerMetrics.averageLoadTime = (
      (this.powerMetrics.averageLoadTime * (this.powerMetrics.totalModelLoads - 1) + loadDuration) / 
      this.powerMetrics.totalModelLoads
    );

    // Log to Sentry
    this.logSentryEvent('model_activated', {
      engineId,
      engineName: engineData.name,
      model: engineData.model,
      loadDuration,
      totalActivations: this.powerMetrics.totalModelLoads
    });
  }

  recordModelDeactivation(engineId, sessionDuration) {
    const activation = this.modelActivations.get(engineId);
    if (activation) {
      activation.sessionDuration = sessionDuration;
      this.powerMetrics.totalComputeTime += sessionDuration;
      
      // Log to Sentry
      this.logSentryEvent('model_deactivated', {
        engineId,
        engineName: activation.engineName,
        sessionDuration,
        requestCount: activation.requestCount,
        totalComputeTime: this.powerMetrics.totalComputeTime
      });
      
      this.modelActivations.delete(engineId);
    }
  }

  recordModelRequest(engineId, processingTime, success) {
    const activation = this.modelActivations.get(engineId);
    if (activation) {
      activation.requestCount++;
      activation.computeTime += processingTime;
      
      // Track performance metrics
      if (!success) {
        this.logSentryEvent('model_request_failed', {
          engineId,
          processingTime,
          requestCount: activation.requestCount
        });
      }
    }
  }

  recordThermalEvent(eventType, temperature, throttling = false) {
    const thermalEvent = {
      eventType,
      temperature,
      throttling,
      timestamp: Date.now()
    };
    
    this.powerMetrics.thermalEvents.push(thermalEvent);
    
    // Keep only last 100 events
    if (this.powerMetrics.thermalEvents.length > 100) {
      this.powerMetrics.thermalEvents.shift();
    }
    
    // Alert on critical thermal events
    if (temperature > 85 || throttling) {
      this.logSentryEvent('thermal_warning', {
        eventType,
        temperature,
        throttling,
        activeModels: Array.from(this.modelActivations.keys())
      }, 'warning');
    }
  }

  updateMemoryUsage(memoryUsage) {
    if (memoryUsage > this.powerMetrics.peakMemoryUsage) {
      this.powerMetrics.peakMemoryUsage = memoryUsage;
      
      // Alert on high memory usage
      if (memoryUsage > 8000) { // 8GB threshold
        this.logSentryEvent('high_memory_usage', {
          memoryUsage,
          peakUsage: this.powerMetrics.peakMemoryUsage,
          activeModels: Array.from(this.modelActivations.keys())
        }, 'warning');
      }
    }
  }

  logSentryEvent(eventType, data, level = 'info') {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      eventType,
      data,
      sessionUptime: Date.now() - this.startTime
    };
    
    console.log(`📊 Telemetry [${level.toUpperCase()}]:`, eventType, data);
    
    // Try real Sentry integration
    try {
      if (typeof window !== 'undefined' && window.Sentry) {
        // Real Sentry SDK available
        window.Sentry.captureMessage(`Sprite Engine: ${eventType}`, level, {
          extra: data,
          tags: {
            component: 'sprite_engine',
            eventType: eventType
          }
        });
      } else if (typeof window !== 'undefined' && window.sentryAPI) {
        // Custom Sentry API available
        window.sentryAPI.captureMessage(`Sprite Engine: ${eventType}`, level, data);
      } else {
        // No Sentry integration available - just log locally
        console.warn(`Feature not implemented: Sentry telemetry unavailable for event: ${eventType}`);
        
        // Store locally for debugging
        if (typeof localStorage !== 'undefined') {
          const key = 'hearthlink_telemetry_log';
          const existingLogs = JSON.parse(localStorage.getItem(key) || '[]');
          existingLogs.push(logEntry);
          
          // Keep only last 100 entries
          if (existingLogs.length > 100) {
            existingLogs.splice(0, existingLogs.length - 100);
          }
          
          localStorage.setItem(key, JSON.stringify(existingLogs));
        }
      }
    } catch (error) {
      console.error(`❌ Telemetry logging failed: ${error.message}`);
    }
  }

  getPowerMetrics() {
    return {
      ...this.powerMetrics,
      sessionUptime: Date.now() - this.startTime,
      activeModels: Array.from(this.modelActivations.entries()).map(([id, activation]) => ({
        engineId: id,
        engineName: activation.engineName,
        model: activation.model,
        activeDuration: Date.now() - activation.activatedAt,
        requestCount: activation.requestCount,
        computeTime: activation.computeTime
      })),
      recentThermalEvents: this.powerMetrics.thermalEvents.slice(-10)
    };
  }

  getModelActivationSummary() {
    const activations = Array.from(this.modelActivations.values());
    
    return {
      totalActiveModels: activations.length,
      totalRequests: activations.reduce((sum, a) => sum + a.requestCount, 0),
      totalComputeTime: activations.reduce((sum, a) => sum + a.computeTime, 0),
      averageRequestsPerModel: activations.length > 0 ? 
        activations.reduce((sum, a) => sum + a.requestCount, 0) / activations.length : 0,
      activationsByModel: activations.reduce((acc, a) => {
        acc[a.model] = (acc[a.model] || 0) + 1;
        return acc;
      }, {})
    };
  }
}

// Power budget enforcement and thermal monitoring
class PowerManager {
  constructor(telemetry) {
    this.telemetry = telemetry;
    this.powerBudget = {
      maxConcurrentModels: 2,
      maxMemoryUsage: 16000, // 16GB
      maxThermalThreshold: 85, // Celsius
      maxContinuousRuntime: 3600000, // 1 hour in ms
      throttleTemperature: 80,
      emergencyShutdownTemp: 95
    };
    
    this.currentState = {
      isThrottling: false,
      thermalShutdownActive: false,
      powerSaveMode: false,
      lastThermalCheck: Date.now(),
      memoryPressure: 'normal' // normal, elevated, critical
    };
    
    this.thermalMonitor = null;
    this.powerEnforcementCallbacks = [];
    
    // Start monitoring
    this.startThermalMonitoring();
    this.startMemoryMonitoring();
  }

  startThermalMonitoring() {
    // Simulate thermal monitoring - in real implementation would use system APIs
    this.thermalMonitor = setInterval(() => {
      this.checkThermalStatus();
    }, 5000); // Check every 5 seconds
  }

  startMemoryMonitoring() {
    // Monitor memory usage every 10 seconds
    setInterval(() => {
      this.checkMemoryPressure();
    }, 10000);
  }

  async checkThermalStatus() {
    try {
      // Attempt real system temperature monitoring
      const systemTemp = this.getSystemTemperature();
      const gpuTemp = this.getGPUTemperature();
      const maxTemp = Math.max(systemTemp, gpuTemp);
      
      this.currentState.lastThermalCheck = Date.now();
      
      // Record thermal event
      this.telemetry.recordThermalEvent('thermal_check', maxTemp, this.currentState.isThrottling);
      
      // Check for thermal thresholds
      if (maxTemp >= this.powerBudget.emergencyShutdownTemp) {
        await this.triggerEmergencyThermalShutdown(maxTemp);
      } else if (maxTemp >= this.powerBudget.maxThermalThreshold) {
        await this.enableThermalThrottling(maxTemp);
      } else if (maxTemp >= this.powerBudget.throttleTemperature) {
        await this.enablePowerSaveMode(maxTemp);
      } else if (this.currentState.isThrottling && maxTemp < this.powerBudget.throttleTemperature - 5) {
        await this.disableThermalThrottling(maxTemp);
      }
      
    } catch (error) {
      // Thermal monitoring not implemented - disable monitoring
      console.warn('⚠️ Thermal monitoring not available:', error.message);
      this.currentState.thermalMonitoringAvailable = false;
      
      // Stop thermal monitoring since it's not implemented
      if (this.thermalMonitor) {
        clearInterval(this.thermalMonitor);
        this.thermalMonitor = null;
      }
      
      this.telemetry.logSentryEvent('thermal_monitoring_unavailable', { 
        error: error.message,
        status: 'Feature not implemented'
      }, 'warning');
    }
  }

  async checkMemoryPressure() {
    try {
      const memoryUsage = this.getMemoryUsage();
      this.telemetry.updateMemoryUsage(memoryUsage);
      
      const usagePercent = (memoryUsage / this.powerBudget.maxMemoryUsage) * 100;
      
      let newPressure = 'normal';
      if (usagePercent > 90) {
        newPressure = 'critical';
      } else if (usagePercent > 75) {
        newPressure = 'elevated';
      }
      
      if (newPressure !== this.currentState.memoryPressure) {
        const oldPressure = this.currentState.memoryPressure;
        this.currentState.memoryPressure = newPressure;
        
        this.telemetry.logSentryEvent('memory_pressure_changed', {
          oldPressure,
          newPressure,
          memoryUsage,
          usagePercent
        }, newPressure === 'critical' ? 'warning' : 'info');
        
        if (newPressure === 'critical') {
          await this.enforceMemoryBudget();
        }
      }
      
    } catch (error) {
      // Memory monitoring not fully implemented - use basic fallback
      console.warn('⚠️ Advanced memory monitoring not available:', error.message);
      this.currentState.memoryMonitoringAvailable = false;
      this.currentState.memoryPressure = 'unknown';
      
      this.telemetry.logSentryEvent('memory_monitoring_limited', { 
        error: error.message,
        status: 'Feature partially implemented - using basic fallback'
      }, 'warning');
    }
  }

  async enforceMemoryBudget() {
    console.log('🔥 Enforcing memory budget due to critical memory pressure');
    
    // Trigger callbacks to unload non-essential models
    for (const callback of this.powerEnforcementCallbacks) {
      try {
        await callback('memory_pressure', {
          currentPressure: this.currentState.memoryPressure,
          memoryUsage: this.getMemoryUsage(),
          maxMemory: this.powerBudget.maxMemoryUsage
        });
      } catch (error) {
        console.error('Power enforcement callback error:', error);
      }
    }
  }

  async triggerEmergencyThermalShutdown(temperature) {
    if (this.currentState.thermalShutdownActive) return;
    
    console.log(`🚨 EMERGENCY THERMAL SHUTDOWN - Temperature: ${temperature}°C`);
    this.currentState.thermalShutdownActive = true;
    
    this.telemetry.logSentryEvent('emergency_thermal_shutdown', {
      temperature,
      threshold: this.powerBudget.emergencyShutdownTemp
    }, 'error');
    
    // Trigger emergency shutdown callbacks
    for (const callback of this.powerEnforcementCallbacks) {
      try {
        await callback('emergency_shutdown', { temperature, reason: 'thermal' });
      } catch (error) {
        console.error('Emergency shutdown callback error:', error);
      }
    }
  }

  async enableThermalThrottling(temperature) {
    if (this.currentState.isThrottling) return;
    
    console.log(`🔥 Enabling thermal throttling - Temperature: ${temperature}°C`);
    this.currentState.isThrottling = true;
    
    this.telemetry.logSentryEvent('thermal_throttling_enabled', {
      temperature,
      threshold: this.powerBudget.maxThermalThreshold
    }, 'warning');
    
    // Trigger throttling callbacks
    for (const callback of this.powerEnforcementCallbacks) {
      try {
        await callback('throttle_enable', { temperature });
      } catch (error) {
        console.error('Throttling callback error:', error);
      }
    }
  }

  async enablePowerSaveMode(temperature) {
    if (this.currentState.powerSaveMode) return;
    
    console.log(`⚡ Enabling power save mode - Temperature: ${temperature}°C`);
    this.currentState.powerSaveMode = true;
    
    this.telemetry.logSentryEvent('power_save_enabled', {
      temperature,
      threshold: this.powerBudget.throttleTemperature
    }, 'info');
  }

  async disableThermalThrottling(temperature) {
    if (!this.currentState.isThrottling) return;
    
    console.log(`❄️ Disabling thermal throttling - Temperature: ${temperature}°C`);
    this.currentState.isThrottling = false;
    this.currentState.powerSaveMode = false;
    this.currentState.thermalShutdownActive = false;
    
    this.telemetry.logSentryEvent('thermal_throttling_disabled', {
      temperature
    }, 'info');
    
    // Trigger throttling disable callbacks
    for (const callback of this.powerEnforcementCallbacks) {
      try {
        await callback('throttle_disable', { temperature });
      } catch (error) {
        console.error('Throttling disable callback error:', error);
      }
    }
  }

  getSystemTemperature() {
    // Real system temperature monitoring would require native system access
    throw new Error('Feature not implemented: Real system temperature monitoring requires native platform integration');
  }

  getGPUTemperature() {
    // Real GPU temperature monitoring would require GPU vendor APIs
    throw new Error('Feature not implemented: Real GPU temperature monitoring requires vendor-specific APIs (NVIDIA-ML, AMD ADL)');
  }

  getMemoryUsage() {
    // Real memory usage monitoring would require system APIs
    if (typeof process !== 'undefined' && process.memoryUsage) {
      // Node.js environment - can get real memory usage
      const usage = process.memoryUsage();
      return Math.round(usage.heapUsed / 1024 / 1024); // Convert to MB
    } else if (typeof performance !== 'undefined' && performance.memory) {
      // Browser environment - limited memory info
      return Math.round(performance.memory.usedJSHeapSize / 1024 / 1024); // Convert to MB
    } else {
      throw new Error('Feature not implemented: Real memory monitoring requires platform-specific APIs');
    }
  }

  canLoadModel(modelSize = 2000) {
    const currentMemory = this.getMemoryUsage();
    const projectedMemory = currentMemory + modelSize;
    
    // Check memory budget
    if (projectedMemory > this.powerBudget.maxMemoryUsage) {
      console.log(`❌ Model load denied: Memory budget exceeded (${projectedMemory}MB > ${this.powerBudget.maxMemoryUsage}MB)`);
      return false;
    }
    
    // Check concurrent model limit
    if (this.telemetry.modelActivations.size >= this.powerBudget.maxConcurrentModels) {
      console.log(`❌ Model load denied: Concurrent model limit exceeded (${this.telemetry.modelActivations.size} >= ${this.powerBudget.maxConcurrentModels})`);
      return false;
    }
    
    // Check thermal state
    if (this.currentState.thermalShutdownActive) {
      console.log('❌ Model load denied: Emergency thermal shutdown active');
      return false;
    }
    
    if (this.currentState.isThrottling) {
      console.log('⚠️ Model load throttled: Thermal throttling active');
      return false;
    }
    
    return true;
  }

  addPowerEnforcementCallback(callback) {
    this.powerEnforcementCallbacks.push(callback);
  }

  updatePowerBudget(newBudget) {
    this.powerBudget = { ...this.powerBudget, ...newBudget };
    this.telemetry.logSentryEvent('power_budget_updated', newBudget, 'info');
  }

  getPowerStatus() {
    return {
      budget: this.powerBudget,
      currentState: this.currentState,
      memoryUsage: this.getMemoryUsage(),
      systemTemperature: this.getSystemTemperature(),
      gpuTemperature: this.getGPUTemperature(),
      activeModels: this.telemetry.modelActivations.size,
      canLoadModel: this.canLoadModel(),
      lastThermalCheck: this.currentState.lastThermalCheck
    };
  }

  shutdown() {
    if (this.thermalMonitor) {
      clearInterval(this.thermalMonitor);
      this.thermalMonitor = null;
    }
  }
}

export class SpriteEngine {
  constructor() {
    this.vault = new Vault('sprite_engine');
    this.activeSprites = new Map();
    this.heavyLLMPool = new Map();
    this.currentTask = null;
    this.isInitialized = false;
    
    // Initialize Sentry telemetry
    this.telemetry = new SentryTelemetry();
    
    // Initialize power management
    this.powerManager = new PowerManager(this.telemetry);
    
    // Sprite Light configuration
    this.config = {
      confidenceThreshold: 0.75,
      escalationEnabled: true,
      maxRetries: 2,
      swapTimeout: 10000,
      memoryIsolation: true,
      auditLogging: true
    };
    
    // Sprite roster with conversational capabilities
    this.spriteRoster = {
      routing: {
        name: 'Router Sprite',
        model: 'llama3.2:3b',
        type: 'micro',
        capabilities: ['intent_classification', 'persona_routing', 'task_delegation'],
        systemPrompt: 'You are a routing specialist who interprets user requests and determines which AI persona (Alden, Alice, etc.) should handle the task. Respond with the target persona and a brief explanation of why.',
        alwaysLoaded: true
      },
      voice: {
        name: 'Voice Command Sprite',
        model: 'llama3.2:3b', 
        type: 'micro',
        capabilities: ['voice_interpretation', 'natural_language_processing', 'intent_extraction'],
        systemPrompt: 'You specialize in interpreting voice commands and natural speech. Convert voice input into clear, actionable requests that AI personas can understand and execute.',
        alwaysLoaded: true
      },
      quick: {
        name: 'Quick Response Sprite',
        model: 'llama3.2:3b',
        type: 'micro', 
        capabilities: ['simple_qa', 'quick_facts', 'basic_assistance'],
        systemPrompt: 'You handle quick, simple questions and basic assistance. If a request seems complex or requires deep reasoning, escalate to a Heavy-LLM persona.',
        alwaysLoaded: false
      },
      security: {
        name: 'Security Validation Sprite',
        model: 'llama3.2:3b',
        type: 'micro',
        capabilities: ['safety_assessment', 'permission_validation', 'risk_evaluation'],
        systemPrompt: 'You evaluate requests for potential security risks or system modifications. Flag anything that needs user confirmation before execution.',
        alwaysLoaded: false
      },
      context: {
        name: 'Context Management Sprite', 
        model: 'llama3.2:3b',
        type: 'micro',
        capabilities: ['context_switching', 'session_management', 'memory_coordination'],
        systemPrompt: 'You manage conversation context and coordinate between different AI personas. Ensure smooth handoffs and maintain conversation continuity.',
        alwaysLoaded: false
      }
    };
    
    // Heavy-LLM reasoning engines
    this.heavyLLMEngines = {
      reasoning: {
        name: 'Reasoning Engine',
        model: 'llama3:latest',
        type: 'heavy',
        capabilities: ['complex_reasoning', 'analysis', 'problem_solving'],
        roles: ['alden_complex', 'alice_analysis'],
        hotSwappable: true
      },
      coding: {
        name: 'Code Engine', 
        model: 'codellama:7b-instruct',
        type: 'heavy',
        capabilities: ['code_generation', 'debugging', 'technical_assistance'],
        roles: ['alden_coding', 'technical_tasks'],
        hotSwappable: true
      },
      creative: {
        name: 'Creative Engine',
        model: 'mistral:7b-instruct', 
        type: 'heavy',
        capabilities: ['creative_writing', 'content_generation', 'ideation'],
        roles: ['alden_creative', 'content_tasks'],
        hotSwappable: true
      }
    };
  }

  async initialize() {
    try {
      console.log('🚀 Initializing Sprite Engine...');
      
      // Load configuration from Vault
      await this.loadConfiguration();
      
      // Initialize always-loaded Sprites
      await this.initializeAlwaysLoadedSprites();
      
      // Setup power management callbacks
      this.setupPowerManagement();
      
      // Setup audit logging
      if (this.config.auditLogging) {
        await this.initializeAuditLogging();
      }
      
      this.isInitialized = true;
      console.log('✅ Sprite Engine initialized successfully');
      
      return {
        success: true,
        activeSprites: Array.from(this.activeSprites.keys()),
        availableEngines: Object.keys(this.heavyLLMEngines),
        powerStatus: this.powerManager.getPowerStatus()
      };
      
    } catch (error) {
      console.error('❌ Failed to initialize Sprite Engine:', error);
      throw new Error(`Sprite Engine initialization failed: ${error.message}`);
    }
  }

  setupPowerManagement() {
    // Register power enforcement callback
    this.powerManager.addPowerEnforcementCallback(async (eventType, data) => {
      switch (eventType) {
        case 'emergency_shutdown':
          await this.handleEmergencyShutdown(data);
          break;
        case 'memory_pressure':
          await this.handleMemoryPressure(data);
          break;
        case 'throttle_enable':
          await this.handleThermalThrottling(true, data);
          break;
        case 'throttle_disable':
          await this.handleThermalThrottling(false, data);
          break;
      }
    });
  }

  async handleEmergencyShutdown(data) {
    console.log('🚨 Sprite Engine: Emergency shutdown triggered');
    
    // Immediately unload all Heavy-LLM engines
    await this.unloadAllHeavyLLM();
    
    // Log emergency event
    await this.auditLog('emergency_shutdown', {
      reason: data.reason,
      temperature: data.temperature,
      activeModels: Array.from(this.heavyLLMPool.keys())
    });
  }

  async handleMemoryPressure(data) {
    console.log('🔥 Sprite Engine: Handling memory pressure');
    
    // Unload least recently used Heavy-LLM engines
    const engines = Array.from(this.heavyLLMPool.entries())
      .sort(([,a], [,b]) => a.loadedAt - b.loadedAt);
    
    // Unload oldest engines until memory pressure is reduced
    const targetUnloads = Math.ceil(engines.length / 2);
    for (let i = 0; i < targetUnloads && i < engines.length; i++) {
      const [engineId] = engines[i];
      await this.gracefulEngineUnload(engineId);
    }
  }

  async handleThermalThrottling(enabled, data) {
    if (enabled) {
      console.log('🔥 Sprite Engine: Thermal throttling enabled');
      // Reduce concurrent model limit
      this.powerManager.updatePowerBudget({ maxConcurrentModels: 1 });
    } else {
      console.log('❄️ Sprite Engine: Thermal throttling disabled');
      // Restore normal concurrent model limit
      this.powerManager.updatePowerBudget({ maxConcurrentModels: 2 });
    }
  }

  async loadConfiguration() {
    try {
      const savedConfig = await this.vault.retrieve('sprite_config');
      if (savedConfig) {
        this.config = { ...this.config, ...savedConfig };
        console.log('📋 Loaded Sprite configuration from Vault');
      }
    } catch (error) {
      console.warn('⚠️ Using default Sprite configuration:', error.message);
    }
  }

  async initializeAlwaysLoadedSprites() {
    const alwaysLoaded = Object.entries(this.spriteRoster)
      .filter(([_, sprite]) => sprite.alwaysLoaded);
    
    for (const [spriteId, sprite] of alwaysLoaded) {
      try {
        await this.loadSprite(spriteId);
        console.log(`✅ Always-loaded Sprite ready: ${sprite.name}`);
      } catch (error) {
        console.error(`❌ Failed to load Sprite ${spriteId}:`, error);
      }
    }
  }

  async initializeAuditLogging() {
    const auditEntry = {
      timestamp: new Date().toISOString(),
      event: 'sprite_engine_initialized',
      details: {
        activeSprites: Array.from(this.activeSprites.keys()),
        configuration: this.config
      }
    };
    
    await this.vault.store('audit_log', auditEntry);
  }

  /**
   * Process a conversational request through the Sprite Light architecture
   */
  async processConversationalRequest(request) {
    try {
      const taskId = this.generateTaskId();
      console.log(`🗣️ Processing conversational request [${taskId}]:`, request.text?.substring(0, 50) + '...');
      
      // Step 1: Route through Voice Sprite if it's a voice input
      let processedRequest = request;
      if (request.inputType === 'voice') {
        processedRequest = await this.processVoiceInput(request);
      }
      
      // Step 2: Determine intent and target persona through Router Sprite
      const routingDecision = await this.routeRequest(processedRequest);
      
      // Step 3: Security validation for potentially troublesome actions
      const securityCheck = await this.validateSecurity(processedRequest, routingDecision);
      
      // Step 4: Execute through appropriate persona/engine
      const result = await this.executeRequest(processedRequest, routingDecision, securityCheck);
      
      // Step 5: Audit logging
      await this.logTaskExecution(taskId, processedRequest, routingDecision, result);
      
      return result;
      
    } catch (error) {
      console.error('❌ Failed to process conversational request:', error);
      return {
        success: false,
        error: error.message,
        fallback: 'I apologize, but I encountered an issue processing your request. Could you please try rephrasing it?'
      };
    }
  }

  async processVoiceInput(request) {
    const voiceSprite = this.activeSprites.get('voice');
    if (!voiceSprite) {
      await this.loadSprite('voice');
    }
    
    const voiceProcessingResult = await this.callSprite('voice', {
      text: request.text,
      audioMetadata: request.audioMetadata,
      task: 'interpret_voice_input'
    });
    
    return {
      ...request,
      interpretedText: voiceProcessingResult.interpretation,
      confidence: voiceProcessingResult.confidence,
      extractedIntent: voiceProcessingResult.intent
    };
  }

  async routeRequest(request) {
    const routerSprite = this.activeSprites.get('routing');
    
    const routingResult = await this.callSprite('routing', {
      text: request.interpretedText || request.text,
      context: request.context,
      task: 'determine_routing'
    });
    
    // Parse routing decision
    const decision = {
      targetPersona: routingResult.targetPersona || 'alden', // Default to Alden
      reasoning: routingResult.reasoning,
      confidence: routingResult.confidence,
      requiredEngine: routingResult.requiredEngine || 'reasoning',
      escalationRecommended: routingResult.confidence < this.config.confidenceThreshold
    };
    
    console.log(`🎯 Routing decision: ${decision.targetPersona} (confidence: ${decision.confidence})`);
    
    return decision;
  }

  async validateSecurity(request, routingDecision) {
    // Load security sprite if needed
    if (!this.activeSprites.has('security')) {
      await this.loadSprite('security');
    }
    
    const securityResult = await this.callSprite('security', {
      text: request.interpretedText || request.text,
      targetPersona: routingDecision.targetPersona,
      requiredEngine: routingDecision.requiredEngine,
      task: 'assess_security_risk'
    });
    
    const validation = {
      riskLevel: securityResult.riskLevel || 'low',
      requiresConfirmation: securityResult.requiresConfirmation || false,
      flaggedConcerns: securityResult.concerns || [],
      recommendations: securityResult.recommendations || []
    };
    
    if (validation.requiresConfirmation) {
      console.log(`⚠️ Security validation flagged request for confirmation:`, validation.flaggedConcerns);
    }
    
    return validation;
  }

  async executeRequest(request, routingDecision, securityCheck) {
    // If security check requires confirmation and it's not provided, return confirmation request
    if (securityCheck.requiresConfirmation && !request.confirmationProvided) {
      return {
        success: true,
        requiresConfirmation: true,
        confirmationMessage: `I need to confirm: ${securityCheck.flaggedConcerns.join(', ')}. Should I proceed?`,
        securityDetails: securityCheck
      };
    }
    
    // Determine if we need Heavy-LLM escalation
    if (routingDecision.escalationRecommended && this.config.escalationEnabled) {
      console.log(`⬆️ Escalating to Heavy-LLM engine: ${routingDecision.requiredEngine}`);
      return await this.executeWithHeavyLLM(request, routingDecision);
    } else {
      // Try with Sprites first
      const spriteResult = await this.executeWithSprites(request, routingDecision);
      
      // Check if Sprite result meets confidence threshold
      if (spriteResult.confidence < this.config.confidenceThreshold && this.config.escalationEnabled) {
        console.log(`⬆️ Sprite confidence low (${spriteResult.confidence}), escalating to Heavy-LLM`);
        return await this.executeWithHeavyLLM(request, routingDecision);
      }
      
      return spriteResult;
    }
  }

  async executeWithSprites(request, routingDecision) {
    // Use Quick Response Sprite for simple tasks
    if (!this.activeSprites.has('quick')) {
      await this.loadSprite('quick');
    }
    
    const result = await this.callSprite('quick', {
      text: request.interpretedText || request.text,
      targetPersona: routingDecision.targetPersona,
      context: request.context,
      task: 'handle_simple_request'
    });
    
    return {
      success: true,
      response: result.response,
      confidence: result.confidence,
      source: 'sprite',
      spriteUsed: 'quick',
      persona: routingDecision.targetPersona
    };
  }

  async executeWithHeavyLLM(request, routingDecision) {
    const startTime = Date.now();
    let success = false;
    
    try {
      // Load appropriate Heavy-LLM engine
      const engine = await this.loadHeavyLLM(routingDecision.requiredEngine);
      
      // Execute with Heavy-LLM through Local LLM API
      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: request.interpretedText || request.text,
          task_type: routingDecision.requiredEngine,
          profile: 'heavy',
          context: {
            persona: routingDecision.targetPersona,
            engine: routingDecision.requiredEngine
          }
        })
      });
      
      const result = await response.json();
      success = true;
      
      const processingTime = Date.now() - startTime;
      
      // Record telemetry
      this.telemetry.recordModelRequest(routingDecision.requiredEngine, processingTime, success);
      
      return {
        success: true,
        response: result.response,
        confidence: 0.9, // Heavy-LLM assumed high confidence
        source: 'heavy_llm',
        engine: routingDecision.requiredEngine,
        model: result.model,
        processingTime: result.processing_time || processingTime,
        persona: routingDecision.targetPersona
      };
      
    } catch (error) {
      const processingTime = Date.now() - startTime;
      
      // Record failed telemetry
      this.telemetry.recordModelRequest(routingDecision.requiredEngine, processingTime, false);
      
      console.error('❌ Heavy-LLM execution failed:', error);
      throw new Error(`Heavy-LLM execution failed: ${error.message}`);
    }
  }

  async callSprite(spriteId, params) {
    try {
      const sprite = this.spriteRoster[spriteId];
      if (!sprite) {
        throw new Error(`Unknown sprite: ${spriteId}`);
      }

      // Check if sprite is loaded and active
      const loadedSprite = this.activeSprites.get(spriteId);
      if (!loadedSprite || loadedSprite.status !== 'active') {
        throw new Error(`Feature not implemented: Sprite ${spriteId} not loaded or failed to load`);
      }
      
      // Real Sprite API call
      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `${sprite.systemPrompt}\n\nUser request: ${params.text}`,
          task_type: 'routing',
          profile: 'micro',
          model: sprite.model
        })
      });
      
      if (!response.ok) {
        throw new Error(`Feature not implemented: Sprite API unavailable (HTTP ${response.status})`);
      }
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(`Feature not implemented: Sprite processing failed - ${result.error || 'Unknown error'}`);
      }
      
      // Real confidence calculation based on API response
      const confidence = result.confidence || (result.response ? 0.8 : 0.3);
      
      return {
        response: result.response,
        confidence: confidence,
        interpretation: result.response,
        targetPersona: this.extractPersonaFromResponse(result.response),
        requiredEngine: this.extractEngineFromResponse(result.response),
        riskLevel: result.risk_level || 'low',
        requiresConfirmation: this.checkForSensitiveContent(params.text)
      };
      
    } catch (error) {
      console.error(`❌ Sprite call failed [${spriteId}]:`, error);
      // Don't hide the real error - expose implementation gaps
      throw new Error(`Feature not implemented: Sprite system not functional - ${error.message}`);
    }
  }

  extractPersonaFromResponse(response) {
    const text = response.toLowerCase();
    if (text.includes('alice') || text.includes('analysis')) return 'alice';
    if (text.includes('alden') || text.includes('assistant')) return 'alden';
    return 'alden'; // Default
  }

  extractEngineFromResponse(response) {
    const text = response.toLowerCase();
    if (text.includes('code') || text.includes('programming')) return 'coding';
    if (text.includes('creative') || text.includes('writing')) return 'creative';
    return 'reasoning'; // Default
  }

  checkForSensitiveContent(text) {
    const sensitiveKeywords = ['delete', 'remove', 'uninstall', 'format', 'reset', 'shutdown'];
    return sensitiveKeywords.some(keyword => text.toLowerCase().includes(keyword));
  }

  async loadSprite(spriteId) {
    const sprite = this.spriteRoster[spriteId];
    if (!sprite) {
      throw new Error(`Unknown sprite: ${spriteId}`);
    }
    
    console.log(`🔄 Loading Sprite: ${sprite.name}`);
    
    try {
      // Real sprite loading through model API
      await this.callModelLoadAPI(sprite.model);
      
      this.activeSprites.set(spriteId, {
        ...sprite,
        loadedAt: Date.now(),
        status: 'active'
      });
      
      await this.auditLog('sprite_loaded', { spriteId, name: sprite.name });
    } catch (error) {
      console.error(`❌ Failed to load sprite ${spriteId}:`, error);
      
      // Mark as failed, don't pretend it worked
      this.activeSprites.set(spriteId, {
        ...sprite,
        loadedAt: Date.now(),
        status: 'failed',
        error: error.message
      });
      
      throw error;
    }
  }

  async loadHeavyLLM(engineId) {
    const engine = this.heavyLLMEngines[engineId];
    if (!engine) {
      throw new Error(`Unknown Heavy-LLM engine: ${engineId}`);
    }
    
    // Check power budget before loading
    if (!this.powerManager.canLoadModel()) {
      const powerStatus = this.powerManager.getPowerStatus();
      throw new Error(`Cannot load model: Power budget constraints. Status: ${JSON.stringify(powerStatus.currentState)}`);
    }
    
    // Check if already loaded and active
    if (this.heavyLLMPool.has(engineId)) {
      const existingEngine = this.heavyLLMPool.get(engineId);
      if (existingEngine.status === 'active') {
        console.log(`✅ Heavy-LLM engine already active: ${engine.name}`);
        return existingEngine;
      }
    }
    
    console.log(`🔄 Hot-swapping Heavy-LLM engine: ${engine.name}`);
    
    try {
      // Step 1: Memory isolation - prepare for GPU context reset
      if (this.config.memoryIsolation) {
        await this.prepareMemoryIsolation(engineId);
      }
      
      // Step 2: Gracefully unload conflicting engines
      await this.performHotSwap(engineId);
      
      // Step 3: Load new engine with timeout protection
      const loadedEngine = await this.performEngineLoad(engineId, engine);
      
      // Step 4: Verify engine is responding
      await this.verifyEngineHealth(engineId);
      
      console.log(`✅ Heavy-LLM engine hot-swap completed: ${engine.name}`);
      return loadedEngine;
      
    } catch (error) {
      console.error(`❌ Hot-swap failed for ${engine.name}:`, error);
      await this.auditLog('heavy_llm_swap_failed', { 
        engineId, 
        name: engine.name, 
        error: error.message 
      });
      throw new Error(`Hot-swap failed: ${error.message}`);
    }
  }

  async prepareMemoryIsolation(targetEngineId) {
    const activeEngines = Array.from(this.heavyLLMPool.keys());
    
    if (activeEngines.length > 0) {
      console.log(`🧹 Preparing memory isolation for GPU context reset...`);
      
      // Mark engines for unloading
      for (const engineId of activeEngines) {
        if (engineId !== targetEngineId) {
          const engine = this.heavyLLMPool.get(engineId);
          engine.status = 'unloading';
          this.heavyLLMPool.set(engineId, engine);
        }
      }
      
      await this.auditLog('memory_isolation_prepared', { 
        unloadingEngines: activeEngines.filter(id => id !== targetEngineId),
        targetEngine: targetEngineId 
      });
    }
  }

  async performHotSwap(targetEngineId) {
    const unloadPromises = [];
    
    for (const [engineId, engine] of this.heavyLLMPool.entries()) {
      if (engineId !== targetEngineId && engine.status !== 'unloading') {
        unloadPromises.push(this.gracefulEngineUnload(engineId));
      }
    }
    
    if (unloadPromises.length > 0) {
      console.log(`🔄 Hot-swapping ${unloadPromises.length} engines...`);
      await Promise.allSettled(unloadPromises);
    }
  }

  async gracefulEngineUnload(engineId) {
    const engine = this.heavyLLMPool.get(engineId);
    if (!engine) return;
    
    try {
      console.log(`🗑️ Gracefully unloading: ${engine.name}`);
      
      // Set status to unloading
      engine.status = 'unloading';
      this.heavyLLMPool.set(engineId, engine);
      
      // In full implementation: Call model unload API
      await this.callModelUnloadAPI(engine.model);
      
      // Remove from pool
      this.heavyLLMPool.delete(engineId);
      
      const sessionDuration = Date.now() - engine.loadedAt;
      
      await this.auditLog('heavy_llm_gracefully_unloaded', { 
        engineId, 
        name: engine.name,
        loadDuration: sessionDuration
      });
      
      // Record telemetry
      this.telemetry.recordModelDeactivation(engineId, sessionDuration);
      
    } catch (error) {
      console.error(`❌ Failed to gracefully unload ${engine.name}:`, error);
      // Force removal even if unload failed
      this.heavyLLMPool.delete(engineId);
    }
  }

  async performEngineLoad(engineId, engine) {
    const loadStartTime = Date.now();
    
    // Set loading status
    const loadingEngine = {
      ...engine,
      loadedAt: loadStartTime,
      status: 'loading'
    };
    this.heavyLLMPool.set(engineId, loadingEngine);
    
    try {
      // In full implementation: Call model load API with timeout
      await Promise.race([
        this.callModelLoadAPI(engine.model),
        this.createSwapTimeout()
      ]);
      
      // Mark as active
      loadingEngine.status = 'active';
      loadingEngine.loadCompletedAt = Date.now();
      this.heavyLLMPool.set(engineId, loadingEngine);
      
      const finalLoadDuration = Date.now() - loadStartTime;
      
      await this.auditLog('heavy_llm_loaded', { 
        engineId, 
        name: engine.name,
        loadDuration: finalLoadDuration
      });
      
      // Record telemetry
      this.telemetry.recordModelActivation(engineId, engine, finalLoadDuration);
      
      return loadingEngine;
      
    } catch (error) {
      // Clean up failed load
      this.heavyLLMPool.delete(engineId);
      throw error;
    }
  }

  async verifyEngineHealth(engineId) {
    const engine = this.heavyLLMPool.get(engineId);
    if (!engine) {
      throw new Error(`Engine ${engineId} not found after load`);
    }
    
    try {
      // Health check with simple test query
      const healthCheck = await fetch('http://localhost:8001/api/health', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: engine.model,
          test_query: 'Health check'
        }),
        timeout: 5000
      });
      
      if (!healthCheck.ok) {
        throw new Error(`Engine health check failed: ${healthCheck.status}`);
      }
      
      console.log(`✅ Engine health verified: ${engine.name}`);
      await this.auditLog('engine_health_verified', { engineId, name: engine.name });
      
    } catch (error) {
      console.error(`❌ Engine health check failed for ${engine.name}:`, error);
      engine.status = 'unhealthy';
      this.heavyLLMPool.set(engineId, engine);
      throw new Error(`Engine health verification failed: ${error.message}`);
    }
  }

  async callModelLoadAPI(modelName) {
    // Real model loading through Local LLM API
    try {
      const response = await fetch('http://localhost:8001/api/models/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelName }),
        timeout: 30000
      });

      if (!response.ok) {
        throw new Error(`Model load failed: HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log(`📥 Model loaded: ${modelName}`);
      return result;
    } catch (error) {
      console.error(`❌ Model load failed: ${error.message}`);
      throw new Error(`Feature not implemented: Real model loading API not available. ${error.message}`);
    }
  }

  async callModelUnloadAPI(modelName) {
    // Real model unloading through Local LLM API
    try {
      const response = await fetch('http://localhost:8001/api/models/unload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelName }),
        timeout: 10000
      });

      if (!response.ok) {
        throw new Error(`Model unload failed: HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log(`📤 Model unloaded: ${modelName}`);
      return result;
    } catch (error) {
      console.error(`❌ Model unload failed: ${error.message}`);
      throw new Error(`Feature not implemented: Real model unloading API not available. ${error.message}`);
    }
  }

  createSwapTimeout() {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Model swap timeout after ${this.config.swapTimeout}ms`));
      }, this.config.swapTimeout);
    });
  }

  async unloadAllHeavyLLM() {
    const unloadPromises = [];
    
    for (const [engineId, engine] of this.heavyLLMPool.entries()) {
      unloadPromises.push(this.gracefulEngineUnload(engineId));
    }
    
    if (unloadPromises.length > 0) {
      console.log(`🗑️ Unloading all ${unloadPromises.length} Heavy-LLM engines...`);
      await Promise.allSettled(unloadPromises);
    }
  }

  async auditLog(event, details) {
    if (!this.config.auditLogging) return;
    
    const logEntry = {
      timestamp: new Date().toISOString(),
      event,
      details,
      sessionId: this.getSessionId()
    };
    
    try {
      const existingLogs = await this.vault.retrieve('audit_logs') || [];
      existingLogs.push(logEntry);
      
      // Keep only last 1000 entries
      if (existingLogs.length > 1000) {
        existingLogs.splice(0, existingLogs.length - 1000);
      }
      
      await this.vault.store('audit_logs', existingLogs);
    } catch (error) {
      console.error('❌ Failed to write audit log:', error);
    }
  }

  async logTaskExecution(taskId, request, routing, result) {
    await this.auditLog('task_executed', {
      taskId,
      inputType: request.inputType,
      targetPersona: routing.targetPersona,
      confidence: routing.confidence,
      escalated: routing.escalationRecommended,
      source: result.source,
      success: result.success
    });
  }

  generateTaskId() {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getSessionId() {
    // Basic session ID generation - session manager not implemented
    try {
      // Try to get session from vault or window context
      if (typeof window !== 'undefined' && window.sessionAPI && window.sessionAPI.getSessionId) {
        return window.sessionAPI.getSessionId();
      } else {
        // Fallback to timestamp-based ID
        console.warn('Feature not implemented: Centralized session management not available');
        return 'session_' + Date.now();
      }
    } catch (error) {
      console.warn('Session ID generation fallback:', error.message);
      return 'session_' + Date.now();
    }
  }

  // Public API methods
  getActiveSprites() {
    return Array.from(this.activeSprites.entries()).map(([id, sprite]) => ({
      id,
      name: sprite.name,
      status: sprite.status,
      loadedAt: sprite.loadedAt
    }));
  }

  getLoadedEngines() {
    return Array.from(this.heavyLLMPool.entries()).map(([id, engine]) => ({
      id,
      name: engine.name,
      status: engine.status,
      loadedAt: engine.loadedAt,
      loadCompletedAt: engine.loadCompletedAt,
      loadDuration: engine.loadCompletedAt ? engine.loadCompletedAt - engine.loadedAt : null,
      model: engine.model,
      capabilities: engine.capabilities,
      hotSwappable: engine.hotSwappable
    }));
  }

  /**
   * Get detailed hot-swap metrics and status
   */
  getHotSwapStatus() {
    const engines = this.getLoadedEngines();
    const activeEngines = engines.filter(e => e.status === 'active');
    const loadingEngines = engines.filter(e => e.status === 'loading');
    const unhealthyEngines = engines.filter(e => e.status === 'unhealthy');
    
    return {
      totalEngines: engines.length,
      activeEngines: activeEngines.length,
      loadingEngines: loadingEngines.length,
      unhealthyEngines: unhealthyEngines.length,
      memoryIsolationEnabled: this.config.memoryIsolation,
      swapTimeout: this.config.swapTimeout,
      engines: engines,
      lastSwapTime: this.getLastSwapTime(),
      averageLoadTime: this.calculateAverageLoadTime(engines)
    };
  }

  getLastSwapTime() {
    const engines = Array.from(this.heavyLLMPool.values());
    if (engines.length === 0) return null;
    
    return Math.max(...engines.map(e => e.loadedAt || 0));
  }

  calculateAverageLoadTime(engines) {
    const completedEngines = engines.filter(e => e.loadDuration !== null);
    if (completedEngines.length === 0) return null;
    
    const totalTime = completedEngines.reduce((sum, e) => sum + e.loadDuration, 0);
    return Math.round(totalTime / completedEngines.length);
  }

  async updateConfiguration(newConfig) {
    this.config = { ...this.config, ...newConfig };
    await this.vault.store('sprite_config', this.config);
    await this.auditLog('config_updated', newConfig);
  }

  getConfiguration() {
    return { ...this.config };
  }

  /**
   * Get power metrics and telemetry data
   */
  getPowerMetrics() {
    return this.telemetry.getPowerMetrics();
  }

  /**
   * Get model activation summary for monitoring
   */
  getModelActivationSummary() {
    return this.telemetry.getModelActivationSummary();
  }

  /**
   * Record thermal event for monitoring
   */
  recordThermalEvent(eventType, temperature, throttling = false) {
    this.telemetry.recordThermalEvent(eventType, temperature, throttling);
  }

  /**
   * Update memory usage metrics
   */
  updateMemoryUsage(memoryUsage) {
    this.telemetry.updateMemoryUsage(memoryUsage);
  }

  /**
   * Get comprehensive telemetry report
   */
  getTelemetryReport() {
    return {
      powerMetrics: this.getPowerMetrics(),
      activationSummary: this.getModelActivationSummary(),
      hotSwapStatus: this.getHotSwapStatus(),
      powerStatus: this.getPowerStatus(),
      systemHealth: {
        activeSprites: this.getActiveSprites().length,
        loadedEngines: this.getLoadedEngines().length,
        configurationValid: Boolean(this.config),
        vaultConnected: Boolean(this.vault),
        lastUpdate: new Date().toISOString()
      }
    };
  }

  /**
   * Get power management status
   */
  getPowerStatus() {
    return this.powerManager.getPowerStatus();
  }

  /**
   * Update power budget settings
   */
  async updatePowerBudget(newBudget) {
    this.powerManager.updatePowerBudget(newBudget);
    await this.auditLog('power_budget_updated', newBudget);
  }

  /**
   * Check if a model can be loaded under current power constraints
   */
  canLoadModel(modelSize) {
    return this.powerManager.canLoadModel(modelSize);
  }

  /**
   * Shutdown power management and cleanup
   */
  async shutdown() {
    console.log('🔌 Shutting down Sprite Engine...');
    
    // Shutdown power manager
    this.powerManager.shutdown();
    
    // Unload all models
    await this.unloadAllHeavyLLM();
    
    // Clear active sprites
    this.activeSprites.clear();
    
    await this.auditLog('sprite_engine_shutdown', {
      timestamp: new Date().toISOString()
    });
  }
}

export default SpriteEngine;