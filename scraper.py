import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

PORTAIS = {
    "OLX": "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={modelo}&sf=1",
    "Webmotors": "https://www.webmotors.com.br/carros/usados/{modelo}",
}

MARCAS = [
    "honda",
    "toyota",
    "fiat strada cabine simples",
    "hyundai creta",
    "hb20"
]


def buscar_fipe(modelo):
    url = f"https://veiculos.fipe.org.br/api/veiculos/ConsultarValorComTodosParametros"
    # A FIPE tem proteção, então pegamos rede alternativa:
    try:
        url2 = f"https://parallelum.com.br/fipe/api/v2/cars/brands"
        marcas = requests.get(url2, timeout=10).json()
    except:
        return None

    return None  # Mantemos genérico até definir modelo exato (ficará na versão 2)

def buscar_portais():
    resultados = []

    for modelo in MARCAS:
        for nome, url in PORTAIS.items():
            link = url.format(modelo=modelo.replace(" ", "-"))
            print(f"📡 Buscando: {modelo.upper()} em {nome}")

            try:
                r = requests.get(link, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(r.text, "lxml")

                # Extrair títulos e preços (LÓGICA SIMPLIFICADA)
                titulos = [x.text.strip() for x in soup.find_all("h2")][:10]
                precos = [x.text.strip() for x in soup.find_all("p") if "R$" in x.text][:10]

                for t, p in zip(titulos, precos):
                    resultados.append({
                        "portal": nome,
                        "modelo": modelo,
                        "titulo": t,
                        "preco": p,
                        "url": link,
                        "hora": datetime.now().strftime("%H:%M:%S")
                    })

            except Exception as e:
                print(f"Erro ao buscar {modelo}: {e}")

    return pd.DataFrame(resultados)
{
  "version": 2,
  "builds": [
    { "src": "main.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "main.py" }
  ]
}
