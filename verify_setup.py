#!/usr/bin/env python
"""
Script de verificación para Generador de Recetas con IA
Ejecuta: python verify_setup.py
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    print("✓ Verificando versión de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} - Se requiere 3.7+")
        return False

def check_required_files():
    """Verifica que existan los archivos necesarios"""
    print("\n✓ Verificando archivos creados...")
    files = [
        'mattel/ai_service.py',
        'mattel/templates/mattel/receta_gemini.html',
        'mattel/templates/mattel/recetas_multiples_gemini.html',
        'GEMINI_SETUP.md',
        'README_GEMINI_IA.md',
        'INICIO_RAPIDO.txt',
        '.env.example',
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ FALTA: {file}")
            all_exist = False
    
    return all_exist

def check_packages():
    """Verifica que los paquetes estén instalados"""
    print("\n✓ Verificando paquetes instalados...")
    packages = [
        ('django', 'Django'),
        ('google.generativeai', 'google-generativeai'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_installed = True
    for module, name in packages:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ FALTA: {name} - Instala con: pip install {name}")
            all_installed = False
    
    return all_installed

def check_api_key():
    """Verifica que la API key esté configurada"""
    print("\n✓ Verificando configuración de Gemini API...")
    
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if api_key and api_key != 'TU_API_KEY_AQUI':
        # Mostrar solo los primeros y últimos caracteres por seguridad
        masked = f"{api_key[:10]}...{api_key[-5:]}"
        print(f"  ✓ GEMINI_API_KEY configurada: {masked}")
        return True
    else:
        print("  ⚠️  GEMINI_API_KEY no configurada")
        print("     Ejecuta en PowerShell:")
        print("     $env:GEMINI_API_KEY = 'tu_api_key_aqui'")
        return False

def check_django_settings():
    """Verifica que settings.py tenga la configuración"""
    print("\n✓ Verificando configuración en settings.py...")
    
    try:
        with open('dani/settings.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content:
                print("  ✓ GEMINI_API_KEY en settings.py")
                return True
            else:
                print("  ✗ GEMINI_API_KEY no encontrada en settings.py")
                return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def check_urls():
    """Verifica que las URLs estén configuradas"""
    print("\n✓ Verificando rutas en urls.py...")
    
    try:
        with open('mattel/urls.py', 'r', encoding='utf-8') as f:
            content = f.read()
            routes = [
                'generar-receta-ia',
                'generar-multiples-ia',
                'guardar-receta-ia',
            ]
            
            all_found = True
            for route in routes:
                if route in content:
                    print(f"  ✓ Ruta: /{route}/")
                else:
                    print(f"  ✗ Falta: /{route}/")
                    all_found = False
            
            return all_found
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def check_views():
    """Verifica que las vistas estén definidas"""
    print("\n✓ Verificando vistas en views.py...")
    
    try:
        with open('mattel/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
            views = [
                'generar_receta_gemini',
                'generar_multiples_recetas_ia',
                'guardar_receta_gemini',
            ]
            
            all_found = True
            for view in views:
                if view in content:
                    print(f"  ✓ Vista: {view}()")
                else:
                    print(f"  ✗ Falta: {view}()")
                    all_found = False
            
            return all_found
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Ejecuta todas las verificaciones"""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   VERIFICADOR - Generador de Recetas con IA              ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    results = []
    
    results.append(("Python", check_python_version()))
    results.append(("Archivos", check_required_files()))
    results.append(("Paquetes", check_packages()))
    results.append(("API Key", check_api_key()))
    results.append(("Settings", check_django_settings()))
    results.append(("URLs", check_urls()))
    results.append(("Views", check_views()))
    
    print("\n" + "═" * 60)
    print("RESUMEN FINAL:")
    print("═" * 60)
    
    for name, result in results:
        status = "✓ OK" if result else "⚠️  REVISA"
        print(f"{name:.<45} {status}")
    
    print("\n" + "═" * 60)
    
    all_ok = all(result for _, result in results)
    
    if all_ok:
        print("\n🎉 ¡TODOS LOS VERIFICADORES PASARON! 🎉")
        print("\nAhora puedes ejecutar:")
        print("  $ python manage.py runserver")
    else:
        print("\n⚠️  ALGUNOS VERIFICADORES FALLARON")
        print("\nRevisa las secciones marcadas como 'REVISA'")
        print("\nLee los archivos de documentación:")
        print("  - INICIO_RAPIDO.txt (2 minutos)")
        print("  - GEMINI_SETUP.md (completo)")
        print("  - README_GEMINI_IA.md (características)")
    
    print("\n" + "═" * 60)

if __name__ == '__main__':
    main()
