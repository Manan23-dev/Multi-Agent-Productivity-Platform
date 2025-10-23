"""
Observer Agent - Monitors system state and triggers events
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import structlog
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from backend.core.config import get_settings
from backend.core.redis_client import get_redis
from backend.services.mcp_client import MCPClient

logger = structlog.get_logger()

class ObserverAgent:
    """Observer Agent for monitoring and event detection"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=self.settings.openai_temperature,
            openai_api_key=self.settings.openai_api_key
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.is_running = False
        self.monitoring_tasks: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize the Observer Agent"""
        logger.info("Initializing Observer Agent")
        
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
                name="external_event_detector",
                description="Detect external events and triggers",
                func=self._detect_external_events
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
            agent=self._create_agent(prompt, tools),
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        logger.info("Observer Agent initialized successfully")
    
    def _create_agent(self, prompt, tools):
        """Create the agent with tools and prompt"""
        from langchain.agents import create_openai_functions_agent
        
        return create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Observer Agent"""
        return """
        You are the Observer Agent in the FlowAgent multi-agent system. Your primary responsibilities are:

        1. **System Monitoring**: Continuously monitor system health, performance metrics, and resource utilization
        2. **Event Detection**: Identify patterns, anomalies, and significant events in the system
        3. **User Behavior Analysis**: Track user interactions and behavior patterns
        4. **Workflow Monitoring**: Monitor running workflows and their progress
        5. **Alert Generation**: Generate alerts and notifications when thresholds are exceeded
        6. **Data Collection**: Collect and analyze data for insights and decision making

        Key Capabilities:
        - Real-time monitoring of system metrics
        - Pattern recognition and anomaly detection
        - Event correlation and analysis
        - Automated alert generation
        - Performance trend analysis
        - User activity tracking

        When monitoring, pay attention to:
        - System performance metrics (CPU, memory, disk usage)
        - Workflow execution times and success rates
        - User engagement patterns
        - Error rates and exception patterns
        - Resource utilization trends
        - External system dependencies

        Always provide clear, actionable insights and recommendations based on your observations.
        """
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        if self.is_running:
            logger.warning("Observer Agent is already running")
            return
        
        self.is_running = True
        logger.info("Starting Observer Agent monitoring")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitoring_loop()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._event_detection_loop()),
            asyncio.create_task(self._user_activity_loop())
        ]
        
        self.monitoring_tasks = {task.get_name(): task for task in tasks}
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error("Error in monitoring tasks", error=str(e))
        finally:
            self.is_running = False
    
    async def stop_monitoring(self):
        """Stop the monitoring loop"""
        logger.info("Stopping Observer Agent monitoring")
        self.is_running = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        self.monitoring_tasks.clear()
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Perform comprehensive system monitoring
                monitoring_data = await self._perform_monitoring_cycle()
                
                # Store monitoring data in Redis
                redis_client = await get_redis()
                await redis_client.setex(
                    "observer:monitoring_data",
                    300,  # 5 minutes
                    json.dumps(monitoring_data, default=str)
                )
                
                # Analyze data for patterns and anomalies
                analysis = await self._analyze_monitoring_data(monitoring_data)
                
                if analysis.get("alerts"):
                    await self._process_alerts(analysis["alerts"])
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.settings.observer_agent_interval)
                
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _health_check_loop(self):
        """Health check monitoring loop"""
        while self.is_running:
            try:
                health_status = await self._check_system_health()
                
                if health_status.get("status") != "healthy":
                    await self._send_alert({
                        "type": "system_health",
                        "severity": "warning",
                        "message": f"System health issue detected: {health_status}",
                        "timestamp": datetime.now().isoformat()
                    })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Error in health check loop", error=str(e))
                await asyncio.sleep(30)
    
    async def _event_detection_loop(self):
        """Event detection monitoring loop"""
        while self.is_running:
            try:
                events = await self._detect_external_events()
                
                for event in events:
                    await self._process_event(event)
                
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error("Error in event detection loop", error=str(e))
                await asyncio.sleep(30)
    
    async def _user_activity_loop(self):
        """User activity monitoring loop"""
        while self.is_running:
            try:
                activity_data = await self._monitor_user_activity()
                
                # Store user activity patterns
                redis_client = await get_redis()
                await redis_client.setex(
                    "observer:user_activity",
                    600,  # 10 minutes
                    json.dumps(activity_data, default=str)
                )
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error("Error in user activity loop", error=str(e))
                await asyncio.sleep(60)
    
    async def _perform_monitoring_cycle(self) -> Dict[str, Any]:
        """Perform a complete monitoring cycle"""
        monitoring_data = {
            "timestamp": datetime.now().isoformat(),
            "system_health": await self._check_system_health(),
            "workflow_status": await self._check_workflow_status(),
            "user_activity": await self._monitor_user_activity(),
            "external_events": await self._detect_external_events()
        }
        
        return monitoring_data
    
    async def _analyze_monitoring_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze monitoring data for patterns and anomalies"""
        analysis_prompt = f"""
        Analyze the following monitoring data and identify:
        1. Performance trends and patterns
        2. Anomalies or unusual behavior
        3. Potential issues or bottlenecks
        4. Recommendations for optimization
        5. Alerts that should be generated
        
        Monitoring Data:
        {json.dumps(data, indent=2)}
        
        Provide your analysis in JSON format with the following structure:
        {{
            "trends": ["trend1", "trend2"],
            "anomalies": ["anomaly1", "anomaly2"],
            "issues": ["issue1", "issue2"],
            "recommendations": ["rec1", "rec2"],
            "alerts": [
                {{
                    "type": "alert_type",
                    "severity": "low|medium|high|critical",
                    "message": "alert message",
                    "recommendation": "recommended action"
                }}
            ]
        }}
        """
        
        try:
            response = await self.agent_executor.ainvoke({"input": analysis_prompt})
            analysis = json.loads(response["output"])
            return analysis
        except Exception as e:
            logger.error("Error analyzing monitoring data", error=str(e))
            return {"alerts": []}
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system health metrics"""
        # This would integrate with actual system monitoring
        return {
            "status": "healthy",
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "network_latency": 12.5,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _check_workflow_status(self) -> Dict[str, Any]:
        """Check status of running workflows"""
        # This would check actual workflow status
        return {
            "active_workflows": 3,
            "completed_today": 15,
            "failed_today": 1,
            "average_execution_time": 45.2,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _monitor_user_activity(self) -> Dict[str, Any]:
        """Monitor user activity patterns"""
        # This would track actual user activity
        return {
            "active_users": 12,
            "new_users_today": 3,
            "user_engagement_score": 8.5,
            "popular_features": ["workflow_creation", "task_execution"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _detect_external_events(self) -> List[Dict[str, Any]]:
        """Detect external events and triggers"""
        # This would integrate with external systems
        return [
            {
                "type": "api_rate_limit",
                "severity": "medium",
                "message": "API rate limit approaching",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _send_alert(self, alert_data: Dict[str, Any]):
        """Send alert notification"""
        logger.warning("Alert generated", **alert_data)
        
        # Store alert in Redis
        redis_client = await get_redis()
        await redis_client.lpush("observer:alerts", json.dumps(alert_data))
        
        # Send to MCP server for coordination with other agents
        await self.mcp_client.send_message({
            "type": "alert",
            "source": "observer_agent",
            "data": alert_data
        })
    
    async def _process_alerts(self, alerts: List[Dict[str, Any]]):
        """Process generated alerts"""
        for alert in alerts:
            await self._send_alert(alert)
    
    async def _process_event(self, event: Dict[str, Any]):
        """Process detected event"""
        logger.info("Processing event", event=event)
        
        # Send event to MCP server for coordination
        await self.mcp_client.send_message({
            "type": "event",
            "source": "observer_agent",
            "data": event
        })
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Observer Agent status"""
        return {
            "agent_type": "observer",
            "status": "running" if self.is_running else "stopped",
            "monitoring_tasks": len(self.monitoring_tasks),
            "last_monitoring_cycle": datetime.now().isoformat(),
            "memory_usage": len(self.memory.chat_memory.messages)
        }
