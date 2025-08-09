import React, { useState, useEffect } from 'react';
import './LaunchPage.css';

const LaunchPage = ({ onModuleSelect, onShowAccessibility, onShowHelp }) => {
  // console.log('LaunchPage: Component rendering with props:', { onModuleSelect: !!onModuleSelect });
  
  // const navigate = useNavigate(); // Removed for Tauri native app
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [currentStatus, setCurrentStatus] = useState('Initializing Hearthlink...');
  const [isLoaded, setIsLoaded] = useState(false);
  const [showIcons, setShowIcons] = useState(false);

  const loadingSteps = [
    { progress: 10, status: 'Initializing Hearthlink Systems...', delay: 800 },
    { progress: 25, status: 'Loading AI Personas...', delay: 1000 },
    { progress: 40, status: 'Connecting to Synapse Gateway...', delay: 1200 },
    { progress: 55, status: 'Initializing Memory Systems...', delay: 900 },
    { progress: 70, status: 'Loading Orchestration Engine...', delay: 1100 },
    { progress: 85, status: 'Establishing Workspace Connection...', delay: 800 },
    { progress: 95, status: 'Finalizing StarCraft Interface...', delay: 700 },
    { progress: 100, status: 'All Systems Online - Select Module', delay: 1000 }
  ];

  useEffect(() => {
    const runLoadingSequence = async () => {
      // Show icons after initial delay
      setTimeout(() => {
        // console.log('LaunchPage: Setting showIcons to true');
        setShowIcons(true);
      }, 1500);
      
      for (let i = 0; i < loadingSteps.length; i++) {
        const step = loadingSteps[i];
        
        await new Promise(resolve => setTimeout(resolve, step.delay));
        
        setLoadingProgress(step.progress);
        setCurrentStatus(step.status);
        
        if (step.progress === 100) {
          setTimeout(() => {
            // console.log('LaunchPage: Setting isLoaded to true');
            setIsLoaded(true);
            // Don't auto-complete - wait for user selection
          }, 500);
        }
      }
    };
    
    runLoadingSequence();
  }, []);

  // 7 modules arranged in 270° arc with equal spacing, opening centered at top (12 o'clock)
  // Gap from 225° to 315° (90° gap centered at top)
  // Rotated by -90° to position gap at top
  const modules = [
    { name: 'Synapse', angle: 315, description: 'Security Gateway' }, // Top-left (start of arc)
    { name: 'Alden', angle: 0, description: 'Primary AI Persona' }, // Right
    { name: 'Alice', angle: 45, description: 'Assistant Persona' }, // Bottom-right
    { name: 'Vault', angle: 90, description: 'Memory Repository' }, // Bottom
    { name: 'Core', angle: 135, description: 'AI Orchestration Engine' }, // Bottom-left
    { name: 'Mimic', angle: 180, description: 'Adaptive Intelligence' }, // Left
    { name: 'Sentry', angle: 225, description: 'System Monitor' } // Top-right (end of arc)
  ];

  // Route mapping for navigation
  const routeMap = {
    'Core': '/core',
    'Alden': '/alden',
    'Synapse': '/synapse',
    'Vault': '/vault',
    'Mimic': '/mimic',
    'Sentry': '/sentry',
    'Alice': '/alice'
  };

  const handleModuleClick = (moduleName) => {
    // console.log('LaunchPage: handleModuleClick called with:', moduleName, { isLoaded, onModuleSelect: !!onModuleSelect });
    
    if (!isLoaded) {
      // console.log('LaunchPage: Click ignored - not loaded yet');
      return;
    }
    
    // console.log('LaunchPage: Processing module click:', moduleName);
    
    // Try the callback first
    if (onModuleSelect) {
      try {
        // console.log('LaunchPage: Calling onModuleSelect...');
        onModuleSelect(moduleName);
        // console.log('LaunchPage: onModuleSelect called successfully');
        return;
      } catch (error) {
        console.error('LaunchPage: Error calling onModuleSelect:', error);
      }
    }
    
    // Fallback to direct navigation
    // console.log('LaunchPage: Using fallback navigation...');
    const route = routeMap[moduleName];
    if (route) {
      // console.log('LaunchPage: Navigating to:', route);
      navigate(route);
    } else {
      console.error('LaunchPage: No route found for module:', moduleName);
    }
  };

  // Convert angle to x,y position in 270° arc avoiding top 90°
  // Standard coordinate system: 0° = right, 90° = bottom, 180° = left, 270° = top
  const getRadialPosition = (angle) => {
    // Convert angle to radians for trigonometric functions
    const radian = (angle * Math.PI) / 180;
    const centerX = 50; // 50% of viewport width
    const centerY = 50; // 50% from top - centered with loading icon
    
    // Fixed radius for all icons to ensure perfect circular spacing
    const radius = 20; // Consistent radius for all positions
    
    // Standard trigonometric positioning
    return {
      x: centerX + (radius * Math.cos(radian)),
      y: centerY + (radius * Math.sin(radian))
    };
  };

  return (
    <div className="launch-page">
      {/* Header Logo - Top Center */}
      <div className="header-logo">
        <img src="/assets/header-logo.png" alt="Header Logo" />
      </div>
      
      {/* System Controls - Top Right */}
      <div className="system-controls">
        <div className="system-control" title="Voice Interface">
          <img src="/assets/Voice.png" alt="Voice" className="system-control-icon" />
          <div className="system-control-label">Voice</div>
        </div>
        <div className="system-control" title="Help & Support" onClick={onShowHelp}>
          <img src="/assets/Help.png" alt="Help" className="system-control-icon" />
          <div className="system-control-label">Help</div>
        </div>
        <div className="system-control" title="Accessibility Options" onClick={onShowAccessibility}>
          <img src="/assets/Accessibility.png" alt="Accessibility" className="system-control-icon" />
          <div className="system-control-label">Accessibility</div>
        </div>
      </div>
      
      {/* Starfield Background */}
      <div className="starfield">
        <div className="stars"></div>
        <div className="stars2"></div>
        <div className="stars3"></div>
      </div>
      
      {/* Animated Background Gradient */}
      <div className="gradient-overlay"></div>
      
      {/* Wave Backlight Effect - Behind text */}
      <div className="wave-backlight"></div>
      
      {/* Central Loading Icon */}
      <div className="loading-container">
        <div className="loading-icon-wrapper">
          <div className="electric-glow"></div>
          <div className="pulse-rings">
            <div className="pulse-ring ring-1"></div>
            <div className="pulse-ring ring-2"></div>
            <div className="pulse-ring ring-3"></div>
          </div>
          <img 
            src="/assets/Loading.png" 
            alt="Loading" 
            className={`loading-icon ${isLoaded ? 'loaded' : ''}`}
          />
        </div>
      </div>
      
      {/* Circular Module Icons */}
      {showIcons && (
        <div className="module-icons">
          {/* console.log('LaunchPage: Rendering module icons', { showIcons, isLoaded, moduleCount: modules.length }) */}
          {modules.map((module, index) => {
            const position = getRadialPosition(module.angle);
            return (
              <div
                key={module.name}
                className={`module-icon ${isLoaded ? 'clickable' : ''}`}
                style={{
                  left: `${position.x}%`,
                  top: `${position.y}%`,
                  animationDelay: `${index * 200}ms`,
                  zIndex: 1000 // Keep the z-index fix
                }}
                onClick={(e) => {
                  // console.log('Module clicked:', module.name);
                  handleModuleClick(module.name);
                }}
              >
                <div className="icon-glow"></div>
                <div className="module-icon-wrapper">
                  <img 
                    src={`/assets/${module.name}.png`} 
                    alt={module.name}
                    className="persona-icon"
                  />
                </div>
                <div className="icon-label">{module.name}</div>
                {isLoaded && (
                  <div className="module-description">{module.description}</div>
                )}
              </div>
            );
          })}
        </div>
      )}
      
      {/* Loading Progress */}
      {!isLoaded && (
        <div className="loading-progress">
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${loadingProgress}%` }}
              ></div>
            </div>
            <div className="progress-text">
              {loadingProgress}%
            </div>
          </div>
          
          <div className={`loading-status ${isLoaded ? 'loaded' : ''}`}>
            {currentStatus}
          </div>
        </div>
      )}
      
      {/* Selection Prompt */}
      {isLoaded && (
        <div className="selection-prompt">
          <div className="welcome-text">
            <h2>HEARTHLINK ONLINE</h2>
            <p>AI Orchestration Platform</p>
            <p className="sub-text">Select a module to begin</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LaunchPage;