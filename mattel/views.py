from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Producto, Receta
from .forms import ContactoForm
from django.contrib import messages
import random
import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

# 🔐 IMPORTAR AMBOS MÓDULOS DE SEGURIDAD
from .security import (
    PasswordValidator, 
    RateLimiter, 
    AuditLog,
    rate_limit_login,
    secure_password_required
)
from .advanced_security import (
    InputValidator,
    SessionSecurityManager,
    AnomalyDetector,
    require_advanced_security
)

load_dotenv()

# Obtener API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != 'TU_API_KEY_AQUI':
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configurando Gemini: {e}")

def generate_recipe_name(ingredients):
    base = ingredients[:2]
    nombre_base = " ".join(base)
    opciones = [
        f"{nombre_base} al Estilo Gourmet",
        f"Delicia de {nombre_base}",
        f"{nombre_base} en Fusión Creativa",
        f"{nombre_base} Artesanal",
        f"Selección Suprema de {nombre_base}",
        f"{nombre_base} a la Cocina Moderna"
    ]
    return random.choice(opciones)


def generar_receta_profesional(ingredientes):
    if not ingredientes:
        return None

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        ingredientes_txt = ", ".join(ingredientes)
        
        prompt = f"""
        Actúa como un chef experto y genera una receta única y detallada usando estos ingredientes: {ingredientes_txt}.
        Puedes agregar otros ingredientes básicos (sal, aceite, especias) si es necesario.
        
        Devuelve la respuesta en el siguiente formato exacto (sin markdown, solo texto plano):
        Titulo: [Nombre creativo de la receta]
        Descripcion: [Breve descripción apetitosa]
        Pasos:
        1. [Paso 1]
        2. [Paso 2]
        ...
        """

        response = model.generate_content(prompt)
        text = response.text
        
        # Parsear la respuesta
        lines = text.split('\n')
        titulo = "Receta Sorpresa"
        descripcion = "Una deliciosa preparación."
        pasos = []
        
        mode = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith("titulo:"):
                titulo = line.split(":", 1)[1].strip()
            elif line.lower().startswith("descripcion:"):
                descripcion = line.split(":", 1)[1].strip()
            elif line.lower().startswith("pasos:"):
                mode = "pasos"
            elif mode == "pasos" and (line[0].isdigit() or line.startswith("-")):
                # Limpiar el número o guión inicial
                cleaned_step = line.lstrip("0123456789.- ")
                pasos.append(cleaned_step)

        if not pasos:
            # Fallback si el parseo falla
            return {
                "nombre": titulo,
                "descripcion": descripcion,
                "pasos": [text]
            }

        return {
            "nombre": titulo,
            "descripcion": descripcion,
            "pasos": pasos
        }

    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            print("⚠️ Cuota de Gemini agotada, usando generador local")
        else:
            print(f"⚠️ Aviso: Usando generador local de recetas")
        # Fallback a la lógica anterior si falla la API
        ingredientes_random = random.sample(ingredientes, min(len(ingredientes), 4))
        ingredientes_txt = ", ".join(ingredientes_random)
        principales = ingredientes_random[:3]
        principales_txt = ", ".join(principales)
        titulo = generate_recipe_name(ingredientes_random)
        
        variaciones = [
            [
                f"Lava cuidadosamente los ingredientes: {ingredientes_txt}.",
                f"Corta {principales_txt} en trozos medianos.",
                f"Saltea {principales_txt} a fuego alto para activar aromas.",
                "Añade los ingredientes restantes y cocina a fuego medio.",
                "Rectifica sazón con hierbas secas.",
                "Cocina hasta obtener una consistencia suave.",
                "Sirve caliente."
            ],
            # ... (mantener otras variaciones si se desea, o simplificar el fallback)
        ]
        pasos = variaciones[0] # Simplificado para el fallback

        return {
            "nombre": titulo,
            "descripcion": f"Preparación profesional basada en {principales_txt} (Modo Offline).",
            "pasos": pasos
        }


