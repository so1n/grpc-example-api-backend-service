from flask.app import Flask

from app_service.route import manager_book_bp, social_book_bp, user_bp
from app_service.utils import ContextMiddleware, api_exception
from grpc_service.book_service import BookGrpcService
from grpc_service.user_service import UserGrpcService


def create_app() -> Flask:
    app: Flask = Flask(__name__)
    app.register_blueprint(manager_book_bp)
    app.register_blueprint(social_book_bp)
    app.register_blueprint(user_bp)

    book_grpc_service: BookGrpcService = BookGrpcService("0.0.0.0", 9000)
    book_grpc_service.channel_ready_future(timeout=3)
    user_grpc_service: UserGrpcService = UserGrpcService("0.0.0.0", 9001)
    user_grpc_service.channel_ready_future(timeout=3)
    ContextMiddleware(app=app, book_grpc_service=book_grpc_service, user_grpc_service=user_grpc_service)

    app.errorhandler(Exception)(api_exception)
    return app


if __name__ == "__main__":
    create_app().run("localhost", port=8000)
