// API route: /api/workflows/status
export default function handler(req, res) {
  const workflows = [
    {
      workflow_id: 'wf_1',
      name: 'Data Processing Pipeline',
      status: 'running',
      progress: Math.floor(Math.random() * 30) + 60,
      tasks_completed: Math.floor(Math.random() * 5) + 10,
      tasks_total: 20
    },
    {
      workflow_id: 'wf_2',
      name: 'Email Automation',
      status: 'completed',
      progress: 100,
      tasks_completed: 8,
      tasks_total: 8
    },
    {
      workflow_id: 'wf_3',
      name: 'Report Generation',
      status: 'pending',
      progress: 0,
      tasks_completed: 0,
      tasks_total: 15
    }
  ];

  res.status(200).json({ workflows });
}
