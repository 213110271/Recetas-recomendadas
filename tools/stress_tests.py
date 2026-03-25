import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8090"

def get_csrf(session):
    for path in ["/productos/", "/"]:
        r = session.get(f"{BASE_URL}{path}", timeout=10)
        if "csrftoken" in session.cookies:
            return session.cookies.get("csrftoken")
    return None

def run_flow():
    s = requests.Session()
    csrf = get_csrf(s)
    headers = {}
    if csrf:
        headers["X-CSRFToken"] = csrf

    metrics = {}

    t0 = time.perf_counter()
    r1 = s.get(f"{BASE_URL}/api/buscar-ingredientes/", params={"q": "tomate"}, timeout=10)
    t1 = time.perf_counter()
    metrics["buscar_ingredientes_ms"] = (t1 - t0) * 1000
    assert r1.status_code == 200

    t2 = time.perf_counter()
    r2 = s.post(f"{BASE_URL}/api/agregar-ingrediente/", json={
        "nombre": "Tomate",
        "cantidad": 1,
        "unidad": "unidades"
    }, headers=headers, timeout=10)
    t3 = time.perf_counter()
    metrics["agregar_ingrediente_ms"] = (t3 - t2) * 1000
    assert r2.status_code == 200

    t4 = time.perf_counter()
    r3 = s.get(f"{BASE_URL}/api/ingredientes-seleccionados/", timeout=10)
    t5 = time.perf_counter()
    metrics["ingredientes_seleccionados_ms"] = (t5 - t4) * 1000
    assert r3.status_code == 200

    t6 = time.perf_counter()
    r4 = s.get(f"{BASE_URL}/generar-receta-ia/", timeout=30)
    t7 = time.perf_counter()
    metrics["generar_receta_ia_ms"] = (t7 - t6) * 1000
    assert r4.status_code == 200

    t8 = time.perf_counter()
    r5 = s.post(f"{BASE_URL}/api/limpiar-ingredientes/", headers=headers, timeout=10)
    t9 = time.perf_counter()
    metrics["limpiar_ingredientes_ms"] = (t9 - t8) * 1000
    assert r5.status_code == 200

    return metrics

def run_flow_multi():
    s = requests.Session()
    csrf = get_csrf(s)
    headers = {}
    if csrf:
        headers["X-CSRFToken"] = csrf

    metrics = {}

    s.get(f"{BASE_URL}/api/buscar-ingredientes/", params={"q": "ajo"}, timeout=10)
    s.post(f"{BASE_URL}/api/agregar-ingrediente/", json={
        "nombre": "Ajo",
        "cantidad": 1,
        "unidad": "unidades"
    }, headers=headers, timeout=10)
    s.post(f"{BASE_URL}/api/agregar-ingrediente/", json={
        "nombre": "Cebolla",
        "cantidad": 1,
        "unidad": "unidades"
    }, headers=headers, timeout=10)

    t0 = time.perf_counter()
    r = s.get(f"{BASE_URL}/generar-multiples-ia/", timeout=30)
    t1 = time.perf_counter()
    metrics["generar_multiples_ia_ms"] = (t1 - t0) * 1000
    assert r.status_code == 200

    s.post(f"{BASE_URL}/api/limpiar-ingredientes/", headers=headers, timeout=10)
    return metrics

def percentile(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    k = max(0, min(len(values)-1, int(round(p/100.0*(len(values)-1)))))
    return values[k]

def summarize(name, samples):
    vals = [m[name] for m in samples]
    return {
        "count": len(vals),
        "avg_ms": statistics.mean(vals) if vals else 0.0,
        "p50_ms": percentile(vals, 50),
        "p90_ms": percentile(vals, 90),
        "p95_ms": percentile(vals, 95),
        "max_ms": max(vals) if vals else 0.0
    }

def run_sequential(n=10):
    samples = []
    for _ in range(n):
        samples.append(run_flow())
    return samples

def run_concurrent(n=20, workers=10):
    samples = []
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(run_flow) for _ in range(n)]
        for fut in as_completed(futures):
            samples.append(fut.result())
    duration = time.perf_counter() - start
    throughput = n / duration if duration > 0 else 0.0
    return samples, duration, throughput

def main():
    print("== Warmup ==")
    _ = run_flow()

    print("\n== Prueba secuencial (10 flujos) ==")
    seq = run_sequential(10)
    for key in ["buscar_ingredientes_ms","agregar_ingrediente_ms","ingredientes_seleccionados_ms","generar_receta_ia_ms","limpiar_ingredientes_ms"]:
        s = summarize(key, seq)
        print(f"{key}: avg={s['avg_ms']:.1f}ms p90={s['p90_ms']:.1f}ms p95={s['p95_ms']:.1f}ms max={s['max_ms']:.1f}ms")

    print("\n== Prueba concurrente (20 flujos, 10 hilos) ==")
    conc, dur, thr = run_concurrent(20, 10)
    print(f"Duración total: {dur:.2f}s  |  Throughput: {thr:.2f} flujos/s")
    s = summarize("generar_receta_ia_ms", conc)
    print(f"generar_receta_ia_ms: avg={s['avg_ms']:.1f}ms p90={s['p90_ms']:.1f}ms p95={s['p95_ms']:.1f}ms max={s['max_ms']:.1f}ms")

    print("\n== Prueba integración múltiple (5 flujos) ==")
    samples = [run_flow_multi() for _ in range(5)]
    s2 = summarize("generar_multiples_ia_ms", samples)
    print(f"generar_multiples_ia_ms: avg={s2['avg_ms']:.1f}ms p90={s2['p90_ms']:.1f}ms p95={s2['p95_ms']:.1f}ms max={s2['max_ms']:.1f}ms")

if __name__ == "__main__":
    main()
