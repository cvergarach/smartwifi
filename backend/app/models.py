# ============================================
# MODELS.PY - Modelos de datos
# ============================================

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================
# ENUMS
# ============================================

class RolUsuario(str, Enum):
    ADMIN = "admin"
    USER = "user"

class EstadoAnalisis(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"

# ============================================
# MODELOS DE USUARIO
# ============================================

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: Optional[str] = None
    rol: RolUsuario = RolUsuario.USER
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None
    password: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

# ============================================
# MODELOS DE AUTENTICACIÓN
# ============================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UsuarioResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    rol: Optional[str] = None

# ============================================
# MODELOS DE ANÁLISIS DE GATEWAY
# ============================================

class AnalisisGatewayRequest(BaseModel):
    mac_address: str = Field(..., min_length=12, max_length=17)
    modo: str = Field(default="single", pattern="^(single|bulk)$")
    incluir_eventos: bool = True
    
    @validator('mac_address')
    def validate_mac(cls, v):
        # Permitir formato con o sin separadores
        import re
        v = v.replace(':', '').replace('-', '').replace('.', '').upper()
        if not re.match(r'^[0-9A-F]{12}$', v):
            raise ValueError('MAC address inválida')
        # Retornar formato con dos puntos
        return ':'.join([v[i:i+2] for i in range(0, 12, 2)])

class AnalisisBulkRequest(BaseModel):
    mac_addresses: List[str] = Field(..., min_items=1, max_items=50)
    incluir_eventos: bool = True

class AnalisisGatewayResponse(BaseModel):
    id: str
    usuario_id: str
    mac_address: str
    estado: EstadoAnalisis
    informe_ia: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalisisCompletoResponse(AnalisisGatewayResponse):
    datos_tecnicos: Dict[str, Any]
    usuario_email: Optional[str] = None

# ============================================
# MODELOS DE CHAT
# ============================================

class ChatRequest(BaseModel):
    analisis_id: str
    pregunta: str = Field(..., min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    id: str
    pregunta: str
    respuesta: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatHistorialResponse(BaseModel):
    analisis_id: str
    mensajes: List[ChatResponse]

# ============================================
# MODELOS DE RESPUESTA GENÉRICA
# ============================================

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

# ============================================
# MODELOS DE ESTADÍSTICAS
# ============================================

class EstadisticasUsuario(BaseModel):
    usuario_id: str
    email: str
    nombre: Optional[str]
    total_analisis: int
    ultimo_analisis: Optional[datetime]
    ultimo_acceso: Optional[datetime]

class EstadisticasGlobales(BaseModel):
    total_usuarios: int
    usuarios_activos: int
    total_analisis: int
    analisis_hoy: int
    analisis_semana: int
    top_usuarios: List[EstadisticasUsuario]

# ============================================
# MODELOS DE PROMPT
# ============================================

class PromptTemplate(BaseModel):
    nombre: str
    template: str
    descripcion: Optional[str] = None
    
class PromptUpdateRequest(BaseModel):
    template: str = Field(..., min_length=100)
