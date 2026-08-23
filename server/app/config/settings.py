import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered College Information Assistant"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Server & Environment
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    
    # Use Union[str, List[str]] so pydantic-settings does not force json.loads on comma-separated env strings
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def format_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean.startswith("[") and v_clean.endswith("]"):
                try:
                    parsed = json.loads(v_clean)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed]
                except Exception:
                    pass
            return [origin.strip() for origin in v_clean.split(",") if origin.strip()]
        return v
    
    # Authentication & JWT
    JWT_SECRET: str = "supersecretcollegeinformationassistantjwtkey2026!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./college_rag.db"
    
    # AI & RAG Configuration
    LLM_PROVIDER: str = "gemini"  # "gemini", "openai", "local"
    EMBEDDING_PROVIDER: str = "gemini"  # "gemini", "openai", "local"
    
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # RAG Hyperparameters
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 80
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.40
    HYBRID_SEARCH: bool = True
    
    # Upload Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: Union[str, List[str]] = [".pdf", ".docx", ".doc", ".txt", ".md"]

    @field_validator("ALLOWED_EXTENSIONS", mode="after")
    @classmethod
    def format_allowed_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean.startswith("[") and v_clean.endswith("]"):
                try:
                    parsed = json.loads(v_clean)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed]
                except Exception:
                    pass
            return [ext.strip() for ext in v_clean.split(",") if ext.strip()]
        return v

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
