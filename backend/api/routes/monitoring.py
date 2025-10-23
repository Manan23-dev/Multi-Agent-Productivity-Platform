"""
Monitoring API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from backend.core.database import get_db
from backend.core.redis_client import get_redis
from backend.models import SystemMetric, ExecutionLog

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "healthy",
            "redis": "healthy",
            "agents": "healthy"
        }
    }

@router.get("/status")
async def get_system_status():
    """Get system status"""
    return {
        "system_status": "operational",
        "active_agents": 3,
        "running_workflows": 5,
        "queued_tasks": 12,
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "uptime": "2d 14h 30m"
    }

@router.get("/agents/status")
async def get_agents_status():
    """Get all agents status"""
    return {
        "agents": [
            {
                "agent_id": "observer",
                "status": "active",
                "uptime": "2d 14h 30m",
                "last_heartbeat": "2024-01-01T12:00:00Z"
            },
            {
                "agent_id": "planner",
                "status": "active",
                "uptime": "2d 14h 30m",
                "last_heartbeat": "2024-01-01T12:00:00Z"
            },
            {
                "agent_id": "executor",
                "status": "active",
                "uptime": "2d 14h 30m",
                "last_heartbeat": "2024-01-01T12:00:00Z"
            }
        ]
    }

@router.get("/workflows/status")
async def get_workflows_status():
    """Get workflows status"""
    return {
        "workflows": [
            {
                "workflow_id": "wf_1",
                "status": "running",
                "progress": 65.5,
                "tasks_completed": 13,
                "tasks_total": 20
            },
            {
                "workflow_id": "wf_2",
                "status": "completed",
                "progress": 100.0,
                "tasks_completed": 8,
                "tasks_total": 8
            }
        ]
    }

@router.get("/logs")
async def get_execution_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get execution logs"""
    return {
        "logs": [
            {
                "execution_id": "exec_1",
                "workflow_id": "wf_1",
                "status": "completed",
                "duration": 120,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ]
    }

@router.get("/metrics/system")
async def get_system_metrics():
    """Get system metrics"""
    return {
        "metrics": [
            {
                "name": "cpu_usage",
                "value": 45.2,
                "unit": "percent",
                "timestamp": "2024-01-01T12:00:00Z"
            },
            {
                "name": "memory_usage",
                "value": 67.8,
                "unit": "percent",
                "timestamp": "2024-01-01T12:00:00Z"
            },
            {
                "name": "disk_usage",
                "value": 23.1,
                "unit": "percent",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ]
    }

@router.get("/alerts")
async def get_alerts():
    """Get active alerts"""
    return {
        "alerts": [
            {
                "alert_id": "alert_1",
                "type": "high_cpu_usage",
                "severity": "warning",
                "message": "CPU usage is above 80%",
                "timestamp": "2024-01-01T12:00:00Z",
                "status": "active"
            }
        ]
    }
