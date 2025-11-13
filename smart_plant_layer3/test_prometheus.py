import time
import requests
from prometheus_client.parser import text_string_to_metric_families

def test_prometheus_metrics():
    time.sleep(3)  # attendre que Flask soit démarré
    API_URL = "http://localhost:5000/metrics"
    print("🔍 Test de l'endpoint Prometheus...")

    try:
        response = requests.get(API_URL)
    except Exception as e:
        print(f"❌ Impossible d’accéder à {API_URL}")
        print("Erreur :", e)
        return

    if response.status_code != 200:
        print(f"❌ L'API répond mais renvoie le code {response.status_code}")
        return

    print("✅ L’endpoint /metrics est accessible !\n")

    metrics_text = response.text
    metric_count = 0
    important_metrics_found = {
        "flask_http_request_total": False,
        "process_cpu_seconds_total": False,
        "python_gc_objects_collected_total": False
    }

    for family in text_string_to_metric_families(metrics_text):
        metric_count += 1
        name = family.name
        if name in important_metrics_found:
            important_metrics_found[name] = True
        if metric_count <= 5:
            print(f"➡️  {family.name} ({len(family.samples)} samples)")

    print("\n📈 Résultats des vérifications :")
    if metric_count > 0:
        print(f"✅ Total des métriques détectées : {metric_count}")
    else:
        print("❌ Aucune métrique détectée.")

    print("\n🧪 Vérification des métriques essentielles :")
    for metric, found in important_metrics_found.items():
        if found:
            print(f"   ✔️ {metric} détectée")
        else:
            print(f"   ❌ {metric} manquante")

if __name__ == "__main__":
    test_prometheus_metrics()
