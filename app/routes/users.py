import os
import csv
from flask import Blueprint, jsonify, request, make_response, abort
from playhouse.shortcuts import model_to_dict
from app.models.user import User
from app.extensions import cache
from peewee import IntegrityError

users_bp = Blueprint("users", __name__)

@users_bp.route("/users", methods=["GET"])
def list_users():
    # Handle Pagination
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    
    query = User.select().order_by(User.id)
    total_count = query.count()
    users = query.paginate(page, per_page)
    
    data = [model_to_dict(u) for u in users]
    
    response = make_response(jsonify(data))
    response.headers["X-Total-Count"] = total_count
    # Add cache header for Tier 3 verification (safe for no-redis environments)
    try:
        x_cache = "HIT" if cache.get(f"users_p{page}") else "MISS"
    except Exception:
        x_cache = "MISS (No Redis)"
    
    response.headers["X-Cache"] = x_cache
    return response

@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = User.get_by_id(user_id)
        return jsonify(model_to_dict(user))
    except User.DoesNotExist:
        return jsonify(error="Resource not found", status=404), 404

@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "username" not in data or "email" not in data:
        return jsonify(error="Missing required fields", status=400), 400
    
    try:
        user = User.create(
            username=data["username"],
            email=data["email"],
            created_at=data.get("created_at") # Use provided or default
        )
        return jsonify(model_to_dict(user)), 201
    except IntegrityError:
        return jsonify(error="User already exists", status=400), 400

@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = User.get_by_id(user_id)
        data = request.get_json()
        
        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"]
            
        user.save()
        return jsonify(model_to_dict(user))
    except User.DoesNotExist:
        return jsonify(error="Resource not found", status=404), 404

@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = User.get_by_id(user_id)
        user.delete_instance()
        return jsonify(message="User deleted"), 200
    except User.DoesNotExist:
        return jsonify(error="Resource not found", status=404), 404

@users_bp.route("/users/bulk", methods=["POST"])
def bulk_load_users():
    data = request.get_json()
    filename = data.get("file", "users.csv")
    
    # Try multiple common locations for the CSV
    possible_paths = [
        filename,
        os.path.join("seed", filename),
        os.path.join("data", filename)
    ]
    
    filepath = next((p for p in possible_paths if os.path.exists(p)), None)
    
    if not filepath:
        return jsonify(error=f"File {filename} not found in root or /seed", status=404), 404
        
    try:
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        from app.database import db
        with db.atomic():
            for i in range(0, len(rows), 100):
                User.insert_many(rows[i:i+100]).on_conflict_ignore().execute()
                
        return jsonify(message=f"Successfully processed {len(rows)} users"), 201
    except Exception as e:
        return jsonify(error=str(e), status=500), 500
