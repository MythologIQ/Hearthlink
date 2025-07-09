
// backend/gatekeeper.js
import dotenv from 'dotenv';
dotenv.config(); // Load .env file AT THE VERY TOP

import express from 'express';
import http from 'http';
import cors from 'cors';
import { createClient } from '@supabase/supabase-js';

import { logger } from './utils/logger.js';
import { initializeWebSocketServer, getClientSessions } from './websocket/handler.js';

// Import route modules/factory functions
import dockerRoutes from './routes/dockerRoutes.js';
import systemRoutes, { setLastApiError } from './routes/systemRoutes.js';
import createGeminiRouter from './routes/geminiRoutes.js'; // Import the factory function
import eventRoutes from './routes/eventRoutes.js';
import memoryRoutes from './routes/memoryRoutes.js';
import agentRoutes from './routes/agentRoutes.js';
import ingestRoutes from './routes/ingestRoutes.js';
import clientLogRoutes from './routes/clientLogRoutes.js';
import aldenRoutes from './routes/aldenRoutes.js';


const app = express();
const server = http.createServer(app);

const PORT = process.env.GATEKEEPER_HTTP_PORT || 9341;
const GATEKEEPER_TOKEN = process.env.GATEKEEPER_TOKEN || 'verysecrettoken';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY; // Read after dotenv.config()

logger.info(`Gatekeeper starting on port ${PORT}`, 'CoreStartup');
logger.info(`Gatekeeper Token: ${GATEKEEPER_TOKEN ? 'Set (Ending with ...' + GATEKEEPER_TOKEN.slice(-4) + ')' : 'Not Set (Using default - INSECURE)'}`, 'CoreStartup');
logger.info(`Gemini API Key: ${GEMINI_API_KEY ? 'Set (Ending with ...' + GEMINI_API_KEY.slice(-4) + ')' : 'NOT SET - Gemini features will be unavailable.'}`, 'CoreStartup');


// Supabase Client for Alden DB
const aldenSupabaseUrl = process.env.ALDEN_SUPABASE_URL;
const aldenSupabaseKey = process.env.ALDEN_SUPABASE_KEY;
const supabaseAlden = aldenSupabaseUrl && aldenSupabaseKey ? createClient(aldenSupabaseUrl, aldenSupabaseKey) : null;

if (!supabaseAlden) {
  logger.warn('Alden Supabase URL or Key not set. Alden DB features will be limited.', 'SupabaseInit_Alden');
} else {
  logger.info('Alden Supabase client initialized.', 'SupabaseInit_Alden');
}

// Supabase Client for MCP DB
const mcpSupabaseUrl = process.env.MCP_SUPABASE_URL;
const mcpSupabaseKey = process.env.MCP_SUPABASE_KEY;
const supabaseMCP = mcpSupabaseUrl && mcpSupabaseKey ? createClient(mcpSupabaseUrl, mcpSupabaseKey) : null;

if (!supabaseMCP) {
  logger.warn('MCP Supabase URL or Key not set. MCP DB features will be limited.', 'SupabaseInit_MCP');
} else {
  logger.info('MCP Supabase client initialized.', 'SupabaseInit_MCP');
}

// Configure CORS
const defaultAllowedOrigins = 'http://localhost:3000,http://localhost:5173,https://43wfq9dfus43wtdmbixx3jzt5nxt8lpnksylml4gtdt7dwtl14-h758245015.scf.usercontent.goog,https://2joa7utar4lvh8m52kitb2yym69zx0x3lpwz0c69ypgun24hsb-h758245015.scf.usercontent.goog,https://1vwaslt5i5rb0ddmhi301db68winas28d0bqegnf2w1ywnh3a3-h758245015.scf.usercontent.goog';
const allowOriginsEnv = process.env.ALLOW_ORIGINS || defaultAllowedOrigins;
const allowOrigins = allowOriginsEnv.split(',').map(origin => origin.trim());
logger.info(`CORS Explicitly Allowed Origins: ${allowOrigins.join(', ')}`, 'CoreStartup');

const userContentRegex = /^https:\/\/[a-z0-9-]+\.scf\.usercontent\.goog$/;

app.use(cors({
  origin: (origin, callback) => {
    if (!origin) {
      callback(null, true);
      return;
    }
    if (allowOrigins.includes(origin)) {
      callback(null, true);
    } else if (userContentRegex.test(origin)) {
      logger.info(`CORS: Allowing dynamic origin via regex: ${origin}`, 'CORS');
      callback(null, true);
    }
    else {
      logger.warn(`CORS: Request from disallowed origin: ${origin}`, 'CORS');
      callback(new Error(`Not allowed by CORS: ${origin}`));
    }
  }
}));

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));


// --- API Routes ---
// Initialize Gemini router after dotenv has loaded and clients are potentially set up
const geminiRouter = createGeminiRouter(); // Call the factory function

app.get('/api/status', (req, res) => res.json({ status: 'Gatekeeper is active', timestamp: new Date().toISOString() }));
app.use('/api/containers', dockerRoutes);
app.use('/api/system', systemRoutes);
app.use('/api/gemini', geminiRouter); // Use the router returned by the factory
app.use('/api/alden', aldenRoutes);
app.use('/api/events', eventRoutes(supabaseAlden));
app.use('/api/memory_items', memoryRoutes(supabaseAlden));
app.use('/api/agents', agentRoutes(supabaseMCP, getClientSessions));
app.use('/api/ingest', ingestRoutes);
app.use('/api/log/client', clientLogRoutes);


// --- WebSocket Server Initialization ---
initializeWebSocketServer(server, GATEKEEPER_TOKEN);


// --- Global Error Handler ---
app.use((err, req, res, next) => {
  logger.error(`Unhandled error on ${req.method} ${req.originalUrl}`, 'GlobalErrorHandler', { error: err.message, stack: err.stack });
  setLastApiError(err, req);
  res.status(err.status || 500).json({
    error: 'An unexpected error occurred on the server.',
    details: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Start the HTTP server
server.listen(PORT, () => {
  logger.info(`Gatekeeper HTTP server listening on port ${PORT}`, 'CoreStartup');
  logger.info('WebSocket server is also running, attached to the HTTP server.', 'CoreStartup');
});

process.on('SIGINT', () => {
    logger.info('Gatekeeper shutting down (SIGINT)...', 'CoreShutdown');
    server.close(() => {
        logger.info('HTTP server closed.', 'CoreShutdown');
        process.exit(0);
    });
});
