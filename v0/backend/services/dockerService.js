// backend/services/dockerService.js
import { exec } from 'child_process';
import { logger } from '../utils/logger.js';

/**
 * Executes a Docker command.
 * @param {string} command The Docker command to execute.
 * @returns {Promise<string>} A promise that resolves with the stdout of the command.
 */
export function executeDockerCommand(command) {
  return new Promise((resolve, reject) => {
    // Basic check for command safety
    if (command.includes(';') || command.includes('&&') || command.includes('||') || (command.includes('|') && !command.startsWith('docker ps --format'))) {
      logger.error(`Potentially unsafe characters detected in Docker command: ${command}`, 'DockerServiceExecute');
      return reject(new Error('Potentially unsafe Docker command.'));
    }

    logger.debug(`Executing Docker command: ${command}`, 'DockerServiceExecute');
    exec(command, (error, stdout, stderr) => {
      if (error) {
        logger.error(`Docker Command Error`, 'DockerServiceExecute', { command, stderr: stderr || error.message, error: error.message });
        reject(new Error(stderr || error.message));
        return;
      }
      logger.debug(`Docker Command Success`, 'DockerServiceExecute', { command, stdout: stdout.trim() });
      resolve(stdout.trim());
    });
  });
}