from typing import List, Optional
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Meeting AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    WORKERS: int = Field(default=1)

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=0)

    # Redis
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # AWS
    AWS_REGION: str = Field(default="us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_ENDPOINT_URL: Optional[str] = None
    S3_BUCKET_RAW_AUDIO: str
    S3_BUCKET_PROCESSED: str
    S3_BUCKET_LOGS: str

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    WHISPER_MODEL: str = Field(default="whisper-1")

    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash-exp")

    # Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # CORS
    CORS_ORIGINS: List[str] = Field(default_factory=list)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)

    # Vector Search
    VECTOR_DIMENSION: int = Field(default=1536)
    VECTOR_INDEX_TYPE: str = Field(default="ivfflat")
    VECTOR_SEARCH_LIMIT: int = Field(default=10)

    # Audio Processing
    MAX_AUDIO_FILE_SIZE_MB: int = Field(default=500)
    SUPPORTED_AUDIO_FORMATS: List[str] = Field(default_factory=list)
    AUDIO_CHUNK_SIZE_SECONDS: int = Field(default=300)
    TEXT_CHUNK_SIZE: int = Field(default=256)
    TEXT_CHUNK_OVERLAP: int = Field(default=32)

    @field_validator("SUPPORTED_AUDIO_FORMATS", mode="before")
    @classmethod
    def assemble_audio_formats(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_METRICS_PATH: str = Field(default="/metrics")

    # Feature Flags
    ENABLE_SPEAKER_DIARIZATION: bool = Field(default=False)
    ENABLE_REAL_TIME_PROCESSING: bool = Field(default=False)
    ENABLE_COST_TRACKING: bool = Field(default=True)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def max_audio_file_size_bytes(self) -> int:
        return self.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()