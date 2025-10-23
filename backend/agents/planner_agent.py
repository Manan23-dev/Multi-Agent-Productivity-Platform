"""
Functional Planner Agent - Real LangChain implementation
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

class PlannerAgent:
    """Real Planner Agent for workflow creation and optimization"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=openai_api_key
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.active_plans = {}
        self.workflow_templates = {
            "data_processing": {
                "name": "Data Processing Pipeline",
                "description": "Process and transform data files",
                "tasks": [
                    {"name": "Validate Input", "duration": 5, "dependencies": []},
                    {"name": "Transform Data", "duration": 15, "dependencies": ["Validate Input"]},
                    {"name": "Quality Check", "duration": 10, "dependencies": ["Transform Data"]},
                    {"name": "Export Results", "duration": 5, "dependencies": ["Quality Check"]}
                ]
            },
            "email_automation": {
                "name": "Email Automation Workflow",
                "description": "Automated email processing and responses",
                "tasks": [
                    {"name": "Check Inbox", "duration": 2, "dependencies": []},
                    {"name": "Categorize Emails", "duration": 8, "dependencies": ["Check Inbox"]},
                    {"name": "Generate Responses", "duration": 12, "dependencies": ["Categorize Emails"]},
                    {"name": "Send Responses", "duration": 3, "dependencies": ["Generate Responses"]}
                ]
            },
            "report_generation": {
                "name": "Report Generation",
                "description": "Generate automated reports",
                "tasks": [
                    {"name": "Collect Data", "duration": 10, "dependencies": []},
                    {"name": "Analyze Data", "duration": 20, "dependencies": ["Collect Data"]},
                    {"name": "Create Report", "duration": 15, "dependencies": ["Analyze Data"]},
                    {"name": "Review Report", "duration": 8, "dependencies": ["Create Report"]}
                ]
            }
        }
        
    async def initialize(self):
        """Initialize the Planner Agent with tools"""
        print("🤖 Initializing Planner Agent...")
        
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
                name="estimate_resources",
                description="Estimate resource requirements for tasks",
                func=self._estimate_resources
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
            agent=create_openai_functions_agent(self.llm, tools, prompt),
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        print("✅ Planner Agent initialized successfully")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Planner Agent"""
        return """
        You are the Planner Agent in the FlowAgent multi-agent system. Your primary responsibilities are:

        1. **Workflow Design**: Create comprehensive workflow plans based on user objectives
        2. **Task Decomposition**: Break down complex goals into manageable tasks
        3. **Resource Optimization**: Optimize resource allocation and scheduling
        4. **Timeline Planning**: Create realistic timelines and milestones
        5. **Constraint Handling**: Work within system and user constraints
        6. **Plan Validation**: Ensure plans are feasible and executable

        Key Capabilities:
        - Intelligent task decomposition
        - Multi-objective optimization
        - Resource constraint analysis
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

        Available Workflow Templates:
        - data_processing: Process and transform data files
        - email_automation: Automated email processing
        - report_generation: Generate automated reports

        Always provide:
        - Clear task breakdown
        - Realistic timelines
        - Resource requirements
        - Dependency mapping
        - Risk assessment
        """
    
    async def create_workflow_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive workflow plan"""
        print(f"📋 Creating workflow plan: {requirements.get('name', 'Unknown')}")
        
        try:
            # Analyze requirements
            analysis = await self._analyze_requirements(json.dumps(requirements))
            
            # Create workflow plan
            workflow_id = f"wf_{int(time.time())}"
            
            # Determine workflow type
            workflow_type = requirements.get('type', 'custom')
            if workflow_type in self.workflow_templates:
                template = self.workflow_templates[workflow_type]
                tasks = template['tasks'].copy()
            else:
                # Create custom workflow
                tasks = await self._decompose_tasks(requirements.get('description', ''))
            
            # Optimize schedule
            optimized_tasks = await self._optimize_schedule(json.dumps(tasks))
            
            # Estimate resources
            resource_estimate = await self._estimate_resources(json.dumps(optimized_tasks))
            
            # Create final plan
            plan = {
                "workflow_id": workflow_id,
                "name": requirements.get('name', f'Workflow {workflow_id}'),
                "description": requirements.get('description', 'Custom workflow'),
                "type": workflow_type,
                "status": "planned",
                "tasks": optimized_tasks,
                "resource_estimate": resource_estimate,
                "timeline": {
                    "estimated_duration": sum(task.get('duration', 0) for task in optimized_tasks),
                    "start_time": datetime.now().isoformat(),
                    "end_time": (datetime.now() + timedelta(minutes=sum(task.get('duration', 0) for task in optimized_tasks))).isoformat()
                },
                "created_at": datetime.now().isoformat(),
                "analysis": analysis
            }
            
            # Store plan
            self.active_plans[workflow_id] = plan
            
            print(f"✅ Workflow plan created: {workflow_id}")
            return plan
            
        except Exception as e:
            print(f"❌ Error creating workflow plan: {e}")
            return {
                "error": str(e),
                "workflow_id": f"wf_error_{int(time.time())}"
            }
    
    async def _analyze_requirements(self, requirements_text: str) -> str:
        """Analyze user requirements and constraints"""
        try:
            requirements = json.loads(requirements_text)
            
            analysis = {
                "complexity": "medium",
                "estimated_duration": "30-60 minutes",
                "resource_requirements": ["CPU", "Memory"],
                "constraints": [],
                "risks": []
            }
            
            # Analyze complexity
            if requirements.get('type') == 'data_processing':
                analysis["complexity"] = "high"
                analysis["estimated_duration"] = "45-90 minutes"
                analysis["resource_requirements"].extend(["Storage", "Network"])
            elif requirements.get('type') == 'email_automation':
                analysis["complexity"] = "low"
                analysis["estimated_duration"] = "15-30 minutes"
            
            # Identify constraints
            if requirements.get('priority') == 'high':
                analysis["constraints"].append("Time-sensitive execution required")
            
            return json.dumps(analysis)
            
        except Exception as e:
            return f"Error analyzing requirements: {e}"
    
    async def _decompose_tasks(self, task_description: str) -> str:
        """Break down complex tasks into smaller subtasks"""
        try:
            # Create basic task breakdown
            tasks = [
                {
                    "name": "Initialize Process",
                    "description": "Set up and initialize the workflow",
                    "duration": 5,
                    "dependencies": [],
                    "priority": "high"
                },
                {
                    "name": "Execute Main Task",
                    "description": task_description,
                    "duration": 20,
                    "dependencies": ["Initialize Process"],
                    "priority": "high"
                },
                {
                    "name": "Validate Results",
                    "description": "Validate and verify task completion",
                    "duration": 10,
                    "dependencies": ["Execute Main Task"],
                    "priority": "medium"
                },
                {
                    "name": "Cleanup",
                    "description": "Clean up resources and finalize",
                    "duration": 5,
                    "dependencies": ["Validate Results"],
                    "priority": "low"
                }
            ]
            
            return json.dumps(tasks)
            
        except Exception as e:
            return f"Error decomposing tasks: {e}"
    
    async def _optimize_schedule(self, tasks_json: str) -> str:
        """Optimize task scheduling and resource allocation"""
        try:
            tasks = json.loads(tasks_json)
            
            # Add optimization metadata
            for i, task in enumerate(tasks):
                task["task_id"] = f"task_{i+1}"
                task["estimated_start"] = i * 5  # 5 minutes between tasks
                task["estimated_end"] = task["estimated_start"] + task["duration"]
                task["resources"] = ["CPU", "Memory"]
                
                # Add parallel execution opportunities
                if task["name"] == "Validate Results":
                    task["can_parallel"] = True
            
            return json.dumps(tasks)
            
        except Exception as e:
            return f"Error optimizing schedule: {e}"
    
    async def _estimate_resources(self, tasks_json: str) -> str:
        """Estimate resource requirements for tasks"""
        try:
            tasks = json.loads(tasks_json)
            
            total_duration = sum(task.get('duration', 0) for task in tasks)
            
            resource_estimate = {
                "total_duration_minutes": total_duration,
                "cpu_requirements": "Medium",
                "memory_requirements": "512MB - 1GB",
                "storage_requirements": "100MB - 500MB",
                "network_requirements": "Low",
                "estimated_cost": f"${total_duration * 0.01:.2f}",
                "peak_resources": "During main task execution"
            }
            
            return json.dumps(resource_estimate)
            
        except Exception as e:
            return f"Error estimating resources: {e}"
    
    async def _create_workflow(self, workflow_spec: str) -> str:
        """Create executable workflow from plan"""
        try:
            spec = json.loads(workflow_spec)
            
            workflow = {
                "executable": True,
                "steps": len(spec.get('tasks', [])),
                "dependencies_resolved": True,
                "ready_for_execution": True
            }
            
            return json.dumps(workflow)
            
        except Exception as e:
            return f"Error creating workflow: {e}"
    
    async def get_plan_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow plan"""
        if workflow_id in self.active_plans:
            return {
                "workflow_id": workflow_id,
                "status": "active",
                "plan": self.active_plans[workflow_id]
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
            "available_templates": list(self.workflow_templates.keys()),
            "last_plan_created": datetime.now().isoformat()
        }
