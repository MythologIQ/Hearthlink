import React, { useState, useEffect, useCallback } from 'react';
import './TaskCreator.css';
import SteveAugustTemplate from './SteveAugustTemplate';

const TaskCreator = ({ isOpen, onClose, onTaskCreate, existingTasks = [], agents = [], userId = 'default-user' }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isAIAssisting, setIsAIAssisting] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [showSteveAugustTemplate, setShowSteveAugustTemplate] = useState(false);
  
  // Enhanced task form data with SPEC-2 fields
  const [taskData, setTaskData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    estimatedTime: 1,
    dueDate: '',
    tags: [],
    assignedAgent: 'alden',
    dependencies: [],
    subtasks: [],
    category: 'general',
    // SPEC-2 Enhanced fields
    mission: '',
    values: [],
    habitTracker: {
      frequency: 'daily',
      target: 1,
      streak: 0,
      lastCompleted: null
    },
    decisions: [],
    template: null,
    projectContext: null,
    memoryTags: [],
    vaultPath: null
  });
  
  // AI analysis state
  const [aiAnalysis, setAiAnalysis] = useState({
    complexity: 'medium',
    suggestedBreakdown: [],
    relatedTasks: [],
    timeEstimate: null,
    priorityReasoning: '',
    riskFactors: [],
    successCriteria: []
  });
  
  const [customTag, setCustomTag] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const predefinedTags = [
    'development', 'design', 'research', 'testing', 'documentation', 
    'bug-fix', 'feature', 'optimization', 'security', 'maintenance',
    'ui', 'api', 'database', 'performance', 'integration',
    // SPEC-2 Enhanced tags
    'memory-integration', 'vault-backed', 'persistent', 'llm-enhanced',
    'alden-memory', 'habit-tracking', 'decision-support', 'template-based'
  ];

  const coreValues = [
    'efficiency', 'innovation', 'quality', 'collaboration', 'learning',
    'sustainability', 'user-focus', 'reliability', 'scalability', 'security'
  ];

  const taskTemplates = [
    {
      id: 'alden-productivity',
      name: 'Alden Productivity Task',
      description: 'Vault-backed task with memory integration',
      fields: {
        mission: 'Enhance productivity through AI-assisted task management',
        values: ['efficiency', 'innovation'],
        habitTracker: { frequency: 'daily', target: 1 },
        category: 'productivity'
      }
    },
    {
      id: 'development-sprint',
      name: 'Development Sprint Task',
      description: 'Code development with performance tracking',
      fields: {
        mission: 'Deliver high-quality code solutions',
        values: ['quality', 'innovation'],
        habitTracker: { frequency: 'daily', target: 2 },
        category: 'development'
      }
    },
    {
      id: 'memory-research',
      name: 'Memory Research Task',
      description: 'Research task with Vault integration',
      fields: {
        mission: 'Advance memory integration capabilities',
        values: ['learning', 'innovation'],
        habitTracker: { frequency: 'weekly', target: 1 },
        category: 'research'
      }
    },
    {
      id: 'steve-august-focus-formula',
      name: '🧠 Steve August Focus Formula',
      description: 'Licensed ADHD coaching worksheet (Professional)',
      licensed: true,
      fields: {
        mission: 'ADHD-focused weekly productivity planning',
        values: ['focus', 'self-care', 'executive-function'],
        habitTracker: { frequency: 'weekly', target: 1 },
        category: 'adhd-coaching'
      }
    }
  ];

  const categories = [
    { id: 'development', name: 'Development', icon: '💻' },
    { id: 'design', name: 'Design', icon: '🎨' },
    { id: 'research', name: 'Research', icon: '🔍' },
    { id: 'testing', name: 'Testing', icon: '🧪' },
    { id: 'planning', name: 'Planning', icon: '📋' },
    { id: 'communication', name: 'Communication', icon: '💬' },
    { id: 'maintenance', name: 'Maintenance', icon: '🔧' },
    { id: 'general', name: 'General', icon: '📝' }
  ];

  const availableAgents = agents.length > 0 ? agents : [
    { id: 'alden', name: 'Alden', specialties: ['planning', 'coordination', 'management'] },
    { id: 'alice', name: 'Alice', specialties: ['analysis', 'testing', 'research'] },
    { id: 'mimic', name: 'Mimic', specialties: ['development', 'coding', 'implementation'] },
    { id: 'sentry', name: 'Sentry', specialties: ['security', 'monitoring', 'maintenance'] }
  ];

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setCurrentStep(1);
      setTaskData({
        title: '',
        description: '',
        priority: 'medium',
        estimatedTime: 1,
        dueDate: '',
        tags: [],
        assignedAgent: 'alden',
        dependencies: [],
        subtasks: [],
        category: 'general',
        // SPEC-2 Enhanced fields
        mission: '',
        values: [],
        habitTracker: {
          frequency: 'daily',
          target: 1,
          streak: 0,
          lastCompleted: null
        },
        decisions: [],
        template: null,
        projectContext: null,
        memoryTags: [],
        vaultPath: null
      });
      setAiSuggestions([]);
      setAiAnalysis({
        complexity: 'medium',
        suggestedBreakdown: [],
        relatedTasks: [],
        timeEstimate: null,
        priorityReasoning: '',
        riskFactors: [],
        successCriteria: []
      });
    }
  }, [isOpen]);

  // AI-powered task analysis
  const analyzeTask = useCallback(async () => {
    if (!taskData.title.trim() || !taskData.description.trim()) return;
    
    setIsAIAssisting(true);
    
    try {
      // Simulate AI analysis (in production, this would call actual AI service)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockAnalysis = generateMockAIAnalysis(taskData, existingTasks);
      setAiAnalysis(mockAnalysis);
      
      // Generate AI suggestions for improvement
      const suggestions = generateTaskSuggestions(taskData, mockAnalysis);
      setAiSuggestions(suggestions);
      
    } catch (error) {
      console.error('AI analysis failed:', error);
    } finally {
      setIsAIAssisting(false);
    }
  }, [taskData, existingTasks]);

  const generateMockAIAnalysis = (task, existing) => {
    const complexityFactors = [
      task.description.length > 100,
      task.title.includes('implement') || task.title.includes('develop'),
      task.title.includes('complex') || task.title.includes('advanced'),
      task.tags.includes('integration') || task.tags.includes('architecture')
    ];
    
    const complexity = complexityFactors.filter(Boolean).length > 2 ? 'high' : 
                     complexityFactors.filter(Boolean).length > 0 ? 'medium' : 'low';
    
    const baseTime = task.estimatedTime;
    const complexityMultiplier = { low: 1, medium: 1.3, high: 1.8 }[complexity];
    const suggestedTime = Math.ceil(baseTime * complexityMultiplier);
    
    const relatedTasks = existing.filter(existingTask => 
      existingTask.category === task.category ||
      task.tags.some(tag => existingTask.tags.includes(tag))
    ).slice(0, 3);
    
    const suggestedBreakdown = complexity === 'high' ? [
      'Research and planning phase',
      'Core implementation',
      'Testing and validation',
      'Documentation and cleanup'
    ] : complexity === 'medium' ? [
      'Planning and setup',
      'Implementation',
      'Testing'
    ] : ['Complete task'];
    
    const priorityReasoning = task.priority === 'high' ? 
      'High priority task requiring immediate attention' :
      task.priority === 'low' ?
      'Low priority task suitable for background processing' :
      'Standard priority task for regular development cycle';
    
    return {
      complexity,
      suggestedBreakdown,
      relatedTasks,
      timeEstimate: suggestedTime,
      priorityReasoning,
      riskFactors: complexity === 'high' ? [
        'Complex implementation may require additional time',
        'Dependencies on other systems',
        'Potential for scope creep'
      ] : complexity === 'medium' ? [
        'Standard development risks',
        'Testing requirements'
      ] : ['Minimal risk factors'],
      successCriteria: [
        'Task completion meets requirements',
        'Code passes all tests',
        'Documentation updated',
        'Stakeholder approval received'
      ]
    };
  };

  const generateTaskSuggestions = (task, analysis) => {
    const suggestions = [];
    
    if (task.description.length < 50) {
      suggestions.push({
        type: 'improvement',
        title: 'Add More Detail',
        description: 'Consider adding more specific details about requirements, constraints, and expected outcomes.',
        priority: 'medium'
      });
    }
    
    if (analysis.complexity === 'high' && task.estimatedTime < 4) {
      suggestions.push({
        type: 'warning',
        title: 'Time Estimate May Be Low',
        description: `Based on the complexity analysis, this task might require ${analysis.timeEstimate} hours instead of ${task.estimatedTime} hours.`,
        priority: 'high'
      });
    }
    
    if (analysis.relatedTasks.length > 0) {
      suggestions.push({
        type: 'info',
        title: 'Related Tasks Found',
        description: `Found ${analysis.relatedTasks.length} related tasks that might share dependencies or resources.`,
        priority: 'low'
      });
    }
    
    if (task.tags.length < 2) {
      suggestions.push({
        type: 'improvement',
        title: 'Add More Tags',
        description: 'Adding relevant tags helps with task organization and filtering.',
        priority: 'low'
      });
    }
    
    if (!task.dueDate && task.priority === 'high') {
      suggestions.push({
        type: 'warning',
        title: 'High Priority Without Deadline',
        description: 'High priority tasks should typically have a specific deadline.',
        priority: 'medium'
      });
    }
    
    return suggestions;
  };

  const handleInputChange = (field, value) => {
    setTaskData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTagAdd = (tag) => {
    if (!taskData.tags.includes(tag)) {
      setTaskData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
  };

  const handleTagRemove = (tag) => {
    setTaskData(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const handleCustomTagAdd = () => {
    if (customTag.trim() && !taskData.tags.includes(customTag.trim())) {
      handleTagAdd(customTag.trim());
      setCustomTag('');
    }
  };

  const handleSubtaskAdd = () => {
    const newSubtask = {
      id: `subtask_${Date.now()}`,
      title: '',
      completed: false
    };
    setTaskData(prev => ({
      ...prev,
      subtasks: [...prev.subtasks, newSubtask]
    }));
  };

  const handleSubtaskUpdate = (subtaskId, field, value) => {
    setTaskData(prev => ({
      ...prev,
      subtasks: prev.subtasks.map(subtask =>
        subtask.id === subtaskId ? { ...subtask, [field]: value } : subtask
      )
    }));
  };

  const handleSubtaskRemove = (subtaskId) => {
    setTaskData(prev => ({
      ...prev,
      subtasks: prev.subtasks.filter(subtask => subtask.id !== subtaskId)
    }));
  };

  const applySuggestion = (suggestion) => {
    if (suggestion.title === 'Time Estimate May Be Low') {
      handleInputChange('estimatedTime', aiAnalysis.timeEstimate);
    }
    // Remove applied suggestion
    setAiSuggestions(prev => prev.filter(s => s.title !== suggestion.title));
  };

  const handleCreateTask = async () => {
    const newTask = {
      id: `task_${Date.now()}`,
      ...taskData,
      createdAt: new Date().toISOString(),
      status: 'todo',
      progress: 0,
      aiAnalysis: aiAnalysis
    };
    
    try {
      // SPEC-2: Store in Vault with audit logging
      await persistTaskToVault(newTask);
      
      // SPEC-2: Log creation via Alden's CRUD interface
      await logTaskCRUD('CREATE', newTask);
      
      onTaskCreate(newTask);
      onClose();
    } catch (error) {
      console.error('Failed to create task:', error);
      // Show error to user
      alert('Failed to create task. Please try again.');
    }
  };

  // SPEC-2: Vault persistence function
  const persistTaskToVault = async (task) => {
    try {
      const response = await fetch('/api/vault/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          task: task,
          vaultPath: task.vaultPath || `tasks/${task.assignedAgent}/${task.id}`,
          encrypted: true,
          memoryTags: task.memoryTags
        })
      });
      
      if (!response.ok) {
        throw new Error(`Vault storage failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Vault persistence error:', error);
      throw error;
    }
  };

  // SPEC-2: CRUD audit logging
  const logTaskCRUD = async (operation, task) => {
    try {
      const auditEntry = {
        operation,
        entityType: 'task',
        entityId: task.id,
        timestamp: new Date().toISOString(),
        agent: task.assignedAgent,
        metadata: {
          title: task.title,
          category: task.category,
          template: task.template
        }
      };
      
      const response = await fetch('/api/task-templates/audit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify(auditEntry)
      });
      
      if (!response.ok) {
        console.warn('Audit logging failed:', response.statusText);
      }
    } catch (error) {
      console.warn('Audit logging error:', error);
    }
  };

  // SPEC-2: Apply task template
  const applyTemplate = (templateId) => {
    const template = taskTemplates.find(t => t.id === templateId);
    if (template) {
      // Handle licensed templates specially
      if (template.licensed && templateId === 'steve-august-focus-formula') {
        setShowSteveAugustTemplate(true);
        return;
      }
      
      setTaskData(prev => ({
        ...prev,
        ...template.fields,
        template: templateId,
        memoryTags: [...prev.memoryTags, `template:${templateId}`]
      }));
    }
  };

  // SPEC-2: Handle values selection
  const handleValueToggle = (value) => {
    setTaskData(prev => ({
      ...prev,
      values: prev.values.includes(value)
        ? prev.values.filter(v => v !== value)
        : [...prev.values, value]
    }));
  };

  // SPEC-2: Add decision entry
  const addDecision = () => {
    const newDecision = {
      id: `decision_${Date.now()}`,
      title: '',
      options: ['', ''],
      selected: null,
      reasoning: '',
      timestamp: new Date().toISOString()
    };
    
    setTaskData(prev => ({
      ...prev,
      decisions: [...prev.decisions, newDecision]
    }));
  };

  // SPEC-2: Update decision
  const updateDecision = (decisionId, field, value) => {
    setTaskData(prev => ({
      ...prev,
      decisions: prev.decisions.map(d => 
        d.id === decisionId ? { ...d, [field]: value } : d
      )
    }));
  };

  // SPEC-2: Remove decision
  const removeDecision = (decisionId) => {
    setTaskData(prev => ({
      ...prev,
      decisions: prev.decisions.filter(d => d.id !== decisionId)
    }));
  };

  const canProceedToNextStep = () => {
    switch (currentStep) {
      case 1:
        return taskData.title.trim() && taskData.description.trim();
      case 2:
        return taskData.category && taskData.priority;
      case 3:
        return true; // Optional step
      default:
        return true;
    }
  };

  const getSuggestionIcon = (type) => {
    switch (type) {
      case 'warning': return '⚠️';
      case 'improvement': return '💡';
      case 'info': return 'ℹ️';
      default: return '💡';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="task-creator-overlay">
      <div className="task-creator-modal">
        <div className="creator-header">
          <h2>Create New Task</h2>
          <div className="step-indicator">
            <div className={`step ${currentStep >= 1 ? 'active' : ''}`} title="Templates & Basic Info">1</div>
            <div className={`step ${currentStep >= 2 ? 'active' : ''}`} title="Categories & Values">2</div>
            <div className={`step ${currentStep >= 3 ? 'active' : ''}`} title="Tags & Advanced Options">3</div>
            <div className={`step ${currentStep >= 4 ? 'active' : ''}`} title="AI Analysis & Review">4</div>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="creator-content">
          {currentStep === 1 && (
            <div className="step-content">
              <h3>📝 Basic Information & Templates</h3>
              
              {/* SPEC-2: Template Selection */}
              <div className="form-group">
                <label>Task Template (Optional)</label>
                <div className="template-selection">
                  {taskTemplates.map(template => (
                    <button
                      key={template.id}
                      className={`template-btn ${taskData.template === template.id ? 'selected' : ''} ${template.licensed ? 'licensed' : ''}`}
                      onClick={() => applyTemplate(template.id)}
                    >
                      <div className="template-name">
                        {template.name}
                        {template.licensed && <span className="license-badge">🔐 Licensed</span>}
                      </div>
                      <div className="template-desc">{template.description}</div>
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="form-group">
                <label>Task Title *</label>
                <input
                  type="text"
                  value={taskData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="Enter a clear, specific task title..."
                  className="task-input"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Description *</label>
                <textarea
                  value={taskData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Describe what needs to be done, including requirements and expected outcomes..."
                  className="task-textarea"
                  rows={4}
                />
                <div className="character-count">
                  {taskData.description.length} characters
                  {taskData.description.length < 50 && (
                    <span className="hint"> (Consider adding more detail)</span>
                  )}
                </div>
              </div>

              {/* SPEC-2: Mission Field */}
              <div className="form-group">
                <label>Mission Statement</label>
                <textarea
                  value={taskData.mission}
                  onChange={(e) => handleInputChange('mission', e.target.value)}
                  placeholder="Define the broader mission this task serves..."
                  className="mission-textarea"
                  rows={2}
                />
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="step-content">
              <h3>🎯 Categorization, Priority & Values</h3>
              
              {/* SPEC-2: Values Selection */}
              <div className="form-group">
                <label>Core Values</label>
                <div className="values-grid">
                  {coreValues.map(value => (
                    <button
                      key={value}
                      className={`value-btn ${taskData.values.includes(value) ? 'selected' : ''}`}
                      onClick={() => handleValueToggle(value)}
                    >
                      {value}
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="form-grid">
                <div className="form-group">
                  <label>Category</label>
                  <div className="category-grid">
                    {categories.map(category => (
                      <button
                        key={category.id}
                        className={`category-btn ${taskData.category === category.id ? 'selected' : ''}`}
                        onClick={() => handleInputChange('category', category.id)}
                      >
                        <span className="category-icon">{category.icon}</span>
                        <span className="category-name">{category.name}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="form-group">
                  <label>Priority Level</label>
                  <div className="priority-options">
                    {['high', 'medium', 'low'].map(priority => (
                      <button
                        key={priority}
                        className={`priority-btn ${priority} ${taskData.priority === priority ? 'selected' : ''}`}
                        onClick={() => handleInputChange('priority', priority)}
                      >
                        <div className="priority-indicator"></div>
                        <span>{priority.toUpperCase()}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="form-group">
                  <label>Estimated Time (hours)</label>
                  <input
                    type="number"
                    min="0.5"
                    max="40"
                    step="0.5"
                    value={taskData.estimatedTime}
                    onChange={(e) => handleInputChange('estimatedTime', parseFloat(e.target.value) || 1)}
                    className="time-input"
                  />
                </div>

                <div className="form-group">
                  <label>Due Date (optional)</label>
                  <input
                    type="datetime-local"
                    value={taskData.dueDate}
                    onChange={(e) => handleInputChange('dueDate', e.target.value)}
                    className="date-input"
                  />
                </div>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="step-content">
              <h3>🏷️ Tags & Assignment</h3>
              
              <div className="form-group">
                <label>Tags</label>
                <div className="tags-section">
                  <div className="selected-tags">
                    {taskData.tags.map(tag => (
                      <div key={tag} className="tag-item">
                        {tag}
                        <button
                          className="tag-remove"
                          onClick={() => handleTagRemove(tag)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                  
                  <div className="tag-input-section">
                    <input
                      type="text"
                      value={customTag}
                      onChange={(e) => setCustomTag(e.target.value)}
                      placeholder="Add custom tag..."
                      className="tag-input"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleCustomTagAdd();
                        }
                      }}
                    />
                    <button onClick={handleCustomTagAdd} className="add-tag-btn">
                      Add
                    </button>
                  </div>
                  
                  <div className="predefined-tags">
                    {predefinedTags.filter(tag => !taskData.tags.includes(tag)).map(tag => (
                      <button
                        key={tag}
                        className="predefined-tag"
                        onClick={() => handleTagAdd(tag)}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label>Assign to Agent</label>
                <div className="agent-selection">
                  {availableAgents.map(agent => (
                    <div
                      key={agent.id}
                      className={`agent-option ${taskData.assignedAgent === agent.id ? 'selected' : ''}`}
                      onClick={() => handleInputChange('assignedAgent', agent.id)}
                    >
                      <div className="agent-name">{agent.name}</div>
                      <div className="agent-specialties">
                        {agent.specialties.map(specialty => (
                          <span key={specialty} className="specialty-tag">
                            {specialty}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="advanced-toggle">
                <button
                  className="toggle-btn"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                >
                  {showAdvanced ? '▼' : '▶'} Advanced Options
                </button>
              </div>

              {showAdvanced && (
                <div className="advanced-options">
                  {/* SPEC-2: Habit Tracker Configuration */}
                  <div className="form-group">
                    <label>Habit Tracker</label>
                    <div className="habit-config">
                      <div className="habit-row">
                        <label>Frequency:</label>
                        <select
                          value={taskData.habitTracker.frequency}
                          onChange={(e) => handleInputChange('habitTracker', {
                            ...taskData.habitTracker,
                            frequency: e.target.value
                          })}
                        >
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                          <option value="monthly">Monthly</option>
                        </select>
                      </div>
                      <div className="habit-row">
                        <label>Target:</label>
                        <input
                          type="number"
                          min="1"
                          value={taskData.habitTracker.target}
                          onChange={(e) => handleInputChange('habitTracker', {
                            ...taskData.habitTracker,
                            target: parseInt(e.target.value) || 1
                          })}
                        />
                      </div>
                    </div>
                  </div>

                  {/* SPEC-2: Decision Support */}
                  <div className="form-group">
                    <label>Decisions to Track</label>
                    <div className="decisions-section">
                      {taskData.decisions.map(decision => (
                        <div key={decision.id} className="decision-item">
                          <input
                            type="text"
                            value={decision.title}
                            onChange={(e) => updateDecision(decision.id, 'title', e.target.value)}
                            placeholder="Decision title..."
                            className="decision-title"
                          />
                          <textarea
                            value={decision.reasoning}
                            onChange={(e) => updateDecision(decision.id, 'reasoning', e.target.value)}
                            placeholder="Decision reasoning..."
                            className="decision-reasoning"
                            rows={2}
                          />
                          <button
                            className="decision-remove"
                            onClick={() => removeDecision(decision.id)}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                      <button className="add-decision-btn" onClick={addDecision}>
                        + Add Decision
                      </button>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Subtasks</label>
                    <div className="subtasks-section">
                      {taskData.subtasks.map(subtask => (
                        <div key={subtask.id} className="subtask-item">
                          <input
                            type="text"
                            value={subtask.title}
                            onChange={(e) => handleSubtaskUpdate(subtask.id, 'title', e.target.value)}
                            placeholder="Subtask description..."
                            className="subtask-input"
                          />
                          <button
                            className="subtask-remove"
                            onClick={() => handleSubtaskRemove(subtask.id)}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                      <button className="add-subtask-btn" onClick={handleSubtaskAdd}>
                        + Add Subtask
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {currentStep === 4 && (
            <div className="step-content">
              <h3>🤖 AI Analysis & Review</h3>
              
              {!isAIAssisting && aiSuggestions.length === 0 && (
                <div className="ai-analysis-trigger">
                  <p>Let AI analyze your task and provide suggestions for improvement.</p>
                  <button className="analyze-btn" onClick={analyzeTask}>
                    🧠 Analyze Task
                  </button>
                </div>
              )}

              {isAIAssisting && (
                <div className="ai-analyzing">
                  <div className="analyzing-spinner"></div>
                  <p>AI is analyzing your task...</p>
                </div>
              )}

              {aiSuggestions.length > 0 && (
                <div className="ai-suggestions">
                  <h4>AI Suggestions</h4>
                  {aiSuggestions.map((suggestion, index) => (
                    <div key={index} className={`suggestion-item ${suggestion.priority}`}>
                      <div className="suggestion-header">
                        <span className="suggestion-icon">
                          {getSuggestionIcon(suggestion.type)}
                        </span>
                        <span className="suggestion-title">{suggestion.title}</span>
                        <span className={`suggestion-priority ${suggestion.priority}`}>
                          {suggestion.priority}
                        </span>
                      </div>
                      <div className="suggestion-description">
                        {suggestion.description}
                      </div>
                      {suggestion.title === 'Time Estimate May Be Low' && (
                        <button
                          className="apply-suggestion-btn"
                          onClick={() => applySuggestion(suggestion)}
                        >
                          Update to {aiAnalysis.timeEstimate} hours
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {aiAnalysis.complexity && (
                <div className="ai-analysis-results">
                  <h4>Analysis Results</h4>
                  <div className="analysis-grid">
                    <div className="analysis-item">
                      <div className="analysis-label">Complexity</div>
                      <div className={`analysis-value complexity-${aiAnalysis.complexity}`}>
                        {aiAnalysis.complexity.toUpperCase()}
                      </div>
                    </div>
                    
                    <div className="analysis-item">
                      <div className="analysis-label">Suggested Time</div>
                      <div className="analysis-value">
                        {aiAnalysis.timeEstimate}h
                      </div>
                    </div>
                    
                    <div className="analysis-item">
                      <div className="analysis-label">Related Tasks</div>
                      <div className="analysis-value">
                        {aiAnalysis.relatedTasks.length}
                      </div>
                    </div>
                  </div>
                  
                  {aiAnalysis.suggestedBreakdown.length > 0 && (
                    <div className="suggested-breakdown">
                      <div className="breakdown-label">Suggested Breakdown:</div>
                      <ul className="breakdown-list">
                        {aiAnalysis.suggestedBreakdown.map((step, index) => (
                          <li key={index}>{step}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              <div className="task-summary">
                <h4>Task Summary</h4>
                <div className="summary-content">
                  <div className="summary-row">
                    <strong>Title:</strong> {taskData.title}
                  </div>
                  <div className="summary-row">
                    <strong>Category:</strong> {categories.find(c => c.id === taskData.category)?.name}
                  </div>
                  <div className="summary-row">
                    <strong>Priority:</strong> {taskData.priority.toUpperCase()}
                  </div>
                  <div className="summary-row">
                    <strong>Estimated Time:</strong> {taskData.estimatedTime}h
                  </div>
                  <div className="summary-row">
                    <strong>Assigned to:</strong> {availableAgents.find(a => a.id === taskData.assignedAgent)?.name}
                  </div>
                  {taskData.template && (
                    <div className="summary-row">
                      <strong>Template:</strong> {taskTemplates.find(t => t.id === taskData.template)?.name}
                    </div>
                  )}
                  {taskData.mission && (
                    <div className="summary-row">
                      <strong>Mission:</strong> {taskData.mission.substring(0, 60)}...
                    </div>
                  )}
                  {taskData.values.length > 0 && (
                    <div className="summary-row">
                      <strong>Values:</strong> {taskData.values.join(', ')}
                    </div>
                  )}
                  {taskData.tags.length > 0 && (
                    <div className="summary-row">
                      <strong>Tags:</strong> {taskData.tags.join(', ')}
                    </div>
                  )}
                  {taskData.decisions.length > 0 && (
                    <div className="summary-row">
                      <strong>Decisions:</strong> {taskData.decisions.length} tracked
                    </div>
                  )}
                  <div className="summary-row">
                    <strong>Habit Frequency:</strong> {taskData.habitTracker.frequency} (target: {taskData.habitTracker.target})
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="creator-footer">
          <div className="footer-actions">
            {currentStep > 1 && (
              <button
                className="back-btn"
                onClick={() => setCurrentStep(currentStep - 1)}
              >
                ← Back
              </button>
            )}
            
            {currentStep < 4 ? (
              <button
                className="next-btn"
                onClick={() => setCurrentStep(currentStep + 1)}
                disabled={!canProceedToNextStep()}
              >
                Next →
              </button>
            ) : (
              <button
                className="create-btn"
                onClick={handleCreateTask}
                disabled={!canProceedToNextStep()}
              >
                🚀 Create Task
              </button>
            )}
          </div>
        </div>
      </div>
      
      {/* Steve August Template Modal */}
      <SteveAugustTemplate
        isOpen={showSteveAugustTemplate}
        onClose={() => setShowSteveAugustTemplate(false)}
        onTaskCreate={(taskData) => {
          onTaskCreate(taskData);
          setShowSteveAugustTemplate(false);
          onClose();
        }}
        userId={userId}
      />
    </div>
  );
};

export default TaskCreator;