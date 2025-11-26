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

    logo_path: Path = Path(__file__).parent.parent / "assets" / "logo-2.png"
    icon_path: Path = Path(__file__).parent.parent / "assets" / "logo.png"
    favicon_path: Path = Path(__file__).parent.parent / "assets" / "favicon.ico"
    
    app_name: str = str(os.getenv("APP_NAME", ""))
    page_title: str = str(os.getenv("PAGE_TITLE", ""))
    
    log_max_size: int = int(os.getenv("LOG_MAX_SIZE", "10000000"))  # in bytes
    log_max_backups: int = int(os.getenv("LOG_MAX_BACKUPS", "5"))  # number of backup files
    
    jwt_key_name: str = os.getenv("JWT_KEY_NAME", "cell_jwt_secret_key")

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
    tool_endpoint: str = "tools/"
    login_endpoint: str = "authentication/login"

@dataclass
class LogConfig(object):
    """Logging configuration class."""

    log_max_size: str = os.getenv("LOG_MAX_SIZE", "10485760")  # 10 MB
    log_max_backups: str = os.getenv("LOG_MAX_BACKUPS", "5")    # 5 backup files

@dataclass
class ToolInfo:
    """Agent tool information."""
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    logo: str = "🛠️"

@dataclass
class AWSBedrockModelInfo:
    "AWS Bedrock model information."
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    logo: str = "🧠"

class ToolDescription:
    """Centralized tool metadata for display & documentation."""

    DATA = {
        "Arxiv": {
            "description": "Search academic papers and preprints from arXiv.",
            "tags": ["Research", "Academic"],
            "logo": "📚",
        },
        "AskNews": {
            "description": "Fetch the latest breaking news from various sources.",
            "tags": ["News", "Trending"],
            "logo": "🗞️",
        },
        "DuckDuckGo": {
            "description": "Privacy-focused general-purpose web search.",
            "tags": ["Search", "Web"],
            "logo": "🦆",
        },
        "GoogleSearch": {
            "description": "Comprehensive Google-powered web search.",
            "tags": ["Search", "Web"],
            "logo": "🌐",
        },
        "GoogleScholar": {
            "description": "Search scholarly publications and citations.",
            "tags": ["Research", "Academic"],
            "logo": "🎓",
        },
        "GoogleTrends": {
            "description": "Analyze trending search queries and interest over time.",
            "tags": ["Analytics", "Search"],
            "logo": "📈",
        },
        "RedditSearch": {
            "description": "Find community discussions and opinions from Reddit.",
            "tags": ["Community", "Social"],
            "logo": "💬",
        },
        "SearxSearch": {
            "description": "Meta search engine combining results from multiple sources.",
            "tags": ["Search", "Meta"],
            "logo": "🕸️",
        },
        "Weather": {
            "description": "Check current and forecasted weather conditions.",
            "tags": ["Utility", "Environment"],
            "logo": "⛅",
        },
        "Wikipedia": {
            "description": "Retrieve general knowledge, summaries, and definitions.",
            "tags": ["Knowledge", "Reference"],
            "logo": "📖",
        },
    }

class AWSBedrockModelDescription:
    """Central registry of AWS Bedrock foundation models."""

    DATA = {
        "Claude": {
            "description": (
                "Anthropic Claude is a family of advanced reasoning language models "
                "optimized for safety, reliability, and long-context reasoning. "
                "Ideal for general-purpose chat, document analysis, and secure LLM applications."
            ),
            "tags": ["Anthropic", "Reasoning", "Conversational"],
            "logo": "👾",
        },
        "GPT-OSS": {
            "description": (
                "GPT OSS models are open-source large language models hosted on AWS Bedrock. "
                "They provide customizable performance for text generation, code, and creative tasks."
            ),
            "tags": ["Open Source", "Text Generation", "Flexible"],
            "logo": "🧩",
        },
        "Llama": {
            "description": (
                "Meta’s Llama models deliver high performance for chat, reasoning, and multi-language use cases. "
                "They are efficient and fine-tuned for enterprise-grade workloads on Bedrock."
            ),
            "tags": ["Meta", "Efficient", "Multilingual"],
            "logo": "🦙",
        },
    }