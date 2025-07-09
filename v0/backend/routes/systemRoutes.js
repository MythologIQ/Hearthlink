
// backend/routes/systemRoutes.js
import express from 'express';
import si from 'systeminformation';
import { exec } from 'child_process';
import fetch from 'node-fetch'; // Ensure node-fetch is installed or use global fetch if Node v18+
import { executeDockerCommand } from '../services/dockerService.js';
import { logger } from '../utils/logger.js';
import { getClientSessions } from '../websocket/handler.js'; // Import to get WS sessions

const router = express.Router();
let gatekeeperStartTime = Date.now(); // Store Gatekeeper start time
let lastApiErrorLog = null; // Store the last significant API error

// Middleware to potentially capture significant errors (simplified for example)
// A more robust solution would involve a proper error handling middleware that calls this.
// For now, this is a placeholder. Real error logging should happen in the global error handler in gatekeeper.js
export function setLastApiError(error, req) { // Export if called from elsewhere
  lastApiErrorLog = { 
    message: error.message, 
    timestamp: new Date().toISOString(), 
    route: req ? req.originalUrl : 'N/A',
    details: error.stack ? error.stack.split('\n')[0] : '' // First line of stack
  };
}


// GET /api/system/status - Get system health
router.get('/status', async (req, res) => {
  let dockerHealthy = false;
  try {
    await executeDockerCommand('docker version');
    dockerHealthy = true;
  } catch (error) {
    logger.warn('Docker status check failed during system status check', 'SystemRoutes', { error: error.message });
  }
  res.json({
    wsStatus: "Connected", // Assuming if Gatekeeper is up, WS can be connected to
    gatekeeperStatus: "Active", // Gatekeeper itself is active if serving this
    consoleVerified: true, // This might need a more dynamic check
    dockerStatus: dockerHealthy ? "Healthy" : "Unhealthy",
  });
});

// GET /api/system/metrics - Get system metrics
router.get('/metrics', async (req, res) => {
  try {
    const [cpuData, memData, fsSizeData] = await Promise.all([
      si.currentLoad(),
      si.mem(),
      si.fsSize()
    ]);
    const fsTotal = fsSizeData.reduce((acc, fs) => acc + fs.size, 0);
    const fsUsed = fsSizeData.reduce((acc, fs) => acc + fs.used, 0);

    const metrics = [
      { name: 'CPU Load', value: parseFloat(cpuData.currentLoad?.toFixed(2)) || 0 },
      { name: 'Memory Usage', value: parseFloat(((memData.active / memData.total) * 100).toFixed(2)) || 0 },
      { name: 'Disk Usage', value: parseFloat(((fsUsed / fsTotal) * 100).toFixed(2)) || 0 }
    ];
    const timeSeriesMetrics = ['Now-6', 'Now-5', 'Now-4', 'Now-3', 'Now-2', 'Now-1', 'Now'].map((timeLabel, index) => {
      const baseCpu = metrics.find(m => m.name === 'CPU Load')?.value || 0;
      const baseMem = metrics.find(m => m.name === 'Memory Usage')?.value || 0;
      return {
        name: timeLabel,
        'CPU Load (%)': parseFloat(Math.max(0, Math.min(100, baseCpu + (Math.random() * 10 - 5 * (7 - index)/7))).toFixed(2)),
        'Memory Usage (%)': parseFloat(Math.max(0, Math.min(100, baseMem + (Math.random() * 20 - 10 * (7 - index)/7))).toFixed(2)),
      };
    });
    res.json(timeSeriesMetrics);
  } catch (error) {
    logger.error('Failed to get system metrics', 'SystemRoutes', { error: error.message });
    const mockMetrics = ['Now-6', 'Now-5', 'Now-4', 'Now-3', 'Now-2', 'Now-1', 'Now'].map(day => ({
        name: day,
        'CPU Load (%)': Math.floor(Math.random() * 100),
        'Memory Usage (%)': Math.floor(Math.random() * 100)
    }));
    res.status(500).json(mockMetrics); // Send mock on error
  }
});

