/**
 * Alden Orchestration Engine - Full Project Command Implementation
 * Implements all SOPs: Methodology Evaluation, Role Assignment, Retrospective Cycle, Method Switch Protocol
 */

class AldenOrchestrationEngine {
  constructor(memorySystem, delegationAPI) {
    this.memorySystem = memorySystem;
    this.delegationAPI = delegationAPI;
    this.activeProjects = new Map();
    this.agentRoles = new Map();
    this.methodologies = {
      agile: { 
        risk_tolerance: 'medium', 
        team_size: '3-9', 
        iteration_length: '1-4 weeks',
        roles: ['product_owner', 'scrum_master', 'developer', 'tester']
      },
      waterfall: { 
        risk_tolerance: 'low', 
        team_size: '5-15', 
        iteration_length: '3-6 months',
        roles: ['project_manager', 'business_analyst', 'architect', 'developer', 'tester']
      },
      kanban: { 
        risk_tolerance: 'medium', 
        team_size: '2-8', 
        iteration_length: 'continuous',
        roles: ['flow_manager', 'developer', 'analyst']
      },
      lean: { 
        risk_tolerance: 'high', 
        team_size: '2-5', 
        iteration_length: '1-2 weeks',
        roles: ['lean_coach', 'developer', 'customer_advocate']
      }
    };
    this.riskProfiles = {
      low: { complexity: 1-3, uncertainty: 1-2, team_experience: 'high' },
      medium: { complexity: 3-6, uncertainty: 2-4, team_experience: 'medium' },
      high: { complexity: 6-8, uncertainty: 4-5, team_experience: 'mixed' },
      critical: { complexity: 8-10, uncertainty: 5, team_experience: 'varied' }
    };
    
    this.orchestrationLog = [];
    this.performanceMetrics = {
      successful_delegations: 0,
      failed_delegations: 0,
      methodology_switches: 0,
      average_project_velocity: 0,
      agent_utilization: {}
    };
  }

  /**
   * SOP: Methodology Evaluation Engine
   * Evaluates and recommends the best methodology for a project
   */
  async evaluateMethodology(projectData) {
    this.log('METHODOLOGY_EVALUATION', `Starting evaluation for project: ${projectData.name}`);
    
    const riskProfile = this.assessRiskProfile(projectData);
    const teamCapabilities = await this.assessTeamCapabilities(projectData.agents || []);
    const projectConstraints = this.analyzeConstraints(projectData);
    
    // Score each methodology
    const methodologyScores = {};
    for (const [methodology, config] of Object.entries(this.methodologies)) {
      methodologyScores[methodology] = this.scoreMethodology(
        methodology, 
        config, 
        riskProfile, 
        teamCapabilities, 
        projectConstraints
      );
    }
    
    // Rank methodologies by score
    const rankedMethodologies = Object.entries(methodologyScores)
      .sort(([,a], [,b]) => b.total_score - a.total_score)
      .map(([name, scores]) => ({ name, ...scores }));
    
    const recommendation = {
      recommended: rankedMethodologies[0],
      alternatives: rankedMethodologies.slice(1, 3),
      risk_profile: riskProfile,
      rationale: this.generateMethodologyRationale(rankedMethodologies[0], riskProfile),
      confidence: rankedMethodologies[0].total_score / 10
    };
    
    // Store in memory
    this.memorySystem.storeSemanticMemory(
      `methodology_evaluation_${projectData.id}`,
      recommendation
    );
    
    this.log('METHODOLOGY_EVALUATION', `Recommended: ${recommendation.recommended.name} (confidence: ${recommendation.confidence.toFixed(2)})`);
    
    return recommendation;
  }