def generar_pasos_receta_bd(receta):
    ingredientes = [i.nombre for i in receta.ingredientes.all()]
    if not ingredientes:
        return [
            "No hay ingredientes suficientes para generar pasos."
        ]

    principales = ingredientes[:3]
    ing_txt = ", ".join(ingredientes)
    princ_txt = ", ".join(principales)

    return [
        f"Lava y prepara los ingredientes seleccionados: {ing_txt}.",
        f"Pica los ingredientes principales ({princ_txt}) en trozos similares.",
        f"Calienta una sartén y saltea {princ_txt} hasta dorar ligeramente.",
        "Agrega el resto de ingredientes y mezcla suavemente.",
        "Añade sal, pimienta y especias al gusto.",
        "Cocina a fuego medio por 10–15 minutos.",
        "Sirve caliente y disfruta de esta preparación casera."
    ]


def inicio(request):
    return render(request, 'mattel/inicio.html')


def productos(request):
    if request.GET.get("reset") == "1":
        request.session.pop("ingredientes_seleccionados", None)
        request.session.pop("ingredientes_detallados", None)

    from django.db.models import Q
    import random
    
    # Obtener productos recomendados (aleatorios, máximo 20)
    todos_productos = list(Producto.objects.all())
    productos_recomendados = random.sample(todos_productos, min(20, len(todos_productos))) if todos_productos else []

    categorias = ["vegetales", "frutas", "carnes", "legumbres", "cereales", "condimentos", "especias"]

    cat = request.GET.get("cat")

    if cat in categorias:
        productos_lista = Producto.objects.filter(categoria=cat)
        titulo = f"Productos de {cat.capitalize()}"
    else:
        productos_lista = productos_recomendados
        titulo = "Catálogo de Productos"

    return render(request, 'mattel/productos.html', {
        'productos': productos_lista,
        'titulo': titulo,
        'categorias': categorias,
        'ingredientes_seleccionados': request.session.get("ingredientes_seleccionados", [])
    })

def buscar_ingredientes(request):
    """
    Redirige a la página de productos donde está integrada la búsqueda
    """
    return redirect('productos')
def distribuidor(request):
    return render(request, 'mattel/distribuidor.html')


def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensaje enviado correctamente.')
            return redirect('contacto')
        else:
            messages.error(request, 'Ocurrió un error.')
    else:
        form = ContactoForm()
    return render(request, 'mattel/contacto.html', {'form': form})


def catalogo_categoria(request, categoria):
    if request.GET.get("reset") == "1":
        if "ingredientes_seleccionados" in request.session:
            del request.session["ingredientes_seleccionados"]

    productos = Producto.objects.filter(categoria=categoria)
    return render(request, "mattel/catalogo.html", {
        "productos": productos,
        "categoria": categoria,
        'ingredientes_seleccionados': request.session.get("ingredientes_seleccionados", [])
    })


def seleccionar_ingredientes(request):
    if request.method == "POST":
        seleccionados = request.POST.getlist("ingredientes")
        if "ingredientes_seleccionados" not in request.session:
            request.session["ingredientes_seleccionados"] = []

        actuales = set(request.session["ingredientes_seleccionados"])
        actuales.update(seleccionados)

        request.session["ingredientes_seleccionados"] = list(actuales)
        return redirect(request.META.get("HTTP_REFERER", "catalogo_categoria"))

    categorias = ["carnes", "verduras", "lácteos", "frutas", "granos"]
    return render(request, "mattel/productos.html", {
        "categorias": categorias,
        'ingredientes_seleccionados': request.session.get("ingredientes_seleccionados", [])
    })


def ver_recetas(request):
    ingredientes = request.session.get("ingredientes_seleccionados", [])

    # Recetas reales filtradas
    if ingredientes:
        recetas_filtradas = Receta.objects.filter(
            ingredientes__nombre__in=ingredientes
        ).distinct()
    else:
        recetas_filtradas = Receta.objects.none()

    recetas_lista = list(recetas_filtradas)
    random.shuffle(recetas_lista)

    sugeridas = recetas_lista[:3]
    restantes = recetas_lista[3:]

    # 🔥 Generar SIEMPRE 3 recetas dinámicas únicas
    recetas_generadas = []
    if ingredientes:
        for _ in range(3):
            recetas_generadas.append(generar_receta_profesional(ingredientes))

    return render(request, "mattel/recetas_recomendadas.html", {
        "ingredientes": ingredientes,
        "sugeridas": sugeridas,
        "recetas": restantes,
        "recetas_generadas": recetas_generadas
    })


