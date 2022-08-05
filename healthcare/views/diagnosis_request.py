import datetime
from http import HTTPStatus

from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from config.utils.permissions import AuthBearer
from config.utils.schemas import MessageOut
from config.utils.utils import paginated_response as pr
from account.models import User
from healthcare.models import Doctor, DiagnosisRequest
from healthcare.utils import calc_diagnosis_expired_time
from healthcare.mappers.diagnosis_request import map_diagnosis_request
from healthcare import schemas

diagnosis_request_controller = Router(tags=['diagnosis_request'])


@diagnosis_request_controller.post("/request", auth=AuthBearer(), response={
    200: schemas.DiagnosisRequestRes,
    403: MessageOut,
})
def reqeust(request, payload: schemas.DiagnosisRequestReq):
    """
    <h2> 진료 요청 API (환자 전용 API) </h2>
    content-type: application/json </br>
    auth_user_role: PATIENT </br>
    |param|description|type|example|
    |-----|-----------|----|-------|
    |doctor_id|진료 요청 하고자 하는 의사의 id|int|1|
    |request_at|진료 요청 하고자 하는 시간|datetime with timezone(UTC)|"2022-01-15T09:00:00Z"|
    ------
    - 진료 요청은 다음의 규칙을 따릅니다. (__*진료 요청 시간*__은 유저가 요청하는 때에 동적으로 정해집니다. 입력 파라미터 __*request_at*__ 은 __*진료 요청 시간*__이 아닌 진료 희망 시간 입니다.)
        1. 서버 기준 시간은 UTC 입니다. (KST 기준 19:00에 요청을 하면 서버에서 처리하는 "현재 시간"은 10:00 입니다.)
        2. 진료 요청 시간 (UTC)이 의사의 영업시간이 아닌경우,
            1. 영업 시작 전 이거나, 휴식시간인 경우 -> 영업 시작(재개) 후 15분 동안 해당 요청이 유효함
            2. 영업 시작 종료인 경우 -> 다음 영업일의 영업 시작 후 15분 동안 해당 요청이 유효
    - 진료 희망 시간은 다음의 규칙에 따라 입력되어야 합니다.
        1. __*진료 희망 시간(request_at)*__이 영업시간이 아닌 경우 (휴식시간이거나, 영업시간이 아니거나, 휴일인경우) -> 진료를 요청할 수 없습니다.
        2. __*진료 희망 시간(request_at)*__이 과거의 시간인 경우 -> 진료를 요청할 수 없습니다.
    """
    user = get_object_or_404(User, id=request.auth.id)
    doctor = get_object_or_404(Doctor, id=payload.doctor_id)
    if user.role != "PATIENT":
        return HTTPStatus.FORBIDDEN, {
            "message": f"username {user.username} is not a patient user"
        }

    if payload.request_at < timezone.now():
        return HTTPStatus.FORBIDDEN, {
            "message": "can not request a time in the past"
        }

    expired_at = calc_diagnosis_expired_time(doctor, created_at=timezone.now(), request_at=payload.request_at)
    if expired_at is False:
        return HTTPStatus.FORBIDDEN, {
            "message": f"the hours entered are not business hours."
        }

    diagnosis_request = DiagnosisRequest(
        user=user,
        doctor_id=payload.doctor_id,
        request_at=payload.request_at,
        request_expired_at=expired_at
    )

    diagnosis_request.save()

    res = schemas.DiagnosisRequestRes(
        id=diagnosis_request.id,
        patient_name=diagnosis_request.user.nickname,
        doctor_name=diagnosis_request.doctor.name,
        request_at=diagnosis_request.request_at,
        request_expired_at=diagnosis_request.request_expired_at,
    )

    return HTTPStatus.OK, res


@diagnosis_request_controller.get("", auth=AuthBearer(), response={
    200: schemas.PaginatedDiagnosisRequestRes,
    403: MessageOut,
})
def list_diagnosis_requests(request, per_page: int = 10, page: int = 1):
    """
    <h2> 진료 요청 리스트 확인 API (의사 전용 API) </h2>
    auth_user_role: DOCTOR </br>
    |param|description|type|example|
    |-----|-----------|----|-------|
    |per_page|__*(query param)*__ 한 페이지에 몇개의 응답값을 받을지 (기본값=10)|int|10 or null|
    |page|__*(query param)*__ 몇 페이지를 쿼리할지 (기본값=1)|int|10 or null|
    ----
    - 다음의 진료 요청 건은 리스트에 표시되지 않습니다.
        1. 이미 승낙된 진료 요청
        2. 진료 요청 만료 시간이 지금 시간(UTC기준) 보다 빠른 요청
        3. 진료 희망 시간이 지금 시간(UTC기준) 보다 빠른 요청
    """
    user = get_object_or_404(User, id=request.auth.id)
    if user.role != "DOCTOR":
        return HTTPStatus.FORBIDDEN, {
            "message": f"username {user.username} is not a doctor user"
        }

    res = DiagnosisRequest.objects.filter(
        Q(doctor__user_id=user.id) & Q(is_approved=False)
        & Q(request_expired_at__gte=timezone.now()) & Q(request_at__gte=timezone.now())
    ).all()
    paginated_response = pr(res, map_diagnosis_request, schemas.PaginatedDiagnosisRequestRes)
    return HTTPStatus.OK, paginated_response


@diagnosis_request_controller.post("/{request_id}/approve", auth=AuthBearer(), response={
    200: schemas.DiagnosisRequestRes,
    403: MessageOut,
})
def approve_diagnosis_request(request, request_id: int):
    """
    <h2> 진료 요청 승낙 API (의사 전용 API) </h2>
    auth_user_role: DOCTOR </br>
    |param|description|type|example|
    |-----|-----------|----|-------|
    |request_id|__*(path param)*__ 승낙할 진료 요청 id|int|1|
    -----
    - 진료 요청 승낙은 다음의 규칙을 따릅니다.
        1. 이미 승낙된 진료 요청은 승낙할 수 없습니다.
        2. 진료 희망 시간이 지금 시간(UTC기준)보다 빠를 경우, 즉 이미 진료 희망 시간이 지나간 경우 승낙할 수 없습니다.
        3. 진료 요청 만료 시간이 지금 시간(UTC기준)보다 빠를 경우, 즉 진료 요청 만료 시간이 지나간 경우 승낙할 수 없습니다.
    """
    now = timezone.now()
    user = get_object_or_404(User, id=request.auth.id)
    if user.role != "DOCTOR":
        return HTTPStatus.FORBIDDEN, {
            "message": f"username {user.username} is not a doctor user"
        }

    diagnosis_request = get_object_or_404(DiagnosisRequest, id=request_id)
    if diagnosis_request.is_approved:
        return HTTPStatus.FORBIDDEN, {
            "message": "diagnosis request already approved"
        }

    if diagnosis_request.request_at < now:
        return HTTPStatus.FORBIDDEN, {
            "message": "diagnosis request time already passed"
        }
    if diagnosis_request.request_expired_at < now:
        return HTTPStatus.FORBIDDEN, {
            "message": "diagnosis request already expired"
        }

    diagnosis_request.is_approved = True
    diagnosis_request.save()
    return HTTPStatus.OK, map_diagnosis_request(diagnosis_request)
