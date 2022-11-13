from typing import Any, Callable, Type
from uuid import uuid4
import grpc

from flask import Flask, jsonify, Response
from pydantic import BaseModel, Field

from pait.app.flask.grpc_route import GrpcGatewayRoute
from pait.app import set_app_attribute
from pait.field import Header, Query, Body, BaseField
from pait.model.response import PaitBaseResponseModel, PaitJsonResponseModel
from pait.util.grpc_inspect.stub import GrpcModel
from pait.util.grpc_inspect.types import Message
from protobuf_to_pydantic import msg_to_pydantic_model

from grpc_example_common.protos.user import user_pb2, user_pb2_grpc


def gen_response_model_handle(grpc_model: GrpcModel) -> Type[PaitBaseResponseModel]:
    class CustomerJsonResponseModel(PaitJsonResponseModel):
        class CustomerJsonResponseRespModel(BaseModel):
            code: int = Field(0, description="api code")
            msg: str = Field("success", description="api status msg")
            data: msg_to_pydantic_model(grpc_model.response) = Field(description="api response data")  # type: ignore

        name: str = grpc_model.response.DESCRIPTOR.name
        response_data: Type[BaseModel] = CustomerJsonResponseRespModel

    return CustomerJsonResponseModel


def add_grpc_gateway_route(app: Flask) -> None:
    """Split out to improve the speed of test cases"""

    def _make_response(resp_dict: dict) -> Response:
        return jsonify({"code": 0, "msg": "", "data": resp_dict})

    class CustomerGrpcGatewayRoute(GrpcGatewayRoute):
        def _gen_request_pydantic_class_from_message(self, message: Type[Message], http_method: str) -> Type[BaseModel]:
            """The `DELETE` method is not supported by default,
            here the `DELETE` method is supported by inheriting the original method"""
            if http_method == "GET":
                default_field: Type[BaseField] = Query
            elif http_method in ("POST", "DELETE"):
                default_field = Body
            else:
                raise RuntimeError(f"{http_method} is not supported")
            return msg_to_pydantic_model(
                message,
                default_field=default_field,
                comment_prefix="pait",
                parse_msg_desc_method=getattr(message, "_message_module")
                if self._parse_msg_desc == "by_mypy"
                else self._parse_msg_desc,
            )

        def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:

            # Token is not required for logging in and creating user interfaces, so the native method is used
            if grpc_model.method in ("/user.User/login_user", "/user.User/create_user"):
                return super().gen_route(grpc_model, request_pydantic_model_class)
            else:
                def _route(
                    # The pydantic.BaseModel object generated by the corresponding grpc message
                    request_pydantic_model: request_pydantic_model_class,  # type: ignore
                    # Add token parameter
                    token: str = Header.i(description="User Token"),
                    # Add the request id parameter, irrelevant to the requirement
                    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                ) -> Any:
                    func: Callable = self.get_grpc_func(grpc_model.method)
                    request_dict: dict = request_pydantic_model.dict()  # type: ignore
                    if grpc_model.method == "/user.User/logout_user":
                        # A token is required to log out of the login interface
                        request_dict["token"] = token
                    else:
                        # Other interfaces do not need the token parameter,
                        # and only need to check whether the token is legal
                        result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(self.channel).get_uid_by_token(
                            user_pb2.GetUidByTokenRequest(token=token)
                        )
                        if not result.uid:
                            raise RuntimeError(f"Not found user by token:{token}")
                    # Generate the parameters of the call and then call the g RPC method,
                    # and return the data returned by the g RPC method to the caller
                    request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
                    # add req_id to request
                    grpc_msg: Message = func(request_msg, metadata=[("req_id", req_id)])
                    return self._make_response(self.get_dict_from_msg(grpc_msg))

                return _route

    grpc_gateway_route: CustomerGrpcGatewayRoute = CustomerGrpcGatewayRoute(
        app,
        user_pb2_grpc.UserStub,
        prefix="/api/gateway",
        title="UserGrpc",
        gen_response_model_handle=gen_response_model_handle,
        make_response=_make_response,
    )
    grpc_gateway_route.init_channel(grpc.intercept_channel(grpc.insecure_channel("127.0.0.1:9001")))
    set_app_attribute(app, "grpc_gateway_route", grpc_gateway_route)  # support unittest