// Manual React type declarations to resolve TypeScript errors

declare module 'react/jsx-runtime' {
  export namespace JSX {
    interface Element {
      type: any;
      props: any;
      key: any;
    }
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
  export function jsx(type: any, props: any, key?: any): JSX.Element;
  export function jsxs(type: any, props: any, key?: any): JSX.Element;
}

declare module 'react' {
  import * as CSS from 'csstype';
  
  // Basic React types
  export interface ComponentProps<T> {
    [key: string]: any;
  }

  export interface ReactElement<P = any, T extends string | React.ComponentType<any> = string | React.ComponentType<any>> {
    type: T;
    props: P;
    key: React.Key | null;
  }

  export interface ReactNode {
    [key: string]: any;
  }

  export type Key = string | number;
  export type Ref<T> = { current: T | null } | ((instance: T | null) => void) | null;

  // Component types
  export interface FunctionComponent<P = {}> {
    (props: P & { children?: ReactNode }): ReactElement | null;
    displayName?: string;
  }

  export interface ComponentClass<P = {}, S = any> {
    new (props: P): Component<P, S>;
  }

  export type ComponentType<P = {}> = ComponentClass<P> | FunctionComponent<P>;
  export type FC<P = {}> = FunctionComponent<P>;

  // Component class
  export class Component<P = {}, S = {}> {
    props: Readonly<P>;
    state: Readonly<S>;
    context: any;
    refs: { [key: string]: ReactInstance };
    constructor(props: P);
    setState<K extends keyof S>(
      state: ((prevState: Readonly<S>, props: Readonly<P>) => (Pick<S, K> | S | null)) | (Pick<S, K> | S | null),
      callback?: () => void
    ): void;
    forceUpdate(callback?: () => void): void;
    render(): ReactNode;
    componentDidMount?(): void;
    componentWillUnmount?(): void;
    componentDidUpdate?(prevProps: Readonly<P>, prevState: Readonly<S>, snapshot?: any): void;
  }

  // Hook types
  export function useState<S>(initialState: S | (() => S)): [S, (value: S | ((prevState: S) => S)) => void];
  export function useState<S = undefined>(): [S | undefined, (value: S | ((prevState: S | undefined) => S)) => void];

  export function useEffect(effect: () => (void | (() => void)), deps?: readonly any[]): void;
  export function useContext<T>(context: Context<T>): T;
  export function useReducer<R extends (state: any, action: any) => any>(
    reducer: R,
    initialState: Parameters<R>[0],
    init?: (initial: Parameters<R>[0]) => Parameters<R>[0]
  ): [Parameters<R>[0], (action: Parameters<R>[1]) => void];

  export function useMemo<T>(factory: () => T, deps: readonly any[] | undefined): T;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: readonly any[]): T;
  export function useRef<T>(initialValue: T): { current: T };
  export function useRef<T>(initialValue: T | null): { current: T | null };
  export function useRef<T = undefined>(): { current: T | undefined };

  // Context
  export interface Context<T> {
    Provider: ComponentType<{ value: T; children?: ReactNode }>;
    Consumer: ComponentType<{ children: (value: T) => ReactNode }>;
    displayName?: string;
  }
  export function createContext<T>(defaultValue: T): Context<T>;

  // Events
  export interface SyntheticEvent<T = Element> {
    currentTarget: T;
    target: EventTarget & T;
    preventDefault(): void;
    stopPropagation(): void;
  }

  export interface MouseEvent<T = Element> extends SyntheticEvent<T> {
    button: number;
    buttons: number;
    clientX: number;
    clientY: number;
    ctrlKey: boolean;
    shiftKey: boolean;
    altKey: boolean;
    metaKey: boolean;
  }

  export interface ChangeEvent<T = Element> extends SyntheticEvent<T> {
    target: EventTarget & T;
  }

  export interface FormEvent<T = Element> extends SyntheticEvent<T> {}

  // HTML attributes
  export interface HTMLAttributes<T> {
    className?: string;
    id?: string;
    style?: CSS.Properties;
    onClick?: (event: MouseEvent<T>) => void;
    onChange?: (event: ChangeEvent<T>) => void;
    onSubmit?: (event: FormEvent<T>) => void;
    children?: ReactNode;
    [key: string]: any;
  }