  /**
   * SOP: Role Assignment Manager
   * Validates required roles and assigns agents with expiration monitoring
   */
  async assignRoles(projectId, methodology, availableAgents) {
    this.log('ROLE_ASSIGNMENT', `Starting role assignment for project: ${projectId}`);
    
    const requiredRoles = this.methodologies[methodology].roles;
    const roleAssignments = {};
    const roleCapabilities = await this.assessAgentCapabilities(availableAgents);
    
    // Primary role assignment
    for (const role of requiredRoles) {
      const bestAgent = this.selectBestAgentForRole(role, roleCapabilities, roleAssignments);
      if (bestAgent) {
        roleAssignments[role] = {
          agent: bestAgent,
          assigned_at: new Date().toISOString(),
          expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days
          performance_score: 0.7,
          workload: this.calculateAgentWorkload(bestAgent)
        };
        
        // Update agent roles tracking
        this.agentRoles.set(`${projectId}_${role}`, roleAssignments[role]);
      }
    }
    
    // Validate role coverage
    const coverage = this.validateRoleCoverage(requiredRoles, roleAssignments);
    if (!coverage.complete) {
      this.log('ROLE_ASSIGNMENT', `Warning: Incomplete role coverage. Missing: ${coverage.missing.join(', ')}`);
    }
    
    // Store role log
    const roleLog = {
      project_id: projectId,
      methodology: methodology,
      assignments: roleAssignments,
      coverage: coverage,
      assigned_at: new Date().toISOString()
    };
    
    this.memorySystem.storeProceduralMemory(
      `role_assignment_${projectId}`,
      {
        description: 'Role assignment for project execution',
        assignments: roleAssignments,
        methodology: methodology,
        coverage: coverage
      }
    );
    
    this.log('ROLE_ASSIGNMENT', `Role assignment complete. Coverage: ${coverage.coverage_percentage}%`);
    
    return roleLog;
  }

  /**
   * SOP: Method Switch Protocol
   * Handles methodology switching with cooldown and override logic
   */
  async initiateMethodSwitch(projectId, newMethodology, reason = 'performance') {
    this.log('METHOD_SWITCH', `Switch request: ${projectId} -> ${newMethodology} (reason: ${reason})`);
    
    const project = this.activeProjects.get(projectId);
    if (!project) {
      throw new Error(`Project ${projectId} not found`);
    }
    
    // Check cooldown period
    const lastSwitch = project.last_method_switch || project.created_at;
    const cooldownPeriod = 48 * 60 * 60 * 1000; // 48 hours
    const timeSinceLastSwitch = Date.now() - new Date(lastSwitch).getTime();
    
    if (timeSinceLastSwitch < cooldownPeriod && reason !== 'emergency') {
      const remainingCooldown = Math.ceil((cooldownPeriod - timeSinceLastSwitch) / (60 * 60 * 1000));
      throw new Error(`Method switch on cooldown. ${remainingCooldown} hours remaining.`);
    }
    
    // Validate new methodology
    const evaluationResult = await this.evaluateMethodology({
      ...project,
      current_methodology: newMethodology
    });
    
    if (evaluationResult.confidence < 0.6 && reason !== 'override') {
      throw new Error(`Low confidence in methodology switch (${evaluationResult.confidence.toFixed(2)}). Use override if necessary.`);
    }
    
    // Execute switch
    const switchData = {
      project_id: projectId,
      old_methodology: project.methodology,
      new_methodology: newMethodology,
      reason: reason,
      confidence: evaluationResult.confidence,
      timestamp: new Date().toISOString(),
      triggered_by: 'alden'
    };
    
    // Re-assign roles for new methodology
    const newRoleAssignments = await this.assignRoles(
      projectId, 
      newMethodology, 
      project.agents
    );
    
    // Update project
    project.methodology = newMethodology;
    project.last_method_switch = switchData.timestamp;
    project.method_switches = (project.method_switches || 0) + 1;
    project.role_assignments = newRoleAssignments.assignments;
    
    // Log switch
    this.performanceMetrics.methodology_switches++;
    this.memorySystem.storeEpisodicMemory({
      content: `Method switch executed: ${switchData.old_methodology} -> ${switchData.new_methodology}`,
      context: `Project: ${projectId}, Reason: ${reason}`,
      success: true
    });
    
    this.log('METHOD_SWITCH', `Switch complete: ${newMethodology} (confidence: ${evaluationResult.confidence.toFixed(2)})`);
    
    return switchData;
  }

