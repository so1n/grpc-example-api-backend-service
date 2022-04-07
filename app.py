import datetime
from json import JSONEncoder
from typing import Any

from flask.app import Flask

from app_service.route import manager_book_bp, social_book_bp, user_bp
from app_service.utils import ContextMiddleware, api_exception
from grpc_service.book_service import BookGrpcService
from grpc_service.user_service import UserGrpcService


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if type(obj) == datetime.date:
            return datetime.datetime.strptime(str(obj), "%Y-%m-%d")
        elif isinstance(obj, datetime.datetime):
            return int(obj.timestamp())
        else:
            return super().default(obj)


def create_app() -> Flask:
    app: Flask = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
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
