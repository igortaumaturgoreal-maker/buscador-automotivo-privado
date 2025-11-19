from scraper import buscar_ofertas
import json

def handler(request, response):
    try:
        min_margin = int(request.get("query", {}).get("min_margin", 12000))

        resultados = buscar_ofertas(min_margin=min_margin)

        response.status_code = 200
        response.headers["Content-Type"] = "application/json"
        response.body = json.dumps({
            "status": "ok",
            "count": len(resultados),
            "results": resultados
        })

    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({"status": "error", "message": str(e)})
