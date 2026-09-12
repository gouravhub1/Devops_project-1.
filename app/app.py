import os
import socket
import time
import psutil
from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
START_TIME = time.time()

REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests', 
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request Latency in seconds', 
    ['endpoint']
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if request.path != '/metrics':
        resp_time = time.time() - getattr(request, 'start_time', time.time())
        REQUEST_LATENCY.labels(endpoint=request.path).observe(resp_time)
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=request.path, 
            http_status=response.status_code
        ).inc()
    return response

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Enterprise Core Microservice",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("APP_ENV", "production"),
        "hostname": socket.gethostname(),
        "status": "HEALTHY",
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }), 200

@app.route('/health/liveness', methods=['GET'])
def liveness():
    return jsonify({"status": "UP"}), 200

@app.route('/health/readiness', methods=['GET'])
def readiness():
    memory = psutil.virtual_memory()
    if memory.percent > 95.0:
        return jsonify({
            "status": "DEGRADED",
            "reason": "High Memory Utilization",
            "memory_percent": memory.percent
        }), 503
    return jsonify({
        "status": "READY",
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": memory.percent
    }), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
