


import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Header } from './components/Header';
import { AgentPanel } from './components/AgentPanel';
import { ChatConsolePanel, ChatTarget } from './components/ChatConsolePanel';
// WebCrawlPanel import removed as it's no longer used in Operations Hub
import { InsightsPanel } from './components/InsightsPanel';
import { ContainersPanel } from './components/ContainersPanel';
import { Panel } from './components/Panel';
import { Tabs, Tab } from './components/common/Tabs';
import { DiagnosticsPanel } from './components/DiagnosticsPanel';
import { MemoryInventoryPanel } from './components/MemoryInventoryPanel';
import { CombinedLogsPanel } from './components/CombinedLogsPanel';
import { RecentTasksPanel } from './components/RecentTasksPanel';
import { Toolbar } from './components/Toolbar'; // Import Toolbar
import { Agent, Container, LogEntry, ChatMessage, MemoryItem, Task, InsightDataPoint, LogItemType } from './types'; // WebCrawlSource removed from types import, Added LogItemType
import { RefreshIcon, PlusIcon, BrainIcon } from './constants'; // Added BrainIcon
import { ToastProvider, useToast } from './contexts/ToastContext';
import { Toaster } from './components/common/Toaster';

// Safely get the raw environment variable value at module scope
let moduleLevelImportMetaEnvApp: Record<string, any> | undefined;
try {
  moduleLevelImportMetaEnvApp = (import.meta as any).env;
} catch (e) {
  console.error("[App.tsx Module Scope] Error accessing import.meta.env:", e);
  moduleLevelImportMetaEnvApp = undefined; 
}

// --- START MOVED DEFINITIONS ---
// Define API_BASE_URL early as logToServer might need it.
// Temporarily define GATEKEEPER_PORT_RAW_FOR_LOGGING for logToServer's initial setup.
// This will be properly defined by getEnvVariable later.
const GATEKEEPER_PORT_RAW_FOR_LOGGING = typeof moduleLevelImportMetaEnvApp !== 'undefined' ? moduleLevelImportMetaEnvApp.VITE_GATEKEEPER_HTTP_PORT : undefined;
const DEFAULT_GATEKEEPER_PORT_FOR_LOGGING = '9341'; // Fallback for logging setup

let tempApiBaseUrlForLogging: string;
if (typeof moduleLevelImportMetaEnvApp === 'undefined') {
    tempApiBaseUrlForLogging = `http://localhost:${DEFAULT_GATEKEEPER_PORT_FOR_LOGGING}`;
} else if (typeof GATEKEEPER_PORT_RAW_FOR_LOGGING === 'string' && GATEKEEPER_PORT_RAW_FOR_LOGGING.trim() !== '') {
    tempApiBaseUrlForLogging = `http://localhost:${GATEKEEPER_PORT_RAW_FOR_LOGGING}`;
} else {
    tempApiBaseUrlForLogging = `http://localhost:${DEFAULT_GATEKEEPER_PORT_FOR_LOGGING}`;
}


const logToServer = async (level: 'info' | 'warn' | 'error' | 'debug', message: string, component: string = 'Frontend', context?: any) => {
  try {
    // Use tempApiBaseUrlForLogging as API_BASE_URL might not be initialized yet
    if (!tempApiBaseUrlForLogging.startsWith('http://localhost:')) {
        console.warn(`logToServer: tempApiBaseUrlForLogging seems incorrect: ${tempApiBaseUrlForLogging}. Log might fail.`);
    }
    await fetch(`${tempApiBaseUrlForLogging}/api/log/client`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        level,
        message,
        component,
        timestamp: new Date().toISOString(),
        context,
        clientEnv: { // Add some client env info for debugging
            GATEKEEPER_PORT_RAW: typeof moduleLevelImportMetaEnvApp !== 'undefined' ? moduleLevelImportMetaEnvApp.VITE_GATEKEEPER_HTTP_PORT : 'moduleLevelImportMetaEnvApp_undefined',
            PYTHON_WS_URL_RAW: typeof moduleLevelImportMetaEnvApp !== 'undefined' ? moduleLevelImportMetaEnvApp.VITE_PYTHON_WS_URL : 'moduleLevelImportMetaEnvApp_undefined',
            API_BASE_URL_EFFECTIVE_FOR_LOG: tempApiBaseUrlForLogging, // Log what URL is being used
            // PYTHON_WS_URL will be defined later
            viteMode: typeof moduleLevelImportMetaEnvApp !== 'undefined' ? moduleLevelImportMetaEnvApp.MODE : 'unknown'
        }
      }),
    });
  } catch (error) {
    console.error(`Failed to send log to server (API: ${tempApiBaseUrlForLogging}/api/log/client):`, error);
  }
};

