
// backend/routes/clientLogRoutes.js
import express from 'express';
import fetch from 'node-fetch'; // Ensure node-fetch is available
import { logger } from '../utils/logger.js';

const router = express.Router();

router.post('/', async (req, res) => {
  const { level = 'INFO', message, component = 'Frontend', timestamp, context } = req.body;
  
  if (!message) {
    return res.status(400).json({ error: 'Log message is required.' });
  }

  const logTimestamp = timestamp || new Date().toISOString();
  const logComponent = `Client[${component}]`;

  // 1. Log to Gatekeeper's internal logger (file/console)
  const formattedMessage = `(${logTimestamp}) ${message}`;
  switch (level.toUpperCase()) {
    case 'INFO':
      logger.info(formattedMessage, logComponent, context);
      break;
    case 'WARN':
      logger.warn(formattedMessage, logComponent, context);
      break;
    case 'ERROR':
      logger.error(formattedMessage, logComponent, context);
      break;
    case 'DEBUG':
      logger.debug(formattedMessage, logComponent, context);
      break;
    default:
      logger.info(`(Unknown Level: ${level}) ${formattedMessage}`, logComponent, context);
  }

  // 2. Create an "Event" log entry for UI visibility via /api/events
  try {
    const gatekeeperPort = process.env.GATEKEEPER_HTTP_PORT || 9341;
    const internalEventPayload = {
      type: 'Event', // Or a more specific type like 'ClientLog' if you adapt CombinedLogsPanel
      source: `Client[${component}]`,
      message: message,
      timestamp: logTimestamp,
      details: { clientLevel: level, ...(context || {}) } // Add client's original level to details
    };

    // Fire-and-forget this internal request. The main goal is to log the client's message.
    // If this internal logging fails, it shouldn't prevent the client's request from succeeding.
    fetch(`http://localhost:${gatekeeperPort}/api/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(internalEventPayload),
    })
    .then(internalRes => {
      if (!internalRes.ok) {
        internalRes.text().then(text => {
            logger.error('Failed to internally log client event to /api/events', 'ClientLogRoutes', { status: internalRes.status, response: text, originalClientLog: message });
        }).catch(() => {
             logger.error('Failed to internally log client event to /api/events and parse error response', 'ClientLogRoutes', { status: internalRes.status, originalClientLog: message });
        });
      } else {
        logger.debug('Successfully logged client message as an internal event.', 'ClientLogRoutes', { clientMessage: message });
      }
    })
    .catch(internalErr => {
      logger.error('Error during internal fetch to log client event', 'ClientLogRoutes', { error: internalErr.message, originalClientLog: message });
    });

  } catch (e) {
    logger.error('Exception while preparing to internally log client event', 'ClientLogRoutes', { error: e.message, originalClientLog: message });
  }

  res.status(202).json({ success: true, message: 'Log received and processed.' });
});

export default router;
