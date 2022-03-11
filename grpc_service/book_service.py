import datetime
import logging
from typing import List, Optional

import grpc
from grpc_example_common.helper import field, grpc_wrapper
from grpc_example_common.interceptor.client_interceptor.customer_top import CustomerTopInterceptor
from grpc_example_common.protos.book import manager_pb2 as manager_message
from grpc_example_common.protos.book import manager_pb2_grpc as manager_service
from grpc_example_common.protos.book import social_pb2 as social_message
from grpc_example_common.protos.book import social_pb2_grpc as social_service

logger: logging.Logger = logging.getLogger()


class BookManagerGrpcServiceMixin(object):
    def __init__(self, channel: grpc.Channel):
        self.manager_stub: manager_service.BookManagerStub = manager_service.BookManagerStub(channel)
        grpc_wrapper.auto_load_wrapper_by_stub(self.manager_stub, grpc_wrapper.grpc_client_func_wrapper)

    def create_book(self, *, isbn: str, book_name: str, book_author: str, book_desc: str, book_url: str) -> None:
        self.manager_stub.create_book(
            manager_message.CreateBookRequest(
                isbn=isbn, book_name=book_name, book_author=book_author, book_desc=book_desc, book_url=book_url
            )
        )

    def delete_book(self, isbn: str) -> None:
        self.manager_stub.delete_book(manager_message.DeleteBookRequest(isbn=isbn))

    def get_book(self, isbn: str) -> manager_message.GetBookResult:
        return self.manager_stub.get_book(manager_message.GetBookRequest(isbn=isbn))

    def get_book_list(
        self, *, limit: int = 20, next_create_time: Optional[datetime.datetime] = None
    ) -> manager_message.GetBookListResult:
        return self.manager_stub.get_book_list(
            manager_message.GetBookListRequest(
                limit=limit, next_create_time=field.datetime_to_timestamp(next_create_time)
            )
        )


class BookSocialGrpcServiceMixin(object):
    def __init__(self, channel: grpc.Channel):
        self.social_stub: social_service.BookSocialStub = social_service.BookSocialStub(channel)
        grpc_wrapper.auto_load_wrapper_by_stub(self.social_stub, grpc_wrapper.grpc_client_func_wrapper)

    def like_book(self, *, isbn: str, like: bool, uid: str) -> None:
        self.social_stub.like_book(social_message.LikeBookRequest(isbn=isbn, like=like, uid=uid))

    def get_book_like(self, *, isbn_list: List[str]) -> social_message.GetBookLikesListResult:
        return self.social_stub.get_book_like(social_message.GetBookLikesRequest(isbn=isbn_list))

    def comment_book(self, *, isbn: str, content: str, uid: str) -> None:
        self.social_stub.comment_book(social_message.CommentBookRequest(isbn=isbn, content=content, uid=uid))

    def get_book_comment(
        self, *, isbn: str, next_create_time: Optional[datetime.datetime] = None, limit: int = 20
    ) -> social_message.GetBookLikesListResult:
        return self.social_stub.get_book_comment(
            social_message.GetBookCommentRequest(
                isbn=isbn, next_create_time=field.datetime_to_timestamp(next_create_time), limit=limit
            )
        )


class BookGrpcService(BookSocialGrpcServiceMixin, BookManagerGrpcServiceMixin):
    def __init__(self, host: str, port: int) -> None:
        self.channel: grpc.Channel = grpc.intercept_channel(
            grpc.insecure_channel(f"{host}:{port}"), CustomerTopInterceptor()
        )
        BookSocialGrpcServiceMixin.__init__(self, self.channel)
        BookManagerGrpcServiceMixin.__init__(self, self.channel)

    def channel_ready_future(self, timeout: int = 10) -> None:
        target: str = (
            f"{self.__class__.__name__}"
            f" {self.channel._channel._connectivity_state.channel.target().decode()}"  # type: ignore
        )  # type: ignore
        try:
            grpc.channel_ready_future(self.channel).result(timeout=timeout)
        except grpc.FutureTimeoutError:
            logger.exception(f"channel:{target} connect timeout")
            raise RuntimeError(f"channel:{target} connect timeout")
        else:
            logger.info(f"channel:{target} connect success")