  export interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
    value?: string | number;
    type?: string;
    placeholder?: string;
    disabled?: boolean;
    checked?: boolean;
  }

  export interface ButtonHTMLAttributes<T> extends HTMLAttributes<T> {
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
  }

  // JSX
  export namespace JSX {
    interface Element extends ReactElement<any, any> {}
    interface ElementClass extends Component<any> {}
    interface ElementAttributesProperty {
      props: {};
    }
    interface ElementChildrenAttribute {
      children: {};
    }

    interface IntrinsicElements {
      div: HTMLAttributes<HTMLDivElement>;
      span: HTMLAttributes<HTMLSpanElement>;
      p: HTMLAttributes<HTMLParagraphElement>;
      h1: HTMLAttributes<HTMLHeadingElement>;
      h2: HTMLAttributes<HTMLHeadingElement>;
      h3: HTMLAttributes<HTMLHeadingElement>;
      h4: HTMLAttributes<HTMLHeadingElement>;
      h5: HTMLAttributes<HTMLHeadingElement>;
      h6: HTMLAttributes<HTMLHeadingElement>;
      button: ButtonHTMLAttributes<HTMLButtonElement>;
      input: InputHTMLAttributes<HTMLInputElement>;
      form: HTMLAttributes<HTMLFormElement>;
      label: HTMLAttributes<HTMLLabelElement>;
      select: HTMLAttributes<HTMLSelectElement>;
      option: HTMLAttributes<HTMLOptionElement>;
      textarea: HTMLAttributes<HTMLTextAreaElement>;
      img: HTMLAttributes<HTMLImageElement>;
      a: HTMLAttributes<HTMLAnchorElement>;
      ul: HTMLAttributes<HTMLUListElement>;
      ol: HTMLAttributes<HTMLOListElement>;
      li: HTMLAttributes<HTMLLIElement>;
      nav: HTMLAttributes<HTMLNavElement>;
      header: HTMLAttributes<HTMLElement>;
      main: HTMLAttributes<HTMLElement>;
      section: HTMLAttributes<HTMLElement>;
      article: HTMLAttributes<HTMLElement>;
      aside: HTMLAttributes<HTMLElement>;
      footer: HTMLAttributes<HTMLElement>;
      [elemName: string]: any;
    }
  }

  // Default export
  const React: {
    Component: typeof Component;
    useState: typeof useState;
    useEffect: typeof useEffect;
    useContext: typeof useContext;
    useMemo: typeof useMemo;
    useCallback: typeof useCallback;
    useRef: typeof useRef;
    createContext: typeof createContext;
    FC: typeof FunctionComponent;
    ReactNode: ReactNode;
    ReactElement: ReactElement;
  };

  export default React;
  
  // Global React namespace for legacy code
  global {
    namespace React {
      type FC<P = {}> = FunctionComponent<P>;
      type ReactNode = any;
      type ReactElement = any;
      type CSSProperties = any;
      interface MouseEvent<T = Element> extends SyntheticEvent<T> {
        button: number;
        clientX: number;
        clientY: number;
        ctrlKey: boolean;
        shiftKey: boolean;
        altKey: boolean;
        metaKey: boolean;
      }
      interface ChangeEvent<T = Element> extends SyntheticEvent<T> {
        target: EventTarget & T;
      }
      interface SyntheticEvent<T = Element> {
        currentTarget: T;
        target: EventTarget & T;
        preventDefault(): void;
        stopPropagation(): void;
      }
    }
  }
}

declare module 'react-router-dom' {
  import { ComponentType, ReactNode } from 'react';

  export interface RouteProps {
    path?: string;
    element?: ReactNode;
    children?: ReactNode;
  }

  export interface LinkProps {
    to: string;
    children?: ReactNode;
    className?: string;
    style?: React.CSSProperties;
    onClick?: (event: React.MouseEvent) => void;
  }

  export interface NavigateOptions {
    replace?: boolean;
    state?: any;
  }

  export function useNavigate(): (to: string, options?: NavigateOptions) => void;
  export function useLocation(): { pathname: string; search: string; hash: string; state: any };
  export function useParams<T extends Record<string, string>>(): T;

  export const BrowserRouter: ComponentType<{ children?: ReactNode }>;
  export const Routes: ComponentType<{ children?: ReactNode }>;
  export const Route: ComponentType<RouteProps>;
  export const Link: ComponentType<LinkProps>;
  export const Navigate: ComponentType<{ to: string; replace?: boolean }>;
}

