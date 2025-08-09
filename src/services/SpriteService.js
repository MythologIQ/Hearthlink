/**
 * Sprite Service - Integration layer for Sprite Light architecture
 * 
 * Provides a service interface for components to interact with the Sprite Engine
 * and handles conversational AI routing throughout the application.
 */

import SpriteEngine from '../core/SpriteEngine.js';

class SpriteService {
  constructor() {
    this.spriteEngine = null;
    this.isInitialized = false;
    this.initializationPromise = null;
  }

  async initialize() {
    if (this.isInitialized) {
      return this.spriteEngine;
    }

    if (this.initializationPromise) {
      return this.initializationPromise;
    }

    this.initializationPromise = this._doInitialize();
    return this.initializationPromise;
  }

  async _doInitialize() {
    try {
      console.log('🎯 Starting Sprite Service initialization...');
      
      this.spriteEngine = new SpriteEngine();
      await this.spriteEngine.initialize();
      
      this.isInitialized = true;
      console.log('✅ Sprite Service initialized successfully');
      
      return this.spriteEngine;
    } catch (error) {
      console.error('❌ Sprite Service initialization failed:', error);
      this.initializationPromise = null;
      throw error;
    }
  }

  /**
   * Process a conversational request from any component
   */
  async processRequest(options = {}) {
    await this.initialize();
    
    const request = {
      text: options.text || options.message || '',
      inputType: options.inputType || 'text',
      context: options.context || {},
      audioMetadata: options.audioMetadata,
      confirmationProvided: options.confirmationProvided || false,
      source: options.source || 'unknown'
    };

    return await this.spriteEngine.processConversationalRequest(request);
  }

  /**
   * Process voice input specifically
   */
  async processVoiceRequest(audioInput, context = {}) {
    return await this.processRequest({
      text: audioInput.transcript || audioInput.text,
      inputType: 'voice',
      context,
      audioMetadata: {
        duration: audioInput.duration,
        confidence: audioInput.confidence,
        language: audioInput.language
      },
      source: 'voice_interface'
    });
  }

  /**
   * Process text input from UI components
   */
  async processTextRequest(text, context = {}, source = 'ui') {
    return await this.processRequest({
      text,
      inputType: 'text',
      context,
      source
    });
  }

  /**
   * Handle confirmation responses for security-flagged requests
   */
  async processConfirmation(originalRequest, confirmed) {
    const request = {
      ...originalRequest,
      confirmationProvided: confirmed
    };

    if (!confirmed) {
      return {
        success: true,
        response: 'Understood. I won\'t proceed with that action.',
        cancelled: true
      };
    }

    return await this.processRequest(request);
  }

  /**
   * Route request to specific persona (Alden, Alice, etc.)
   */
  async routeToPersona(text, targetPersona, context = {}) {
    return await this.processRequest({
      text,
      inputType: 'text',
      context: {
        ...context,
        explicitPersona: targetPersona
      },
      source: 'persona_routing'
    });
  }

  /**
   * Get current Sprite Engine status
   */
  async getStatus() {
    if (!this.isInitialized) {
      return {
        initialized: false,
        error: 'Sprite Service not initialized'
      };
    }

    return {
      initialized: true,
      activeSprites: this.spriteEngine.getActiveSprites(),
      loadedEngines: this.spriteEngine.getLoadedEngines(),
      configuration: this.spriteEngine.getConfiguration()
    };
  }

  /**
   * Update Sprite Engine configuration
   */
  async updateConfiguration(config) {
    await this.initialize();
    return await this.spriteEngine.updateConfiguration(config);
  }

  /**
   * Integration with existing Alden interface
   */
  async handleAldenRequest(message, context = {}) {
    const result = await this.processRequest({
      text: message,
      inputType: 'text',
      context: {
        ...context,
        explicitPersona: 'alden',
        interface: 'alden_main'
      },
      source: 'alden_interface'
    });

    // Format response for Alden interface compatibility
    return {
      success: result.success,
      response: result.response,
      requiresConfirmation: result.requiresConfirmation,
      confirmationMessage: result.confirmationMessage,
      metadata: {
        source: result.source,
        confidence: result.confidence,
        persona: result.persona,
        processingTime: result.processingTime
      }
    };
  }

