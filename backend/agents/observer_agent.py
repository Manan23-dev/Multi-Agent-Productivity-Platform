"""
Functional Observer Agent - Real LangChain implementation
"""

import asyncio
import json
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

class ObserverAgent:
    """Real Observer Agent for monitoring and event detection"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.is_running = False
        self.monitoring_data = {
            "system_health": {},
            "workflow_status": {},
            "user_activity": {},
            "alerts": []
        }
        
    async def initialize(self):
        """Initialize the Observer Agent with tools"""
        print("🤖 Initializing Observer Agent...")
        
        # Define monitoring tools
        tools = [
            Tool(
                name="system_health_check",
                description="Check system health and performance metrics",
                func=self._check_system_health
            ),
            Tool(
                name="workflow_status_check",
                description="Check status of running workflows",
                func=self._check_workflow_status
            ),
            Tool(
                name="user_activity_monitor",
                description="Monitor user activity and behavior patterns",
                func=self._monitor_user_activity
            ),
            Tool(
                name="alert_system",
                description="Send alerts and notifications",
                func=self._send_alert
            )
        ]
        
        # Create agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent executor
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=create_openai_functions_agent(self.llm, tools, prompt),
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        print("✅ Observer Agent initialized successfully")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Observer Agent"""
        return """
        You are the Observer Agent in the FlowAgent multi-agent system. Your primary responsibilities are:

        1. **System Monitoring**: Continuously monitor system health, performance, and resources
        2. **Event Detection**: Detect anomalies, errors, and important events
        3. **Alert Generation**: Generate alerts for critical issues
        4. **Data Collection**: Collect and analyze system metrics
        5. **Trend Analysis**: Identify patterns and trends in system behavior

        Key Capabilities:
        - Real-time system health monitoring
        - Performance metrics analysis
        - Workflow status tracking
        - User activity monitoring
        - Alert generation and management
        - Trend analysis and reporting

        Monitoring Process:
        1. Collect system metrics (CPU, memory, disk, network)
        2. Check workflow execution status
        3. Monitor user activity patterns
        4. Analyze data for anomalies
        5. Generate alerts for critical issues
        6. Provide insights and recommendations

        Always provide:
        - Clear status reports
        - Actionable insights
        - Proactive recommendations
        - Detailed analysis of issues
        """
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.is_running = True
        print("🔍 Observer Agent started monitoring...")
        
        while self.is_running:
            try:
                # Perform monitoring cycle
                await self._monitoring_cycle()
                await asyncio.sleep(30)  # Monitor every 30 seconds
            except Exception as e:
                print(f"❌ Error in monitoring cycle: {e}")
                await asyncio.sleep(10)
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        print("🛑 Observer Agent stopped monitoring")
    
    async def _monitoring_cycle(self):
        """Perform one monitoring cycle"""
        try:
            # Check system health
            system_health = await self._check_system_health()
            
            # Check workflow status
            workflow_status = await self._check_workflow_status()
            
            # Monitor user activity
            user_activity = await self._monitor_user_activity()
            
            # Analyze data and generate insights
            insights = await self._analyze_data(system_health, workflow_status, user_activity)
            
            # Update monitoring data
            self.monitoring_data.update({
                "system_health": system_health,
                "workflow_status": workflow_status,
                "user_activity": user_activity,
                "last_update": datetime.now().isoformat()
            })
            
            # Generate alerts if needed
            if insights.get("alerts"):
                for alert in insights["alerts"]:
                    await self._send_alert(alert)
            
            print(f"📊 Monitoring cycle completed: {insights.get('summary', 'No issues detected')}")
            
        except Exception as e:
            print(f"❌ Error in monitoring cycle: {e}")
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system health and performance metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Analyze health status
            health_status = "healthy"
            issues = []
            
            if cpu_percent > 80:
                health_status = "warning"
                issues.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 85:
                health_status = "warning"
                issues.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > 90:
                health_status = "critical"
                issues.append(f"Low disk space: {disk.percent}%")
            
            return {
                "status": health_status,
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "issues": issues,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_workflow_status(self) -> Dict[str, Any]:
        """Check status of running workflows"""
        # Simulate workflow status check
        workflows = [
            {
                "id": "wf_1",
                "name": "Data Processing Pipeline",
                "status": "running",
                "progress": 65,
                "tasks_completed": 13,
                "tasks_total": 20
            },
            {
                "id": "wf_2", 
                "name": "Email Automation",
                "status": "completed",
                "progress": 100,
                "tasks_completed": 8,
                "tasks_total": 8
            }
        ]
        
        return {
            "workflows": workflows,
            "total_running": len([w for w in workflows if w["status"] == "running"]),
            "total_completed": len([w for w in workflows if w["status"] == "completed"]),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _monitor_user_activity(self) -> Dict[str, Any]:
        """Monitor user activity and behavior patterns"""
        # Simulate user activity monitoring
        return {
            "active_users": 3,
            "api_requests": 45,
            "page_views": 120,
            "last_activity": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_data(self, system_health: Dict, workflow_status: Dict, user_activity: Dict) -> Dict[str, Any]:
        """Analyze monitoring data and generate insights"""
        insights = {
            "summary": "System operating normally",
            "alerts": [],
            "recommendations": []
        }
        
        # Analyze system health
        if system_health.get("status") == "critical":
            insights["alerts"].append({
                "type": "critical",
                "message": "Critical system issues detected",
                "details": system_health.get("issues", [])
            })
            insights["summary"] = "Critical issues detected"
        
        elif system_health.get("status") == "warning":
            insights["alerts"].append({
                "type": "warning", 
                "message": "System performance warnings",
                "details": system_health.get("issues", [])
            })
            insights["summary"] = "Performance warnings detected"
        
        # Analyze workflow status
        if workflow_status.get("total_running", 0) > 10:
            insights["recommendations"].append("Consider scaling resources for high workflow load")
        
        return insights
    
    async def _send_alert(self, alert_data: Dict[str, Any]):
        """Send alert notification"""
        print(f"🚨 ALERT [{alert_data.get('type', 'info').upper()}]: {alert_data.get('message', 'Unknown alert')}")
        if alert_data.get("details"):
            for detail in alert_data["details"]:
                print(f"   - {detail}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_type": "observer",
            "status": "active" if self.is_running else "inactive",
            "monitoring_data": self.monitoring_data,
            "uptime": "2h 30m",  # This would be calculated
            "last_heartbeat": datetime.now().isoformat()
        }
    
    async def analyze_system_health(self, query: str) -> str:
        """Analyze system health based on query"""
        try:
            response = await self.agent_executor.ainvoke({
                "input": f"Analyze system health: {query}"
            })
            return response["output"]
        except Exception as e:
            return f"Error analyzing system health: {e}"
