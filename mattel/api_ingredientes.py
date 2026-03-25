"""
API para búsqueda y gestión de ingredientes
"""
from django.http import JsonResponse
from .models import Producto
from django.views.decorators.http import require_http_methods
import json
import requests
import os

# API Keys para búsqueda en línea
SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY', 'a09cdaac6e5946d1933b8ea5a75ec5c9')  # Free tier
SPOONACULAR_BASE_URL = "https://api.spoonacular.com/food/ingredients/search"

@require_http_methods(["GET"])
def buscar_ingredientes(request):
    """
    Busca ingredientes por nombre (búsqueda en tiempo real)
    Primero intenta en línea con Spoonacular, luego en BD local como fallback
    GET /api/buscar-ingredientes/?q=cebolla
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'resultados': []})
    
    resultados = []
    
    try:
        # 1. Intentar búsqueda en línea con Spoonacular
        params = {
            'query': query,
            'number': 15,
            'apiKey': SPOONACULAR_API_KEY
        }
        
        try:
            response = requests.get(SPOONACULAR_BASE_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                datos_online = response.json()
                # Formatear resultados de Spoonacular
                for ing in datos_online:
                    resultados.append({
                        'id': ing.get('id'),
                        'nombre': ing.get('name', ing.get('title', '')),
                        'categoria': 'importado',
                        'precio': 0,
                        'fuente': 'online'
                    })
        except requests.exceptions.RequestException:
            # Si falla la búsqueda online, continuar con BD local
            pass
        
        # 2. Búsqueda en BD local como complemento
        productos_locales = Producto.objects.filter(
            nombre__icontains=query
        ).values('id', 'nombre', 'categoria', 'precio')[:10]
        
        for prod in productos_locales:
            prod['fuente'] = 'local'
            resultados.append(prod)
        
        # Remover duplicados (mantener online primero)
        nombres_vistos = set()
        resultados_unicos = []
        for res in resultados:
            nombre_lower = res['nombre'].lower()
            if nombre_lower not in nombres_vistos:
                nombres_vistos.add(nombre_lower)
                resultados_unicos.append(res)
        
        return JsonResponse({
            'resultados': resultados_unicos[:15],
            'total': len(resultados_unicos)
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'resultados': []
        }, status=400)


@require_http_methods(["GET"])
def obtener_ingredientes_seleccionados(request):
    """
    Obtiene los ingredientes seleccionados de la sesión
    GET /api/ingredientes-seleccionados/
    """
    ingredientes = request.session.get('ingredientes_detallados', [])
    return JsonResponse({
        'ingredientes': ingredientes,
        'total': len(ingredientes)
    })


@require_http_methods(["POST"])
def agregar_ingrediente_detallado(request):
    """
    Agrega un ingrediente con cantidad a la sesión
    POST /api/agregar-ingrediente/
    
    Body JSON:
    {
        "nombre": "cebolla",
        "cantidad": 2,
        "unidad": "unidades"
    }
    """
    try:
        datos = json.loads(request.body)
        nombre = datos.get('nombre', '').strip()
        cantidad = int(datos.get('cantidad', 1))
        unidad = datos.get('unidad', 'unidades').strip()
        
        if not nombre or cantidad < 1:
            return JsonResponse({
                'success': False,
                'error': 'Datos inválidos'
            }, status=400)
        
        # Obtener ingredientes de sesión
        if 'ingredientes_detallados' not in request.session:
            request.session['ingredientes_detallados'] = []
        
        ingredientes = request.session['ingredientes_detallados']
        
        # Verificar si ya existe (para actualizar)
        existe = False
        for ing in ingredientes:
            if ing['nombre'].lower() == nombre.lower():
                ing['cantidad'] = cantidad
                ing['unidad'] = unidad
                existe = True
                break
        
        # Si no existe, agregarlo
        if not existe:
            ingredientes.append({
                'nombre': nombre,
                'cantidad': cantidad,
                'unidad': unidad
            })
        
        request.session['ingredientes_detallados'] = ingredientes
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': f'{nombre} agregado',
            'ingredientes': ingredientes
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["POST"])
def eliminar_ingrediente(request):
    """
    Elimina un ingrediente de la sesión
    POST /api/eliminar-ingrediente/
    
    Body JSON:
    {
        "nombre": "cebolla"
    }
    """
    try:
        datos = json.loads(request.body)
        nombre = datos.get('nombre', '').strip()
        
        if 'ingredientes_detallados' not in request.session:
            request.session['ingredientes_detallados'] = []
        
        # Filtrar el ingrediente
        ingredientes = [
            ing for ing in request.session['ingredientes_detallados']
            if ing['nombre'].lower() != nombre.lower()
        ]
        
        request.session['ingredientes_detallados'] = ingredientes
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': f'{nombre} eliminado',
            'ingredientes': ingredientes
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["POST"])
def limpiar_ingredientes_detallados(request):
    """
    Limpia todos los ingredientes seleccionados
    POST /api/limpiar-ingredientes/
    """
    try:
        request.session['ingredientes_detallados'] = []
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Ingredientes limpiados'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
