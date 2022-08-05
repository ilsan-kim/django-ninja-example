from http import HTTPStatus

from ninja import Router
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from config.utils.permissions import create_token, AuthBearer
from config.utils.schemas import MessageOut
from account.models import User
from account import schemas

auth_controller = Router(tags=["auth"])


@auth_controller.post("/register", auth=None, response={
    200: schemas.AccountSignupResp,
    403: MessageOut,
    500: MessageOut,
})
def register(request, payload: schemas.AccountSignupReq):
    """
    <h2>회원가입 API</h2>
    content-type: application/json </br>
    |param|description|type|example|
    |-----|-----------|----|-------|
    |username|로그인시 사용할 username, unique=True|string|"kim"|
    |role|생성할 회원 role|enum (string)|"PATIENT" / "DOCTOR"|
    |nickname|회원 이름|string|"김환자"|
    |password|로그인시 사용할 비밀번호|string|"thisissafepassword"|
    """
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
    """
    <h2>로그인 API</h2>
    content-type: application/json </br>
    |param|description|type|example|
    |-----|-----------|----|-------|
    |username|회원가입시 입력한 username값|string|"kim"|
    |password|회원가입시 입력한 password값|string|"thisissafepassword"|
    """
    user = authenticate(username=payload.username, password=payload.password)
    if user is not None:
        return HTTPStatus.OK, {
            "profile": user,
            "token": create_token(user.id)
        }
    return HTTPStatus.NOT_FOUND, {
        "message": "user not found"
    }
