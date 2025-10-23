# FlowAgent - Multi-Agent Productivity Platform

A sophisticated multi-agent system built with LangChain, FastAPI, React, and Redis for intelligent workflow automation.

## 🚀 Live Demo

- **Application**: https://flowagent.vercel.app
- **API Health**: https://flowagent.vercel.app/api/health
- **GitHub**: https://github.com/Manan23-dev/Multi-Agent-Productivity-Platform

## 🏗️ Architecture

```
React Frontend ←→ Vercel API ←→ LangChain Agents
                      ↓
                 OpenAI GPT-4
```

## 🤖 AI Agents

- **Observer**: Monitors system health, detects events, and generates alerts
- **Planner**: Creates workflow plans, decomposes tasks, and optimizes resources  
- **Executor**: Executes tasks, manages workflows, and monitors progress

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: Vercel Serverless Functions
- **AI Agents**: LangChain, OpenAI GPT-4
- **Communication**: REST API
- **Deployment**: Vercel (100% Free)

## 🚀 Quick Start

### Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/Manan23-dev/Multi-Agent-Productivity-Platform.git
   cd Multi-Agent-Productivity-Platform
   cp env.example .env
   # Edit .env with your OpenAI API key
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Vercel Deployment (100% Free)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add FlowAgent multi-agent system"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [Vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Configure:
     - **Framework**: Create React App
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `build`
   - Add environment variable: `OPENAI_API_KEY`
   - Click "Deploy"

3. **Test Your App**
   - Frontend: `https://your-project.vercel.app`
   - API: `https://your-project.vercel.app/api/health`

## 📊 Features

✅ **Real AI Agents** with LangChain integration
✅ **System Monitoring** with live metrics
✅ **Workflow Automation** - create and execute workflows
✅ **Agent Management** - start/stop agents with capabilities
✅ **Progress Tracking** - real-time execution monitoring
✅ **Error Handling** - intelligent retry and failure management
✅ **Responsive Design** with Tailwind CSS
✅ **100% Free** deployment on Vercel

## 🔧 Configuration

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key

## 📝 API Endpoints

- `GET /api/health` - Health check
- `GET /api/status` - System status
- `GET /api/agents/status` - List agents
- `POST /api/agents/{id}/start` - Start agent
- `POST /api/workflows/create` - Create workflow

## 🤖 Agent Capabilities

### Observer Agent
- System health monitoring with psutil
- Workflow status tracking
- User activity monitoring
- Alert generation and analysis
- LangChain tools and memory

### Planner Agent
- Workflow plan creation with templates
- Task decomposition and optimization
- Resource estimation and scheduling
- Timeline planning and validation
- LangChain agent executor

### Executor Agent
- Real task execution with different types
- Workflow management and coordination
- Progress monitoring and reporting
- Error handling and retry logic
- Resource allocation

## 🎯 Use Cases

- **Data Processing**: Automated data transformation pipelines
- **Email Automation**: Intelligent email processing and responses
- **Report Generation**: Automated report creation and analysis
- **System Monitoring**: Real-time health checks and alerts
- **Workflow Orchestration**: Complex task coordination

## 📚 Documentation

- [Vercel Deployment Guide](VERCEL_DEPLOYMENT.md)
- [API Documentation](https://your-project.vercel.app/api/health)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.