// Helper function to safely get environment variables
function getEnvVariable(rawValue: string | undefined, varName: string, defaultValue: string, component: string = "App.tsx"): string {
  if (typeof moduleLevelImportMetaEnvApp === 'undefined') {
    const message = `Vite 'import.meta.env' was not accessible at module scope. This usually means the app is not being served by Vite's dev server, or the build isn't processed correctly. Ensure you are running 'npm run dev' or serving a Vite build. Falling back to default for ${varName}: '${defaultValue}'.`;
    console.warn(`[${component}] ${message}`);
    // logToServer is now defined, so it can be called.
    logToServer('warn', message, `EnvUtil[${component}]`);
    return defaultValue;
  }
  if (typeof rawValue === 'string' && rawValue.trim() !== '') {
    return rawValue;
  }
  if (typeof rawValue !== 'undefined') {
     const message = `Environment variable ${varName} from import.meta.env was defined but not a non-empty string (value: ${rawValue}). Falling back to default: '${defaultValue}'. Check your .env file.`;
     console.warn(`[${component}] ${message}`);
     logToServer('warn', message, `EnvUtil[${component}]`);
    return defaultValue;
  }
  const message = `Environment variable ${varName} is not defined in your .env file or is empty. Please ensure it's set in a .env file in your project root (e.g., ${varName}=your_value). Falling back to default: '${defaultValue}'.`;
  console.warn(`[${component}] ${message}`);
  logToServer('warn', message, `EnvUtil[${component}]`);
  return defaultValue;
}

const GATEKEEPER_PORT_RAW = typeof moduleLevelImportMetaEnvApp !== 'undefined' ? moduleLevelImportMetaEnvApp.VITE_GATEKEEPER_HTTP_PORT : undefined;
const PYTHON_WS_URL_RAW = typeof moduleLevelImportMetaEnvApp !== 'undefined' ? moduleLevelImportMetaEnvApp.VITE_PYTHON_WS_URL : undefined;

const GATEKEEPER_PORT = getEnvVariable(GATEKEEPER_PORT_RAW, 'VITE_GATEKEEPER_HTTP_PORT', '9341', 'App.tsx_Global');
const API_BASE_URL = `http://localhost:${GATEKEEPER_PORT}`;
const PYTHON_WS_URL = getEnvVariable(PYTHON_WS_URL_RAW, 'VITE_PYTHON_WS_URL', 'ws://localhost:8765', 'App.tsx_Global');
// --- END MOVED DEFINITIONS ---


// Simple Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  { hasError: boolean; error: Error | null; errorInfo: React.ErrorInfo | null }
> {
  constructor(props: { children: React.ReactNode; fallback?: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo });
    console.error("Uncaught error in ErrorBoundary:", error, errorInfo);
    // logToServer is now guaranteed to be defined here due to reordering
    logToServer('error', `ErrorBoundary caught: ${error.message}`, 'ErrorBoundary', { stack: error.stack, info: errorInfo.componentStack });
  }

  render() {
    if (this.state.hasError) {
      const errorDisplay = this.state.error ? this.state.error.toString() : "Unknown error";
      const stackDisplay = this.state.errorInfo ? this.state.errorInfo.componentStack : "No stack trace available";
      
      return this.props.fallback || (
        <div style={{
            position: 'fixed', inset: 0, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            backgroundColor: '#1C1C2E', color: '#E0E0E0', fontFamily: 'Inter, sans-serif', 
            padding: '20px', textAlign: 'center', overflowY: 'auto'
        }}>
            <img src="/header.png" alt="MythologIQ" style={{ height: '40px', marginBottom: '20px' }} />
            <h1 style={{ fontSize: '24px', marginBottom: '10px', color: '#FF3864' }}>Application Error</h1>
            <p style={{ marginBottom: '5px' }}>Nexus Command Console encountered a critical problem.</p>
            <p style={{ fontSize: '14px', color: '#A0A0B0', marginBottom: '20px' }}>
                Please try refreshing the page. If the issue persists, check the browser console (F12) for detailed error messages.
            </p>
            <button
                onClick={() => window.location.reload()}
                style={{
                    padding: '10px 20px', backgroundColor: '#8F48FF', color: 'white', border: 'none',
                    borderRadius: '4px', cursor: 'pointer', fontSize: '16px', marginBottom: '20px'
                }}
            >
                Refresh Page
            </button>
            {/* Display error details if available and in development mode */}
            { (typeof moduleLevelImportMetaEnvApp !== 'undefined' && moduleLevelImportMetaEnvApp.MODE === 'development') && this.state.error && (
                <pre style={{ 
                    marginTop: '20px', textAlign: 'left', background: '#25253A', 
                    padding: '10px', borderRadius: '4px', maxHeight: '300px', 
                    overflowY: 'auto', color: '#FF3864', whiteSpace: 'pre-wrap', wordBreak: 'break-all' 
                }}>
                    Error: {errorDisplay}
                    <hr style={{margin: '10px 0', borderColor: '#3A3A5A'}} />
                    Stack: {stackDisplay}
                </pre>
            )}
        </div>
      );
    }
    return this.props.children;
  }
}

