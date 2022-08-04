from http import HTTPStatus

from ninja import Router
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from config.utils.permissions import create_token, AuthBearer
from config.utils.schemas import MessageOut
from account.models import User
from account import schemas

auth_controller = Router(tags=["auth"])


# TODO change return model from dict to pydantic schema
@auth_controller.post("/register", auth=None, response={
    200: schemas.AccountSignupResp,
    403: MessageOut,
    500: MessageOut,
})
def register(request, payload: schemas.AccountSignupReq):
    already_registered = User.already_registered(username=payload.username)
    if already_registered:
        return HTTPStatus.FORBIDDEN, {
            "message": f"username {payload.username} already registered"
        }

    user = User.objects.create_user(
        username=payload.username,
        password=payload.password,
        role=payload.role,
        nickname=payload.nickname,
    )

    if user:
        token = create_token(user.id)
        return HTTPStatus.OK, {
            "profile": user,
            "token": token
        }
    else:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {
            "message": "error on create user"
            }


@auth_controller.post("/login", auth=None, response={
    200: schemas.AccountSigninResp,
    404: MessageOut,
})
def login(request, payload: schemas.AccountSigninReq):
    user = authenticate(username=payload.username, password=payload.password)
    if user is not None:
        return HTTPStatus.OK, {
            "profile": user,
            "token": create_token(user.id)
        }
    return HTTPStatus.NOT_FOUND, {
        "message": "user not found"
    }