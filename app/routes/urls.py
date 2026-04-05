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
    user_id = request.args.get("user_id")
    if user_id:
        urls = list(Url.select().where(Url.user == user_id))
    else:
        urls = list(Url.select())
    data = [model_to_dict(u, recurse=False) for u in urls]
    return jsonify(kind="list", sample=data, total_items=len(data))

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
    if not data:
        return jsonify(error="No data provided"), 400
    if "original_url" not in data:
        return jsonify(error="Missing fields: ['original_url']"), 400
    short_code = data.get("short_code") or generate_short_code()
    try:
        url = Url.create(
            user=data.get("user_id"),
            short_code=short_code,
            original_url=data["original_url"],
            title=data.get("title"),
            is_active=data.get("is_active", True)
        )
        return jsonify(model_to_dict(url, recurse=False)), 201
    except Exception as e:
        return jsonify(error=str(e)), 400

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
