from typing import Any, Generator

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from grpc import _utilities

from app import create_app


def result(self: Any, timeout: Any = None) -> Any:
    pass


# Blocking the start check of grpc service
_utilities._ChannelReadyFuture.result = result


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
