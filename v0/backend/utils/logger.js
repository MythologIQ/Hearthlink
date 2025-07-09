// backend/utils/logger.js
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const LOG_DIR = path.join(__dirname, '..', 'logs'); // Create 'logs' directory in backend/
const MAX_LOG_FILES = 7; // Keep up to 7 days of logs

if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

function getLogFileName(serviceName = 'gatekeeper') {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return path.join(LOG_DIR, `${serviceName}_${year}-${month}-${day}.log`);
}

function purgeOldLogs(serviceName = 'gatekeeper') {
  fs.readdir(LOG_DIR, (err, files) => {
    if (err) {
      console.error('Failed to read log directory for purging:', err);
      return;
    }

    const serviceLogs = files
      .filter(file => file.startsWith(`${serviceName}_`) && file.endsWith('.log'))
      .sort((a, b) => {
        // Sort by date, newest first (though fs.statSync(path.join(LOG_DIR, b)).mtime might be more robust)
        return b.localeCompare(a);
      });

    if (serviceLogs.length > MAX_LOG_FILES) {
      const filesToPurge = serviceLogs.slice(MAX_LOG_FILES);
      filesToPurge.forEach(file => {
        fs.unlink(path.join(LOG_DIR, file), err => {
          if (err) {
            console.error(`Failed to purge old log file ${file}:`, err);
          } else {
            // console.log(`Purged old log file: ${file}`); // Log this to the current log file
            logToFile('INFO', `Purged old log file: ${file}`, 'LoggerMaintenance');
          }
        });
      });
    }
  });
}

function logToFile(level, message, component = 'GatekeeperCore', details = '') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] [${component}] ${message}${details ? ' | Details: ' + (typeof details === 'object' ? JSON.stringify(details) : details) : ''}\n`;
  const logFile = getLogFileName();

  // Also log to console for real-time visibility during development
  const consoleColorMap = {
    INFO: '\x1b[34m', // Blue
    WARN: '\x1b[33m', // Yellow
    ERROR: '\x1b[31m', // Red
    DEBUG: '\x1b[36m', // Cyan
    DEFAULT: '\x1b[0m' // Reset
  };
  const color = consoleColorMap[level.toUpperCase()] || consoleColorMap.DEFAULT;
  console.log(`${color}${logMessage.trim()}${consoleColorMap.DEFAULT}`);


  fs.appendFile(logFile, logMessage, err => {
    if (err) {
      console.error('FATAL: Failed to write to log file:', err);
    }
  });

  // Check for purging after logging (can be optimized to run less frequently)
  // For simplicity, running it each time. Could be daily.
  if (Math.random() < 0.1) { // Run purge check randomly 10% of the time to reduce overhead
      purgeOldLogs();
  }
}

// Initial purge check on startup
purgeOldLogs();

export const logger = {
  info: (message, component, details) => logToFile('INFO', message, component, details),
  warn: (message, component, details) => logToFile('WARN', message, component, details),
  error: (message, component, details) => logToFile('ERROR', message, component, details),
  debug: (message, component, details) => logToFile('DEBUG', message, component, details),
};

// Helper to ensure the logger is ready and initial purge is done.
logger.info("Logger initialized.", "LoggerBootstrap");
