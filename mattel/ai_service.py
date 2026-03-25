import google.generativeai as genai
from django.conf import settings
import json
import re
import os
import concurrent.futures

# Obtener la API key de variables de entorno o de settings
def configurar_gemini():
    api_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)
    
    if api_key and api_key != 'TU_API_KEY_AQUI':
        try:
            genai.configure(api_key=api_key)
            return True
        except Exception as e:
            print(f"Error configurando Gemini API: {e}")
    
    return False

def generar_receta_con_gemini(productos_seleccionados):
    """
    Genera una receta usando Gemini basada en los productos seleccionados.
    Con reintentos y mejor manejo de cuota agotada.
    
    Args:
        productos_seleccionados: Lista con nombres de productos (strings) O
                                Lista de dicts con {nombre, cantidad, unidad}
    
    Returns:
        dict: Contiene nombre, descripcion, pasos, tiempo, dificultad, tipo
    """
    
    if not productos_seleccionados:
        return None
    
    # Convertir a formato legible para la IA
    if productos_seleccionados and isinstance(productos_seleccionados[0], dict):
        # Si son dicts con cantidad
        productos_str = ", ".join([
            f"{ing['cantidad']} {ing['unidad']} de {ing['nombre']}"
            for ing in productos_seleccionados
        ])
    else:
        # Si son strings simples
        productos_str = ", ".join(productos_seleccionados)
    
    # Verificar que la API esté configurada
   # Verificar que la API esté configurada
    if not configurar_gemini():
        print("⚠️ GEMINI_API_KEY no está configurada")
        return generar_receta_fallback(productos_seleccionados)
    
    # Crear el prompt para Gemini
    prompt = f"""Eres un chef profesional. Crea una receta deliciosa y práctica usando estos ingredientes: {productos_str}

Responde en formato JSON con esta estructura exacta:
{{
    "nombre": "nombre de la receta",
    "descripcion": "descripción breve de la receta",
    "pasos": ["paso 1", "paso 2", "paso 3", ...],
    "tiempo": "tiempo estimado (ej: 30 minutos)",
    "dificultad": "Fácil|Media|Difícil",
    "tipo": "ensalada|guisado|sopa|postre|bebida|sandwich|pasta|carne|mariscos|vegana|pizza|tacos|wrap|arroz|cereal|pan|dulce|salado|light|rápida",
    "rendimiento": "cantidad de porciones (ej: 4 porciones)"
}}

La receta debe:
- Usar principalmente los ingredientes proporcionados
- Ser realista y práctica
- Incluir al menos 5-7 pasos detallados
- Tener instrucciones claras

Solo responde el JSON, sin explicaciones adicionales."""

    max_intentos = 3
    ultimo_error = None
    timeout_seconds = 20
    
    for intento in range(max_intentos):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(model.generate_content, prompt)
                response = future.result(timeout=timeout_seconds)
            
            response_text = response.text
            
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            m = re.search(r'\{[\s\S]*\}', response_text)
            if m:
                response_text = m.group(0)
            
            receta_data = json.loads(response_text)
            
            print(f"✅ Receta generada exitosamente con Gemini (intento {intento + 1})")
            return receta_data
            
        except json.JSONDecodeError as e:
            ultimo_error = f"JSON inválido: {str(e)}"
            print(f"⚠️ Intento {intento + 1}/{max_intentos}: JSON inválido de Gemini")
            if intento == max_intentos - 1:
                print(f"❌ No se pudo generar receta: {ultimo_error}")
                return generar_receta_fallback(productos_seleccionados)
        except concurrent.futures.TimeoutError:
            ultimo_error = "Timeout esperando respuesta de Gemini"
            print(f"⚠️ Intento {intento + 1}/{max_intentos}: Timeout de {timeout_seconds}s")
            if intento == max_intentos - 1:
                print("❌ Timeout persistente. Usando receta offline...")
                return generar_receta_fallback(productos_seleccionados)
        except Exception as e:
            error_str = str(e)
            ultimo_error = str(e)
            
            if "429" in error_str or "ResourceExhausted" in error_str or "quota" in error_str.lower():
                print(f"⚠️ Intento {intento + 1}/{max_intentos}: Cuota de Gemini agotada")
                if intento == max_intentos - 1:
                    print("❌ Cuota de Gemini agotada. Usando receta offline...")
                    return generar_receta_fallback(productos_seleccionados)
            else:
                print(f"⚠️ Intento {intento + 1}/{max_intentos}: Error en Gemini - {type(e).__name__}")
                if intento == max_intentos - 1:
                    print(f"❌ Error después de {max_intentos} intentos: {ultimo_error}")
                    return generar_receta_fallback(productos_seleccionados)
    
    print("⚠️ Fallback final: Generando receta offline")
    return generar_receta_fallback(productos_seleccionados)


