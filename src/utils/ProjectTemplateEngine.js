/**
 * Project Template Engine - Advanced project structure generation
 * 
 * Provides pre-built project templates with intelligent task generation,
 * dependency mapping, resource allocation, and workflow automation.
 */

import { v4 as uuidv4 } from 'uuid';

export class ProjectTemplateEngine {
  constructor() {
    this.templates = this.initializeTemplates();
    this.dependencies = new Map();
    this.resourceProfiles = this.initializeResourceProfiles();
  }

  initializeTemplates() {
    return {
      'full-stack-web-app': {
        name: 'Full-Stack Web Application',
        description: 'Complete web application with frontend, backend, and database',
        category: 'development',
        estimatedDuration: '8-12 weeks',
        complexity: 'high',
        requiredSkills: ['frontend', 'backend', 'database', 'devops'],
        methodology: 'agile',
        phases: [
          {
            name: 'Planning & Architecture',
            duration: '1-2 weeks',
            tasks: [
              'requirements-gathering',
              'system-architecture-design',
              'technology-stack-selection',
              'database-schema-design',
              'api-endpoint-planning'
            ]
          },
          {
            name: 'Backend Development',
            duration: '3-4 weeks',
            tasks: [
              'database-setup',
              'authentication-system',
              'api-endpoints-crud',
              'business-logic-implementation',
              'error-handling-middleware',
              'api-documentation'
            ]
          },
          {
            name: 'Frontend Development',
            duration: '3-4 weeks',
            tasks: [
              'ui-component-library',
              'routing-setup',
              'state-management',
              'api-integration',
              'responsive-design',
              'user-authentication-ui'
            ]
          },
          {
            name: 'Integration & Testing',
            duration: '1-2 weeks',
            tasks: [
              'unit-testing',
              'integration-testing',
              'e2e-testing',
              'performance-optimization',
              'security-audit',
              'deployment-setup'
            ]
          }
        ]
      },

      'ai-integration-project': {
        name: 'AI Integration Project',
        description: 'Integration of AI services into existing applications',
        category: 'ai',
        estimatedDuration: '4-6 weeks',
        complexity: 'medium',
        requiredSkills: ['ai', 'api-integration', 'data-processing'],
        methodology: 'lean',
        phases: [
          {
            name: 'AI Strategy & Planning',
            duration: '1 week',
            tasks: [
              'ai-requirements-analysis',
              'service-provider-evaluation',
              'integration-architecture',
              'data-pipeline-design'
            ]
          },
          {
            name: 'AI Service Integration',
            duration: '2-3 weeks',
            tasks: [
              'api-client-implementation',
              'data-preprocessing',
              'response-processing',
              'error-handling-ai-calls',
              'rate-limiting-implementation'
            ]
          },
          {
            name: 'Testing & Optimization',
            duration: '1-2 weeks',
            tasks: [
              'ai-response-validation',
              'performance-benchmarking',
              'accuracy-testing',
              'cost-optimization',
              'monitoring-implementation'
            ]
          }
        ]
      },

      'data-analytics-dashboard': {
        name: 'Data Analytics Dashboard',
        description: 'Interactive dashboard for data visualization and analysis',
        category: 'analytics',
        estimatedDuration: '6-8 weeks',
        complexity: 'medium',
        requiredSkills: ['data-analysis', 'visualization', 'backend', 'frontend'],
        methodology: 'kanban',
        phases: [
          {
            name: 'Data Architecture',
            duration: '1-2 weeks',
            tasks: [
              'data-source-analysis',
              'etl-pipeline-design',
              'data-warehouse-setup',
              'api-design-analytics'
            ]
          },
          {
            name: 'Dashboard Development',
            duration: '3-4 weeks',
            tasks: [
              'chart-library-selection',
              'interactive-visualizations',
              'real-time-data-updates',
              'filter-and-drill-down',
              'export-functionality'
            ]
          },
          {
            name: 'Advanced Features',
            duration: '2 weeks',
            tasks: [
              'predictive-analytics',
              'automated-reporting',
              'alert-system',
              'user-permissions',
              'performance-optimization'
            ]
          }
        ]
      },

      'microservices-architecture': {
        name: 'Microservices Architecture',
        description: 'Containerized microservices with orchestration',
        category: 'architecture',
        estimatedDuration: '10-16 weeks',
        complexity: 'very-high',
        requiredSkills: ['microservices', 'containers', 'orchestration', 'devops'],
        methodology: 'scrumban',
        phases: [
          {
            name: 'Architecture Design',
            duration: '2-3 weeks',
            tasks: [
              'service-decomposition',
              'api-gateway-design',
              'service-mesh-architecture',
              'data-consistency-strategy',
              'monitoring-strategy'
            ]
          },
          {
            name: 'Core Services',
            duration: '4-6 weeks',
            tasks: [
              'user-service',
              'authentication-service',
              'notification-service',
              'file-storage-service',
              'logging-service'
            ]
          },
          {
            name: 'Infrastructure',
            duration: '2-3 weeks',
            tasks: [
              'container-orchestration',
              'service-discovery',
              'load-balancing',
              'auto-scaling',
              'health-monitoring'
            ]
          },
          {
            name: 'DevOps Pipeline',
            duration: '2-4 weeks',
            tasks: [
              'ci-cd-pipeline',
              'automated-testing',
              'deployment-automation',
              'monitoring-alerts',
              'disaster-recovery'
            ]
          }
        ]
      },

      'mobile-app-mvp': {
        name: 'Mobile App MVP',
        description: 'Cross-platform mobile app minimum viable product',
        category: 'mobile',
        estimatedDuration: '6-10 weeks',
        complexity: 'medium',
        requiredSkills: ['mobile-development', 'ui-design', 'api-integration'],
        methodology: 'lean',
        phases: [
          {
            name: 'MVP Definition',
            duration: '1 week',
            tasks: [
              'user-story-mapping',
              'feature-prioritization',
              'wireframe-creation',
              'tech-stack-selection'
            ]
          },
          {
            name: 'Core Development',
            duration: '3-4 weeks',
            tasks: [
              'navigation-setup',
              'core-screens',
              'api-integration',
              'local-data-storage',
              'push-notifications'
            ]
          },
          {
            name: 'Polish & Launch',
            duration: '2-5 weeks',
            tasks: [
              'ui-refinement',
              'performance-optimization',
              'testing-qa',
              'app-store-preparation',
              'analytics-integration'
            ]
          }
        ]
      }
    };
  }

