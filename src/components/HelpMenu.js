import React, { useState, useEffect } from 'react';

const HelpMenu = ({ isVisible, onClose, appVersion }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [documentation, setDocumentation] = useState({});

  useEffect(() => {
    if (isVisible && window.fileSystem) {
      loadDocumentation();
    }
  }, [isVisible]);

  const loadDocumentation = async () => {
    try {
      const docs = {};
      
      // Load documentation files
      const files = [
        { key: 'userGuide', path: 'docs/public/USER_GUIDE.md' },
        { key: 'accessibility', path: 'docs/public/ACCESSIBILITY.md' },
        { key: 'troubleshooting', path: 'docs/public/TROUBLESHOOTING.md' },
        { key: 'quickStart', path: 'docs/public/QUICK_START.md' },
        { key: 'faq', path: 'docs/public/FAQ.md' }
      ];

      for (const file of files) {
        try {
          const exists = await window.fileSystem.exists(file.path);
          if (exists) {
            const content = await window.fileSystem.readFile(file.path);
            docs[file.key] = content;
          }
        } catch (error) {
          console.error(`Error loading ${file.path}:`, error);
        }
      }

      setDocumentation(docs);
    } catch (error) {
      console.error('Error loading documentation:', error);
    }
  };

  const renderMarkdown = (text) => {
    if (!text) return <p>Documentation not available.</p>;
    
    // Simple markdown rendering
    return text
      .split('\n')
      .map((line, index) => {
        if (line.startsWith('# ')) {
          return <h1 key={index}>{line.substring(2)}</h1>;
        }
        if (line.startsWith('## ')) {
          return <h2 key={index}>{line.substring(3)}</h2>;
        }
        if (line.startsWith('### ')) {
          return <h3 key={index}>{line.substring(4)}</h3>;
        }
        if (line.startsWith('- ')) {
          return <li key={index}>{line.substring(2)}</li>;
        }
        if (line.trim() === '') {
          return <br key={index} />;
        }
        return <p key={index}>{line}</p>;
      });
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '🏠' },
    { id: 'userGuide', label: 'User Guide', icon: '📖' },
    { id: 'accessibility', label: 'Accessibility', icon: '♿' },
    { id: 'troubleshooting', label: 'Troubleshooting', icon: '🔧' },
    { id: 'quickStart', label: 'Quick Start', icon: '⚡' },
    { id: 'faq', label: 'FAQ', icon: '❓' },
    { id: 'shortcuts', label: 'Shortcuts', icon: '⌨️' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="help-section">
            <h2>Welcome to Hearthlink v{appVersion}</h2>
            <p>
              Hearthlink is an AI-powered productivity system designed with accessibility 
              and voice-first principles. It helps you manage tasks, stay organized, and 
              work more efficiently through intelligent assistance.
            </p>
            
            <h3>Key Features</h3>
            <ul>
              <li><strong>Voice Commands:</strong> Control the application hands-free</li>
              <li><strong>Accessibility First:</strong> Built for users with diverse needs</li>
              <li><strong>AI Personas:</strong> Different AI assistants for different tasks</li>
              <li><strong>Dashboard:</strong> Visual overview of your productivity</li>
              <li><strong>Voice Feedback:</strong> Audio confirmation of actions</li>
            </ul>
            
            <h3>Getting Started</h3>
            <p>
              Use the persona selector to switch between different AI assistants. 
              Press F1 for help, or use Ctrl+Shift+V to activate voice commands.
            </p>
          </div>
        );
        
      case 'userGuide':
        return (
          <div className="help-section">
            <h2>User Guide</h2>
            <div className="markdown-content">
              {renderMarkdown(documentation.userGuide)}
            </div>
          </div>
        );
        
      case 'accessibility':
        return (
          <div className="help-section">
            <h2>Accessibility Guide</h2>
            <div className="markdown-content">
              {renderMarkdown(documentation.accessibility)}
            </div>
          </div>
        );
        
      case 'troubleshooting':
        return (
          <div className="help-section">
            <h2>Troubleshooting</h2>
            <div className="markdown-content">
              {renderMarkdown(documentation.troubleshooting)}
            </div>
          </div>
        );
        
      case 'quickStart':
        return (
          <div className="help-section">
            <h2>Quick Start Guide</h2>
            <div className="markdown-content">
              {renderMarkdown(documentation.quickStart)}
            </div>
          </div>
        );
        
      case 'faq':
        return (
          <div className="help-section">
            <h2>Frequently Asked Questions</h2>
            <div className="markdown-content">
              {renderMarkdown(documentation.faq)}
            </div>
          </div>
        );
        
      case 'shortcuts':
        return (
          <div className="help-section">
            <h2>Keyboard Shortcuts</h2>
            
            <h3>Application Shortcuts</h3>
            <ul className="shortcut-list">
              <li>
                <span>New Session</span>
                <span className="shortcut-key">Ctrl+N</span>
              </li>
              <li>
                <span>Open Help</span>
                <span className="shortcut-key">F1</span>
              </li>
              <li>
                <span>Toggle Voice Interface</span>
                <span className="shortcut-key">Ctrl+Shift+V</span>
              </li>
              <li>
                <span>Toggle Accessibility Panel</span>
                <span className="shortcut-key">Ctrl+Shift+A</span>
              </li>
              <li>
                <span>Exit Application</span>
                <span className="shortcut-key">Ctrl+Q</span>
              </li>
            </ul>
            
            <h3>Voice Commands</h3>
            <ul className="shortcut-list">
              <li>
                <span>New Session</span>
                <span className="shortcut-key">"New session"</span>
              </li>
              <li>
                <span>Open Help</span>
                <span className="shortcut-key">"Help"</span>
              </li>
              <li>
                <span>Accessibility Guide</span>
                <span className="shortcut-key">"Accessibility"</span>
              </li>
              <li>
                <span>Troubleshooting</span>
                <span className="shortcut-key">"Troubleshooting"</span>
              </li>
              <li>
                <span>Exit Application</span>
                <span className="shortcut-key">"Exit" or "Quit"</span>
              </li>
            </ul>
            
            <h3>Navigation</h3>
            <ul className="shortcut-list">
              <li>
                <span>Switch Personas</span>
                <span className="shortcut-key">Tab (then arrow keys)</span>
              </li>
              <li>
                <span>Focus Management</span>
                <span className="shortcut-key">Tab / Shift+Tab</span>
              </li>
              <li>
                <span>Activate Button</span>
                <span className="shortcut-key">Enter / Space</span>
              </li>
            </ul>
          </div>
        );
        
      default:
        return <p>Select a tab to view help content.</p>;
    }
  };

  if (!isVisible) return null;

  return (
    <div className="help-menu visible">
      <div className="help-header">
        <h2>
          ❓ Help & Documentation
          <button 
            onClick={onClose}
            className="close-btn"
            aria-label="Close help menu"
          >
            ✕
          </button>
        </h2>
      </div>
      
      <div className="help-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`help-tab ${activeTab === tab.id ? 'active' : ''}`}
            aria-label={`Open ${tab.label} tab`}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>
      
      <div className="help-content">
        {renderTabContent()}
      </div>
      
      <div className="help-footer">
        <p>
          <strong>Hearthlink v{appVersion}</strong> - Built with accessibility and voice-first design principles.
        </p>
        <div className="help-links">
          <button 
            onClick={() => window.electronAPI?.openExternal('https://github.com/WulfForge/Hearthlink')}
            className="external-link"
          >
            GitHub Repository
          </button>
          <button 
            onClick={() => window.electronAPI?.openExternal('https://github.com/WulfForge/Hearthlink/issues')}
            className="external-link"
          >
            Report Issues
          </button>
        </div>
      </div>
    </div>
  );
};

export default HelpMenu; 