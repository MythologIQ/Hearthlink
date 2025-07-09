// backend/routes/aldenRoutes.js
import express from 'express';
import fetch from 'node-fetch'; // Ensure node-fetch is installed or use global fetch if Node v18+
import { logger } from '../utils/logger.js';

const router = express.Router();

// POST /api/alden/chat - Proxy to Alden's /submit_prompt
router.post('/chat', async (req, res) => {
  const { prompt, userId } = req.body; // Assuming Alden might need userId
  const aldenFlaskPort = process.env.ALDEN_FLASK_PORT;

  if (!aldenFlaskPort) {
    logger.error('ALDEN_FLASK_PORT not configured in .env for Alden chat proxy.', 'AldenRoutes');
    return res.status(500).json({ error: 'Alden service port not configured on server.' });
  }

  if (!prompt) {
    logger.warn('Alden chat attempt without prompt.', 'AldenRoutes');
    return res.status(400).json({ error: 'Prompt is required for Alden chat.' });
  }

  const aldenUrl = `http://localhost:${aldenFlaskPort}/submit_prompt`;
  logger.debug(`Proxying chat to Alden: ${aldenUrl}`, 'AldenRoutes', { promptLength: prompt.length, userId });

  try {
    const aldenResponse = await fetch(aldenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt_text: prompt, user_id: userId || 'nexus_console_user' }), // Match Alden's expected payload
    });

    if (!aldenResponse.ok) {
      const errorText = await aldenResponse.text();
      logger.error(`Alden API (/submit_prompt) responded with error ${aldenResponse.status}`, 'AldenRoutes', { url: aldenUrl, status: aldenResponse.status, errorText });
      return res.status(aldenResponse.status).json({ error: `Alden API error: ${errorText}` });
    }

    const responseData = await aldenResponse.json();
    // Alden's /submit_prompt according to API_README returns tags + emotion, or {id, status} from console_api_schema
    // Adjust based on actual Alden response for chat. Assuming it might return a direct text reply or structured data.
    // For now, let's assume responseData might have a 'reflection' or 'text' field.
    logger.debug('Received response from Alden /submit_prompt', 'AldenRoutes', responseData);
    res.json({ text: responseData.reflection || responseData.text || responseData }); 

  } catch (error) {
    logger.error('Failed to proxy chat to Alden', 'AldenRoutes', { url: aldenUrl, error: error.message });
    res.status(500).json({ error: 'Failed to communicate with Alden service.' });
  }
});

export default router;