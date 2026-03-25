#!/usr/bin/env python
"""
Script de prueba para verificar:
1. Cantidad de productos mostrados (20)
2. Recetas cargadas con cantidades
3. Sistema offline genera recetas con cantidades correctas
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dani.settings')
django.setup()

from mattel.models import Receta, Producto
from mattel.ai_service import generar_receta_fallback

print("=" * 60)
print("🧪 PRUEBAS DEL SISTEMA")
print("=" * 60)

# Test 1: Verificar cantidad de productos
print("\n📦 TEST 1: Cantidad de productos en BD")
print("-" * 60)
total_productos = Producto.objects.count()
print(f"✅ Total de productos en BD: {total_productos}")

# Test 2: Verificar cantidad de recetas cargadas
print("\n📚 TEST 2: Recetas cargadas con cantidades")
print("-" * 60)
total_recetas = Receta.objects.count()
print(f"✅ Total de recetas cargadas: {total_recetas}")

# Mostrar algunas recetas con sus pasos
print("\n📋 Primeras 3 recetas:")
for receta in Receta.objects.all()[:3]:
    print(f"\n  • {receta.nombre}")
    print(f"    - Tipo: {receta.tipo}")
    print(f"    - Tiempo: {receta.tiempo}")
    print(f"    - Dificultad: {receta.dificultad}")
    print(f"    - Pasos: {receta.pasos[:100]}...")

# Test 3: Prueba sistema offline con cantidades
print("\n\n🤖 TEST 3: Sistema offline con cantidades")
print("-" * 60)

# Simular ingredientes seleccionados CON cantidades
ingredientes_con_cantidades = [
    {"nombre": "Pescado", "cantidad": 500, "unidad": "gramos"},
    {"nombre": "Limón", "cantidad": 3, "unidad": "unidades"},
    {"nombre": "Cebolla", "cantidad": 1, "unidad": "unidades"},
    {"nombre": "Cilantro", "cantidad": 20, "unidad": "gramos"}
]

print("\n📝 Ingredientes seleccionados:")
for ing in ingredientes_con_cantidades:
    print(f"  • {ing['cantidad']} {ing['unidad']} de {ing['nombre']}")

print("\n🔄 Generando receta en modo offline...")
receta = generar_receta_fallback(ingredientes_con_cantidades)

if receta:
    print(f"\n✅ Receta generada exitosamente!")
    print(f"\n  📌 Nombre: {receta['nombre']}")
    print(f"  📄 Descripción: {receta['descripcion']}")
    print(f"  ⏱️  Tiempo: {receta['tiempo']}")
    print(f"  ⭐ Dificultad: {receta['dificultad']}")
    print(f"\n  📖 Pasos:")
    for i, paso in enumerate(receta['pasos'], 1):
        print(f"     {i}. {paso}")
    
    # Verificar si los pasos contienen las cantidades
    pasos_texto = " ".join(receta['pasos'])
    if "500" in pasos_texto or "gramos" in pasos_texto:
        print(f"\n  ✅ ¡Las cantidades se incluyen en los pasos!")
    else:
        print(f"\n  ⚠️  Las cantidades podrían no estar incluidas")
else:
    print("❌ Error al generar receta")

# Test 4: Prueba con ingredientes simples (strings)
print("\n\n🤖 TEST 4: Sistema offline con ingredientes simples")
print("-" * 60)

ingredientes_simples = ["Pollo", "Arroz", "Cebolla"]
print(f"\n📝 Ingredientes: {', '.join(ingredientes_simples)}")

receta2 = generar_receta_fallback(ingredientes_simples)
if receta2:
    print(f"\n✅ Receta generada!")
    print(f"  📌 Nombre: {receta2['nombre']}")
    print(f"  📖 Primeros 2 pasos:")
    for paso in receta2['pasos'][:2]:
        print(f"     • {paso}")
else:
    print("❌ Error al generar receta")

print("\n" + "=" * 60)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 60)