  initializeResourceProfiles() {
    return {
      'alden': {
        specializations: ['project-management', 'planning', 'coordination'],
        capacity: 10,
        availability: 0.9,
        skills: ['requirements-gathering', 'system-architecture-design', 'project-coordination']
      },
      'alice': {
        specializations: ['user-research', 'ui-design', 'testing'],
        capacity: 8,
        availability: 0.85,
        skills: ['user-story-mapping', 'wireframe-creation', 'ui-refinement', 'testing-qa']
      },
      'mimic': {
        specializations: ['development', 'coding', 'technical-implementation'],
        capacity: 12,
        availability: 0.95,
        skills: ['frontend', 'backend', 'api-integration', 'database-setup', 'performance-optimization']
      },
      'sentry': {
        specializations: ['security', 'monitoring', 'devops'],
        capacity: 6,
        availability: 0.8,
        skills: ['security-audit', 'monitoring-implementation', 'deployment-setup', 'ci-cd-pipeline']
      }
    };
  }

  /**
   * Generate a complete project from a template
   */
  generateProject(templateId, customizations = {}) {
    const template = this.templates[templateId];
    if (!template) {
      throw new Error(`Template ${templateId} not found`);
    }

    const projectId = uuidv4();
    const project = {
      id: projectId,
      name: customizations.name || template.name,
      description: customizations.description || template.description,
      template: templateId,
      category: template.category,
      complexity: template.complexity,
      methodology: customizations.methodology || template.methodology,
      estimatedDuration: template.estimatedDuration,
      requiredSkills: template.requiredSkills,
      created: new Date().toISOString(),
      status: 'planning',
      progress: 0,
      phases: [],
      tasks: [],
      resources: {},
      dependencies: [],
      metrics: {
        totalTasks: 0,
        completedTasks: 0,
        blockedTasks: 0,
        estimatedEffort: 0,
        actualEffort: 0
      }
    };

    // Generate phases and tasks
    this.generatePhasesAndTasks(project, template, customizations);

    // Calculate dependencies
    this.calculateTaskDependencies(project);

    // Allocate resources
    this.allocateResources(project);

    // Estimate effort
    this.calculateEffortEstimates(project);

    return project;
  }

