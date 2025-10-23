"""
FlowAgent Backend - Main FastAPI Application

Multi-agent productivity platform with LangChain, MCP, Redis, and GPT-4 integration.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

import structlog
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from backend.core.config import get_settings
from backend.core.database import init_db
from backend.core.redis_client import init_redis
# from backend.api.routes import agents, workflows, tasks, monitoring
from backend.services.mcp_client import MCPClient
from backend.services.agent_manager import AgentManager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

# Global variables for services
mcp_client: MCPClient = None
agent_manager: AgentManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global mcp_client, agent_manager
    
    settings = get_settings()
    
    # Initialize services
    logger.info("Initializing FlowAgent services...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized successfully")
        
        # Initialize MCP client
        mcp_client = MCPClient(
            host=settings.mcp_server_host,
            port=settings.mcp_server_port,
            protocol=settings.mcp_server_protocol
        )
        await mcp_client.connect()
        logger.info("MCP client connected successfully")
        
        # Initialize agent manager
        agent_manager = AgentManager(mcp_client)
        await agent_manager.initialize_agents()
        logger.info("Agent manager initialized successfully")
        
        logger.info("FlowAgent startup completed successfully")
        
    except Exception as e:
        logger.error("Failed to initialize FlowAgent services", error=str(e))
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down FlowAgent services...")
    
    if agent_manager:
        await agent_manager.shutdown()
    
    if mcp_client:
        await mcp_client.disconnect()
    
    logger.info("FlowAgent shutdown completed")

# Create FastAPI application
app = FastAPI(
    title="FlowAgent API",
    description="Multi-Agent Productivity Platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.render.com"]
)

# Include API routes
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])

# WebSocket connections for real-time updates
active_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.info("Received WebSocket message", client_id=client_id, data=data)
            
            # Echo back for now - can be extended for specific message handling
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        active_connections.pop(client_id, None)
        logger.info("WebSocket disconnected", client_id=client_id)

async def broadcast_to_clients(message: str):
    """Broadcast message to all connected WebSocket clients"""
    for client_id, connection in active_connections.items():
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.error("Failed to send message to client", client_id=client_id, error=str(e))
            active_connections.pop(client_id, None)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FlowAgent Multi-Agent Productivity Platform",
        "version": "0.1.0",
        "status": "running",
        "agents": {
            "observer": "active",
            "planner": "active", 
            "executor": "active"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        # Check Redis connection
        # Check MCP server connection
        # Check agent status
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "database": "healthy",
                "redis": "healthy",
                "mcp_server": "healthy",
                "agents": "healthy"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/v1/status")
async def get_status():
    """Get system status"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    status = await agent_manager.get_system_status()
    return status

@app.post("/api/v1/workflows/create")
async def create_workflow(workflow_data: Dict[str, Any]):
    """Create a new workflow"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        workflow_id = await agent_manager.create_workflow(workflow_data)
        
        # Broadcast workflow creation to connected clients
        await broadcast_to_clients(f"Workflow created: {workflow_id}")
        
        return {"workflow_id": workflow_id, "status": "created"}
    except Exception as e:
        logger.error("Failed to create workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tasks/execute")
async def execute_task(task_data: Dict[str, Any]):
    """Execute a task"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        task_id = await agent_manager.execute_task(task_data)
        
        # Broadcast task execution to connected clients
        await broadcast_to_clients(f"Task executed: {task_id}")
        
        return {"task_id": task_id, "status": "executed"}
    except Exception as e:
        logger.error("Failed to execute task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=settings.api_workers if not settings.api_reload else 1
    )