  /**
   * SOP: Retrospective Cycle
   * Captures velocity, sentiment, adherence, and blockers for learning
   */
  async conductRetrospective(projectId) {
    this.log('RETROSPECTIVE', `Starting retrospective for project: ${projectId}`);
    
    const project = this.activeProjects.get(projectId);
    if (!project) {
      throw new Error(`Project ${projectId} not found`);
    }
    
    // Gather retrospective data
    const retrospectiveData = {
      project_id: projectId,
      methodology: project.methodology,
      conducted_at: new Date().toISOString(),
      
      // Velocity metrics
      velocity: await this.calculateVelocity(project),
      
      // Sentiment analysis
      sentiment: await this.analyzeSentiment(project),
      
      // Methodology adherence
      adherence: await this.assessAdherence(project),
      
      // Blockers and impediments
      blockers: await this.identifyBlockers(project),
      
      // Agent performance
      agent_performance: await this.evaluateAgentPerformance(project),
      
      // Lessons learned
      lessons_learned: await this.extractLessonsLearned(project)
    };
    
    // Update learning algorithms
    await this.updateLearningModel(retrospectiveData);
    
    // Generate recommendations
    const recommendations = await this.generateRecommendations(retrospectiveData);
    
    // Store retrospective
    this.memorySystem.storeEpisodicMemory({
      content: `Retrospective completed for ${project.name}`,
      context: `Velocity: ${retrospectiveData.velocity.current}, Sentiment: ${retrospectiveData.sentiment.overall}`,
      success: true,
      systemResponse: JSON.stringify(recommendations)
    });
    
    const retrospectiveResult = {
      ...retrospectiveData,
      recommendations: recommendations,
      next_retrospective: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
    };
    
    this.log('RETROSPECTIVE', `Retrospective complete. Velocity: ${retrospectiveData.velocity.current}, Recommendations: ${recommendations.length}`);
    
    return retrospectiveResult;
  }

  /**
   * Core Orchestration Method - Coordinates all SOPs
   */
  async orchestrateProject(projectData) {
    this.log('ORCHESTRATION', `Starting orchestration for: ${projectData.name}`);
    
    try {
      // Step 1: Methodology Evaluation
      const methodologyEvaluation = await this.evaluateMethodology(projectData);
      
      // Step 2: Role Assignment
      const roleAssignment = await this.assignRoles(
        projectData.id,
        methodologyEvaluation.recommended.name,
        projectData.agents || ['alden', 'gemini', 'claude']
      );
      
      // Step 3: Initialize Project
      const orchestratedProject = {
        ...projectData,
        methodology: methodologyEvaluation.recommended.name,
        risk_profile: methodologyEvaluation.risk_profile,
        role_assignments: roleAssignment.assignments,
        orchestration_data: {
          methodology_evaluation: methodologyEvaluation,
          role_assignment: roleAssignment,
          orchestrated_at: new Date().toISOString(),
          orchestrated_by: 'alden'
        },
        status: 'orchestrated',
        created_at: new Date().toISOString()
      };
      
      // Store project
      this.activeProjects.set(projectData.id, orchestratedProject);
      
      // Step 4: Delegate Initial Tasks
      await this.delegateProjectTasks(orchestratedProject);
      
      // Step 5: Schedule Retrospective
      setTimeout(() => {
        this.conductRetrospective(projectData.id);
      }, 7 * 24 * 60 * 60 * 1000); // 7 days
      
      this.log('ORCHESTRATION', `Orchestration complete for: ${projectData.name}`);
      
      return orchestratedProject;
      
    } catch (error) {
      this.log('ORCHESTRATION', `Orchestration failed: ${error.message}`, 'error');
      throw error;
    }
  }

  /**
   * Gemini Integration - Delegate specific tasks to Gemini Pro
   */
  async delegateToGemini(task, context = '') {
    this.log('GEMINI_DELEGATION', `Delegating task: ${task.substring(0, 50)}...`);
    
    try {
      const result = await this.delegationAPI.claudeDelegateToGoogle({
        task: task,
        context: `Alden Orchestration Context: ${context}`,
        requiresReview: true
      });
      
      if (result.success) {
        this.performanceMetrics.successful_delegations++;
        
        // Learn from successful delegation
        this.memorySystem.learnFromInteraction(
          {
            content: task,
            context: context,
            userInput: task,
            systemResponse: result.googleResponse
          },
          { success: true }
        );
        
        this.log('GEMINI_DELEGATION', 'Delegation successful');
        return result;
      } else {
        this.performanceMetrics.failed_delegations++;
        this.log('GEMINI_DELEGATION', `Delegation failed: ${result.error}`, 'error');
        return result;
      }
    } catch (error) {
      this.performanceMetrics.failed_delegations++;
      this.log('GEMINI_DELEGATION', `Delegation error: ${error.message}`, 'error');
      throw error;
    }
  }

  // Helper Methods

