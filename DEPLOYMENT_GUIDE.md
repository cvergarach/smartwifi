# 🚀 Guía de Despliegue Completa - Paso a Paso

Esta guía te llevará desde cero hasta tener tu aplicación completamente funcional en producción.

## 📋 Requisitos Previos

- [ ] Cuenta de GitHub
- [ ] Cuenta de Supabase (gratis)
- [ ] Cuenta de Google Cloud (para Gemini API)
- [ ] Cuenta de Render (gratis)
- [ ] Cuenta de Vercel (gratis)

## 🗂️ Paso 1: Preparar el Código

### 1.1 Crear Repositorio en GitHub

```bash
# Crear nuevo repositorio
mkdir wifi-gateway-analyzer
cd wifi-gateway-analyzer

# Inicializar git
git init

# Copiar todos los archivos del proyecto aquí

# Crear .gitignore
cat > .gitignore << EOF
# Backend
backend/__pycache__/
backend/.env
backend/*.pyc
backend/.pytest_cache/
backend/.venv/
backend/venv/

# Frontend
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/.env.local
frontend/.env.production.local
frontend/.env.development.local
frontend/.env.test.local
frontend/.DS_Store
frontend/*.log
EOF

# Commit inicial
git add .
git commit -m "Initial commit: WiFi Gateway Analyzer"

# Crear repositorio en GitHub y subir
git remote add origin https://github.com/tu-usuario/wifi-gateway-analyzer.git
git branch -M main
git push -u origin main
```

## 🗄️ Paso 2: Configurar Supabase

### 2.1 Crear Proyecto