def generar_receta_fallback(productos_seleccionados):

    """
    Genera una receta sin usar API de IA (fallback).
    Se usa cuando Gemini API falla o alcanza cuota.
    Ahora respeta las cantidades elegidas por el usuario.
    """
    if not productos_seleccionados:
        return None
    
    import random
    
    # Mantener las cantidades elegidas por el usuario
    ingredientes_con_cantidad = []
    ingredientes_nombres = []
    
    for ing in productos_seleccionados:
        if isinstance(ing, dict):
            # Si es dict con cantidad y unidad
            nombre = ing.get('nombre', str(ing))
            cantidad = ing.get('cantidad', '')
            unidad = ing.get('unidad', '')
            if cantidad and unidad:
                ingredientes_con_cantidad.append(f"{cantidad} {unidad} de {nombre}")
                ingredientes_nombres.append(nombre)
            else:
                ingredientes_con_cantidad.append(nombre)
                ingredientes_nombres.append(nombre)
        else:
            # Si es string directo
            ingredientes_con_cantidad.append(str(ing))
            ingredientes_nombres.append(str(ing))
    
    # Usar todos los ingredientes (o máximo 6) en la receta
    max_ingredientes = min(len(ingredientes_con_cantidad), 6)
    ingredientes_usados = ingredientes_con_cantidad[:max_ingredientes]
    ingredientes_txt = ", ".join(ingredientes_usados)
    
    # Principales para el nombre
    principales_nombres = ingredientes_nombres[:min(3, len(ingredientes_nombres))]
    principales_txt = ", ".join(principales_nombres)
    
    # Generar nombre creativo
    opciones_nombre = [
        f"Delicia de {principales_txt}",
        f"{principales_txt} al Estilo Casero",
        f"Preparación Especial de {principales_txt}",
        f"{principales_txt} Gourmet",
        f"Fusión de {principales_txt}",
    ]
    
    titulo = random.choice(opciones_nombre)
    
    # Pasos fijos pero variados
    pasos_opciones = [
        [
            f"Lava cuidadosamente los ingredientes: {ingredientes_txt}.",
            f"Corta {principales_txt} en trozos medianos.",
            f"Saltea {principales_txt} a fuego alto para activar aromas.",
            "Añade los ingredientes restantes y cocina a fuego medio.",
            "Rectifica sazón con hierbas secas.",
            "Cocina hasta obtener una consistencia suave.",
            "Sirve caliente."
        ],
        [
            f"Enjuaga los ingredientes frescos: {ingredientes_txt}.",
            f"Corta {principales_txt} finamente.",
            f"Sofríe {principales_txt} con un toque de aceite.",
            "Agrega los demás ingredientes y mezcla bien.",
            "Añade sal, ajo y pimienta al gusto.",
            "Cocina 12 minutos a fuego medio.",
            "Sirve decorado con perejil."
        ],
        [
            f"Limpia y seca los ingredientes: {ingredientes_txt}.",
            f"Machaca ligeramente {principales_txt} para intensificar sabor.",
            f"Coloca {principales_txt} en una olla caliente.",
            "Incorpora los ingredientes restantes.",
            "Usa sal, orégano y especias suaves.",
            "Cocina lentamente para un sabor profundo.",
            "Sirve tibio."
        ]
    ]
    
    pasos = random.choice(pasos_opciones)
    
    return {
        "nombre": titulo,
        "descripcion": f"Preparación casera basada en {principales_txt}. (Modo offline)",
        "pasos": pasos,
        "tiempo": "30 minutos",
        "dificultad": "Fácil",
        "tipo": "ensalada",
        "rendimiento": "4 porciones",
        "_offline": True
    }



def generar_multiples_recetas_gemini(productos_seleccionados, cantidad=3):
    """
    Genera múltiples recetas variadas usando Gemini.
    
    Args:
        productos_seleccionados: Lista con nombres de productos
        cantidad: Número de recetas a generar (1-5)
    
    Returns:
        list: Lista de diccionarios con recetas
    """
    
    cantidad = min(max(cantidad, 1), 5)  # Límitar entre 1-5
    recetas = []
    
    for i in range(cantidad):
        receta = generar_receta_con_gemini(productos_seleccionados)
        if receta:
            recetas.append(receta)
    
    return recetas