  generatePhasesAndTasks(project, template, customizations) {
    template.phases.forEach((phaseTemplate, phaseIndex) => {
      const phase = {
        id: uuidv4(),
        name: phaseTemplate.name,
        description: `${phaseTemplate.name} phase of ${project.name}`,
        duration: phaseTemplate.duration,
        startDate: this.calculatePhaseStartDate(phaseIndex, template.phases),
        status: phaseIndex === 0 ? 'ready' : 'waiting',
        progress: 0,
        tasks: []
      };

      phaseTemplate.tasks.forEach((taskTemplate, taskIndex) => {
        const task = this.generateTask(taskTemplate, phase, project, taskIndex);
        phase.tasks.push(task.id);
        project.tasks.push(task);
      });

      project.phases.push(phase);
    });

    project.metrics.totalTasks = project.tasks.length;
  }

  generateTask(taskTemplate, phase, project, taskIndex) {
    const taskDefinitions = this.getTaskDefinitions();
    const taskDef = taskDefinitions[taskTemplate] || { 
      name: taskTemplate.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      description: `Complete ${taskTemplate} for ${project.name}`,
      type: 'development',
      estimatedHours: 8,
      skills: ['general']
    };

    const task = {
      id: uuidv4(),
      name: taskDef.name,
      description: taskDef.description,
      type: taskDef.type,
      phase: phase.id,
      priority: this.calculateTaskPriority(taskIndex, phase),
      status: 'not_started',
      progress: 0,
      estimatedHours: taskDef.estimatedHours,
      actualHours: 0,
      skills: taskDef.skills,
      assignedAgent: null,
      dependencies: [],
      blockers: [],
      created: new Date().toISOString(),
      startDate: null,
      endDate: null,
      notes: []
    };

    return task;
  }

  getTaskDefinitions() {
    return {
      'requirements-gathering': {
        name: 'Requirements Gathering',
        description: 'Collect and document project requirements from stakeholders',
        type: 'analysis',
        estimatedHours: 16,
        skills: ['analysis', 'communication', 'documentation']
      },
      'system-architecture-design': {
        name: 'System Architecture Design',
        description: 'Design overall system architecture and component interactions',
        type: 'design',
        estimatedHours: 24,
        skills: ['architecture', 'system-design', 'documentation']
      },
      'technology-stack-selection': {
        name: 'Technology Stack Selection',
        description: 'Research and select appropriate technologies for the project',
        type: 'research',
        estimatedHours: 8,
        skills: ['research', 'technology-evaluation']
      },
      'database-schema-design': {
        name: 'Database Schema Design',
        description: 'Design database structure and relationships',
        type: 'design',
        estimatedHours: 16,
        skills: ['database-design', 'data-modeling']
      },
      'api-endpoint-planning': {
        name: 'API Endpoint Planning',
        description: 'Plan and document API endpoints and contracts',
        type: 'design',
        estimatedHours: 12,
        skills: ['api-design', 'documentation']
      },
      'database-setup': {
        name: 'Database Setup',
        description: 'Set up database infrastructure and initial schema',
        type: 'development',
        estimatedHours: 12,
        skills: ['database', 'devops']
      },
      'authentication-system': {
        name: 'Authentication System',
        description: 'Implement user authentication and authorization',
        type: 'development',
        estimatedHours: 20,
        skills: ['backend', 'security']
      },
      'api-endpoints-crud': {
        name: 'API Endpoints (CRUD)',
        description: 'Implement Create, Read, Update, Delete API endpoints',
        type: 'development',
        estimatedHours: 24,
        skills: ['backend', 'api-development']
      },
      'business-logic-implementation': {
        name: 'Business Logic Implementation',
        description: 'Implement core business logic and rules',
        type: 'development',
        estimatedHours: 32,
        skills: ['backend', 'business-logic']
      },
      'ui-component-library': {
        name: 'UI Component Library',
        description: 'Create reusable UI components and design system',
        type: 'development',
        estimatedHours: 20,
        skills: ['frontend', 'ui-design']
      },
      'responsive-design': {
        name: 'Responsive Design Implementation',
        description: 'Ensure application works across all device sizes',
        type: 'development',
        estimatedHours: 16,
        skills: ['frontend', 'css', 'responsive-design']
      },
      'unit-testing': {
        name: 'Unit Testing',
        description: 'Write comprehensive unit tests for all components',
        type: 'testing',
        estimatedHours: 24,
        skills: ['testing', 'development']
      },
      'integration-testing': {
        name: 'Integration Testing',
        description: 'Test integration between different system components',
        type: 'testing',
        estimatedHours: 16,
        skills: ['testing', 'integration']
      },
      'performance-optimization': {
        name: 'Performance Optimization',
        description: 'Optimize application performance and resource usage',
        type: 'optimization',
        estimatedHours: 20,
        skills: ['optimization', 'performance-analysis']
      },
      'security-audit': {
        name: 'Security Audit',
        description: 'Conduct comprehensive security review and testing',
        type: 'security',
        estimatedHours: 16,
        skills: ['security', 'audit']
      },
      'deployment-setup': {
        name: 'Deployment Setup',
        description: 'Set up production deployment infrastructure',
        type: 'devops',
        estimatedHours: 20,
        skills: ['devops', 'deployment']
      }
    };
  }

