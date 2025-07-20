/**
 * Task Delegation Service
 * Handles intelligent task routing to available AI services
 */

class TaskDelegationService {
  constructor() {
    this.apiBase = 'http://localhost:8000/api';
    this.services = {
      'alden': { available: false, capabilities: ['conversation', 'reasoning', 'memory'] },
      'alice': { available: false, capabilities: ['analysis', 'problem-solving', 'optimization'] },
      'mimic': { available: false, capabilities: ['adaptation', 'learning', 'pattern-recognition'] },
      'sentry': { available: false, capabilities: ['monitoring', 'security', 'alerting'] }
    };
    this.lastStatusCheck = 0;
    this.statusCheckInterval = 30000; // 30 seconds
  }

  async checkServiceAvailability() {
    try {
      const response = await fetch(`${this.apiBase}/agents`);
      if (response.ok) {
        const data = await response.json();
        // Update service availability based on agent status
        data.agents.forEach(agent => {
          if (this.services[agent.id]) {
            this.services[agent.id].available = agent.status === 'active';
            this.services[agent.id].load = agent.load;
            this.services[agent.id].performance = agent.performance;
            this.services[agent.id].capabilities = agent.capabilities;
          }
        });
        this.lastStatusCheck = Date.now();
        return true;
      }
    } catch (error) {
      console.warn('Failed to check service availability:', error);
    }
    return false;
  }

  async getServiceStatus() {
    const now = Date.now();
    if (now - this.lastStatusCheck > this.statusCheckInterval) {
      await this.checkServiceAvailability();
    }
    return this.services;
  }

  selectBestService(taskType, requirements = {}) {
    const services = Object.entries(this.services)
      .filter(([name, service]) => service.available)
      .filter(([name, service]) => service.capabilities.includes(taskType))
      .sort((a, b) => {
        // Priority order: claude-code > google-ai > ollama
        const priority = { 'claude-code': 3, 'google-ai': 2, 'ollama': 1 };
        return (priority[b[0]] || 0) - (priority[a[0]] || 0);
      });

    return services.length > 0 ? services[0][0] : null;
  }

  async delegateTask(taskType, taskDescription, context = {}) {
    // Ensure services are up to date
    await this.getServiceStatus();

    const bestService = this.selectBestService(taskType, context);
    if (!bestService) {
      return {
        success: false,
        error: 'No suitable service available for this task type',
        taskType,
        availableServices: Object.keys(this.services).filter(s => this.services[s].available)
      };
    }

    try {
      // Create a new project for the task
      const projectResponse = await fetch(`${this.apiBase}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: `Task: ${taskDescription}`,
          description: taskDescription,
          type: taskType,
          assigned_agent: bestService
        })
      });

      if (!projectResponse.ok) {
        throw new Error(`Failed to create project: ${projectResponse.status}`);
      }

      const projectData = await projectResponse.json();
      
      // Start orchestration for the project
      const orchestrationResponse = await fetch(`${this.apiBase}/projects/${projectData.project_id}/orchestrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          context: context,
          priority: 'high'
        })
      });

      const response = orchestrationResponse;

      const result = await response.json();
      
      return {
        ...result,
        service_used: bestService,
        task_type: taskType,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        taskType,
        service_used: bestService
      };
    }
  }

  // Specific task delegation methods
  async analyzeCode(filePath, analysisType = 'general') {
    return await this.delegateTask('code_analysis', `Analyze ${filePath}`, {
      file_path: filePath,
      analysis_type: analysisType
    });
  }

  async generateCode(prompt, language, filePath = null) {
    return await this.delegateTask('code_generation', prompt, {
      language,
      file_path: filePath
    });
  }

  async refactorCode(filePath, refactorType, target = null) {
    return await this.delegateTask('code_refactoring', `Refactor ${filePath}`, {
      file_path: filePath,
      refactor_type: refactorType,
      target
    });
  }

  async explainCode(filePath, lineRange = null) {
    return await this.delegateTask('code_explanation', `Explain ${filePath}`, {
      file_path: filePath,
      line_range: lineRange
    });
  }

  async debugCode(filePath, errorMessage = null) {
    return await this.delegateTask('code_debugging', `Debug ${filePath}`, {
      file_path: filePath,
      error_message: errorMessage
    });
  }

  async generateAIResponse(prompt, context = {}) {
    return await this.delegateTask('ai_response', prompt, context);
  }

  async summarizeText(text, summaryType = 'general') {
    return await this.delegateTask('text_summary', text, {
      summary_type: summaryType
    });
  }

  async planProject(projectDescription, methodology = 'agile') {
    return await this.delegateTask('project_planning', projectDescription, {
      methodology,
      planning_type: 'comprehensive'
    });
  }

  async reviewCode(filePath, reviewType = 'general') {
    return await this.delegateTask('code_review', `Review ${filePath}`, {
      file_path: filePath,
      review_type: reviewType
    });
  }

  async generateTests(filePath, testType = 'unit') {
    return await this.delegateTask('test_generation', `Generate tests for ${filePath}`, {
      file_path: filePath,
      test_type: testType
    });
  }

  async optimizeCode(filePath, optimizationType = 'performance') {
    return await this.delegateTask('code_optimization', `Optimize ${filePath}`, {
      file_path: filePath,
      optimization_type: optimizationType
    });
  }

  // Batch task delegation
  async delegateMultipleTasks(tasks) {
    const results = [];
    
    for (const task of tasks) {
      const result = await this.delegateTask(
        task.type,
        task.description,
        task.context || {}
      );
      
      results.push({
        ...result,
        task_id: task.id || `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        original_task: task
      });
      
      // Add small delay between tasks to avoid overwhelming services
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    return results;
  }

  // Get task delegation statistics
  async getTaskStats() {
    try {
      const response = await fetch(`${this.apiBase}/project/stats`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to get task stats:', error);
    }
    
    return {
      total_tasks: 0,
      successful_tasks: 0,
      failed_tasks: 0,
      services_used: {},
      average_response_time: 0
    };
  }

  // Get recommendations for task optimization
  async getTaskRecommendations(taskHistory) {
    try {
      const response = await fetch(`${this.apiBase}/project/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task_history: taskHistory })
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to get task recommendations:', error);
    }
    
    return {
      recommendations: [],
      optimization_suggestions: [],
      service_suggestions: []
    };
  }

  // Event handlers for real-time updates
  onServiceStatusChange(callback) {
    this.statusChangeCallback = callback;
  }

  onTaskComplete(callback) {
    this.taskCompleteCallback = callback;
  }

  // Utility methods
  getAvailableServices() {
    return Object.entries(this.services)
      .filter(([name, service]) => service.available)
      .map(([name, service]) => ({ name, ...service }));
  }

  getServiceCapabilities(serviceName) {
    return this.services[serviceName]?.capabilities || [];
  }

  isServiceAvailable(serviceName) {
    return this.services[serviceName]?.available || false;
  }

  getSupportedTaskTypes() {
    const allCapabilities = Object.values(this.services)
      .filter(service => service.available)
      .flatMap(service => service.capabilities);
    
    return [...new Set(allCapabilities)];
  }
}

// Export singleton instance
const taskDelegationService = new TaskDelegationService();
export default taskDelegationService;

// Also export the class for testing
export { TaskDelegationService };