// GET /api/system/diagnostics - New endpoint for diagnostics panel
router.get('/diagnostics', (req, res) => {
  const clientSessions = getClientSessions();
  const uptimeMs = Date.now() - gatekeeperStartTime;
  const uptimeSecs = Math.floor(uptimeMs / 1000);
  const uptimeMins = Math.floor(uptimeSecs / 60);
  const uptimeHours = Math.floor(uptimeMins / 60);
  
  const uptimeFormatted = `${uptimeHours}h ${uptimeMins % 60}m ${uptimeSecs % 60}s`;
  const memoryUsageBytes = process.memoryUsage().rss;
  const memoryUsageMB = (memoryUsageBytes / 1024 / 1024).toFixed(2);

  logger.debug('Fetching system diagnostics', 'SystemRoutes_Diagnostics', { clients: clientSessions.size });
  res.json({
    gatekeeper: {
      uptime: uptimeFormatted,
      memoryUsageMB: memoryUsageMB,
      nodeVersion: process.version,
      platform: process.platform,
      lastApiError: lastApiErrorLog // Send the last logged error
    },
    websockets: {
      connectedClients: clientSessions.size,
      // Future: add more detailed WebSocket stats if tracked (e.g., message counts)
    },
    // Future: Add status for Alden, Databases by trying to ping them or check cached status
  });
});


// POST /api/system/components/:componentId/start
router.post('/components/:componentId/start', async (req, res) => {
    const { componentId } = req.params;
    let command = '';
    let successMessage = '';

    logger.info(`Attempting to start component: ${componentId}`, 'SystemComponentRoutes');

    switch (componentId) {
        case 'alden':
            command = process.env.ALDEN_START_COMMAND;
            if (!command) {
                logger.error('ALDEN_START_COMMAND not configured in .env for starting Alden.', 'SystemComponentRoutes');
                return res.status(500).json({ success: false, message: 'Alden start command not configured on server.' });
            }
            successMessage = 'Alden start command issued.';
            break;
        case 'supabaseAldenDB':
            const aldenDbContainer = process.env.SUPABASE_ALDEN_DB_CONTAINER_NAME;
            if (!aldenDbContainer) {
                logger.error('SUPABASE_ALDEN_DB_CONTAINER_NAME not configured in .env.', 'SystemComponentRoutes');
                return res.status(500).json({ success: false, message: 'Alden DB container name not configured.'});
            }
            command = `docker start ${aldenDbContainer}`;
            successMessage = `Alden Supabase DB (${aldenDbContainer}) start command issued.`;
            break;
        case 'supabaseMCPDB':
            const mcpDbContainer = process.env.SUPABASE_MCP_DB_CONTAINER_NAME;
            if (!mcpDbContainer) {
                logger.error('SUPABASE_MCP_DB_CONTAINER_NAME not configured in .env.', 'SystemComponentRoutes');
                return res.status(500).json({ success: false, message: 'MCP DB container name not configured.'});
            }
            command = `docker start ${mcpDbContainer}`;
            successMessage = `MCP Supabase DB (${mcpDbContainer}) start command issued.`;
            break;
        case 'gatekeeperWS': // Gatekeeper itself
            logger.info('Request to start Gatekeeper component received. Gatekeeper is already running.', 'SystemComponentRoutes');
            return res.json({ success: true, message: 'Gatekeeper is already running or needs to be managed externally.' });
        default:
            logger.warn(`Attempt to start unknown component: ${componentId}`, 'SystemComponentRoutes');
            return res.status(404).json({ success: false, message: 'Unknown component.' });
    }

    logger.info(`Executing start command for ${componentId}: ${command}`, 'SystemComponentRoutes');
    try {
        exec(command, (error, stdout, stderr) => { // Fire-and-forget
            if (error) {
                logger.error(`Error during async execution of start command for ${componentId}`, 'SystemComponentRoutes_AsyncExec', { command, error: error.message, stderr });
                setLastApiError(new Error(`Async start failed for ${componentId}: ${stderr || error.message}`), { originalUrl: `/api/system/components/${componentId}/start` });
                return;
            }
            if (stderr) {
                logger.warn(`Stderr during async start of ${componentId}`, 'SystemComponentRoutes_AsyncExec', { command, stderr });
            }
            logger.info(`Stdout from async start of ${componentId}`, 'SystemComponentRoutes_AsyncExec', { command, stdout });
        });
        res.json({ success: true, message: successMessage });
    } catch (error) { // This catch is unlikely to be hit for exec's async callback errors
        logger.error(`Failed to issue start command for ${componentId}`, 'SystemComponentRoutes', { command, error: error.message });
        setLastApiError(error, req);
        res.status(500).json({ success: false, message: `Failed to start ${componentId}.`, details: error.message });
    }
});

