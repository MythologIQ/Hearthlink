// backend/routes/eventRoutes.js
import express from 'express';
import { createHash } from 'crypto';
import { logger } from '../utils/logger.js';
// Supabase client will be passed or initialized globally in main gatekeeper.js
// For now, assume supabaseAlden is available if configured.

let inMemoryEvents = []; // Fallback store

export default function(supabaseAlden) {
  const router = express.Router();

  // GET /api/events - Get logs/tasks
  router.get('/', async (req, res) => {
    const { source, type: eventType, limit = 100, offset = 0 } = req.query;
    const parsedLimit = parseInt(limit, 10);
    const parsedOffset = parseInt(offset, 10);

    if (supabaseAlden) {
      try {
        let query = supabaseAlden.from('events').select('*').order('timestamp', { ascending: false }).range(parsedOffset, parsedOffset + parsedLimit -1);
        if (source) query = query.eq('source', source);
        if (eventType) query = query.eq('type', eventType);

        const { data, error, count } = await query; // Assuming 'count' can be retrieved for pagination
        if (error) throw error;
        
        logger.debug('Events fetched from Supabase Alden DB.', 'EventRoutes', { count: data?.length });
        return res.json({ data: data || [], total: count /* May need separate count query */ });
      } catch (dbError) {
        logger.error('Supabase error fetching events', 'EventRoutes', { error: dbError.message });
        // Fall through to in-memory if Supabase fails and it's configured
      }
    }
    // Fallback to in-memory events
    let filteredEvents = [...inMemoryEvents]; // Create a copy to avoid modifying the original
    if (source) filteredEvents = filteredEvents.filter(e => e.source === source);
    if (eventType) filteredEvents = filteredEvents.filter(e => e.type === eventType);
    
    const paginatedEvents = filteredEvents.slice(parsedOffset, parsedOffset + parsedLimit);
    logger.debug('Events fetched from in-memory store.', 'EventRoutes', { count: paginatedEvents.length });
    res.json({data: paginatedEvents, total: filteredEvents.length });
  });

  // POST /api/events - Log a new event/task
  router.post('/', async (req, res) => {
    const { type, source, message, details } = req.body;
    if (!type || !source || !message) {
        logger.warn('Attempt to log event with missing fields', 'EventRoutes', { body: req.body });
        return res.status(400).json({error: 'Missing required fields: type, source, message'});
    }

    const timestamp = new Date().toISOString();
    // Simple ID generation, consider UUIDs for more robustness if IDs need to be globally unique and guess-proof
    const id = createHash('md5').update(JSON.stringify(req.body) + timestamp + Math.random()).digest('hex');
    const newEvent = { id, type, source, message, timestamp, details };

    if (supabaseAlden) {
      try {
        const { data, error } = await supabaseAlden.from('events').insert([
          { 
            // id: id, // Let Supabase auto-generate UUID if 'id' is primary and default uuid_generate_v4()
            source: newEvent.source, 
            type: newEvent.type, 
            message: newEvent.message, 
            timestamp: newEvent.timestamp,
            details: newEvent.details || null 
          }
        ]).select();
        if (error) throw error;
        
        const dbEvent = data ? data[0] : newEvent;
        logger.info('Event logged to Supabase Alden DB', 'EventRoutes', { eventId: dbEvent.id, type: dbEvent.type, source: dbEvent.source });
        
        // Also add to in-memory for quick access if DB is slow or as a cache, capped size
        inMemoryEvents.unshift(dbEvent);
        if(inMemoryEvents.length > 200) inMemoryEvents.length = 200; // Cap in-memory store
        
        return res.status(201).json(dbEvent);
      } catch (dbError) {
        logger.error('Supabase error logging event, falling back to in-memory', 'EventRoutes', { error: dbError.message });
      }
    }
    
    // Fallback to in-memory if Supabase not configured or failed
    inMemoryEvents.unshift(newEvent);
    if(inMemoryEvents.length > 200) inMemoryEvents.length = 200; // Cap in-memory store
    logger.info('Event logged to in-memory store', 'EventRoutes', { eventId: newEvent.id, type: newEvent.type, source: newEvent.source });
    res.status(201).json(newEvent);
  });

  return router;
}
