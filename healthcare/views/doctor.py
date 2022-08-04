import datetime
import operator
from http import HTTPStatus
from functools import reduce

from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q

from config.utils.permissions import AuthBearer
from config.utils.schemas import MessageOut
from config.utils.utils import paginated_response as pr
from account.models import User
from healthcare.models import Doctor, WorkingDay
from healthcare.mappers.doctor import map_doctor
from healthcare import utils
from healthcare import schemas

doctor_controller = Router(tags=["doctor"])


@doctor_controller.post("/register", auth=AuthBearer(), response={
    200: schemas.DoctorRes,
    403: MessageOut,
    404: MessageOut,
})
def register(request, payload: schemas.DoctorRegisterReq):
    user = get_object_or_404(User, id=request.auth.id)
    # TODO: refactor to user.role
    if user.get_user_role() != "DOCTOR":
        return HTTPStatus.FORBIDDEN, {
            "message": f"username {user.username} is not a doctor user"
        }

    already_registered = Doctor.already_registered(user_id=user.pk)
    if already_registered:
        return HTTPStatus.FORBIDDEN, {
            "message": f"username {user.username} is already registered to doctor"
        }

    doctor = Doctor(
        user=user,
        name=payload.name,
        hospital_name=payload.hospital_name,
        department=payload.department,
        non_paid_object=payload.non_paid_object,
        is_approved=False
    )

    doctor._workingday_set = [
        WorkingDay(
            is_workingday=working_day.is_workingday,
            doctor=doctor,
            day=working_day.day,
            work_start_time=working_day.work_start_time,
            work_end_time=working_day.work_end_time,
            break_start_time=working_day.break_start_time,
            break_end_time=working_day.break_end_time,
        ) for working_day in payload.working_days
    ]

    doctor.save()

    return HTTPStatus.OK, map_doctor(doctor)


@doctor_controller.get("", auth=None, response={
    200: schemas.PaginatedDoctorResp,
    403: MessageOut,
})
def list_doctors(request, q: str = None, time: datetime.datetime = None, per_page: int = 10,
                 page: int = 1):
    """
    <h2>:param time: 2022-01-15T09:00:00Z</h2>
    """
    """
    QueryBuild 과정이 비효율적이다.
    정상적인 검색을 위해서 name, hospital_name, non_paid_object 에 모두 인덱스를 걸어야하는데 그럼 입력과정이 너무 무거워진다.
    요구사항에 부합하면서도 효율적인 검색 로직을 짜려면 reverse indexing을 지원하는 검색엔진을 도입해야한다.
    """
    base_query = Doctor.objects
    if q and time:
        return HTTPStatus.FORBIDDEN, {"message": "you can not use q and time at one request"}

    if q:
        queries = request.GET.get("q")
        query_list = queries.split(" ")

        query_target = []
        for query in query_list:
            if query == "정형외과":
                query_target.append(Q(department__contains="1"))
            elif query == "내과":
                query_target.append(Q(department__contains="2"))
            elif query == "한의사":
                query_target.append(Q(department__contains="3"))
            elif query == "일반의":
                query_target.append(Q(department__contains="4"))
            else:
                query_target.append(
                    Q(name__contains=query) | Q(hospital_name__contains=query) | Q(non_paid_object__contains=query)
                )

        base_query = base_query.filter(reduce(operator.and_, query_target))
    if time:
        target_time = time.time()
        weekday = utils.get_weekday_from_datetime(time)

        query_target = (
            Q(workingday__day=weekday) & Q(workingday__is_workingday=True)
            & Q(workingday__work_start_time__lte=target_time) & Q(workingday__work_end_time__gte=target_time)
            & (Q(workingday__break_start_time__gte=target_time) | Q(workingday__break_end_time__lte=target_time))
        )

        base_query = base_query.filter(query_target)

    res = base_query.all()

    paginated_response = pr(res, map_doctor, schemas.PaginatedDoctorResp)
    return HTTPStatus.OK, paginated_response
