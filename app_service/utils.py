from typing import Any, Union

from flask import Blueprint, Flask, Response
from flask import g as flask_g
from flask import jsonify, request

from grpc_service.book_service import BookGrpcService
from grpc_service.user_service import UserGrpcService

APP_TYPE = Union[Blueprint, Flask]


class CustomerGType(object):
    book_grpc_service: BookGrpcService
    user_grpc_service: UserGrpcService

    def __getattr__(self, key: str) -> Any:
        return getattr(flask_g, key)

    def __setattr__(self, key: str, value: Any) -> None:
        setattr(flask_g, key, value)


g: CustomerGType = CustomerGType()


class ContextMiddleware(object):
    def __init__(
        self, *, app: APP_TYPE, book_grpc_service: BookGrpcService, user_grpc_service: UserGrpcService
    ) -> None:
        self._app = app
        self._app.before_request(self._before_requests)
        self._app.after_request(self._after_requests)

        self._book_grpc_service: BookGrpcService = book_grpc_service
        self._user_grpc_service: UserGrpcService = user_grpc_service

    def _before_requests(self) -> None:
        g.book_grpc_service = self._book_grpc_service
        g.user_grpc_service = self._user_grpc_service
        return

    def _after_requests(self, response: Response) -> Response:
        return response


def get_uid_by_token() -> str:
    token: str = request.headers.get("token", "")
    if not token:
        raise RuntimeError("Can not found token")
    return g.user_grpc_service.get_uid_by_token(token=token)


def make_response(data: Any = None, code: int = 0) -> Response:
    return jsonify({"code": code, "data": data})


def api_exception(exc: Exception) -> Response:
    return make_response(data=str(exc), code=1)
