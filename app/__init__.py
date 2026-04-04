import os
from dotenv import load_dotenv
from flask import Flask, jsonify 

import time
import logging

from app.database import init_db, db  
from app.routes import register_routes
from app.logging_config import setup_logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""), # Placeholder for your real DSN
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

START_TIME = time.time()

def create_app():
    setup_logging()
    load_dotenv()

    app = Flask(__name__)
    
    # ... rest of your config ...
    init_db(app)

    # Register internal blueprints
    from app.routes.monitoring import monitoring_bp
    app.register_blueprint(monitoring_bp)

    from app import models 

    register_routes(app)

    from app.extensions import cache
    app.config["CACHE_TYPE"] = "RedisCache"
    app.config["CACHE_REDIS_URL"] = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    cache.init_app(app)

    @app.route("/health")
    def health():
        try: 
            db.execute_sql("SELECT 1")
            uptime_seconds = int(time.time() - START_TIME)
            return jsonify(status="ok", database="connected", uptime_seconds=uptime_seconds)
        
        except Exception as e: 
            return jsonify(status="error", database="unreachable", reason=str(e)), 500
        
    @app.route("/debug-sentry")
    def trigger_error():
        # This will trigger an automatic Sentry Alert
        division_by_zero = 1 / 0
        return division_by_zero
        
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Resource not found", status=404), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="Internal server error", status=500), 500 
   
    return app  

