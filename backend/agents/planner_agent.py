"""
Planner Agent - Creates and optimizes workflows
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

class PlannerAgent:
    """Planner Agent for workflow creation and optimization"""
    
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
        self.active_plans: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self):
        """Initialize the Planner Agent"""
        logger.info("Initializing Planner Agent")
        
        # Define planning tools
        tools = [
            Tool(
                name="analyze_requirements",
                description="Analyze user requirements and constraints",
                func=self._analyze_requirements
            ),
            Tool(
                name="decompose_tasks",
                description="Break down complex tasks into smaller subtasks",
                func=self._decompose_tasks
            ),
            Tool(
                name="optimize_schedule",
                description="Optimize task scheduling and resource allocation",
                func=self._optimize_schedule
            ),
            Tool(
                name="check_dependencies",
                description="Check task dependencies and constraints",
                func=self._check_dependencies
            ),
            Tool(
                name="estimate_resources",
                description="Estimate resource requirements for tasks",
                func=self._estimate_resources
            ),
            Tool(
                name="validate_plan",
                description="Validate workflow plan for feasibility",
                func=self._validate_plan
            ),
            Tool(
                name="create_workflow",
                description="Create executable workflow from plan",
                func=self._create_workflow
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
        
        logger.info("Planner Agent initialized successfully")
    
    def _create_agent(self, prompt, tools):
        """Create the agent with tools and prompt"""
        from langchain.agents import create_openai_functions_agent
        
        return create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Planner Agent"""
        return """
        You are the Planner Agent in the FlowAgent multi-agent system. Your primary responsibilities are:

        1. **Workflow Design**: Create comprehensive workflow plans based on user objectives
        2. **Task Decomposition**: Break down complex goals into manageable tasks
        3. **Resource Optimization**: Optimize resource allocation and scheduling
        4. **Dependency Management**: Identify and manage task dependencies
        5. **Timeline Planning**: Create realistic timelines and milestones
        6. **Constraint Handling**: Work within system and user constraints
        7. **Plan Validation**: Ensure plans are feasible and executable

        Key Capabilities:
        - Intelligent task decomposition
        - Multi-objective optimization
        - Resource constraint analysis
        - Dependency graph creation
        - Timeline optimization
        - Risk assessment and mitigation
        - Plan validation and refinement

        Planning Process:
        1. Analyze user requirements and objectives
        2. Identify constraints and limitations
        3. Decompose complex tasks into subtasks
        4. Determine task dependencies
        5. Estimate resource requirements
        6. Optimize scheduling and allocation
        7. Validate plan feasibility
        8. Create executable workflow

        Always consider:
        - Available resources and capabilities
        - Time constraints and deadlines
        - Task dependencies and prerequisites
        - Risk factors and mitigation strategies
        - User preferences and constraints
        - System limitations and capabilities

        Provide clear, actionable plans with detailed task breakdowns and realistic timelines.
        """
    
    async def create_workflow_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive workflow plan"""
        logger.info("Creating workflow plan", requirements=requirements)
        
        planning_prompt = f"""
        Create a comprehensive workflow plan based on the following requirements:
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Please provide a detailed plan including:
        1. Task decomposition
        2. Resource requirements
        3. Timeline and milestones
        4. Dependencies
        5. Risk assessment
        6. Success criteria
        
        Format your response as a JSON object with the following structure:
        {{
            "workflow_id": "unique_workflow_id",
            "name": "workflow_name",
            "description": "workflow_description",
            "objectives": ["objective1", "objective2"],
            "tasks": [
                {{
                    "task_id": "task_1",
                    "name": "task_name",
                    "description": "task_description",
                    "type": "task_type",
                    "priority": "high|medium|low",
                    "estimated_duration": "duration_in_minutes",
                    "resources_required": ["resource1", "resource2"],
                    "dependencies": ["task_id"],
                    "success_criteria": ["criteria1", "criteria2"]
                }}
            ],
            "timeline": {{
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "milestones": [
                    {{
                        "name": "milestone_name",
                        "date": "YYYY-MM-DD",
                        "tasks": ["task_id1", "task_id2"]
                    }}
                ]
            }},
            "resources": {{
                "human": ["role1", "role2"],
                "technical": ["tool1", "tool2"],
                "external": ["service1", "service2"]
            }},
            "risks": [
                {{
                    "risk": "risk_description",
                    "probability": "low|medium|high",
                    "impact": "low|medium|high",
                    "mitigation": "mitigation_strategy"
                }}
            ],
            "success_metrics": ["metric1", "metric2"]
        }}
        """
        
        try:
            response = await self.agent_executor.ainvoke({"input": planning_prompt})
            plan = json.loads(response["output"])
            
            # Store plan in Redis
            redis_client = await get_redis()
            await redis_client.setex(
                f"planner:plan:{plan['workflow_id']}",
                3600,  # 1 hour
                json.dumps(plan)
            )
            
            # Store in active plans
            self.active_plans[plan["workflow_id"]] = plan
            
            logger.info("Workflow plan created", workflow_id=plan["workflow_id"])
            return plan
            
        except Exception as e:
            logger.error("Error creating workflow plan", error=str(e))
            raise
    
    async def optimize_workflow(self, workflow_id: str, optimization_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize an existing workflow"""
        logger.info("Optimizing workflow", workflow_id=workflow_id, criteria=optimization_criteria)
        
        # Get current plan
        redis_client = await get_redis()
        plan_data = await redis_client.get(f"planner:plan:{workflow_id}")
        
        if not plan_data:
            raise ValueError(f"Workflow plan {workflow_id} not found")
        
        current_plan = json.loads(plan_data)
        
        optimization_prompt = f"""
        Optimize the following workflow plan based on the optimization criteria:
        
        Current Plan:
        {json.dumps(current_plan, indent=2)}
        
        Optimization Criteria:
        {json.dumps(optimization_criteria, indent=2)}
        
        Please provide an optimized version of the plan focusing on:
        1. Improved efficiency and resource utilization
        2. Reduced timeline where possible
        3. Better risk mitigation
        4. Enhanced success probability
        
        Return the optimized plan in the same JSON format as the original plan.
        """
        
        try:
            response = await self.agent_executor.ainvoke({"input": optimization_prompt})
            optimized_plan = json.loads(response["output"])
            
            # Update stored plan
            await redis_client.setex(
                f"planner:plan:{workflow_id}",
                3600,
                json.dumps(optimized_plan)
            )
            
            # Update active plans
            self.active_plans[workflow_id] = optimized_plan
            
            logger.info("Workflow optimized", workflow_id=workflow_id)
            return optimized_plan
            
        except Exception as e:
            logger.error("Error optimizing workflow", error=str(e))
            raise
    
    async def _analyze_requirements(self, requirements_text: str) -> str:
        """Analyze user requirements and constraints"""
        # This would perform detailed requirement analysis
        return f"Analyzed requirements: {requirements_text}"
    
    async def _decompose_tasks(self, task_description: str) -> str:
        """Break down complex tasks into smaller subtasks"""
        # This would perform task decomposition
        return f"Decomposed task: {task_description}"
    
    async def _optimize_schedule(self, schedule_data: str) -> str:
        """Optimize task scheduling and resource allocation"""
        # This would perform schedule optimization
        return f"Optimized schedule: {schedule_data}"
    
    async def _check_dependencies(self, task_list: str) -> str:
        """Check task dependencies and constraints"""
        # This would check dependencies
        return f"Checked dependencies for: {task_list}"
    
    async def _estimate_resources(self, resource_requirements: str) -> str:
        """Estimate resource requirements for tasks"""
        # This would estimate resources
        return f"Estimated resources: {resource_requirements}"
    
    async def _validate_plan(self, plan_data: str) -> str:
        """Validate workflow plan for feasibility"""
        # This would validate the plan
        return f"Validated plan: {plan_data}"
    
    async def _create_workflow(self, workflow_spec: str) -> str:
        """Create executable workflow from plan"""
        # This would create the workflow
        return f"Created workflow: {workflow_spec}"
    
    async def get_plan_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow plan"""
        if workflow_id in self.active_plans:
            return {
                "workflow_id": workflow_id,
                "status": "active",
                "plan": self.active_plans[workflow_id]
            }
        
        redis_client = await get_redis()
        plan_data = await redis_client.get(f"planner:plan:{workflow_id}")
        
        if plan_data:
            return {
                "workflow_id": workflow_id,
                "status": "stored",
                "plan": json.loads(plan_data)
            }
        
        return {
            "workflow_id": workflow_id,
            "status": "not_found"
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Planner Agent status"""
        return {
            "agent_type": "planner",
            "status": "active",
            "active_plans": len(self.active_plans),
            "memory_usage": len(self.memory.chat_memory.messages),
            "last_plan_created": datetime.now().isoformat()
        }
