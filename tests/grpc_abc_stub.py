from typing import Any


class UserStub(object):
    def __init__(self, channel: Any):
        pass

    def get_uid_by_token(self, *args: Any, **kwargs: Any) -> None:
        pass

    def logout_user(self, *args: Any, **kwargs: Any) -> None:
        pass

    def login_user(self, *args: Any, **kwargs: Any) -> None:
        pass

    def create_user(self, *args: Any, **kwargs: Any) -> None:
        pass

    def delete_user(self, *args: Any, **kwargs: Any) -> None:
        pass


class BookManagerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel: Any):
        pass

    def create_book(self, *args: Any, **kwargs: Any) -> None:
        pass

    def delete_book(self, *args: Any, **kwargs: Any) -> None:
        pass

    def get_book(self, *args: Any, **kwargs: Any) -> None:
        pass

    def get_book_list(self, *args: Any, **kwargs: Any) -> None:
        pass


class BookSocialStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel: Any):
        pass

    def like_book(self, *args: Any, **kwargs: Any) -> None:
        pass

    def get_book_like(self, *args: Any, **kwargs: Any) -> None:
        pass

    def comment_book(self, *args: Any, **kwargs: Any) -> None:
        pass

    def get_book_comment(self, *args: Any, **kwargs: Any) -> None:
        pass
