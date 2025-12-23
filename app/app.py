import os
import time
from flask import Flask, request, jsonify
import redis

app = Flask(__name__)

APP_TMP_DATA = os.getenv("APP_TMP_DATA", "/tmp")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def write_tmp_probe():
    os.makedirs(APP_TMP_DATA, exist_ok=True)
    path = os.path.join(APP_TMP_DATA, "probe.txt")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{time.time()} ok\n")
    return path

@app.get("/")
def index():
    return "OK\n"

@app.get("/health")
def health():
    details = {}

    # 1) Проверка записи во временную директорию
    try:
        probe_path = write_tmp_probe()
        details["tmp_write"] = "ok"
        details["tmp_path"] = probe_path
    except Exception as e:
        return jsonify(status="fail", reason="tmp_write_failed", error=str(e)), 500

    # 2) Проверка Redis
    try:
        r.ping()
        details["redis"] = "ok"
    except Exception as e:
        return jsonify(status="fail", reason="redis_unreachable", error=str(e), details=details), 500

    return jsonify(status="ok", details=details), 200

@app.post("/cache/<key>")
def cache_set(key):
    value = request.get_data(as_text=True) or ""
    r.set(key, value)
    return jsonify(ok=True, key=key, value=value), 200

@app.get("/cache/<key>")
def cache_get(key):
    value = r.get(key)
    return jsonify(ok=True, key=key, value=value), 200

if __name__ == "__main__":
    # В контейнере слушаем на 0.0.0.0, чтобы было доступно из сети Docker
    app.run(host="0.0.0.0", port=8080)