// GET /api/system/components/:componentId/status
router.get('/components/:componentId/status', async (req, res) => {
    const { componentId } = req.params;
    logger.info(`Verifying status for component: ${componentId}`, 'SystemComponentRoutes');

    try {
        switch (componentId) {
            case 'alden':
                const aldenFlaskPort = process.env.ALDEN_FLASK_PORT;
                if (!aldenFlaskPort) {
                    logger.error('ALDEN_FLASK_PORT not configured in .env for Alden status check.', 'SystemComponentRoutes');
                    return res.json({ status: 'Unknown', details: 'Alden service port not configured on server.' });
                }
                const aldenStatusUrl = `http://localhost:${aldenFlaskPort}/status`;
                try {
                    logger.debug(`Fetching Alden status from: ${aldenStatusUrl}`, 'SystemComponentRoutes');
                    const aldenRes = await fetch(aldenStatusUrl);
                    if (aldenRes.ok) {
                        const aldenStatus = await aldenRes.json();
                        logger.info('Alden status check successful', 'SystemComponentRoutes', { status: aldenStatus });
                        res.json({ status: aldenStatus.status || 'Running', details: aldenStatus });
                    } else {
                        logger.warn(`Alden API (${aldenStatusUrl}) responded with error ${aldenRes.status}`, 'SystemComponentRoutes');
                        res.json({ status: 'Offline', details: `Alden API failed with status ${aldenRes.status}` });
                    }
                } catch (fetchError) {
                     logger.warn(`Could not connect to Alden API at ${aldenStatusUrl}`, 'SystemComponentRoutes', { error: fetchError.message });
                     res.json({ status: 'Offline', details: `Could not connect to Alden API: ${fetchError.message}` });
                }
                break;
            case 'supabaseAldenDB':
            case 'supabaseMCPDB':
                const envVarName = componentId === 'supabaseAldenDB' ? 
                    'SUPABASE_ALDEN_DB_CONTAINER_NAME' : 'SUPABASE_MCP_DB_CONTAINER_NAME';
                const containerName = process.env[envVarName];

                if (!containerName) {
                     logger.warn(`Container name for ${componentId} (${envVarName}) not configured in .env`, 'SystemComponentRoutes');
                     return res.json({ status: 'Unknown', details: `Container name for ${componentId} not configured in .env` });
                }
                logger.debug(`Checking Docker status for container: ${containerName}`, 'SystemComponentRoutes');
                const dockerStatusOutput = await executeDockerCommand(`docker ps -f name=^/${containerName}$ --format "{{.Status}}"`);
                if (dockerStatusOutput && dockerStatusOutput.toLowerCase().startsWith('up')) {
                    logger.info(`Docker container ${containerName} is running`, 'SystemComponentRoutes', { status: dockerStatusOutput });
                    res.json({ status: 'Running', details: dockerStatusOutput });
                } else if (dockerStatusOutput) { // Container found but not 'up'
                    logger.info(`Docker container ${containerName} is not 'Up'`, 'SystemComponentRoutes', { status: dockerStatusOutput });
                    res.json({ status: 'Offline', details: `Status: ${dockerStatusOutput}` });
                } else { // Container not found
                    logger.info(`Docker container ${containerName} not found`, 'SystemComponentRoutes');
                    res.json({ status: 'Offline', details: 'Container not found or not running.' });
                }
                break;
            case 'gatekeeperWS': // Gatekeeper itself
                const wsPort = process.env.GATEKEEPER_WS_PORT || process.env.GATEKEEPER_HTTP_PORT || 9341;
                logger.info('GatekeeperWS status check: Gatekeeper is running.', 'SystemComponentRoutes');
                res.json({ status: 'Running', details: `Gatekeeper HTTP/WebSocket server active on port ${wsPort}` });
                break;
            default:
                logger.warn(`Status check for unknown component: ${componentId}`, 'SystemComponentRoutes');
                res.status(404).json({ status: 'Unknown', message: 'Unknown component.' });
        }
    } catch (error) {
        logger.error(`Error verifying component ${componentId} status`, 'SystemComponentRoutes', { error: error.message, stack: error.stack });
        setLastApiError(error, req);
        res.json({ status: 'Error', details: error.message });
    }
});

export default router;
