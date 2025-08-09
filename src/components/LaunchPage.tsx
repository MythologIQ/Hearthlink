import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Power, Settings, Database, Shield, Bot, Eye, User } from 'lucide-react';

interface LoadingStep {
  progress: number;
  status: string;
  delay: number;
}

interface Module {
  name: string;
  angle: number;
  description: string;
  icon: any;
}

interface LaunchPageProps {
  onModuleSelect?: (moduleName: string) => void;
}

const LaunchPage: React.FC<LaunchPageProps> = ({ onModuleSelect }) => {
  const navigate = useNavigate();
  const [loadingProgress, setLoadingProgress] = useState<number>(0);
  const [currentStatus, setCurrentStatus] = useState<string>('Initializing Hearthlink...');
  const [isLoaded, setIsLoaded] = useState<boolean>(false);
  const [showIcons, setShowIcons] = useState<boolean>(false);

  const loadingSteps: LoadingStep[] = [
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
      setTimeout(() => setShowIcons(true), 1500);
      
      for (let i = 0; i < loadingSteps.length; i++) {
        const step = loadingSteps[i];
        if (!step) continue; // TypeScript safety check
        
        await new Promise(resolve => setTimeout(resolve, step.delay));
        
        setLoadingProgress(step.progress);
        setCurrentStatus(step.status);
        
        if (step.progress === 100) {
          setTimeout(() => {
            setIsLoaded(true);
          }, 500);
        }
      }
    };
    
    runLoadingSequence();
  }, []);

  // Module definitions with Lucide icons
  const modules: Module[] = [
    { name: 'Core', angle: 0, description: 'AI Orchestration Engine', icon: Settings },
    { name: 'Alden', angle: 51.4, description: 'Primary AI Persona', icon: Bot },
    { name: 'Synapse', angle: 102.8, description: 'Security Gateway', icon: Shield },
    { name: 'Vault', angle: 154.3, description: 'Memory Repository', icon: Database },
    { name: 'Mimic', angle: 205.7, description: 'Adaptive Intelligence', icon: Power },
    { name: 'Sentry', angle: 257.1, description: 'System Monitor', icon: Eye },
    { name: 'Alice', angle: 308.6, description: 'Assistant Persona', icon: User }
  ];

  // Route mapping for navigation
  const routeMap: Record<string, string> = {
    'Core': '/core',
    'Alden': '/alden',
    'Synapse': '/synapse',
    'Vault': '/vault',
    'Mimic': '/mimic',
    'Sentry': '/sentry',
    'Alice': '/alice'
  };

  const handleModuleClick = (moduleName: string) => {
    if (isLoaded) {
      const route = routeMap[moduleName];
      if (route) {
        navigate(route);
      } else {
        // Fallback to legacy handler if route not found
        if (onModuleSelect) {
          onModuleSelect(moduleName);
        }
      }
    }
  };

  // Convert angle to x,y position on circle - INCREASED RADIUS TO PREVENT OVERLAP
  const getCircularPosition = (angle: number, radius: number = 220) => {
    const radian = (angle * Math.PI) / 180;
    const centerX = 50; // 50% of viewport width
    const centerY = 50; // 50% of viewport height
    const radiusX = radius * 0.15; // Percentage of viewport width
    const radiusY = radius * 0.15; // Percentage of viewport height
    
    return {
      x: centerX + (radiusX * Math.cos(radian)),
      y: centerY + (radiusY * Math.sin(radian))
    };
  };

  return (
    <div className="fixed inset-0 w-screen h-screen overflow-auto bg-cover bg-center bg-no-repeat font-orbitron"
         style={{ backgroundImage: 'url("/assets/obsidian-bg.png")' }}>
      
      {/* Starfield Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 opacity-80"
             style={{ backgroundImage: 'url("/assets/stars.png")', backgroundSize: 'cover', backgroundPosition: 'center' }} />
        
        {/* Animated starfield layers */}
        <div className="absolute inset-0 animate-starfield">
          <div className="absolute inset-0 bg-gradient-to-br from-starcraft-blue/10 via-transparent to-starcraft-gold/5" />
        </div>
      </div>

      {/* MythologIQ Header Logo - CENTERED */}
      <div className="absolute top-[5%] left-1/2 transform -translate-x-1/2 z-10 text-center">
        <img src="/assets/header-logo.png" alt="MythologIQ" 
             className="h-20 w-auto filter drop-shadow-lg animate-pulse" 
             style={{ filter: 'drop-shadow(0 0 10px rgba(251, 191, 36, 0.6))' }} />
      </div>
      
      {/* Central Loading Icon */}
      <div className="absolute inset-0 flex items-center justify-center z-10">
        <div className="relative w-48 h-48 flex items-center justify-center">
          
          {/* Electric glow background */}
          <div className="absolute inset-0 rounded-full bg-gradient-radial from-starcraft-blue/30 via-starcraft-blue/10 to-transparent animate-pulse-glow" />
          
          {/* Pulse rings */}
          <div className="absolute inset-0">
            <div className="absolute w-[120%] h-[120%] -top-[10%] -left-[10%] rounded-full border-2 border-starcraft-blue/30 animate-ping" 
                 style={{ animationDelay: '0s', animationDuration: '3s' }} />
            <div className="absolute w-[140%] h-[140%] -top-[20%] -left-[20%] rounded-full border-2 border-starcraft-blue/20 animate-ping" 
                 style={{ animationDelay: '1s', animationDuration: '3s' }} />
            <div className="absolute w-[160%] h-[160%] -top-[30%] -left-[30%] rounded-full border-2 border-starcraft-blue/10 animate-ping" 
                 style={{ animationDelay: '2s', animationDuration: '3s' }} />
          </div>
          
          {/* Loading icon */}
          <Loader2 
            className={`w-24 h-24 text-starcraft-blue animate-spin transition-opacity duration-500 ${isLoaded ? 'opacity-30' : 'opacity-100'}`}
            style={{ 
              filter: 'drop-shadow(0 0 20px rgba(34, 211, 238, 0.8)) drop-shadow(0 0 40px rgba(34, 211, 238, 0.6))' 
            }}
          />
        </div>
      </div>
      
      {/* Circular Module Icons */}
      {showIcons && (
        <div className="absolute inset-0 w-full h-full pointer-events-none">
          {modules.map((module, index) => {
            const position = getCircularPosition(module.angle);
            const IconComponent = module.icon;
            
            return (
              <div
                key={module.name}
                className={`absolute flex flex-col items-center animate-float ${isLoaded ? 'pointer-events-auto cursor-pointer' : ''} 
                           transition-all duration-300 hover:scale-110`}
                style={{
                  left: `${position.x}%`,
                  top: `${position.y}%`,
                  animationDelay: `${index * 200}ms`,
                  transform: 'translate(-50%, -50%)'
                }}
                onClick={() => handleModuleClick(module.name)}
              >
                {/* Icon glow */}
                <div className="absolute w-20 h-20 rounded-full bg-gradient-radial from-starcraft-gold/20 via-starcraft-gold/10 to-transparent 
                               animate-pulse group-hover:scale-140 group-hover:opacity-100 transition-all duration-300" />
                
                {/* Module icon */}
                <div className="relative z-10 w-16 h-16 rounded-full border-2 border-starcraft-gold/50 bg-starcraft-dark/80 
                               flex items-center justify-center backdrop-blur-sm
                               hover:border-starcraft-gold hover:bg-starcraft-gold/10 hover:shadow-lg hover:shadow-starcraft-gold/50
                               transition-all duration-300">
                  <IconComponent className="w-8 h-8 text-starcraft-gold" />
                </div>
                
                {/* Module label */}
                <div className="mt-2 text-xs font-bold text-starcraft-gold text-center tracking-wider uppercase
                               text-shadow-sm opacity-90 hover:opacity-100 transition-opacity duration-300">
                  {module.name}
                </div>
                
                {/* Module description - appears on hover when loaded */}
                {isLoaded && (
                  <div className="mt-1 text-xs text-slate-300 text-center max-w-30 leading-tight
                                 opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0
                                 transition-all duration-300">
                    {module.description}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
      
      {/* Loading Progress */}
      {!isLoaded && (
        <div className="absolute bottom-[15%] left-1/2 transform -translate-x-1/2 text-center z-10">
          <div className="flex items-center gap-4 mb-5">
            <div className="w-80 h-1 bg-starcraft-dark/80 rounded-full overflow-hidden border border-starcraft-blue/30">
              <div 
                className="h-full bg-gradient-to-r from-starcraft-blue to-cyan-400 rounded-full transition-all duration-300 shadow-lg shadow-starcraft-blue/60"
                style={{ width: `${loadingProgress}%` }}
              />
            </div>
            <div className="text-lg font-bold text-starcraft-blue min-w-12 text-shadow">
              {loadingProgress}%
            </div>
          </div>
          
          <div className={`text-base text-slate-300 tracking-wide animate-pulse transition-opacity duration-500 ${isLoaded ? 'opacity-30' : 'opacity-100'}`}>
            {currentStatus}
          </div>
        </div>
      )}
      
      {/* Selection Prompt */}
      {isLoaded && (
        <div className="absolute bottom-[15%] left-1/2 transform -translate-x-1/2 text-center z-20 animate-fadeIn">
          <div className="space-y-2">
            <h2 className="text-4xl font-light text-starcraft-blue tracking-wide
                           text-shadow-lg animate-pulse">
              HEARTHLINK ONLINE
            </h2>
            <p className="text-xl text-slate-300 tracking-wider">
              Select a module to begin
            </p>
          </div>
        </div>
      )}
      
      {/* Hearthlink Logo */}
      <div className="absolute bottom-[5%] right-[5%] z-10">
        <img src="/assets/hearthlink-logo.png" alt="Hearthlink" 
             className="w-30 h-auto opacity-80 animate-float filter drop-shadow-md" />
      </div>
    </div>
  );
};

export default LaunchPage;