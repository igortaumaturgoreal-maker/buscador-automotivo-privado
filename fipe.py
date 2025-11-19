# fipe.py
import requests
import re

BASE = "https://parallelum.com.br/fipe/api/v1"

def _parse_valor(valor_str):
    if not valor_str:
        return None
    s = re.sub(r"[^\d,\.]", "", valor_str)
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return None

def get_fipe_value(brand, model, prefer_year=None):
    # fetch marcas
    try:
        marcas = requests.get(f"{BASE}/carros/marcas", timeout=10).json()
    except Exception:
        return None

    brand_code = None
    for m in marcas:
        nome = m.get("nome","").lower()
        if brand.lower() in nome or nome in brand.lower():
            brand_code = m["codigo"]
            break
    if not brand_code:
        return None

    # modelos
    try:
        modelos = requests.get(f"{BASE}/carros/marcas/{brand_code}/modelos", timeout=10).json().get("modelos", [])
    except Exception:
        return None

    model_code = None
    for mod in modelos:
        if model.lower() in mod.get("nome","").lower():
            model_code = mod["codigo"]
            break
    if not model_code and modelos:
        model_code = modelos[0]["codigo"]

    # anos
    try:
        anos = requests.get(f"{BASE}/carros/marcas/{brand_code}/modelos/{model_code}/anos", timeout=10).json()
    except Exception:
        return None

    ano_code = None
    if prefer_year:
        for a in anos:
            if str(prefer_year) in a.get("nome",""):
                ano_code = a.get("codigo"); break
    if not ano_code and anos:
        ano_code = anos[0].get("codigo")

    if not ano_code:
        return None

    try:
        data = requests.get(f"{BASE}/carros/marcas/{brand_code}/modelos/{model_code}/anos/{ano_code}", timeout=10).json()
        valor = data.get("Valor") or data.get("value")
        return _parse_valor(valor)
    except Exception:
        return None
