/**
 * SPEC-2 Task Editor Component
 * Multi-step form for creating/editing tasks with August Weekly Focus Formula schema
 */

import React, { useState, useEffect, useCallback } from 'react';
import { X, ChevronLeft, ChevronRight, Save, AlertCircle, CheckCircle, Calendar, Target, Zap as Brain, Lightbulb } from 'lucide-react';
import './TaskEditor.css';

// TypeScript interfaces based on JSON schema
interface WeeklySchedule {
  Mon: boolean;
  Tue: boolean;
  Wed: boolean;
  Thu: boolean;
  Fri: boolean;
  Sat: boolean;
  Sun: boolean;
}

interface BrainDumpOption {
  goal: string;
  rock: string;
  smallestNextStep: string;
}

interface Decision {
  decision: string;
  deadline: string;
  options: string[];
  criteria: string;
}

interface WeeklyReflection {
  wins: string[];
  challenges: string[];
  lessons: string;
  nextWeekFocus: string;
}

interface SteveAugustData {
  weekOf: string;
  twoHourWorkdayPriorities: string[];
  brainDumpOptions: BrainDumpOption[];
  magneticNorth: string;
  mission: string;
  vision: string;
  values: string;
  selfCareHabitTracker: {
    habitName: string;
    targetFrequency: string;
    weekly: WeeklySchedule;
    notes: string;
  };
  daily2HRPriorities: {
    Monday: string;
    Tuesday: string;
    Wednesday: string;
    Thursday: string;
    Friday: string;
  };
  decisions: Decision[];
  weeklyReflection: WeeklyReflection;
}

interface Task {
  id?: string;
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
  steveAugustData?: SteveAugustData;
}

interface TaskTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  mission: string;
  values: string[];
  priority: string;
  estimatedTime: number;
  assignedAgent: string;
  tags: string[];
}

interface ValidationError {
  field: string;
  message: string;
}

interface TaskEditorProps {
  task?: Task | null;
  template?: TaskTemplate | null;
  onSave: (taskId: string, taskData: Partial<Task>) => Promise<void>;
  onClose: () => void;
  userId: string;
  focusFormulaLicenseToken?: string;
}

