# ============================================
# AUTH.PY - Autenticación y autorización
# ============================================

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client

from .config import settings
from .models import TokenData, UsuarioResponse, RolUsuario
from .database import get_supabase

# ============================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ============================================
# FUNCIONES DE HASHING
# ============================================

def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña contra hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ============================================
# FUNCIONES JWT
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """
    Decodificar y validar token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        rol: str = payload.get("rol")
        
        if email is None or user_id is None:
            raise credentials_exception
        
        return TokenData(email=email, user_id=user_id, rol=rol)
    
    except JWTError:
        raise credentials_exception

# ============================================
# DEPENDENCIAS DE AUTENTICACIÓN
# ============================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> UsuarioResponse:
    """
    Obtener usuario actual desde token JWT
    """
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    # Buscar usuario en la base de datos
    response = supabase.table("usuarios").select("*").eq("id", token_data.user_id).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    usuario = response.data[0]
    
    if not usuario.get("activo", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Actualizar último acceso
    supabase.table("usuarios").update({
        "ultimo_acceso": datetime.utcnow().isoformat()
    }).eq("id", usuario["id"]).execute()
    
    return UsuarioResponse(**usuario)

async def get_current_active_user(
    current_user: UsuarioResponse = Depends(get_current_user)
) -> UsuarioResponse:
    """
    Verificar que el usuario esté activo
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user

async def get_current_admin_user(
    current_user: UsuarioResponse = Depends(get_current_user)
) -> UsuarioResponse:
    """
    Verificar que el usuario sea administrador
    """
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user

# ============================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================

async def authenticate_user(
    email: str, 
    password: str, 
    supabase: Client
) -> Optional[dict]:
    """
    Autenticar usuario con email y contraseña
    """
    # Buscar usuario por email
    response = supabase.table("usuarios").select("*").eq("email", email).execute()
    
    if not response.data or len(response.data) == 0:
        return None
    
    usuario = response.data[0]
    
    # Verificar contraseña
    if not verify_password(password, usuario["password_hash"]):
        return None
    
    # Verificar que esté activo
    if not usuario.get("activo", False):
        return None
    
    return usuario

async def crear_usuario_inicial(supabase: Client) -> None:
    """
    Crear usuario administrador inicial si no existe
    """
    try:
        # Verificar si ya existe
        response = supabase.table("usuarios").select("id").eq(
            "email", settings.ADMIN_EMAIL
        ).execute()
        
        if response.data and len(response.data) > 0:
            print(f"✅ Usuario admin {settings.ADMIN_EMAIL} ya existe")
            return
        
        # Crear usuario admin
        usuario_data = {
            "email": settings.ADMIN_EMAIL,
            "password_hash": hash_password(settings.ADMIN_PASSWORD),
            "nombre": settings.ADMIN_NAME,
            "rol": RolUsuario.ADMIN.value,
            "activo": True
        }
        
        supabase.table("usuarios").insert(usuario_data).execute()
        print(f"✅ Usuario admin {settings.ADMIN_EMAIL} creado exitosamente")
        
    except Exception as e:
        print(f"❌ Error al crear usuario inicial: {e}")
