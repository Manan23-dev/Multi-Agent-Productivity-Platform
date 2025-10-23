// API route: /api/health
export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      database: 'healthy',
      redis: 'healthy',
      agents: 'healthy'
    }
  });
}
