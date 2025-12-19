# 🚀 WiFi Gateway Analyzer - Backend API

API REST construida con FastAPI para análisis de gateways WiFi con inteligencia artificial.

## 📋 Características

- ✅ Autenticación JWT con Supabase
- ✅ Gestión de usuarios (admin y users)
- ✅ Análisis completo de gateways Huawei
- ✅ Informes generados con IA (Google Gemini)
- ✅ Chat interactivo con datos técnicos
- ✅ API REST documentada (Swagger/OpenAPI)
- ✅ Variables de ambiente seguras
- ✅ Rate limiting y seguridad

## 🏗️ Tecnologías

- **FastAPI** - Framework web moderno
- **Supabase** - Base de datos PostgreSQL
- **Google Gemini** - IA para análisis
- **JWT** - Autenticación segura
- **Pydantic** - Validación de datos
- **LangChain** - Orquestación de IA

## 📦 Instalación Local

### 1. Clonar repositorio

```bash
git clone <tu-repo>
cd backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de ambiente

Copia `.env.example` a `.env` y completa los valores:

```bash
cp .env.example .env
```

Edita el archivo `.env`:

```env
# Supabase (obtener de tu proyecto Supabase)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key
SUPABASE_SERVICE_KEY=tu_service_role_key

# Gateway API (Huawei)
GATEWAY_BASE_URL=https://176.52.129.49:26335
GATEWAY_USERNAME=Claro_cvergara_API
GATEWAY_PASSWORD=H0men3tw0rk@api

# Google Gemini
GOOGLE_API_KEY=tu_api_key_de_google

# JWT (genera uno aleatorio)
JWT_SECRET_KEY=tu_secret_key_super_segura_aqui

# Admin inicial
ADMIN_EMAIL=cesar.vergara@clarovtr.cl
ADMIN_PASSWORD=abundancia.28
ADMIN_NAME=Cesar Vergara
```

### 5. Configurar Supabase

Ejecuta el script SQL en tu proyecto Supabase:

```bash
# Copia el contenido de supabase_schema.sql
# Pégalo en el SQL Editor de Supabase
# Ejecuta el script
```

### 6. Ejecutar servidor

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

- Documentación Swagger: `http://localhost:8000/docs`
- Documentación ReDoc: `http://localhost:8000/redoc`

## 🌐 Despliegue en Render

### Método 1: Despliegue Manual

1. Ve a [render.com](https://render.com)
2. Crea una nueva "Web Service"
3. Conecta tu repositorio
4. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11

5. Agrega las variables de ambiente en la sección "Environment"

### Método 2: Despliegue con Blueprint

1. Usa el archivo `render.yaml`
2. En Render, ve a "Blueprints"
3. Conecta tu repositorio
4. Render detectará automáticamente la configuración

### Variables de Ambiente en Render

Configura estas variables en Render:

```
SUPABASE_URL=<tu_supabase_url>
SUPABASE_KEY=<tu_supabase_key>
SUPABASE_SERVICE_KEY=<tu_service_key>
GATEWAY_BASE_URL=https://176.52.129.49:26335
GATEWAY_USERNAME=Claro_cvergara_API
GATEWAY_PASSWORD=H0men3tw0rk@api
GOOGLE_API_KEY=<tu_google_api_key>
JWT_SECRET_KEY=<genera_uno_aleatorio>
ADMIN_EMAIL=cesar.vergara@clarovtr.cl
ADMIN_PASSWORD=abundancia.28
ADMIN_NAME=Cesar Vergara
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://tu-frontend.vercel.app
```

## 📚 Documentación de API

### Autenticación

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "cesar.vergara@clarovtr.cl",
  "password": "abundancia.28"
}
```

Respuesta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "email": "cesar.vergara@clarovtr.cl",
    "nombre": "Cesar Vergara",
    "rol": "admin"
  }
}
```

### Usuarios (Solo Admin)

#### Crear Usuario
```http
POST /api/usuarios
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "nuevo@ejemplo.com",
  "password": "contraseña123",
  "nombre": "Nuevo Usuario",
  "rol": "user",
  "activo": true
}
```

### Análisis de Gateways

#### Crear Análisis
```http
POST /api/analisis
Authorization: Bearer <token>
Content-Type: application/json

{
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "incluir_eventos": true
}
```

#### Listar Análisis
```http
GET /api/analisis?limit=20&offset=0
Authorization: Bearer <token>
```

### Chat

#### Hacer Pregunta
```http
POST /api/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "analisis_id": "uuid-del-analisis",
  "pregunta": "¿Cuál es el estado de la señal WiFi?"
}
```

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Autenticación JWT
- ✅ CORS configurado
- ✅ Variables de ambiente sensibles
- ✅ Rate limiting
- ✅ Validación de datos con Pydantic

## 🐛 Troubleshooting

### Error de conexión con Supabase

Verifica que las URLs y keys sean correctas:
```bash
# Prueba la conexión
python -c "from app.database import verificar_conexion; import asyncio; print(asyncio.run(verificar_conexion()))"
```

### Error con Google Gemini

Verifica que tu API key tenga acceso a Gemini:
```bash
# Prueba la API key
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=$GOOGLE_API_KEY"
```

### Puerto ya en uso

```bash
# Encuentra el proceso usando el puerto 8000
lsof -i :8000
# Mata el proceso
kill -9 <PID>
```

## 📧 Soporte

Para soporte, contacta a: cesar.vergara@clarovtr.cl

## 📄 Licencia

Propiedad de Claro Chile - Uso interno
