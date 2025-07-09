import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ accessibilitySettings, onVoiceCommand }) => {
  const [tasks, setTasks] = useState([]);
  const [goals, setGoals] = useState([]);
  const [stats, setStats] = useState({
    completed: 0,
    pending: 0,
    overdue: 0,
    productivity: 85
  });

  useEffect(() => {
    // Load sample data
    loadSampleData();
  }, []);

  const loadSampleData = () => {
    setTasks([
      { id: 1, title: 'Complete project proposal', status: 'pending', priority: 'high', dueDate: '2025-01-15' },
      { id: 2, title: 'Review code changes', status: 'completed', priority: 'medium', dueDate: '2025-01-10' },
      { id: 3, title: 'Schedule team meeting', status: 'pending', priority: 'low', dueDate: '2025-01-12' },
      { id: 4, title: 'Update documentation', status: 'overdue', priority: 'high', dueDate: '2025-01-08' }
    ]);

    setGoals([
      { id: 1, title: 'Improve productivity by 20%', progress: 75, target: 100 },
      { id: 2, title: 'Complete certification course', progress: 45, target: 100 },
      { id: 3, title: 'Learn new programming language', progress: 30, target: 100 }
    ]);
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ff3b30';
      case 'medium': return '#ff9500';
      case 'low': return '#34c759';
      default: return '#8e8e93';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#34c759';
      case 'pending': return '#007aff';
      case 'overdue': return '#ff3b30';
      default: return '#8e8e93';
    }
  };

  const handleTaskToggle = (taskId) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId 
        ? { ...task, status: task.status === 'completed' ? 'pending' : 'completed' }
        : task
    ));
  };

  const addTask = (title, priority = 'medium') => {
    const newTask = {
      id: Date.now(),
      title,
      status: 'pending',
      priority,
      dueDate: new Date().toISOString().split('T')[0]
    };
    setTasks(prev => [...prev, newTask]);
  };

  const handleVoiceCommand = (command) => {
    const lowerCommand = command.toLowerCase();
    
    if (lowerCommand.includes('add task')) {
      const taskTitle = command.replace(/add task/i, '').trim();
      if (taskTitle) {
        addTask(taskTitle);
        if (window.accessibility && accessibilitySettings.voiceFeedback) {
          window.accessibility.speak(`Added task: ${taskTitle}`);
        }
      }
    } else if (lowerCommand.includes('complete task')) {
      const taskTitle = command.replace(/complete task/i, '').trim();
      const task = tasks.find(t => t.title.toLowerCase().includes(taskTitle.toLowerCase()));
      if (task) {
        handleTaskToggle(task.id);
        if (window.accessibility && accessibilitySettings.voiceFeedback) {
          window.accessibility.speak(`Completed task: ${task.title}`);
        }
      }
    }
    
    onVoiceCommand(command);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Productivity Dashboard</h2>
        <div className="dashboard-stats">
          <div className="stat-item">
            <span className="stat-number">{stats.completed}</span>
            <span className="stat-label">Completed</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.pending}</span>
            <span className="stat-label">Pending</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.overdue}</span>
            <span className="stat-label">Overdue</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.productivity}%</span>
            <span className="stat-label">Productivity</span>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-section">
          <h3>📋 Tasks</h3>
          <div className="task-list">
            {tasks.map(task => (
              <div key={task.id} className={`task-item ${task.status}`}>
                <input
                  type="checkbox"
                  checked={task.status === 'completed'}
                  onChange={() => handleTaskToggle(task.id)}
                  aria-label={`Mark task as ${task.status === 'completed' ? 'pending' : 'completed'}`}
                />
                <div className="task-content">
                  <span className="task-title">{task.title}</span>
                  <div className="task-meta">
                    <span 
                      className="task-priority"
                      style={{ backgroundColor: getPriorityColor(task.priority) }}
                    >
                      {task.priority}
                    </span>
                    <span 
                      className="task-status"
                      style={{ backgroundColor: getStatusColor(task.status) }}
                    >
                      {task.status}
                    </span>
                    <span className="task-date">{task.dueDate}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button 
            onClick={() => addTask('New task')}
            className="add-task-btn"
            aria-label="Add new task"
          >
            + Add Task
          </button>
        </div>

        <div className="dashboard-section">
          <h3>🎯 Goals</h3>
          <div className="goal-list">
            {goals.map(goal => (
              <div key={goal.id} className="goal-item">
                <div className="goal-header">
                  <span className="goal-title">{goal.title}</span>
                  <span className="goal-progress">{goal.progress}%</span>
                </div>
                <div className="goal-bar">
                  <div 
                    className="goal-progress-bar"
                    style={{ width: `${(goal.progress / goal.target) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-section">
          <h3>📊 Quick Actions</h3>
          <div className="quick-actions">
            <button 
              onClick={() => handleVoiceCommand('add task')}
              className="action-btn"
              aria-label="Add task via voice"
            >
              🎤 Voice Add Task
            </button>
            <button 
              onClick={() => window.electronAPI?.openExternal('https://calendar.google.com')}
              className="action-btn"
              aria-label="Open calendar"
            >
              📅 Open Calendar
            </button>
            <button 
              onClick={() => window.electronAPI?.openExternal('https://todoist.com')}
              className="action-btn"
              aria-label="Open todoist"
            >
              ✅ Open Todoist
            </button>
            <button 
              onClick={() => window.electronAPI?.openExternal('https://notion.so')}
              className="action-btn"
              aria-label="Open notion"
            >
              📝 Open Notion
            </button>
          </div>
        </div>
      </div>

      <div className="dashboard-footer">
        <p>
          Use voice commands like "Add task [task name]" or "Complete task [task name]" 
          to manage your tasks hands-free.
        </p>
      </div>
    </div>
  );
};

export default Dashboard; 