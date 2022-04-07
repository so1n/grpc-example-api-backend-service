from flask import Response, request
from grpc_example_common.protos.user import user_pb2 as user_message

from app_service.utils import g, get_uid_by_token, make_response


def create_user() -> Response:
    request_dict: dict = request.json
    g.user_grpc_service.create_user(
        uid=request_dict["uid"], user_name=request_dict["user_name"], password=request_dict["password"]
    )
    return make_response()


def delete_user() -> Response:
    request_dict: dict = request.json
    g.user_grpc_service.delete_user(uid=request_dict["uid"])
    return make_response()


def login_route() -> Response:
    request_dict: dict = request.json
    login_result: user_message.LoginUserResult = g.user_grpc_service.login_user(
        uid=request_dict["uid"], password=request_dict["password"]
    )
    return make_response({"token": login_result.token, "uid": login_result.uid})


def logout_route() -> Response:
    request_dict: dict = request.json
    if get_uid_by_token() == request_dict["uid"]:
        token: str = request.headers.get("token", "")
        g.user_grpc_service.logout_user(uid=request_dict["uid"], token=token)
        return make_response()
    else:
        raise RuntimeError("Uid ERROR")
