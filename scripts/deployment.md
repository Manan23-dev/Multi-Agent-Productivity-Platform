# FlowAgent Deployment Scripts

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Backend Setup
```bash
cd flowagent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Database Setup
```bash
# Create database
createdb flowagent

# Run migrations
alembic upgrade head
```

### Environment Variables
Create `.env` file with:
```
DATABASE_URL=postgresql://user:password@localhost:5432/flowagent
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
DEBUG=true
ENVIRONMENT=development
```

## Production Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Render Deployment

#### Backend Service
- **Build Command**: `pip install -e .`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `DATABASE_URL`: PostgreSQL connection string
  - `REDIS_URL`: Redis connection string
  - `OPENAI_API_KEY`: OpenAI API key
  - `SECRET_KEY`: Secret key for JWT tokens

#### Frontend Service
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/build`
- **Environment Variables**:
  - `REACT_APP_API_URL`: Backend API URL

### Health Checks
- Backend: `GET /api/v1/monitoring/health`
- Frontend: Static file serving
- Database: PostgreSQL connection
- Redis: Redis ping

### Monitoring
- Prometheus metrics: `/api/v1/monitoring/metrics`
- System status: `/api/v1/monitoring/status`
- Agent status: `/api/v1/monitoring/agents/status`

### Scaling
- Backend: Horizontal scaling with load balancer
- Database: Read replicas for read-heavy workloads
- Redis: Redis Cluster for high availability
- Agents: Multiple agent instances for redundancy
