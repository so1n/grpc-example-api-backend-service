from contextlib import contextmanager
from typing import Any, Generator

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from grpc import _utilities
from grpc_example_common.protos.book import manager_pb2_grpc, social_pb2_grpc
from grpc_example_common.protos.user import user_pb2_grpc

from app import create_app
from tests.grpc_abc_stub import BookManagerStub, BookSocialStub, UserStub


def result(self: Any, timeout: Any = None) -> Any:
    pass


# Blocking the start check of grpc service
_utilities._ChannelReadyFuture.result = result

user_pb2_grpc.UserStub = UserStub
user_pb2_grpc.UserStub = UserStub
social_pb2_grpc.BookSocialStub = BookSocialStub
manager_pb2_grpc.BookManagerStub = BookManagerStub


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    flask_app: Flask = create_app()
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    client: FlaskClient = flask_app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = flask_app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


@contextmanager
def customer_app() -> Generator[FlaskClient, None, None]:
    flask_app: Flask = create_app()
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    client: FlaskClient = flask_app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = flask_app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()
