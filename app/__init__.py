from flask import Flask
from app.routes.authroutes import Authroutes


def create_app():
    app=Flask(__name__)

    auth_routes=Authroutes()
    app.register_blueprint(auth_routes.login())

    return app