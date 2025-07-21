import React, { useState, useEffect, useCallback } from 'react';
import './TaskDashboard.css';
import TaskCreator from '../TaskCreator';

const TaskDashboard = ({ data, isExpanded, onTaskCreate, onTaskUpdate }) => {
  const [tasks, setTasks] = useState(data?.tasks || []);
  const [projects, setProjects] = useState(data?.projects || []);
  const [activeView, setActiveView] = useState('overview');
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  // Quick task creation state
  const [quickTaskTitle, setQuickTaskTitle] = useState('');
  const [quickTaskPriority, setQuickTaskPriority] = useState('medium');

  // Performance metrics
  const [metrics, setMetrics] = useState({
    totalTasks: 0,
    completedToday: 0,
    inProgress: 0,
    overdue: 0,
    completionRate: 0,
    avgCompletionTime: 0,
    productivityScore: 0
  });

  // Update metrics when tasks change
  useEffect(() => {
    const today = new Date().toDateString();
    const totalTasks = tasks.length;
    const completed = tasks.filter(t => t.status === 'completed');
    const completedToday = completed.filter(t => new Date(t.completedAt).toDateString() === today).length;
    const inProgress = tasks.filter(t => t.status === 'in_progress').length;
    const overdue = tasks.filter(t => t.dueDate && new Date(t.dueDate) < new Date() && t.status !== 'completed').length;
    const completionRate = totalTasks > 0 ? (completed.length / totalTasks) * 100 : 0;
    
    // Calculate average completion time
    const completedWithTime = completed.filter(t => t.completedAt && t.createdAt);
    const avgCompletionTime = completedWithTime.length > 0 
      ? completedWithTime.reduce((sum, task) => {
          const created = new Date(task.createdAt);
          const completed = new Date(task.completedAt);
          return sum + (completed - created);
        }, 0) / completedWithTime.length / (1000 * 60 * 60) // Convert to hours
      : 0;

    // Calculate productivity score (weighted combination of metrics)
    const productivityScore = Math.round(
      (completionRate * 0.4) + 
      (Math.max(0, (24 - avgCompletionTime) / 24) * 30) + // Faster completion = higher score
      (Math.max(0, (totalTasks - overdue) / Math.max(totalTasks, 1)) * 30) // Fewer overdue = higher score
    );

    setMetrics({
      totalTasks,
      completedToday,
      inProgress,
      overdue,
      completionRate,
      avgCompletionTime,
      productivityScore
    });
  }, [tasks]);

  const handleQuickTaskCreate = useCallback(async () => {
    if (!quickTaskTitle.trim()) return;

    const newTask = {
      id: `task_${Date.now()}`,
      title: quickTaskTitle,
      description: '',
      priority: quickTaskPriority,
      status: 'todo',
      createdAt: new Date().toISOString(),
      dueDate: null,
      tags: [],
      estimatedTime: 0,
      assignedAgent: 'alden',
      progress: 0
    };

    setTasks(prev => [newTask, ...prev]);
    setQuickTaskTitle('');
    
    if (onTaskCreate) {
      onTaskCreate(newTask);
    }
  }, [quickTaskTitle, quickTaskPriority, onTaskCreate]);

  const handleTaskStatusChange = useCallback((taskId, newStatus) => {
    setTasks(prev => prev.map(task => {
      if (task.id === taskId) {
        const updatedTask = {
          ...task,
          status: newStatus,
          completedAt: newStatus === 'completed' ? new Date().toISOString() : task.completedAt,
          progress: newStatus === 'completed' ? 100 : task.progress
        };
        
        if (onTaskUpdate) {
          onTaskUpdate(updatedTask);
        }
        
        return updatedTask;
      }
      return task;
    }));
  }, [onTaskUpdate]);

  const handleAdvancedTaskCreate = useCallback((newTask) => {
    setTasks(prev => [newTask, ...prev]);
    setShowCreateModal(false);
    
    if (onTaskCreate) {
      onTaskCreate(newTask);
    }
  }, [onTaskCreate]);

  const filteredTasks = tasks.filter(task => {
    const matchesPriority = selectedPriority === 'all' || task.priority === selectedPriority;
    const matchesSearch = searchQuery === '' || 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesPriority && matchesSearch;
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '⚡';
      case 'blocked': return '🚫';
      case 'todo': return '📋';
      default: return '📋';
    }
  };

  if (!isExpanded) {
    // Compact preview for panel grid
    return (
      <div className="task-dashboard-preview">
        <div className="productivity-score">
          <div className="score-ring" style={{
            background: `conic-gradient(#22d3ee ${metrics.productivityScore * 3.6}deg, rgba(34, 211, 238, 0.2) 0deg)`,
            borderRadius: '50%',
            width: '60px',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.8rem',
            fontWeight: 'bold',
            color: '#22d3ee'
          }}>
            {metrics.productivityScore}
          </div>
          <div className="score-label">Productivity Score</div>
        </div>
        
        <div className="task-stats-preview">
          <div className="stat-item">
            <span className="stat-value">{metrics.totalTasks}</span>
            <span className="stat-label">Total Tasks</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{metrics.completedToday}</span>
            <span className="stat-label">Done Today</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{metrics.inProgress}</span>
            <span className="stat-label">In Progress</span>
          </div>
          {metrics.overdue > 0 && (
            <div className="stat-item overdue">
              <span className="stat-value">{metrics.overdue}</span>
              <span className="stat-label">Overdue</span>
            </div>
          )}
        </div>

        <div className="quick-add-preview">
          <input
            type="text"
            placeholder="Quick task..."
            value={quickTaskTitle}
            onChange={(e) => setQuickTaskTitle(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.stopPropagation();
                handleQuickTaskCreate();
              }
            }}
            className="quick-task-input"
          />
          <select
            value={quickTaskPriority}
            onChange={(e) => setQuickTaskPriority(e.target.value)}
            className="quick-priority-select"
            onClick={(e) => e.stopPropagation()}
          >
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleQuickTaskCreate();
            }}
            className="quick-add-btn"
            disabled={!quickTaskTitle.trim()}
          >
            ＋
          </button>
        </div>
      </div>
    );
  }

  // Expanded view
  return (
    <div className="task-dashboard-expanded">
      <div className="dashboard-header">
        <h2>Task Management Dashboard</h2>
        <div className="header-actions">
          <button
            className="create-task-btn"
            onClick={() => setShowCreateModal(true)}
          >
            ＋ New Task
          </button>
        </div>
      </div>

      <div className="dashboard-nav">
        <button
          className={`nav-btn ${activeView === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveView('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`nav-btn ${activeView === 'tasks' ? 'active' : ''}`}
          onClick={() => setActiveView('tasks')}
        >
          📋 Tasks
        </button>
        <button
          className={`nav-btn ${activeView === 'projects' ? 'active' : ''}`}
          onClick={() => setActiveView('projects')}
        >
          📁 Projects
        </button>
        <button
          className={`nav-btn ${activeView === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveView('analytics')}
        >
          📈 Analytics
        </button>
      </div>

      {activeView === 'overview' && (
        <div className="overview-content">
          <div className="metrics-grid">
            <div className="metric-card productivity">
              <div className="metric-icon">🎯</div>
              <div className="metric-data">
                <div className="metric-value">{metrics.productivityScore}</div>
                <div className="metric-label">Productivity Score</div>
              </div>
            </div>
            
            <div className="metric-card completion">
              <div className="metric-icon">✅</div>
              <div className="metric-data">
                <div className="metric-value">{Math.round(metrics.completionRate)}%</div>
                <div className="metric-label">Completion Rate</div>
              </div>
            </div>
            
            <div className="metric-card time">
              <div className="metric-icon">⏱️</div>
              <div className="metric-data">
                <div className="metric-value">{Math.round(metrics.avgCompletionTime)}h</div>
                <div className="metric-label">Avg Completion</div>
              </div>
            </div>
            
            <div className="metric-card today">
              <div className="metric-icon">📅</div>
              <div className="metric-data">
                <div className="metric-value">{metrics.completedToday}</div>
                <div className="metric-label">Done Today</div>
              </div>
            </div>
          </div>

          <div className="task-summary">
            <div className="summary-header">
              <h3>Task Summary</h3>
              <div className="task-filters">
                <select
                  value={selectedPriority}
                  onChange={(e) => setSelectedPriority(e.target.value)}
                  className="priority-filter"
                >
                  <option value="all">All Priorities</option>
                  <option value="high">High Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="low">Low Priority</option>
                </select>
                <input
                  type="text"
                  placeholder="Search tasks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />
              </div>
            </div>
            
            <div className="task-list">
              {filteredTasks.slice(0, 10).map(task => (
                <div key={task.id} className={`task-item ${task.status}`}>
                  <div className="task-status-control">
                    <button
                      className="status-btn"
                      onClick={() => {
                        const nextStatus = task.status === 'completed' ? 'todo' : 
                                         task.status === 'todo' ? 'in_progress' : 'completed';
                        handleTaskStatusChange(task.id, nextStatus);
                      }}
                    >
                      {getStatusIcon(task.status)}
                    </button>
                  </div>
                  
                  <div className="task-content">
                    <div className="task-title">{task.title}</div>
                    <div className="task-meta">
                      <span 
                        className="priority-badge"
                        style={{ backgroundColor: getPriorityColor(task.priority) }}
                      >
                        {task.priority}
                      </span>
                      {task.dueDate && (
                        <span className="due-date">
                          Due: {new Date(task.dueDate).toLocaleDateString()}
                        </span>
                      )}
                      {task.estimatedTime > 0 && (
                        <span className="estimated-time">
                          ~{task.estimatedTime}h
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {task.progress > 0 && task.status !== 'completed' && (
                    <div className="task-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span className="progress-text">{task.progress}%</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeView === 'tasks' && (
        <div className="tasks-content">
          <div className="tasks-header">
            <h3>All Tasks ({filteredTasks.length})</h3>
            <div className="task-actions">
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              <select
                value={selectedPriority}
                onChange={(e) => setSelectedPriority(e.target.value)}
                className="priority-filter"
              >
                <option value="all">All Priorities</option>
                <option value="high">High Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="low">Low Priority</option>
              </select>
            </div>
          </div>

          <div className="detailed-task-list">
            {filteredTasks.map(task => (
              <div key={task.id} className={`detailed-task-item ${task.status}`}>
                <div className="task-main">
                  <button
                    className="status-toggle"
                    onClick={() => {
                      const nextStatus = task.status === 'completed' ? 'todo' : 
                                       task.status === 'todo' ? 'in_progress' : 'completed';
                      handleTaskStatusChange(task.id, nextStatus);
                    }}
                  >
                    {getStatusIcon(task.status)}
                  </button>
                  
                  <div className="task-info">
                    <div className="task-title">{task.title}</div>
                    {task.description && (
                      <div className="task-description">{task.description}</div>
                    )}
                    <div className="task-metadata">
                      <span 
                        className="priority-badge"
                        style={{ backgroundColor: getPriorityColor(task.priority) }}
                      >
                        {task.priority}
                      </span>
                      <span className="created-date">
                        Created: {new Date(task.createdAt).toLocaleDateString()}
                      </span>
                      {task.dueDate && (
                        <span className={`due-date ${new Date(task.dueDate) < new Date() ? 'overdue' : ''}`}>
                          Due: {new Date(task.dueDate).toLocaleDateString()}
                        </span>
                      )}
                      {task.assignedAgent && (
                        <span className="assigned-agent">
                          Assigned: {task.assignedAgent}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                {task.progress > 0 && task.status !== 'completed' && (
                  <div className="task-progress-detailed">
                    <div className="progress-header">
                      <span>Progress</span>
                      <span>{task.progress}%</span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeView === 'analytics' && (
        <div className="analytics-content">
          <h3>Productivity Analytics</h3>
          <div className="analytics-grid">
            <div className="analytics-card">
              <h4>Completion Trends</h4>
              <div className="trend-visualization">
                {/* Simple visualization - in production would use a charting library */}
                <div className="trend-bars">
                  {Array.from({ length: 7 }, (_, i) => (
                    <div
                      key={i}
                      className="trend-bar"
                      style={{
                        height: `${Math.random() * 80 + 20}%`,
                        backgroundColor: '#22d3ee'
                      }}
                    />
                  ))}
                </div>
                <div className="trend-labels">
                  <span>7d ago</span>
                  <span>Today</span>
                </div>
              </div>
            </div>
            
            <div className="analytics-card">
              <h4>Priority Distribution</h4>
              <div className="priority-distribution">
                {['high', 'medium', 'low'].map(priority => {
                  const count = tasks.filter(t => t.priority === priority).length;
                  const percentage = tasks.length > 0 ? (count / tasks.length) * 100 : 0;
                  return (
                    <div key={priority} className="priority-item">
                      <div className="priority-info">
                        <span className="priority-name">{priority}</span>
                        <span className="priority-count">{count}</span>
                      </div>
                      <div className="priority-bar">
                        <div 
                          className="priority-fill"
                          style={{ 
                            width: `${percentage}%`,
                            backgroundColor: getPriorityColor(priority)
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TaskCreator Modal */}
      <TaskCreator
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onTaskCreate={handleAdvancedTaskCreate}
        existingTasks={tasks}
        agents={[
          { id: 'alden', name: 'Alden', specialties: ['planning', 'coordination', 'management'] },
          { id: 'alice', name: 'Alice', specialties: ['analysis', 'testing', 'research'] },
          { id: 'mimic', name: 'Mimic', specialties: ['development', 'coding', 'implementation'] },
          { id: 'sentry', name: 'Sentry', specialties: ['security', 'monitoring', 'maintenance'] }
        ]}
      />
    </div>
  );
};

export default TaskDashboard;