from django.urls import path
from . import views
from . import api_ingredientes
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos/', views.productos, name='productos'),
    path('distribuidor/', views.distribuidor, name='distribuidor'),
    path('contacto/', views.contacto, name='contacto'),

    # 🔥 NUEVAS RUTAS PARA TU SISTEMA DE INGREDIENTES
    path('categoria/<str:categoria>/', views.catalogo_categoria, name='catalogo_categoria'),
    path('seleccionar/', views.seleccionar_ingredientes, name='seleccionar_ingredientes'),

    # ⭐ RUTA QUE MUESTRA LAS 3 RECETAS SUGERIDAS
    path('recetas/', views.ver_recetas, name='recetas_con_ingredientes'),

    # ⭐ RUTA QUE MUESTRA UNA RECETA COMPLETA (la correcta)
    path('receta/<int:receta_id>/', views.receta_completa, name='receta_completa'),

    # ⚡ RUTA DE GUARDAR RECETA
    path('guardar-receta/', views.guardar_receta, name='guardar_receta'),
    path('limpiar/', views.limpiar_ingredientes, name='limpiar_ingredientes'),

    # ⭐ RUTAS PARA GEMINI IA
    path('generar-receta-ia/', views.generar_receta_gemini, name='generar_receta_gemini'),
    path('generar-multiples-ia/', views.generar_multiples_recetas_ia, name='generar_multiples_ia'),
    path('guardar-receta-ia/', views.guardar_receta_gemini, name='guardar_receta_gemini'),

    # 🔎 API PARA BUSCAR INGREDIENTES
    path('api/buscar-ingredientes/', api_ingredientes.buscar_ingredientes, name='buscar_ingredientes'),
    path('api/ingredientes-seleccionados/', api_ingredientes.obtener_ingredientes_seleccionados, name='obtener_ingredientes'),
    path('api/agregar-ingrediente/', api_ingredientes.agregar_ingrediente_detallado, name='agregar_ingrediente'),
    path('api/eliminar-ingrediente/', api_ingredientes.eliminar_ingrediente, name='eliminar_ingrediente'),
    path('api/limpiar-ingredientes/', api_ingredientes.limpiar_ingredientes_detallados, name='limpiar_ingredientes_api'),
    
    # � AUTENTICACIÓN Y RECETAS GUARDADAS
    path('registrarse/', views.registrarse, name='registrarse'),
    path('iniciar-sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('mis-recetas/', views.mis_recetas, name='mis_recetas'),
    path('api/guardar-receta/', views.guardar_receta, name='api_guardar_receta'),
    path('eliminar-receta/<int:receta_id>/', views.eliminar_receta, name='eliminar_receta'),
    path('marcar-favorita/<int:receta_id>/', views.marcar_favorita, name='marcar_favorita'),
    
    # �🔍 DEBUG
    path('debug/session/', views.debug_session, name='debug_session'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)