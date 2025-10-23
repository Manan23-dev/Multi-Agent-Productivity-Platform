// API route: /api/agents/[id]/start - Start functional agents
import { AgentManager } from '../../../../backend/agents/agent_manager.js';

let agentManager = null;

export default async function handler(req, res) {
  const { id } = req.query;
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Initialize agent manager if not already done
    if (!agentManager) {
      const openaiApiKey = process.env.OPENAI_API_KEY;
      if (!openaiApiKey) {
        return res.status(500).json({ 
          error: 'OpenAI API key not configured'
        });
      }
      
      agentManager = new AgentManager(openaiApiKey);
      await agentManager.initialize_agents();
    }

    // Start the specific agent
    if (id === 'observer') {
      await agentManager.observer_agent.start_monitoring();
    } else if (id === 'planner') {
      // Planner doesn't need to be started, it's stateless
      console.log('Planner agent is always ready');
    } else if (id === 'executor') {
      await agentManager.executor_agent.start_execution_loop();
    } else {
      return res.status(400).json({ error: 'Invalid agent ID' });
    }

    res.status(200).json({
      message: `Agent ${id} started successfully`,
      agent_id: id,
      status: 'active',
      timestamp: new Date().toISOString(),
      capabilities: getAgentCapabilities(id)
    });
    
  } catch (error) {
    console.error(`Error starting agent ${id}:`, error);
    res.status(500).json({ 
      error: `Failed to start agent ${id}`
    });
  }
}

function getAgentCapabilities(agentId) {
  const capabilities = {
    observer: ['System Monitoring', 'Health Checks', 'Alert Generation', 'Performance Analysis'],
    planner: ['Workflow Planning', 'Task Decomposition', 'Resource Optimization', 'Timeline Planning'],
    executor: ['Task Execution', 'Workflow Management', 'Progress Monitoring', 'Error Handling']
  };
  
  return capabilities[agentId] || [];
}