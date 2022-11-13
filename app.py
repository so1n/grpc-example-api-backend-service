import datetime
from json import JSONEncoder
from typing import Any

from flask.app import Flask

from app_service.route import manager_book_bp, social_book_bp, user_bp
from app_service.utils import ContextMiddleware, api_exception
from grpc_service.book_service import BookGrpcService
from grpc_service.user_service import UserGrpcService
from app_service.user_gateway_route import add_grpc_gateway_route
from pait.app.flask import add_doc_route
from pait.g import config
from pait.extra.config import apply_block_http_method_set


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

    # 映射gRPC服务对应的接口到app
    add_grpc_gateway_route(app)
    # 添加一个OpenAPI文档路由，从而可以查看被Pait托管路由的接口文档
    add_doc_route(app)
    app.errorhandler(Exception)(api_exception)
    return app


if __name__ == "__main__":
    # 屏蔽接口文档中`OPTIONS`和`HEAD`方法接口的展示
    config.init_config(apply_func_list=[apply_block_http_method_set({"OPTIONS", "HEAD"})])
    create_app().run("localhost", port=8000)
