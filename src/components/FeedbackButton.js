import React, { useState, useRef } from 'react';
import { X, Bug, MessageSquare, Upload, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import './FeedbackButton.css';

const FeedbackButton = ({ onSubmit, className = '' }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'bug',
    attachments: []
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);
  const [errors, setErrors] = useState({});
  const fileInputRef = useRef(null);

  const categories = [
    { value: 'bug', label: '🐛 Bug Report', description: 'Something is broken or not working' },
    { value: 'feature', label: '✨ Feature Request', description: 'Suggest a new feature or improvement' },
    { value: 'UI', label: '🎨 UI/UX Issue', description: 'Interface or usability problem' },
    { value: 'performance', label: '⚡ Performance', description: 'Speed or efficiency concerns' }
  ];

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      category: 'bug',
      attachments: []
    });
    setErrors({});
    setSubmitResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const openModal = () => {
    setIsModalOpen(true);
    resetForm();
  };

  const closeModal = () => {
    setIsModalOpen(false);
    resetForm();
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear field-specific errors when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['text/plain', 'image/png', 'image/jpeg', 'application/pdf', 'application/json'];
    
    const validFiles = files.filter(file => {
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        return false;
      }
      if (!allowedTypes.includes(file.type)) {
        alert(`File ${file.name} has an unsupported type. Allowed: txt, png, jpg, pdf, json`);
        return false;
      }
      return true;
    });

    setFormData(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...validFiles]
    }));
  };

  const removeAttachment = (index) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.length > 10000) {
      newErrors.description = 'Description must be 10,000 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const getCurrentBuildHash = async () => {
    try {
      // Try to get build hash from window object or make API call
      if (window.electronAPI) {
        return await window.electronAPI.getBuildHash();
      }
      // Fallback to timestamp-based hash
      return `web-${Date.now().toString(36)}`;
    } catch {
      return `fallback-${Date.now().toString(36)}`;
    }
  };

  const getCurrentPageContext = () => {
    return {
      url: window.location.href,
      pathname: window.location.pathname,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    };
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setSubmitResult(null);

    try {
      // Gather system context
      const buildHash = await getCurrentBuildHash();
      const pageCtx = getCurrentPageContext();

      // Prepare form data for submission
      const submitData = new FormData();
      submitData.append('title', formData.title);
      submitData.append('description', formData.description);
      submitData.append('category', formData.category);
      submitData.append('page_ctx', JSON.stringify(pageCtx));
      submitData.append('build_hash', buildHash);
      submitData.append('user_role', 'user'); // Could be dynamic based on auth

      // Add attachments
      formData.attachments.forEach((file, index) => {
        submitData.append(`attachments`, file);
      });

      // Submit to API
      const response = await fetch('/api/bugs', {
        method: 'POST',
        body: submitData
      });

      const result = await response.json();

      if (response.ok) {
        setSubmitResult({
          type: 'success',
          message: `Feedback submitted successfully! Reference ID: ${result.bug_id}`,
          bugId: result.bug_id
        });
        
        // Call optional onSubmit callback
        if (onSubmit) {
          onSubmit(result);
        }

        // Auto-close modal after success
        setTimeout(() => {
          closeModal();
        }, 3000);

      } else {
        throw new Error(result.detail || 'Failed to submit feedback');
      }

    } catch (error) {
      console.error('Feedback submission error:', error);
      setSubmitResult({
        type: 'error',
        message: `Failed to submit feedback: ${error.message}`
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const takeScreenshot = async () => {
    try {
      if (window.electronAPI && window.electronAPI.takeScreenshot) {
        const screenshotBlob = await window.electronAPI.takeScreenshot();
        const file = new File([screenshotBlob], `screenshot-${Date.now()}.png`, {
          type: 'image/png'
        });
        
        setFormData(prev => ({
          ...prev,
          attachments: [...prev.attachments, file]
        }));
      } else {
        alert('Screenshot functionality is not available in this environment');
      }
    } catch (error) {
      console.error('Screenshot failed:', error);
      alert('Failed to take screenshot');
    }
  };

  return (
    <>
      {/* Floating Feedback Button */}
      <button
        onClick={openModal}
        className={`feedback-button ${className}`}
        title="Send Feedback"
        aria-label="Send feedback or report a bug"
      >
        <MessageSquare size={20} />
        <span>Feedback</span>
      </button>

      {/* Modal */}
      {isModalOpen && (
        <div className="feedback-modal-overlay" onClick={closeModal}>
          <div className="feedback-modal" onClick={e => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="feedback-modal-header">
              <h2>
                <Bug size={24} />
                Send Feedback
              </h2>
              <button
                onClick={closeModal}
                className="feedback-modal-close"
                aria-label="Close feedback modal"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="feedback-modal-body">
              {submitResult ? (
                <div className={`feedback-result feedback-result-${submitResult.type}`}>
                  {submitResult.type === 'success' ? (
                    <CheckCircle size={24} />
                  ) : (
                    <AlertCircle size={24} />
                  )}
                  <p>{submitResult.message}</p>
                  {submitResult.bugId && (
                    <small>Keep this reference ID for tracking: {submitResult.bugId}</small>
                  )}
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="feedback-form">
                  {/* Category Selection */}
                  <div className="form-group">
                    <label htmlFor="category">Category *</label>
                    <div className="category-grid">
                      {categories.map(cat => (
                        <label key={cat.value} className="category-option">
                          <input
                            type="radio"
                            name="category"
                            value={cat.value}
                            checked={formData.category === cat.value}
                            onChange={e => handleInputChange('category', e.target.value)}
                          />
                          <div className="category-content">
                            <strong>{cat.label}</strong>
                            <small>{cat.description}</small>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Title Field */}
                  <div className="form-group">
                    <label htmlFor="title">Title *</label>
                    <input
                      id="title"
                      type="text"
                      value={formData.title}
                      onChange={e => handleInputChange('title', e.target.value)}
                      placeholder="Brief summary of your feedback..."
                      maxLength={200}
                      className={errors.title ? 'error' : ''}
                      required
                    />
                    {errors.title && <span className="error-message">{errors.title}</span>}
                    <small>{formData.title.length}/200 characters</small>
                  </div>

                  {/* Description Field */}
                  <div className="form-group">
                    <label htmlFor="description">Description *</label>
                    <textarea
                      id="description"
                      value={formData.description}
                      onChange={e => handleInputChange('description', e.target.value)}
                      placeholder="Please provide detailed information about your feedback..."
                      maxLength={10000}
                      rows={6}
                      className={errors.description ? 'error' : ''}
                      required
                    />
                    {errors.description && <span className="error-message">{errors.description}</span>}
                    <small>{formData.description.length}/10,000 characters</small>
                  </div>

                  {/* File Attachments */}
                  <div className="form-group">
                    <label>Attachments (Optional)</label>
                    <div className="attachment-controls">
                      <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        onChange={handleFileSelect}
                        accept=".txt,.log,.png,.jpg,.jpeg,.pdf,.json"
                        style={{ display: 'none' }}
                      />
                      <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="attachment-button"
                      >
                        <Upload size={16} />
                        Select Files
                      </button>
                      <button
                        type="button"
                        onClick={takeScreenshot}
                        className="attachment-button"
                      >
                        📸 Screenshot
                      </button>
                    </div>
                    
                    {formData.attachments.length > 0 && (
                      <div className="attachment-list">
                        {formData.attachments.map((file, index) => (
                          <div key={index} className="attachment-item">
                            <span>{file.name}</span>
                            <small>({(file.size / 1024 / 1024).toFixed(2)} MB)</small>
                            <button
                              type="button"
                              onClick={() => removeAttachment(index)}
                              className="remove-attachment"
                              aria-label={`Remove ${file.name}`}
                            >
                              <X size={14} />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    <small>Supported formats: txt, log, png, jpg, pdf, json (max 10MB each)</small>
                  </div>

                  {/* Submit Button */}
                  <div className="form-actions">
                    <button
                      type="button"
                      onClick={closeModal}
                      className="button-secondary"
                      disabled={isSubmitting}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="button-primary"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? (
                        <>
                          <Loader size={16} className="spinner" />
                          Submitting...
                        </>
                      ) : (
                        <>
                          <MessageSquare size={16} />
                          Submit Feedback
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FeedbackButton;