  calculateTaskDependencies(project) {
    // Define common dependency patterns
    const dependencyRules = {
      'database-setup': ['database-schema-design'],
      'api-endpoints-crud': ['database-setup', 'api-endpoint-planning'],
      'authentication-system': ['database-setup'],
      'business-logic-implementation': ['api-endpoints-crud'],
      'ui-component-library': ['system-architecture-design'],
      'api-integration': ['api-endpoints-crud', 'ui-component-library'],
      'unit-testing': ['business-logic-implementation', 'ui-component-library'],
      'integration-testing': ['unit-testing'],
      'performance-optimization': ['integration-testing'],
      'security-audit': ['integration-testing'],
      'deployment-setup': ['security-audit', 'performance-optimization']
    };

    project.tasks.forEach(task => {
      const taskKey = task.name.toLowerCase().replace(/\s+/g, '-').replace(/[()]/g, '');
      const dependencies = dependencyRules[taskKey] || [];
      
      dependencies.forEach(depKey => {
        const dependentTask = project.tasks.find(t => 
          t.name.toLowerCase().replace(/\s+/g, '-').replace(/[()]/g, '') === depKey
        );
        if (dependentTask) {
          task.dependencies.push(dependentTask.id);
        }
      });
    });
  }

  allocateResources(project) {
    const taskSkillMap = {
      'analysis': ['alden'],
      'design': ['alden', 'alice'],
      'research': ['alden', 'mimic'],
      'development': ['mimic'],
      'testing': ['alice', 'mimic'],
      'security': ['sentry'],
      'devops': ['sentry', 'mimic'],
      'optimization': ['mimic', 'sentry']
    };

    project.tasks.forEach(task => {
      const suitableAgents = taskSkillMap[task.type] || ['mimic'];
      const bestAgent = this.selectBestAgent(suitableAgents, task);
      task.assignedAgent = bestAgent;
      
      // Update resource allocation
      if (!project.resources[bestAgent]) {
        project.resources[bestAgent] = {
          tasks: [],
          estimatedHours: 0,
          utilization: 0
        };
      }
      
      project.resources[bestAgent].tasks.push(task.id);
      project.resources[bestAgent].estimatedHours += task.estimatedHours;
    });

    // Calculate utilization
    Object.keys(project.resources).forEach(agent => {
      const profile = this.resourceProfiles[agent];
      if (profile) {
        const maxCapacity = profile.capacity * profile.availability;
        project.resources[agent].utilization = 
          Math.min(project.resources[agent].estimatedHours / maxCapacity, 1.0);
      }
    });
  }

  selectBestAgent(suitableAgents, task) {
    // Simple selection based on current workload and skills
    let bestAgent = suitableAgents[0];
    let bestScore = 0;

    suitableAgents.forEach(agent => {
      const profile = this.resourceProfiles[agent];
      if (!profile) return;

      let score = profile.availability;
      
      // Skill match bonus
      const skillMatches = task.skills.filter(skill => profile.skills.includes(skill)).length;
      score += skillMatches * 0.2;
      
      // Specialization bonus
      const specializationMatch = profile.specializations.some(spec => 
        task.type.includes(spec) || task.name.toLowerCase().includes(spec)
      );
      if (specializationMatch) score += 0.3;

      if (score > bestScore) {
        bestScore = score;
        bestAgent = agent;
      }
    });

    return bestAgent;
  }

