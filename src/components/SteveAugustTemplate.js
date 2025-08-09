/**
 * Steve August ADHD Focus Formula Template Component
 * Licensed proprietary template with validation and integration
 */

import React, { useState, useEffect } from 'react';
import './SteveAugustTemplate.css';

const SteveAugustTemplate = ({ isOpen, onClose, onTaskCreate, userId }) => {
  const [formData, setFormData] = useState({
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
  });

  const [licenseStatus, setLicenseStatus] = useState({
    valid: false,
    type: 'none',
    message: '',
    trialUsesRemaining: 0,
    features: []
  });

  const [licenseKey, setLicenseKey] = useState('');
  const [showLicenseDialog, setShowLicenseDialog] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Check license status on component mount
  useEffect(() => {
    if (isOpen && userId) {
      checkLicenseStatus();
    }
  }, [isOpen, userId]);

  const checkLicenseStatus = async () => {
    try {
      const response = await fetch(`/api/templates/license-info/steve-august-focus-formula`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        }
      });

      if (response.ok) {
        const licenseInfo = await response.json();
        
        // Check user's current license status
        const userLicensesResponse = await fetch(`/api/templates/user-licenses/${userId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        });

        if (userLicensesResponse.ok) {
          const userLicenses = await userLicensesResponse.json();
          const templateStatus = userLicenses.userLicenses['steve-august-focus-formula'];

          if (templateStatus?.trialActive) {
            setLicenseStatus({
              valid: true,
              type: 'trial',
              message: `Trial active: ${templateStatus.trialUsesRemaining} uses remaining`,
              trialUsesRemaining: templateStatus.trialUsesRemaining,
              features: ['limited-template']
            });
          } else if (templateStatus?.trialUsesRemaining === 0) {
            setLicenseStatus({
              valid: false,
              type: 'expired',
              message: 'Trial expired. License required.',
              trialUsesRemaining: 0,
              features: []
            });
            setShowLicenseDialog(true);
          } else {
            setLicenseStatus({
              valid: false,
              type: 'none',
              message: 'License or trial required',
              trialUsesRemaining: licenseInfo.maxTrialUses,
              features: []
            });
            setShowLicenseDialog(true);
          }
        }
      }
    } catch (error) {
      console.error('Failed to check license status:', error);
      setLicenseStatus({
        valid: false,
        type: 'error',
        message: 'Unable to verify license status',
        trialUsesRemaining: 0,
        features: []
      });
    }
  };

  const validateLicense = async (licenseKey) => {
    setIsValidating(true);
    
    try {
      const response = await fetch('/api/templates/validate-license', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          templateId: 'steve-august-focus-formula',
          licenseKey: licenseKey,
          userId: userId
        })
      });

      const result = await response.json();
      
      if (result.valid) {
        setLicenseStatus({
          valid: true,
          type: result.licenseType,
          message: result.message,
          trialUsesRemaining: result.currentUsage ? result.usageLimit - result.currentUsage : 0,
          features: result.features
        });
        setShowLicenseDialog(false);
      } else {
        setLicenseStatus({
          valid: false,
          type: 'invalid',
          message: result.message,
          trialUsesRemaining: 0,
          features: []
        });
      }
    } catch (error) {
      console.error('License validation failed:', error);
      setLicenseStatus({
        valid: false,
        type: 'error',
        message: 'License validation failed',
        trialUsesRemaining: 0,
        features: []
      });
    } finally {
      setIsValidating(false);
    }
  };

  const startTrial = async () => {
    try {
      const response = await fetch('/api/templates/start-trial', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          templateId: 'steve-august-focus-formula',
          userId: userId,
          email: 'user@example.com' // In production, get from user profile
        })
      });

      if (response.ok) {
        const result = await response.json();
        setLicenseStatus({
          valid: true,
          type: 'trial',
          message: `Trial started: ${result.trialUsesRemaining} uses available`,
          trialUsesRemaining: result.trialUsesRemaining,
          features: ['limited-template']
        });
        setShowLicenseDialog(false);
      }
    } catch (error) {
      console.error('Failed to start trial:', error);
    }
  };

  const recordUsage = async () => {
    try {
      await fetch('/api/templates/record-usage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
        },
        body: JSON.stringify({
          templateId: 'steve-august-focus-formula',
          licenseKey: licenseKey,
          userId: userId,
          action: 'create_task'
        })
      });
    } catch (error) {
      console.error('Failed to record usage:', error);
    }
  };

  const handleSubmit = async () => {
    if (!licenseStatus.valid) {
      setShowLicenseDialog(true);
      return;
    }

    setIsLoading(true);

    try {
      // Record usage
      await recordUsage();

      // Create task with Steve August template data
      const taskData = {
        title: `Weekly Focus Formula - Week of ${formData.weekOf}`,
        description: `Steve August ADHD Weekly Focus Formula worksheet`,
        category: 'adhd-coaching',
        priority: 'high',
        estimatedTime: 2,
        assignedAgent: 'alden',
        template: 'steve-august-focus-formula',
        mission: formData.mission,
        values: formData.values.split(',').map(v => v.trim()).filter(v => v),
        steveAugustData: formData,
        memoryTags: ['steve-august', 'focus-formula', 'adhd-coaching', 'weekly-planning'],
        vaultPath: `templates/steve-august/${userId}/${new Date().getTime()}`
      };

      onTaskCreate(taskData);
      onClose();
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateFormData = (path, value) => {
    setFormData(prev => {
      const newData = { ...prev };
      const keys = path.split('.');
      let current = newData;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newData;
    });
  };

  const addArrayItem = (arrayPath, defaultItem) => {
    const current = arrayPath.split('.').reduce((obj, key) => obj[key], formData);
    updateFormData(arrayPath, [...current, defaultItem]);
  };

  const removeArrayItem = (arrayPath, index) => {
    const current = arrayPath.split('.').reduce((obj, key) => obj[key], formData);
    updateFormData(arrayPath, current.filter((_, i) => i !== index));
  };

  if (!isOpen) return null;

  return (
    <div className="steve-august-modal-overlay">
      <div className="steve-august-modal">
        <div className="modal-header">
          <h2>🧠 Steve August Weekly Focus Formula</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        {/* License Dialog */}
        {showLicenseDialog && (
          <div className="license-dialog">
            <div className="license-content">
              <h3>🔐 License Required</h3>
              <p>This is a proprietary template by Steve August, ADHD coach.</p>
              
              <div className="license-options">
                <div className="license-option">
                  <h4>Enter License Key</h4>
                  <input
                    type="text"
                    placeholder="SA-2025-XXXX-XXXX-XXXX"
                    value={licenseKey}
                    onChange={(e) => setLicenseKey(e.target.value)}
                    className="license-input"
                  />
                  <button
                    onClick={() => validateLicense(licenseKey)}
                    disabled={isValidating || !licenseKey}
                    className="validate-btn"
                  >
                    {isValidating ? '🔄 Validating...' : '✅ Validate License'}
                  </button>
                </div>

                {licenseStatus.trialUsesRemaining > 0 && (
                  <div className="license-option">
                    <h4>Start Free Trial</h4>
                    <p>Try the template with {licenseStatus.trialUsesRemaining} free uses</p>
                    <button onClick={startTrial} className="trial-btn">
                      🆓 Start Trial
                    </button>
                  </div>
                )}

                <div className="license-option">
                  <h4>Purchase License</h4>
                  <p>Get unlimited access to this professional ADHD coaching tool</p>
                  <a
                    href="https://steve-august.com/focus-formula"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="purchase-btn"
                  >
                    🛒 Purchase License
                  </a>
                </div>
              </div>

              {licenseStatus.message && (
                <div className={`license-message ${licenseStatus.valid ? 'success' : 'error'}`}>
                  {licenseStatus.message}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Main Form */}
        {licenseStatus.valid && (
          <div className="steve-august-form">
            <div className="form-progress">
              <div className="progress-steps">
                {[1, 2, 3, 4].map(step => (
                  <div key={step} className={`step ${currentStep >= step ? 'active' : ''}`}>
                    {step}
                  </div>
                ))}
              </div>
            </div>

            {currentStep === 1 && (
              <div className="form-step">
                <h3>📅 Week Planning</h3>
                
                <div className="form-group">
                  <label>Week of:</label>
                  <input
                    type="date"
                    value={formData.weekOf}
                    onChange={(e) => updateFormData('weekOf', e.target.value)}
                    className="date-input"
                  />
                </div>

                <div className="form-group">
                  <label>2HR Workday Priorities:</label>
                  {formData.twoHourWorkdayPriorities.map((priority, index) => (
                    <div key={index} className="array-item">
                      <input
                        type="text"
                        value={priority}
                        onChange={(e) => {
                          const newPriorities = [...formData.twoHourWorkdayPriorities];
                          newPriorities[index] = e.target.value;
                          updateFormData('twoHourWorkdayPriorities', newPriorities);
                        }}
                        placeholder="What can you accomplish in 2 focused hours?"
                        className="text-input"
                      />
                      {formData.twoHourWorkdayPriorities.length > 1 && (
                        <button
                          onClick={() => removeArrayItem('twoHourWorkdayPriorities', index)}
                          className="remove-btn"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayItem('twoHourWorkdayPriorities', '')}
                    className="add-btn"
                  >
                    ➕ Add Priority
                  </button>
                </div>
              </div>
            )}

            {currentStep === 2 && (
              <div className="form-step">
                <h3>🧠 Brain Dump & Vision</h3>
                
                <div className="form-group">
                  <label>Magnetic North:</label>
                  <textarea
                    value={formData.magneticNorth}
                    onChange={(e) => updateFormData('magneticNorth', e.target.value)}
                    placeholder="Your guiding principle for this week..."
                    className="textarea-input"
                  />
                </div>

                <div className="form-group">
                  <label>Mission:</label>
                  <textarea
                    value={formData.mission}
                    onChange={(e) => updateFormData('mission', e.target.value)}
                    placeholder="What are you working toward this week?"
                    className="textarea-input"
                  />
                </div>

                <div className="form-group">
                  <label>Vision:</label>
                  <textarea
                    value={formData.vision}
                    onChange={(e) => updateFormData('vision', e.target.value)}
                    placeholder="What does success look like?"
                    className="textarea-input"
                  />
                </div>

                <div className="form-group">
                  <label>Values:</label>
                  <input
                    type="text"
                    value={formData.values}
                    onChange={(e) => updateFormData('values', e.target.value)}
                    placeholder="Core values guiding your decisions (comma-separated)"
                    className="text-input"
                  />
                </div>
              </div>
            )}

            {currentStep === 3 && (
              <div className="form-step">
                <h3>💪 Self-Care & Daily Priorities</h3>
                
                <div className="form-group">
                  <label>Self-Care Habit:</label>
                  <input
                    type="text"
                    value={formData.selfCareHabitTracker.habitName}
                    onChange={(e) => updateFormData('selfCareHabitTracker.habitName', e.target.value)}
                    placeholder="e.g., Morning meditation, Evening walk"
                    className="text-input"
                  />
                </div>

                <div className="form-group">
                  <label>Weekly Habit Tracking:</label>
                  <div className="habit-tracker">
                    {Object.entries(formData.selfCareHabitTracker.weekly).map(([day, checked]) => (
                      <label key={day} className="habit-day">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={(e) => updateFormData(`selfCareHabitTracker.weekly.${day}`, e.target.checked)}
                        />
                        {day}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="form-group">
                  <label>Daily 2HR Priorities:</label>
                  {Object.entries(formData.daily2HRPriorities).map(([day, priority]) => (
                    <div key={day} className="daily-priority">
                      <label>{day}:</label>
                      <input
                        type="text"
                        value={priority}
                        onChange={(e) => updateFormData(`daily2HRPriorities.${day}`, e.target.value)}
                        placeholder={`Your 2-hour focus for ${day}`}
                        className="text-input"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {currentStep === 4 && (
              <div className="form-step">
                <h3>🎯 Decisions & Brain Dump</h3>
                
                <div className="form-group">
                  <label>Key Decisions:</label>
                  {formData.decisions.map((decision, index) => (
                    <div key={index} className="decision-item">
                      <input
                        type="text"
                        value={decision.decision}
                        onChange={(e) => {
                          const newDecisions = [...formData.decisions];
                          newDecisions[index].decision = e.target.value;
                          updateFormData('decisions', newDecisions);
                        }}
                        placeholder="What decision do you need to make?"
                        className="text-input"
                      />
                      <input
                        type="date"
                        value={decision.deadline}
                        onChange={(e) => {
                          const newDecisions = [...formData.decisions];
                          newDecisions[index].deadline = e.target.value;
                          updateFormData('decisions', newDecisions);
                        }}
                        className="date-input"
                      />
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayItem('decisions', { decision: '', deadline: '', options: [''], criteria: '' })}
                    className="add-btn"
                  >
                    ➕ Add Decision
                  </button>
                </div>

                <div className="form-group">
                  <label>Brain Dump Options:</label>
                  {formData.brainDumpOptions.map((option, index) => (
                    <div key={index} className="brain-dump-item">
                      <input
                        type="text"
                        value={option.goal}
                        onChange={(e) => {
                          const newOptions = [...formData.brainDumpOptions];
                          newOptions[index].goal = e.target.value;
                          updateFormData('brainDumpOptions', newOptions);
                        }}
                        placeholder="Goal"
                        className="text-input"
                      />
                      <input
                        type="text"
                        value={option.rock}
                        onChange={(e) => {
                          const newOptions = [...formData.brainDumpOptions];
                          newOptions[index].rock = e.target.value;
                          updateFormData('brainDumpOptions', newOptions);
                        }}
                        placeholder="Obstacle/Rock"
                        className="text-input"
                      />
                      <input
                        type="text"
                        value={option.smallestNextStep}
                        onChange={(e) => {
                          const newOptions = [...formData.brainDumpOptions];
                          newOptions[index].smallestNextStep = e.target.value;
                          updateFormData('brainDumpOptions', newOptions);
                        }}
                        placeholder="Smallest next step"
                        className="text-input"
                      />
                      {formData.brainDumpOptions.length > 1 && (
                        <button
                          onClick={() => removeArrayItem('brainDumpOptions', index)}
                          className="remove-btn"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayItem('brainDumpOptions', { goal: '', rock: '', smallestNextStep: '' })}
                    className="add-btn"
                  >
                    ➕ Add Brain Dump Option
                  </button>
                </div>
              </div>
            )}

            <div className="form-navigation">
              {currentStep > 1 && (
                <button
                  onClick={() => setCurrentStep(prev => prev - 1)}
                  className="nav-btn prev-btn"
                >
                  ← Previous
                </button>
              )}
              
              {currentStep < 4 ? (
                <button
                  onClick={() => setCurrentStep(prev => prev + 1)}
                  className="nav-btn next-btn"
                >
                  Next →
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={isLoading}
                  className="nav-btn submit-btn"
                >
                  {isLoading ? '🔄 Creating...' : '✅ Create Weekly Plan'}
                </button>
              )}
            </div>
          </div>
        )}

        <div className="template-credit">
          <p>© 2025 <a href="https://steve-august.com" target="_blank" rel="noopener noreferrer">Steve August – ADHD Coaching</a></p>
          {licenseStatus.type === 'trial' && (
            <p className="trial-notice">Trial: {licenseStatus.trialUsesRemaining} uses remaining</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SteveAugustTemplate;