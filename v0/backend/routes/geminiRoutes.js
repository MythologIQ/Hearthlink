
// backend/routes/geminiRoutes.js
import express from 'express';
import { GoogleGenAI } from '@google/genai';
import { logger } from '../utils/logger.js';

// aiInstance will be initialized when the factory function is called.
let aiInstance = null;

// Export a factory function that creates and returns the router
export default function createGeminiRouter() {
  if (!aiInstance) { // Initialize only once
    if (process.env.GEMINI_API_KEY) {
      try {
        aiInstance = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
        logger.info('GoogleGenAI client initialized successfully for Gemini.', 'GeminiRoutes_Factory');
      } catch (e) {
        logger.error("Failed to initialize GoogleGenAI in factory. Check API Key and library version", 'GeminiRoutes_Factory', { message: e.message, stack: e.stack });
        aiInstance = null;
      }
    } else {
      logger.warn('GEMINI_API_KEY not set when creating Gemini router. Gemini API features will be unavailable.', 'GeminiRoutes_Factory');
    }
  }

  const router = express.Router();

  // POST /api/gemini/generate - Proxy for Gemini API
  router.post('/generate', async (req, res) => {
    if (!aiInstance) {
      logger.error('Gemini API call attempt while client not initialized (from factory).', 'GeminiRoutes');
      return res.status(503).json({ error: 'Gemini AI client not initialized. Check API Key and server logs.' });
    }

    const { prompt, model: requestedModel, config } = req.body;
    if (!prompt) {
      logger.warn('Gemini API call attempt without prompt.', 'GeminiRoutes');
      return res.status(400).json({ error: 'Prompt is required' });
    }

    const modelToUse = requestedModel || 'gemini-2.5-flash-preview-04-17';

    try {
      logger.debug(`Generating content with Gemini. Model: ${modelToUse}`, 'GeminiRoutes', { promptLength: prompt.length, config });

      const response = await aiInstance.models.generateContent({
        model: modelToUse,
        contents: prompt,
        ...(config && { config })
      });

      const textOutput = response.text;

      if (typeof textOutput !== 'string') {
        logger.error('Gemini API response.text was not a string.', 'GeminiRoutes', { response });
        return res.status(500).json({ error: 'Unexpected response format from Gemini API.' });
      }

      logger.info(`Successfully generated content from Gemini model ${modelToUse}. Output length: ${textOutput.length}`, 'GeminiRoutes');
      res.json({ text: textOutput });

    } catch (error) {
      logger.error('Gemini API Error via Proxy', 'GeminiRoutes', { model: modelToUse, error: error.message, stack: error.stack });
      let clientErrorMessage = 'Failed to generate content from Gemini API.';
      if (error.message) {
        if (error.message.includes('API key not valid')) {
          clientErrorMessage = 'Gemini API key is not valid. Please check server configuration.';
        } else if (error.message.toLowerCase().includes('quota')) {
          clientErrorMessage = 'Gemini API quota exceeded.';
        } else if (error.message.toLowerCase().includes('model_not_found')) {
          clientErrorMessage = `Gemini model '${modelToUse}' not found or not accessible.`;
        }
      }
      res.status(500).json({ error: clientErrorMessage, details: process.env.NODE_ENV === 'development' ? error.message : undefined });
    }
  });

  return router;
}
