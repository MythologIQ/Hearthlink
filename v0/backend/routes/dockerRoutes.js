// backend/routes/dockerRoutes.js
import express from 'express';
import { executeDockerCommand } from '../services/dockerService.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// GET /api/containers - List Docker containers
router.get('/', async (req, res) => {
  try {
    logger.debug('Attempting to list Docker containers.', 'DockerRoutes');
    const stdout = await executeDockerCommand('docker ps --format "{{json .}}" --all');
    const containers = stdout.split('\n').filter(Boolean).map(line => {
      try {
        const item = JSON.parse(line);
        return {
          id: item.ID,
          name: item.Names,
          image: item.Image,
          status: item.State || item.Status, 
        };
      } catch (e) {
        logger.error('Failed to parse Docker item line:', 'DockerRoutes', { line, error: e.message });
        return null;
      }
    }).filter(Boolean);
    logger.info(`Successfully listed ${containers.length} Docker containers.`, 'DockerRoutes');
    res.json(containers);
  } catch (error) {
    logger.error('Failed to get containers', 'DockerRoutes', { error: error.message });
    res.status(500).json({ error: 'Failed to get containers', details: error.message });
  }
});

// POST /api/containers/:id/:action - Perform action on a container
router.post('/:id/:action', async (req, res) => {
  const { id, action } = req.params;
  const validActions = ['start', 'stop', 'delete', 'restart']; 
  
  logger.info(`Attempting Docker action '${action}' on container '${id}'.`, 'DockerRoutes');

  if (!validActions.includes(action)) {
    logger.warn(`Invalid Docker action attempted: ${action} for container ${id}`, 'DockerRoutes');
    return res.status(400).json({ error: 'Invalid action' });
  }

  if (!/^[a-zA-Z0-9-_]+$/.test(id) && !/^[a-f0-9]{12,64}$/.test(id) && !id.startsWith('sha256:')) {
    logger.error(`Invalid container ID format provided for action '${action}': ${id}`, 'DockerRoutes');
    return res.status(400).json({ error: 'Invalid container ID format.' });
  }

  const command = action === 'delete' ? `docker rm -f ${id}` : `docker ${action} ${id}`;
  try {
    logger.debug(`Executing Docker command: ${command}`, 'DockerRoutes');
    await executeDockerCommand(command);
    logger.info(`Container ${id} ${action}ed successfully.`, 'DockerRoutes');
    res.json({ success: true, message: `Container ${id} ${action}ed successfully.` });
  } catch (error) {
    logger.error(`Failed to ${action} container ${id}`, 'DockerRoutes', { command, error: error.message });
    res.status(500).json({ error: `Failed to ${action} container`, details: error.message });
  }
});

export default router;