1. Ve a [supabase.com](https://supabase.com)
2. Click en "Start your project"
3. Click en "New Project"
4. Llena los datos:
   - **Name**: wifi-analyzer
   - **Database Password**: [Genera una contraseña segura]
   - **Region**: South America (São Paulo) - más cercano a Chile
   - **Pricing Plan**: Free
5. Click "Create new project"
6. Espera 2-3 minutos a que se cree el proyecto

### 2.2 Configurar Base de Datos

1. En el proyecto, ve a **SQL Editor** (icono de rayo en la barra lateral)
2. Click en "New query"
3. Copia TODO el contenido de `supabase_schema.sql`
4. Pégalo en el editor
5. Click en "Run" (o presiona Ctrl+Enter)
6. Deberías ver: "Success. No rows returned"

### 2.3 Guardar Credenciales

1. Ve a **Project Settings** (icono de engranaje)
2. Ve a **API**
3. Copia y guarda estos valores:

```
Project URL: https://xxxxxxxxxxxxx.supabase.co
anon public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ IMPORTANTE**: Nunca compartas la `service_role key` públicamente.

## 🤖 Paso 3: Configurar Google Gemini API

### 3.1 Obtener API Key

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Click en "Create API Key"
4. Selecciona un proyecto de Google Cloud o crea uno nuevo
5. Click en "Create API key in new project"
6. Copia la API key generada
7. Guárdala de forma segura:

```
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 3.2 Verificar Acceso

Prueba que la API key funcione:

```bash
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hola, ¿funciona?"}]}]}' \
  "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=TU_API_KEY"
```

Deberías recibir una respuesta JSON con texto generado.

## 🖥️ Paso 4: Desplegar Backend en Render

### 4.1 Crear Web Service

1. Ve a [render.com](https://render.com)
2. Inicia sesión (puedes usar GitHub)
3. Click en "New +" → "Web Service"
4. Conecta tu repositorio de GitHub
5. Selecciona el repositorio `wifi-gateway-analyzer`
6. Click en "Connect"

### 4.2 Configurar el Servicio

Llena los siguientes datos:

**Basic Settings:**
- **Name**: `wifi-analyzer-api`
- **Region**: Oregon (USA) - buena latencia a Chile
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Selecciona: **Free** ($0/month)

### 4.3 Configurar Variables de Ambiente

En la sección "Environment Variables", agrega TODAS estas variables:

```
# Supabase (usar los valores guardados del Paso 2.3)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...[anon key]
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...[service key]

# Gateway API
GATEWAY_BASE_URL=https://176.52.129.49:26335
GATEWAY_USERNAME=Claro_cvergara_API
GATEWAY_PASSWORD=H0men3tw0rk@api

# Google Gemini (usar API key del Paso 3)
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# JWT (generar un string aleatorio seguro)
JWT_SECRET_KEY=tu_string_super_secreto_aleatorio_de_64_caracteres_minimo

# Admin inicial
ADMIN_EMAIL=cesar.vergara@clarovtr.cl
ADMIN_PASSWORD=abundancia.28
ADMIN_NAME=Cesar Vergara

# Configuración
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# CORS (agregar después de tener la URL de Vercel)
ALLOWED_ORIGINS=*
```

**Para generar JWT_SECRET_KEY seguro:**

```bash
# En tu terminal local
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4.4 Desplegar

1. Click en "Create Web Service"
2. Render comenzará a construir y desplegar
3. Espera 5-10 minutos
4. Cuando veas "Your service is live 🎉", anota la URL:

```
https://wifi-analyzer-api.onrender.com
```

### 4.5 Verificar que Funciona

Abre en tu navegador:

```
https://wifi-analyzer-api.onrender.com/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-..."
}
```

Si ves "database": "disconnected", revisa las credenciales de Supabase.

### 4.6 Verificar Usuario Admin

Abre la documentación de la API:

```
https://wifi-analyzer-api.onrender.com/docs
```

Prueba el endpoint `/api/auth/login`:
1. Click en "POST /api/auth/login"
2. Click en "Try it out"
3. Ingresa:
```json
{
  "email": "cesar.vergara@clarovtr.cl",
  "password": "abundancia.28"
}
```
4. Click "Execute"
5. Deberías ver una respuesta 200 con un token

**✅ Si esto funciona, tu backend está 100% operativo!**

## 🌐 Paso 5: Desplegar Frontend en Vercel

### 5.1 Preparar Configuración

Antes de desplegar, crea el archivo `frontend/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install"
}
```

Haz commit y push:

```bash
git add frontend/vercel.json
git commit -m "Add Vercel config"
git push
```

### 5.2 Crear Proyecto en Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Inicia sesión (puedes usar GitHub)
3. Click en "Add New" → "Project"
4. Importa tu repositorio de GitHub
5. Selecciona `wifi-gateway-analyzer`

### 5.3 Configurar el Proyecto

**Framework Preset**: Next.js (se detecta automáticamente)

**Root Directory**: Click en "Edit" y selecciona `frontend`

**Build and Output Settings**:
- **Build Command**: `npm run build` (por defecto)
- **Output Directory**: `.next` (por defecto)
- **Install Command**: `npm install` (por defecto)

**Environment Variables**:

Agrega esta variable:

```
NEXT_PUBLIC_API_URL=https://wifi-analyzer-api.onrender.com
```

(Usa la URL de tu backend de Render del Paso 4.4)

### 5.4 Desplegar

1. Click en "Deploy"
2. Vercel comenzará a construir
3. Espera 3-5 minutos
4. Cuando veas "Congratulations!", anota la URL:

```
https://wifi-gateway-analyzer.vercel.app
```

(El nombre puede variar)

### 5.5 Configurar CORS en Backend

Ahora que tienes la URL del frontend, actualiza el backend:

1. Ve a Render → tu servicio backend
2. Ve a "Environment"
3. Edita la variable `ALLOWED_ORIGINS`:

```
ALLOWED_ORIGINS=https://wifi-gateway-analyzer.vercel.app
```

(Usa tu URL real de Vercel)

4. Click "Save Changes"
5. Render redesplegará automáticamente

## ✅ Paso 6: Verificación Final

### 6.1 Probar Frontend

1. Abre tu URL de Vercel en el navegador
2. Deberías ver la página de login
3. Ingresa:
   - Email: `cesar.vergara@clarovtr.cl`
   - Password: `abundancia.28`
4. Click "Iniciar Sesión"
5. Deberías entrar al dashboard

### 6.2 Probar Funcionalidades

**Crear Usuario:**
1. Ve a "Usuarios" en el menú
2. Click "Nuevo Usuario"
3. Llena el formulario
4. Click "Crear"
5. Verifica que aparezca en la lista

**Crear Análisis:**
1. Ve a "Nuevo Análisis"
2. Ingresa una MAC (ej: `AA:BB:CC:DD:EE:FF`)
3. Click "Analizar"
4. Espera unos segundos
5. Deberías ver el informe generado

**Probar Chat:**
1. En un análisis, click "Chat"
2. Escribe una pregunta
3. Verifica que la IA responda

## 🔧 Paso 7: Configuraciones Adicionales

### 7.1 Dominio Personalizado (Opcional)

**En Vercel:**
1. Ve a tu proyecto
2. Ve a "Settings" → "Domains"
3. Agrega tu dominio personalizado
4. Sigue las instrucciones de DNS

**Actualizar CORS:**
- Actualiza `ALLOWED_ORIGINS` en Render con tu nuevo dominio

### 7.2 Cambiar Contraseña del Admin

**IMPORTANTE**: Cambia la contraseña del admin inmediatamente:

1. Login como admin
2. Ve a "Usuarios"
3. Busca tu usuario (cesar.vergara@clarovtr.cl)
4. Click "Editar"
5. Cambia la contraseña
6. Guarda

### 7.3 Monitoreo

**Render:**
- Revisa logs en tiempo real en "Logs"
- Configura alertas en "Events"

**Vercel:**
- Revisa analytics en "Analytics"
- Revisa logs en "Deployments"

**Supabase:**
- Revisa uso de base de datos en "Reports"
- Configura backups en "Database" → "Backups"

## 🆘 Solución de Problemas Comunes

### Backend no inicia

**Síntoma**: Error 500 o servicio no responde

**Soluciones**:
1. Revisa logs en Render
2. Verifica todas las variables de ambiente
3. Verifica que Supabase esté funcionando
4. Verifica que la Google API key sea válida

### Frontend muestra error de red

**Síntoma**: "Network Error" o "Failed to fetch"

**Soluciones**:
1. Verifica `NEXT_PUBLIC_API_URL` en Vercel
2. Verifica `ALLOWED_ORIGINS` en Render
3. Verifica que el backend esté corriendo
4. Revisa HTTPS (ambos deben usar HTTPS)

### No puedo hacer login

**Síntoma**: "Email o contraseña incorrectos"

**Soluciones**:
1. Verifica que el usuario admin se creó en Supabase:
   - Ve a Supabase → Table Editor → usuarios
   - Busca cesar.vergara@clarovtr.cl
2. Si no existe, conéctate a tu backend con Postman y crea el usuario
3. Verifica JWT_SECRET_KEY en Render

### Análisis falla

**Síntoma**: Error al crear análisis

**Soluciones**:
1. Verifica credenciales del gateway (GATEWAY_USERNAME, GATEWAY_PASSWORD)
2. Verifica que el gateway esté accesible
3. Verifica GOOGLE_API_KEY
4. Revisa logs en Render para ver el error específico

## 📊 Monitoreo Continuo

### Límites del Plan Gratuito

**Render Free Tier:**
- 750 horas/mes de uso
- Se duerme después de 15 minutos de inactividad
- Primer request tarda ~30 segundos en despertar

**Vercel Free Tier:**
- Deployments ilimitados
- 100 GB de ancho de banda/mes
- Funciones serverless con límite de ejecución

**Supabase Free Tier:**
- 500 MB de base de datos
- 1 GB de almacenamiento
- 2 GB de transferencia/mes

**Google Gemini:**
- 60 requests/minuto (gratis)
- Cuota diaria generosa

### Upgrade Recomendado (Futuro)

Cuando necesites más recursos:

1. **Render**: $7/mes para instancia dedicada
2. **Vercel**: $20/mes para Pro
3. **Supabase**: $25/mes para Pro

## ✅ Checklist Final

- [ ] Backend desplegado en Render
- [ ] Frontend desplegado en Vercel
- [ ] Base de datos configurada en Supabase
- [ ] Usuario admin creado y funcional
- [ ] CORS configurado correctamente
- [ ] Login funciona
- [ ] Crear usuario funciona
- [ ] Análisis funciona
- [ ] Chat funciona
- [ ] Contraseña del admin cambiada
- [ ] URLs documentadas
- [ ] Variables de ambiente respaldadas de forma segura

---

## 🎉 ¡Listo!

Tu sistema está completamente operativo en producción.

**URLs Finales:**
- Backend API: `https://tu-backend.onrender.com`
- Frontend: `https://tu-frontend.vercel.app`
- API Docs: `https://tu-backend.onrender.com/docs`
- Supabase: `https://app.supabase.com/project/tu-proyecto`

**Credenciales Iniciales:**
- Email: cesar.vergara@clarovtr.cl
- Password: [la que estableciste]

**Próximos Pasos:**
1. Crea usuarios adicionales
2. Empieza a hacer análisis
3. Familiarízate con el sistema
4. Customiza según tus necesidades

**Soporte:**
cesar.vergara@clarovtr.cl
