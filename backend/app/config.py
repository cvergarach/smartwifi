# ============================================
# CONFIG.PY - Configuración de la aplicación
# ============================================

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings
    Lee automáticamente desde variables de ambiente
    """
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # Gateway API (Huawei)
    GATEWAY_BASE_URL: str
    GATEWAY_USERNAME: str
    GATEWAY_PASSWORD: str
    
    # Google Gemini
    GOOGLE_API_KEY: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Admin inicial
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_NAME: str = "Administrador"
    
    # API Settings
    API_VERSION: str = "v1"
    API_TITLE: str = "WiFi Gateway Analyzer API"
    API_DESCRIPTION: str = "API para análisis de gateways WiFi con IA"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # CORS
    ALLOWED_ORIGINS: str = "*"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_CONCURRENT_REQUESTS: int = 10
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = [".txt", ".csv"]
    
    # AI Configuration
    DEFAULT_PROMPT_TEMPLATE: str = "default"
    MAX_CHAT_HISTORY: int = 20
    AI_MODEL: str = "gemini-1.5-flash"
    AI_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convierte el string de orígenes permitidos en lista"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Función cacheada para obtener settings
    Se carga una sola vez y se reutiliza
    """
    return Settings()


# Instancia global de settings
settings = get_settings()
