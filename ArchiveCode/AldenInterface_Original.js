import React, { useState, useEffect, useRef } from 'react';
import './AldenInterface.css';

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

    // Generate AI response (now async)
    setTimeout(async () => {
      const response = await generateResponse(content);
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

  // Enhanced Alden with Project Command integration
  const delegateToGoogle = async (task, context = '') => {
    try {
      if (window.electronAPI && window.electronAPI.claudeDelegateToGoogle) {
        const result = await window.electronAPI.claudeDelegateToGoogle({
          task: task,
          context: `Alden context: ${context}`,
          requiresReview: true
        });
        return result;
      } else {
        // Fallback simulation
        return {
          success: true,
          googleResponse: `Simulated Google AI response for: ${task}`,
          requiresReview: true
        };
      }
    } catch (error) {
      console.error('Delegation error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  };

  const generateResponse = async (userInput) => {
    const input = userInput.toLowerCase();
    
    // Project orchestration commands
    if (input.includes('orchestrate') || input.includes('project command') || input.includes('start project')) {
      const delegation = await delegateToGoogle(
        'Help design a project orchestration strategy for a coding workspace',
        'User wants to orchestrate a coding project with AI assistance'
      );
      
      if (delegation.success) {
        return `🎯 **Project Command Initiated** 

I'm now acting as your primary project orchestrator! Let me delegate this to our AI team for comprehensive planning:

**Google AI Analysis:**
${delegation.googleResponse}

**My Orchestration Plan:**
1. **Project Assessment** - Let's identify your coding objectives
2. **Resource Allocation** - I'll coordinate with our AI agents
3. **Task Breakdown** - ADHD-friendly incremental steps
4. **Execution Monitoring** - Real-time progress tracking

**Available Commands:**
• "write code to [path]" - Direct file creation
• "analyze codebase" - Architecture review
• "optimize performance" - Speed improvements
• "deploy project" - Production setup

What specific coding project would you like me to orchestrate?`;
      } else {
        return `🎯 **Project Command Ready** (Simulation Mode)

I'm ready to orchestrate your coding project! As your primary coordinator, I can:

**Core Capabilities:**
• Direct file writing to your workspace
• AI agent coordination (Google AI, Claude Code)
• ADHD-friendly task management
• Real-time progress monitoring

**Next Steps:**
1. Tell me about your coding project
2. I'll break it into manageable tasks
3. We'll use AI delegation for complex analysis
4. I'll write code directly to your workspace

What project would you like to start?`;
      }
    }
    
    // Workspace management
    if (input.includes('write') && (input.includes('file') || input.includes('code'))) {
      return `📝 **Workspace Writing Mode Activated**

I can write code directly to your workspace! Here's how:

**Supported Operations:**
• Create new files and directories
• Write/modify existing code
• Generate project structures
• Update configurations

**Usage Examples:**
• "Write a React component to ./src/components/MyComponent.js"
• "Create a Python script at ./scripts/automation.py"
• "Update package.json with new dependencies"

**File Path Formats:**
• Relative: ./src/file.js
• Absolute: /full/path/to/file.py
• Project root: package.json, README.md

What would you like me to write to your workspace?`;
    }
    
    // AI delegation
    if (input.includes('delegate') || input.includes('google ai') || input.includes('ask ai')) {
      return `🤖 **AI Delegation Center**

I can coordinate with Google AI for complex analysis! Available delegation:

**Code Analysis:**
• Architecture review and optimization
• Performance bottleneck identification
• Security vulnerability assessment
• Best practices recommendations

**Development Planning:**
• Technical specification creation
• Implementation roadmaps
• Testing strategies
• Deployment planning

**Problem Solving:**
• Debug assistance
• Algorithm optimization
• Integration challenges
• Scalability solutions

What would you like me to delegate to our AI team?`;
    }
    
    // File writing commands
    if (input.includes('write') && input.includes('to') && (input.includes('/') || input.includes('\\'))) {
      const match = input.match(/write (.+?) to (.+)/);
      if (match) {
        const content = match[1];
        const filePath = match[2];
        
        try {
          const result = await window.electronAPI.aldenWriteFile(filePath, content);
          if (result.success) {
            return `✅ **File Written Successfully!**

**File:** ${result.filePath}
**Size:** ${result.size} characters
**Created:** ${new Date(result.timestamp).toLocaleString()}

The file has been written to your workspace. I can also:
• Update existing files
• Create directory structures
• Generate project templates
• Review and modify code

Need me to write anything else?`;
          } else {
            return `❌ **File Write Failed**

**Error:** ${result.error}
**Path:** ${filePath}

Let me help troubleshoot:
• Check if the directory exists
• Verify file permissions
• Use relative paths like ./src/file.js
• Try a different location

Would you like me to try a different approach?`;
          }
        } catch (error) {
          return `❌ **Workspace Error:** ${error.message}

Let me guide you through file writing:
• Use format: "write [content] to [path]"
• Example: "write console.log('hello') to ./test.js"
• I'll create directories automatically
• Paths can be relative or absolute

Try again with a specific file and content!`;
        }
      }
    }
    
    // Code analysis commands
    if (input.includes('analyze') && (input.includes('code') || input.includes('project') || input.includes('codebase'))) {
      const delegation = await delegateToGoogle(
        'Analyze the current codebase structure and provide optimization recommendations',
        'User wants comprehensive code analysis and improvement suggestions'
      );
      
      if (delegation.success) {
        return `🔍 **Codebase Analysis Complete**

I've delegated this to our AI team for deep analysis:

**Google AI Analysis:**
${delegation.googleResponse}

**My ADHD-Friendly Action Plan:**
1. **Quick Wins** - Easy improvements (15-30 min each)
2. **Major Refactors** - Schedule during high-energy times
3. **Documentation** - Break into small daily tasks
4. **Testing** - Add incrementally, not all at once

**Next Steps:**
• Pick 1-2 quick wins to start
• Schedule major work for your best focus times
• I can write specific code changes to files

Which improvements should we tackle first?`;
      } else {
        return `🔍 **Codebase Analysis Ready**

I can help analyze your project! Here's what I can do:

**Analysis Types:**
• Performance bottlenecks
• Code quality issues
• Architecture improvements
• Security vulnerabilities
• ADHD-friendly refactoring plans

**Process:**
1. I'll examine your code structure
2. Delegate complex analysis to AI team
3. Break improvements into manageable tasks
4. Write updated code directly to files

What specific aspect would you like me to analyze?`;
      }
    }
    
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
          <button 
            onClick={() => handleSendMessage('orchestrate new project')}
            className="quick-action-btn project-command"
          >
            🎯 Project Command
          </button>
          <button 
            onClick={() => handleSendMessage('write code to ./example.js')}
            className="quick-action-btn workspace"
          >
            📝 Write Code
          </button>
          <button 
            onClick={() => handleSendMessage('analyze codebase')}
            className="quick-action-btn analysis"
          >
            🔍 Analyze Code
          </button>
          <button 
            onClick={() => handleSendMessage('delegate to google ai')}
            className="quick-action-btn delegation"
          >
            🤖 AI Delegate
          </button>
        </div>
      </div>
    </div>
  );
};

export default AldenInterface; 