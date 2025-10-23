"""
Executor Agent - Executes planned tasks and manages workflow execution
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

class ExecutorAgent:
    """Executor Agent for task execution and workflow management"""
    
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
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        
    async def initialize(self):
        """Initialize the Executor Agent"""
        logger.info("Initializing Executor Agent")
        
        # Define execution tools
        tools = [
            Tool(
                name="execute_task",
                description="Execute a specific task",
                func=self._execute_task
            ),
            Tool(
                name="check_task_status",
                description="Check the status of a running task",
                func=self._check_task_status
            ),
            Tool(
                name="handle_task_failure",
                description="Handle task execution failures",
                func=self._handle_task_failure
            ),
            Tool(
                name="allocate_resources",
                description="Allocate resources for task execution",
                func=self._allocate_resources
            ),
            Tool(
                name="monitor_progress",
                description="Monitor task execution progress",
                func=self._monitor_progress
            ),
            Tool(
                name="report_results",
                description="Report task execution results",
                func=self._report_results
            ),
            Tool(
                name="schedule_follow_up",
                description="Schedule follow-up tasks",
                func=self._schedule_follow_up
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
        
        # Start execution loop
        asyncio.create_task(self._execution_loop())
        
        logger.info("Executor Agent initialized successfully")
    
    def _create_agent(self, prompt, tools):
        """Create the agent with tools and prompt"""
        from langchain.agents import create_openai_functions_agent
        
        return create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Executor Agent"""
        return """
        You are the Executor Agent in the FlowAgent multi-agent system. Your primary responsibilities are:

        1. **Task Execution**: Execute planned tasks according to specifications
        2. **Workflow Management**: Manage workflow execution and coordination
        3. **Resource Management**: Allocate and manage resources for task execution
        4. **Progress Monitoring**: Monitor task progress and provide updates
        5. **Error Handling**: Handle failures and implement recovery strategies
        6. **Result Reporting**: Report execution results and outcomes
        7. **Follow-up Management**: Schedule and execute follow-up tasks

        Key Capabilities:
        - Intelligent task execution
        - Resource optimization
        - Progress tracking and reporting
        - Error handling and recovery
        - Performance monitoring
        - Result validation
        - Follow-up automation

        Execution Process:
        1. Receive task specifications
        2. Allocate required resources
        3. Execute task according to plan
        4. Monitor progress continuously
        5. Handle any errors or issues
        6. Validate results
        7. Report outcomes
        8. Schedule follow-ups if needed

        Always ensure:
        - Tasks are executed efficiently and accurately
        - Resources are used optimally
        - Progress is tracked and reported
        - Errors are handled gracefully
        - Results meet quality standards
        - Follow-ups are scheduled appropriately

        Provide clear execution reports with detailed progress updates and outcome summaries.
        """
    
    async def execute_workflow(self, workflow_id: str, workflow_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete workflow"""
        logger.info("Executing workflow", workflow_id=workflow_id)
        
        execution_id = f"exec_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        execution_context = {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "plan": workflow_plan,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "completed_tasks": [],
            "failed_tasks": [],
            "current_task": None,
            "progress": 0.0
        }
        
        self.active_executions[execution_id] = execution_context
        
        try:
            # Execute workflow tasks in order
            tasks = workflow_plan.get("tasks", [])
            total_tasks = len(tasks)
            
            for i, task in enumerate(tasks):
                task_id = task["task_id"]
                execution_context["current_task"] = task_id
                execution_context["progress"] = (i / total_tasks) * 100
                
                logger.info("Executing task", task_id=task_id, progress=f"{execution_context['progress']:.1f}%")
                
                # Execute task
                task_result = await self._execute_single_task(task, execution_context)
                
                if task_result["status"] == "success":
                    execution_context["completed_tasks"].append(task_id)
                else:
                    execution_context["failed_tasks"].append({
                        "task_id": task_id,
                        "error": task_result.get("error"),
                        "retry_count": task_result.get("retry_count", 0)
                    })
                    
                    # Handle task failure
                    await self._handle_task_failure(task, task_result, execution_context)
            
            # Complete execution
            execution_context["status"] = "completed"
            execution_context["end_time"] = datetime.now().isoformat()
            execution_context["progress"] = 100.0
            
            # Generate execution report
            execution_report = await self._generate_execution_report(execution_context)
            
            # Store results
            redis_client = await get_redis()
            await redis_client.setex(
                f"executor:execution:{execution_id}",
                86400,  # 24 hours
                json.dumps(execution_context)
            )
            
            logger.info("Workflow execution completed", execution_id=execution_id)
            return execution_report
            
        except Exception as e:
            logger.error("Error executing workflow", execution_id=execution_id, error=str(e))
            execution_context["status"] = "failed"
            execution_context["error"] = str(e)
            execution_context["end_time"] = datetime.now().isoformat()
            raise
    
    async def _execute_single_task(self, task: Dict[str, Any], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        task_id = task["task_id"]
        
        execution_prompt = f"""
        Execute the following task:
        
        Task Details:
        {json.dumps(task, indent=2)}
        
        Execution Context:
        {json.dumps(execution_context, indent=2)}
        
        Please provide execution details including:
        1. Resource allocation
        2. Execution steps
        3. Progress updates
        4. Result validation
        5. Any issues encountered
        
        Format your response as JSON:
        {{
            "status": "success|failed|retry",
            "execution_time": "duration_in_seconds",
            "resources_used": ["resource1", "resource2"],
            "output": "task_output_or_result",
            "error": "error_message_if_failed",
            "retry_count": 0,
            "next_steps": ["step1", "step2"]
        }}
        """
        
        try:
            response = await self.agent_executor.ainvoke({"input": execution_prompt})
            result = json.loads(response["output"])
            
            # Simulate task execution time
            await asyncio.sleep(1)  # Replace with actual task execution
            
            return result
            
        except Exception as e:
            logger.error("Error executing task", task_id=task_id, error=str(e))
            return {
                "status": "failed",
                "error": str(e),
                "retry_count": 0
            }
    
    async def _execution_loop(self):
        """Main execution loop for processing queued tasks"""
        while True:
            try:
                # Process queued tasks
                if not self.task_queue.empty():
                    task_data = await self.task_queue.get()
                    await self._process_queued_task(task_data)
                
                # Monitor active executions
                await self._monitor_active_executions()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error("Error in execution loop", error=str(e))
                await asyncio.sleep(10)
    
    async def _process_queued_task(self, task_data: Dict[str, Any]):
        """Process a queued task"""
        logger.info("Processing queued task", task_data=task_data)
        
        # Execute the task
        result = await self._execute_single_task(task_data, {})
        
        # Report results
        await self._report_results(result)
    
    async def _monitor_active_executions(self):
        """Monitor active workflow executions"""
        for execution_id, execution_context in self.active_executions.items():
            if execution_context["status"] == "running":
                # Update progress and check for issues
                await self._update_execution_progress(execution_id, execution_context)
    
    async def _update_execution_progress(self, execution_id: str, execution_context: Dict[str, Any]):
        """Update execution progress"""
        # This would update progress based on actual task execution
        pass
    
    async def _execute_task(self, task_spec: str) -> str:
        """Execute a specific task"""
        return f"Executed task: {task_spec}"
    
    async def _check_task_status(self, task_id: str) -> str:
        """Check the status of a running task"""
        return f"Task {task_id} status: running"
    
    async def _handle_task_failure(self, task: Dict[str, Any], error_result: Dict[str, Any], execution_context: Dict[str, Any]) -> str:
        """Handle task execution failures"""
        logger.warning("Handling task failure", task_id=task["task_id"], error=error_result.get("error"))
        
        # Implement retry logic
        retry_count = error_result.get("retry_count", 0)
        max_retries = self.settings.executor_agent_retry_count
        
        if retry_count < max_retries:
            # Retry the task
            logger.info("Retrying task", task_id=task["task_id"], retry_count=retry_count + 1)
            
            # Add retry delay
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            
            # Re-execute task
            retry_result = await self._execute_single_task(task, execution_context)
            retry_result["retry_count"] = retry_count + 1
            
            return f"Retried task {task['task_id']}, result: {retry_result['status']}"
        else:
            # Max retries exceeded
            logger.error("Task failed after max retries", task_id=task["task_id"])
            return f"Task {task['task_id']} failed after {max_retries} retries"
    
    async def _allocate_resources(self, resource_requirements: str) -> str:
        """Allocate resources for task execution"""
        return f"Allocated resources: {resource_requirements}"
    
    async def _monitor_progress(self, task_id: str) -> str:
        """Monitor task execution progress"""
        return f"Monitoring progress for task: {task_id}"
    
    async def _report_results(self, execution_result: Dict[str, Any]) -> str:
        """Report task execution results"""
        logger.info("Reporting execution results", result=execution_result)
        
        # Send results to MCP server
        await self.mcp_client.send_message({
            "type": "execution_result",
            "source": "executor_agent",
            "data": execution_result
        })
        
        return f"Reported results: {execution_result['status']}"
    
    async def _schedule_follow_up(self, follow_up_data: str) -> str:
        """Schedule follow-up tasks"""
        return f"Scheduled follow-up: {follow_up_data}"
    
    async def _generate_execution_report(self, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive execution report"""
        report = {
            "execution_id": execution_context["execution_id"],
            "workflow_id": execution_context["workflow_id"],
            "status": execution_context["status"],
            "start_time": execution_context["start_time"],
            "end_time": execution_context.get("end_time"),
            "duration": self._calculate_duration(
                execution_context["start_time"],
                execution_context.get("end_time")
            ),
            "total_tasks": len(execution_context["plan"].get("tasks", [])),
            "completed_tasks": len(execution_context["completed_tasks"]),
            "failed_tasks": len(execution_context["failed_tasks"]),
            "success_rate": (
                len(execution_context["completed_tasks"]) / 
                len(execution_context["plan"].get("tasks", [])) * 100
                if execution_context["plan"].get("tasks") else 0
            ),
            "progress": execution_context["progress"],
            "summary": {
                "completed": execution_context["completed_tasks"],
                "failed": execution_context["failed_tasks"],
                "errors": execution_context.get("errors", [])
            }
        }
        
        return report
    
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate execution duration"""
        if not end_time:
            return "ongoing"
        
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration = end - start
        
        return str(duration)
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status of a workflow execution"""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        
        redis_client = await get_redis()
        execution_data = await redis_client.get(f"executor:execution:{execution_id}")
        
        if execution_data:
            return json.loads(execution_data)
        
        return {"status": "not_found"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Executor Agent status"""
        return {
            "agent_type": "executor",
            "status": "active",
            "active_executions": len(self.active_executions),
            "queued_tasks": self.task_queue.qsize(),
            "memory_usage": len(self.memory.chat_memory.messages),
            "last_execution": datetime.now().isoformat()
        }
