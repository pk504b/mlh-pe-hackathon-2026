def register_routes(app):
    from app.routes.songs import songs_bp
    app.register_blueprint(songs_bp)