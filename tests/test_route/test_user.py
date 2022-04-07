from google.protobuf.empty_pb2 import Empty  # type: ignore
from grpc_example_common.protos.user import user_pb2 as user_message
from pytest_mock import MockFixture
from werkzeug.test import TestResponse

from tests.conftest import customer_app


class TestUser:
    def test_create_user(self, mocker: MockFixture) -> None:
        mocker.patch("grpc_example_common.protos.user.user_pb2_grpc.UserStub.create_user").return_value = Empty()
        with customer_app() as client:
            resp: TestResponse = client.post(
                "/api/user/create", json={"uid": "123", "user_name": "so1n", "password": "aha"}
            )
            assert resp.json["code"] == 0

    def test_delete_user(self, mocker: MockFixture) -> None:
        mocker.patch("grpc_example_common.protos.user.user_pb2_grpc.UserStub.delete_user").return_value = Empty()
        with customer_app() as client:
            resp: TestResponse = client.post("/api/user/delete", json={"uid": "123"})
            assert resp.json["code"] == 0
        mocker.patch("grpc_example_common.protos.user.user_pb2_grpc.UserStub.delete_user").side_effect = RuntimeError(
            "test error"
        )
        with customer_app() as client:
            resp = client.post("/api/user/delete", json={"uid": "123"})
            assert resp.json["data"] == "test error"

    def test_login_user(self, mocker: MockFixture) -> None:
        mocker.patch(
            "grpc_example_common.protos.user.user_pb2_grpc.UserStub.login_user"
        ).return_value = user_message.LoginUserResult(uid="123", token="66666")
        with customer_app() as client:
            resp: TestResponse = client.post("/api/user/login", json={"uid": "123", "password": "pw"})
            assert resp.json["data"] == {"uid": "123", "token": "66666"}

    def test_logout(self, mocker: MockFixture) -> None:
        mocker.patch("grpc_example_common.protos.user.user_pb2_grpc.UserStub.logout_user").return_value = Empty()
        mocker.patch(
            "grpc_example_common.protos.user.user_pb2_grpc.UserStub.get_uid_by_token"
        ).return_value = user_message.GetUidByTokenResult(uid="123")
        with customer_app() as client:
            resp: TestResponse = client.post("/api/user/logout", json={"uid": "123"}, headers={"token": "666666"})
            assert resp.json["code"] == 0

        mocker.patch(
            "grpc_example_common.protos.user.user_pb2_grpc.UserStub.get_uid_by_token"
        ).return_value = user_message.GetUidByTokenResult(uid="1234")
        with customer_app() as client:
            resp = client.post("/api/user/logout", json={"uid": "123"}, headers={"token": "666666"})
            print(resp.json)
            assert resp.json["data"] == "Uid ERROR"
