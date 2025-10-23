// API route: /api/status
export default function handler(req, res) {
  res.status(200).json({
    system_status: 'operational',
    active_agents: 3,
    running_workflows: 5,
    queued_tasks: 12,
    cpu_usage: Math.floor(Math.random() * 30) + 40,
    memory_usage: Math.floor(Math.random() * 20) + 60,
    uptime: '2d 14h 30m'
  });
}
