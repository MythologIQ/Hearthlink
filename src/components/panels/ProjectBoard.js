import React, { useState, useEffect, useCallback } from 'react';
import './ProjectBoard.css';

const ProjectBoard = ({ data, isExpanded, onProjectCreate, onProjectUpdate, onTaskUpdate }) => {
  const [projects, setProjects] = useState(data?.projects || []);
  const [tasks, setTasks] = useState(data?.tasks || []);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [draggedTask, setDraggedTask] = useState(null);
  const [boardView, setBoardView] = useState('kanban'); // kanban, timeline, list
  
  // Project creation form state
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    dueDate: '',
    priority: 'medium',
    status: 'planning',
    color: '#22d3ee'
  });

  // Kanban columns configuration
  const kanbanColumns = [
    { id: 'backlog', title: 'Backlog', color: '#6b7280', limit: null },
    { id: 'todo', title: 'To Do', color: '#22d3ee', limit: 8 },
    { id: 'in_progress', title: 'In Progress', color: '#fbbf24', limit: 3 },
    { id: 'review', title: 'Review', color: '#8b5cf6', limit: 5 },
    { id: 'completed', title: 'Completed', color: '#10b981', limit: null }
  ];

  // Project status configuration
  const projectStatuses = [
    { id: 'planning', name: 'Planning', color: '#6b7280' },
    { id: 'active', name: 'Active', color: '#22d3ee' },
    { id: 'on_hold', name: 'On Hold', color: '#fbbf24' },
    { id: 'completed', name: 'Completed', color: '#10b981' },
    { id: 'cancelled', name: 'Cancelled', color: '#ef4444' }
  ];

  // Update local state when props change
  useEffect(() => {
    setProjects(data?.projects || []);
    setTasks(data?.tasks || []);
  }, [data]);

  // Auto-select first project if none selected
  useEffect(() => {
    if (projects.length > 0 && !selectedProject) {
      setSelectedProject(projects[0]);
    }
  }, [projects, selectedProject]);

  // Get tasks for selected project
  const getProjectTasks = useCallback((project) => {
    if (!project) return [];
    return tasks.filter(task => project.taskIds?.includes(task.id) || task.projectId === project.id);
  }, [tasks]);

  // Get tasks by column
  const getTasksByColumn = useCallback((columnId) => {
    const projectTasks = getProjectTasks(selectedProject);
    return projectTasks.filter(task => {
      // Map task status to kanban columns
      switch (columnId) {
        case 'backlog':
          return task.status === 'backlog' || (!task.status && task.priority === 'low');
        case 'todo':
          return task.status === 'todo' || !task.status;
        case 'in_progress':
          return task.status === 'in_progress';
        case 'review':
          return task.status === 'review' || task.status === 'blocked';
        case 'completed':
          return task.status === 'completed';
        default:
          return false;
      }
    });
  }, [selectedProject, getProjectTasks]);

  // Calculate project progress
  const calculateProjectProgress = useCallback((project) => {
    const projectTasks = getProjectTasks(project);
    if (projectTasks.length === 0) return 0;
    
    const completedTasks = projectTasks.filter(task => task.status === 'completed').length;
    return Math.round((completedTasks / projectTasks.length) * 100);
  }, [getProjectTasks]);

  // Handle project creation
  const handleCreateProject = useCallback(async () => {
    if (!newProject.name.trim()) return;

    const project = {
      id: `project_${Date.now()}`,
      ...newProject,
      createdAt: new Date().toISOString(),
      taskIds: [],
      progress: 0
    };

    setProjects(prev => [project, ...prev]);
    setShowCreateProject(false);
    setNewProject({
      name: '',
      description: '',
      dueDate: '',
      priority: 'medium',
      status: 'planning',
      color: '#22d3ee'
    });

    if (onProjectCreate) {
      onProjectCreate(project);
    }

    // Auto-select the new project
    setSelectedProject(project);
  }, [newProject, onProjectCreate]);

  // Handle task status change via drag and drop
  const handleTaskMove = useCallback((taskId, newStatus) => {
    const updatedTasks = tasks.map(task => {
      if (task.id === taskId) {
        return {
          ...task,
          status: newStatus,
          completedAt: newStatus === 'completed' ? new Date().toISOString() : task.completedAt,
          progress: newStatus === 'completed' ? 100 : task.progress
        };
      }
      return task;
    });

    setTasks(updatedTasks);
    
    if (onTaskUpdate) {
      const updatedTask = updatedTasks.find(t => t.id === taskId);
      onTaskUpdate(updatedTask);
    }
  }, [tasks, onTaskUpdate]);

  // Drag and drop handlers
  const handleDragStart = useCallback((e, task) => {
    setDraggedTask(task);
    e.dataTransfer.effectAllowed = 'move';
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }, []);

  const handleDrop = useCallback((e, columnId) => {
    e.preventDefault();
    if (!draggedTask) return;

    // Map column to task status
    const statusMap = {
      backlog: 'backlog',
      todo: 'todo',
      in_progress: 'in_progress',
      review: 'review',
      completed: 'completed'
    };

    handleTaskMove(draggedTask.id, statusMap[columnId]);
    setDraggedTask(null);
  }, [draggedTask, handleTaskMove]);

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#fbbf24';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  // Render compact preview for panel grid
  if (!isExpanded) {
    return (
      <div className="project-board-preview">
        <div className="preview-header">
          <h4>Projects</h4>
          <span className="project-count">{projects.length}</span>
        </div>
        
        <div className="projects-mini-list">
          {projects.slice(0, 3).map(project => (
            <div key={project.id} className="project-mini-item">
              <div 
                className="project-color-dot" 
                style={{ backgroundColor: project.color || '#22d3ee' }}
              />
              <div className="project-mini-info">
                <div className="project-mini-name">{project.name}</div>
                <div className="project-mini-progress">
                  <div className="mini-progress-bar">
                    <div 
                      className="mini-progress-fill"
                      style={{ 
                        width: `${calculateProjectProgress(project)}%`,
                        backgroundColor: project.color || '#22d3ee'
                      }}
                    />
                  </div>
                  <span className="mini-progress-text">
                    {calculateProjectProgress(project)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {projects.length > 3 && (
          <div className="preview-more">
            +{projects.length - 3} more projects
          </div>
        )}
      </div>
    );
  }

  // Expanded view
  return (
    <div className="project-board-expanded">
      {/* Header */}
      <div className="project-board-header">
        <div className="header-left">
          <h2>Project Board</h2>
          <div className="view-toggles">
            <button
              className={`view-toggle ${boardView === 'kanban' ? 'active' : ''}`}
              onClick={() => setBoardView('kanban')}
            >
              📋 Kanban
            </button>
            <button
              className={`view-toggle ${boardView === 'timeline' ? 'active' : ''}`}
              onClick={() => setBoardView('timeline')}
            >
              📅 Timeline
            </button>
            <button
              className={`view-toggle ${boardView === 'list' ? 'active' : ''}`}
              onClick={() => setBoardView('list')}
            >
              📝 List
            </button>
          </div>
        </div>
        
        <div className="header-actions">
          <button
            className="create-project-btn"
            onClick={() => setShowCreateProject(true)}
          >
            ✨ New Project
          </button>
        </div>
      </div>

      {/* Project Selector */}
      <div className="project-selector">
        <div className="project-tabs">
          {projects.map(project => (
            <button
              key={project.id}
              className={`project-tab ${selectedProject?.id === project.id ? 'active' : ''}`}
              onClick={() => setSelectedProject(project)}
            >
              <div 
                className="project-tab-color"
                style={{ backgroundColor: project.color }}
              />
              <span className="project-tab-name">{project.name}</span>
              <div className="project-tab-stats">
                <span className="task-count">
                  {getProjectTasks(project).length}
                </span>
                <span className="progress-mini">
                  {calculateProjectProgress(project)}%
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Board Content */}
      <div className="board-content">
        {selectedProject ? (
          <>
            {/* Project Info Panel */}
            <div className="project-info-panel">
              <div className="project-title-section">
                <h3>{selectedProject.name}</h3>
                <div className="project-status-badges">
                  <span 
                    className={`status-badge ${selectedProject.status}`}
                    style={{ 
                      backgroundColor: projectStatuses.find(s => s.id === selectedProject.status)?.color 
                    }}
                  >
                    {projectStatuses.find(s => s.id === selectedProject.status)?.name}
                  </span>
                  <span 
                    className="priority-badge"
                    style={{ backgroundColor: getPriorityColor(selectedProject.priority) }}
                  >
                    {selectedProject.priority?.toUpperCase()}
                  </span>
                </div>
              </div>
              
              <div className="project-progress-section">
                <div className="progress-info">
                  <span className="progress-label">Progress</span>
                  <span className="progress-value">{calculateProjectProgress(selectedProject)}%</span>
                </div>
                <div className="progress-bar-full">
                  <div 
                    className="progress-bar-fill"
                    style={{ 
                      width: `${calculateProjectProgress(selectedProject)}%`,
                      backgroundColor: selectedProject.color 
                    }}
                  />
                </div>
              </div>

              <div className="project-stats">
                <div className="stat-item">
                  <span className="stat-value">{getProjectTasks(selectedProject).length}</span>
                  <span className="stat-label">Total Tasks</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">
                    {getProjectTasks(selectedProject).filter(t => t.status === 'completed').length}
                  </span>
                  <span className="stat-label">Completed</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">
                    {getProjectTasks(selectedProject).filter(t => t.status === 'in_progress').length}
                  </span>
                  <span className="stat-label">In Progress</span>
                </div>
              </div>
            </div>

            {/* Kanban Board */}
            {boardView === 'kanban' && (
              <div className="kanban-board">
                {kanbanColumns.map(column => (
                  <div 
                    key={column.id}
                    className="kanban-column"
                    onDragOver={handleDragOver}
                    onDrop={(e) => handleDrop(e, column.id)}
                  >
                    <div className="column-header">
                      <div className="column-title">
                        <div 
                          className="column-color-indicator"
                          style={{ backgroundColor: column.color }}
                        />
                        <span>{column.title}</span>
                        <span className="task-count-badge">
                          {getTasksByColumn(column.id).length}
                        </span>
                      </div>
                      {column.limit && (
                        <div className="column-limit">
                          Limit: {column.limit}
                        </div>
                      )}
                    </div>

                    <div className="kanban-tasks">
                      {getTasksByColumn(column.id).map(task => (
                        <div
                          key={task.id}
                          className="kanban-task"
                          draggable
                          onDragStart={(e) => handleDragStart(e, task)}
                        >
                          <div className="task-header">
                            <div className="task-priority-dot">
                              <div 
                                className="priority-indicator"
                                style={{ backgroundColor: getPriorityColor(task.priority) }}
                              />
                            </div>
                            <div className="task-id">#{task.id.slice(-4)}</div>
                          </div>
                          
                          <div className="task-title">{task.title}</div>
                          
                          {task.description && (
                            <div className="task-description">{task.description}</div>
                          )}

                          <div className="task-footer">
                            {task.tags && task.tags.length > 0 && (
                              <div className="task-tags">
                                {task.tags.slice(0, 2).map(tag => (
                                  <span key={tag} className="task-tag">{tag}</span>
                                ))}
                                {task.tags.length > 2 && (
                                  <span className="tag-more">+{task.tags.length - 2}</span>
                                )}
                              </div>
                            )}
                            
                            <div className="task-meta">
                              {task.assignedAgent && (
                                <div className="assigned-agent">{task.assignedAgent}</div>
                              )}
                              {task.dueDate && (
                                <div className="due-date">
                                  {new Date(task.dueDate).toLocaleDateString()}
                                </div>
                              )}
                            </div>
                          </div>

                          {task.progress > 0 && task.status !== 'completed' && (
                            <div className="task-progress">
                              <div className="progress-bar-mini">
                                <div 
                                  className="progress-fill-mini"
                                  style={{ width: `${task.progress}%` }}
                                />
                              </div>
                              <span className="progress-text-mini">{task.progress}%</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Timeline View Placeholder */}
            {boardView === 'timeline' && (
              <div className="timeline-view">
                <div className="timeline-placeholder">
                  <h3>📅 Timeline View</h3>
                  <p>Timeline visualization coming soon...</p>
                  <div className="timeline-mockup">
                    {/* Simple timeline mockup */}
                    <div className="timeline-items">
                      {getProjectTasks(selectedProject).slice(0, 5).map(task => (
                        <div key={task.id} className="timeline-item">
                          <div className="timeline-date">
                            {task.dueDate ? new Date(task.dueDate).toLocaleDateString() : 'No date'}
                          </div>
                          <div className="timeline-content">
                            <strong>{task.title}</strong>
                            <span className={`timeline-status ${task.status}`}>
                              {task.status || 'todo'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* List View */}
            {boardView === 'list' && (
              <div className="list-view">
                <div className="task-list-table">
                  <div className="table-header">
                    <div className="header-cell">Task</div>
                    <div className="header-cell">Status</div>
                    <div className="header-cell">Priority</div>
                    <div className="header-cell">Assignee</div>
                    <div className="header-cell">Due Date</div>
                    <div className="header-cell">Progress</div>
                  </div>
                  
                  <div className="table-body">
                    {getProjectTasks(selectedProject).map(task => (
                      <div key={task.id} className="table-row">
                        <div className="table-cell task-cell">
                          <div className="task-title-cell">{task.title}</div>
                          {task.description && (
                            <div className="task-desc-cell">{task.description}</div>
                          )}
                        </div>
                        <div className="table-cell">
                          <span className={`status-cell ${task.status || 'todo'}`}>
                            {task.status || 'todo'}
                          </span>
                        </div>
                        <div className="table-cell">
                          <span 
                            className="priority-cell"
                            style={{ color: getPriorityColor(task.priority) }}
                          >
                            {task.priority || 'medium'}
                          </span>
                        </div>
                        <div className="table-cell">
                          {task.assignedAgent || 'Unassigned'}
                        </div>
                        <div className="table-cell">
                          {task.dueDate ? new Date(task.dueDate).toLocaleDateString() : '-'}
                        </div>
                        <div className="table-cell">
                          <div className="progress-cell">
                            <div className="progress-bar-table">
                              <div 
                                className="progress-fill-table"
                                style={{ width: `${task.progress || 0}%` }}
                              />
                            </div>
                            <span>{task.progress || 0}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="no-project-selected">
            <h3>No Project Selected</h3>
            <p>Create a new project or select an existing one to get started.</p>
            <button
              className="create-first-project-btn"
              onClick={() => setShowCreateProject(true)}
            >
              ✨ Create Your First Project
            </button>
          </div>
        )}
      </div>

      {/* Create Project Modal */}
      {showCreateProject && (
        <div className="create-project-modal-overlay">
          <div className="create-project-modal">
            <div className="modal-header">
              <h3>Create New Project</h3>
              <button 
                className="modal-close-btn"
                onClick={() => setShowCreateProject(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Project Name *</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter project name..."
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Project description..."
                  rows="3"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Priority</label>
                  <select
                    value={newProject.priority}
                    onChange={(e) => setNewProject(prev => ({ ...prev, priority: e.target.value }))}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={newProject.status}
                    onChange={(e) => setNewProject(prev => ({ ...prev, status: e.target.value }))}
                  >
                    {projectStatuses.map(status => (
                      <option key={status.id} value={status.id}>
                        {status.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Due Date</label>
                <input
                  type="date"
                  value={newProject.dueDate}
                  onChange={(e) => setNewProject(prev => ({ ...prev, dueDate: e.target.value }))}
                />
              </div>

              <div className="form-group">
                <label>Project Color</label>
                <div className="color-picker">
                  {['#22d3ee', '#10b981', '#fbbf24', '#ef4444', '#8b5cf6', '#f97316'].map(color => (
                    <button
                      key={color}
                      className={`color-option ${newProject.color === color ? 'selected' : ''}`}
                      style={{ backgroundColor: color }}
                      onClick={() => setNewProject(prev => ({ ...prev, color }))}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="cancel-btn"
                onClick={() => setShowCreateProject(false)}
              >
                Cancel
              </button>
              <button
                className="create-btn"
                onClick={handleCreateProject}
                disabled={!newProject.name.trim()}
              >
                Create Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectBoard;