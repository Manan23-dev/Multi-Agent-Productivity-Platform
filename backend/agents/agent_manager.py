"""
Agent Manager - Coordinates functional agents
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from backend.agents.observer_agent import ObserverAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.executor_agent import ExecutorAgent

class AgentManager:
    """Manages functional agents and their coordination"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
        # Initialize agents
        self.observer_agent = ObserverAgent(openai_api_key)
        self.planner_agent = PlannerAgent(openai_api_key)
        self.executor_agent = ExecutorAgent(openai_api_key)
        
        self.agents = {
            "observer": self.observer_agent,
            "planner": self.planner_agent,
            "executor": self.executor_agent
        }
        
        self.is_running = False
        self.workflow_history = []
    
    async def initialize_agents(self):
        """Initialize all agents"""
        print("🤖 Initializing functional agents...")
        
        try:
            # Initialize each agent
            await self.observer_agent.initialize()
            await self.planner_agent.initialize()
            await self.executor_agent.initialize()
            
            print("✅ All functional agents initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize agents: {e}")
            raise
    
    async def start_all_agents(self):
        """Start all agents"""
        if self.is_running:
            print("⚠️ Agents are already running")
            return
        
        print("🚀 Starting all functional agents...")
        self.is_running = True
        
        try:
            # Start observer agent monitoring
            asyncio.create_task(self.observer_agent.start_monitoring())
            
            # Start executor agent execution loop
            asyncio.create_task(self.executor_agent.start_execution_loop())
            
            print("✅ All functional agents started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start agents: {e}")
            self.is_running = False
            raise
    
    async def stop_all_agents(self):
        """Stop all agents"""
        if not self.is_running:
            print("⚠️ Agents are not running")
            return
        
        print("🛑 Stopping all functional agents...")
        self.is_running = False
        
        try:
            # Stop observer agent
            await self.observer_agent.stop_monitoring()
            
            # Stop executor agent
            await self.executor_agent.stop_execution_loop()
            
            print("✅ All functional agents stopped successfully")
            
        except Exception as e:
            print(f"❌ Error stopping agents: {e}")
    
    async def create_and_execute_workflow(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create and execute a workflow using the agents"""
        print(f"🔄 Creating and executing workflow: {requirements.get('name', 'Unknown')}")
        
        try:
            # Step 1: Planner creates the workflow plan
            workflow_plan = await self.planner_agent.create_workflow_plan(requirements)
            
            if workflow_plan.get("error"):
                return {
                    "status": "failed",
                    "error": workflow_plan["error"],
                    "step": "planning"
                }
            
            # Step 2: Executor executes the workflow
            execution_result = await self.executor_agent.execute_workflow(workflow_plan)
            
            # Step 3: Store in workflow history
            workflow_record = {
                "workflow_id": workflow_plan["workflow_id"],
                "requirements": requirements,
                "plan": workflow_plan,
                "execution_result": execution_result,
                "created_at": datetime.now().isoformat()
            }
            
            self.workflow_history.append(workflow_record)
            
            return {
                "status": "success",
                "workflow_id": workflow_plan["workflow_id"],
                "execution_result": execution_result,
                "summary": {
                    "tasks_completed": execution_result.get("completed_tasks", 0),
                    "tasks_failed": execution_result.get("failed_tasks", 0),
                    "success_rate": execution_result.get("success_rate", 0),
                    "duration": execution_result.get("duration", "unknown")
                }
            }
            
        except Exception as e:
            print(f"❌ Error in workflow execution: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "step": "execution"
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "system_status": "operational" if self.is_running else "stopped",
            "agents": {},
            "workflow_history": len(self.workflow_history),
            "timestamp": datetime.now().isoformat()
        }
        
        # Get status from each agent
        for agent_name, agent in self.agents.items():
            try:
                agent_status = await agent.get_status()
                status["agents"][agent_name] = agent_status
            except Exception as e:
                print(f"❌ Failed to get agent status: {agent_name}, error: {e}")
                status["agents"][agent_name] = {"status": "error", "error": str(e)}
        
        return status
    
    async def get_agent_insights(self, agent_type: str, query: str) -> str:
        """Get insights from a specific agent"""
        if agent_type not in self.agents:
            return f"Agent type '{agent_type}' not found"
        
        agent = self.agents[agent_type]
        
        try:
            if agent_type == "observer":
                return await agent.analyze_system_health(query)
            elif agent_type == "planner":
                # Planner insights would be implemented here
                return f"Planner insights for: {query}"
            elif agent_type == "executor":
                # Executor insights would be implemented here
                return f"Executor insights for: {query}"
            else:
                return f"No insights available for agent type: {agent_type}"
                
        except Exception as e:
            return f"Error getting insights from {agent_type}: {e}"
    
    async def get_workflow_history(self) -> list:
        """Get workflow execution history"""
        return self.workflow_history[-10:]  # Return last 10 workflows
    
    async def shutdown(self):
        """Shutdown agent manager"""
        print("🔄 Shutting down functional agent manager...")
        
        await self.stop_all_agents()
        
        print("✅ Functional agent manager shutdown complete")
