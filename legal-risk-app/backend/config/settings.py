from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    anthropic_api_key: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/legal_docs.db"

    # Paths
    documents_path: Path = Path("./data/documents")
    images_path: Path = Path("./data/images")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Models
    summary_model: str = "claude-haiku-3-5-20241022"
    agent_model: str = "claude-sonnet-4-5-20250929"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Ensure directories exist
settings.documents_path.mkdir(parents=True, exist_ok=True)
settings.images_path.mkdir(parents=True, exist_ok=True)
