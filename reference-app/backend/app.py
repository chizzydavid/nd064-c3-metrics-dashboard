from flask import Response, Flask, render_template, request, jsonify, abort
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Summary, Counter, Histogram, Gauge
import time
import pymongo
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "example-mongodb"
app.config[
    "MONGO_URI"
] = "mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb"

mongo = PyMongo(app)

_INF = float("inf")

graphs = {}
graphs['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
graphs['4x'] = Counter('python_request_operations_err_4xx_total', 'The total number of requests returning a 4xx error')
graphs['5x'] = Counter('python_request_operations_err_5xx_total', 'The total number of requests returning a 5xx error')
graphs['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds.', buckets=(1, 2, 5, 6, 10, _INF))


@app.route("/")
def homepage():
    start = time.time()
    graphs['c'].inc()
    
    time.sleep(0.200)
    end = time.time()
    graphs['h'].observe(end - start) 
    return "Hello World"


@app.route("/api")
def my_api():
    start = time.time()
    graphs['c'].inc()
    
    time.sleep(0.300)
    end = time.time()
    graphs['h'].observe(end - start)
    return jsonify(repsonse="Api route")


@app.route("/not-found")
def not_found():
    graphs['c'].inc()
    graphs['4x'].inc()
    abort(404, description="Resource not found")


@app.route("/metrics")
def requests_count():
    res = []
    for k,v in graphs.items():
        res.append(prometheus_client.generate_latest(v))
    return Response(res, mimetype="text/plain")    


@app.route("/star", methods=["POST"])
def add_star():
    graphs['c'].inc()
    graphs['5x'].inc()
    star = mongo.db.stars
    name = request.json["name"]
    distance = request.json["distance"]
    star_id = star.insert({"name": name, "distance": distance})
    new_star = star.find_one({"_id": star_id})
    output = {"name": new_star["name"], "distance": new_star["distance"]}
    return jsonify({"result": output})



if __name__ == "__main__":
    app.run()