def receta_detalle(request, index):
    ingredientes = request.session.get("ingredientes_seleccionados", [])
    receta = generar_receta_profesional(ingredientes)

    return render(request, "mattel/recetas.html", {
        "ingredientes": ingredientes,
        "receta": receta
    })


def guardar_receta(request):
    if request.method == "POST":
        ingredientes = request.session.get("ingredientes_seleccionados", [])

        if ingredientes:
            receta = Receta.objects.create(nombre="Receta Generada")
            for ing in ingredientes:
                try:
                    p = Producto.objects.get(nombre=ing)
                    receta.ingredientes.add(p)
                except Producto.DoesNotExist:
                    pass

        request.session["ingredientes_seleccionados"] = []
        return redirect("ver_recetas")

    return redirect("inicio")


def recetas_recomendadas(request):
    ingredientes = request.GET.getlist("ingredientes")

    if ingredientes:
        recetas_filtradas = Receta.objects.filter(
            ingredientes__nombre__in=ingredientes
        ).distinct()
    else:
        recetas_filtradas = Receta.objects.all()

    sugeridas = recetas_filtradas[:3]
    recetas = recetas_filtradas.exclude(id__in=[r.id for r in sugeridas])

    recetas_generadas = []
    if ingredientes:
        for _ in range(3):
            recetas_generadas.append(generar_receta_profesional(ingredientes))

    return render(request, "mattel/recetas_recomendadas.html", {
        "sugeridas": sugeridas,
        "recetas": recetas,
        "ingredientes": ingredientes,
        "recetas_generadas": recetas_generadas
    })


def receta_completa(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id)

    receta.pasos_lista = generar_pasos_receta_bd(receta)

    return render(request, "mattel/receta_completa.html", {"receta": receta})


def limpiar_ingredientes(request):
    if 'ingredientes_seleccionados' in request.session:
        request.session['ingredientes_seleccionados'] = []
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ⭐ NUEVAS VISTAS CON GEMINI IA ⭐

def generar_receta_gemini(request):
    """
    Genera recetas usando Gemini API basadas en productos seleccionados.
    """
    from .ai_service import generar_receta_con_gemini
    
    # Intentar primero con ingredientes detallados (con cantidad)
    ingredientes = request.session.get("ingredientes_detallados", [])
    
    # Si no hay, usar los ingredientes simples
    if not ingredientes:
        ingredientes = request.session.get("ingredientes_seleccionados", [])
    
    print(f"🔍 DEBUG generar_receta_gemini:")
    print(f"   - ingredientes_detallados: {request.session.get('ingredientes_detallados', [])}")
    print(f"   - ingredientes_seleccionados: {request.session.get('ingredientes_seleccionados', [])}")
    print(f"   - ingredientes finales: {ingredientes}")
    
    if not ingredientes:
        print("❌ Sin ingredientes seleccionados")
        messages.warning(request, "Por favor selecciona ingredientes primero.")
        return redirect("productos")
    
    print(f"✅ Iniciando generación con {len(ingredientes)} ingredientes")
    
    # Generar receta con Gemini (ahora con fallback integrado)
    try:
        receta_ia = generar_receta_con_gemini(ingredientes)
        
        if not receta_ia:
            print("❌ generar_receta_con_gemini retornó None")
            messages.error(request, "No se pudo generar la receta. Intenta de nuevo.")
            return redirect("productos")
        
        # Ver si es una receta offline o en línea
        es_offline = receta_ia.get('_offline', False)
        if es_offline:
            print(f"⚠️ Receta generada en modo OFFLINE (cuota agotada o error)")
            messages.info(request, "Receta generada en modo offline (cuota de IA agotada)")
        else:
            print(f"✅ Receta generada exitosamente: {receta_ia.get('nombre', 'Sin nombre')}")
        
        return render(request, "mattel/receta_gemini.html", {
            "receta": receta_ia,
            "ingredientes": ingredientes
        })
    except Exception as e:
        print(f"❌ Exception ({type(e).__name__}): {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"Error inesperado: {str(e)}")
        return redirect("productos")


def generar_multiples_recetas_ia(request):
    """
    Genera múltiples recetas (3-5) usando Gemini API.
    """
    from .ai_service import generar_multiples_recetas_gemini
    
    # Intentar primero con ingredientes detallados (con cantidad)
    ingredientes = request.session.get("ingredientes_detallados", [])
    
    # Si no hay, usar los ingredientes simples
    if not ingredientes:
        ingredientes = request.session.get("ingredientes_seleccionados", [])
    
    if not ingredientes:
        messages.warning(request, "Por favor selecciona ingredientes primero.")
        return redirect("productos")
    
    # Generar múltiples recetas
    try:
        recetas_ia = generar_multiples_recetas_gemini(ingredientes, cantidad=3)
        
        if not recetas_ia:
            messages.error(request, "No se pudieron generar las recetas. Intenta de nuevo.")
            return redirect("productos")
        
        return render(request, "mattel/recetas_multiples_gemini.html", {
            "recetas": recetas_ia,
            "ingredientes": ingredientes
        })
    except ValueError as e:
        messages.error(request, f"Error generando recetas: {str(e)}")
        return redirect("productos")
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        return redirect("productos")


def guardar_receta_gemini(request):
    """
    Guarda una receta generada por Gemini en la base de datos.
    """
    if request.method == "POST":
        import json
        from django.http import JsonResponse
        
        try:
            datos = json.loads(request.body)
            nombre = datos.get("nombre", "Receta Generada por IA")
            descripcion = datos.get("descripcion", "")
            pasos_lista = datos.get("pasos", [])
            tiempo = datos.get("tiempo", "30 minutos")
            dificultad = datos.get("dificultad", "Fácil")
            tipo = datos.get("tipo", "ensalada")
            ingredientes = datos.get("ingredientes", [])
            
            # Convertir pasos a string
            if isinstance(pasos_lista, list):
                pasos_str = "\n".join([f"{i+1}. {paso}" for i, paso in enumerate(pasos_lista)])
            else:
                pasos_str = str(pasos_lista)
            
            # Crear la receta
            receta = Receta.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                pasos=pasos_str,
                tiempo=tiempo,
                dificultad=dificultad,
                tipo=tipo
            )
            
            # Agregar ingredientes
            if isinstance(ingredientes, list):
                for ing_nombre in ingredientes:
                    try:
                        producto = Producto.objects.get(nombre__iexact=ing_nombre)
                        receta.ingredientes.add(producto)
                    except Producto.DoesNotExist:
                        pass
            
            return JsonResponse({
                "success": True,
                "message": "Receta guardada exitosamente",
                "redirect": f"/receta/{receta.id}/"
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "Error al parsear datos JSON"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": f"Error al guardar: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        "success": False,
        "message": "Método no permitido"
    }, status=405)


