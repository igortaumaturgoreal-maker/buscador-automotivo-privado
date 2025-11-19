from fastapi import FastAPI
import scraper

app = FastAPI()

@app.get("/")
def root():
    return {"status": "online", "mensagem": "Monitor de oportunidades ativo!"}

@app.get("/scan")
def scan():
    df = scraper.buscar_portais()
    return df.to_dict(orient="records")