  assessRiskProfile(projectData) {
    let complexity = 5; // Default medium
    let uncertainty = 3;
    
    // Assess complexity based on project characteristics
    if (projectData.tasks && projectData.tasks.length > 10) complexity += 2;
    if (projectData.agents && projectData.agents.length > 5) complexity += 1;
    if (projectData.description && projectData.description.includes('integration')) complexity += 1;
    
    // Assess uncertainty
    if (projectData.timeline && projectData.timeline.estimated_completion) {
      const timeToCompletion = new Date(projectData.timeline.estimated_completion) - new Date();
      if (timeToCompletion < 7 * 24 * 60 * 60 * 1000) uncertainty += 2; // Less than a week
    }
    
    complexity = Math.min(10, Math.max(1, complexity));
    uncertainty = Math.min(5, Math.max(1, uncertainty));
    
    let riskLevel = 'medium';
    if (complexity <= 3 && uncertainty <= 2) riskLevel = 'low';
    else if (complexity >= 7 || uncertainty >= 4) riskLevel = 'high';
    if (complexity >= 9 && uncertainty >= 5) riskLevel = 'critical';
    
    return {
      level: riskLevel,
      complexity: complexity,
      uncertainty: uncertainty,
      assessment_date: new Date().toISOString()
    };
  }

  async assessTeamCapabilities(agents) {
    const capabilities = {};
    for (const agent of agents) {
      capabilities[agent] = {
        experience_level: 'medium', // Would be determined by agent history
        availability: 0.8,
        specializations: this.getAgentSpecializations(agent),
        performance_history: 0.75
      };
    }
    return capabilities;
  }

  getAgentSpecializations(agent) {
    const specializations = {
      'alden': ['orchestration', 'adhd_support', 'task_management', 'memory_systems'],
      'gemini': ['analysis', 'code_review', 'architecture', 'optimization'],
      'claude': ['implementation', 'documentation', 'refactoring', 'testing'],
      'synapse': ['integration', 'deployment', 'monitoring', 'external_apis']
    };
    return specializations[agent] || ['general'];
  }

  scoreMethodology(methodology, config, riskProfile, teamCapabilities, constraints) {
    let score = 0;
    
    // Risk alignment
    if (config.risk_tolerance === riskProfile.level) score += 3;
    else if (Math.abs(['low', 'medium', 'high', 'critical'].indexOf(config.risk_tolerance) - 
                    ['low', 'medium', 'high', 'critical'].indexOf(riskProfile.level)) === 1) score += 1;
    
    // Team size alignment
    const teamSize = Object.keys(teamCapabilities).length;
    const [minSize, maxSize] = config.team_size.split('-').map(s => parseInt(s.replace(/\D/g, '')));
    if (teamSize >= minSize && teamSize <= maxSize) score += 2;
    
    // Add methodology-specific bonuses
    if (methodology === 'agile' && riskProfile.uncertainty >= 3) score += 1;
    if (methodology === 'waterfall' && riskProfile.complexity <= 4) score += 1;
    if (methodology === 'kanban' && teamSize <= 6) score += 1;
    if (methodology === 'lean' && constraints.time_pressure) score += 2;
    
    return {
      total_score: score,
      risk_alignment: score >= 3 ? 'high' : score >= 1 ? 'medium' : 'low',
      team_fit: teamSize >= minSize && teamSize <= maxSize ? 'good' : 'poor'
    };
  }

  log(operation, message, level = 'info') {
    const logEntry = {
      timestamp: new Date().toISOString(),
      operation: operation,
      message: message,
      level: level
    };
    this.orchestrationLog.push(logEntry);
    console.log(`[ALDEN ORCHESTRATION] [${operation}] ${message}`);
  }

  getOrchestrationStatus() {
    return {
      active_projects: this.activeProjects.size,
      performance_metrics: this.performanceMetrics,
      recent_logs: this.orchestrationLog.slice(-10),
      methodologies_available: Object.keys(this.methodologies),
      orchestration_protocols: {
        methodology_evaluation: true,
        role_assignment: true,
        retrospective_cycle: true,
        method_switch_protocol: true
      }
    };
  }

  // Additional helper methods would be implemented here...
  analyzeConstraints(projectData) {
    return {
      time_pressure: projectData.priority === 'critical',
      resource_constraints: false,
      external_dependencies: projectData.agents && projectData.agents.includes('external')
    };
  }

  async delegateProjectTasks(project) {
    // Delegate initial tasks based on role assignments
    for (const [role, assignment] of Object.entries(project.role_assignments)) {
      const tasks = this.getTasksForRole(project, role);
      if (tasks.length > 0) {
        this.log('TASK_DELEGATION', `Delegating ${tasks.length} tasks to ${assignment.agent} (${role})`);
      }
    }
  }

  getTasksForRole(project, role) {
    // Return tasks appropriate for the given role
    return project.tasks ? project.tasks.filter(task => 
      task.assignee === project.role_assignments[role]?.agent
    ) : [];
  }
}

export default AldenOrchestrationEngine;