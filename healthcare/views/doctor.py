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
    """
    <h2> 의사 등록 API (의사 전용 API) </h2>
    content-type: application/json </br>
    auth_user_role: DOCTOR </br>

    __입력 json 설명__ <br>
    |param|description|type|example|
    |-----|-----------|----|-------|
    |hospital_name|병원이름|string|"리버풀병원"|
    |name|의사이름|string|"조던헨더슨"|
    |department|진료코드 / 1: 정형외과, 2: 내과, 3: 한의사, 4: 일반의|string|정형외과,일반의 인경우 "14" </br> 정형외과,내과인 경우 "12" </br> 정형외과,내과,한의사,일반의인 경우 "1234"|
    |non_paid_object|비급여진료과목|optional[string]|"틸모약"|
    |working_days|업무시간|list[json]|후술|
    -----
    -----

    __working_days 입력 json 설명__ <br>
    |param|description|type|example|
    |-----|-----------|----|-------|
    |is_workingday|휴일 여부|boolean|true|
    |day|업무 요일|enum (string)|"MON" / "TUE" / "WED" / "THU" / "FRI" / "SAT" / "SUN"|
    |work_start_time|진료 시작 시간 (UTC기준)|string|"09:00"|
    |work_end_time|진료 종료 시간 (UTC기준)|string|"18:00"|
    |break_start_time|휴식 시작 시간 (UTC기준)|string|"12:00"|
    |break_end_time|휴식 종료 시간 (UTC기준)|string|"13:00"|
    -----
    -----

    - non_paid_object는 필수 파라미터가 아닙니다.
    - working_days: list[json] 은 다음의 규칙으로 입력되어야 합니다.
        1. 리스트는 일주일에 맞게 총 7개의 오브젝트를 포함해야합니다.
        2. 각 오브젝트의 "day" 파라미터는 ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"] 의 값이 각각 모두 들어가야 합니다.
            1. "MON"이 두번 들어가거나, "SUN"이 한번도 안들어가면 길이가 7이어도 validation을 통과하지 못합니다.
        3. is_workingday 가 false로 입력되는 경우, work_start_time, work_end_time, break_start_time, break_end_time 은 어떤값이 입력되는지와 상관없이 자동으로 00:00 으로 처리됩니다.
        4. 의사의 휴식시간이 없는 경우, break_start_time, break_end_time 은 "00:00"으로 입력해주세요.
    """
    user = get_object_or_404(User, id=request.auth.id)
    if user.role != "DOCTOR":
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
    <h2> 의사 리스트 확인 API </h2>
    |param|description|type|example|
    |-----|-----------|----|-------|
    |per_page|__*(query param)*__ 한 페이지에 몇개의 응답값을 받을지 (기본값=10)|int|10 or null|
    |page|__*(query param)*__ 몇 페이지를 쿼리할지 (기본값=1)|int|10 or null|
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
