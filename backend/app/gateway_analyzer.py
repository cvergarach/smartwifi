# ============================================
# GATEWAY_ANALYZER.PY - Análisis de Gateways
# ============================================

import requests
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import settings

# Ignorar advertencias SSL
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ============================================
# PROMPT POR DEFECTO
# ============================================

DEFAULT_PROMPT = """
# ROL Y OBJETIVO
Actúa como un ingeniero de redes senior y experto en soporte técnico. Tu misión es traducir los siguientes datos técnicos crudos en un informe ejecutivo para un agente de call center que necesita entender rápidamente la situación de un cliente y darle soluciones claras.

# REGLAS CRÍTICAS DE FORMATO Y TONO
- **Formato Estricto**: USA ÚNICAMENTE TEXTO PLANO. Está ABSOLUTAMENTE PROHIBIDO el uso de markdown.
- **Títulos**: Usa MAYÚSCULAS sostenidas para los títulos de las secciones principales.
- **Iconografía Simple**: Solo puedes usar estos emojis para indicar estado:
  - ✅: Bueno, sin problemas detectados.
  - ⚠️: Advertencia, algo podría mejorar o requiere monitoreo.
  - ❌: Problema crítico, requiere acción inmediata.
- **Claridad y Brevedad**: Usa líneas cortas, párrafos breves y separa las secciones con una línea en blanco.
- **Lenguaje Simple**: Traduce toda la jerga técnica.
- **Datos Faltantes**: Si una sección de datos no está disponible, indícalo explícitamente.

# ESTRUCTURA OBLIGATORIA DEL INFORME
INFORME DE DIAGNÓSTICO - GATEWAY RESIDENCIAL

ESTADO GENERAL DEL SERVICIO
[Usa ✅, ⚠️, o ❌. Describe en una o dos frases el estado general]

CALIDAD DE SEÑAL ÓPTICA
- Estado de la Conexión: [✅, ⚠️, ❌]
- Potencia Recibida (Rx): [Valor dBm y su interpretación]
- Potencia Transmitida (Tx): [Valor dBm y su interpretación]

DISPOSITIVOS CONECTADOS
[Lista de dispositivos con señal y velocidad]

CONFIGURACIÓN WIFI ACTUAL
- Red 2.4 GHz: [SSID, Canal, Ancho, Potencia]
- Red 5 GHz: [SSID, Canal, Ancho, Potencia]

ANÁLISIS DE INTERFERENCIA
[Identificar redes vecinas problemáticas]

HISTORIAL DE EVENTOS RECIENTES
[Resumir reinicios y cambios de canal]

ESTADO DE PUERTOS FÍSICOS (LAN)
[Estado de cada puerto LAN]

RECOMENDACIONES INMEDIATAS
[Lista de acciones claras y priorizadas]

PROBLEMAS DETECTADOS Y SOLUCIONES
- PROBLEMA: [Descripción]
  - SOLUCIÓN: [Acción específica]

--- DATOS TÉCNICOS RAW ---
{contenido}
"""

# ============================================
# CLASE ANALIZADOR DE GATEWAY
# ============================================