# 🔍 DEBUG VIEW
from django.http import JsonResponse

def debug_session(request):
    """
    Muestra el contenido de la sesión actual para debugging
    """
    return JsonResponse({
        "ingredientes_seleccionados": request.session.get("ingredientes_seleccionados", []),
        "ingredientes_detallados": request.session.get("ingredientes_detallados", []),
        "session_key": request.session.session_key,
        "all_session_keys": list(request.session.keys())
    }, safe=False)

# 🔐 AUTENTICACIÓN Y GUARDADO DE RECETAS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import RecetaGuardada
import json

@require_http_methods(["GET", "POST"])
@require_advanced_security(endpoint_type='register')
def registrarse(request):
    """Registro de nuevos usuarios con validación AVANZADA de seguridad"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # 🔍 VALIDACIÓN EXHAUSTIVA DE INPUTS
        is_valid_username, username_msg = InputValidator.validate_username(username)
        if not is_valid_username:
            messages.error(request, username_msg)
            return redirect('registrarse')
        
        is_valid_email, email_msg = InputValidator.validate_email(email)
        if not is_valid_email:
            messages.error(request, email_msg)
            return redirect('registrarse')
        
        # Validaciones básicas
        if not username or not email or not password:
            messages.error(request, "❌ Todos los campos son obligatorios")
            return redirect('registrarse')
        
        if password != password_confirm:
            messages.error(request, "❌ Las contraseñas no coinciden")
            return redirect('registrarse')
        
        # 🔐 VALIDAR CONTRASEÑA FUERTE
        is_valid, validation_message = PasswordValidator.validate(password)
        if not is_valid:
            messages.error(request, validation_message)
            return redirect('registrarse')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"❌ El usuario '{username}' ya existe")
            return redirect('registrarse')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, f"❌ El email '{email}' ya está registrado")
            return redirect('registrarse')
        
        # Crear usuario
        try:
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            # Hacer login automático
            login(request, usuario)
            
            # 🔐 CONFIGURAR SESIÓN SEGURA
            SessionSecurityManager.secure_session_settings(request)
            
            # 📋 REGISTRAR EN AUDITORÍA
            AuditLog.log_login_attempt(
                username=username,
                ip_address=RateLimiter.get_ip_address(request),
                success=True,
                reason="NUEVO_REGISTRO"
            )
            
            messages.success(request, f"✅ ¡Bienvenido {username}! Tu cuenta ha sido creada")
            return redirect('perfil')
        except Exception as e:
            messages.error(request, f"❌ Error al crear la cuenta: {str(e)}")
            return redirect('registrarse')
    
    return render(request, 'mattel/registrarse.html')


@require_http_methods(["GET", "POST"])
@require_advanced_security(endpoint_type='login')
def iniciar_sesion(request):
    """Login de usuarios con PROTECCIÓN AVANZADA"""
    # Limpiar mensajes anteriores para evitar acumulación
    from django.contrib.messages import get_messages
    storage = get_messages(request)
    storage.used = True
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        ip_address = RateLimiter.get_ip_address(request)
        
        # 🔍 VALIDACIÓN DE INPUTS CONTRA INYECCIÓN
        is_safe, injection_msg = InputValidator.check_injection_patterns(username, 'username')
        if not is_safe:
            AnomalyDetector.log_suspicious_event(username, ip_address, 'INJECTION_ATTEMPT', injection_msg)
            messages.error(request, "❌ Username contiene caracteres no permitidos")
            return redirect('iniciar_sesion')
        
        # 🛡️ VERIFICAR RATE LIMITING
        if RateLimiter.is_locked_out(request, username):
            AuditLog.log_login_attempt(
                username=username,
                ip_address=ip_address,
                success=False,
                reason="CUENTA_BLOQUEADA_POR_RATE_LIMITING"
            )
            messages.error(
                request, 
                f"❌ Demasiados intentos fallidos. Intenta de nuevo en {RateLimiter.LOCKOUT_TIME} minutos."
            )
            return redirect('iniciar_sesion')
        
        if not username or not password:
            messages.error(request, "❌ Usuario y contraseña requeridos")
            return redirect('iniciar_sesion')
        
        # 🔐 AUTENTICAR USUARIO
        usuario = authenticate(request, username=username, password=password)
        
        if usuario is not None:
            # ✅ LOGIN EXITOSO
            login(request, usuario)
            
            # 🔐 CONFIGURAR SESIÓN SEGURA
            SessionSecurityManager.secure_session_settings(request)
            
            # 📋 REGISTRAR EN AUDITORÍA
            AuditLog.log_login_attempt(
                username=username,
                ip_address=ip_address,
                success=True,
                reason="LOGIN_EXITOSO"
            )
            
            # 🔄 LIMPIAR INTENTOS FALLIDOS
            RateLimiter.reset_attempts(request, username)
            
            messages.success(request, f"✅ ¡Bienvenido {username}!")
            
            # Redirigir a página anterior o a inicio
            next_url = request.GET.get('next', 'inicio')
            return redirect(next_url)
        else:
            # ❌ LOGIN FALLIDO
            # 🛡️ REGISTRAR INTENTO FALLIDO
            attempts = RateLimiter.record_failed_attempt(request, username)
            remaining = RateLimiter.get_remaining_attempts(request, username)
            
            AuditLog.log_login_attempt(
                username=username,
                ip_address=ip_address,
                success=False,
                reason=f"CONTRASEÑA_INCORRECTA (Intento {attempts})"
            )
            
            if remaining > 0:
                messages.error(
                    request, 
                    f"❌ Usuario o contraseña incorrectos. Intentos restantes: {remaining}"
                )
            else:
                messages.error(
                    request, 
                    f"❌ Demasiados intentos fallidos. Intenta de nuevo en {RateLimiter.LOCKOUT_TIME} minutos."
                )
            
            return redirect('iniciar_sesion')
    
    return render(request, 'mattel/iniciar_sesion.html')


@login_required(login_url='iniciar_sesion')
def cerrar_sesion(request):
    """Logout - Mensaje de despedida en inicio"""
    username = request.user.username
    logout(request)
    # Agregar mensaje DESPUÉS del logout para que aparezca en la siguiente página
    messages.success(request, f"¡Hasta luego {username}! Vuelve pronto 👋")
    return redirect('inicio')


@login_required(login_url='iniciar_sesion')
@require_http_methods(["POST"])
def guardar_receta(request):
    """
    AJAX endpoint para guardar una receta al perfil del usuario.
    Espera JSON con: nombre, descripcion, pasos, tiempo, dificultad, tipo, ingredientes, origen
    """
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        campos_requeridos = ['nombre', 'descripcion', 'pasos', 'tipo']
        for campo in campos_requeridos:
            if not data.get(campo):
                return JsonResponse({
                    'success': False,
                    'error': f"Falta el campo requerido: {campo}"
                }, status=400)
        
        # Crear RecetaGuardada
        receta_guardada = RecetaGuardada.objects.create(
            usuario=request.user,
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            pasos=data.get('pasos'),
            tiempo=data.get('tiempo', '30 minutos'),
            dificultad=data.get('dificultad', 'Fácil'),
            tipo=data.get('tipo', 'ensalada'),
            ingredientes=json.dumps(data.get('ingredientes', [])),
            origen=data.get('origen', 'offline'),
            notas=data.get('notas', '')
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': f"✅ Receta '{receta_guardada.nombre}' guardada exitosamente",
            'receta_id': receta_guardada.id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': "Datos JSON inválidos"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"Error al guardar: {str(e)}"
        }, status=500)


@login_required(login_url='iniciar_sesion')
def mis_recetas(request):
    """
    Página con todas las recetas guardadas del usuario.
    Permite ver, editar y eliminar recetas.
    """
    recetas = RecetaGuardada.objects.filter(usuario=request.user)
    
    # Filtros opcionales
    origen_filter = request.GET.get('origen', '')
    tipo_filter = request.GET.get('tipo', '')
    
    if origen_filter:
        recetas = recetas.filter(origen=origen_filter)
    
    if tipo_filter:
        recetas = recetas.filter(tipo=tipo_filter)
    
    # Obtener stats
    stats = {
        'total': RecetaGuardada.objects.filter(usuario=request.user).count(),
        'ia': RecetaGuardada.objects.filter(usuario=request.user, origen='ia').count(),
        'offline': RecetaGuardada.objects.filter(usuario=request.user, origen='offline').count(),
        'favoritas': RecetaGuardada.objects.filter(usuario=request.user, favorita=True).count(),
    }
    
    context = {
        'recetas': recetas,
        'stats': stats,
        'origen_filter': origen_filter,
        'tipo_filter': tipo_filter,
    }
    
    return render(request, 'mattel/mis_recetas.html', context)


@login_required(login_url='iniciar_sesion')
@require_http_methods(["POST"])
def eliminar_receta(request, receta_id):
    """Eliminar una receta guardada"""
    receta = get_object_or_404(RecetaGuardada, id=receta_id, usuario=request.user)
    nombre = receta.nombre
    receta.delete()
    messages.success(request, f"Receta '{nombre}' eliminada")
    return redirect('mis_recetas')


@login_required(login_url='iniciar_sesion')
@require_http_methods(["POST"])
def marcar_favorita(request, receta_id):
    """Marcar/desmarcar receta como favorita"""
    receta = get_object_or_404(RecetaGuardada, id=receta_id, usuario=request.user)
    receta.favorita = not receta.favorita
    receta.save()
    
    return JsonResponse({
        'success': True,
        'favorita': receta.favorita,
        'mensaje': f"{'⭐ Agregada' if receta.favorita else '☆ Removida'} de favoritas"
    })


@login_required(login_url='iniciar_sesion')
def perfil_usuario(request):
    """Página de perfil del usuario"""
    recetas_totales = RecetaGuardada.objects.filter(usuario=request.user).count()
    recetas_ia = RecetaGuardada.objects.filter(usuario=request.user, origen='ia').count()
    recetas_offline = RecetaGuardada.objects.filter(usuario=request.user, origen='offline').count()
    favoritas = RecetaGuardada.objects.filter(usuario=request.user, favorita=True).count()
    
    context = {
        'recetas_totales': recetas_totales,
        'recetas_ia': recetas_ia,
        'recetas_offline': recetas_offline,
        'favoritas': favoritas,
    }
    
    return render(request, 'mattel/perfil.html', context)