from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Illegal Waste API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    DATABASE_URL: str

    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    BACKEND_CORS_ORIGINS: List[str] = []

    ENVIRONMENT: str = "dev"
    
    # MinIO Configuration
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_NAME: str = "illegal-waste-media"
    MINIO_SECURE: bool = False  # True jika menggunakan HTTPS
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()