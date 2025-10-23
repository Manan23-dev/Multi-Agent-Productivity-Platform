"""
Configuration management for FlowAgent
"""

from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(0.7, env="OPENAI_TEMPERATURE")
    
    # LangChain Configuration
    langchain_tracing_v2: bool = Field(True, env="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(None, env="LANGCHAIN_API_KEY")
    langchain_project: str = Field("flowagent", env="LANGCHAIN_PROJECT")
    
    # MCP Server Configuration
    mcp_server_host: str = Field("localhost", env="MCP_SERVER_HOST")
    mcp_server_port: int = Field(8001, env="MCP_SERVER_PORT")
    mcp_server_protocol: str = Field("http", env="MCP_SERVER_PROTOCOL")
    
    # FastAPI Configuration
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_reload: bool = Field(True, env="API_RELOAD")
    api_workers: int = Field(4, env="API_WORKERS")
    
    # Security Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Celery Configuration
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    
    # Monitoring Configuration
    prometheus_port: int = Field(9090, env="PROMETHEUS_PORT")
    grafana_port: int = Field(3001, env="GRAFANA_PORT")
    
    # Agent Configuration
    observer_agent_interval: int = Field(30, env="OBSERVER_AGENT_INTERVAL")
    planner_agent_timeout: int = Field(60, env="PLANNER_AGENT_TIMEOUT")
    executor_agent_retry_count: int = Field(3, env="EXECUTOR_AGENT_RETRY_COUNT")
    
    # Development Configuration
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    environment: str = Field("development", env="ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
