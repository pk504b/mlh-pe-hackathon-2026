import string
import random
from flask import Blueprint, jsonify, request, make_response
from playhouse.shortcuts import model_to_dict
from app.models.url import Url
from app.models.user import User
from peewee import IntegrityError

urls_bp = Blueprint("urls", __name__)

def generate_short_code(length=6):
    """Generate a unique short code for the URL."""
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        # Verify uniqueness
        if not Url.select().where(Url.short_code == code).exists():
            return code

@urls_bp.route("/urls", methods=["GET"])
def list_urls():
    user_id = request.args.get("user_id", type=int)
    is_active = request.args.get("is_active")
    
    query = Url.select().order_by(Url.id)
    
    if user_id:
        query = query.where(Url.user == user_id)
        
    if is_active is not None:
        # Handle "true"/"false" strings from query params
        active_bool = is_active.lower() == "true"
        query = query.where(Url.is_active == active_bool)
        
    data = [model_to_dict(u) for u in query]
    return jsonify(data)

@urls_bp.route("/urls/<int:url_id>", methods=["GET"])
def get_url(url_id):
    try:
        url = Url.get_by_id(url_id)
        return jsonify(model_to_dict(url))
    except Url.DoesNotExist:
        return jsonify(error="Resource not found", status=404), 404

@urls_bp.route("/urls", methods=["POST"])
def create_url():
    data = request.get_json()
    if not data or "original_url" not in data or "user_id" not in data:
         return jsonify(error="Missing required fields", status=400), 400
         
    try:
        user = User.get_by_id(data["user_id"])
    except User.DoesNotExist:
        return jsonify(error="User not found", status=404), 404
        
    short_code = generate_short_code()
    
    url = Url.create(
        user=user,
        original_url=data["original_url"],
        title=data.get("title", "Untitled"),
        short_code=short_code,
        is_active=True
    )
    
    return jsonify(model_to_dict(url)), 201

@urls_bp.route("/urls/<int:url_id>", methods=["PUT"])
def update_url(url_id):
    try:
        url = Url.get_by_id(url_id)
        data = request.get_json()
        
        if "title" in data:
            url.title = data["title"]
        if "is_active" in data:
            url.is_active = data["is_active"]
        if "original_url" in data:
            url.original_url = data["original_url"]
            
        url.save()
        return jsonify(model_to_dict(url))
    except Url.DoesNotExist:
        return jsonify(error="Resource not found", status=404), 404

@urls_bp.route("/urls/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    try:
        url = Url.get_by_id(url_id)
        url.delete_instance()
        return jsonify(message="URL deleted"), 200
    except Url.DoesNotExist:
        return jsonify(error="Resource not found", status=404), 404
