from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("main.html")


@app.route("/api")
def home():
    res = requests.get("http://backend-service.default.svc.cluster.local:8081/")
    return res.text

@app.route("/api/trace")
def trace():
    res = requests.get("http://trial-service.default.svc.cluster.local:8082/trace")
    return jsonify(res.json())


if __name__ == "__main__":
    app.run()
