from flask import Flask, render_template

app = Flask(_name_)

@app.route("/")
from scraper import executar_busca

@app.route("/scan")
def scan():
    return executar_busca()
def home():
    return render_template("index.html")

if _name_ == "_main_":
    app.run()
