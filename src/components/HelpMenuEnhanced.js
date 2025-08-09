import React, { useState, useEffect, useRef } from 'react';
import './HelpMenuEnhanced.css';

const HelpMenuEnhanced = ({ isVisible, onClose, appVersion }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [documentation, setDocumentation] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [recentlyViewed, setRecentlyViewed] = useState([]);
  const searchInputRef = useRef(null);

  useEffect(() => {
    if (isVisible) {
      loadDocumentation();
      // Focus search input for immediate search
      setTimeout(() => {
        if (searchInputRef.current) {
          searchInputRef.current.focus();
        }
      }, 100);
    }
  }, [isVisible]);

  useEffect(() => {
    // Load favorites and recent from localStorage
    const savedFavorites = localStorage.getItem('hearthlink-help-favorites');
    const savedRecent = localStorage.getItem('hearthlink-help-recent');
    
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
    if (savedRecent) {
      setRecentlyViewed(JSON.parse(savedRecent));
    }
  }, []);

  useEffect(() => {
    // Save favorites and recent to localStorage
    localStorage.setItem('hearthlink-help-favorites', JSON.stringify(favorites));
    localStorage.setItem('hearthlink-help-recent', JSON.stringify(recentlyViewed));
  }, [favorites, recentlyViewed]);

  useEffect(() => {
    // Search functionality
    if (searchTerm.length > 2) {
      performSearch(searchTerm);
      setIsSearchMode(true);
    } else {
      setIsSearchMode(false);
      setSearchResults([]);
    }
  }, [searchTerm, documentation]);

  const loadDocumentation = async () => {
    setLoadingDocs(true);
    try {
      const docs = {};
      
      // Load documentation files
      const files = [
        { key: 'userGuide', path: 'docs/public/USER_GUIDE.md', title: 'User Guide' },
        { key: 'accessibility', path: 'docs/public/ACCESSIBILITY.md', title: 'Accessibility' },
        { key: 'troubleshooting', path: 'docs/public/TROUBLESHOOTING.md', title: 'Troubleshooting' },
        { key: 'quickStart', path: 'docs/public/QUICK_START.md', title: 'Quick Start' },
        { key: 'faq', path: 'docs/public/FAQ.md', title: 'FAQ' }
      ];

      for (const file of files) {
        try {
          if (window.fileSystem) {
            const exists = await window.fileSystem.exists(file.path);
            if (exists) {
              const content = await window.fileSystem.readFile(file.path);
              docs[file.key] = { content, title: file.title, path: file.path };
            }
          } else {
            // Fallback: try to fetch from public directory
            try {
              const response = await fetch(`/${file.path}`);
              if (response.ok) {
                const content = await response.text();
                docs[file.key] = { content, title: file.title, path: file.path };
              }
            } catch (fetchError) {
              console.warn(`Could not fetch ${file.path}:`, fetchError);
            }
          }
        } catch (error) {
          console.error(`Error loading ${file.path}:`, error);
        }
      }

      setDocumentation(docs);
    } catch (error) {
      console.error('Error loading documentation:', error);
    } finally {
      setLoadingDocs(false);
    }
  };

  const performSearch = (term) => {
    const results = [];
    const searchLower = term.toLowerCase();

    // Search through all documentation
    Object.entries(documentation).forEach(([key, doc]) => {
      if (doc.content) {
        const lines = doc.content.split('\n');
        lines.forEach((line, index) => {
          if (line.toLowerCase().includes(searchLower)) {
            results.push({
              docKey: key,
              docTitle: doc.title,
              line: line.trim(),
              lineNumber: index + 1,
              context: getContextLines(lines, index, 1)
            });
          }
        });
      }
    });

    // Search through built-in content
    const builtInSections = [
      { key: 'overview', title: 'Overview', content: getOverviewContent() },
      { key: 'shortcuts', title: 'Shortcuts', content: getShortcutsContent() }
    ];

    builtInSections.forEach(section => {
      if (section.content.toLowerCase().includes(searchLower)) {
        results.push({
          docKey: section.key,
          docTitle: section.title,
          line: 'Found in ' + section.title,
          builtIn: true
        });
      }
    });

    setSearchResults(results.slice(0, 20)); // Limit to 20 results
  };

  const getContextLines = (lines, centerIndex, radius) => {
    const start = Math.max(0, centerIndex - radius);
    const end = Math.min(lines.length, centerIndex + radius + 1);
    return lines.slice(start, end).join(' ').trim();
  };

  const getOverviewContent = () => {
    return `Welcome to Hearthlink v${appVersion} AI-powered productivity system accessibility voice-first principles manage tasks organized efficient intelligent assistance`;
  };

  const getShortcutsContent = () => {
    return 'keyboard shortcuts F1 help Ctrl+N new session Ctrl+Shift+V voice Ctrl+Shift+A accessibility navigation Tab Enter Space Escape';
  };

  const addToFavorites = (tabId) => {
    if (!favorites.includes(tabId)) {
      setFavorites([...favorites, tabId]);
    }
  };

  const removeFromFavorites = (tabId) => {
    setFavorites(favorites.filter(id => id !== tabId));
  };

  const addToRecentlyViewed = (tabId) => {
    const newRecent = [tabId, ...recentlyViewed.filter(id => id !== tabId)].slice(0, 5);
    setRecentlyViewed(newRecent);
  };

  const handleTabClick = (tabId) => {
    setActiveTab(tabId);
    addToRecentlyViewed(tabId);
    setIsSearchMode(false);
    setSearchTerm('');
  };

  const handleSearchResultClick = (result) => {
    if (!result.builtIn) {
      setActiveTab(result.docKey);
      addToRecentlyViewed(result.docKey);
    } else {
      setActiveTab(result.docKey);
    }
    setIsSearchMode(false);
    setSearchTerm('');
  };

  const renderMarkdown = (text) => {
    if (!text) return <p>Documentation not available.</p>;
    
    // Enhanced markdown rendering with better formatting
    const lines = text.split('\n');
    const elements = [];
    let currentList = [];
    let inCodeBlock = false;
    let codeBlockContent = [];

    lines.forEach((line, index) => {
      // Code blocks
      if (line.startsWith('```')) {
        if (inCodeBlock) {
          elements.push(
            <pre key={`code-${index}`} className="code-block">
              <code>{codeBlockContent.join('\n')}</code>
            </pre>
          );
          codeBlockContent = [];
        }
        inCodeBlock = !inCodeBlock;
        return;
      }

      if (inCodeBlock) {
        codeBlockContent.push(line);
        return;
      }

      // Headers
      if (line.startsWith('# ')) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${index}`}>{currentList}</ul>);
          currentList = [];
        }
        elements.push(<h1 key={index} className="doc-h1">{line.substring(2)}</h1>);
      } else if (line.startsWith('## ')) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${index}`}>{currentList}</ul>);
          currentList = [];
        }
        elements.push(<h2 key={index} className="doc-h2">{line.substring(3)}</h2>);
      } else if (line.startsWith('### ')) {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${index}`}>{currentList}</ul>);
          currentList = [];
        }
        elements.push(<h3 key={index} className="doc-h3">{line.substring(4)}</h3>);
      } else if (line.startsWith('- ') || line.startsWith('* ')) {
        currentList.push(<li key={`li-${index}`}>{line.substring(2)}</li>);
      } else if (line.trim() === '') {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${index}`}>{currentList}</ul>);
          currentList = [];
        }
        elements.push(<br key={index} />);
      } else if (line.startsWith('**') && line.endsWith('**')) {
        elements.push(<p key={index} className="doc-emphasis">{line.slice(2, -2)}</p>);
      } else {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${index}`}>{currentList}</ul>);
          currentList = [];
        }
        // Handle inline code and links
        const formattedLine = line
          .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
          .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        elements.push(
          <p key={index} className="doc-paragraph" 
             dangerouslySetInnerHTML={{ __html: formattedLine }} />
        );
      }
    });

    // Don't forget the last list
    if (currentList.length > 0) {
      elements.push(<ul key="final-list">{currentList}</ul>);
    }

    return elements;
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '🏠', category: 'Getting Started' },
    { id: 'quickStart', label: 'Quick Start', icon: '⚡', category: 'Getting Started' },
    { id: 'userGuide', label: 'User Guide', icon: '📖', category: 'Documentation' },
    { id: 'accessibility', label: 'Accessibility', icon: '♿', category: 'Accessibility' },
    { id: 'troubleshooting', label: 'Troubleshooting', icon: '🔧', category: 'Support' },
    { id: 'faq', label: 'FAQ', icon: '❓', category: 'Support' },
    { id: 'shortcuts', label: 'Shortcuts', icon: '⌨️', category: 'Reference' }
  ];

  const categorizedTabs = tabs.reduce((acc, tab) => {
    if (!acc[tab.category]) acc[tab.category] = [];
    acc[tab.category].push(tab);
    return acc;
  }, {});

  const renderTabContent = () => {
    if (isSearchMode) {
      return (
        <div className="search-results">
          <h3>Search Results for "{searchTerm}"</h3>
          {searchResults.length === 0 ? (
            <p>No results found. Try different keywords.</p>
          ) : (
            <div className="search-results-list">
              {searchResults.map((result, index) => (
                <div 
                  key={index} 
                  className="search-result-item"
                  onClick={() => handleSearchResultClick(result)}
                >
                  <div className="search-result-header">
                    <span className="search-result-doc">{result.docTitle}</span>
                    {result.lineNumber && (
                      <span className="search-result-line">Line {result.lineNumber}</span>
                    )}
                  </div>
                  <div className="search-result-content">
                    {result.line}
                  </div>
                  {result.context && result.context !== result.line && (
                    <div className="search-result-context">
                      {result.context}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    switch (activeTab) {
      case 'overview':
        return (
          <div className="help-section">
            <div className="section-header">
              <h2>Welcome to Hearthlink v{appVersion}</h2>
              <button 
                className={`favorite-btn ${favorites.includes('overview') ? 'favorited' : ''}`}
                onClick={() => favorites.includes('overview') ? removeFromFavorites('overview') : addToFavorites('overview')}
                aria-label="Add to favorites"
              >
                {favorites.includes('overview') ? '★' : '☆'}
              </button>
            </div>
            
            <div className="feature-grid">
              <div className="feature-card">
                <div className="feature-icon">🤖</div>
                <h3>AI Orchestration</h3>
                <p>Multiple AI personas working together for complex tasks</p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">🎤</div>
                <h3>Voice-First Design</h3>
                <p>Complete voice control for hands-free operation</p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">♿</div>
                <h3>Accessibility First</h3>
                <p>Built for users with diverse abilities and needs</p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">🔒</div>
                <h3>Privacy & Security</h3>
                <p>Local-first architecture with enterprise security</p>
              </div>
            </div>
            
            <div className="quick-start-actions">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <button 
                  className="action-btn primary"
                  onClick={() => handleTabClick('quickStart')}
                >
                  🚀 Get Started in 5 Minutes
                </button>
                <button 
                  className="action-btn secondary"
                  onClick={() => handleTabClick('shortcuts')}
                >
                  ⌨️ View Keyboard Shortcuts
                </button>
                <button 
                  className="action-btn secondary"
                  onClick={() => handleTabClick('troubleshooting')}
                >
                  🔧 Solve Common Issues
                </button>
              </div>
            </div>
            
            <div className="help-tips">
              <h3>💡 Pro Tips</h3>
              <ul>
                <li><strong>Search Help:</strong> Use the search box above to find specific information</li>
                <li><strong>Voice Commands:</strong> Press Ctrl+Shift+V or say "Help" to open this menu</li>
                <li><strong>Keyboard Navigation:</strong> Use Tab and arrow keys to navigate</li>
                <li><strong>Context Help:</strong> Press F1 anywhere for context-specific help</li>
              </ul>
            </div>
          </div>
        );
        
      case 'shortcuts':
        return (
          <div className="help-section">
            <div className="section-header">
              <h2>Keyboard Shortcuts & Commands</h2>
              <button 
                className={`favorite-btn ${favorites.includes('shortcuts') ? 'favorited' : ''}`}
                onClick={() => favorites.includes('shortcuts') ? removeFromFavorites('shortcuts') : addToFavorites('shortcuts')}
                aria-label="Add to favorites"
              >
                {favorites.includes('shortcuts') ? '★' : '☆'}
              </button>
            </div>
            
            <div className="shortcuts-grid">
              <div className="shortcut-category">
                <h3>🔧 Application Shortcuts</h3>
                <div className="shortcut-list">
                  <div className="shortcut-item">
                    <span>Open Help</span>
                    <kbd>F1</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>New Session</span>
                    <kbd>Ctrl+N</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Toggle Voice Interface</span>
                    <kbd>Ctrl+Shift+V</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Toggle Accessibility Panel</span>
                    <kbd>Ctrl+Shift+A</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Settings</span>
                    <kbd>Ctrl+,</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Exit Application</span>
                    <kbd>Ctrl+Q</kbd>
                  </div>
                </div>
              </div>

              <div className="shortcut-category">
                <h3>🎤 Voice Commands</h3>
                <div className="shortcut-list">
                  <div className="shortcut-item">
                    <span>Open Help</span>
                    <kbd>"Help"</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>New Session</span>
                    <kbd>"New session"</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Switch Agent</span>
                    <kbd>"Switch to [name]"</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Check Status</span>
                    <kbd>"Check status"</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Accessibility</span>
                    <kbd>"Accessibility"</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Exit Application</span>
                    <kbd>"Exit" or "Quit"</kbd>
                  </div>
                </div>
              </div>

              <div className="shortcut-category">
                <h3>🧭 Navigation</h3>
                <div className="shortcut-list">
                  <div className="shortcut-item">
                    <span>Navigate Forward</span>
                    <kbd>Tab</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Navigate Backward</span>
                    <kbd>Shift+Tab</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Activate Button</span>
                    <kbd>Enter / Space</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Close Dialog</span>
                    <kbd>Escape</kbd>
                  </div>
                  <div className="shortcut-item">
                    <span>Navigate Lists</span>
                    <kbd>Arrow Keys</kbd>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
        
      default:
        if (documentation[activeTab]) {
          return (
            <div className="help-section">
              <div className="section-header">
                <h2>{documentation[activeTab].title}</h2>
                <div className="section-actions">
                  <button 
                    className={`favorite-btn ${favorites.includes(activeTab) ? 'favorited' : ''}`}
                    onClick={() => favorites.includes(activeTab) ? removeFromFavorites(activeTab) : addToFavorites(activeTab)}
                    aria-label="Add to favorites"
                  >
                    {favorites.includes(activeTab) ? '★' : '☆'}
                  </button>
                  <button 
                    className="print-btn"
                    onClick={() => window.print()}
                    aria-label="Print this page"
                  >
                    🖨️
                  </button>
                </div>
              </div>
              <div className="markdown-content">
                {renderMarkdown(documentation[activeTab].content)}
              </div>
            </div>
          );
        }
        return <p>Select a tab to view help content.</p>;
    }
  };

  if (!isVisible) return null;

  return (
    <div className="help-menu-enhanced visible">
      <div className="help-header">
        <div className="help-title">
          <h2>
            ❓ Help & Documentation
          </h2>
          <div className="help-search">
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search documentation..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
              aria-label="Search help documentation"
            />
            {searchTerm && (
              <button 
                className="clear-search"
                onClick={() => setSearchTerm('')}
                aria-label="Clear search"
              >
                ✕
              </button>
            )}
          </div>
        </div>
        <button 
          onClick={onClose}
          className="close-btn"
          aria-label="Close help menu"
        >
          ✕
        </button>
      </div>
      
      <div className="help-body">
        <div className="help-sidebar">
          {/* Favorites Section */}
          {favorites.length > 0 && (
            <div className="sidebar-section">
              <h4>★ Favorites</h4>
              <div className="quick-tabs">
                {favorites.map(favId => {
                  const tab = tabs.find(t => t.id === favId);
                  return tab ? (
                    <button
                      key={favId}
                      onClick={() => handleTabClick(favId)}
                      className={`quick-tab ${activeTab === favId ? 'active' : ''}`}
                      title={tab.label}
                    >
                      <span className="tab-icon">{tab.icon}</span>
                      <span className="tab-label">{tab.label}</span>
                    </button>
                  ) : null;
                })}
              </div>
            </div>
          )}

          {/* Recently Viewed */}
          {recentlyViewed.length > 0 && (
            <div className="sidebar-section">
              <h4>🕒 Recent</h4>
              <div className="quick-tabs">
                {recentlyViewed.slice(0, 3).map(recentId => {
                  const tab = tabs.find(t => t.id === recentId);
                  return tab ? (
                    <button
                      key={recentId}
                      onClick={() => handleTabClick(recentId)}
                      className={`quick-tab ${activeTab === recentId ? 'active' : ''}`}
                      title={tab.label}
                    >
                      <span className="tab-icon">{tab.icon}</span>
                      <span className="tab-label">{tab.label}</span>
                    </button>
                  ) : null;
                })}
              </div>
            </div>
          )}

          {/* All Tabs Categorized */}
          <div className="sidebar-section">
            <h4>📚 All Documentation</h4>
            {Object.entries(categorizedTabs).map(([category, categoryTabs]) => (
              <div key={category} className="tab-category">
                <h5>{category}</h5>
                <div className="category-tabs">
                  {categoryTabs.map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => handleTabClick(tab.id)}
                      className={`help-tab ${activeTab === tab.id ? 'active' : ''}`}
                      aria-label={`Open ${tab.label} tab`}
                    >
                      <span className="tab-icon">{tab.icon}</span>
                      <span className="tab-label">{tab.label}</span>
                      {favorites.includes(tab.id) && <span className="fav-indicator">★</span>}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="help-content">
          {loadingDocs ? (
            <div className="loading-indicator">
              <div className="spinner"></div>
              <p>Loading documentation...</p>
            </div>
          ) : (
            renderTabContent()
          )}
        </div>
      </div>
      
      <div className="help-footer">
        <div className="footer-info">
          <span><strong>Hearthlink v{appVersion}</strong></span>
          <span>Press <kbd>F1</kbd> for context help anywhere</span>
          <span>Use <kbd>Ctrl+Shift+V</kbd> for voice commands</span>
        </div>
        <div className="help-links">
          <button 
            onClick={() => window.electronAPI?.openExternal('https://github.com/WulfForge/Hearthlink')}
            className="external-link"
          >
            🔗 GitHub Repository
          </button>
          <button 
            onClick={() => window.electronAPI?.openExternal('https://github.com/WulfForge/Hearthlink/issues')}
            className="external-link"
          >
            🐛 Report Issues
          </button>
        </div>
      </div>
    </div>
  );
};

export default HelpMenuEnhanced;