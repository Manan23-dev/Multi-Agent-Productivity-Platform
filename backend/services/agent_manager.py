"""
Agent Manager - Coordinates all agents
"""

import asyncio
from typing import Dict, Any, Optional
import structlog

from backend.core.config import get_settings
from backend.services.mcp_client import MCPClient
from backend.agents.observer_agent import ObserverAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.executor_agent import ExecutorAgent

logger = structlog.get_logger()

class AgentManager:
    """Manages all agents and their coordination"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.settings = get_settings()
        
        # Initialize agents
        self.observer_agent = ObserverAgent(mcp_client)
        self.planner_agent = PlannerAgent(mcp_client)
        self.executor_agent = ExecutorAgent(mcp_client)
        
        self.agents = {
            "observer": self.observer_agent,
            "planner": self.planner_agent,
            "executor": self.executor_agent
        }
        
        self.is_running = False
    
    async def initialize_agents(self):
        """Initialize all agents"""
        logger.info("Initializing all agents")
        
        try:
            # Initialize each agent
            await self.observer_agent.initialize()
            await self.planner_agent.initialize()
            await self.executor_agent.initialize()
            
            # Register MCP message handlers
            self._register_mcp_handlers()
            
            logger.info("All agents initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize agents", error=str(e))
            raise
    
    def _register_mcp_handlers(self):
        """Register MCP message handlers"""
        self.mcp_client.register_handler("workflow_request", self._handle_workflow_request)
        self.mcp_client.register_handler("task_execution", self._handle_task_execution)
        self.mcp_client.register_handler("alert", self._handle_alert)
        self.mcp_client.register_handler("event", self._handle_event)
    
    async def start_all_agents(self):
        """Start all agents"""
        if self.is_running:
            logger.warning("Agents are already running")
            return
        
        logger.info("Starting all agents")
        self.is_running = True
        
        try:
            # Start observer agent monitoring
            await self.observer_agent.start_monitoring()
            
            logger.info("All agents started successfully")
            
        except Exception as e:
            logger.error("Failed to start agents", error=str(e))
            self.is_running = False
            raise
    
    async def stop_all_agents(self):
        """Stop all agents"""
        if not self.is_running:
            logger.warning("Agents are not running")
            return
        
        logger.info("Stopping all agents")
        self.is_running = False
        
        try:
            # Stop observer agent
            await self.observer_agent.stop_monitoring()
            
            logger.info("All agents stopped successfully")
            
        except Exception as e:
            logger.error("Error stopping agents", error=str(e))
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create a new workflow"""
        logger.info("Creating workflow", workflow_data=workflow_data)
        
        try:
            # Send workflow request to planner agent
            response = await self.mcp_client.send_message(
                "workflow_request",
                workflow_data,
                destination="planner_agent",
                wait_for_response=True
            )
            
            workflow_id = response.get("workflow_id", "unknown")
            logger.info("Workflow created", workflow_id=workflow_id)
            
            return workflow_id
            
        except Exception as e:
            logger.error("Failed to create workflow", error=str(e))
            raise
    
    async def execute_task(self, task_data: Dict[str, Any]) -> str:
        """Execute a task"""
        logger.info("Executing task", task_data=task_data)
        
        try:
            # Send task execution request to executor agent
            response = await self.mcp_client.send_message(
                "task_execution",
                task_data,
                destination="executor_agent",
                wait_for_response=True
            )
            
            task_id = response.get("task_id", "unknown")
            logger.info("Task executed", task_id=task_id)
            
            return task_id
            
        except Exception as e:
            logger.error("Failed to execute task", error=str(e))
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        status = {
            "system_status": "operational" if self.is_running else "stopped",
            "agents": {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Get status from each agent
        for agent_name, agent in self.agents.items():
            try:
                agent_status = await agent.get_status()
                status["agents"][agent_name] = agent_status
            except Exception as e:
                logger.error("Failed to get agent status", agent_name=agent_name, error=str(e))
                status["agents"][agent_name] = {"status": "error", "error": str(e)}
        
        return status
    
    async def _handle_workflow_request(self, message: Dict[str, Any]):
        """Handle workflow request from MCP"""
        logger.info("Handling workflow request", message=message)
        
        # This would coordinate between planner and executor agents
        pass
    
    async def _handle_task_execution(self, message: Dict[str, Any]):
        """Handle task execution from MCP"""
        logger.info("Handling task execution", message=message)
        
        # This would coordinate task execution
        pass
    
    async def _handle_alert(self, message: Dict[str, Any]):
        """Handle alert from MCP"""
        logger.info("Handling alert", message=message)
        
        # This would process alerts and notify relevant agents
        pass
    
    async def _handle_event(self, message: Dict[str, Any]):
        """Handle event from MCP"""
        logger.info("Handling event", message=message)
        
        # This would process events and trigger appropriate responses
        pass
    
    async def shutdown(self):
        """Shutdown agent manager"""
        logger.info("Shutting down agent manager")
        
        await self.stop_all_agents()
        
        logger.info("Agent manager shutdown complete")
