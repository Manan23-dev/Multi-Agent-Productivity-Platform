"""
Database models for FlowAgent
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflows = relationship("Workflow", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")

class Workflow(Base):
    """Workflow model"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="draft")  # draft, active, completed, failed
    workflow_data = Column(JSON)  # Store workflow plan
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    owner = relationship("User", back_populates="workflows")
    tasks = relationship("Task", back_populates="workflow")

class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    priority = Column(String(20), default="medium")  # low, medium, high
    task_type = Column(String(100))
    task_data = Column(JSON)  # Store task-specific data
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_duration = Column(Integer)  # in minutes
    actual_duration = Column(Integer)  # in minutes
    
    # Relationships
    workflow = relationship("Workflow", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")

class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    agent_type = Column(String(50), nullable=False)  # observer, planner, executor
    status = Column(String(50), default="inactive")  # active, inactive, error
    config = Column(JSON)  # Agent configuration
    last_heartbeat = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionLog(Base):
    """Execution log model"""
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(255), unique=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    status = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Integer)  # in seconds
    error_message = Column(Text)
    execution_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow")
    agent = relationship("Agent")

class SystemMetric(Base):
    """System metrics model"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(String(255), nullable=False)
    metric_type = Column(String(50))  # counter, gauge, histogram
    tags = Column(JSON)  # Additional tags
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Index for efficient querying
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )
