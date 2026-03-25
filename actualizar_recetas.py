#!/usr/bin/env python
"""
Script para actualizar recetas con pasos detallados que incluyen cantidades de ingredientes.
Esto reemplaza el sistema de fixtures JSON para permitir pasos más complejos.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dani.settings')
django.setup()

from mattel.models import Receta, Producto

# Datos de recetas con pasos que incluyen cantidades
RECETAS_MEJORADAS = [
    {
        "pk": 2,
        "nombre": "Guisado de Res",
        "descripcion": "Carne de res cocida lentamente con verduras y especias.",
        "tipo": "guisado",
        "tiempo": "45 minutos",
        "dificultad": "Media",
        "pasos": """
1. Lavar 500 gramos de carne de res y cortar en cubos medianos.
2. Saltear la carne en una olla caliente con aceite caliente hasta dorar.
3. Agregar 1 cebolla picada y 3 dientes de ajo.
4. Incorporar 2 zanahorias y 3 papas cortadas en cubos.
5. Verter 1 litro de caldo de res.
6. Cocinar 40 minutos a fuego bajo.
7. Salpimentar al gusto y servir caliente.
"""
    },
    {
        "pk": 3,
        "nombre": "Sopa de Lentejas",
        "descripcion": "Sopa nutritiva con lentejas, zanahoria y apio.",
        "tipo": "sopa",
        "tiempo": "35 minutos",
        "dificultad": "Fácil",
        "pasos": """
1. Lavar 200 gramos de lentejas y remojar.
2. Hervir agua en una olla grande.
3. Agregar las lentejas a el agua hirviendo.
4. Picar 2 zanahorias, 1 tallo de apio y 1 cebolla.
5. Agregar las verduras a la olla.
6. Cocinar 30 minutos hasta que las lentejas estén suaves.
7. Condimentar con sal y servir caliente.
"""
    },
    {
        "pk": 21,
        "nombre": "Ceviche de Pescado",
        "descripcion": "Plato fresco de pescado marinado en limón y especias.",
        "tipo": "entrada",
        "tiempo": "20 minutos",
        "dificultad": "Media",
        "pasos": """
1. Cortar 500 gramos de pescado blanco fresco en cubos pequeños.
2. Exprimir 6 limones frescos en un bol.
3. Marinar el pescado en jugo de limón fresco 15 minutos.
4. Picar 1 cebolla morada finamente.
5. Picar 30 gramos de cilantro fresco.
6. Mezclar pescado con cebolla y cilantro.
7. Servir sobre camote cocido con maíz tostado.
"""
    }
]

def actualizar_recetas():
    """Actualizar recetas con pasos mejorados."""
    for datos in RECETAS_MEJORADAS:
        pk = datos["pk"]
        try:
            receta = Receta.objects.get(pk=pk)
            receta.nombre = datos["nombre"]
            receta.descripcion = datos["descripcion"]
            receta.tipo = datos["tipo"]
            receta.tiempo = datos["tiempo"]
            receta.dificultad = datos["dificultad"]
            receta.pasos = datos["pasos"]
            receta.save()
            print(f"✅ Actualizada receta: {receta.nombre}")
        except Receta.DoesNotExist:
            print(f"⚠️ Receta con pk={pk} no encontrada")
        except Exception as e:
            print(f"❌ Error al actualizar pk={pk}: {e}")

if __name__ == "__main__":
    actualizar_recetas()
    print("\n✅ Actualización completada")
