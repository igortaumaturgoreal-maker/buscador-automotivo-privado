# scraper.py
import requests
from bs4 import BeautifulSoup
import re
import time
from fipe import get_fipe_value
from datetime import datetime

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"}
MIN_MARGIN = 12000  # default, main will override from env if set
MODELS = [
    {"brand":"Honda","model":"HR-V"},
    {"brand":"Honda","model":"Fit"},
    {"brand":"Honda","model":"City"},
    {"brand":"Toyota","model":"Corolla"},
    {"brand":"Toyota","model":"Etios"},
    {"brand":"Fiat","model":"Strada"},
    {"brand":"Hyundai","model":"Creta"},
    {"brand":"Hyundai","model":"HB20"}
]

def _parse_price_text(txt):
    if not txt:
        return None
    m = re.search(r"R\$[\s\d\.\,]+", txt)
    if not m:
        # maybe just digits
        s = re.sub(r"[^\d,\.]", "", txt)
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except:
            return None
    s = m.group(0)
    s = s.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(s)
    except:
        return None

# --- OLX simple search (search page) ---
def search_olx(query, limit=12):
    q = query.replace(" ", "%20")
    url = f"https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={q}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
    except Exception:
        return []

    results = []
    # heuristics: OLX uses ad cards with anchor tags; we'll find anchors with href and price pattern nearby
    anchors = soup.find_all("a", href=True)
    seen = set()
    for a in anchors:
        href = a["href"]
        if href in seen:
            continue
        text = a.get_text(" ", strip=True)
        price = _parse_price_text(text)
        if price:
            full = href if href.startswith("http") else href
            # sometimes OLX links are full; add simple cleaning
            results.append({"title": text[:140], "price": price, "url": full, "source":"OLX"})
            seen.add(href)
        if len(results) >= limit:
            break
    return results

# --- Webmotors simple search ---
def search_webmotors(query, limit=12):
    q = query.replace(" ", "%20")
    url = f"https://www.webmotors.com.br/carros/estoque?tipoveiculo=carros&palavra-chave={q}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
    except Exception:
        return []

    results = []
    anchors = soup.find_all("a", href=True)
    seen = set()
    for a in anchors:
        text = a.get_text(" ", strip=True)
        price = _parse_price_text(text)
        href = a["href"]
        if price and href not in seen:
            full = href if href.startswith("http") else ("https://www.webmotors.com.br" + href)
            results.append({"title": text[:140], "price": price, "url": full, "source":"Webmotors"})
            seen.add(href)
        if len(results) >= limit:
            break
    return results

# --- Master: find opportunities
def find_opportunities(min_margin=MIN_MARGIN):
    out = []
    seen_urls = set()
    for m in MODELS:
        q = f"{m['brand']} {m['model']}"
        # search both portals
        candidates = []
        candidates += search_olx(q, limit=10)
        time.sleep(0.6)
        candidates += search_webmotors(q, limit=8)
        time.sleep(0.6)

        for c in candidates:
            url = c.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            price = c.get("price")
            if not price:
                continue
            # FIPE lookup - prefer_year not provided (uses latest available)
            fipe_val = get_fipe_value(m['brand'], m['model'])
            if not fipe_val:
                continue
            margin = fipe_val - price
            if margin >= min_margin:
                out.append({
                    "brand": m['brand'],
                    "model": m['model'],
                    "title": c.get("title"),
                    "price": price,
                    "fipe": fipe_val,
                    "margin": margin,
                    "url": url,
                    "source": c.get("source"),
                    "scraped_at": datetime.utcnow().isoformat() + "Z"
                })
        # small pause between models to avoid aggressive scraping
        time.sleep(0.8)
    return out

# convenience wrapper for Flask
def executar_busca(min_margin=None):
    try:
        mm = int(min_margin) if min_margin else MIN_MARGIN
    except:
        mm = MIN_MARGIN
    return {"status":"ok", "count": len(find_opportunities(mm)), "results": find_opportunities(mm)}
