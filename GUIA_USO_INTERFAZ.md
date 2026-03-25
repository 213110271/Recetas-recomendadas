# 📖 Guía de Uso - Nueva Interfaz Integrada

## 🎯 ¿Cómo Usar la Búsqueda de Ingredientes Integrada?

### Paso a Paso

#### 1️⃣ Accede a la Página de Productos
```
URL: http://localhost:8001/productos/
```

Verás:
- **Lado izquierdo**: Categorías de ingredientes (Vegetales, Frutas, etc.)
- **Lado derecho**: Panel de búsqueda con campo de entrada

#### 2️⃣ Busca un Ingrediente
```
1. Escribe en el campo "Buscar (cebolla, tomate...)"
2. Aparecerá un dropdown con sugerencias
3. Haz clic en el que desees
```

**Ejemplo:**
```
Escribes: "ceb"
↓
Aparece dropdown:
├─ Cebolla          (Vegetales)
├─ Cebolla Morada   (Vegetales)
└─ Cebolleta        (Vegetales)
↓
Haces clic en "Cebolla"
```

#### 3️⃣ Configura Cantidad y Unidad
```
Después de seleccionar:
├─ Cantidad: [campo numérico]
├─ Unidad: [dropdown con opciones]
└─ [✓ Agregar]
```

**Opciones de unidad:**
- `Un.` = Unidades
- `gr` = Gramos
- `kg` = Kilogramos
- `ml` = Mililitros
- `L` = Litros
- `cda` = Cucharas
- `taza` = Tazas

**Ejemplo completo:**
```
Ingrediente: Cebolla
Cantidad: 2
Unidad: Un. (Unidades)
↓
Haz clic [✓ Agregar]
```

#### 4️⃣ Verás el Ingrediente en "Seleccionados"
```
📋 Seleccionados
├─ Cebolla
│  2 un. [✕]
```

El botón `[✕]` te permite eliminarlo si te arrepientes.

#### 5️⃣ Agrega Más Ingredientes (Opcional)
Repite pasos 2-4 para cada ingrediente que desees.

**Resultado esperado:**
```
📋 Seleccionados
├─ Cebolla         2 un.     [✕]
├─ Tomate          500 gr    [✕]
├─ Ajo             10 gr     [✕]
├─ Aceite de oliva 3 cda     [✕]
```

#### 6️⃣ Genera tu Receta
```
Haz clic en: [🤖 Generar Receta]
```

El sistema:
1. ✅ Toma todos los ingredientes seleccionados
2. ✅ Los envía a Google Gemini IA
3. ✅ Genera una receta personalizada
4. ✅ Te muestra la receta completa

#### 7️⃣ (Opcional) Ver Recetas Sugeridas
```
Haz clic en: [👁️ Ver Recetas]
```

Muestra 3 variaciones de recetas sugeridas basadas en tus ingredientes.

#### 8️⃣ (Opcional) Limpiar Todo
```
Haz clic en: [🗑️ Limpiar]
```

Confirma y todos los ingredientes se eliminan. Empiezas de cero.

---

## 💡 Consejos y Trucos

### 🔍 Búsqueda Inteligente
```
Puedes buscar por:
✅ Nombre exacto: "tomate"
✅ Inicial: "to" → muestra tomate, tomillo, tomatillo
✅ Parte del nombre: "mat" → muestra tomate, tomatillo
❌ No es case-sensitive: "CEBOLLA" = "cebolla"
```

### 📱 En Móvil
```
En pantallas pequeñas (< 768px):
├─ El panel de búsqueda aparece ARRIBA
├─ Las categorías aparecen ABAJO
└─ Desplázate para acceder a todo
```

### 💾 Persistencia
```
Tus ingredientes se guardan mientras:
✅ Navegas en la página
✅ Actualizas la página (F5)
✅ Cambias entre vistas
❌ Cierras el navegador (se borra la sesión)
```

### ⚡ Atajos Rápidos
```
1. Usa Tab para navegar entre campos
2. Enter después de escribir = agregar automáticamente
3. Click en [✕] para eliminar rápidamente
```

---

## 🎓 Ejemplos Prácticos

### Ejemplo 1: Receta de Ensalada
```
1. Busca "Lechuga" → Agrega 1 un.
2. Busca "Tomate" → Agrega 500 gr
3. Busca "Cebolla" → Agrega 1 un.
4. Busca "Aceite de oliva" → Agrega 3 cda
5. Click [🤖 Generar Receta]

Resultado: Receta de ensalada personalizada ✨
```

### Ejemplo 2: Receta de Sopa
```
1. Busca "Caldo" → Agrega 1 L
2. Busca "Zanahoria" → Agrega 2 un.
3. Busca "Pollo" → Agrega 500 gr
4. Busca "Sal" → Agrega 1 cda
5. Click [🤖 Generar Receta]

Resultado: Sopa personalizada 🍲
```

### Ejemplo 3: Postres
```
1. Busca "Harina" → Agrega 200 gr
2. Busca "Azúcar" → Agrega 100 gr
3. Busca "Huevo" → Agrega 2 un.
4. Busca "Mantequilla" → Agrega 100 gr
5. Click [🤖 Generar Receta]

Resultado: Postre personalizado 🎂
```

---

## ⚙️ Técnico: Cómo Funciona Internamente

### Flujo de Datos
```
1. Usuario escribe en búsqueda
   ↓
2. JavaScript envía GET a /api/buscar-ingredientes/?q=query
   ↓
3. Django busca en BD: Producto.objects.filter(nombre__icontains=query)
   ↓
4. Retorna JSON con hasta 15 resultados
   ↓
5. JavaScript muestra dropdown autocomplete
   ↓
6. Usuario selecciona → muestra campos de cantidad
   ↓
7. Usuario agrega → POST a /api/agregar-ingrediente/
   ↓
8. Django guarda en sesión: request.session['ingredientes_detallados']
   ↓
9. JavaScript actualiza lista visible
```

### Estructura de Sesión
```python
request.session['ingredientes_detallados'] = [
    {
        'nombre': 'Cebolla',
        'cantidad': 2,
        'unidad': 'un.'
    },
    {
        'nombre': 'Tomate',
        'cantidad': 500,
        'unidad': 'gr'
    }
]
```

### API Endpoints Utilizados

| Acción | Endpoint | Método |
|--------|----------|--------|
| Búsqueda | `/api/buscar-ingredientes/?q=` | GET |
| Agregar | `/api/agregar-ingrediente/` | POST |
| Eliminar | `/api/eliminar-ingrediente/` | POST |
| Listar | `/api/ingredientes-seleccionados/` | GET |
| Limpiar | `/api/limpiar-ingredientes/` | POST |

---

## 🐛 Solución de Problemas

### Problema: No aparecen resultados en búsqueda
```
Solución:
1. Verifica que escribes ≥ 2 caracteres
2. Intenta con un nombre diferente
3. Abre F12 → Console → verifica errores
4. Asegúrate que los productos existen en BD
```

### Problema: No se agrega el ingrediente
```
Solución:
1. Verifica que apareció en los resultados
2. Revisa que la cantidad es ≥ 1
3. Abre DevTools → Network → verifica respuesta de API
4. Comprueba que CSRF token se envía (Django lo requiere)
```

### Problema: Se pierden los ingredientes
```
Solución:
1. Verifica que NO cerraste el navegador
2. Revisa que NOT hiciste clic en [🗑️ Limpiar]
3. Abre DevTools → Application → Cookies → verifica sesión
4. Intenta actualizar la página (F5)
```

### Problema: Los botones no funcionan
```
Solución:
1. Verifica que JavaScript está habilitado (generalmente sí)
2. Abre Console (F12) y busca errores en rojo
3. Intenta en otro navegador
4. Limpia cache del navegador (Ctrl+Shift+Del)
```

---

## ✨ Características Futuras (Roadmap)

Se está considerando agregar:

- 🌐 Búsqueda por internet (Google Custom Search)
- 📊 Mostrar sugerencias de cantidad basadas en recetas existentes
- ⭐ Guardar combinaciones favoritas de ingredientes
- 📈 Historial de búsquedas recientes
- 🔗 Compartir recetas por enlace
- 📸 Foto de ingredientes al buscar
- 🎯 Categorías sugeridas mientras escribes

---

## 📚 Documentación Relacionada

- [Guía de Instalación](README_GEMINI_IA.md)
- [API de Ingredientes](api_ingredientes.py)
- [Servicio de IA](mattel/ai_service.py)

---

## 🎉 ¡Listo para Cocinar!

Ya sabes cómo usar la interfaz. Ahora:
1. ✅ Accede a `/productos/`
2. ✅ Busca tus ingredientes favoritos
3. ✅ Genera recetas con IA
4. ✅ ¡Disfruta cocinando! 👨‍🍳

---

**¿Preguntas?** Consulta los documentos GEMINI_SETUP.md o README_GEMINI_IA.md
