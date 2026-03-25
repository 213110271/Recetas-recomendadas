"""
🔐 MÓDULO DE SEGURIDAD - Sistema de Protección de Contraseñas y Datos
Implementa validaciones, hashing, encriptación y auditoría de seguridad
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
import re


class PasswordValidator:
    """
    ✅ Validador de contraseñas FUERTES
    Verifica: longitud, mayúsculas, minúsculas, números, caracteres especiales
    """
    
    @staticmethod
    def validate(password):
        """
        Valida que la contraseña cumpla con criterios de seguridad
        Retorna: (es_válida, mensaje_de_error)
        """
        
        # Verificar longitud mínima (12 caracteres recomendado)
        if len(password) < 8:
            return False, "❌ Contraseña muy corta. Mínimo 8 caracteres."
        
        # Verificar máximo (128 caracteres por seguridad)
        if len(password) > 128:
            return False, "❌ Contraseña muy larga. Máximo 128 caracteres."
        
        # Verificar espacios en blanco
        if ' ' in password:
            return False, "❌ La contraseña no puede contener espacios."
        
        # Verificar que tenga al menos una mayúscula
        if not any(c.isupper() for c in password):
            return False, "❌ Debe tener al menos una MAYÚSCULA (A-Z)."
        
        # Verificar que tenga al menos una minúscula
        if not any(c.islower() for c in password):
            return False, "❌ Debe tener al menos una minúscula (a-z)."
        
        # Verificar que tenga al menos un número
        if not any(c.isdigit() for c in password):
            return False, "❌ Debe tener al menos un NÚMERO (0-9)."
        
        # Verificar que tenga al menos un carácter especial
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "❌ Debe tener al menos un carácter especial (!@#$%^&*...)."
        
        # Verificar contraseñas comunes (lista negra básica)
        common_passwords = [
            'password', '12345678', 'qwerty', 'abc12345',
            '123456789', 'password123', 'admin123', 'letmein'
        ]
        
        if password.lower() in common_passwords:
            return False, "❌ Esta contraseña es muy común. Elige una más única."
        
        # ✅ Contraseña válida
        return True, "✅ Contraseña fuerte y segura."
    
    @staticmethod
    def generate_strong_password(length=16):
        """Genera una contraseña fuerte aleatoria"""
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Asegurar que tenga al menos uno de cada tipo
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Rellenar el resto aleatoriamente
        all_chars = uppercase + lowercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Mezclar
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)


class RateLimiter:
    """
    🛡️ Protección contra ataques de fuerza bruta
    Limita intentos de login fallidos por IP/usuario
    """
    
    MAX_ATTEMPTS = 5  # Máximo de intentos fallidos
    LOCKOUT_TIME = 15  # Minutos bloqueado
    
    @staticmethod
    def get_cache_key(username, ip_address):
        """Genera clave única para cada usuario+IP"""
        return f"login_attempts:{username}:{ip_address}"
    
    @staticmethod
    def get_ip_address(request):
        """Obtiene la dirección IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def record_failed_attempt(request, username):
        """Registra un intento fallido de login"""
        ip = RateLimiter.get_ip_address(request)
        cache_key = RateLimiter.get_cache_key(username, ip)
        
        attempts = cache.get(cache_key, 0)
        attempts += 1
        
        # Guardar con expiración
        cache.set(cache_key, attempts, RateLimiter.LOCKOUT_TIME * 60)
        
        return attempts
    
    @staticmethod
    def is_locked_out(request, username):
        """Verifica si la cuenta está bloqueada"""
        ip = RateLimiter.get_ip_address(request)
        cache_key = RateLimiter.get_cache_key(username, ip)
        attempts = cache.get(cache_key, 0)
        return attempts >= RateLimiter.MAX_ATTEMPTS
    
    @staticmethod
    def get_remaining_attempts(request, username):
        """Obtiene los intentos restantes"""
        ip = RateLimiter.get_ip_address(request)
        cache_key = RateLimiter.get_cache_key(username, ip)
        attempts = cache.get(cache_key, 0)
        return max(0, RateLimiter.MAX_ATTEMPTS - attempts)
    
    @staticmethod
    def reset_attempts(request, username):
        """Limpia los intentos fallidos (después de login exitoso)"""
        ip = RateLimiter.get_ip_address(request)
        cache_key = RateLimiter.get_cache_key(username, ip)
        cache.delete(cache_key)


class AuditLog:
    """
    📋 Registro de auditoría
    Registra intentos de login, cambios de contraseña, etc.
    """
    
    @staticmethod
    def log_login_attempt(username, ip_address, success=False, reason=""):
        """Registra un intento de login"""
        from mattel.models import LoginAudit
        
        status = "SUCCESS" if success else "FAILED"
        print(f"🔐 AUDIT: [{status}] Usuario '{username}' desde IP {ip_address}. Razón: {reason}")
        
        try:
            LoginAudit.objects.create(
                username=username,
                ip_address=ip_address,
                success=success,
                reason=reason,
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"⚠️ Error al registrar auditoría: {e}")
    
    @staticmethod
    def log_password_change(user):
        """Registra un cambio de contraseña"""
        print(f"🔐 AUDIT: Usuario '{user.username}' cambió su contraseña")


class DataEncryption:
    """
    🔒 Encriptación de datos sensibles
    Cifra datos que se almacenan en la base de datos
    """
    
    @staticmethod
    def hash_sensitive_data(data):
        """
        Hashea datos sensibles (sin posibilidad de desencriptar)
        Útil para: emails, teléfonos, etc.
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def generate_secure_token(length=32):
        """Genera un token seguro para recovery, confirmación, etc."""
        return secrets.token_urlsafe(length)


def rate_limit_login(view_func):
    """
    🛡️ Decorador para proteger vistas de login contra fuerza bruta
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        username = request.POST.get('username', '').strip()
        
        # Solo aplicar rate limiting en POST (intentos de login)
        if request.method == 'POST' and username:
            if RateLimiter.is_locked_out(request, username):
                messages.error(
                    request, 
                    f"❌ Demasiados intentos fallidos. Intenta de nuevo en {RateLimiter.LOCKOUT_TIME} minutos."
                )
                return redirect('iniciar_sesion')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def secure_password_required(view_func):
    """
    🔐 Decorador que verifica contraseña segura antes de registrarse
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            password = request.POST.get('password', '')
            is_valid, message = PasswordValidator.validate(password)
            
            if not is_valid:
                messages.error(request, message)
                return redirect('registrarse')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# 📊 ESTADÍSTICAS DE SEGURIDAD
class SecurityStats:
    """Estadísticas de seguridad del sistema"""
    
    @staticmethod
    def get_stats():
        """Obtiene estadísticas de seguridad"""
        return {
            "max_login_attempts": RateLimiter.MAX_ATTEMPTS,
            "lockout_time_minutes": RateLimiter.LOCKOUT_TIME,
            "password_min_length": 8,
            "password_max_length": 128,
            "requires_uppercase": True,
            "requires_lowercase": True,
            "requires_digits": True,
            "requires_special_chars": True
        }
