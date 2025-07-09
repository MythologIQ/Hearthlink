
// backend/routes/agentRoutes.js
import express from 'express';
import { executeDockerCommand } from '../services/dockerService.js';
import { logger } from '../utils/logger.js';
// Supabase and WebSocket clientSessions will be passed or initialized globally

export default function(supabaseMCP, clientSessionsGetter) {
  const router = express.Router();

  // GET /api/agents - Get aggregated agent list
  router.get('/', async (req, res) => {
      const aggregatedAgents = new Map();
      const clientSessions = clientSessionsGetter(); // Get current sessions

      // 1. Docker Agents (Collected but will be filtered out later for the /api/agents endpoint)
      const dockerAgentsForInternalTracking = new Map();
      try {
          const stdout = await executeDockerCommand('docker ps --format "{{json .}}" --all');
          stdout.split('\n').filter(Boolean).forEach(line => {
              try {
                  const item = JSON.parse(line);
                  const agentName = item.Names; 
                  const agent = {
                      id: `docker-${item.ID}`,
                      name: agentName,
                      status: item.State || item.Status,
                      avatarUrl: `https://picsum.photos/seed/${agentName}/40/40`,
                      role: 'Containerized Service',
                      activeProcess: item.Status, 
                      lastSeen: new Date().toISOString(), 
                      sourceSystem: 'Docker'
                  };
                  dockerAgentsForInternalTracking.set(agentName, agent);
              } catch (e) { logger.error('Error parsing Docker agent line for agent list', 'AgentRoutes', e); }
          });
      } catch (error) {
          logger.warn('Failed to get Docker agents for agent list', 'AgentRoutes', { error: error.message });
      }

      // 2. Alden Agent (via HTTP API)
      const aldenPort = process.env.ALDEN_FLASK_PORT || 9342;
      const aldenStatusUrl = `http://localhost:${aldenPort}/status`;
      try {
          const aldenRes = await fetch(aldenStatusUrl); 
          if (!aldenRes.ok) throw new Error(`Alden API error: ${aldenRes.status} ${aldenRes.statusText}`);
          const aldenData = await aldenRes.json();
          const agentName = aldenData.name || 'Alden';
          const aldenAgent = {
              id: aldenData.id || 'alden-local-ai',
              name: agentName,
              status: aldenData.status || 'Unknown',
              avatarUrl: aldenData.avatarUrl || `https://picsum.photos/seed/${agentName}/40/40`,
              role: aldenData.role || 'Local AI',
              activeProcess: aldenData.activeProcess || 'Idle',
              lastSeen: aldenData.lastSeen || new Date().toISOString(),
              sourceSystem: 'AldenAPI'
          };
          const existing = aggregatedAgents.get(agentName) || {};
          aggregatedAgents.set(agentName, { ...existing, ...aldenAgent });
      } catch (error) {
          logger.warn("Failed to get Alden's status via API for agent list", 'AgentRoutes', { url: aldenStatusUrl, error: error.message });
          const agentName = 'Alden'; 
          if (!aggregatedAgents.has(agentName)) {
              aggregatedAgents.set(agentName, { id: 'alden-api-offline', name: agentName, status: 'Offline (API)', avatarUrl: `https://picsum.photos/seed/${agentName}/40/40`, role: 'Local AI', sourceSystem: 'FallbackAPI' });
          } else {
              const existing = aggregatedAgents.get(agentName);
              if (existing) existing.status = `${existing.status || 'Unknown'} (API Offline)`;
          }
      }
      
      // 3. Nexus Lens Agents (from WebSocket sessions)
      clientSessions.forEach((session, sessionId) => {
          if (session.agentType === 'NexusLens') { 
              const agentName = session.agentName || `Nexus Lens ${sessionId.substring(0, 6)}`;
              const agent = {
                  id: `nexuslens-${sessionId}`,
                  name: agentName,
                  status: 'Connected (WS)',
                  avatarUrl: `https://picsum.photos/seed/${agentName}/40/40`,
                  role: 'Browser Extension',
                  activeProcess: session.currentTabTitle || 'Monitoring',
                  lastSeen: new Date(session.lastPing || Date.now()).toISOString(),
                  sourceSystem: 'WebSocket'
              };
              const existing = aggregatedAgents.get(agentName) || {};
              aggregatedAgents.set(agentName, { ...existing, ...agent, id: existing.id || agent.id });
          }
      });

      // 4. MCP Agents (from MCP Supabase DB)
      if (supabaseMCP) {
          try {
              const { data, error } = await supabaseMCP.from('agents').select('id, name, role, active, registered_at, last_seen, current_task');
              if (error) throw error;
              (data || []).forEach(mcpAgentData => {
                   const agentName = mcpAgentData.name;
                   const agent = {
                      id: `mcp-${mcpAgentData.id}`,
                      name: agentName,
                      status: mcpAgentData.active ? 'Active (MCP DB)' : 'Inactive (MCP DB)',
                      avatarUrl: `https://picsum.photos/seed/${agentName}/40/40`,
                      role: mcpAgentData.role || 'MCP Agent',
                      activeProcess: mcpAgentData.current_task || (mcpAgentData.active ? 'Registered' : 'N/A'),
                      lastSeen: new Date(mcpAgentData.last_seen || mcpAgentData.registered_at).toISOString(),
                      sourceSystem: 'MCP_DB'
                  };
                  const existing = aggregatedAgents.get(agentName) || {};
                  aggregatedAgents.set(agentName, { ...existing, ...agent });
              });
          } catch (error) {
              logger.warn('Failed to get MCP agents from Supabase for agent list', 'AgentRoutes', { error: error.message });
          }
      }

      // 5. Gemini API Service Agent
      if (process.env.GEMINI_API_KEY) {
        const geminiAgentName = 'Gemini';
        const geminiAgent = {
            id: 'gemini-api-service', 
            name: geminiAgentName,
            status: 'Available',
            avatarUrl: 'https://picsum.photos/seed/GeminiAI/40/40', 
            role: 'AI Language Model',
            activeProcess: 'Ready (API Key Configured)',
            lastSeen: new Date().toISOString(), 
            sourceSystem: 'GeminiAPI'
        };
        const existing = aggregatedAgents.get(geminiAgentName) || {};
        aggregatedAgents.set(geminiAgentName, { ...existing, ...geminiAgent });
        logger.info('Gemini API service added to agent list as Available.', 'AgentRoutes');
      } else {
        logger.warn('Gemini API Key not set, Gemini service not listed as an active agent.', 'AgentRoutes');
      }
      
      // Filter out Docker containers before sending the response
      // Docker containers are managed in their own panel
      const finalAgentList = Array.from(aggregatedAgents.values()).filter(agent => 
        agent.role !== 'Containerized Service' && agent.sourceSystem !== 'Docker'
      );

      logger.debug(`Returning ${finalAgentList.length} non-container agents.`, 'AgentRoutes');
      res.json(finalAgentList);
  });

  return router;
}