class GatewayAnalyzer:
    """
    Clase para analizar gateways WiFi Huawei
    """
    
    def __init__(self):
        self.base_url = settings.GATEWAY_BASE_URL
        self.username = settings.GATEWAY_USERNAME
        self.password = settings.GATEWAY_PASSWORD
        self.session = None
        self.headers = None
        
    def _get_session(self) -> requests.Session:
        """Crear sesión HTTP con autenticación"""
        if self.session is None:
            self.session = requests.Session()
            self.session.auth = (self.username, self.password)
            self.headers = {
                "Content-Type": "application/yang-data+json",
                "Accept": "application/yang-data+json"
            }
        return self.session
    
    def _api_call(
        self, 
        mac: str, 
        url: str, 
        method: str = 'get', 
        params: Optional[Dict] = None, 
        json_payload: Optional[Dict] = None, 
        timeout: int = 15
    ) -> str:
        """
        Realizar llamada a la API del gateway
        """
        try:
            session = self._get_session()
            
            if method == 'get':
                r = session.get(
                    url, 
                    headers=self.headers, 
                    params=params, 
                    verify=False, 
                    timeout=timeout
                )
            else:
                r = session.post(
                    url, 
                    headers=self.headers, 
                    json=json_payload, 
                    verify=False, 
                    timeout=timeout
                )
            
            r.raise_for_status()
            return "\n" + json.dumps(r.json(), indent=4)
        
        except requests.exceptions.HTTPError as e:
            try:
                error_details = e.response.json()
                return f"\n[i] No disponible o error en la consulta: {e.response.status_code} {e.response.reason}\nDetalles: {json.dumps(error_details, indent=2)}"
            except json.JSONDecodeError:
                return f"\n[i] No disponible o error en la consulta: {e}"
        except Exception as e:
            return f"\n[!] Error general: {e}"
    
    def get_basic_info(self, mac: str) -> str:
        """Obtener información básica del gateway"""
        output = "\n" + "="*80 + "\n===== INFORMACIÓN BÁSICA DEL GATEWAY =====\n" + "="*80
        url = f"{self.base_url}/restconf/v1/data/huawei-nce-resource-activation-configuration-home-gateway:home-gateway/home-gateway-info"
        return output + self._api_call(mac, url, params={"mac": mac})
    
    def get_connected_devices(self, mac: str) -> str:
        """Obtener dispositivos conectados"""
        output = "\n" + "="*80 + "\n===== DISPOSITIVOS CONECTADOS =====\n" + "="*80
        url = f"{self.base_url}/restconf/v1/data/huawei-nce-resource-activation-configuration-home-gateway:home-gateway/sub-devices"
        return output + self._api_call(mac, url, params={"mac": mac})
    
    def get_performance_data(self, mac: str) -> str:
        """Obtener datos de rendimiento"""
        output = "\n" + "="*80 + "\n===== DATOS DE RENDIMIENTO =====\n" + "="*80
        url = f"{self.base_url}/restconf/v1/operations/huawei-nce-homeinsight-performance-management:query-history-pm-datas"
        
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=1)
        
        payload = {
            "huawei-nce-homeinsight-performance-management:input": {
                "query-indicator-groups": {
                    "query-indicator-group": [{"indicator-group-name": "QUALITY_ANALYSIS"}]
                },
                "res-type-name": "HOME_NETWORK",
                "gateway-list": [{"gateway-mac": mac}],
                "data-type": "ANALYSIS_BY_5MIN",
                "start-time": start.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                "end-time": end.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            }
        }
        
        return output + self._api_call(mac, url, method='post', json_payload=payload, timeout=20)
    
    def get_wifi_band_info(self, mac: str) -> str:
        """Obtener configuración WiFi por banda"""
        output = "\n" + "="*80 + "\n===== CONFIGURACIÓN WIFI =====\n" + "="*80
        url = f"{self.base_url}/restconf/v1/data/huawei-nce-resource-activation-configuration-home-gateway:home-gateway/wifi-band"
        
        for band in ["2.4G", "5G"]:
            output += f"\n--- Banda {band} ---"
            output += self._api_call(mac, url, params={"mac": mac, "radio-type": band})
        
        return output
    
    def get_guest_wifi_info(self, mac: str) -> str:
        """Obtener información de WiFi invitados"""
        output = "\n" + "="*80 + "\n===== WIFI INVITADOS =====\n" + "="*80
        url = f"{self.base_url}/restconf/v1/operations/huawei-nce-resource-activation-configuration-home-gateway:query-gateway-guest-ssid"
        payload = {
            "huawei-nce-resource-activation-configuration-home-gateway:input": {"mac": mac}
        }
        return output + self._api_call(mac, url, method='post', json_payload=payload)
    
    def get_downstream_ports(self, mac: str) -> str:
        """Obtener estado de puertos LAN"""
        output = "\n" + "="*80 + "\n===== PUERTOS LAN =====\n" + "="*80
        url = f"{self.base_url}/restconf/v1/operations/huawei-nce-resource-activation-configuration-home-gateway:query-gateway-downstream-port"
        payload = {
            "huawei-nce-resource-activation-configuration-home-gateway:input": {"mac": mac}
        }
        return output + self._api_call(mac, url, method='post', json_payload=payload)
    
    def get_neighboring_ssids(self, mac: str) -> str:
        """Obtener redes WiFi vecinas"""
        output = "\n" + "="*80 + "\n===== REDES VECINAS =====\n" + "="*80
        url = f"{self.base_url}/restconf/v1/data/huawei-nce-resource-activation-configuration-home-gateway:home-gateway/neighbor-ssids"
        
        for band in ["2.4G", "5G"]:
            output += f"\n--- Banda {band} ---"
            output += self._api_call(mac, url, params={"mac": mac, "radio-type": band}, timeout=20)
        
        return output
    
    def get_session_info(self, mac: str) -> str:
        """Obtener sesiones activas"""
        output = "\n" + "="*80 + "\n===== SESIONES ACTIVAS =====\n" + "="*80
        url = f"{self.base_url}/restconf/v1/operations/huawei-nce-resource-activation-configuration-home-gateway:query-session-info"
        payload = {
            "huawei-nce-resource-activation-configuration-home-gateway:input": {"mac": mac}
        }
        return output + self._api_call(mac, url, method='post', json_payload=payload)
    
    def analyze_gateway(self, mac: str, incluir_eventos: bool = True) -> Dict[str, Any]:
        """
        Realizar análisis completo del gateway
        Retorna un diccionario con todos los datos técnicos
        """
        datos_tecnicos = {
            "mac_address": mac,
            "timestamp": datetime.now().isoformat(),
            "basic_info": self.get_basic_info(mac),
            "connected_devices": self.get_connected_devices(mac),
            "performance_data": self.get_performance_data(mac),
            "wifi_band_info": self.get_wifi_band_info(mac),
            "guest_wifi_info": self.get_guest_wifi_info(mac),
            "downstream_ports": self.get_downstream_ports(mac),
            "neighboring_ssids": self.get_neighboring_ssids(mac),
            "session_info": self.get_session_info(mac)
        }
        
        return datos_tecnicos
    
    def generate_ai_report(
        self, 
        datos_tecnicos: Dict[str, Any], 
        prompt_template: Optional[str] = None
    ) -> str:
        """
        Generar informe con IA usando los datos técnicos
        """
        # Convertir datos técnicos a texto
        contenido = "\n\n".join([
            f"{key.upper()}:\n{value}" 
            for key, value in datos_tecnicos.items() 
            if key not in ["mac_address", "timestamp"]
        ])
        
        # Usar prompt por defecto si no se proporciona uno
        template_str = prompt_template or DEFAULT_PROMPT
        
        # Configurar modelo de IA
        llm = ChatGoogleGenerativeAI(
            model=settings.AI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.AI_TEMPERATURE
        )
        
        # Crear prompt
        prompt = PromptTemplate(
            input_variables=["contenido"],
            template=template_str
        )
        
        # Generar informe
        chain = prompt | llm
        resultado = chain.invoke({"contenido": contenido})
        
        return resultado.content
    
    def chat_with_data(
        self, 
        pregunta: str, 
        datos_tecnicos: Dict[str, Any], 
        historial: Optional[list] = None
    ) -> str:
        """
        Hacer preguntas sobre los datos del análisis
        """
        # Preparar contexto
        contenido = "\n\n".join([
            f"{key.upper()}:\n{value}" 
            for key, value in datos_tecnicos.items() 
            if key not in ["mac_address", "timestamp"]
        ])
        
        # Construir historial si existe
        historial_str = ""
        if historial and len(historial) > 0:
            historial_str = "\n\n--- HISTORIAL DE CONVERSACIÓN ---\n"
            historial_str += "\n".join(historial[-settings.MAX_CHAT_HISTORY:])
        
        # Template de chat
        template_chat = f"""
Eres un asistente experto en análisis de redes WiFi. 
Responde a la siguiente pregunta basándote ÚNICAMENTE en los datos técnicos proporcionados.

{historial_str}

--- DATOS TÉCNICOS DEL GATEWAY ---
{contenido}

--- PREGUNTA DEL USUARIO ---
{{pregunta}}

Proporciona una respuesta clara, técnica pero entendible, basada SOLO en los datos disponibles.
Si la información no está disponible en los datos, indícalo claramente.
"""
        
        # Configurar modelo
        llm = ChatGoogleGenerativeAI(
            model=settings.AI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.5
        )
        
        # Crear prompt
        prompt = PromptTemplate(
            input_variables=["pregunta"],
            template=template_chat
        )
        
        # Generar respuesta
        chain = prompt | llm
        resultado = chain.invoke({"pregunta": pregunta})
        
        return resultado.content