const TaskEditor: React.FC<TaskEditorProps> = ({
  task,
  template,
  onSave,
  onClose,
  userId,
  focusFormulaLicenseToken
}) => {
  // Form state
  const [formData, setFormData] = useState<Task>({
    title: '',
    description: '',
    priority: 'medium',
    estimatedTime: 1,
    dueDate: null,
    tags: [],
    assignedAgent: 'alden',
    category: 'general',
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

  // UI state
  const [currentStep, setCurrentStep] = useState(1);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Initialize form data
  useEffect(() => {
    if (task) {
      // Editing existing task
      setFormData(task);
    } else if (template) {
      // Creating from template
      setFormData(prev => ({
        ...prev,
        title: template.id === 'steve-august-focus-formula' 
          ? `Weekly Focus Formula - Week of ${new Date().toISOString().split('T')[0]}`
          : `New ${template.name}`,
        description: template.description,
        category: template.category,
        mission: template.mission,
        values: template.values,
        priority: template.priority,
        estimatedTime: template.estimatedTime,
        assignedAgent: template.assignedAgent,
        tags: [...template.tags],
        template: template.id,
        memoryTags: [`template:${template.id}`],
        // Initialize Steve August specific data
        steveAugustData: template.id === 'steve-august-focus-formula' ? {
          weekOf: '',
          twoHourWorkdayPriorities: [''],
          brainDumpOptions: [{ goal: '', rock: '', smallestNextStep: '' }],
          magneticNorth: '',
          mission: '',
          vision: '',
          values: '',
          selfCareHabitTracker: {
            habitName: '',
            targetFrequency: 'daily',
            weekly: {
              Mon: false, Tue: false, Wed: false, Thu: false,
              Fri: false, Sat: false, Sun: false
            },
            notes: ''
          },
          daily2HRPriorities: {
            Monday: '', Tuesday: '', Wednesday: '', Thursday: '', Friday: ''
          },
          decisions: [{ decision: '', deadline: '', options: [''], criteria: '' }],
          weeklyReflection: {
            wins: [''], challenges: [''], lessons: '', nextWeekFocus: ''
          }
        } : undefined
      }));
    }
  }, [task, template]);

  // Validation
  const validateCurrentStep = useCallback((): ValidationError[] => {
    const stepErrors: ValidationError[] = [];

    if (currentStep === 1) {
      if (!formData.title.trim()) {
        stepErrors.push({ field: 'title', message: 'Title is required' });
      }
      if (!formData.description.trim()) {
        stepErrors.push({ field: 'description', message: 'Description is required' });
      }
      
      // Steve August specific validation
      if (template?.id === 'steve-august-focus-formula' && formData.steveAugustData) {
        if (!formData.steveAugustData.weekOf) {
          stepErrors.push({ field: 'weekOf', message: 'Week date is required' });
        }
      }
    }

    if (currentStep === 2) {
      if (!formData.category) {
        stepErrors.push({ field: 'category', message: 'Category is required' });
      }
      if (!formData.priority) {
        stepErrors.push({ field: 'priority', message: 'Priority is required' });
      }
    }

    if (currentStep === 3 && template?.id === 'steve-august-focus-formula') {
      const augustData = formData.steveAugustData;
      if (augustData) {
        if (!augustData.magneticNorth.trim()) {
          stepErrors.push({ field: 'magneticNorth', message: 'Magnetic North is required' });
        }
        if (augustData.brainDumpOptions.some(option => !option.goal.trim() || !option.smallestNextStep.trim())) {
          stepErrors.push({ field: 'brainDumpOptions', message: 'All brain dump options must have a goal and next step' });
        }
      }
    }

    return stepErrors;
  }, [currentStep, formData, template]);

  // Update form data
  const updateFormData = (path: string, value: any) => {
    setFormData(prev => {
      const newData = { ...prev };
      const keys = path.split('.');
      let current: any = newData;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newData;
    });
  };

  // Array manipulation helpers
  const addArrayItem = (path: string, defaultItem: any) => {
    const current = path.split('.').reduce((obj: any, key) => obj[key], formData);
    updateFormData(path, [...current, defaultItem]);
  };

  const removeArrayItem = (path: string, index: number) => {
    const current = path.split('.').reduce((obj: any, key) => obj[key], formData);
    updateFormData(path, current.filter((_: any, i: number) => i !== index));
  };

  // Navigation
  const goToNextStep = () => {
    const stepErrors = validateCurrentStep();
    setErrors(stepErrors);
    
    if (stepErrors.length === 0) {
      setCurrentStep(prev => Math.min(prev + 1, getMaxSteps()));
    }
  };

  const goToPreviousStep = () => {
    setErrors([]);
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const getMaxSteps = () => {
    return template?.id === 'steve-august-focus-formula' ? 4 : 3;
  };

  // Save task
  const handleSave = async () => {
    const allErrors = validateCurrentStep();
    setErrors(allErrors);
    
    if (allErrors.length > 0) return;

    setSaving(true);
    setSaveSuccess(false);

    try {
      const taskData: Partial<Task> = {
        ...formData,
        memoryTags: [
          ...formData.memoryTags,
          `user:${userId}`,
          `category:${formData.category}`,
          `agent:${formData.assignedAgent}`
        ],
        vaultPath: formData.vaultPath || `tasks/${formData.assignedAgent}/${Date.now()}`
      };

      await onSave(task?.id || '', taskData);
      
      setSaveSuccess(true);
      setTimeout(() => onClose(), 1500);
      
    } catch (err) {
      console.error('Failed to save task:', err);
      setErrors([{ field: 'general', message: 'Failed to save task. Please try again.' }]);
    } finally {
      setSaving(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return renderBasicInfoStep();
      case 2:
        return renderCategoryStep();
      case 3:
        return template?.id === 'steve-august-focus-formula' 
          ? renderSteveAugustStep1() 
          : renderAdvancedStep();
      case 4:
        return renderSteveAugustStep2();
      default:
        return null;
    }
  };

  const renderBasicInfoStep = () => (
    <div className="form-step">
      <div className="step-header">
        <Calendar className="w-6 h-6" />
        <h3>Basic Information</h3>
      </div>

      <div className="form-group">
        <label htmlFor="title">Task Title *</label>
        <input
          id="title"
          type="text"
          value={formData.title}
          onChange={(e) => updateFormData('title', e.target.value)}
          placeholder="Enter a clear, specific task title..."
          className={`form-input ${errors.find(e => e.field === 'title') ? 'error' : ''}`}
        />
        {errors.find(e => e.field === 'title') && (
          <div className="error-message">
            <AlertCircle className="w-4 h-4" />
            {errors.find(e => e.field === 'title')?.message}
          </div>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="description">Description *</label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => updateFormData('description', e.target.value)}
          placeholder="Describe what needs to be done..."
          className={`form-textarea ${errors.find(e => e.field === 'description') ? 'error' : ''}`}
          rows={4}
        />
        {errors.find(e => e.field === 'description') && (
          <div className="error-message">
            <AlertCircle className="w-4 h-4" />
            {errors.find(e => e.field === 'description')?.message}
          </div>
        )}
      </div>

      {template?.id === 'steve-august-focus-formula' && (
        <div className="form-group">
          <label htmlFor="weekOf">Week of *</label>
          <input
            id="weekOf"
            type="date"
            value={formData.steveAugustData?.weekOf || ''}
            onChange={(e) => updateFormData('steveAugustData.weekOf', e.target.value)}
            className={`form-input ${errors.find(e => e.field === 'weekOf') ? 'error' : ''}`}
          />
          {errors.find(e => e.field === 'weekOf') && (
            <div className="error-message">
              <AlertCircle className="w-4 h-4" />
              {errors.find(e => e.field === 'weekOf')?.message}
            </div>
          )}
        </div>
      )}

      <div className="form-group">
        <label htmlFor="mission">Mission Statement</label>
        <textarea
          id="mission"
          value={formData.mission}
          onChange={(e) => updateFormData('mission', e.target.value)}
          placeholder="Define the broader mission this task serves..."
          className="form-textarea"
          rows={2}
        />
      </div>
    </div>
  );

  const renderCategoryStep = () => (
    <div className="form-step">
      <div className="step-header">
        <Target className="w-6 h-6" />
        <h3>Categorization & Priority</h3>
      </div>

      <div className="form-group">
        <label htmlFor="category">Category *</label>
        <select
          id="category"
          value={formData.category}
          onChange={(e) => updateFormData('category', e.target.value)}
          className={`form-select ${errors.find(e => e.field === 'category') ? 'error' : ''}`}
        >
          <option value="general">General</option>
          <option value="development">Development</option>
          <option value="design">Design</option>
          <option value="research">Research</option>
          <option value="productivity">Productivity</option>
          <option value="adhd-coaching">ADHD Coaching</option>
        </select>
        {errors.find(e => e.field === 'category') && (
          <div className="error-message">
            <AlertCircle className="w-4 h-4" />
            {errors.find(e => e.field === 'category')?.message}
          </div>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="priority">Priority Level *</label>
        <div className="priority-options">
          {['high', 'medium', 'low'].map(priority => (
            <button
              key={priority}
              type="button"
              className={`priority-btn ${priority} ${formData.priority === priority ? 'selected' : ''}`}
              onClick={() => updateFormData('priority', priority)}
            >
              <div className="priority-indicator"></div>
              <span>{priority.toUpperCase()}</span>
            </button>
          ))}
        </div>
        {errors.find(e => e.field === 'priority') && (
          <div className="error-message">
            <AlertCircle className="w-4 h-4" />
            {errors.find(e => e.field === 'priority')?.message}
          </div>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="estimatedTime">Estimated Time (hours)</label>
        <input
          id="estimatedTime"
          type="number"
          min="0.5"
          max="40"
          step="0.5"
          value={formData.estimatedTime}
          onChange={(e) => updateFormData('estimatedTime', parseFloat(e.target.value) || 1)}
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="assignedAgent">Assigned Agent</label>
        <select
          id="assignedAgent"
          value={formData.assignedAgent}
          onChange={(e) => updateFormData('assignedAgent', e.target.value)}
          className="form-select"
        >
          <option value="alden">Alden</option>
          <option value="alice">Alice</option>
          <option value="mimic">Mimic</option>
          <option value="sentry">Sentry</option>
        </select>
      </div>
    </div>
  );

  const renderSteveAugustStep1 = () => (
    <div className="form-step">
      <div className="step-header">
        <Brain className="w-6 h-6" />
        <h3>Focus & Vision</h3>
      </div>

      <div className="form-group">
        <label htmlFor="magneticNorth">Magnetic North *</label>
        <textarea
          id="magneticNorth"
          value={formData.steveAugustData?.magneticNorth || ''}
          onChange={(e) => updateFormData('steveAugustData.magneticNorth', e.target.value)}
          placeholder="Your guiding principle for this week..."
          className={`form-textarea ${errors.find(e => e.field === 'magneticNorth') ? 'error' : ''}`}
          rows={2}
        />
        {errors.find(e => e.field === 'magneticNorth') && (
          <div className="error-message">
            <AlertCircle className="w-4 h-4" />
            {errors.find(e => e.field === 'magneticNorth')?.message}
          </div>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="steveVision">Vision</label>
        <textarea
          id="steveVision"
          value={formData.steveAugustData?.vision || ''}
          onChange={(e) => updateFormData('steveAugustData.vision', e.target.value)}
          placeholder="What does success look like this week?"
          className="form-textarea"
          rows={2}
        />
      </div>

      <div className="form-group">
        <label htmlFor="steveValues">Values</label>
        <input
          id="steveValues"
          type="text"
          value={formData.steveAugustData?.values || ''}
          onChange={(e) => updateFormData('steveAugustData.values', e.target.value)}
          placeholder="Core values guiding your decisions this week"
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label>2HR Workday Priorities</label>
        {formData.steveAugustData?.twoHourWorkdayPriorities.map((priority, index) => (
          <div key={index} className="array-item">
            <input
              type="text"
              value={priority}
              onChange={(e) => {
                const newPriorities = [...(formData.steveAugustData?.twoHourWorkdayPriorities || [])];
                newPriorities[index] = e.target.value;
                updateFormData('steveAugustData.twoHourWorkdayPriorities', newPriorities);
              }}
              placeholder="What can you accomplish in 2 focused hours?"
              className="form-input"
            />
            {(formData.steveAugustData?.twoHourWorkdayPriorities.length || 0) > 1 && (
              <button
                type="button"
                onClick={() => removeArrayItem('steveAugustData.twoHourWorkdayPriorities', index)}
                className="remove-btn"
              >
                ×
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={() => addArrayItem('steveAugustData.twoHourWorkdayPriorities', '')}
          className="add-btn"
        >
          + Add Priority
        </button>
      </div>

      <div className="form-group">
        <label>Brain Dump Options</label>
        {formData.steveAugustData?.brainDumpOptions.map((option, index) => (
          <div key={index} className="brain-dump-item">
            <input
              type="text"
              value={option.goal}
              onChange={(e) => {
                const newOptions = [...(formData.steveAugustData?.brainDumpOptions || [])];
                newOptions[index].goal = e.target.value;
                updateFormData('steveAugustData.brainDumpOptions', newOptions);
              }}
              placeholder="Goal"
              className="form-input"
            />
            <input
              type="text"
              value={option.rock}
              onChange={(e) => {
                const newOptions = [...(formData.steveAugustData?.brainDumpOptions || [])];
                newOptions[index].rock = e.target.value;
                updateFormData('steveAugustData.brainDumpOptions', newOptions);
              }}
              placeholder="Obstacle/Rock"
              className="form-input"
            />
            <input
              type="text"
              value={option.smallestNextStep}
              onChange={(e) => {
                const newOptions = [...(formData.steveAugustData?.brainDumpOptions || [])];
                newOptions[index].smallestNextStep = e.target.value;
                updateFormData('steveAugustData.brainDumpOptions', newOptions);
              }}
              placeholder="Smallest next step *"
              className="form-input"
            />
            {(formData.steveAugustData?.brainDumpOptions.length || 0) > 1 && (
              <button
                type="button"
                onClick={() => removeArrayItem('steveAugustData.brainDumpOptions', index)}
                className="remove-btn"
              >
                ×
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={() => addArrayItem('steveAugustData.brainDumpOptions', { goal: '', rock: '', smallestNextStep: '' })}
          className="add-btn"
        >
          + Add Brain Dump Option
        </button>
        {errors.find(e => e.field === 'brainDumpOptions') && (
          <div className="error-message">
            <AlertCircle className="w-4 h-4" />
            {errors.find(e => e.field === 'brainDumpOptions')?.message}
          </div>
        )}
      </div>
    </div>
  );

  const renderSteveAugustStep2 = () => (
    <div className="form-step">
      <div className="step-header">
        <Lightbulb className="w-6 h-6" />
        <h3>Habits & Decisions</h3>
      </div>

      <div className="form-group">
        <label htmlFor="habitName">Self-Care Habit</label>
        <input
          id="habitName"
          type="text"
          value={formData.steveAugustData?.selfCareHabitTracker.habitName || ''}
          onChange={(e) => updateFormData('steveAugustData.selfCareHabitTracker.habitName', e.target.value)}
          placeholder="e.g., Morning meditation, Evening walk"
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label>Weekly Habit Tracking</label>
        <div className="habit-tracker">
          {Object.entries(formData.steveAugustData?.selfCareHabitTracker.weekly || {}).map(([day, checked]) => (
            <label key={day} className="habit-day">
              <input
                type="checkbox"
                checked={checked}
                onChange={(e) => updateFormData(`steveAugustData.selfCareHabitTracker.weekly.${day}`, e.target.checked)}
              />
              {day}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Daily 2HR Priorities</label>
        {Object.entries(formData.steveAugustData?.daily2HRPriorities || {}).map(([day, priority]) => (
          <div key={day} className="daily-priority">
            <label>{day}:</label>
            <input
              type="text"
              value={priority}
              onChange={(e) => updateFormData(`steveAugustData.daily2HRPriorities.${day}`, e.target.value)}
              placeholder={`Your 2-hour focus for ${day}`}
              className="form-input"
            />
          </div>
        ))}
      </div>

      <div className="form-group">
        <label>Key Decisions</label>
        {formData.steveAugustData?.decisions.map((decision, index) => (
          <div key={index} className="decision-item">
            <input
              type="text"
              value={decision.decision}
              onChange={(e) => {
                const newDecisions = [...(formData.steveAugustData?.decisions || [])];
                newDecisions[index].decision = e.target.value;
                updateFormData('steveAugustData.decisions', newDecisions);
              }}
              placeholder="What decision do you need to make?"
              className="form-input"
            />
            <input
              type="date"
              value={decision.deadline}
              onChange={(e) => {
                const newDecisions = [...(formData.steveAugustData?.decisions || [])];
                newDecisions[index].deadline = e.target.value;
                updateFormData('steveAugustData.decisions', newDecisions);
              }}
              className="form-input"
            />
            <input
              type="text"
              value={decision.criteria}
              onChange={(e) => {
                const newDecisions = [...(formData.steveAugustData?.decisions || [])];
                newDecisions[index].criteria = e.target.value;
                updateFormData('steveAugustData.decisions', newDecisions);
              }}
              placeholder="Decision criteria"
              className="form-input"
            />
            {(formData.steveAugustData?.decisions.length || 0) > 1 && (
              <button
                type="button"
                onClick={() => removeArrayItem('steveAugustData.decisions', index)}
                className="remove-btn"
              >
                ×
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={() => addArrayItem('steveAugustData.decisions', { decision: '', deadline: '', options: [''], criteria: '' })}
          className="add-btn"
        >
          + Add Decision
        </button>
      </div>
    </div>
  );

  const renderAdvancedStep = () => (
    <div className="form-step">
      <div className="step-header">
        <Target className="w-6 h-6" />
        <h3>Advanced Options</h3>
      </div>

      <div className="form-group">
        <label htmlFor="tags">Tags</label>
        <input
          id="tags"
          type="text"
          value={formData.tags.join(', ')}
          onChange={(e) => updateFormData('tags', e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag))}
          placeholder="Enter tags separated by commas"
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="dueDate">Due Date</label>
        <input
          id="dueDate"
          type="datetime-local"
          value={formData.dueDate || ''}
          onChange={(e) => updateFormData('dueDate', e.target.value || null)}
          className="form-input"
        />
      </div>
    </div>
  );

  return (
    <div className="task-editor-overlay">
      <div className="task-editor-modal">
        <div className="editor-header">
          <h2>
            {task ? 'Edit Task' : template ? `Create from ${template.name}` : 'Create New Task'}
          </h2>
          <button onClick={onClose} className="close-btn">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress indicator */}
        <div className="step-progress">
          {Array.from({ length: getMaxSteps() }, (_, i) => i + 1).map(step => (
            <div key={step} className={`step-indicator ${currentStep >= step ? 'active' : ''}`}>
              {step}
            </div>
          ))}
        </div>

        {/* Form content */}
        <div className="editor-content">
          {renderStepContent()}
        </div>

        {/* Error display */}
        {errors.length > 0 && (
          <div className="error-summary">
            <AlertCircle className="w-5 h-5" />
            <div>
              <p>Please fix the following errors:</p>
              <ul>
                {errors.map((error, index) => (
                  <li key={index}>{error.message}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Success message */}
        {saveSuccess && (
          <div className="success-message">
            <CheckCircle className="w-5 h-5" />
            <span>Task saved successfully!</span>
          </div>
        )}

        {/* Navigation */}
        <div className="editor-footer">
          <div className="footer-actions">
            {currentStep > 1 && (
              <button
                onClick={goToPreviousStep}
                className="nav-btn secondary"
                disabled={saving}
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>
            )}
            
            {currentStep < getMaxSteps() ? (
              <button
                onClick={goToNextStep}
                className="nav-btn primary"
                disabled={saving}
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSave}
                className="nav-btn primary"
                disabled={saving || errors.length > 0}
              >
                {saving ? (
                  <>
                    <div className="loading-spinner"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save Task
                  </>
                )}
              </button>
            )}
          </div>

          {/* Steve August credit */}
          {template?.id === 'steve-august-focus-formula' && (
            <div className="template-credit">
              <p>
                © 2025{' '}
                <a 
                  href="https://steve-august.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="credit-link"
                >
                  Steve August – ADHD Coaching
                </a>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TaskEditor;