#!/usr/bin/env python
"""
Script de prueba para verificar que búsqueda y generación de recetas funcionan
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dani.settings')
django.setup()

print("=" * 70)
print("🧪 PRUEBA DE FUNCIONALIDADES")
print("=" * 70)

# Test 1: Búsqueda en línea
print("\n✅ TEST 1: Búsqueda de ingredientes en línea")
print("-" * 70)

from mattel.api_ingredientes import buscar_ingredientes
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/api/buscar-ingredientes/?q=tomate')

try:
    response = buscar_ingredientes(request)
    data = __import__('json').loads(response.content.decode())
    
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Total resultados: {data.get('total', 0)}")
    
    if data.get('resultados'):
        print(f"✅ Primer resultado: {data['resultados'][0].get('nombre', 'N/A')}")
        print(f"✅ Fuente: {data['resultados'][0].get('fuente', 'N/A')}")
    else:
        print("⚠️  Sin resultados")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 2: Generación de receta
print("\n✅ TEST 2: Generación de receta con fallback")
print("-" * 70)

from mattel.ai_service import generar_receta_con_gemini

ingredientes_test = ["tomate", "ajo", "sal"]
print(f"Ingredientes: {', '.join(ingredientes_test)}")

try:
    receta = generar_receta_con_gemini(ingredientes_test)
    
    if receta:
        print(f"✅ Nombre: {receta.get('nombre', 'N/A')}")
        print(f"✅ Dificultad: {receta.get('dificultad', 'N/A')}")
        print(f"✅ Tiempo: {receta.get('tiempo', 'N/A')}")
        print(f"✅ Pasos: {len(receta.get('pasos', []))} pasos")
        print(f"\n📝 Primeros 2 pasos:")
        for i, paso in enumerate(receta.get('pasos', [])[:2], 1):
            print(f"   {i}. {paso[:60]}...")
    else:
        print("❌ No se generó receta")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 70)
