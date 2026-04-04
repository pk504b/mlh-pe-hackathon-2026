from dotenv import load_dotenv
from flask import Flask, jsonify 

import time

from app.database import init_db, db  
from app.routes import register_routes

START_TIME = time.time()

def create_app():
    load_dotenv()

    app = Flask(__name__)

    init_db(app)

    from app import models 

    register_routes(app)

    @app.route("/health")
    def health():
        try: 
            db.execute_sql("SELECT 1")
            uptime_seconds = int(time.time() - START_TIME)
            return jsonify(status="ok", database="connected", uptime_seconds=uptime_seconds)
        
        except Exception as e: 
            return jsonify(status="error", database="unreachable", reason=str(e)), 500
        
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Resource not found", status=404), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="Internal server error", status=500), 500 
   
    return app  

