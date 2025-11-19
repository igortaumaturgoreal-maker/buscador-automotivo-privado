from flask import Flask, render_template

app = Flask(_name_)   # ← CORRETO!

@app.route("/")
def home():
    return render_template("index.html")

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000)
