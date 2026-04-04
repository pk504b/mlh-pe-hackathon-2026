import psutil
import os
from flask import Blueprint, jsonify

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/metrics')
def metrics():
    # Gather live system data
    data = {
        "status": "up",
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "used_mb": psutil.virtual_memory().used / (1024 * 1024),
                "total_mb": psutil.virtual_memory().total / (1024 * 1024)
            },
            "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    }
    return jsonify(data)
