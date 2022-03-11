import logging

import grpc
from grpc_example_common.helper import grpc_wrapper
from grpc_example_common.interceptor.client_interceptor.customer_top import CustomerTopInterceptor
from grpc_example_common.protos.user import user_pb2 as user_message
from grpc_example_common.protos.user import user_pb2_grpc as user_service

logger: logging.Logger = logging.getLogger()


class UserGrpcServiceMixin(object):
    def __init__(self, channel: grpc.Channel):
        self.user_stub: user_service.UserStub = user_service.UserStub(channel)
        grpc_wrapper.auto_load_wrapper_by_stub(self.user_stub, grpc_wrapper.grpc_client_func_wrapper)

    def create_user(self, *, uid: str, user_name: str, password: str) -> None:
        self.user_stub.create_user(user_message.CreateUserRequest(uid=uid, user_name=user_name, password=password))

    def delete_user(self, *, uid: str) -> None:
        self.user_stub.delete_user(user_message.DeleteUserRequest(uid=uid))

    def login_user(self, *, uid: str, password: str) -> user_message.LoginUserResult:
        return self.user_stub.login_user(user_message.LoginUserRequest(uid=uid, password=password))

    def logout_user(self, *, uid: str, token: str) -> None:
        self.user_stub.logout_user(user_message.LogoutUserRequest(uid=uid, token=token))

    def get_uid_by_token(self, *, token: str) -> str:
        result: user_message.GetUidByTokenResult = self.user_stub.get_uid_by_token(
            user_message.GetUidByTokenRequest(token=token)
        )
        return result.uid


class UserGrpcService(UserGrpcServiceMixin):
    def __init__(self, host: str, port: int) -> None:
        self.channel: grpc.Channel = grpc.intercept_channel(
            grpc.insecure_channel(f"{host}:{port}"), CustomerTopInterceptor()
        )
        UserGrpcServiceMixin.__init__(self, self.channel)

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
