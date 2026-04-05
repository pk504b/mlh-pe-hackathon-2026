def register_routes(app):
    from app.routes.songs import songs_bp
    from app.routes.users import users_bp
    from app.routes.events import events_bp
    from app.routes.urls import urls_bp
    
    app.register_blueprint(songs_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(urls_bp)
