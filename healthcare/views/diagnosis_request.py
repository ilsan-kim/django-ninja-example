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
    <h2>:param time: 2022-01-15T09:00:00Z</h2>
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
    user = get_object_or_404(User, id=request.auth.id)
    if user.role != "DOCTOR":
        return HTTPStatus.FORBIDDEN, {
            "message": f"username {user.username} is not a doctor user"
        }

    res = DiagnosisRequest.objects.filter(
        Q(doctor__user_id=user.id) & Q(is_approved=False)
        & Q(request_expired_at__gte=timezone.now()) & Q(request_at__gte=datetime.datetime.now())
    ).all()
    paginated_response = pr(res, map_diagnosis_request, schemas.PaginatedDiagnosisRequestRes)
    return HTTPStatus.OK, paginated_response


@diagnosis_request_controller.post("/{request_id}/approve", auth=AuthBearer(), response={
    200: schemas.DiagnosisRequestRes,
    403: MessageOut,
})
def approve_diagnosis_request(request, request_id: int):
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
