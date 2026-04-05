import json
from flask import Blueprint, jsonify, request, make_response
from playhouse.shortcuts import model_to_dict
from app.models.event import Event
from app.models.user import User
from app.models.url import Url

events_bp = Blueprint("events", __name__)

@events_bp.route("/events", methods=["GET"])
def list_events():
    # Dynamic Filtering from query parameters
    url_id = request.args.get("url_id", type=int)
    user_id = request.args.get("user_id", type=int)
    event_type = request.args.get("event_type")
    
    query = Event.select().order_by(Event.timestamp.desc())
    
    if url_id:
        query = query.where(Event.url == url_id)
    if user_id:
        query = query.where(Event.user == user_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
        
    data = []
    for e in query:
        # Convert peewee model to dict
        e_dict = model_to_dict(e)
        
        # Parse 'details' if it's a JSON string
        if isinstance(e_dict.get("details"), str):
            try:
                e_dict["details"] = json.loads(e_dict["details"])
            except json.JSONDecodeError:
                pass
        data.append(e_dict)
        
    return jsonify(data)

@events_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()
    if not data or "event_type" not in data or "url_id" not in data or "user_id" not in data:
         return jsonify(error="Missing required fields", status=400), 400
         
    # Check if dependencies exist
    try:
        user = User.get_by_id(data["user_id"])
        url = Url.get_by_id(data["url_id"])
    except (User.DoesNotExist, Url.DoesNotExist):
        return jsonify(error="User or URL not found", status=404), 404
        
    # details can be a dict or a string. 
    details = data.get("details", "")
    if isinstance(details, dict):
        details = json.dumps(details)
        
    event = Event.create(
        user=user,
        url=url,
        event_type=data["event_type"],
        timestamp=data.get("timestamp"), # Use provided or default
        details=details
    )
    
    # Return the newly created event as a dict
    res_dict = model_to_dict(event)
    if isinstance(res_dict.get("details"), str):
        try:
            res_dict["details"] = json.loads(res_dict["details"])
        except json.JSONDecodeError:
            pass
            
    return jsonify(res_dict), 201
