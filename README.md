# 📡 Sistema Administrador WiFi Gateway - Claro Chile

Sistema web completo para análisis y administración de gateways WiFi con inteligencia artificial.

## 🎯 Descripción

Aplicación web empresarial que permite:
- ✅ **Gestión de usuarios** con roles (Admin/User)
- ✅ **Análisis completo de gateways WiFi** Huawei
- ✅ **Informes generados con IA** usando Google Gemini
- ✅ **Chat interactivo** para consultas sobre los análisis
- ✅ **Dashboard ejecutivo** con estadísticas
- ✅ **Autenticación segura** con JWT
- ✅ **Diseño responsive** y profesional

## 🏗️ Arquitectura

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│                 │      │                  │      │                 │
│  Frontend       │─────▶│   Backend API    │─────▶│   Supabase      │
│  (Vercel)       │      │   (Render)       │      │   (Database)    │
│  Next.js + React│      │   FastAPI        │      │   PostgreSQL    │
│                 │      │                  │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  │
                         ┌────────▼──────────┐
                         │                   │
                         │  Google Gemini AI │
                         │  (Análisis)       │
                         │                   │
                         └───────────────────┘
```

## 📦 Tecnologías

### Backend
- **FastAPI** - Framework web Python moderno
- **Supabase** - Base de datos PostgreSQL
- **Google Gemini** - IA para análisis
- **JWT** - Autenticación segura
- **LangChain** - Orquestación de IA
- **Render** - Hosting backend

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos
- **React Query** - Estado del servidor
- **Zustand** - Estado global
- **Axios** - Cliente HTTP
- **Vercel** - Hosting frontend

## 🚀 Inicio Rápido

### 1. Configurar Supabase

1. Crea una cuenta en [supabase.com](https://supabase.com)
2. Crea un nuevo proyecto
3. Ve a SQL Editor y ejecuta el script:
   ```sql
   -- Copiar contenido de backend/supabase_schema.sql
   ```
4. Guarda las credenciales:
   - Project URL
   - Anon key
   - Service role key

### 2. Configurar Google Gemini API

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una API key
3. Guárdala para usarla en las variables de ambiente

### 3. Desplegar Backend en Render

**Opción A: Despliegue automático**

1. Ve a [render.com](https://render.com)
2. Conecta tu repositorio
3. Render detectará `render.yaml` automáticamente
4. Agrega las variables de ambiente:
   ```
   SUPABASE_URL=tu_supabase_url
   SUPABASE_KEY=tu_anon_key
   SUPABASE_SERVICE_KEY=tu_service_key
   GATEWAY_BASE_URL=https://176.52.129.49:26335
   GATEWAY_USERNAME=Claro_cvergara_API
   GATEWAY_PASSWORD=H0men3tw0rk@api
   GOOGLE_API_KEY=tu_google_api_key
   JWT_SECRET_KEY=genera_un_string_aleatorio_seguro
   ADMIN_EMAIL=cesar.vergara@clarovtr.cl
   ADMIN_PASSWORD=abundancia.28
   ```

**Opción B: Despliegue manual**

1. Crea un nuevo "Web Service"
2. Conecta tu repositorio
3. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
4. Agrega las variables de ambiente

Tu API estará en: `https://tu-app.onrender.com`

### 4. Desplegar Frontend en Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Importa tu repositorio
3. Configura:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Agrega las variables de ambiente:
   ```
   NEXT_PUBLIC_API_URL=https://tu-app.onrender.com
   ```
5. Despliega

Tu frontend estará en: `https://tu-app.vercel.app`

### 5. Configurar CORS

En Render, agrega esta variable:
```
ALLOWED_ORIGINS=https://tu-app.vercel.app
```

## 👤 Usuario Administrador Inicial

El sistema crea automáticamente un usuario administrador al iniciar:

```
Email: cesar.vergara@clarovtr.cl
Password: abundancia.28
```

**⚠️ IMPORTANTE**: Cambia la contraseña inmediatamente después del primer login.

## 📱 Uso de la Aplicación

### 1. Login
- Ingresa con las credenciales del administrador
- El sistema genera un token JWT válido por 24 horas

### 2. Gestión de Usuarios (Solo Admin)
- Ve a "Usuarios" en el menú
- Crea nuevos usuarios con rol User o Admin
- Activa/desactiva usuarios
- Cambia contraseñas

### 3. Análisis de Gateway
- Ve a "Nuevo Análisis"
- Ingresa la dirección MAC del gateway (formato: AA:BB:CC:DD:EE:FF)
- Selecciona incluir eventos (opcional)
- Click en "Analizar"
- El sistema:
  1. Consulta la API del gateway Huawei
  2. Recopila todos los datos técnicos
  3. Genera un informe ejecutivo con IA
  4. Guarda el análisis en la base de datos

