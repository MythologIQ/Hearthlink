import React from 'react';
import './AccessibilityPanel.css';

const AccessibilityPanel = ({ settings, onSettingChange, isVisible, onClose }) => {
  const handleToggle = (feature) => {
    onSettingChange(feature);
  };

  const handleFontSizeChange = (event) => {
    const newSize = event.target.value;
    // Update font size through accessibility API
    if (window.accessibility) {
      window.accessibility.setFontSize(newSize);
    }
  };

  const handleSpeak = (text) => {
    if (window.accessibility) {
      window.accessibility.speak(text);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="accessibility-panel visible">
      <h2>
        ♿ Accessibility Settings
        <button 
          onClick={onClose}
          className="close-btn"
          aria-label="Close accessibility panel"
        >
          ✕
        </button>
      </h2>
      
      <div className="accessibility-option">
        <label>
          <input
            type="checkbox"
            checked={settings.highContrast}
            onChange={() => handleToggle('high-contrast')}
          />
          High Contrast Mode
        </label>
        <p>Increases contrast for better visibility</p>
      </div>
      
      <div className="accessibility-option">
        <label>
          <input
            type="checkbox"
            checked={settings.screenReader}
            onChange={() => handleToggle('screen-reader')}
          />
          Screen Reader Support
        </label>
        <p>Enables screen reader compatibility</p>
      </div>
      
      <div className="accessibility-option">
        <label>
          <input
            type="checkbox"
            checked={settings.voiceFeedback}
            onChange={() => handleToggle('voice-feedback')}
          />
          Voice Feedback
        </label>
        <p>Provides audio feedback for actions</p>
      </div>
      
      <div className="accessibility-option">
        <label>
          Font Size
        </label>
        <select 
          value={settings.fontSize} 
          onChange={handleFontSizeChange}
        >
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
          <option value="x-large">Extra Large</option>
        </select>
      </div>
      
      <div className="accessibility-option">
        <h4>Keyboard Shortcuts</h4>
        <ul className="shortcut-list">
          <li>
            <span>Toggle Voice Interface</span>
            <span className="shortcut-key">Ctrl+Shift+V</span>
          </li>
          <li>
            <span>Toggle Accessibility Panel</span>
            <span className="shortcut-key">Ctrl+Shift+A</span>
          </li>
          <li>
            <span>Open Help</span>
            <span className="shortcut-key">F1</span>
          </li>
          <li>
            <span>New Session</span>
            <span className="shortcut-key">Ctrl+N</span>
          </li>
        </ul>
      </div>
      
      <div className="accessibility-option">
        <h4>Test Voice Feedback</h4>
        <div className="test-buttons">
          <button 
            onClick={() => handleSpeak('Voice feedback is working correctly')}
            className="test-btn"
          >
            Test Voice
          </button>
          <button 
            onClick={() => handleSpeak('High contrast mode activated')}
            className="test-btn"
          >
            Test Contrast
          </button>
        </div>
      </div>
      
      <div className="accessibility-option">
        <h4>Accessibility Information</h4>
        <p>
          Hearthlink is designed with accessibility in mind. All features can be 
          accessed via keyboard navigation, and voice commands are available for 
          hands-free operation.
        </p>
        <p>
          For additional accessibility features, please refer to the Accessibility 
          Guide in the Help menu.
        </p>
      </div>
      
      <div className="accessibility-footer">
        <button 
          onClick={() => window.electronAPI?.openExternal('https://www.w3.org/WAI/')}
          className="external-link"
        >
          Learn More About Web Accessibility
        </button>
      </div>
    </div>
  );
};

export default AccessibilityPanel; 