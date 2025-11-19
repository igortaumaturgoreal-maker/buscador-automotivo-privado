from flask import Flask, render_template, jsonify
from scraper import executar_busca

app = Flask(_name_)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan")
def scan():
    resultado = executar_busca()
    return jsonify(resultado)

if _name_ == "_main_":
    app.run()
