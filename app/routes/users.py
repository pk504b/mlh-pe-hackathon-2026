from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict
from app.models.user import User

users_bp = Blueprint("users", __name__)

@users_bp.route("/users")
def list_users():
    # Only return first 50 users to avoid massive response payload during load test
    users = User.select().limit(50)
    return jsonify([model_to_dict(u) for u in users])
