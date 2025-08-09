/**
 * SPEC-2 Task Management Dashboard
 * Displays and manages task templates with license validation and CRUD operations
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Pencil, Plus, Trash as Trash2, Eye, Calendar, User, Tag, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import TaskEditor from './TaskEditor';
import './TaskDashboard.css';

// TypeScript interfaces
interface TaskTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  mission: string;
  values: string[];
  habitTracker: {
    frequency: string;
    target: number;
    streak: number;
    lastCompleted: string | null;
  };
  priority: string;
  estimatedTime: number;
  assignedAgent: string;
  tags: string[];
  created: string;
  updated: string;
  createdBy: string;
  isSystem: boolean;
  isActive: boolean;
  licensed?: boolean;
}

interface Task {
  id: string;
  title: string;
  description: string;
  priority: string;
  estimatedTime: number;
  dueDate: string | null;
  tags: string[];
  assignedAgent: string;
  category: string;
  mission: string;
  values: string[];
  habitTracker: {
    frequency: string;
    target: number;
    streak: number;
    lastCompleted: string | null;
  };
  decisions: any[];
  template: string | null;
  projectContext: string | null;
  memoryTags: string[];
  vaultPath: string | null;
  status: string;
  progress: number;
  createdAt: string;
  updatedAt: string;
}

interface LicenseStatus {
  valid: boolean;
  type: string;
  message: string;
  trialUsesRemaining: number;
  features: string[];
}

interface TaskDashboardProps {
  userId?: string;
  onTaskCreate?: (task: Task) => void;
  focusFormulaLicenseToken?: string;
}

const TaskDashboard: React.FC<TaskDashboardProps> = ({
  userId = 'default-user',
  onTaskCreate,
  focusFormulaLicenseToken
}) => {
  // State management
  const [tasks, setTasks] = useState<Task[]>([]);
  const [templates, setTemplates] = useState<TaskTemplate[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<TaskTemplate | null>(null);
  const [showEditor, setShowEditor] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState<'tasks' | 'templates'>('tasks');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterAgent, setFilterAgent] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // License management
  const [licenseStatus, setLicenseStatus] = useState<LicenseStatus>({
    valid: false,
    type: 'none',
    message: '',
    trialUsesRemaining: 0,
    features: []
  });

  // Load data on component mount
  useEffect(() => {
    loadDashboardData();
    if (focusFormulaLicenseToken) {
      validateLicense();
    }
  }, [focusFormulaLicenseToken]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load templates and tasks in parallel with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const [templatesResponse, tasksResponse] = await Promise.all([
        fetch('/api/templates/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          },
          signal: controller.signal
        }),
        fetch('/api/vault/tasks/list', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          },
          signal: controller.signal
        })
      ]);
      
      clearTimeout(timeoutId);

      if (templatesResponse.ok) {
        const templatesData = await templatesResponse.json();
        setTemplates(templatesData);
      }

      if (tasksResponse.ok) {
        const tasksData = await tasksResponse.json();
        setTasks(tasksData.tasks || []);
      }

    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const validateLicense = async () => {
    if (!focusFormulaLicenseToken) return;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('/api/templates/validate-license', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          templateId: 'steve-august-focus-formula',
          licenseKey: focusFormulaLicenseToken,
          userId: userId
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        const result = await response.json();
        setLicenseStatus({
          valid: result.valid,
          type: result.licenseType || 'none',
          message: result.message || '',
          trialUsesRemaining: result.usageLimit ? result.usageLimit - (result.currentUsage || 0) : 0,
          features: result.features || []
        });
      }
    } catch (err) {
      console.error('License validation failed:', err);
    }
  };

  // Task CRUD operations with optimistic updates
  const handleCreateTask = useCallback(async (taskId: string, taskData: Partial<Task>) => {
    const tempId = `temp_${Date.now()}`;
    const newTask: Task = {
      id: tempId,
      title: taskData.title || 'New Task',
      description: taskData.description || '',
      priority: taskData.priority || 'medium',
      estimatedTime: taskData.estimatedTime || 1,
      dueDate: taskData.dueDate || null,
      tags: taskData.tags || [],
      assignedAgent: taskData.assignedAgent || 'alden',
      category: taskData.category || 'general',
      mission: taskData.mission || '',
      values: taskData.values || [],
      habitTracker: taskData.habitTracker || {
        frequency: 'daily',
        target: 1,
        streak: 0,
        lastCompleted: null
      },
      decisions: taskData.decisions || [],
      template: taskData.template || null,
      projectContext: taskData.projectContext || null,
      memoryTags: taskData.memoryTags || [],
      vaultPath: taskData.vaultPath || null,
      status: 'todo',
      progress: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    // Optimistic update
    setTasks(prev => [newTask, ...prev]);

    try {
      // API call with audit logging and timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('/api/vault/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          task: newTask,
          vaultPath: newTask.vaultPath || `tasks/${newTask.assignedAgent}/${tempId}`,
          encrypted: true,
          memoryTags: newTask.memoryTags,
          auditLog: {
            operation: 'CREATE',
            entityType: 'task',
            entityId: tempId,
            userId: userId,
            timestamp: new Date().toISOString()
          }
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error('Failed to create task');
      }

      const result = await response.json();
      
      // Update with real ID from server
      setTasks(prev => prev.map(task => 
        task.id === tempId ? { ...newTask, id: result.id } : task
      ));

      // Record template usage if applicable
      if (newTask.template === 'steve-august-focus-formula' && focusFormulaLicenseToken) {
        await recordTemplateUsage();
      }

      onTaskCreate?.(newTask);

    } catch (err) {
      console.error('Failed to create task:', err);
      
      // Rollback optimistic update
      setTasks(prev => prev.filter(task => task.id !== tempId));
      setError('Failed to create task. Please try again.');
    }
  }, [userId, focusFormulaLicenseToken, onTaskCreate]);

  const handleUpdateTask = useCallback(async (taskId: string, taskData: Partial<Task>) => {
    const originalTask = tasks.find(task => task.id === taskId);
    if (!originalTask) return;

    const updatedTask = { ...originalTask, ...taskData, updatedAt: new Date().toISOString() };

    // Optimistic update
    setTasks(prev => prev.map(task => task.id === taskId ? updatedTask : task));

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`/api/vault/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          task: updatedTask,
          auditLog: {
            operation: 'UPDATE',
            entityType: 'task',
            entityId: taskId,
            userId: userId,
            timestamp: new Date().toISOString(),
            changes: taskData
          }
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error('Failed to update task');
      }

    } catch (err) {
      console.error('Failed to update task:', err);
      
      // Rollback optimistic update
      setTasks(prev => prev.map(task => task.id === taskId ? originalTask : task));
      setError('Failed to update task. Please try again.');
    }
  }, [tasks, userId]);

  const handleDeleteTask = useCallback(async (taskId: string) => {
    const taskToDelete = tasks.find(task => task.id === taskId);
    if (!taskToDelete) return;

    // Optimistic update
    setTasks(prev => prev.filter(task => task.id !== taskId));

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`/api/vault/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error('Failed to delete task');
      }

      // Audit log for deletion
      const auditController = new AbortController();
      const auditTimeoutId = setTimeout(() => auditController.abort(), 5000);
      
      await fetch('/api/templates/audit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          operation: 'DELETE',
          entityType: 'task',
          entityId: taskId,
          userId: userId,
          timestamp: new Date().toISOString()
        }),
        signal: auditController.signal
      });
      
      clearTimeout(auditTimeoutId);

    } catch (err) {
      console.error('Failed to delete task:', err);
      
      // Rollback optimistic update
      setTasks(prev => [...prev, taskToDelete]);
      setError('Failed to delete task. Please try again.');
    }
  }, [tasks, userId]);

  const recordTemplateUsage = async () => {
    if (!focusFormulaLicenseToken) return;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      await fetch('/api/templates/record-usage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          templateId: 'steve-august-focus-formula',
          licenseKey: focusFormulaLicenseToken,
          userId: userId,
          action: 'create_task'
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
    } catch (err) {
      console.error('Failed to record template usage:', err);
    }
  };

  // Filter and search functionality
  const filteredTasks = tasks.filter(task => {
    const matchesCategory = filterCategory === 'all' || task.category === filterCategory;
    const matchesAgent = filterAgent === 'all' || task.assignedAgent === filterAgent;
    const matchesSearch = searchQuery === '' || 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesCategory && matchesAgent && matchesSearch;
  });

  const filteredTemplates = templates.filter(template => {
    // Hide Steve August template if no valid license
    if (template.id === 'steve-august-focus-formula') {
      return focusFormulaLicenseToken && licenseStatus.valid;
    }
    
    const matchesSearch = searchQuery === '' || 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesSearch && template.isActive;
  });

  const handleEditTask = (task: Task) => {
    setSelectedTask(task);
    setSelectedTemplate(null);
    setShowEditor(true);
  };

  const handleCreateFromTemplate = (template: TaskTemplate) => {
    setSelectedTemplate(template);
    setSelectedTask(null);
    setShowEditor(true);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-900/20';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20';
      case 'low': return 'text-green-400 bg-green-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-900/20';
      case 'in-progress': return 'text-blue-400 bg-blue-900/20';
      case 'todo': return 'text-gray-400 bg-gray-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  if (loading) {
    return (
      <div className="task-dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading Task Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="task-dashboard">
      <div className="dashboard-header">
        <h1>📋 Task Management Dashboard</h1>
        
        {error && (
          <div className="error-banner">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
            <button onClick={() => setError(null)} className="ml-auto">×</button>
          </div>
        )}

        {/* License Status */}
        {focusFormulaLicenseToken && (
          <div className={`license-status ${licenseStatus.valid ? 'valid' : 'invalid'}`}>
            {licenseStatus.valid ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <AlertCircle className="w-5 h-5" />
            )}
            <span>Steve August License: {licenseStatus.message}</span>
            {licenseStatus.type === 'trial' && (
              <span className="trial-info">({licenseStatus.trialUsesRemaining} uses remaining)</span>
            )}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button
            className={`tab-button ${activeTab === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasks')}
          >
            <Calendar className="w-4 h-4" />
            Tasks ({filteredTasks.length})
          </button>
          <button
            className={`tab-button ${activeTab === 'templates' ? 'active' : ''}`}
            onClick={() => setActiveTab('templates')}
          >
            <Tag className="w-4 h-4" />
            Templates ({filteredTemplates.length})
          </button>
        </div>

        {/* Filters and Search */}
        <div className="dashboard-filters">
          <input
            type="text"
            placeholder="Search tasks and templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          
          {activeTab === 'tasks' && (
            <>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Categories</option>
                <option value="development">Development</option>
                <option value="design">Design</option>
                <option value="research">Research</option>
                <option value="productivity">Productivity</option>
                <option value="adhd-coaching">ADHD Coaching</option>
              </select>
              
              <select
                value={filterAgent}
                onChange={(e) => setFilterAgent(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Agents</option>
                <option value="alden">Alden</option>
                <option value="alice">Alice</option>
                <option value="mimic">Mimic</option>
                <option value="sentry">Sentry</option>
              </select>
            </>
          )}

          <button
            onClick={() => {
              setSelectedTask(null);
              setSelectedTemplate(null);
              setShowEditor(true);
            }}
            className="create-button"
          >
            <Plus className="w-4 h-4" />
            Create New
          </button>
        </div>
      </div>

      {/* Tasks Tab */}
      {activeTab === 'tasks' && (
        <div className="tasks-grid">
          {filteredTasks.length === 0 ? (
            <div className="empty-state">
              <Calendar className="w-12 h-12 text-gray-500" />
              <h3>No tasks found</h3>
              <p>Create your first task or adjust your filters</p>
            </div>
          ) : (
            filteredTasks.map(task => (
              <div key={task.id} className="task-card">
                <div className="task-card-header">
                  <h3 className="task-title">{task.title}</h3>
                  <div className="task-actions">
                    <button
                      onClick={() => handleEditTask(task)}
                      className="action-button edit"
                      title="Edit task"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteTask(task.id)}
                      className="action-button delete"
                      title="Delete task"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <p className="task-description">{task.description}</p>
                
                <div className="task-metadata">
                  <span className={`priority-badge ${getPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                  <span className={`status-badge ${getStatusColor(task.status)}`}>
                    {task.status}
                  </span>
                  <div className="task-agent">
                    <User className="w-4 h-4" />
                    {task.assignedAgent}
                  </div>
                  <div className="task-time">
                    <Clock className="w-4 h-4" />
                    {task.estimatedTime}h
                  </div>
                </div>
                
                {task.tags.length > 0 && (
                  <div className="task-tags">
                    {task.tags.slice(0, 3).map(tag => (
                      <span key={tag} className="task-tag">{tag}</span>
                    ))}
                    {task.tags.length > 3 && (
                      <span className="task-tag-more">+{task.tags.length - 3}</span>
                    )}
                  </div>
                )}
                
                {task.template === 'steve-august-focus-formula' && (
                  <div className="template-credit">
                    <a 
                      href="https://steve-august.com" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="credit-link"
                    >
                      Steve August – ADHD Coaching
                    </a>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="templates-grid">
          {filteredTemplates.length === 0 ? (
            <div className="empty-state">
              <Tag className="w-12 h-12 text-gray-500" />
              <h3>No templates available</h3>
              <p>Templates will appear here when available</p>
            </div>
          ) : (
            filteredTemplates.map(template => (
              <div key={template.id} className="template-card">
                <div className="template-card-header">
                  <h3 className="template-title">{template.name}</h3>
                  {template.id === 'steve-august-focus-formula' && (
                    <span className="licensed-badge">🔐 Licensed</span>
                  )}
                </div>
                
                <p className="template-description">{template.description}</p>
                
                <div className="template-metadata">
                  <span className="template-category">{template.category}</span>
                  <div className="template-agent">
                    <User className="w-4 h-4" />
                    {template.assignedAgent}
                  </div>
                  <div className="template-time">
                    <Clock className="w-4 h-4" />
                    {template.estimatedTime}h
                  </div>
                </div>
                
                <div className="template-values">
                  {template.values.slice(0, 3).map(value => (
                    <span key={value} className="template-value">{value}</span>
                  ))}
                  {template.values.length > 3 && (
                    <span className="template-value-more">+{template.values.length - 3}</span>
                  )}
                </div>
                
                <button
                  onClick={() => handleCreateFromTemplate(template)}
                  className="template-use-button"
                >
                  <Plus className="w-4 h-4" />
                  Use Template
                </button>
                
                {template.id === 'steve-august-focus-formula' && (
                  <div className="template-credit">
                    <a 
                      href="https://steve-august.com" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="credit-link"
                    >
                      Steve August – ADHD Coaching
                    </a>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Task Editor Modal */}
      {showEditor && (
        <TaskEditor
          task={selectedTask}
          template={selectedTemplate}
          onSave={selectedTask ? handleUpdateTask : handleCreateTask}
          onClose={() => {
            setShowEditor(false);
            setSelectedTask(null);
            setSelectedTemplate(null);
          }}
          userId={userId}
          focusFormulaLicenseToken={focusFormulaLicenseToken}
        />
      )}
    </div>
  );
};

export default TaskDashboard;