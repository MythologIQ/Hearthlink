
import React, { useState, useRef, useEffect } from 'react';
import { Panel } from './Panel';
import { ChatMessage } from '../types';
import { Button } from './common/Button';
// TextInput removed as we'll use a direct textarea for better control
import { MicrophoneIcon, UserIcon, ChevronDownIcon, BrainIcon } from '../constants'; // BrainIcon for Gemini

export interface ChatTarget {
  id: string;
  name: string;
  avatarUrl?: string; // URL or could be a way to signal a specific icon component
  icon?: React.FC<{ className?: string }>; // Optional: for direct icon component usage
}

interface ChatConsolePanelProps {
  messages: ChatMessage[];
  chatTargets: ChatTarget[];
  activeChatTargetId: string;
  onTargetChange: (targetId: string) => void;
  onSendMessage: (text: string, targetId: string) => void;
  panelWrapperClassName?: string;
  isSendingMessage: boolean;
}

export const ChatConsolePanel: React.FC<ChatConsolePanelProps> = ({
    messages,
    chatTargets,
    activeChatTargetId,
    onTargetChange,
    onSendMessage,
    panelWrapperClassName,
    isSendingMessage
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const [showTargetSelector, setShowTargetSelector] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  // Fix: Explicitly pass undefined to useRef to satisfy overload expectations if the no-argument call was causing an issue.
  const prevIsSendingMessageRef = useRef<boolean | undefined>(undefined);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // Effect to focus textarea after message sending is complete
  useEffect(() => {
    if (prevIsSendingMessageRef.current === true && isSendingMessage === false) {
      // Using setTimeout to ensure focus is applied after any pending DOM updates
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 0);
    }
    prevIsSendingMessageRef.current = isSendingMessage;
  }, [isSendingMessage]);


  const handleSend = () => {
    if (inputValue.trim() === '' || isSendingMessage) return;
    onSendMessage(inputValue, activeChatTargetId);
    setInputValue('');
    // Focus logic is now handled by the useEffect hook watching isSendingMessage
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height
      const scrollHeight = textareaRef.current.scrollHeight;
      // Max height, e.g., equivalent to 6 lines. Adjust as needed.
      // Assuming line height around 20-24px for text-sm. 3 * 24 = 72px for input itself.
      // Max height can be around 150px or 200px. For now, lets cap at 160px.
      const maxHeight = 160;
      textareaRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  }, [inputValue]);


  const activeTarget = chatTargets.find(t => t.id === activeChatTargetId) || chatTargets[0] || { id: 'default', name: 'Select Target'};

  const getTargetAvatar = (target: ChatTarget) => {
    if (target.id === 'gemini') return <BrainIcon className="w-5 h-5 text-[var(--brand-accent2)] mr-2"/>;
    if (target.avatarUrl) return <img src={target.avatarUrl} alt={target.name} className="w-5 h-5 rounded-full mr-2"/>;
    if (target.icon) { const IconComponent = target.icon; return <IconComponent className="w-5 h-5 text-[var(--brand-text-secondary)] mr-2"/>; }
    return <UserIcon className="w-5 h-5 text-[var(--brand-text-secondary)] mr-2"/>;
  };

  const getMessageAvatar = (senderName: string, avatarUrl?: string) => {
    if (senderName === 'Gemini') return <BrainIcon className="w-7 h-7 text-[var(--brand-accent2)] rounded-full flex-shrink-0" />;
    if (avatarUrl) return <img className="w-7 h-7 rounded-full flex-shrink-0" src={avatarUrl} alt={`${senderName} avatar`} />;
    return <UserIcon className="w-7 h-7 text-[var(--brand-text-secondary)] rounded-full flex-shrink-0" />;
  }


  return (
    <Panel
      title="Chat Console"
      className={`${panelWrapperClassName} flex flex-col`}
      contentClassName="flex flex-col flex-1 min-h-0" // Ensure this container can shrink and defines flex context
    >
      {/* Chat Target Selector */}
      <div className="relative mb-3">
        <Button
            variant="secondary"
            onClick={() => setShowTargetSelector(!showTargetSelector)}
            className="w-full flex justify-between items-center !bg-[var(--brand-primary-bg-lighter)] !border-[var(--brand-border)] hover:!bg-[var(--brand-accent1-hover)]"
            aria-expanded={showTargetSelector}
            aria-controls="chat-target-list"
        >
            <div className="flex items-center">
                {getTargetAvatar(activeTarget)}
                To: {activeTarget?.name || 'Select Target'}
            </div>
          <ChevronDownIcon className={`w-4 h-4 transition-transform ${showTargetSelector ? 'rotate-180' : ''}`} />
        </Button>
        {showTargetSelector && (
          <div
            id="chat-target-list"
            className="absolute z-10 top-full left-0 right-0 mt-1 bg-[var(--brand-primary-bg-lighter)] border border-[var(--brand-border)] rounded-md shadow-lg max-h-48 overflow-y-auto"
          >
            {chatTargets.map(target => (
              <div
                key={target.id}
                role="option"
                aria-selected={target.id === activeChatTargetId}
                onClick={() => {
                  onTargetChange(target.id);
                  setShowTargetSelector(false);
                }}
                className="flex items-center px-3 py-2 text-sm text-[var(--brand-text-secondary)] hover:bg-[var(--brand-accent1)] hover:text-[var(--brand-text-primary)] cursor-pointer"
              >
                {getTargetAvatar(target)}
                {target.name}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex-grow space-y-3 overflow-y-auto p-1 pr-2 mb-3 min-h-0 font-jetbrains-mono">
        {messages.map(msg => (
          <div key={msg.id} className={`flex items-start gap-2 ${msg.sender === 'User' ? 'justify-end' : ''}`}>
            {msg.sender !== 'User' && getMessageAvatar(msg.sender, msg.avatarUrl)}
            <div className={`flex flex-col max-w-[85%] sm:max-w-[75%] leading-snug p-2.5 ${
                msg.sender === 'User' ? 'rounded-s-lg rounded-ee-lg bg-[var(--brand-accent1)] text-white'
                                     : 'rounded-e-lg rounded-es-lg bg-[var(--brand-primary-bg-lighter)] text-[var(--brand-text-primary)]'
            } shadow-md`}>
              <div className="flex items-center space-x-2 rtl:space-x-reverse mb-1">
                <span className={`text-xs font-semibold ${msg.sender === 'User' ? 'text-indigo-100' : msg.sender === 'Gemini' ? 'text-[var(--brand-accent2)]' : 'text-[var(--brand-text-secondary)]'}`}>{msg.sender}</span>
                <span className={`text-xs font-normal ${msg.sender === 'User' ? 'text-indigo-200' : 'text-[var(--brand-text-secondary)]'}`}>{msg.timestamp}</span>
              </div>
              <p className="text-sm font-normal break-words">{msg.text}</p>
            </div>
            {msg.sender === 'User' && getMessageAvatar(msg.sender, msg.avatarUrl)}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="mt-auto border-t border-[var(--brand-border)] pt-3">
        <div className="flex items-stretch bg-[var(--brand-primary-bg)] rounded-lg p-1.5 shadow-md">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                }
            }}
            placeholder={`Message ${activeTarget?.name || ''}...`}
            className="flex-grow font-jetbrains-mono bg-[var(--brand-primary-bg-light)] border border-[var(--brand-border)] placeholder:text-[var(--brand-text-secondary)]
                       text-[var(--brand-text-primary)] text-sm p-2.5 resize-none overflow-y-auto
                       rounded-l-md focus:ring-1 focus:ring-[var(--brand-accent1)] focus:border-[var(--brand-accent1)] focus:outline-none
                       min-h-[44px] max-h-[160px]" // min-h to match button height, max-h for scroll
            aria-label="Chat message input"
            disabled={isSendingMessage}
            rows={1} // Start with 1 row, JS will expand
          />
          <Button
            variant="ghost"
            size="md" // Consistent size with send button
            className="!p-2.5 !rounded-none !border-y !border-r !border-[var(--brand-border)] !border-l-0
                       hover:!bg-[var(--brand-primary-bg-lighter)] !bg-[var(--brand-primary-bg)]" // Darker mic button
            aria-label="Use microphone"
            disabled={isSendingMessage}
            title="Use microphone (not implemented)"
          >
            <MicrophoneIcon className="text-[var(--brand-accent2)] w-5 h-5"/>
          </Button>
          <Button
            onClick={handleSend}
            size="md"
            aria-label="Send message"
            variant="primary"
            className="!px-5 !py-2.5 !rounded-r-md !rounded-l-none"
            disabled={isSendingMessage || inputValue.trim() === ''}
          >
            {isSendingMessage ? 'Sending...' : 'Send'}
          </Button>
        </div>
      </div>
    </Panel>
  );
};