declare module 'lucide-react' {
  import { ComponentType } from 'react';

  interface LucideProps {
    size?: number | string;
    color?: string;
    strokeWidth?: number | string;
    className?: string;
    style?: React.CSSProperties;
  }

  // Missing icons that were causing errors
  export const Loader2: ComponentType<LucideProps>;
  export const Bot: ComponentType<LucideProps>;
  export const AlertTriangle: ComponentType<LucideProps>;
  export const CheckCircle: ComponentType<LucideProps>;
  export const XCircle: ComponentType<LucideProps>;
  export const AlertCircle: ComponentType<LucideProps>;
  
  export const Home: ComponentType<LucideProps>;
  export const Settings: ComponentType<LucideProps>;
  export const User: ComponentType<LucideProps>;
  export const Search: ComponentType<LucideProps>;
  export const Menu: ComponentType<LucideProps>;
  export const X: ComponentType<LucideProps>;
  export const ChevronLeft: ComponentType<LucideProps>;
  export const ChevronRight: ComponentType<LucideProps>;
  export const ChevronDown: ComponentType<LucideProps>;
  export const ChevronUp: ComponentType<LucideProps>;
  export const Plus: ComponentType<LucideProps>;
  export const Minus: ComponentType<LucideProps>;
  export const Edit: ComponentType<LucideProps>;
  export const Trash: ComponentType<LucideProps>;
  export const Save: ComponentType<LucideProps>;
  export const Download: ComponentType<LucideProps>;
  export const Upload: ComponentType<LucideProps>;
  export const Play: ComponentType<LucideProps>;
  export const Pause: ComponentType<LucideProps>;
  export const Stop: ComponentType<LucideProps>;
  export const Volume2: ComponentType<LucideProps>;
  export const VolumeX: ComponentType<LucideProps>;
  export const Mic: ComponentType<LucideProps>;
  export const MicOff: ComponentType<LucideProps>;
  export const Phone: ComponentType<LucideProps>;
  export const PhoneOff: ComponentType<LucideProps>;
  export const Camera: ComponentType<LucideProps>;
  export const CameraOff: ComponentType<LucideProps>;
  export const Monitor: ComponentType<LucideProps>;
  export const Smartphone: ComponentType<LucideProps>;
  export const Tablet: ComponentType<LucideProps>;
  export const Laptop: ComponentType<LucideProps>;
  export const Server: ComponentType<LucideProps>;
  export const Database: ComponentType<LucideProps>;
  export const Folder: ComponentType<LucideProps>;
  export const FolderOpen: ComponentType<LucideProps>;
  export const File: ComponentType<LucideProps>;
  export const FileText: ComponentType<LucideProps>;
  export const Image: ComponentType<LucideProps>;
  export const Video: ComponentType<LucideProps>;
  export const Music: ComponentType<LucideProps>;
  export const Headphones: ComponentType<LucideProps>;
  export const Speaker: ComponentType<LucideProps>;
  export const Wifi: ComponentType<LucideProps>;
  export const WifiOff: ComponentType<LucideProps>;
  export const Signal: ComponentType<LucideProps>;
  export const Battery: ComponentType<LucideProps>;
  export const BatteryLow: ComponentType<LucideProps>;
  export const Power: ComponentType<LucideProps>;
  export const PowerOff: ComponentType<LucideProps>;
  export const Zap: ComponentType<LucideProps>;
  export const ZapOff: ComponentType<LucideProps>;
  export const Activity: ComponentType<LucideProps>;
  export const BarChart: ComponentType<LucideProps>;
  export const BarChart2: ComponentType<LucideProps>;
  export const BarChart3: ComponentType<LucideProps>;
  export const PieChart: ComponentType<LucideProps>;
  export const TrendingUp: ComponentType<LucideProps>;
  export const TrendingDown: ComponentType<LucideProps>;
  export const ArrowUp: ComponentType<LucideProps>;
  export const ArrowDown: ComponentType<LucideProps>;
  export const ArrowLeft: ComponentType<LucideProps>;
  export const ArrowRight: ComponentType<LucideProps>;
  export const MessageCircle: ComponentType<LucideProps>;
  export const MessageSquare: ComponentType<LucideProps>;
  export const Mail: ComponentType<LucideProps>;
  export const Send: ComponentType<LucideProps>;
  export const Share: ComponentType<LucideProps>;
  export const Copy: ComponentType<LucideProps>;
  export const Link: ComponentType<LucideProps>;
  export const ExternalLink: ComponentType<LucideProps>;
  export const Globe: ComponentType<LucideProps>;
  export const MapPin: ComponentType<LucideProps>;
  export const Navigation: ComponentType<LucideProps>;
  export const Compass: ComponentType<LucideProps>;
  export const Calendar: ComponentType<LucideProps>;
  export const Clock: ComponentType<LucideProps>;
  export const Timer: ComponentType<LucideProps>;
  export const Stopwatch: ComponentType<LucideProps>;
  export const AlarmClock: ComponentType<LucideProps>;
  export const Bell: ComponentType<LucideProps>;
  export const BellOff: ComponentType<LucideProps>;
  export const Heart: ComponentType<LucideProps>;
  export const HeartHandshake: ComponentType<LucideProps>;
  export const Star: ComponentType<LucideProps>;
  export const Bookmark: ComponentType<LucideProps>;
  export const Flag: ComponentType<LucideProps>;
  export const Award: ComponentType<LucideProps>;
  export const Trophy: ComponentType<LucideProps>;
  export const Target: ComponentType<LucideProps>;
  export const Crosshair: ComponentType<LucideProps>;
  export const Focus: ComponentType<LucideProps>;
  export const Eye: ComponentType<LucideProps>;
  export const EyeOff: ComponentType<LucideProps>;
  export const Glasses: ComponentType<LucideProps>;
  export const Sun: ComponentType<LucideProps>;
  export const Moon: ComponentType<LucideProps>;
  export const Cloud: ComponentType<LucideProps>;
  export const CloudRain: ComponentType<LucideProps>;
  export const CloudSnow: ComponentType<LucideProps>;
  export const CloudLightning: ComponentType<LucideProps>;
  export const Thermometer: ComponentType<LucideProps>;
  export const Droplets: ComponentType<LucideProps>;
  export const Wind: ComponentType<LucideProps>;
  export const Tornado: ComponentType<LucideProps>;
  export const Rainbow: ComponentType<LucideProps>;
  export const Sunrise: ComponentType<LucideProps>;
  export const Sunset: ComponentType<LucideProps>;
  export const Moonlight: ComponentType<LucideProps>;
  export const Stars: ComponentType<LucideProps>;
  export const Sparkles: ComponentType<LucideProps>;
  export const Wand2: ComponentType<LucideProps>;
  export const Palette: ComponentType<LucideProps>;
  export const Brush: ComponentType<LucideProps>;
  export const Pencil: ComponentType<LucideProps>;
  export const PenTool: ComponentType<LucideProps>;
  export const Eraser: ComponentType<LucideProps>;
  export const Scissors: ComponentType<LucideProps>;
  export const Paperclip: ComponentType<LucideProps>;
  export const Pin: ComponentType<LucideProps>;
  export const Pushpin: ComponentType<LucideProps>;
  export const Stamp: ComponentType<LucideProps>;
  export const Sticker: ComponentType<LucideProps>;
  export const Tag: ComponentType<LucideProps>;
  export const Tags: ComponentType<LucideProps>;
  export const Hash: ComponentType<LucideProps>;
  export const AtSign: ComponentType<LucideProps>;
  export const Percent: ComponentType<LucideProps>;
  export const DollarSign: ComponentType<LucideProps>;
  export const Euro: ComponentType<LucideProps>;
  export const PoundSterling: ComponentType<LucideProps>;
  export const Yen: ComponentType<LucideProps>;
  export const Bitcoin: ComponentType<LucideProps>;
  export const CreditCard: ComponentType<LucideProps>;
  export const Banknote: ComponentType<LucideProps>;
  export const Wallet: ComponentType<LucideProps>;
  export const PiggyBank: ComponentType<LucideProps>;
  export const Calculator: ComponentType<LucideProps>;
  export const Abacus: ComponentType<LucideProps>;
  export const Binary: ComponentType<LucideProps>;
  export const Code: ComponentType<LucideProps>;
  export const Code2: ComponentType<LucideProps>;
  export const CodeSquare: ComponentType<LucideProps>;
  export const Terminal: ComponentType<LucideProps>;
  export const TerminalSquare: ComponentType<LucideProps>;
  export const Command: ComponentType<LucideProps>;
  export const Keyboard: ComponentType<LucideProps>;
  export const Mouse: ComponentType<LucideProps>;
  export const MousePointer: ComponentType<LucideProps>;
  export const MousePointer2: ComponentType<LucideProps>;
  export const MousePointerClick: ComponentType<LucideProps>;
  export const Touchpad: ComponentType<LucideProps>;
  export const TouchpadOff: ComponentType<LucideProps>;
  export const Gamepad: ComponentType<LucideProps>;
  export const Gamepad2: ComponentType<LucideProps>;
  export const Joystick: ComponentType<LucideProps>;
  export const Dices: ComponentType<LucideProps>;
  export const Dice1: ComponentType<LucideProps>;
  export const Dice2: ComponentType<LucideProps>;
  export const Dice3: ComponentType<LucideProps>;
  export const Dice4: ComponentType<LucideProps>;
  export const Dice5: ComponentType<LucideProps>;
  export const Dice6: ComponentType<LucideProps>;
  export const Spade: ComponentType<LucideProps>;
  export const Club: ComponentType<LucideProps>;
  export const Diamond: ComponentType<LucideProps>;
  export const Heart2: ComponentType<LucideProps>;
  export const Suit: ComponentType<LucideProps>;
  export const Crown: ComponentType<LucideProps>;
  export const Gem: ComponentType<LucideProps>;
  export const Coins: ComponentType<LucideProps>;
  export const Key: ComponentType<LucideProps>;
  export const KeyRound: ComponentType<LucideProps>;
  export const KeySquare: ComponentType<LucideProps>;
  export const Lock: ComponentType<LucideProps>;
  export const LockKeyhole: ComponentType<LucideProps>;
  export const Unlock: ComponentType<LucideProps>;
  export const UnlockKeyhole: ComponentType<LucideProps>;
  export const Shield: ComponentType<LucideProps>;
  export const ShieldAlert: ComponentType<LucideProps>;
  export const ShieldCheck: ComponentType<LucideProps>;
  export const ShieldClose: ComponentType<LucideProps>;
  export const ShieldEllipsis: ComponentType<LucideProps>;
  export const ShieldMinus: ComponentType<LucideProps>;
  export const ShieldPlus: ComponentType<LucideProps>;
  export const ShieldQuestion: ComponentType<LucideProps>;
  export const ShieldX: ComponentType<LucideProps>;
  export const Bug: ComponentType<LucideProps>;
  export const BugOff: ComponentType<LucideProps>;
  export const BugPlay: ComponentType<LucideProps>;
  export const Wrench: ComponentType<LucideProps>;
  export const Screwdriver: ComponentType<LucideProps>;
  export const Hammer: ComponentType<LucideProps>;
  export const Drill: ComponentType<LucideProps>;
  export const Pickaxe: ComponentType<LucideProps>;
  export const Shovel: ComponentType<LucideProps>;
  export const Axe: ComponentType<LucideProps>;
  export const Saw: ComponentType<LucideProps>;
  export const Pliers: ComponentType<LucideProps>;
  export const WrenchIcon: ComponentType<LucideProps>;
  export const Cog: ComponentType<LucideProps>;
  export const Cogs: ComponentType<LucideProps>;
  export const Gear: ComponentType<LucideProps>;
  export const Gears: ComponentType<LucideProps>;
  export const Settings2: ComponentType<LucideProps>;
  export const Sliders: ComponentType<LucideProps>;
  export const SlidersHorizontal: ComponentType<LucideProps>;
  export const MoreHorizontal: ComponentType<LucideProps>;
  export const MoreVertical: ComponentType<LucideProps>;
  export const Ellipsis: ComponentType<LucideProps>;
  export const EllipsisVertical: ComponentType<LucideProps>;
  export const Grip: ComponentType<LucideProps>;
  export const GripHorizontal: ComponentType<LucideProps>;
  export const GripVertical: ComponentType<LucideProps>;
  export const Move: ComponentType<LucideProps>;
  export const MoveHorizontal: ComponentType<LucideProps>;
  export const MoveVertical: ComponentType<LucideProps>;
  export const MoveDiagonal: ComponentType<LucideProps>;
  export const MoveDiagonal2: ComponentType<LucideProps>;
  export const Move3D: ComponentType<LucideProps>;
  export const Shuffle: ComponentType<LucideProps>;
  export const Repeat: ComponentType<LucideProps>;
  export const Repeat1: ComponentType<LucideProps>;
  export const Repeat2: ComponentType<LucideProps>;
  export const RotateCw: ComponentType<LucideProps>;
  export const RotateCcw: ComponentType<LucideProps>;
  export const Rotate3D: ComponentType<LucideProps>;
  export const FlipHorizontal: ComponentType<LucideProps>;
  export const FlipVertical: ComponentType<LucideProps>;
  export const FlipHorizontal2: ComponentType<LucideProps>;
  export const FlipVertical2: ComponentType<LucideProps>;
  export const Maximize: ComponentType<LucideProps>;
  export const Maximize2: ComponentType<LucideProps>;
  export const Minimize: ComponentType<LucideProps>;
  export const Minimize2: ComponentType<LucideProps>;
  export const Expand: ComponentType<LucideProps>;
  export const Shrink: ComponentType<LucideProps>;
  export const ArrowUpRight: ComponentType<LucideProps>;
  export const ArrowDownRight: ComponentType<LucideProps>;
  export const ArrowDownLeft: ComponentType<LucideProps>;
  export const ArrowUpLeft: ComponentType<LucideProps>;
  export const Corner: ComponentType<LucideProps>;
  export const CornerDownLeft: ComponentType<LucideProps>;
  export const CornerDownRight: ComponentType<LucideProps>;
  export const CornerLeftDown: ComponentType<LucideProps>;
  export const CornerLeftUp: ComponentType<LucideProps>;
  export const CornerRightDown: ComponentType<LucideProps>;
  export const CornerRightUp: ComponentType<LucideProps>;
  export const CornerUpLeft: ComponentType<LucideProps>;
  export const CornerUpRight: ComponentType<LucideProps>;
  export const Square: ComponentType<LucideProps>;
  export const SquareArrowOutUpRight: ComponentType<LucideProps>;
  export const SquareArrowOutUpLeft: ComponentType<LucideProps>;
  export const SquareArrowOutDownRight: ComponentType<LucideProps>;
  export const SquareArrowOutDownLeft: ComponentType<LucideProps>;
  export const RectangleHorizontal: ComponentType<LucideProps>;
  export const RectangleVertical: ComponentType<LucideProps>;
  export const Circle: ComponentType<LucideProps>;
  export const CircleDot: ComponentType<LucideProps>;
  export const CircleDotDashed: ComponentType<LucideProps>;
  export const CircleDashed: ComponentType<LucideProps>;
  export const Disc: ComponentType<LucideProps>;
  export const Disc2: ComponentType<LucideProps>;
  export const Disc3: ComponentType<LucideProps>;
  export const DiscAlbum: ComponentType<LucideProps>;
  export const Triangle: ComponentType<LucideProps>;
  export const TriangleAlert: ComponentType<LucideProps>;
  export const TriangleRight: ComponentType<LucideProps>;
  export const Pentagon: ComponentType<LucideProps>;
  export const Hexagon: ComponentType<LucideProps>;
  export const Octagon: ComponentType<LucideProps>;
  export const Diamond2: ComponentType<LucideProps>;
  export const Rhombus: ComponentType<LucideProps>;
  export const Parallelogram: ComponentType<LucideProps>;
  export const Trapezoid: ComponentType<LucideProps>;
  export const Cylinder: ComponentType<LucideProps>;
  export const Cone: ComponentType<LucideProps>;
  export const Sphere: ComponentType<LucideProps>;
  export const Cube: ComponentType<LucideProps>;
  export const Box: ComponentType<LucideProps>;
  export const Package: ComponentType<LucideProps>;
  export const Package2: ComponentType<LucideProps>;
  export const PackageCheck: ComponentType<LucideProps>;
  export const PackageMinus: ComponentType<LucideProps>;
  export const PackageOpen: ComponentType<LucideProps>;
  export const PackagePlus: ComponentType<LucideProps>;
  export const PackageSearch: ComponentType<LucideProps>;
  export const PackageX: ComponentType<LucideProps>;
  export const Container: ComponentType<LucideProps>;
  export const Archive: ComponentType<LucideProps>;
  export const ArchiveRestore: ComponentType<LucideProps>;
  export const ArchiveX: ComponentType<LucideProps>;
  export const FolderArchive: ComponentType<LucideProps>;
  export const FolderCheck: ComponentType<LucideProps>;
  export const FolderClosed: ComponentType<LucideProps>;
  export const FolderEdit: ComponentType<LucideProps>;
  export const FolderHeart: ComponentType<LucideProps>;
  export const FolderInput: ComponentType<LucideProps>;
  export const FolderKey: ComponentType<LucideProps>;
  export const FolderLock: ComponentType<LucideProps>;
  export const FolderMinus: ComponentType<LucideProps>;
  export const FolderOutput: ComponentType<LucideProps>;
  export const FolderPlus: ComponentType<LucideProps>;
  export const FolderRoot: ComponentType<LucideProps>;
  export const FolderSearch: ComponentType<LucideProps>;
  export const FolderSearch2: ComponentType<LucideProps>;
  export const FolderSymlink: ComponentType<LucideProps>;
  export const FolderSync: ComponentType<LucideProps>;
  export const FolderTree: ComponentType<LucideProps>;
  export const FolderUp: ComponentType<LucideProps>;
  export const FolderX: ComponentType<LucideProps>;
  export const Folders: ComponentType<LucideProps>;
  export const FileArchive: ComponentType<LucideProps>;
  export const FileAudio: ComponentType<LucideProps>;
  export const FileAudio2: ComponentType<LucideProps>;
  export const FileBadge: ComponentType<LucideProps>;
  export const FileBadge2: ComponentType<LucideProps>;
  export const FileBarChart: ComponentType<LucideProps>;
  export const FileBarChart2: ComponentType<LucideProps>;
  export const FileBox: ComponentType<LucideProps>;
  export const FileCheck: ComponentType<LucideProps>;
  export const FileCheck2: ComponentType<LucideProps>;
  export const FileClock: ComponentType<LucideProps>;
  export const FileCode: ComponentType<LucideProps>;
  export const FileCode2: ComponentType<LucideProps>;
  export const FileCog: ComponentType<LucideProps>;
  export const FileCog2: ComponentType<LucideProps>;
  export const FileDiff: ComponentType<LucideProps>;
  export const FileDigit: ComponentType<LucideProps>;
  export const FileDown: ComponentType<LucideProps>;
  export const FileEdit: ComponentType<LucideProps>;
  export const FileHeart: ComponentType<LucideProps>;
  export const FileImage: ComponentType<LucideProps>;
  export const FileInput: ComponentType<LucideProps>;
  export const FileJson: ComponentType<LucideProps>;
  export const FileJson2: ComponentType<LucideProps>;
  export const FileKey: ComponentType<LucideProps>;
  export const FileKey2: ComponentType<LucideProps>;
  export const FileLock: ComponentType<LucideProps>;
  export const FileLock2: ComponentType<LucideProps>;
  export const FileMinus: ComponentType<LucideProps>;
  export const FileMinus2: ComponentType<LucideProps>;
  export const FileMusic: ComponentType<LucideProps>;
  export const FileOutput: ComponentType<LucideProps>;
  export const FilePenLine: ComponentType<LucideProps>;
  export const FilePieChart: ComponentType<LucideProps>;
  export const FilePlus: ComponentType<LucideProps>;
  export const FilePlus2: ComponentType<LucideProps>;
  export const FileQuestion: ComponentType<LucideProps>;
  export const FileScan: ComponentType<LucideProps>;
  export const FileSearch: ComponentType<LucideProps>;
  export const FileSearch2: ComponentType<LucideProps>;
  export const FileSliders: ComponentType<LucideProps>;
  export const FileSpreadsheet: ComponentType<LucideProps>;
  export const FileStack: ComponentType<LucideProps>;
  export const FileSymlink: ComponentType<LucideProps>;
  export const FileTerminal: ComponentType<LucideProps>;
  export const FileType: ComponentType<LucideProps>;
  export const FileType2: ComponentType<LucideProps>;
  export const FileUp: ComponentType<LucideProps>;
  export const FileVideo: ComponentType<LucideProps>;
  export const FileVideo2: ComponentType<LucideProps>;
  export const FileVolume: ComponentType<LucideProps>;
  export const FileVolume2: ComponentType<LucideProps>;
  export const FileWarning: ComponentType<LucideProps>;
  export const FileX: ComponentType<LucideProps>;
  export const FileX2: ComponentType<LucideProps>;
  export const Files: ComponentType<LucideProps>;
  // ... and many more icons. This is a comprehensive but not exhaustive list.

  // Default export (if the library exports a default)
  const LucideReact: {
    [key: string]: ComponentType<LucideProps>;
  };
  export default LucideReact;
}