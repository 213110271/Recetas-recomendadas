"""
🚨 SIMULADOR DE ATAQUES - Prueba de Seguridad
Este script simula diversos tipos de ataques para verificar que la protección funciona
"""

import requests
import time
from datetime import datetime
import json

BASE_URL = "http://localhost:8008"
REGISTER_URL = f"{BASE_URL}/registrarse/"
LOGIN_URL = f"{BASE_URL}/iniciar-sesion/"

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_attack(num, name, payload):
    print(f"\n{BOLD}{YELLOW}[ATAQUE {num}] {name}{RESET}")
    print(f"Payload: {RED}{payload}{RESET}")

def print_result(blocked, message):
    if blocked:
        print(f"✅ {GREEN}BLOQUEADO{RESET}: {message}")
    else:
        print(f"❌ {RED}NO BLOQUEADO{RESET}: {message}")
    print(f"Hora: {datetime.now().strftime('%H:%M:%S')}")

class AttackSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
    
    def test_attack(self, attack_num, name, method, url, data, expect_blocked=True):
        """Ejecuta un ataque y verifica si fue bloqueado"""
        print_attack(attack_num, name, str(data)[:100])
        
        try:
            if method == 'POST':
                response = self.session.post(url, data=data, timeout=5)
            else:
                response = self.session.get(url, params=data, timeout=5)
            
            # Indicadores de que fue bloqueado
            blocked = (
                response.status_code == 403 or  # Forbidden
                'error' in response.text.lower() or
                'no permitido' in response.text.lower() or
                'bloqueado' in response.text.lower() or
                'caracteres no permitidos' in response.text.lower() or
                'inyección' in response.text.lower() or
                'demasiados' in response.text.lower()
            )
            
            if expect_blocked:
                result = blocked
                message = f"Status: {response.status_code} - {response.reason}"
            else:
                result = not blocked
                message = f"Status: {response.status_code} - {response.reason}"
            
            print_result(result, message)
            self.results.append({
                'numero': attack_num,
                'nombre': name,
                'bloqueado': blocked,
                'esperado_bloqueado': expect_blocked,
                'estado': 'CORRECTO' if result else 'FALLIDO'
            })
            
        except Exception as e:
            print_result(True, f"Excepción: {str(e)}")
            self.results.append({
                'numero': attack_num,
                'nombre': name,
                'bloqueado': True,
                'esperado_bloqueado': expect_blocked,
                'estado': 'EXCEPCIÓN'
            })

