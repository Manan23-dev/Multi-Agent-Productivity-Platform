# FlowAgent - Multi-Agent Productivity Platform

A multi-agent system built with LangChain, FastAPI, React, and Redis for intelligent workflow automation.

## 🚀 Live Demo

- **Frontend**: https://flowagent-frontend.onrender.com
- **Backend API**: https://flowagent-backend.onrender.com
- **API Docs**: https://flowagent-backend.onrender.com/docs

## 🏗️ Architecture

```
React Frontend ←→ FastAPI Backend ←→ MCP Server
                      ↓
                 PostgreSQL + Redis
```

## 🤖 Agents

- **Observer**: Monitors system health and triggers events
- **Planner**: Creates and optimizes workflows  
- **Executor**: Executes tasks and manages workflow execution

## 🛠️ Tech Stack

- **Backend**: FastAPI, LangChain, Redis, PostgreSQL
- **Frontend**: React, TypeScript, Tailwind CSS
- **Agents**: OpenAI GPT-4, LangChain tools
- **Communication**: WebSocket, MCP protocol
- **Deployment**: Docker, Render

## 🚀 Quick Start

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd flowagent
   cp env.example .env
   # Edit .env with your API keys
   ```

2. **Backend**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   uvicorn backend.main:app --reload
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Docker
```bash
docker-compose up -d
```

## 📊 Features

- Real-time system monitoring
- Agent management dashboard
- Workflow creation and execution
- Task monitoring and control
- System metrics and health checks

## 🔧 Configuration

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key

## 📝 API Endpoints

- `GET /api/v1/monitoring/health` - Health check
- `GET /api/v1/monitoring/status` - System status
- `GET /api/v1/agents` - List agents
- `POST /api/v1/agents/{id}/start` - Start agent
- `GET /api/v1/workflows` - List workflows
- `POST /api/v1/workflows` - Create workflow

## 🚀 Deployment

### Render Deployment

1. **Backend Service**
   - Build Command: `pip install -e .`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Add PostgreSQL and Redis addons

2. **Frontend Service**
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/build`
   - Set `REACT_APP_API_URL` environment variable

## 📚 Documentation

- [API Documentation](https://flowagent-backend.onrender.com/docs)
- [Deployment Guide](scripts/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.