  calculateEffortEstimates(project) {
    project.metrics.estimatedEffort = project.tasks.reduce((total, task) => {
      return total + task.estimatedHours;
    }, 0);

    // Add buffer for complexity
    const complexityMultipliers = {
      'low': 1.1,
      'medium': 1.25,
      'high': 1.5,
      'very-high': 2.0
    };

    const multiplier = complexityMultipliers[project.complexity] || 1.25;
    project.metrics.estimatedEffort *= multiplier;
  }

  calculateTaskPriority(taskIndex, phase) {
    // Earlier tasks in a phase get higher priority
    if (taskIndex < 2) return 'high';
    if (taskIndex < 4) return 'medium';
    return 'low';
  }

  calculatePhaseStartDate(phaseIndex, phases) {
    if (phaseIndex === 0) {
      return new Date().toISOString();
    }
    // Simple calculation - in real implementation would consider dependencies
    const weeksDelay = phases.slice(0, phaseIndex).reduce((total, phase) => {
      const duration = phase.duration.split('-')[0]; // Get minimum weeks
      return total + parseInt(duration);
    }, 0);
    
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + (weeksDelay * 7));
    return startDate.toISOString();
  }

  /**
   * Get available templates with filtering
   */
  getAvailableTemplates(filters = {}) {
    let templates = Object.entries(this.templates).map(([id, template]) => ({
      id,
      ...template
    }));

    if (filters.category) {
      templates = templates.filter(t => t.category === filters.category);
    }

    if (filters.complexity) {
      templates = templates.filter(t => t.complexity === filters.complexity);
    }

    if (filters.skills) {
      templates = templates.filter(t => 
        filters.skills.some(skill => t.requiredSkills.includes(skill))
      );
    }

    return templates;
  }

  /**
   * Generate project recommendations based on requirements
   */
  recommendTemplates(requirements) {
    const templates = this.getAvailableTemplates();
    const recommendations = [];

    templates.forEach(template => {
      let score = 0;
      
      // Category match
      if (requirements.category && template.category === requirements.category) {
        score += 30;
      }
      
      // Skill overlap
      if (requirements.skills) {
        const skillOverlap = requirements.skills.filter(skill => 
          template.requiredSkills.includes(skill)
        ).length;
        score += (skillOverlap / requirements.skills.length) * 40;
      }
      
      // Complexity match
      if (requirements.complexity && template.complexity === requirements.complexity) {
        score += 20;
      }
      
      // Duration preference
      if (requirements.duration) {
        const templateWeeks = this.parseDuration(template.estimatedDuration);
        const requiredWeeks = this.parseDuration(requirements.duration);
        const durationMatch = 1 - Math.abs(templateWeeks - requiredWeeks) / Math.max(templateWeeks, requiredWeeks);
        score += durationMatch * 10;
      }

      if (score > 0) {
        recommendations.push({
          template,
          score: Math.round(score),
          reason: this.generateRecommendationReason(template, requirements, score)
        });
      }
    });

    return recommendations.sort((a, b) => b.score - a.score).slice(0, 5);
  }

  parseDuration(durationString) {
    const match = durationString.match(/(\d+)/);
    return match ? parseInt(match[1]) : 8;
  }

  generateRecommendationReason(template, requirements, score) {
    const reasons = [];
    
    if (requirements.category && template.category === requirements.category) {
      reasons.push(`Matches ${requirements.category} category`);
    }
    
    if (requirements.skills) {
      const skillOverlap = requirements.skills.filter(skill => 
        template.requiredSkills.includes(skill)
      ).length;
      if (skillOverlap > 0) {
        reasons.push(`${skillOverlap} matching skills`);
      }
    }
    
    if (template.complexity === 'low' && score > 50) {
      reasons.push('Good for beginners');
    }
    
    if (template.complexity === 'high' && score > 60) {
      reasons.push('Advanced project structure');
    }

    return reasons.length > 0 ? reasons.join(', ') : 'Good general match';
  }
}

export default new ProjectTemplateEngine();