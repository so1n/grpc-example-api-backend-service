from datetime import datetime

from flask import Response, request
from grpc_example_common.helper import field
from grpc_example_common.protos.book import manager_pb2 as manager_message

from app_service.utils import g, get_uid_by_token, make_response


def create_book() -> Response:
    get_uid_by_token()
    g.book_grpc_service.create_book(
        isbn=request.json["isbn"],
        book_url=request.json["book_url"],
        book_desc=request.json["book_desc"],
        book_author=request.json["book_author"],
        book_name=request.json["book_name"],
    )
    return make_response()


def delete_book() -> Response:
    get_uid_by_token()
    g.book_grpc_service.delete_book(isbn=request.json["isbn"])
    return make_response()


def get_book() -> Response:
    get_uid_by_token()
    result: manager_message.GetBookResult = g.book_grpc_service.get_book(isbn=request.args["isbn"])
    return make_response(
        {
            "isbn": result.isbn,
            "book_name": result.book_name,
            "book_author": result.book_author,
            "book_desc": result.book_desc,
            "book_url": result.book_url,
            "create_time": field.timestamp_to_datetime(result.create_time),
            "update_time": field.timestamp_to_datetime(result.update_time),
        }
    )


def get_book_list() -> Response:
    get_uid_by_token()
    return make_response(
        {
            "book_list": g.book_grpc_service.get_book_list(
                limit=int(request.args["limit"]),
                next_create_time=datetime.fromtimestamp(int(request.args["next_create_time"])),
            )
        }
    )
