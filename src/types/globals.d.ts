declare module '@tauri-apps/api/*';
declare module '@tauri-apps/api/tauri' {
  export function invoke<T = any>(cmd: string, args?: Record<string, any>): Promise<T>;
}
declare module '@tauri-apps/api/notification' {
  export const sendNotification: (options: any) => Promise<void>;
}
declare const SpeechRecognition: any;