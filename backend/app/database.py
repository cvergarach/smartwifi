# ============================================
# DATABASE.PY - Conexión con Supabase
# ============================================

from supabase import create_client, Client
from functools import lru_cache
from .config import settings

# ============================================
# CLIENTE SUPABASE
# ============================================

@lru_cache()
def get_supabase_client() -> Client:
    """
    Crear y cachear cliente de Supabase
    Se crea una sola vez y se reutiliza
    """
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )

def get_supabase() -> Client:
    """
    Dependencia para FastAPI
    Retorna el cliente de Supabase
    """
    return get_supabase_client()

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

async def verificar_conexion() -> bool:
    """
    Verificar que la conexión con Supabase funciona
    """
    try:
        supabase = get_supabase_client()
        # Hacer una consulta simple para verificar
        response = supabase.table("usuarios").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"❌ Error de conexión con Supabase: {e}")
        return False
