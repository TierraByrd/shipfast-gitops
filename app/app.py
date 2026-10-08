import os
from datetime import datetime, timezone

from flask import Flask, jsonify

app = Flask(__name__)

SERVICE_NAME = "shipfast-status-api"


@app.get("/status")
def status():
    return jsonify(
        service=SERVICE_NAME,
        version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("APP_ENV", "dev"),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/healthz")
def healthz():
    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
