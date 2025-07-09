import React, { useState, useEffect, useRef } from 'react';

const AldenInterface = ({ accessibilitySettings, onVoiceCommand }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [personaInfo, setPersonaInfo] = useState({
    name: 'Alden',
    role: 'Productivity & ADHD Support Specialist',
    avatar: '/assets/Alden.png',
    description: 'I help you stay focused, organized, and productive with ADHD-friendly strategies.'
  });
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize with welcome message
    const welcomeMessage = {
      id: 1,
      type: 'assistant',
      content: `Hello! I'm ${personaInfo.name}, your productivity and ADHD support specialist. I'm here to help you stay focused, organized, and productive. 

How can I assist you today? You can:
• Ask me to help you break down tasks
• Get reminders and time management tips
• Discuss ADHD-friendly strategies
• Plan your day or week
• Or just chat about productivity challenges

Feel free to type or use voice commands!`,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, [personaInfo.name]);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content) => {
    if (!content.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const response = generateResponse(content);
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);

      // Voice feedback if enabled
      if (window.accessibility && accessibilitySettings.voiceFeedback) {
        window.accessibility.speak('New message received from Alden');
      }
    }, 1000 + Math.random() * 2000); // Random delay for realism
  };

  const generateResponse = (userInput) => {
    const input = userInput.toLowerCase();
    
    // Simple response patterns
    if (input.includes('task') || input.includes('todo')) {
      return `I'd be happy to help you with task management! Let's break this down:

1. **What's the main task?** - Let's identify the core objective
2. **Break it into smaller steps** - ADHD-friendly chunks of 15-30 minutes
3. **Set realistic deadlines** - Consider your energy levels
4. **Use visual reminders** - Post-its, apps, or whiteboards

Would you like me to help you break down a specific task, or would you prefer some general task management strategies?`;
    }
    
    if (input.includes('focus') || input.includes('concentration')) {
      return `Focus challenges are common with ADHD. Here are some strategies that work well:

**Environment:**
• Minimize distractions (noise-canceling headphones, quiet space)
• Use the Pomodoro Technique (25 min work, 5 min break)
• Keep your workspace clean and organized

**Mindset:**
• Start with your most important task when energy is highest
• Use body doubling (work alongside someone else)
• Reward yourself for completing tasks

**Tools:**
• Focus apps like Forest or Freedom
• White noise or instrumental music
• Fidget toys for physical stimulation

What specific focus challenges are you facing right now?`;
    }
    
    if (input.includes('time') || input.includes('schedule')) {
      return `Time management with ADHD requires a different approach. Here's what I recommend:

**Time Blocking:**
• Schedule specific times for specific tasks
• Include buffer time for transitions
• Plan for your energy levels (morning vs afternoon)

**Visual Planning:**
• Use color-coded calendars
• Try time-tracking apps
• Set multiple reminders

**Realistic Expectations:**
• Estimate time needed, then add 50%
• Build in breaks and transition time
• Don't over-schedule your day

Would you like help creating a daily or weekly schedule?`;
    }
    
    if (input.includes('overwhelm') || input.includes('stress')) {
      return `Feeling overwhelmed is completely normal with ADHD. Let's tackle this step by step:

**Right Now:**
• Take 3 deep breaths
• Drink some water
• Step away for 5 minutes if needed

**Break It Down:**
• What's the most urgent thing?
• What can wait until tomorrow?
• What can you delegate or ask for help with?

**Self-Care:**
• Remember to eat and sleep well
• Exercise helps with focus and mood
• Be kind to yourself - progress, not perfection

What's feeling most overwhelming right now? We can work through it together.`;
    }
    
    if (input.includes('reminder') || input.includes('forget')) {
      return `Memory and reminders are crucial for ADHD management. Here are some effective strategies:

**Multiple Reminder Systems:**
• Phone alarms with different sounds
• Visual reminders (post-its, whiteboard)
• Calendar notifications
• Ask friends/family to remind you

**Habit Stacking:**
• Link new habits to existing ones
• "After I brush my teeth, I'll take my medication"
• "When I sit at my desk, I'll check my to-do list"

**External Memory:**
• Write everything down
• Use apps like Todoist or Remember the Milk
• Voice memos for quick capture

What specific things do you tend to forget? We can create a personalized reminder system.`;
    }
    
    // Default response
    return `Thank you for sharing that with me. I'm here to support you with productivity and ADHD management strategies.

Could you tell me more about what you're working on or what challenges you're facing? I can help with:
• Task breakdown and planning
• Focus and concentration techniques
• Time management strategies
• Stress and overwhelm management
• Building better habits and routines

What would be most helpful for you right now?`;
  };

  const handleVoiceCommand = (command) => {
    if (command.toLowerCase().includes('send message') || command.toLowerCase().includes('type')) {
      const messageContent = command.replace(/send message|type/i, '').trim();
      if (messageContent) {
        handleSendMessage(messageContent);
      }
    } else {
      // Treat other voice commands as messages to Alden
      handleSendMessage(command);
    }
    
    onVoiceCommand(command);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputValue);
    }
  };

  return (
    <div className="alden-interface">
      <div className="alden-header">
        <div className="persona-info">
          <img src={personaInfo.avatar} alt={personaInfo.name} className="persona-avatar" />
          <div className="persona-details">
            <h3>{personaInfo.name}</h3>
            <p>{personaInfo.role}</p>
            <p className="persona-description">{personaInfo.description}</p>
          </div>
        </div>
        <div className="persona-controls">
          <button 
            onClick={() => handleVoiceCommand('help')}
            className="help-btn"
            aria-label="Get help from Alden"
          >
            ❓ Help
          </button>
          <button 
            onClick={() => setMessages([{
              id: Date.now(),
              type: 'assistant',
              content: 'I\'ve cleared our conversation. How can I help you start fresh?',
              timestamp: new Date()
            }])}
            className="clear-btn"
            aria-label="Clear conversation"
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="chat-container">
        <div className="messages">
          {messages.map(message => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-content">
                {message.content.split('\n').map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
              <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message assistant typing">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
            className="message-input"
            rows="3"
            aria-label="Type your message to Alden"
          />
          <div className="input-controls">
            <button 
              onClick={() => handleSendMessage(inputValue)}
              disabled={!inputValue.trim() || isTyping}
              className="send-btn"
              aria-label="Send message"
            >
              Send
            </button>
            <button 
              onClick={() => handleVoiceCommand('send message')}
              className="voice-btn"
              aria-label="Send voice message"
            >
              🎤
            </button>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <h4>Quick Actions</h4>
        <div className="action-buttons">
          <button 
            onClick={() => handleSendMessage('Help me break down a task')}
            className="quick-action-btn"
          >
            📋 Break Down Task
          </button>
          <button 
            onClick={() => handleSendMessage('I need help with focus')}
            className="quick-action-btn"
          >
            🎯 Focus Help
          </button>
          <button 
            onClick={() => handleSendMessage('Help me plan my day')}
            className="quick-action-btn"
          >
            📅 Plan My Day
          </button>
          <button 
            onClick={() => handleSendMessage('I feel overwhelmed')}
            className="quick-action-btn"
          >
            😰 Overwhelmed
          </button>
        </div>
      </div>
    </div>
  );
};

export default AldenInterface; 