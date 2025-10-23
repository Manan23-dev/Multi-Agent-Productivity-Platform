// API route: /api/agents/[id]/stop
export default function handler(req, res) {
  const { id } = req.query;
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  res.status(200).json({
    message: `Agent ${id} stopped successfully`,
    agent_id: id,
    status: 'inactive',
    timestamp: new Date().toISOString()
  });
}
