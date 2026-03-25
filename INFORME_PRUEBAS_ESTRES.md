# Informe de Pruebas de Estrés, Integración y Rendimiento

**Fecha:** 24/Mar/2026  
**Entorno:** Windows, Django dev server en http://127.0.0.1:8090/  
**Proyecto:** Generación de recetas con IA (Gemini) y gestión de ingredientes

## Metodología
- Pruebas ejecutadas con script de carga: [stress_tests.py](file:///c:/Users/rapi2/Pictures/web%20-%20copia/proyecto2/proyectoweb3/tools/stress_tests.py)
- Flujos medidos (incluyen CSRF y sesión):
  - Buscar ingredientes: GET /api/buscar-ingredientes/?q=tomate
  - Agregar ingrediente: POST /api/agregar-ingrediente/
  - Ver seleccionados: GET /api/ingredientes-seleccionados/
  - Generar receta IA: GET /generar-receta-ia/
  - Limpiar ingredientes: POST /api/limpiar-ingredientes/
- Escenarios:
  - Secuencial: 10 flujos completos
  - Concurrente: 20 flujos con 10 hilos
  - Integración múltiple: 5 flujos a /generar-multiples-ia/ tras agregar 2 ingredientes

## Resultados

### Secuencial (10 flujos)
- Buscar ingredientes: avg 1325.6 ms, p90 1545.2 ms, p95 1839.5 ms, max 1839.5 ms
- Agregar ingrediente: avg 78.2 ms, p90 48.2 ms, p95 381.1 ms, max 381.1 ms
- Ingredientes seleccionados: avg 4.0 ms, p90 4.2 ms, p95 4.4 ms, max 4.4 ms
- Generar receta IA: avg 800.9 ms, p90 1061.8 ms, p95 1090.4 ms, max 1090.4 ms
- Limpiar ingredientes: avg 45.2 ms, p90 49.3 ms, p95 49.4 ms, max 49.4 ms

### Concurrente (20 flujos, 10 hilos)
- Duración total: 4.78 s
- Throughput: 4.18 flujos/s
- Generar receta IA: avg 483.4 ms, p90 568.0 ms, p95 568.7 ms, max 579.6 ms

### Integración múltiple (5 flujos)
- Generar múltiples IA: avg 2168.6 ms, p90 2727.2 ms, p95 2727.2 ms, max 2727.2 ms

## Observaciones
- El mayor cuello de botella es la búsqueda online (Spoonacular): ~1.3–1.8 s por consulta.
- La generación de receta IA responde <1 s en promedio con el nuevo timeout + fallback.
- En carga concurrente moderada (10 hilos), el endpoint de generación mantiene latencia aceptable (~0.48–0.57 s) y ~4 flujos/s.
- La generación de múltiples recetas naturalmente es más costosa (~2.1–2.7 s), adecuada para uso bajo demanda.

## Recomendaciones
- Cachear resultados de /api/buscar-ingredientes/ por query (60–120 s) para reducir latencia y tráfico externo.
- Establecer timeout estricto de 3–5 s para Spoonacular y fallback inmediato a BD local si excede.
- Afinar el timeout de Gemini (actualmente 20 s) según tu experiencia real; si tu red es confiable, puedes bajarlo a 10–15 s.
- Activar gzip y keep-alive a nivel de servidor si migras a producción (ASGI/WSGI), y considerar un reverse proxy (Nginx).
- Registrar métricas de latencia en logs para monitoreo continuo (p50/p95) y detectar degradaciones.

## Anexos
- Código de pruebas: [tools/stress_tests.py](file:///c:/Users/rapi2/Pictures/web%20-%20copia/proyecto2/proyectoweb3/tools/stress_tests.py)
- Endpoints probados: [urls.py](file:///c:/Users/rapi2/Pictures/web%20-%20copia/proyecto2/proyectoweb3/mattel/urls.py)