### 4. Chat con Análisis
- En un análisis, haz click en "Chat"
- Haz preguntas específicas sobre los datos
- La IA responde basándose SOLO en los datos técnicos recopilados
- El historial se guarda automáticamente

### 5. Dashboard
- Visualiza estadísticas generales
- Análisis recientes
- Usuarios más activos
- Gráficos de uso

## 🔐 Seguridad

El sistema implementa múltiples capas de seguridad:

- ✅ **Contraseñas hasheadas** con bcrypt (12 rounds)
- ✅ **Tokens JWT** con expiración de 24 horas
- ✅ **CORS configurado** solo para dominios permitidos
- ✅ **Variables de ambiente** para datos sensibles
- ✅ **HTTPS obligatorio** en producción
- ✅ **Row Level Security** en Supabase
- ✅ **Validación de datos** con Pydantic
- ✅ **Rate limiting** contra ataques
- ✅ **Headers de seguridad** configurados

## 📊 Endpoints de la API

### Autenticación
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Obtener usuario actual
- `POST /api/auth/logout` - Logout

### Usuarios (Solo Admin)
- `GET /api/usuarios` - Listar usuarios
- `POST /api/usuarios` - Crear usuario
- `PUT /api/usuarios/{id}` - Actualizar usuario
- `DELETE /api/usuarios/{id}` - Eliminar usuario

### Análisis
- `POST /api/analisis` - Crear análisis
- `GET /api/analisis` - Listar análisis
- `GET /api/analisis/{id}` - Obtener análisis específico
- `DELETE /api/analisis/{id}` - Eliminar análisis

### Chat
- `POST /api/chat` - Enviar pregunta
- `GET /api/chat/{analisis_id}` - Obtener historial

### Estadísticas (Solo Admin)
- `GET /api/estadisticas/global` - Estadísticas globales

Documentación completa en: `https://tu-api.onrender.com/docs`

## 🛠️ Desarrollo Local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales
uvicorn app.main:app --reload
```

Backend disponible en: `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Editar .env.local
npm run dev
```

Frontend disponible en: `http://localhost:3000`

## 📁 Estructura del Proyecto

```
wifi-gateway-analyzer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # API principal
│   │   ├── config.py            # Configuración
│   │   ├── models.py            # Modelos Pydantic
│   │   ├── auth.py              # Autenticación
│   │   ├── database.py          # Conexión Supabase
│   │   └── gateway_analyzer.py  # Lógica de análisis
│   ├── requirements.txt
│   ├── .env.example
│   ├── Procfile                 # Para Render
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/                 # App Router Next.js
│   │   ├── components/          # Componentes React
│   │   ├── lib/
│   │   │   ├── api.ts           # Cliente API
│   │   │   └── store.ts         # Estado global
│   │   └── styles/
│   │       └── globals.css
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── tsconfig.json
├── supabase_schema.sql          # Schema de base de datos
└── README.md                    # Este archivo
```

## 🐛 Troubleshooting

### Backend no conecta con Supabase
```bash
# Verificar URLs y keys en .env
# Probar conexión:
python -c "from app.database import verificar_conexion; import asyncio; print(asyncio.run(verificar_conexion()))"
```

### Frontend no conecta con Backend
```bash
# Verificar NEXT_PUBLIC_API_URL en .env.local
# Verificar CORS en backend (ALLOWED_ORIGINS)
# Ver consola del navegador para errores
```

### Error con Google Gemini
```bash
# Verificar que GOOGLE_API_KEY sea válida
# Verificar cuota de API en Google Cloud Console
```

### Error de autenticación
```bash
# Verificar JWT_SECRET_KEY
# Verificar que el token no haya expirado
# Limpiar localStorage del navegador y volver a hacer login
```

## 📈 Próximas Mejoras

- [ ] Análisis en lote de múltiples MACs
- [ ] Exportar informes a PDF
- [ ] Notificaciones push
- [ ] Programación de análisis automáticos
- [ ] Dashboard con gráficos avanzados
- [ ] Integración con Slack
- [ ] Modo oscuro
- [ ] Multi-idioma

## 📞 Soporte

**Desarrollador**: Cesar Vergara  
**Email**: cesar.vergara@clarovtr.cl  
**Empresa**: Claro Chile

## 📄 Licencia

© 2024 Claro Chile - Uso interno exclusivo

---

**Versión**: 1.0.0  
**Última actualización**: Diciembre 2024  
**Estado**: ✅ Producción