const AppContent: React.FC = () => {
  const { addToast } = useToast();

  const [coreAgents, setCoreAgents] = useState<Agent[]>([]);
  const [browserAgents, setBrowserAgents] = useState<Agent[]>([]);
  const [containers, setContainers] = useState<Container[]>([]);
  const [memoryItems, setMemoryItems] = useState<MemoryItem[]>([]);
  const [eventCommandLogs, setEventCommandLogs] = useState<LogEntry[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<InsightDataPoint[]>([]);
  
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [isLoadingContainers, setIsLoadingContainers] = useState(true);
  const [isLoadingMemoryItems, setIsLoadingMemoryItems] = useState(true);
  const [isLoadingEventLogs, setIsLoadingEventLogs] = useState(true);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [isLoadingSystemMetrics, setIsLoadingSystemMetrics] = useState(true);

  const [pythonWsStatus, setPythonWsStatus] = useState<string>("Connecting...");
  const pythonWsInstanceRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);


   const mockChatMessages: Record<string, ChatMessage[]> = {
    nexus: [
        { id: 'nexus_msg1', sender: 'Nexus Core', avatarUrl: 'https://picsum.photos/seed/nexusChat/40/40', text: 'Nexus Core System Online. Monitoring all agent activity.', timestamp: '09:00:00' },
        { id: 'nexus_msg2', sender: 'System', text: 'Agent "Alden" reported status: Healthy.', timestamp: '09:01:00' },
    ],
    alden: [
        { id: 'alden_msg1', sender: 'Alden', avatarUrl: 'https://picsum.photos/seed/aldenChat/40/40', text: 'Alden interface ready. Awaiting your command.', timestamp: '10:00:01' },
    ],
    gemini: [
        { id: 'gemini_msg1', sender: 'Gemini', avatarUrl: '/brain-avatar.png', text: 'Gemini interface ready. Ask me anything.', timestamp: '10:00:00' },
    ],
    gptReader1: [
        {id: 'reader_msg1', sender: 'GPT-Tab-Reader-01', avatarUrl: 'https://picsum.photos/seed/gptReader1Chat/40/40', text: 'Tab Reader active. Currently observing active tab.', timestamp: '11:00:00'}
    ]
  };

  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [headerStatuses, setHeaderStatuses] = useState({
    bridgeStatus: "Loading...", 
    consoleVerified: false, 
  });

  const [activeChatTargetId, setActiveChatTargetId] = useState<string>('alden');
  const [allMessages, setAllMessages] = useState<Record<string, ChatMessage[]>>(mockChatMessages);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  const connectPythonWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pythonWsInstanceRef.current && pythonWsInstanceRef.current.readyState === WebSocket.OPEN) {
      // Already connected and open, no need to log or toast repeatedly
      if (pythonWsStatus !== 'Connected') setPythonWsStatus("Connected"); // Ensure status is accurate
      return;
    }
    
    if (pythonWsInstanceRef.current) { // If exists but not open, close it before reconnecting
        pythonWsInstanceRef.current.close();
    }
    
    setPythonWsStatus("Connecting...");
    const connectMsg = `Attempting to connect to Python WebSocket at ${PYTHON_WS_URL}...`;
    logToServer('info', connectMsg, 'PythonWSClient', { url: PYTHON_WS_URL });


    const ws = new WebSocket(PYTHON_WS_URL);
    pythonWsInstanceRef.current = ws;

    ws.onopen = () => {
      setPythonWsStatus("Connected");
      logToServer('info', 'Python WebSocket Connected.', 'PythonWSClient', { url: PYTHON_WS_URL });
    };

    ws.onmessage = (event) => {
      const messageContent = event.data.toString().substring(0,100);
      logToServer('info', `Python WebSocket Message Received: ${messageContent}`, 'PythonWSClient', { fullMessage: event.data.toString() });
    };

    ws.onerror = (errorEvent) => { 
      setPythonWsStatus("Error");
      const errorMsg = `Python WebSocket Error. Check console. URL: ${PYTHON_WS_URL}`;
      addToast(errorMsg, "error", 7000);
      logToServer('error', 'Python WebSocket Error.', 'PythonWSClient', { url: PYTHON_WS_URL, event: 'Generic WebSocket Error Event' });
      
      if (reconnectTimeoutRef.current) window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = window.setTimeout(connectPythonWebSocket, 5000);
    };

    ws.onclose = (event) => {
      const closeMsg = `Python WebSocket Disconnected. Code: ${event.code}, Clean: ${event.wasClean}, Reason: ${event.reason || 'N/A'}`;
      if (event.wasClean && event.code === 1000) { 
          setPythonWsStatus("Disconnected");
          logToServer('info', closeMsg, 'PythonWSClient', { url: PYTHON_WS_URL, code: event.code, reason: event.reason, wasClean: event.wasClean });
      } else { 
          setPythonWsStatus("Disconnected (Issue)");
          addToast(`Python WS closed (Code: ${event.code}). Will try to reconnect.`, "warning", 4000);
          logToServer('warn', closeMsg, 'PythonWSClient', { url: PYTHON_WS_URL, code: event.code, reason: event.reason, wasClean: event.wasClean });
      }
      
      if (reconnectTimeoutRef.current) window.clearTimeout(reconnectTimeoutRef.current);
      if (event.code !== 1000) { 
        reconnectTimeoutRef.current = window.setTimeout(connectPythonWebSocket, 5000); 
      }
    };
  }, [addToast, PYTHON_WS_URL, pythonWsStatus]);


  useEffect(() => {
    if (typeof moduleLevelImportMetaEnvApp === 'undefined') {
        logToServer('error', 'CRITICAL: import.meta.env IS UNDEFINED at App mount.', 'AppEnvCheck');
    } else {
        logToServer('info', 'App.tsx mounted. Initial Env Vars:', 'AppEnvCheck', {
            VITE_GATEKEEPER_HTTP_PORT: GATEKEEPER_PORT_RAW,
            VITE_PYTHON_WS_URL: PYTHON_WS_URL_RAW,
            Resolved_API_BASE_URL: API_BASE_URL,
            Resolved_PYTHON_WS_URL: PYTHON_WS_URL,
            ViteMode: moduleLevelImportMetaEnvApp.MODE
        });
    }
    connectPythonWebSocket();
    return () => {
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
      }
      if (pythonWsInstanceRef.current) {
        pythonWsInstanceRef.current.close(1000, "Component unmounting");
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); 


  const fetchAgents = useCallback(async () => {
    setIsLoadingAgents(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/agents`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: Agent[] = await response.json();
      setCoreAgents(data.filter(agent => agent.role === 'Coordinator' || agent.role === 'Router' || agent.role === 'Data Fetcher' || agent.role === 'Local AI' || agent.role === 'Containerized Service' || agent.role === 'AI Language Model'));
      setBrowserAgents(data.filter(agent => agent.role === 'Observer' || agent.role === 'Injector' || agent.role === 'Browser Extension'));
      logToServer('info', 'Agents loaded successfully.', 'FetchAgents');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to fetch agents:", error);
      addToast(`Failed to fetch agents: ${errorMessage}`, "error");
      logToServer('error', `Failed to fetch agents: ${errorMessage}`, 'FetchAgents', { api: `${API_BASE_URL}/api/agents` });
      setCoreAgents([]); setBrowserAgents([]);
    } finally {
      setIsLoadingAgents(false);
    }
  }, [addToast]);

  const fetchContainers = useCallback(async () => {
    setIsLoadingContainers(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/containers`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: Container[] = await response.json();
      setContainers(data);
      logToServer('info', 'Containers loaded successfully.', 'FetchContainers');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to fetch containers:", error);
      addToast(`Failed to fetch containers: ${errorMessage}`, "error");
      logToServer('error', `Failed to fetch containers: ${errorMessage}`, 'FetchContainers', { api: `${API_BASE_URL}/api/containers` });
      setContainers([]);
    } finally {
      setIsLoadingContainers(false);
    }
  }, [addToast]);

  const fetchMemoryItems = useCallback(async () => {
    setIsLoadingMemoryItems(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/memory_items`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json(); 
      setMemoryItems(result.data || []);
      logToServer('info', 'Memory inventory loaded.', 'FetchMemory');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to fetch memory items:", error);
      addToast(`Failed to fetch memory inventory: ${errorMessage}`, "error");
      logToServer('error', `Failed to fetch memory inventory: ${errorMessage}`, 'FetchMemory', { api: `${API_BASE_URL}/api/memory_items` });
      setMemoryItems([]);
    } finally {
      setIsLoadingMemoryItems(false);
    }
  }, [addToast]);

  const fetchEventCommandLogs = useCallback(async () => {
    setIsLoadingEventLogs(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/events`); 
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json(); 
      setEventCommandLogs(result.data || []);
      logToServer('info', 'Activity logs loaded.', 'FetchEvents');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to fetch event logs:", error);
      addToast(`Failed to fetch activity logs: ${errorMessage}`, "error");
      logToServer('error', `Failed to fetch activity logs: ${errorMessage}`, 'FetchEvents', { api: `${API_BASE_URL}/api/events` });
      setEventCommandLogs([]);
    } finally {
      setIsLoadingEventLogs(false);
    }
  }, [addToast]);
  
  const fetchTasks = useCallback(async () => {
    setIsLoadingTasks(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/events?type=task`); 
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json(); 
      const tasksData = (result.data || []).map((event: any) => ({
        id: event.id,
        name: event.message, 
        status: event.details?.status || 'Pending', 
        timestamp: event.timestamp,
      }));
      setTasks(tasksData);
      logToServer('info', 'Recent tasks loaded.', 'FetchTasks');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to fetch tasks:", error);
      addToast(`Failed to fetch recent tasks: ${errorMessage}`, "error");
      logToServer('error', `Failed to fetch tasks: ${errorMessage}`, 'FetchTasks', { api: `${API_BASE_URL}/api/events?type=task` });
      setTasks([]);
    } finally {
      setIsLoadingTasks(false);
    }
  }, [addToast]);

  const fetchSystemMetrics = useCallback(async () => {
    setIsLoadingSystemMetrics(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/system/metrics`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: InsightDataPoint[] = await response.json(); 
      setSystemMetrics(data);
      logToServer('info', 'System metrics loaded.', 'FetchMetrics');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to fetch system metrics:", error);
      addToast(`Failed to fetch system metrics: ${errorMessage}`, "error");
      logToServer('error', `Failed to fetch system metrics: ${errorMessage}`, 'FetchMetrics', { api: `${API_BASE_URL}/api/system/metrics` });
      setSystemMetrics([]);
    } finally {
      setIsLoadingSystemMetrics(false);
    }
  }, [addToast]);

  const fetchGatekeeperSystemStatus = useCallback(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/system/status`);
        if (!response.ok) {
          setHeaderStatuses({ bridgeStatus: "Disconnected", consoleVerified: false });
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setHeaderStatuses({
          bridgeStatus: data.gatekeeperStatus?.toLowerCase() === 'error' ? 'Disconnected' : data.gatekeeperStatus || "Disconnected",
          consoleVerified: data.consoleVerified || false,
        });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error("Failed to fetch Gatekeeper system status:", error);
        setHeaderStatuses({ bridgeStatus: "Disconnected", consoleVerified: false });
        addToast(`Failed to fetch Gatekeeper system status: ${errorMessage}`, "error");
        logToServer('error', `Failed to fetch Gatekeeper system status: ${errorMessage}`, 'FetchSysStatus', { api: `${API_BASE_URL}/api/system/status` });
      }
    }, [addToast]);


  useEffect(() => {
    fetchGatekeeperSystemStatus(); 
    fetchAgents();
    fetchContainers();
    fetchMemoryItems();
    fetchEventCommandLogs();
    fetchTasks();
    fetchSystemMetrics();
    const statusInterval = setInterval(fetchGatekeeperSystemStatus, 30000); 
    return () => clearInterval(statusInterval); 
  }, [addToast, fetchGatekeeperSystemStatus, fetchAgents, fetchContainers, fetchMemoryItems, fetchEventCommandLogs, fetchTasks, fetchSystemMetrics]);
  
  const chatTargets: ChatTarget[] = [
    { id: 'nexus', name: 'Nexus Core', avatarUrl: 'https://picsum.photos/seed/nexusChat/40/40' },
    { id: 'alden', name: 'Alden', avatarUrl: 'https://picsum.photos/seed/aldenChat/40/40' },
    { id: 'gemini', name: 'Gemini', avatarUrl: '/brain-avatar.png', icon: BrainIcon }, 
    ...browserAgents.map(agent => ({ id: agent.id, name: agent.name, avatarUrl: agent.avatarUrl || `https://picsum.photos/seed/${agent.name}/40/40` }))
  ];

  const handleSendMessage = async (text: string, targetId: string) => {
    setIsSendingMessage(true);
    const userMessage: ChatMessage = {
      id: `msg${Date.now()}`,
      sender: 'User',
      avatarUrl: 'https://picsum.photos/seed/currentUser/40/40', 
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    };
    setAllMessages(prev => ({
        ...prev,
        [targetId]: [...(prev[targetId] || []), userMessage]
    }));

    const targetAgent = chatTargets.find(t => t.id === targetId);
    let endpoint = '';
    let payload: Record<string, any> = {};
    let replySenderName = targetAgent?.name || 'System';
    let replyAvatarUrl = targetAgent?.avatarUrl;
    let replyTextContent = `Roger that. Processing for ${replySenderName}: "${text}" (Simulated)`;


    if (targetId === 'gemini') {
        endpoint = `${API_BASE_URL}/api/gemini/generate`;
        payload = { prompt: text };
        replySenderName = 'Gemini';
        replyAvatarUrl = '/brain-avatar.png'; // Gemini specific avatar
        logToServer('info', `Sending message to Gemini. Prompt length: ${text.length}`, 'ChatSend_Gemini');
    } else if (targetId === 'alden') {
        endpoint = `${API_BASE_URL}/api/alden/chat`;
        payload = { prompt: text, userId: 'nexus_console_user' };
        replySenderName = 'Alden';
        // replyAvatarUrl is already set from targetAgent
        logToServer('info', `Sending message to Alden. Prompt length: ${text.length}`, 'ChatSend_Alden');
    } else { // Generic target handling
        if (targetId === 'nexus') {
            replySenderName = "Nexus Dispatch"; 
            replyAvatarUrl = "https://picsum.photos/seed/nexusDispatch/40/40"; 
            replyTextContent = `Message acknowledged by Nexus Dispatch. Routing for processing: "${text}" (Simulated)`;
        }
        // For other browser agents or generic targets, replySenderName and replyAvatarUrl remain as targetAgent's.
        // replyTextContent will use the default if not 'nexus'.

        setTimeout(() => {
            const reply: ChatMessage = {
                id: `resp${Date.now()}`,
                sender: replySenderName,
                avatarUrl: replyAvatarUrl,
                text: replyTextContent,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            };
            setAllMessages(prev => ({
                ...prev,
                [targetId]: [...(prev[targetId] || []), reply]
            }));
            logToServer('info', `Simulated message sent by ${replySenderName} to target ${targetId}. Prompt: ${text}`, 'ChatSend_Simulated');
            setIsSendingMessage(false);
        }, 1000);
        return; 
    }

    // This block is for API calls (Gemini, Alden)
    try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: "Failed to parse error response from server." }));
          logToServer('error', `API request to ${endpoint} failed. Status: ${response.status}`, 'ChatSend_APIError', { error: errorData.error, responseStatus: response.status});
          throw new Error(errorData.error || `API request failed with status ${response.status}`);
        }
        
        const responseData = await response.json();
        // Use the already determined replySenderName and replyAvatarUrl
        const actualReplyText = responseData.text || (typeof responseData === 'string' ? responseData : JSON.stringify(responseData));
        logToServer('info', `Response received from ${replySenderName}. Length: ${actualReplyText.length}`, `ChatRecv_${replySenderName}`);

        const replyMessage: ChatMessage = {
          id: `resp${Date.now()}`,
          sender: replySenderName,
          avatarUrl: replyAvatarUrl, 
          text: actualReplyText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        };
        setAllMessages(prev => ({
            ...prev,
            [targetId]: [...(prev[targetId] || []), replyMessage]
        }));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error(`Failed to send message to ${replySenderName}:`, error);
        addToast(`Error with ${replySenderName}: ${errorMessage}`, 'error');
        logToServer('error', `Error communicating with ${replySenderName}: ${errorMessage}`, `ChatError_${replySenderName}`, { endpoint, payload });
        const errorReply: ChatMessage = {
            id: `err${Date.now()}`,
            sender: 'System', 
            text: `Failed to get response from ${replySenderName}: ${errorMessage}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit'}),
        };
        setAllMessages(prev => ({
            ...prev,
            [targetId]: [...(prev[targetId] || []), errorReply]
        }));
      } finally {
        setIsSendingMessage(false);
      }
  };

  const handlePopout = (panelTitle: string) => {
    console.log(`Popout requested for: ${panelTitle}`);
    addToast(`Popout action for "${panelTitle}" triggered. (Feature not fully implemented)`, 'info');
    logToServer('info', `Popout action triggered for ${panelTitle}`, 'UIPopout');
  };

  const operationsHubTabs: Tab[] = [
    { title: 'Activity & System Logs', content: <CombinedLogsPanel initialEventCommandLogs={eventCommandLogs} /> },
    { title: 'Insights', content: <InsightsPanel initialMetrics={systemMetrics} isLoading={isLoadingSystemMetrics} onRefresh={fetchSystemMetrics} onPopoutClick={() => handlePopout('Insights Tab Content')} /> },
    { title: 'Recent Tasks', content: <RecentTasksPanel initialTasks={tasks} isLoading={isLoadingTasks} onRefresh={fetchTasks} /> }, 
  ];


  return (
      <div className="h-full bg-[var(--brand-primary-bg)] text-[var(--brand-text-primary)] flex flex-col">
        <Header 
          wsStatus={pythonWsStatus}
          onRefreshPythonWs={connectPythonWebSocket}
          bridgeStatus={headerStatuses.bridgeStatus}
          isConsoleVerified={headerStatuses.consoleVerified}
          onToggleDiagnostics={() => setShowDiagnostics(prev => !prev)}
          onRefreshSystemStatus={fetchGatekeeperSystemStatus} 
        />
        {showDiagnostics && <DiagnosticsPanel onClose={() => setShowDiagnostics(false)} onRefreshSystemStatus={fetchGatekeeperSystemStatus} />}
        <main className="p-2 sm:p-4 flex-grow overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
            {/* Column 1 */}
            <div className="lg:col-span-3 flex flex-col gap-4 overflow-y-auto">
              <AgentPanel title="Core Agents" agents={isLoadingAgents ? [] : coreAgents} panelWrapperClassName="flex-shrink-0" />
              {isLoadingAgents && coreAgents.length === 0 && <p className="text-center text-sm text-[var(--brand-text-secondary)]">Loading agents...</p>}
              <AgentPanel 
                title="Browser Agents" 
                agents={isLoadingAgents ? [] : browserAgents} 
                headerControls={
                  <div className="flex items-center gap-2">
                    <button aria-label="Add browser agent" className="p-1 text-[var(--brand-text-secondary)] hover:text-[var(--brand-text-primary)]"><PlusIcon /></button>
                    <button aria-label="Refresh browser agents" onClick={fetchAgents} className="p-1 text-[var(--brand-text-secondary)] hover:text-[var(--brand-text-primary)]"><RefreshIcon className={isLoadingAgents ? 'animate-spin' : ''}/></button>
                  </div>
                }
                panelWrapperClassName="flex-shrink-0"
              />
              {isLoadingAgents && browserAgents.length === 0 && <p className="text-center text-sm text-[var(--brand-text-secondary)]">Loading browser agents...</p>}
              <MemoryInventoryPanel 
                  items={isLoadingMemoryItems ? [] : memoryItems} 
                  panelWrapperClassName="flex-1 min-h-[200px]"
                  onPopoutClick={() => handlePopout('Memory Inventory')}
              />
               {isLoadingMemoryItems && memoryItems.length === 0 && <p className="text-center text-sm text-[var(--brand-text-secondary)]">Loading memory items...</p>}
            </div>

            {/* Column 2 - Chat Console & Toolbar */}
            <div className="lg:col-span-4 flex flex-col gap-0 overflow-hidden"> 
              <ChatConsolePanel 
                  messages={allMessages[activeChatTargetId] || []}
                  chatTargets={chatTargets}
                  activeChatTargetId={activeChatTargetId}
                  onTargetChange={setActiveChatTargetId}
                  onSendMessage={handleSendMessage}
                  panelWrapperClassName="flex-1 min-h-0" 
                  isSendingMessage={isSendingMessage}
              />
              <Toolbar /> 
            </div>

            {/* Column 3 - Standalone Containers & Operations Hub */}
            <div className="lg:col-span-5 flex flex-col gap-4 overflow-y-auto">
              <ContainersPanel 
                  initialContainers={isLoadingContainers ? [] : containers}
                  panelWrapperClassName="flex-shrink-0"
                  onPopoutClick={() => handlePopout('Containers')}
                  isLoading={isLoadingContainers}
                  onRefresh={fetchContainers}
              />
               {isLoadingContainers && containers.length === 0 && <p className="text-center text-sm text-[var(--brand-text-secondary)]">Loading containers...</p>}
              <Panel 
                  title="Operations Hub" 
                  className="flex-1 min-h-[300px] flex flex-col"
                  contentClassName="flex-grow p-0" 
                  onPopoutClick={() => handlePopout('Operations Hub')}
              >
                  <Tabs tabs={operationsHubTabs} />
              </Panel>
            </div>
          </div>
        </main>
        <Toaster />
         { GATEKEEPER_PORT_RAW === undefined && typeof moduleLevelImportMetaEnvApp === 'object' && (
            <div style={{ position: 'fixed', bottom: '5px', left: '5px', backgroundColor: 'rgba(255,165,0,0.7)', padding: '3px 8px', borderRadius: '3px', fontSize: '10px', color: 'black', zIndex: 1000}}>
                Warning: VITE_GATEKEEPER_HTTP_PORT not set. Defaulting to {GATEKEEPER_PORT}.
            </div>
        )}
         { PYTHON_WS_URL_RAW === undefined && typeof moduleLevelImportMetaEnvApp === 'object' && (
            <div style={{ position: 'fixed', bottom: '25px', left: '5px', backgroundColor: 'rgba(255,165,0,0.7)', padding: '3px 8px', borderRadius: '3px', fontSize: '10px', color: 'black', zIndex: 1000}}>
                Warning: VITE_PYTHON_WS_URL not set. Defaulting to {PYTHON_WS_URL}.
            </div>
        )}
      </div>
  );
};

const App: React.FC = () => {
  return (
  <ErrorBoundary fallback={
    <div style={{
        position: 'fixed', inset: 0, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        backgroundColor: '#1C1C2E', color: '#E0E0E0', fontFamily: 'Inter, sans-serif', 
        padding: '20px', textAlign: 'center', overflowY: 'auto'
    }}>
        <img src="/header.png" alt="MythologIQ" style={{ height: '40px', marginBottom: '20px' }} />
        <h1 style={{ fontSize: '24px', marginBottom: '10px', color: '#FF3864' }}>Application Error</h1>
        <p style={{ marginBottom: '5px' }}>Nexus Command Console encountered a critical problem.</p>
        <p style={{ fontSize: '14px', color: '#A0A0B0', marginBottom: '20px' }}>
            Please try refreshing the page. If the issue persists, check the browser console (F12) for detailed error messages.
        </p>
        <button 
            onClick={() => window.location.reload()}
            style={{
                padding: '10px 20px', backgroundColor: '#8F48FF', color: 'white', border: 'none', 
                borderRadius: '4px', cursor: 'pointer', fontSize: '16px', marginBottom: '20px'
            }}
        >
            Refresh Page
        </button>
    </div>
  }>
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  </ErrorBoundary>
  );
};

export default App;
