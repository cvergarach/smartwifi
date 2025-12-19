# ============================================
# MAIN.PY - API Principal
# ============================================

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from supabase import Client
from typing import List, Optional

from .config import settings
from .database import get_supabase, verificar_conexion
from .auth import (
    authenticate_user, 
    create_access_token, 
    hash_password,
    get_current_user,
    get_current_admin_user,
    crear_usuario_inicial
)
from .models import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioLogin,
    Token,
    MessageResponse,
    ErrorResponse,
    AnalisisGatewayRequest,
    AnalisisBulkRequest,
    AnalisisGatewayResponse,
    AnalisisCompletoResponse,
    ChatRequest,
    ChatResponse,
    EstadisticasUsuario,
    EstadisticasGlobales,
    RolUsuario
)
from .gateway_analyzer import GatewayAnalyzer

# ============================================
# INICIALIZACIÓN DE FASTAPI
# ============================================

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# CONFIGURACIÓN DE CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# EVENTOS DE INICIO Y CIERRE
# ============================================

@app.on_event("startup")
async def startup_event():
    """
    Ejecutar al iniciar la aplicación
    """
    print("🚀 Iniciando API WiFi Gateway Analyzer...")
    print(f"📝 Versión: {settings.API_VERSION}")
    print(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    
    # Verificar conexión con Supabase
    if await verificar_conexion():
        print("✅ Conexión con Supabase exitosa")
        
        # Crear usuario administrador inicial
        supabase = get_supabase()
        await crear_usuario_inicial(supabase)
    else:
        print("❌ Error de conexión con Supabase")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Ejecutar al cerrar la aplicación
    """
    print("👋 Cerrando API WiFi Gateway Analyzer...")

# ============================================
# ENDPOINTS DE SALUD Y ESTADO
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint raíz - Información de la API
    """
    return {
        "app": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check - Verificar estado de la API
    """
    db_ok = await verificar_conexion()
    
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================

@app.post("/api/auth/login", response_model=Token, tags=["Autenticación"])
async def login(
    credentials: UsuarioLogin,
    supabase: Client = Depends(get_supabase)
):
    """
    Login de usuario - Retorna token JWT
    """
    usuario = await authenticate_user(credentials.email, credentials.password, supabase)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token
    access_token_expires = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    access_token = create_access_token(
        data={
            "sub": usuario["email"],
            "user_id": usuario["id"],
            "rol": usuario["rol"]
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
        user=UsuarioResponse(**usuario)
    )

@app.get("/api/auth/me", response_model=UsuarioResponse, tags=["Autenticación"])
async def get_me(
    current_user: UsuarioResponse = Depends(get_current_user)
):
    """
    Obtener información del usuario actual
    """
    return current_user

@app.post("/api/auth/logout", response_model=MessageResponse, tags=["Autenticación"])
async def logout(
    current_user: UsuarioResponse = Depends(get_current_user)
):
    """
    Logout de usuario (invalidar token en frontend)
    """
    return MessageResponse(
        message="Sesión cerrada exitosamente",
        detail="Token invalidado"
    )

# ============================================
# ENDPOINTS DE USUARIOS (ADMIN)
# ============================================

@app.get("/api/usuarios", response_model=List[UsuarioResponse], tags=["Usuarios"])
async def listar_usuarios(
    current_user: UsuarioResponse = Depends(get_current_admin_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Listar todos los usuarios (solo admin)
    """
    response = supabase.table("usuarios").select("*").order("created_at", desc=True).execute()
    return [UsuarioResponse(**usuario) for usuario in response.data]

@app.post("/api/usuarios", response_model=UsuarioResponse, tags=["Usuarios"])
async def crear_usuario(
    usuario: UsuarioCreate,
    current_user: UsuarioResponse = Depends(get_current_admin_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Crear nuevo usuario (solo admin)
    """
    # Verificar si el email ya existe
    existing = supabase.table("usuarios").select("id").eq("email", usuario.email).execute()
    if existing.data and len(existing.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear usuario
    usuario_data = {
        "email": usuario.email,
        "password_hash": hash_password(usuario.password),
        "nombre": usuario.nombre,
        "rol": usuario.rol.value,
        "activo": usuario.activo
    }
    
    response = supabase.table("usuarios").insert(usuario_data).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear usuario"
        )
    
    return UsuarioResponse(**response.data[0])

@app.put("/api/usuarios/{usuario_id}", response_model=UsuarioResponse, tags=["Usuarios"])
async def actualizar_usuario(
    usuario_id: str,
    usuario_update: UsuarioUpdate,
    current_user: UsuarioResponse = Depends(get_current_admin_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Actualizar usuario (solo admin)
    """
    # Preparar datos de actualización
    update_data = {}
    
    if usuario_update.nombre is not None:
        update_data["nombre"] = usuario_update.nombre
    if usuario_update.rol is not None:
        update_data["rol"] = usuario_update.rol.value
    if usuario_update.activo is not None:
        update_data["activo"] = usuario_update.activo
    if usuario_update.password is not None:
        update_data["password_hash"] = hash_password(usuario_update.password)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )
    
    # Actualizar usuario
    response = supabase.table("usuarios").update(update_data).eq("id", usuario_id).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return UsuarioResponse(**response.data[0])

@app.delete("/api/usuarios/{usuario_id}", response_model=MessageResponse, tags=["Usuarios"])
async def eliminar_usuario(
    usuario_id: str,
    current_user: UsuarioResponse = Depends(get_current_admin_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Eliminar usuario (solo admin)
    No se puede eliminar a sí mismo
    """
    if usuario_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )
    
    response = supabase.table("usuarios").delete().eq("id", usuario_id).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return MessageResponse(message="Usuario eliminado exitosamente")

# ============================================
# ENDPOINTS DE ANÁLISIS DE GATEWAYS
# ============================================

@app.post("/api/analisis", response_model=AnalisisCompletoResponse, tags=["Análisis"])
async def crear_analisis(
    request: AnalisisGatewayRequest,
    current_user: UsuarioResponse = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Crear nuevo análisis de gateway
    """
    try:
        # Crear analizador
        analyzer = GatewayAnalyzer()
        
        # Obtener datos técnicos
        datos_tecnicos = analyzer.analyze_gateway(
            request.mac_address,
            request.incluir_eventos
        )
        
        # Generar informe con IA
        informe_ia = analyzer.generate_ai_report(datos_tecnicos)
        
        # Guardar en base de datos
        analisis_data = {
            "usuario_id": current_user.id,
            "mac_address": request.mac_address,
            "datos_tecnicos": datos_tecnicos,
            "informe_ia": informe_ia,
            "estado": "completado"
        }
        
        response = supabase.table("analisis_gateways").insert(analisis_data).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al guardar análisis"
            )
        
        # Agregar email del usuario
        resultado = response.data[0]
        resultado["usuario_email"] = current_user.email
        
        return AnalisisCompletoResponse(**resultado)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar análisis: {str(e)}"
        )

@app.get("/api/analisis", response_model=List[AnalisisGatewayResponse], tags=["Análisis"])
async def listar_analisis(
    current_user: UsuarioResponse = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
    limit: int = 50,
    offset: int = 0
):
    """
    Listar análisis del usuario actual
    """
    response = supabase.table("analisis_gateways")\
        .select("id, usuario_id, mac_address, estado, created_at")\
        .eq("usuario_id", current_user.id)\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    return [AnalisisGatewayResponse(**analisis) for analisis in response.data]

@app.get("/api/analisis/{analisis_id}", response_model=AnalisisCompletoResponse, tags=["Análisis"])
async def obtener_analisis(
    analisis_id: str,
    current_user: UsuarioResponse = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Obtener análisis específico por ID
    """
    response = supabase.table("analisis_gateways")\
        .select("*")\
        .eq("id", analisis_id)\
        .eq("usuario_id", current_user.id)\
        .execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado"
        )
    
    resultado = response.data[0]
    resultado["usuario_email"] = current_user.email
    
    return AnalisisCompletoResponse(**resultado)

@app.delete("/api/analisis/{analisis_id}", response_model=MessageResponse, tags=["Análisis"])
async def eliminar_analisis(
    analisis_id: str,
    current_user: UsuarioResponse = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Eliminar análisis
    """
    response = supabase.table("analisis_gateways")\
        .delete()\
        .eq("id", analisis_id)\
        .eq("usuario_id", current_user.id)\
        .execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado"
        )
    
    return MessageResponse(message="Análisis eliminado exitosamente")

# ============================================
# ENDPOINTS DE CHAT
# ============================================

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_analisis(
    request: ChatRequest,
    current_user: UsuarioResponse = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Hacer pregunta sobre un análisis específico
    """
    # Verificar que el análisis existe y pertenece al usuario
    analisis_response = supabase.table("analisis_gateways")\
        .select("datos_tecnicos")\
        .eq("id", request.analisis_id)\
        .eq("usuario_id", current_user.id)\
        .execute()
    
    if not analisis_response.data or len(analisis_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado"
        )
    
    # Obtener historial previo
    historial_response = supabase.table("chat_historial")\
        .select("pregunta, respuesta")\
        .eq("analisis_id", request.analisis_id)\
        .order("created_at", desc=False)\
        .limit(settings.MAX_CHAT_HISTORY)\
        .execute()
    
    historial = []
    if historial_response.data:
        for msg in historial_response.data:
            historial.append(f"Humano: {msg['pregunta']}")
            historial.append(f"Asistente: {msg['respuesta']}")
    
    # Generar respuesta con IA
    try:
        analyzer = GatewayAnalyzer()
        respuesta = analyzer.chat_with_data(
            request.pregunta,
            analisis_response.data[0]["datos_tecnicos"],
            historial
        )
        
        # Guardar en historial
        chat_data = {
            "analisis_id": request.analisis_id,
            "usuario_id": current_user.id,
            "pregunta": request.pregunta,
            "respuesta": respuesta
        }
        
        chat_response = supabase.table("chat_historial").insert(chat_data).execute()
        
        if not chat_response.data or len(chat_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al guardar mensaje"
            )
        
        return ChatResponse(**chat_response.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar pregunta: {str(e)}"
        )

@app.get("/api/chat/{analisis_id}", response_model=List[ChatResponse], tags=["Chat"])
async def obtener_historial_chat(
    analisis_id: str,
    current_user: UsuarioResponse = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Obtener historial de chat de un análisis
    """
    response = supabase.table("chat_historial")\
        .select("*")\
        .eq("analisis_id", analisis_id)\
        .eq("usuario_id", current_user.id)\
        .order("created_at", desc=False)\
        .execute()
    
    return [ChatResponse(**msg) for msg in response.data]

# ============================================
# ENDPOINTS DE ESTADÍSTICAS (ADMIN)
# ============================================

@app.get("/api/estadisticas/global", response_model=EstadisticasGlobales, tags=["Estadísticas"])
async def estadisticas_globales(
    current_user: UsuarioResponse = Depends(get_current_admin_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Obtener estadísticas globales del sistema (solo admin)
    """
    # Total de usuarios
    usuarios = supabase.table("usuarios").select("id, activo").execute()
    total_usuarios = len(usuarios.data)
    usuarios_activos = len([u for u in usuarios.data if u.get("activo", False)])
    
    # Total de análisis
    analisis = supabase.table("analisis_gateways").select("id, created_at").execute()
    total_analisis = len(analisis.data)
    
    # Análisis hoy
    hoy = datetime.utcnow().date().isoformat()
    analisis_hoy = len([a for a in analisis.data if a["created_at"].startswith(hoy)])
    
    # Análisis última semana
    hace_semana = (datetime.utcnow().date() - timedelta(days=7)).isoformat()
    analisis_semana = len([a for a in analisis.data if a["created_at"] >= hace_semana])
    
    # Top usuarios
    stats_response = supabase.from_("vista_estadisticas_usuario")\
        .select("*")\
        .order("total_analisis", desc=True)\
        .limit(10)\
        .execute()
    
    top_usuarios = [EstadisticasUsuario(**stat) for stat in stats_response.data]
    
    return EstadisticasGlobales(
        total_usuarios=total_usuarios,
        usuarios_activos=usuarios_activos,
        total_analisis=total_analisis,
        analisis_hoy=analisis_hoy,
        analisis_semana=analisis_semana,
        top_usuarios=top_usuarios
    )

# ============================================
# MANEJO DE ERRORES
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=str(exc.status_code)
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Error interno del servidor",
            detail=str(exc) if settings.DEBUG else None,
            code="500"
        ).dict()
    )

# ============================================
# EJECUTAR APLICACIÓN
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
