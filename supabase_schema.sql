-- ============================================
-- SCHEMA SUPABASE - ADMINISTRADOR WIFI
-- ============================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLA: USUARIOS
-- ============================================
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(255),
    rol VARCHAR(20) DEFAULT 'user' CHECK (rol IN ('admin', 'user')),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);

-- ============================================
-- TABLA: ANÁLISIS DE GATEWAYS
-- ============================================
CREATE TABLE analisis_gateways (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    mac_address VARCHAR(17) NOT NULL,
    datos_tecnicos JSONB NOT NULL,
    informe_ia TEXT,
    estado VARCHAR(50) DEFAULT 'completado',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_analisis_usuario ON analisis_gateways(usuario_id);
CREATE INDEX idx_analisis_mac ON analisis_gateways(mac_address);
CREATE INDEX idx_analisis_fecha ON analisis_gateways(created_at DESC);

-- ============================================
-- TABLA: HISTORIAL DE CHAT
-- ============================================
CREATE TABLE chat_historial (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analisis_id UUID REFERENCES analisis_gateways(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_chat_analisis ON chat_historial(analisis_id);
CREATE INDEX idx_chat_usuario ON chat_historial(usuario_id);

-- ============================================
-- TABLA: SESIONES
-- ============================================
CREATE TABLE sesiones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_sesiones_usuario ON sesiones(usuario_id);
CREATE INDEX idx_sesiones_token ON sesiones(token);
CREATE INDEX idx_sesiones_expira ON sesiones(expires_at);

-- ============================================
-- FUNCIÓN: Actualizar timestamp
-- ============================================
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para usuarios
CREATE TRIGGER trigger_usuarios_updated
    BEFORE UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Habilitar RLS
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE analisis_gateways ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_historial ENABLE ROW LEVEL SECURITY;
ALTER TABLE sesiones ENABLE ROW LEVEL SECURITY;

-- Políticas para usuarios (solo admins pueden ver todos)
CREATE POLICY "Usuarios pueden ver su propio perfil"
    ON usuarios FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Admins pueden ver todos los usuarios"
    ON usuarios FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM usuarios
            WHERE id = auth.uid() AND rol = 'admin'
        )
    );

-- Políticas para análisis
CREATE POLICY "Usuarios pueden ver sus propios análisis"
    ON analisis_gateways FOR SELECT
    USING (usuario_id = auth.uid());

CREATE POLICY "Usuarios pueden crear análisis"
    ON analisis_gateways FOR INSERT
    WITH CHECK (usuario_id = auth.uid());

-- ============================================
-- INSERTAR USUARIO ADMINISTRADOR INICIAL
-- ============================================
-- NOTA: La contraseña debe ser hasheada en el backend
-- Esta es solo una referencia para el setup inicial
INSERT INTO usuarios (email, password_hash, nombre, rol, activo)
VALUES (
    'cesar.vergara@clarovtr.cl',
    -- Este hash será generado por el backend
    '$2b$12$placeholder_hash',
    'Cesar Vergara',
    'admin',
    true
);

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista de análisis con información de usuario
CREATE VIEW vista_analisis_completo AS
SELECT 
    a.id,
    a.mac_address,
    a.estado,
    a.created_at,
    u.email as usuario_email,
    u.nombre as usuario_nombre,
    (a.datos_tecnicos->>'basic_info') as info_basica
FROM analisis_gateways a
JOIN usuarios u ON a.usuario_id = u.id;

-- Vista de estadísticas por usuario
CREATE VIEW vista_estadisticas_usuario AS
SELECT 
    u.id,
    u.email,
    u.nombre,
    COUNT(a.id) as total_analisis,
    MAX(a.created_at) as ultimo_analisis,
    u.ultimo_acceso
FROM usuarios u
LEFT JOIN analisis_gateways a ON u.id = a.usuario_id
GROUP BY u.id, u.email, u.nombre, u.ultimo_acceso;
