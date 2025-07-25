"""
Core configuration and settings for VizLearn
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "VizLearn API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM Configuration
    llm_base_url: str = "http://localhost:1234/v1"
    llm_api_key: str = "sk-not-needed"
    llm_model: str = "local-model"
    llm_timeout: float = 30.0
    llm_max_retries: int = 2
    
    # Authentication
    static_api_key: str = "vizlearn-static-key-2025"
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    
    # Search Configuration
    enable_web_search: bool = True
    search_max_results: int = 5
    search_timeout: float = 10.0
    
    # Content Generation Limits
    max_questions_per_request: int = 20
    default_questions_count: int = 5
    
    def get_allowed_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set USER_AGENT if not already set
        if not os.getenv("USER_AGENT"):
            os.environ["USER_AGENT"] = f"{self.app_name}/{self.app_version}"


# Global settings instance
settings = Settings()
