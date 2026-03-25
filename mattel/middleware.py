"""
Middleware de seguridad avanzada
Se ejecuta en cada request
"""

from django.http import HttpResponseForbidden
from mattel.advanced_security import SecurityHeadersMiddleware, IPReputationFilter
import logging

logger = logging.getLogger('security_audit')


class AdvancedSecurityMiddleware:
    """Middleware que aplica protección a TODAS las requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # ✅ ANTES de procesar la request
        
        ip = request.META.get('REMOTE_ADDR')

        # 1. Permitir localhost siempre (Whitelist)
        if ip in ['0.0.0.0', '127.0.0.1']:
            logger.warning(f"IP local detectada: {ip}")
        else:
            # 2. Verificar reputación de IP (Solo para IPs externas)
            is_reputed, _ = IPReputationFilter.check_ip_reputation(ip)
            if not is_reputed:
                logger.error(f"IP BLOQUEADA: {ip}")
                return HttpResponseForbidden("Acceso denegado por reputación de IP")
        
        # Procesar la request normalmente
        response = self.get_response(request)
        
        # ✅ DESPUÉS de procesar la request
        
        # 3. Agregar security headers
        response = SecurityHeadersMiddleware.add_security_headers(response)
        
        return response


class LogSecurityMiddleware:
    """Middleware que registra todas las acciones de seguridad"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Registrar información de la request
        method = request.method
        path = request.path
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        ip = request.META.get('REMOTE_ADDR')
        
        # Información sensible a registrar
        if method in ['POST', 'PUT', 'DELETE']:
            logger.info(f"ACCION: {method} {path} | Usuario: {user} | IP: {ip}")
        
        response = self.get_response(request)
        
        # Registrar respuestas anómalas
        if response.status_code >= 400:
            logger.warning(f"ERROR: {response.status_code} en {path}")
        
        return response
