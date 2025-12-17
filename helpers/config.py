import os
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

load_dotenv()

@dataclass
class AppConfig(object):
    """Base configuration class."""

    logo_path: Path = Path(__file__).parent.parent / "assets" / "logo.png"
    icon_path: Path = Path(__file__).parent.parent / "assets" / "logo.png"
    agent_logo_path: Path = Path(__file__).parent.parent / "assets" / "agent-logo.png"
    favicon_path: Path = Path(__file__).parent.parent / "assets" / "favicon.ico"
    llm_logo_folder_path: Path = Path(__file__).parent.parent / "assets" / "images" / "llms"
    agent_logo_folder_path: Path = Path(__file__).parent.parent / "assets" / "images" / "agents"
    app_name: str = str(os.getenv("APP_NAME", ""))
    page_title: str = str(os.getenv("PAGE_TITLE", ""))
    
    log_max_size: int = int(os.getenv("LOG_MAX_SIZE", "10000000"))  # in bytes
    log_max_backups: int = int(os.getenv("LOG_MAX_BACKUPS", "5"))  # number of backup files
    
    app_jwt_key_name: str = os.getenv("APP_JWT_KEY_NAME", "")

class FileConfig(BaseModel):
    allowed_file_types: list[str] = Field(
        default_factory=lambda: os.getenv(
            "ALLOWED_FILE_TYPES", "txt,html,md,pdf,docx,doc,png,jpg,jpeg,csv,xlsx,xls"
        ).split(",")
    )
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))


@dataclass
class AWSConfig(object):
    """AWS configuration class."""

    aws_region: str = os.getenv("AWS_REGION", "us-southeast-1")
    aws_secret_name: str = os.getenv("AWS_SECRET_NAME", "")

@dataclass
class APIConfig(object):
    """Chat configuration class."""

    api_service: str = os.getenv("API_SERVICE", "")
    api_auth_key_name: str = os.getenv("API_AUTH_KEY_NAME", "")
    api_timeout_seconds: int = int(os.getenv("API_TIMEOUT_SECONDS", "300"))
    chat_model_support: List[str] = field(default_factory=lambda: ["claude", "llama", "gpt-oss"])
    max_response_tokens: int = int(os.getenv("MAX_RESPONSE_TOKENS", "512"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    top_p: float = float(os.getenv("TOP_P", "0.9"))

    """API service endpoint."""
    chat_agent_completions_endpoint: str = "chat/agent/completions"
    chat_feedback_endpoint: str = "chat/feedback"
    agent_endpoint: str = "agents/"
    llm_endpoint: str = "llms/"
    user_endpoint: str = "users/"
    role_endpoint: str = "roles/"
    tool_endpoint: str = "tools/"
    tag_endpoint:str = "tags/"
    login_endpoint: str = "authentication/login"

@dataclass
class LogConfig(object):
    """Logging configuration class."""

    log_max_size: str = os.getenv("LOG_MAX_SIZE", "10485760")  # 10 MB
    log_max_backups: str = os.getenv("LOG_MAX_BACKUPS", "5")    # 5 backup files