# config/settings.py
import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
import json

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    db_path: str = Field(default="data/knowledge_repr.db", env="DATABASE_PATH")
    backup_path: str = Field(default="data/backups", env="DATABASE_BACKUP_PATH")
    auto_backup: bool = Field(default=False, env="DATABASE_AUTO_BACKUP")
    backup_interval_hours: int = Field(default=24, env="DATABASE_BACKUP_INTERVAL")
    
    class Config:
        env_prefix = "DB_"

class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI configuration settings"""
    api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    deployment: str = Field(default="gpt-4.1-nano", env="AZURE_OPENAI_DEPLOYMENT")
    api_version: str = Field(default="2024-12-01-preview", env="AZURE_OPENAI_API_VERSION")
    
    # Model parameters
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, env="TEMPERATURE")
    max_tokens: int = Field(default=800, ge=1, le=4000, env="MAX_TOKENS")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, env="TOP_P")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, env="FREQUENCY_PENALTY")
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, env="PRESENCE_PENALTY")
    
    class Config:
        env_prefix = "AZURE_OPENAI_"

class AppSettings(BaseSettings):
    """Application configuration settings"""
    title: str = Field(default="Knowledge Representation Engine", env="APP_TITLE")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    session_timeout_hours: int = Field(default=24, env="SESSION_TIMEOUT_HOURS")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    max_query_length: int = Field(default=10000, env="MAX_QUERY_LENGTH")
    max_context_length: int = Field(default=5000, env="MAX_CONTEXT_LENGTH")
    
    # File uploads
    max_upload_size_mb: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    allowed_file_types: list = Field(default=["json", "txt", "md", "csv"], env="ALLOWED_FILE_TYPES")
    
    class Config:
        env_prefix = "APP_"

class UISettings(BaseSettings):
    """UI and UX configuration settings"""
    theme: str = Field(default="modern", env="UI_THEME")
    default_representation_mode: str = Field(default="plain_text", env="DEFAULT_REPRESENTATION_MODE")
    enable_animations: bool = Field(default=True, env="ENABLE_ANIMATIONS")
    auto_save_preferences: bool = Field(default=True, env="AUTO_SAVE_PREFERENCES")
    
    # Display settings
    items_per_page: int = Field(default=20, env="ITEMS_PER_PAGE")
    max_recent_conversations: int = Field(default=50, env="MAX_RECENT_CONVERSATIONS")
    
    class Config:
        env_prefix = "UI_"

class SecuritySettings(BaseSettings):
    """Security configuration settings"""
    enable_cors: bool = Field(default=True, env="ENABLE_CORS")
    allowed_origins: list = Field(default=["*"], env="ALLOWED_ORIGINS")
    enable_authentication: bool = Field(default=False, env="ENABLE_AUTHENTICATION")
    admin_username: str = Field(default="admin", env="ADMIN_USERNAME")
    admin_password_hash: str = Field(default="", env="ADMIN_PASSWORD_HASH")
    
    # API Security
    require_api_key: bool = Field(default=False, env="REQUIRE_API_KEY")
    api_key: str = Field(default="", env="API_KEY")
    
    class Config:
        env_prefix = "SECURITY_"

class AnalyticsSettings(BaseSettings):
    """Analytics and monitoring configuration"""
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    enable_detailed_logging: bool = Field(default=False, env="ENABLE_DETAILED_LOGGING")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Data retention
    conversation_retention_days: int = Field(default=365, env="CONVERSATION_RETENTION_DAYS")
    log_retention_days: int = Field(default=90, env="LOG_RETENTION_DAYS")
    
    # Cost tracking
    enable_cost_tracking: bool = Field(default=True, env="ENABLE_COST_TRACKING")
    cost_per_1k_prompt_tokens: float = Field(default=0.01, env="COST_PER_1K_PROMPT_TOKENS")
    cost_per_1k_completion_tokens: float = Field(default=0.02, env="COST_PER_1K_COMPLETION_TOKENS")
    
    class Config:
        env_prefix = "ANALYTICS_"

class Settings(BaseSettings):
    """Main application settings"""

    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    azure_openai: AzureOpenAISettings = AzureOpenAISettings()
    ui: UISettings = UISettings()
    security: SecuritySettings = SecuritySettings()
    analytics: AnalyticsSettings = AnalyticsSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # 👈 Add this line


class ConfigManager:
    """Configuration management utility"""
    
    def __init__(self, config_file: str = "data/app_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(exist_ok=True)
        self._cache = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._cache = json.load(f)
            else:
                self._cache = self._get_default_config()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._cache = self._get_default_config()
        
        return self._cache
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._cache
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        keys = key.split('.')
        config = self._cache
        
        try:
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            return self.save_config()
        except Exception as e:
            print(f"Error setting config value: {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        try:
            for key, value in updates.items():
                self.set(key, value)
            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        self._cache = self._get_default_config()
        return self.save_config()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get entire configuration as dictionary"""
        return self._cache.copy()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "app": {
                "title": "Knowledge Representation Engine",
                "version": "1.0.0",
                "debug": False,
                "max_query_length": 10000,
                "max_context_length": 5000,
                "rate_limit_per_minute": 60
            },
            "ui": {
                "theme": "modern",
                "default_representation_mode": "plain_text",
                "enable_animations": True,
                "items_per_page": 20,
                "auto_save_preferences": True
            },
            "database": {
                "auto_backup": False,
                "backup_interval_hours": 24,
                "conversation_retention_days": 365
            },
            "analytics": {
                "enable_analytics": True,
                "enable_detailed_logging": False,
                "enable_cost_tracking": True,
                "cost_per_1k_prompt_tokens": 0.01,
                "cost_per_1k_completion_tokens": 0.02
            },
            "security": {
                "enable_cors": True,
                "allowed_origins": ["*"],
                "enable_authentication": False,
                "require_api_key": False
            },
            "representations": {
                "enabled_modes": [
                    "plain_text",
                    "color_coded",
                    "collapsible_concepts", 
                    "knowledge_graph",
                    "analogical",
                    "persona_eli5",
                    "persona_expert",
                    "timeline",
                    "summary",
                    "detailed"
                ],
                "default_preferences": {
                    "visual_style": "modern",
                    "complexity_level": "medium",
                    "color_scheme": "light"
                }
            }
        }

# Global configuration instance
config = Settings()
config_manager = ConfigManager()

def get_settings() -> Settings:
    """Get application settings"""
    return config

def get_config_manager() -> ConfigManager:
    """Get configuration manager"""
    return config_manager

def validate_environment() -> Dict[str, bool]:
    """Validate environment configuration"""
    validation = {
        "azure_openai_configured": bool(config.azure_openai.api_key and config.azure_openai.endpoint),
        "database_accessible": True,  # Would check database connectivity
        "required_directories": True,  # Would check if required directories exist
        "file_permissions": True,  # Would check file write permissions
    }
    
    # Create required directories
    required_dirs = ["data", "data/backups", "data/exports", "data/uploads", "logs"]
    for dir_path in required_dirs:
        Path(dir_path).mkdir(exist_ok=True)
    
    return validation

def get_environment_info() -> Dict[str, Any]:
    """Get environment information"""
    return {
        "python_version": os.sys.version,
        "platform": os.name,
        "working_directory": os.getcwd(),
        "environment_variables": {
            "AZURE_OPENAI_CONFIGURED": bool(os.getenv("AZURE_OPENAI_API_KEY")),
            "DEBUG_MODE": config.app.debug,
            "DATABASE_PATH": config.database.db_path
        },
        "validation": validate_environment()
    }
