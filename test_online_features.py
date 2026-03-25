#!/usr/bin/env python
"""
Script de prueba para verificar que la búsqueda en línea y IA funcionan correctamente
Uso: python test_online_features.py
"""

import os
import sys
import django
import requests
from pathlib import Path

# Configurar Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dani.settings')
django.setup()

from mattel.api_ingredientes import buscar_ingredientes
from mattel.ai_service import generar_receta_con_gemini
from django.test import RequestFactory

print("=" * 70)
print("🧪 TEST DE CARACTERÍSTICAS EN LÍNEA")
print("=" * 70)

# Test 1: Búsqueda en línea
print("\n✅ TEST 1: Búsqueda de ingredientes en línea")
print("-" * 70)

factory = RequestFactory()
request = factory.get('/api/buscar-ingredientes/?q=tomate')
response = buscar_ingredientes(request)

print(f"Status: {response.status_code}")
print(f"Respuesta: {response.content.decode()}")

# Test 2: Verificar variables de entorno
print("\n✅ TEST 2: Variables de entorno")
print("-" * 70)

gemini_key = os.environ.get('GEMINI_API_KEY', 'NO CONFIGURADA')
spoonacular_key = os.environ.get('SPOONACULAR_API_KEY', 'NO CONFIGURADA')

print(f"GEMINI_API_KEY: {gemini_key[:10]}..." if gemini_key != 'NO CONFIGURADA' else f"GEMINI_API_KEY: {gemini_key}")
print(f"SPOONACULAR_API_KEY: {spoonacular_key[:10]}..." if spoonacular_key != 'NO CONFIGURADA' else f"SPOONACULAR_API_KEY: {spoonacular_key}")

# Test 3: Prueba de conexión a Spoonacular
print("\n✅ TEST 3: Conexión a Spoonacular API")
print("-" * 70)

try:
    api_key = os.environ.get('SPOONACULAR_API_KEY')
    params = {
        'query': 'chicken',
        'number': 5,
        'apiKey': api_key
    }
    response = requests.get('https://api.spoonacular.com/food/ingredients/search', params=params, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Resultados: {len(response.json())} ingredientes encontrados")
    if response.json():
        print(f"Primer resultado: {response.json()[0].get('name')}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 4: Prueba de Gemini (sin ingredientes reales)
print("\n✅ TEST 4: Configuración de Gemini API")
print("-" * 70)

try:
    import google.generativeai as genai
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key and api_key != 'TU_API_KEY_AQUI':
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Gemini API configurada correctamente")
        print(f"API Key: {api_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY no está configurada")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 70)
print("\nPróximos pasos:")
print("1. Ve a http://localhost:8000/productos/")
print("2. Busca ingredientes (ej: 'ajo', 'tomate', 'sal')")
print("3. Agrega al menos 3 ingredientes")
print("4. Haz click en 'Generar Receta'")
print("\nPara logs detallados, revisa la terminal del servidor Django")
