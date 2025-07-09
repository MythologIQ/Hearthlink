export enum LogItemType {
  Memory = 'Memory',
  Event = 'Event',
  Command = 'Command',
}

export interface LogEntry {
  id: string;
  type: LogItemType;
  text: string;
  timestamp: string;
  status?: 'REWIND' | 'exited' | string;
}

export interface Agent {
  id: string;
  name: string;
  status: string; // e.g., "Online", "Processing", "Error"
  avatarUrl?: string; // URL to placeholder image
  role?: string; // Added for Phase 1 - Active Config Panel
}

export interface ChatMessage {
  id: string;
  sender: string; // "Alden" or "System"
  avatarUrl?: string;
  text: string;
  timestamp: string;
}

export interface WebCrawlSource {
  id: string;
  name: string;
  url: string;
}

export enum ContainerStatus {
  Running = 'RUNNING',
  Exited = 'exited',
  Stopped = 'stopped',
}

export interface Container {
  id: string;
  name: string;
  status: ContainerStatus;
  image: string;
}

export interface InsightDataPoint {
  name: string; // Typically a date or time string
  value: number;
}

export enum MemorySource {
  AldenRAG = "Alden RAG",
  MCPWebcrawl = "MCP Webcrawl"
}

export interface MemoryItem {
  id: string;
  source: MemorySource;
  type: string; // e.g., "Text Chunk", "Document Embedding", "Web Page Summary"
  description: string; // Short description or content snippet
  size: string; // e.g., "128 vectors", "2.5 MB", "15 pages"
  timestamp: string; // ISO string or human-readable
  tags?: string[];
}

// Added for RecentTasksPanel (Phase 1)
export interface Task {
  id: string;
  name: string;
  status: 'Pending' | 'In Progress' | 'Completed' | 'Failed';
  timestamp: string;
}


// --- Toast Notification System Types (Segment 1) ---
export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastMessage {
  id: string;
  message: string;
  type: ToastType;
  duration?: number; // Optional duration in ms
}

export interface ToastContextType {
  toasts: ToastMessage[];
  addToast: (message: string, type: ToastType, duration?: number) => void;
  removeToast: (id: string) => void;
}
// --- End Toast Notification System Types ---