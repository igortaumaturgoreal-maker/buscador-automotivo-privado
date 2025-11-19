# main.py
from flask import Flask, render_template, jsonify, request
from scraper import find_opportunities
import os

app = Flask(_name_)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan")
def scan():
    try:
        mm = request.args.get("min_margin") or os.getenv("MIN_MARGIN_BRL") or 12000
        mm = int(mm)
    except:
        mm = 12000
    results = find_opportunities(min_margin=mm)
    return jsonify({"status":"ok", "count": len(results), "results": results})

if _name_ == "_main_":
    app.run()
