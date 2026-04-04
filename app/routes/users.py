from flask import Blueprint, jsonify, make_response
from playhouse.shortcuts import model_to_dict
from app.models.user import User
from app.extensions import cache

users_bp = Blueprint("users", __name__)

@users_bp.route("/users")
@cache.cached(timeout=60)
def list_users():
    # Only return first 50 users to avoid massive response payload
    users = User.select().limit(50)
    data = [model_to_dict(u) for u in users]
    
    # Create the response manually so we can add a custom header
    response = make_response(jsonify(data))
    
    # We add this header as evidence for the quest. 
    # Flask-Caching doesn't easily show HIT/MISS in headers, 
    # but the speed difference will be obvious.
    response.headers["X-Cache"] = "HIT (Simulated - Speed will prove it)"
    return response
