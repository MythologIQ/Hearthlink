import React, { useState, useEffect, useCallback } from 'react';
import './CalendarIntegration.css';

const CalendarIntegration = ({ data, isExpanded, onEventCreate, onEventUpdate, onTaskSchedule }) => {
  const [calendarData, setCalendarData] = useState({
    events: [],
    calendars: ['primary'],
    loading: false,
    lastSync: null
  });
  
  const [currentView, setCurrentView] = useState('month'); // month, week, day, agenda
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showCreateEvent, setShowCreateEvent] = useState(false);
  const [mcpConnected, setMcpConnected] = useState(false);
  const [authStatus, setAuthStatus] = useState('checking'); // checking, authenticated, need_auth, error
  
  // Create event form state
  const [newEvent, setNewEvent] = useState({
    summary: '',
    description: '',
    start: '',
    end: '',
    attendees: [],
    calendar_id: 'primary',
    location: '',
    reminders: true
  });

  // Time blocking and task integration
  const [availableTimeSlots, setAvailableTimeSlots] = useState([]);
  const [taskIntegration, setTaskIntegration] = useState({
    linkedTasks: [],
    scheduledTasks: [],
    taskSuggestions: []
  });

  // Initialize MCP connection and check auth
  useEffect(() => {
    if (isExpanded) {
      initializeMCPConnection();
    }
  }, [isExpanded]);

  // Load calendar events when connected and authenticated
  useEffect(() => {
    if (mcpConnected && authStatus === 'authenticated') {
      loadCalendarEvents();
      calculateAvailableTimeSlots();
    }
  }, [mcpConnected, authStatus, selectedDate]);

  const initializeMCPConnection = async () => {
    try {
      setCalendarData(prev => ({ ...prev, loading: true }));
      
      // Check MCP server status
      const serverResponse = await fetch('/api/synapse/mcp/servers/gmail-calendar', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      if (serverResponse.ok) {
        const serverData = await serverResponse.json();
        setMcpConnected(serverData.status === 'active');
        
        if (serverData.status === 'active') {
          await checkAuthenticationStatus();
        } else {
          setAuthStatus('need_auth');
        }
      } else {
        setMcpConnected(false);
        setAuthStatus('error');
      }
      
    } catch (error) {
      console.error('Failed to initialize MCP connection:', error);
      setMcpConnected(false);
      setAuthStatus('error');
    } finally {
      setCalendarData(prev => ({ ...prev, loading: false }));
    }
  };

  const checkAuthenticationStatus = async () => {
    try {
      // Test calendar access by trying to list calendars
      const response = await fetch('/api/synapse/mcp/servers/gmail-calendar/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          tool_name: 'list_calendar_events',
          parameters: {
            calendar_id: 'primary',
            max_results: 1
          }
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setAuthStatus('authenticated');
      } else if (result.error && result.error.includes('authentication')) {
        setAuthStatus('need_auth');
      } else {
        setAuthStatus('error');
      }
      
    } catch (error) {
      console.error('Auth check failed:', error);
      setAuthStatus('error');
    }
  };

  const loadCalendarEvents = async () => {
    try {
      setCalendarData(prev => ({ ...prev, loading: true }));
      
      // Calculate time range for current view
      const { timeMin, timeMax } = getTimeRangeForView(currentView, selectedDate);
      
      const response = await fetch('/api/synapse/mcp/calendar/events', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        params: new URLSearchParams({
          calendar_id: 'primary',
          time_min: timeMin,
          time_max: timeMax,
          max_results: '250'
        })
      });

      const events = await response.json();
      
      if (Array.isArray(events)) {
        setCalendarData(prev => ({
          ...prev,
          events: events.map(event => ({
            id: event.id,
            title: event.summary || 'Untitled Event',
            start: new Date(event.start.dateTime || event.start.date),
            end: new Date(event.end.dateTime || event.end.date),
            description: event.description || '',
            location: event.location || '',
            attendees: event.attendees || [],
            allDay: !event.start.dateTime,
            color: event.colorId ? getEventColor(event.colorId) : '#22d3ee',
            status: event.status || 'confirmed',
            organizer: event.organizer,
            calendar: event.organizer?.displayName || 'Primary'
          })),
          lastSync: new Date()
        }));
      }
      
    } catch (error) {
      console.error('Failed to load calendar events:', error);
    } finally {
      setCalendarData(prev => ({ ...prev, loading: false }));
    }
  };

  const getTimeRangeForView = (view, date) => {
    const start = new Date(date);
    const end = new Date(date);
    
    switch (view) {
      case 'month':
        start.setDate(1);
        start.setHours(0, 0, 0, 0);
        end.setMonth(end.getMonth() + 1, 0);
        end.setHours(23, 59, 59, 999);
        break;
      case 'week':
        const dayOfWeek = start.getDay();
        start.setDate(start.getDate() - dayOfWeek);
        start.setHours(0, 0, 0, 0);
        end.setDate(start.getDate() + 6);
        end.setHours(23, 59, 59, 999);
        break;
      case 'day':
        start.setHours(0, 0, 0, 0);
        end.setHours(23, 59, 59, 999);
        break;
      default:
        start.setDate(start.getDate() - 7);
        end.setDate(end.getDate() + 30);
        break;
    }
    
    return {
      timeMin: start.toISOString(),
      timeMax: end.toISOString()
    };
  };

  const calculateAvailableTimeSlots = useCallback(() => {
    if (!calendarData.events.length) return;
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const slots = [];
    const workingHours = { start: 9, end: 17 }; // 9 AM to 5 PM
    
    // Generate available slots for the next 7 days
    for (let day = 0; day < 7; day++) {
      const currentDay = new Date(today);
      currentDay.setDate(today.getDate() + day);
      
      // Skip weekends for work-focused slots
      if (currentDay.getDay() === 0 || currentDay.getDay() === 6) continue;
      
      // Find busy times for this day
      const dayEvents = calendarData.events.filter(event => {
        const eventDate = new Date(event.start);
        return eventDate.toDateString() === currentDay.toDateString();
      });
      
      // Generate available slots
      for (let hour = workingHours.start; hour < workingHours.end; hour++) {
        const slotStart = new Date(currentDay);
        slotStart.setHours(hour, 0, 0, 0);
        
        const slotEnd = new Date(currentDay);
        slotEnd.setHours(hour + 1, 0, 0, 0);
        
        // Check if slot conflicts with existing events
        const hasConflict = dayEvents.some(event => 
          (slotStart >= event.start && slotStart < event.end) ||
          (slotEnd > event.start && slotEnd <= event.end) ||
          (slotStart <= event.start && slotEnd >= event.end)
        );
        
        if (!hasConflict) {
          slots.push({
            id: `slot_${day}_${hour}`,
            start: slotStart,
            end: slotEnd,
            duration: 60, // minutes
            type: 'available'
          });
        }
      }
    }
    
    setAvailableTimeSlots(slots);
  }, [calendarData.events]);

  const handleCreateEvent = async () => {
    if (!newEvent.summary.trim() || !newEvent.start || !newEvent.end) return;
    
    try {
      const response = await fetch('/api/synapse/mcp/calendar/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          calendar_id: newEvent.calendar_id,
          summary: newEvent.summary,
          description: newEvent.description,
          start: newEvent.start,
          end: newEvent.end,
          attendees: newEvent.attendees,
          location: newEvent.location
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setShowCreateEvent(false);
        setNewEvent({
          summary: '',
          description: '',
          start: '',
          end: '',
          attendees: [],
          calendar_id: 'primary',
          location: '',
          reminders: true
        });
        
        // Refresh calendar events
        await loadCalendarEvents();
        
        if (onEventCreate) {
          onEventCreate(result.result);
        }
      } else {
        console.error('Failed to create event:', result.error);
      }
      
    } catch (error) {
      console.error('Error creating event:', error);
    }
  };

  const handleTaskScheduling = async (task, timeSlot) => {
    try {
      // Create calendar event for the task
      const taskEvent = {
        summary: `Task: ${task.title}`,
        description: `Scheduled task work session\n\nTask Description: ${task.description}\nPriority: ${task.priority}\nEstimated Time: ${task.estimatedTime}h`,
        start: timeSlot.start.toISOString(),
        end: timeSlot.end.toISOString(),
        calendar_id: 'primary'
      };
      
      const response = await fetch('/api/synapse/mcp/calendar/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(taskEvent)
      });

      const result = await response.json();
      
      if (result.success && onTaskSchedule) {
        onTaskSchedule(task, timeSlot, result.result);
        await loadCalendarEvents();
      }
      
    } catch (error) {
      console.error('Failed to schedule task:', error);
    }
  };

  const getEventColor = (colorId) => {
    const colors = {
      '1': '#7986cb', '2': '#33b679', '3': '#8e24aa', '4': '#e67c73',
      '5': '#f6c026', '6': '#f5511d', '7': '#039be5', '8': '#616161',
      '9': '#3f51b5', '10': '#0b8043', '11': '#d50000'
    };
    return colors[colorId] || '#22d3ee';
  };

  const renderAuthenticationPrompt = () => (
    <div className="auth-prompt">
      <div className="auth-icon">🔐</div>
      <h3>Calendar Authentication Required</h3>
      <p>Connect your Google Calendar to access scheduling and time blocking features.</p>
      <button 
        className="auth-btn"
        onClick={() => window.open('/api/synapse/mcp/gmail-calendar/oauth', '_blank')}
      >
        🔗 Connect Google Calendar
      </button>
    </div>
  );

  const renderCalendarPreview = () => (
    <div className="calendar-preview">
      <div className="preview-header">
        <h4>📅 Calendar Integration</h4>
        <div className="sync-status">
          {calendarData.lastSync ? (
            <span className="sync-time">
              Last sync: {calendarData.lastSync.toLocaleTimeString()}
            </span>
          ) : (
            <span className="sync-pending">Not synced</span>
          )}
        </div>
      </div>

      <div className="today-events">
        <div className="today-header">
          <span className="today-label">Today's Events</span>
          <span className="event-count">{getTodaysEvents().length}</span>
        </div>
        
        <div className="event-list-mini">
          {getTodaysEvents().slice(0, 3).map(event => (
            <div key={event.id} className="event-mini">
              <div 
                className="event-color-dot"
                style={{ backgroundColor: event.color }}
              />
              <div className="event-mini-info">
                <div className="event-mini-title">{event.title}</div>
                <div className="event-mini-time">
                  {event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {getTodaysEvents().length > 3 && (
          <div className="more-events">+{getTodaysEvents().length - 3} more events</div>
        )}
      </div>

      <div className="time-blocking-preview">
        <div className="time-block-header">
          <span className="time-block-label">Available Time Slots</span>
          <span className="slot-count">{availableTimeSlots.length}</span>
        </div>
        
        <div className="available-slots">
          {availableTimeSlots.slice(0, 2).map(slot => (
            <div key={slot.id} className="slot-mini">
              <div className="slot-time">
                {slot.start.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })}
              </div>
              <div className="slot-duration">
                {slot.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - 
                {slot.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const getTodaysEvents = () => {
    const today = new Date().toDateString();
    return calendarData.events.filter(event => 
      event.start.toDateString() === today
    );
  };

  const renderMonthView = () => {
    const monthStart = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1);
    const monthEnd = new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 0);
    const startDate = new Date(monthStart);
    startDate.setDate(startDate.getDate() - startDate.getDay());
    
    const days = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= monthEnd || days.length < 42) {
      days.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }

    return (
      <div className="calendar-month-view">
        <div className="month-header">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="day-header">{day}</div>
          ))}
        </div>
        
        <div className="month-grid">
          {days.map(day => {
            const dayEvents = calendarData.events.filter(event => 
              event.start.toDateString() === day.toDateString()
            );
            
            const isCurrentMonth = day.getMonth() === selectedDate.getMonth();
            const isToday = day.toDateString() === new Date().toDateString();
            
            return (
              <div 
                key={day.toISOString()}
                className={`calendar-day ${isCurrentMonth ? 'current-month' : 'other-month'} ${isToday ? 'today' : ''}`}
                onClick={() => setSelectedDate(new Date(day))}
              >
                <div className="day-number">{day.getDate()}</div>
                <div className="day-events">
                  {dayEvents.slice(0, 3).map(event => (
                    <div 
                      key={event.id}
                      className="event-dot"
                      style={{ backgroundColor: event.color }}
                      title={event.title}
                    />
                  ))}
                  {dayEvents.length > 3 && (
                    <div className="event-more">+{dayEvents.length - 3}</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderAgendaView = () => (
    <div className="calendar-agenda-view">
      <div className="agenda-days">
        {getNextSevenDays().map(day => {
          const dayEvents = calendarData.events.filter(event => 
            event.start.toDateString() === day.toDateString()
          );
          
          return (
            <div key={day.toISOString()} className="agenda-day">
              <div className="agenda-day-header">
                <div className="agenda-date">
                  <div className="agenda-day-name">
                    {day.toLocaleDateString([], { weekday: 'long' })}
                  </div>
                  <div className="agenda-date-number">
                    {day.toLocaleDateString([], { month: 'short', day: 'numeric' })}
                  </div>
                </div>
                <div className="agenda-event-count">
                  {dayEvents.length} events
                </div>
              </div>
              
              <div className="agenda-events">
                {dayEvents.length === 0 ? (
                  <div className="no-events">No events scheduled</div>
                ) : (
                  dayEvents.map(event => (
                    <div key={event.id} className="agenda-event">
                      <div 
                        className="event-time-block"
                        style={{ backgroundColor: event.color }}
                      >
                        <div className="event-start-time">
                          {event.start.toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </div>
                      </div>
                      <div className="event-details">
                        <div className="event-title">{event.title}</div>
                        {event.location && (
                          <div className="event-location">📍 {event.location}</div>
                        )}
                        {event.description && (
                          <div className="event-description">{event.description}</div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const getNextSevenDays = () => {
    const days = [];
    const today = new Date();
    
    for (let i = 0; i < 7; i++) {
      const day = new Date(today);
      day.setDate(today.getDate() + i);
      days.push(day);
    }
    
    return days;
  };

  // Preview mode for panel grid
  if (!isExpanded) {
    if (!mcpConnected || authStatus !== 'authenticated') {
      return (
        <div className="calendar-preview-disconnected">
          <div className="disconnect-icon">📅</div>
          <div className="disconnect-message">
            <div className="disconnect-title">Calendar Integration</div>
            <div className="disconnect-status">
              {authStatus === 'need_auth' ? 'Authentication required' : 'Connecting...'}
            </div>
          </div>
        </div>
      );
    }
    
    return renderCalendarPreview();
  }

  // Expanded view
  return (
    <div className="calendar-integration-expanded">
      <div className="calendar-header">
        <div className="header-left">
          <h2>📅 Calendar Integration</h2>
          <div className="view-controls">
            <button
              className={`view-btn ${currentView === 'month' ? 'active' : ''}`}
              onClick={() => setCurrentView('month')}
            >
              Month
            </button>
            <button
              className={`view-btn ${currentView === 'agenda' ? 'active' : ''}`}
              onClick={() => setCurrentView('agenda')}
            >
              Agenda
            </button>
          </div>
        </div>
        
        <div className="header-actions">
          <button
            className="sync-btn"
            onClick={loadCalendarEvents}
            disabled={calendarData.loading}
          >
            {calendarData.loading ? '🔄' : '↻'} Sync
          </button>
          <button
            className="create-event-btn"
            onClick={() => setShowCreateEvent(true)}
          >
            ✨ New Event
          </button>
        </div>
      </div>

      <div className="calendar-content">
        {authStatus === 'need_auth' && renderAuthenticationPrompt()}
        {authStatus === 'authenticated' && (
          <>
            {currentView === 'month' && renderMonthView()}
            {currentView === 'agenda' && renderAgendaView()}
          </>
        )}
        {authStatus === 'error' && (
          <div className="error-state">
            <div className="error-icon">⚠️</div>
            <h3>Connection Error</h3>
            <p>Unable to connect to calendar service. Please check your configuration.</p>
          </div>
        )}
      </div>

      {/* Create Event Modal */}
      {showCreateEvent && (
        <div className="create-event-modal-overlay">
          <div className="create-event-modal">
            <div className="modal-header">
              <h3>Create Calendar Event</h3>
              <button 
                className="modal-close-btn"
                onClick={() => setShowCreateEvent(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Event Title *</label>
                <input
                  type="text"
                  value={newEvent.summary}
                  onChange={(e) => setNewEvent(prev => ({ ...prev, summary: e.target.value }))}
                  placeholder="Enter event title..."
                  autoFocus
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Start Date & Time *</label>
                  <input
                    type="datetime-local"
                    value={newEvent.start}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, start: e.target.value }))}
                  />
                </div>

                <div className="form-group">
                  <label>End Date & Time *</label>
                  <input
                    type="datetime-local"
                    value={newEvent.end}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, end: e.target.value }))}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newEvent.description}
                  onChange={(e) => setNewEvent(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Event description..."
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  value={newEvent.location}
                  onChange={(e) => setNewEvent(prev => ({ ...prev, location: e.target.value }))}
                  placeholder="Event location..."
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="cancel-btn"
                onClick={() => setShowCreateEvent(false)}
              >
                Cancel
              </button>
              <button
                className="create-btn"
                onClick={handleCreateEvent}
                disabled={!newEvent.summary.trim() || !newEvent.start || !newEvent.end}
              >
                Create Event
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarIntegration;