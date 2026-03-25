# 🤖 Configuración de Gemini API para Generador de Recetas

## Paso 1: Obtener tu API Key de Google Gemini

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **"Create API key"**
4. Selecciona o crea un proyecto
5. Copia tu API key (te verá algo como: `AIzaSyD...`)

## Paso 2: Configurar la API Key en tu Proyecto

### Opción A: Variables de Entorno (RECOMENDADO)

**En Windows PowerShell:**
```powershell
# Establece la variable de entorno
$env:GEMINI_API_KEY = "tu_api_key_aqui"

# Verifica que se guardó
$env:GEMINI_API_KEY
```

**Para que sea permanente, edita tu perfil PowerShell:**
```powershell
# Abre tu perfil
notepad $PROFILE

# Añade esta línea:
$env:GEMINI_API_KEY = "tu_api_key_aqui"
```

### Opción B: Archivo .env (Para Desarrollo Local)

1. Crea un archivo `.env` en la raíz del proyecto:
```
GEMINI_API_KEY=tu_api_key_aqui
```

2. Instala python-dotenv:
```bash
pip install python-dotenv
```

3. En `dani/settings.py`, añade al inicio:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Paso 3: Verificar que Todo Funciona

Corre este comando en tu terminal:
```python
python manage.py shell
```

Luego ejecuta:
```python
from django.conf import settings
print(settings.GEMINI_API_KEY)
```

Deberías ver tu API key impresa (sin errores).

## Paso 4: Usar la Funcionalidad

1. Ve a la página de productos
2. Selecciona los ingredientes que quieras
3. Haz clic en **"Generar Receta con IA"**
4. La IA generará recetas personalizadas basadas en tus ingredientes

## 🚀 Características

- ✅ Generar recetas con Gemini AI
- ✅ Múltiples variaciones de recetas
- ✅ Guardar recetas generadas en la base de datos
- ✅ Información completa: pasos, tiempo, dificultad, tipo de receta

## ⚠️ Notas Importantes

- **Gratis**: Google ofrece una cuota gratuita generosa (60 solicitudes por minuto)
- **Límites**: Si excedes los límites, actualiza a un plan de pago en Google Cloud
- **Privacidad**: No guardes tu API key en repositorios públicos
- **Seguridad**: Usa variables de entorno en producción

## 📝 Limitaciones

- Requiere conexión a internet
- Velocidad depende de tu conexión y servidores de Google
- Asegúrate de tener la API habilitada en Google Cloud Console

## 🔧 Troubleshooting

### Error: "API key not found"
- Verifica que `GEMINI_API_KEY` esté configurada correctamente
- Reinicia tu terminal después de establecer la variable

### Error: "Invalid API key"
- Verifica que copiaste la key correctamente
- Confirma que la key está activa en Google Cloud Console

### Error: "Quota exceeded"
- Espera antes de hacer otra solicitud
- Considera actualizar tu plan en Google Cloud

---

¿Necesitas ayuda? Consulta la documentación oficial:
https://ai.google.dev/tutorials/python_quickstart
