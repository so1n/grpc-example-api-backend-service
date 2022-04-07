from datetime import datetime

from flask import Response, request
from grpc_example_common.helper import field
from grpc_example_common.protos.book import social_pb2 as social_message

from app_service.utils import g, get_uid_by_token, make_response


def like_book() -> Response:
    uid: str = get_uid_by_token()
    g.book_grpc_service.like_book(isbn=request.json["isbn"], like=request.json["like"], uid=uid)
    return make_response()


def get_book_likes() -> Response:
    get_uid_by_token()
    result: social_message.GetBookLikesListResult = g.book_grpc_service.get_book_like(
        isbn_list=request.args["isbn_list"].split(",")
    )
    return make_response({"book_like_list": field.proto_dump(result)})


def comment_book() -> Response:
    uid: str = get_uid_by_token()
    g.book_grpc_service.comment_book(
        isbn=request.json["isbn"],
        content=request.json["content"],
        uid=uid,
    )
    return make_response()


def get_book_comment() -> Response:
    get_uid_by_token()
    result: social_message.GetBookCommentListResult = g.book_grpc_service.get_book_comment(
        isbn=request.args["isbn"],
        next_create_time=datetime.fromtimestamp(int(request.args["next_create_time"])),
        limit=int(request.args["limit"]),
    )
    return make_response({"book_comment_list": field.proto_dump(result)})
