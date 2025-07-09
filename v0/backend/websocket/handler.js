
// backend/websocket/handler.js
import { WebSocketServer, WebSocket } from 'ws'; // Import WebSocket for readyState constants
import { createHash } from 'crypto';
import { logger } from '../utils/logger.js';
import { URL } from 'url'; // Node.js URL module

const clientSessions = new Map();
let wssInstance = null;

export function initializeWebSocketServer(httpServer, GATEKEEPER_TOKEN) {
  if (wssInstance) {
    logger.warn('WebSocket server already initialized.', 'WebSocketHandler');
    return wssInstance;
  }

  wssInstance = new WebSocketServer({ server: httpServer });
  logger.info('WebSocket server initialized and attached to HTTP server.', 'WebSocketHandler');

  wssInstance.on('connection', (ws, req) => {
    const connectionAttemptUrl = req.url;
    logger.info(`WS Connection Attempt: URL=${connectionAttemptUrl}`, 'WebSocketConnectAttempt', { remoteAddress: req.socket.remoteAddress });
    
    let sessionId = null; 
    try {
        const params = new URL(connectionAttemptUrl, `ws://${req.headers.host}`).searchParams;
        const token = params.get('token');
        const agentType = params.get('agentType') || 'UnknownClient';
        const agentName = params.get('agentName') || 'UnnamedAgent';
        const tabTitle = params.get('tabTitle') || (agentType === 'NexusLens' ? 'Nexus Lens Tab' : 'N/A');

        if (token !== GATEKEEPER_TOKEN) {
            logger.warn('WS: Invalid token, connection rejected.', 'WebSocketAuth', { remoteAddress: req.socket.remoteAddress, providedTokenEnding: token ? `...${token.slice(-4)}` : 'N/A' });
            ws.terminate();
            return;
        }
        logger.info('WS: Token validation successful.', 'WebSocketAuth', { remoteAddress: req.socket.remoteAddress });

        sessionId = createHash('md5').update(Math.random().toString() + Date.now()).digest('hex');
        const sessionData = { 
            ws, 
            agentType, 
            agentName, 
            currentTabTitle: tabTitle,
            lastPing: Date.now(),
            ip: req.socket.remoteAddress 
        };
        clientSessions.set(sessionId, sessionData);
        const connectionMessage = `WS Client Connected: ID ${sessionId}, Type ${agentType}, Name ${agentName}, IP ${sessionData.ip}, Title: ${tabTitle}`;
        logger.info(connectionMessage, 'WebSocketConnect');
        
        const ackMessage = {type: "connection_ack", sessionId: sessionId, message: "Successfully connected to Gatekeeper."};
        ws.send(JSON.stringify(ackMessage));
        logger.debug(`Sent connection_ack to ${sessionId}`, 'WebSocketSend', ackMessage);


    } catch (error) {
        logger.error('Error during WebSocket connection setup', 'WebSocketConnect', { error: error.message, url: connectionAttemptUrl });
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
            ws.terminate();
        }
        return;
    }


    ws.on('message', messageBuffer => {
      const rawMessage = messageBuffer.toString();
      logger.debug(`WS Msg Received (Raw) from ${sessionId} (${clientSessions.get(sessionId)?.agentType}): ${rawMessage.substring(0, 200)}${rawMessage.length > 200 ? '...' : ''}`, 'WebSocketMessageRaw');
      
      try {
        const parsedMessage = JSON.parse(rawMessage);
        logger.debug(`WS Msg Received (Parsed) from ${sessionId} (${clientSessions.get(sessionId)?.agentType}):`, 'WebSocketMessageParsed', parsedMessage);

        if (parsedMessage.type === 'client_log' && parsedMessage.payload) {
            const { level = 'INFO', message, component = 'Client', timestamp, context } = parsedMessage.payload;
            const logTimestamp = timestamp || new Date().toISOString();
            const logComponent = `WSClient[${component}-${sessionId.substring(0,6)}]`;
            const formattedMessage = `(${logTimestamp}) ${message}`;

            switch (level.toUpperCase()) {
                case 'INFO': logger.info(formattedMessage, logComponent, context); break;
                case 'WARN': logger.warn(formattedMessage, logComponent, context); break;
                case 'ERROR': logger.error(formattedMessage, logComponent, context); break;
                case 'DEBUG': logger.debug(formattedMessage, logComponent, context); break;
                default: logger.info(`(L:${level}) ${formattedMessage}`, logComponent, context);
            }
        } else if (parsedMessage.type === 'ping_gatekeeper') {
            const pongMessage = { type: 'pong_gatekeeper', traceId: parsedMessage.traceId, timestamp: new Date().toISOString() };
            ws.send(JSON.stringify(pongMessage));
            logger.debug(`Sent pong_gatekeeper to ${sessionId}`, 'WebSocketSend', pongMessage);
        }
      } catch (e) {
        logger.error(`WS: Error processing message from ${sessionId}. Raw: ${rawMessage}`, 'WebSocketMessageError', { error: e.message });
      }
    });

    ws.on('pong', () => {
        const session = clientSessions.get(sessionId);
        if (session) {
            session.lastPing = Date.now();
            logger.debug(`WS Pong received from ${sessionId}`, 'WebSocketHeartbeat');
        }
    });

    ws.on('close', (code, reasonBuffer) => {
      const reason = reasonBuffer.toString();
      const session = clientSessions.get(sessionId);
      logger.info(`WS Client Disconnected: ID ${sessionId}, Type ${session?.agentType}, Name ${session?.agentName}. Code: ${code}, Reason: ${reason || 'N/A'}`, 'WebSocketDisconnect');
      clientSessions.delete(sessionId);
    });

    ws.on('error', (error) => {
      const session = clientSessions.get(sessionId);
      logger.error(`WS Error on client: ID ${sessionId}, Type ${session?.agentType}, Name ${session?.agentName}`, 'WebSocketError', { error: error.message, stack: error.stack });
    });
  });

  // Heartbeat for WebSockets
  setInterval(() => {
    clientSessions.forEach((session, sessionId) => {
      if (!session.ws || session.ws.readyState === WebSocket.CLOSING || session.ws.readyState === WebSocket.CLOSED) {
        logger.warn(`WS Cleanup: Client ${sessionId} (Type: ${session.agentType}, Name: ${session.agentName}) is closing/closed. Removing.`, 'WebSocketHeartbeat');
        clientSessions.delete(sessionId);
        return;
      }
      
      if (Date.now() - (session.lastPing || 0) > 65000) { 
          logger.warn(`WS Timeout: Client ${sessionId} (Type: ${session.agentType}, Name: ${session.agentName}) timed out. Terminating.`, 'WebSocketHeartbeat');
          session.ws.terminate();
          clientSessions.delete(sessionId); 
          return;
      }
      
      try {
        logger.debug(`Sending Ping to WS Client ${sessionId} (Type: ${session.agentType}, Name: ${session.agentName})`, 'WebSocketHeartbeat');
        session.ws.ping(null, undefined, (err) => { // Added error callback for ping
            if (err) {
                logger.warn(`WS Ping Error for client ${sessionId}:`, 'WebSocketHeartbeat', {error: err.message});
            }
        });
      } catch (pingError) {
          logger.error(`WS Ping Send Error for client ${sessionId} (Type: ${session.agentType}, Name: ${session.agentName})`, 'WebSocketHeartbeat', {error: pingError.message});
          session.ws.terminate(); // Terminate if ping send fails
          clientSessions.delete(sessionId);
      }
    });
  }, 30000); 

  return wssInstance;
}

export function getClientSessions() {
    return clientSessions;
}

export function broadcastToAllClients(message) {
    if (!wssInstance) {
        logger.warn('Attempted to broadcast when WebSocket server is not initialized.', 'WebSocketBroadcast');
        return;
    }
    const stringifiedMessage = JSON.stringify(message);
    logger.debug('Broadcasting message to all WebSocket clients', 'WebSocketBroadcast', { messageCount: clientSessions.size, message });
    
    clientSessions.forEach((session, sessionId) => {
        if (session.ws.readyState === WebSocket.OPEN) {
            try {
                session.ws.send(stringifiedMessage);
            } catch (e) {
                logger.error(`Error broadcasting to client ${session.agentName} (ID: ${sessionId})`, 'WebSocketBroadcast', { error: e.message });
            }
        } else {
            logger.warn(`Skipping broadcast to client ${sessionId} (Type: ${session.agentType}, Name: ${session.agentName}) due to non-OPEN state: ${session.ws.readyState}`, 'WebSocketBroadcast');
        }
    });
}
