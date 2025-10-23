// API route: /api/workflows/create - Create and execute workflows
import { AgentManager } from '../../../backend/agents/agent_manager.js';

let agentManager = null;

export default async function handler(req, res) {
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
      await agentManager.start_all_agents();
    }

    const { name, description, type, priority } = req.body;

    // Create workflow requirements
    const requirements = {
      name: name || 'Custom Workflow',
      description: description || 'Automated workflow execution',
      type: type || 'custom',
      priority: priority || 'medium'
    };

    // Create and execute workflow using functional agents
    const result = await agentManager.create_and_execute_workflow(requirements);

    if (result.status === 'success') {
      res.status(200).json({
        message: 'Workflow created and executed successfully',
        workflow_id: result.workflow_id,
        execution_result: result.execution_result,
        summary: result.summary
      });
    } else {
      res.status(400).json({
        error: result.error,
        step: result.step
      });
    }
    
  } catch (error) {
    console.error('Error creating workflow:', error);
    res.status(500).json({ 
      error: 'Failed to create workflow'
    });
  }
}
