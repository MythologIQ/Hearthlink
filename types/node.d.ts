// Manual Node.js type declarations to resolve TypeScript errors

declare global {
  var __dirname: string;
  var __filename: string;
  var process: {
    env: { [key: string]: string | undefined };
    platform: string;
    arch: string;
    version: string;
    versions: { [key: string]: string };
    argv: string[];
    execPath: string;
    cwd(): string;
    exit(code?: number): never;
    memoryUsage(): {
      rss: number;
      heapTotal: number;
      heapUsed: number;
      external: number;
      arrayBuffers: number;
    };
    cpuUsage(previousValue?: { user: number; system: number }): {
      user: number;
      system: number;
    };
    uptime(): number;
  };
  var require: (id: string) => any;
  var module: {
    exports: any;
    require: (id: string) => any;
    id: string;
    filename: string;
    loaded: boolean;
    parent: any;
    children: any[];
  };
  var exports: any;
  
  // Error constructor extensions
  interface ErrorConstructor {
    captureStackTrace(targetObject: any, constructorOpt?: any): void;
  }
  
  // Timer functions
  function setTimeout(callback: (...args: any[]) => void, ms?: number, ...args: any[]): NodeJS.Timeout;
  function clearTimeout(timeoutId: NodeJS.Timeout): void;
  function setInterval(callback: (...args: any[]) => void, ms?: number, ...args: any[]): NodeJS.Timer;
  function clearInterval(intervalId: NodeJS.Timer): void;
  function setImmediate(callback: (...args: any[]) => void, ...args: any[]): NodeJS.Immediate;
  function clearImmediate(immediateId: NodeJS.Immediate): void;

  namespace NodeJS {
    interface ProcessEnv {
      [key: string]: string | undefined;
    }
    interface Global {
      [key: string]: any;
    }
    interface Timer {
      hasRef(): boolean;
      ref(): this;
      unref(): this;
    }
    interface Timeout extends Timer {
      close(): void;
    }
    interface Immediate extends Timer {
      close(): void;
    }
    type Platform = 'aix' | 'android' | 'darwin' | 'freebsd' | 'haiku' | 'linux' | 'openbsd' | 'sunos' | 'win32' | 'cygwin' | 'netbsd';
  }
}

// Module declarations for Node.js modules
declare module 'fs' {
  export function readFileSync(path: string, encoding?: string): string | Buffer;
  export function writeFileSync(path: string, data: string | Buffer): void;
  export function existsSync(path: string): boolean;
  export function mkdirSync(path: string, options?: { recursive?: boolean }): void;
  export const promises: {
    readFile(path: string, encoding?: string): Promise<string | Buffer>;
    writeFile(path: string, data: string | Buffer): Promise<void>;
    mkdir(path: string, options?: { recursive?: boolean }): Promise<void>;
    access(path: string): Promise<void>;
  };
}

declare module 'fs/promises' {
  export function readFile(path: string, encoding?: string): Promise<string | Buffer>;
  export function writeFile(path: string, data: string | Buffer): Promise<void>;
  export function mkdir(path: string, options?: { recursive?: boolean }): Promise<void>;
  export function access(path: string): Promise<void>;
}

declare module 'path' {
  export function join(...paths: string[]): string;
  export function resolve(...paths: string[]): string;
  export function dirname(path: string): string;
  export function basename(path: string, ext?: string): string;
  export function extname(path: string): string;
  export function normalize(path: string): string;
  export function isAbsolute(path: string): boolean;
  export const sep: string;
  export const delimiter: string;
}

declare module 'http' {
  export interface IncomingMessage {
    url?: string;
    method?: string;
    headers: { [key: string]: string | string[] | undefined };
    on(event: string, listener: (...args: any[]) => void): this;
  }
  
  export interface ServerResponse {
    writeHead(statusCode: number, headers?: { [key: string]: string }): void;
    write(chunk: string | Buffer): void;
    end(data?: string | Buffer): void;
  }
  
  export interface Server {
    listen(port: number, callback?: () => void): this;
    close(callback?: () => void): this;
  }
  
  export function createServer(requestListener?: (req: IncomingMessage, res: ServerResponse) => void): Server;
}

declare module 'events' {
  export class EventEmitter {
    on(event: string, listener: (...args: any[]) => void): this;
    once(event: string, listener: (...args: any[]) => void): this;
    emit(event: string, ...args: any[]): boolean;
    removeListener(event: string, listener: (...args: any[]) => void): this;
    removeAllListeners(event?: string): this;
  }
}

declare module 'electron' {
  export interface BrowserWindow {
    loadURL(url: string): Promise<void>;
    webContents: {
      openDevTools(): void;
      send(channel: string, ...args: any[]): void;
      on(event: string, listener: (...args: any[]) => void): void;
    };
    on(event: string, listener: (...args: any[]) => void): void;
    show(): void;
    hide(): void;
    close(): void;
  }

  export interface App {
    whenReady(): Promise<void>;
    on(event: string, listener: (...args: any[]) => void): void;
    quit(): void;
    getPath(name: string): string;
  }

  export interface IpcMain {
    handle(channel: string, listener: (event: any, ...args: any[]) => any): void;
    on(channel: string, listener: (event: any, ...args: any[]) => void): void;
  }

  export interface IpcRenderer {
    invoke(channel: string, ...args: any[]): Promise<any>;
    send(channel: string, ...args: any[]): void;
    on(channel: string, listener: (event: any, ...args: any[]) => void): void;
  }

  export const app: App;
  export const ipcMain: IpcMain;
  export const ipcRenderer: IpcRenderer;
  export const BrowserWindow: {
    new (options?: any): BrowserWindow;
  };
}

export {};