import datetime

from google.protobuf.empty_pb2 import Empty  # type: ignore
from grpc_example_common.helper.field import datetime_to_timestamp
from grpc_example_common.protos.book import social_pb2 as social_message
from grpc_example_common.protos.user import user_pb2 as user_message
from pytest_mock import MockFixture
from werkzeug.test import TestResponse

from tests.conftest import customer_app


class TestUser:
    def test_like_book(self, mocker: MockFixture) -> None:
        mocker.patch("grpc_example_common.protos.book.social_pb2_grpc.BookSocialStub.like_book").return_value = Empty()
        mocker.patch(
            "grpc_example_common.protos.user.user_pb2_grpc.UserStub.get_uid_by_token"
        ).return_value = user_message.GetUidByTokenResult(uid="123")
        with customer_app() as client:
            resp: TestResponse = client.post(
                "api/book/social/like-book", json={"isbn": "123", "like": True}, headers={"token": "666666"}
            )
            assert resp.json["code"] == 0

    def test_comment_book(self, mocker: MockFixture) -> None:
        mocker.patch(
            "grpc_example_common.protos.book.social_pb2_grpc.BookSocialStub.comment_book"
        ).return_value = Empty()
        mocker.patch(
            "grpc_example_common.protos.user.user_pb2_grpc.UserStub.get_uid_by_token"
        ).return_value = user_message.GetUidByTokenResult(uid="123")
        with customer_app() as client:
            resp: TestResponse = client.post(
                "api/book/social/comment-book", json={"isbn": "123", "content": "xxx"}, headers={"token": "666666"}
            )
            assert resp.json["code"] == 0

    def test_get_book_likes(self, mocker: MockFixture) -> None:
        mocker.patch(
            "grpc_example_common.protos.book.social_pb2_grpc.BookSocialStub.get_book_like"
        ).return_value = social_message.GetBookLikesListResult(
            result=[social_message.GetBookLikesResult(isbn="123", book_like=5)]
        )
        mocker.patch(
            "grpc_example_common.protos.user.user_pb2_grpc.UserStub.get_uid_by_token"
        ).return_value = user_message.GetUidByTokenResult(uid="123")
        with customer_app() as client:
            resp: TestResponse = client.get(
                "api/book/social/get-book-likes?isbn_list=123,456", headers={"token": "666666"}
            )
            assert resp.json["data"] == {"book_like_list": {"result": [{"book_like": 5, "isbn": "123"}]}}

    def test_get_book_comment(self, mocker: MockFixture) -> None:
        mocker.patch(
            "grpc_example_common.protos.book.social_pb2_grpc.BookSocialStub.get_book_comment"
        ).return_value = social_message.GetBookCommentListResult(
            result=[
                social_message.GetBookCommentResult(
                    isbn="123",
                    content="fake content",
                    uid="123",
                    create_time=datetime_to_timestamp(datetime.datetime.fromtimestamp(1600000000)),
                )
            ]
        )
        mocker.patch(
            "grpc_example_common.protos.user.user_pb2_grpc.UserStub.get_uid_by_token"
        ).return_value = user_message.GetUidByTokenResult(uid="123")
        with customer_app() as client:
            resp: TestResponse = client.get(
                "api/book/social/get-book-comment?isbn=123&next_create_time=1600000000&limit=10",
                headers={"token": "666666"},
            )
            assert resp.json["data"] == {
                "book_comment_list": {
                    "result": [{"content": "fake content", "create_time": 1600000000, "isbn": "123", "uid": "123"}]
                }
            }