  /**
   * Integration with Alice interface
   */
  async handleAliceRequest(message, context = {}) {
    const result = await this.processRequest({
      text: message,
      inputType: 'text',
      context: {
        ...context,
        explicitPersona: 'alice',
        interface: 'alice_analysis'
      },
      source: 'alice_interface'
    });

    return {
      success: result.success,
      response: result.response,
      analysisData: result.analysisData,
      metadata: {
        source: result.source,
        confidence: result.confidence,
        engine: result.engine
      }
    };
  }

  /**
   * Voice command processing for global voice interface
   */
  async handleVoiceCommand(voiceInput) {
    try {
      const result = await this.processVoiceRequest(voiceInput, {
        interface: 'global_voice',
        timestamp: Date.now()
      });

      // Handle confirmation dialogs for voice
      if (result.requiresConfirmation) {
        return {
          ...result,
          voiceResponse: result.confirmationMessage,
          awaitingConfirmation: true
        };
      }

      return {
        ...result,
        voiceResponse: result.response
      };

    } catch (error) {
      console.error('❌ Voice command processing failed:', error);
      return {
        success: false,
        error: error.message,
        voiceResponse: 'I apologize, but I had trouble processing your voice command. Could you please try again?'
      };
    }
  }

  /**
   * Emergency fallback when Sprite Engine fails
   */
  getFallbackResponse(inputText) {
    const fallbacks = [
      "I'm experiencing some technical difficulties right now. Let me try to help you in a simpler way.",
      "My advanced processing systems are temporarily unavailable. How can I assist you with basic tasks?",
      "I'm running in simplified mode. Please let me know how I can help with straightforward requests."
    ];
    
    return {
      success: true,
      response: fallbacks[Math.floor(Math.random() * fallbacks.length)],
      source: 'fallback',
      confidence: 0.5
    };
  }

  /**
   * Health check for monitoring systems
   */
  async healthCheck() {
    try {
      if (!this.isInitialized) {
        return {
          status: 'not_initialized',
          healthy: false
        };
      }

      const status = await this.getStatus();
      const testResult = await this.processRequest({
        text: 'Health check test',
        inputType: 'text',
        context: { test: true },
        source: 'health_check'
      });

      return {
        status: 'healthy',
        healthy: true,
        activeSprites: status.activeSprites.length,
        loadedEngines: status.loadedEngines.length,
        testResponse: testResult.success
      };

    } catch (error) {
      return {
        status: 'error',
        healthy: false,
        error: error.message
      };
    }
  }

  /**
   * Get power metrics and telemetry data
   */
  async getPowerMetrics() {
    await this.initialize();
    return this.spriteEngine.getPowerMetrics();
  }

  /**
   * Get model activation summary
   */
  async getModelActivationSummary() {
    await this.initialize();
    return this.spriteEngine.getModelActivationSummary();
  }

  /**
   * Get hot-swap status and metrics
   */
  async getHotSwapStatus() {
    await this.initialize();
    return this.spriteEngine.getHotSwapStatus();
  }

  /**
   * Get comprehensive telemetry report
   */
  async getTelemetryReport() {
    await this.initialize();
    return this.spriteEngine.getTelemetryReport();
  }

  /**
   * Record thermal event
   */
  async recordThermalEvent(eventType, temperature, throttling = false) {
    await this.initialize();
    return this.spriteEngine.recordThermalEvent(eventType, temperature, throttling);
  }

  /**
   * Update memory usage metrics
   */
  async updateMemoryUsage(memoryUsage) {
    await this.initialize();
    return this.spriteEngine.updateMemoryUsage(memoryUsage);
  }

  /**
   * Get power management status
   */
  async getPowerStatus() {
    await this.initialize();
    return this.spriteEngine.getPowerStatus();
  }

  /**
   * Update power budget settings
   */
  async updatePowerBudget(newBudget) {
    await this.initialize();
    return this.spriteEngine.updatePowerBudget(newBudget);
  }

  /**
   * Check if a model can be loaded under current power constraints
   */
  async canLoadModel(modelSize) {
    await this.initialize();
    return this.spriteEngine.canLoadModel(modelSize);
  }

  /**
   * Shutdown Sprite Service
   */
  async shutdown() {
    if (this.isInitialized) {
      await this.spriteEngine.shutdown();
      this.isInitialized = false;
    }
  }
}

// Create singleton instance
const spriteService = new SpriteService();

export default spriteService;