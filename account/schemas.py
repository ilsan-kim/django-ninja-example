from enum import Enum

from ninja import Schema

from config.utils.schemas import Token


# Role Enum Class
class RoleEnum(str, Enum):
    Patient = "PATIENT"
    Doctor = "DOCTOR"


# Response of account info
class AccountResp(Schema):
    role: RoleEnum = RoleEnum.Patient
    username: str
    nickname: str


# Request of account signup
class AccountSignupReq(Schema):
    username: str
    role: RoleEnum = RoleEnum.Patient
    nickname: str
    password: str


# Response of account signup
class AccountSignupResp(Schema):
    profile: AccountResp
    token: Token


# Reqeust of account update
class AccountUpdateReq(Schema):
    nickname: str = None
    password: str = None


# Request of account signin
class AccountSigninReq(Schema):
    username: str
    password: str


# Response of account signin
class AccountSigninResp(AccountSignupResp):
    pass


# Request of password change
class PasswordChangeIn(Schema):
    old_password: str
    new_password: str