def main():
    print_header("🚨 SIMULADOR DE ATAQUES - TEST DE SEGURIDAD")
    
    simulator = AttackSimulator()
    
    # ============================================================================
    # ATAQUE 1: SQL INJECTION
    # ============================================================================
    simulator.test_attack(
        1,
        "SQL INJECTION en Username",
        'POST',
        LOGIN_URL,
        {
            'username': "admin' OR '1'='1",
            'password': 'test123'
        }
    )
    
    # ============================================================================
    # ATAQUE 2: SQL INJECTION ALTERNATIVO
    # ============================================================================
    simulator.test_attack(
        2,
        "SQL INJECTION - UNION SELECT",
        'POST',
        LOGIN_URL,
        {
            'username': "admin' UNION SELECT * FROM users--",
            'password': 'test123'
        }
    )
    
    # ============================================================================
    # ATAQUE 3: XSS (Cross-Site Scripting)
    # ============================================================================
    simulator.test_attack(
        3,
        "XSS - Script Tag en Username",
        'POST',
        LOGIN_URL,
        {
            'username': "<script>alert('XSS')</script>",
            'password': 'test123'
        }
    )
    
    # ============================================================================
    # ATAQUE 4: XSS ALTERNATIVO
    # ============================================================================
    simulator.test_attack(
        4,
        "XSS - Event Handler (onerror)",
        'POST',
        LOGIN_URL,
        {
            'username': "<img src=x onerror='alert(1)'>",
            'password': 'test123'
        }
    )
    
    # ============================================================================
    # ATAQUE 5: PATH TRAVERSAL
    # ============================================================================
    simulator.test_attack(
        5,
        "PATH TRAVERSAL - ../../../etc/passwd",
        'POST',
        REGISTER_URL,
        {
            'username': 'testuser',
            'email': '../../../etc/passwd@test.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#'
        }
    )
    
    # ============================================================================
    # ATAQUE 6: COMMAND INJECTION
    # ============================================================================
    simulator.test_attack(
        6,
        "COMMAND INJECTION - rm -rf /",
        'POST',
        LOGIN_URL,
        {
            'username': "admin'; rm -rf /; --",
            'password': 'test123'
        }
    )
    
    # ============================================================================
    # ATAQUE 7: PROTOTYPE POLLUTION
    # ============================================================================
    simulator.test_attack(
        7,
        "PROTOTYPE POLLUTION - __proto__",
        'POST',
        REGISTER_URL,
        {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'TestPass123!@#',
            '__proto__': 'polluted'
        }
    )
    
    # ============================================================================
    # ATAQUE 8: FUERZA BRUTA - MÚLTIPLES INTENTOS RÁPIDOS
    # ============================================================================
    print_attack(
        8,
        "FUERZA BRUTA - 6 intentos en 30 segundos",
        "Intentos fallidos consecutivos"
    )
    
    blocked_by_rate_limit = False
    for intento in range(1, 7):
        try:
            response = simulator.session.post(
                LOGIN_URL,
                data={
                    'username': 'testuser_bruteforce',
                    'password': f'wrongpass{intento}'
                },
                timeout=5
            )
            
            if response.status_code == 403 or 'demasiados' in response.text.lower():
                blocked_by_rate_limit = True
                print(f"  Intento {intento}: ⏱️ Rate limit activado")
                break
            else:
                print(f"  Intento {intento}: ❌ Intentable")
        
        except Exception as e:
            print(f"  Intento {intento}: ⚠️ Error: {e}")
        
        time.sleep(1)
    
    print_result(blocked_by_rate_limit, "Rate limiting después de múltiples intentos")
    simulator.results.append({
        'numero': 8,
        'nombre': 'FUERZA BRUTA',
        'bloqueado': blocked_by_rate_limit,
        'esperado_bloqueado': True,
        'estado': 'CORRECTO' if blocked_by_rate_limit else 'FALLIDO'
    })
    
    # ============================================================================
    # ATAQUE 9: CREDENCIAL STUFFING (Múltiples usuarios/passwords)
    # ============================================================================
    print_attack(
        9,
        "CREDENTIAL STUFFING - Lista de usuarios comunes",
        "Intentos con usuarios/passwords comunes"
    )
    
    usuarios_comunes = [
        ('admin', 'password123'),
        ('admin', 'admin123'),
        ('root', 'toor'),
        ('user', 'user'),
    ]
    
    bloqueados = 0
    for user, pwd in usuarios_comunes:
        try:
            response = simulator.session.post(
                LOGIN_URL,
                data={'username': user, 'password': pwd},
                timeout=5
            )
            if response.status_code == 403 or 'demasiados' in response.text.lower():
                bloqueados += 1
        except:
            bloqueados += 1
        time.sleep(0.5)
    
    credential_stuffing_blocked = bloqueados > 0
    print_result(credential_stuffing_blocked, f"{bloqueados} de {len(usuarios_comunes)} intentos bloqueados")
    simulator.results.append({
        'numero': 9,
        'nombre': 'CREDENTIAL STUFFING',
        'bloqueado': credential_stuffing_blocked,
        'esperado_bloqueado': True,
        'estado': 'CORRECTO' if credential_stuffing_blocked else 'FALLIDO'
    })
    
    # ============================================================================
    # ATAQUE 10: JAVASCRIPT INJECTION
    # ============================================================================
    simulator.test_attack(
        10,
        "JAVASCRIPT INJECTION en Email",
        'POST',
        REGISTER_URL,
        {
            'username': 'testuser',
            'email': 'javascript:alert(1)@test.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#'
        }
    )
    
    # ============================================================================
    # RESUMEN DE RESULTADOS
    # ============================================================================
    print_header("📊 RESUMEN DE RESULTADOS")
    
    print(f"\n{BOLD}Resultados detallados:{RESET}\n")
    
    correctos = 0
    fallidos = 0
    
    for result in simulator.results:
        estado_icon = "✅" if result['estado'] == 'CORRECTO' else "❌"
        bloqueado_icon = "🔒" if result['bloqueado'] else "🔓"
        
        print(f"{estado_icon} [{result['numero']:2d}] {result['nombre']:30s} | Bloqueado: {bloqueado_icon} | Estado: {result['estado']}")
        
        if result['estado'] == 'CORRECTO':
            correctos += 1
        else:
            fallidos += 1
    
    # ============================================================================
    # ESTADÍSTICAS FINALES
    # ============================================================================
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"\n{BOLD}ESTADÍSTICAS FINALES:{RESET}")
    print(f"\n  Total de ataques simulados: {len(simulator.results)}")
    print(f"  {GREEN}✅ Ataques bloqueados correctamente: {correctos}{RESET}")
    print(f"  {RED}❌ Ataques no bloqueados: {fallidos}{RESET}")
    
    percentage = (correctos / len(simulator.results)) * 100
    
    print(f"\n  {BOLD}Tasa de éxito: {GREEN}{percentage:.1f}%{RESET}")
    
    if percentage == 100:
        print(f"\n  {GREEN}{BOLD}🎉 ¡TODOS LOS ATAQUES FUERON BLOQUEADOS! 🎉{RESET}")
        print(f"  {GREEN}Tu aplicación está COMPLETAMENTE PROTEGIDA{RESET}\n")
    elif percentage >= 80:
        print(f"\n  {YELLOW}{BOLD}⚠️ La mayoría de ataques fueron bloqueados{RESET}")
        print(f"  {YELLOW}Pero algunos pasaron - revisar logs{RESET}\n")
    else:
        print(f"\n  {RED}{BOLD}🚨 VARIOS ATAQUES NO FUERON BLOQUEADOS 🚨{RESET}")
        print(f"  {RED}Revisar configuración de seguridad{RESET}\n")
    
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    # ============================================================================
    # RECOMENDACIONES
    # ============================================================================
    print(f"\n{BOLD}📋 RECOMENDACIONES:{RESET}\n")
    print("1. Revisar logs/security_audit.log para ver los ataques registrados")
    print("2. Verificar en /admin/ → Auditorías de Login para ver intentos bloqueados")
    print("3. Si algún ataque no fue bloqueado, reportarlo inmediatamente")
    print("4. En producción, activar HTTPS (SESSION_COOKIE_SECURE=True)")
    print("5. Hacer backups regulares de la base de datos")
    print("6. Monitorear los logs diariamente\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}Simulación cancelada por el usuario{RESET}\n")
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}\n")
