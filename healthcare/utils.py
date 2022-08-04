from typing import List, Union
from datetime import datetime, timedelta, time

from healthcare.models import Doctor, WorkingDay


def get_weekday_from_datetime(dt: datetime) -> str:
    weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    dt_weekday = dt.weekday()
    return weekdays[dt_weekday]


# TODO: refactor
def calc_diagnosis_expired_time(doctor: Doctor, created_at: datetime, request_at: datetime) -> Union[datetime, bool]:
    working_days: List[WorkingDay] = doctor.workingday_set.all()

    request_weekday = get_weekday_from_datetime(request_at)
    request_working_day = list(filter(lambda x: x.day == request_weekday, working_days))[0]

    created_weekday = get_weekday_from_datetime(created_at)
    created_working_day = list(filter(lambda x: x.day == created_weekday, working_days))[0]

    # 입력된 "진료희망시간" 이 영업시간이 아닐 때
    if request_working_day.work_start_time > request_at.time() \
            or request_working_day.work_end_time < request_at.time() \
            or request_working_day.is_workingday is False:
        return False

    # 입력된 "진료희망시간" 이 휴식시간일 때
    if request_working_day.break_start_time < request_at.time() < request_working_day.break_end_time:
        return False

    # 입력된 "진료요청시간" 이 영업시간 전
    if created_working_day.work_start_time > created_at.time() and created_working_day.is_workingday:
        expired_time: time = created_working_day.work_start_time
        break_end_datetime = created_at.replace(
            hour=expired_time.hour,
            minute=expired_time.minute,
            second=expired_time.second,
            microsecond=expired_time.microsecond,
        )
        expired_at = break_end_datetime + timedelta(minutes=15)
        return expired_at

    # 입력된 "진료요청시간" 이 영업시간 후 거나 영업일이 아닐때-> 다음의 가장 빠른 영업시간을 찾아야함
    if created_working_day.work_end_time < created_at.time() or created_working_day.is_workingday is False:
        available_datetime, expired_time = __get_available_working_time(created_at, working_days)
        break_end_datetime = available_datetime.replace(
            hour=expired_time.hour,
            minute=expired_time.minute,
            second=expired_time.second,
            microsecond=expired_time.microsecond,
        )
        expired_at = break_end_datetime + timedelta(minutes=15)
        return expired_at

    # 입력된 "진료요청시간" 이 휴식시간일 때
    if created_working_day.break_start_time < created_at.time() < created_working_day.break_end_time:
        expired_time: time = created_working_day.break_end_time
        break_end_datetime = created_at.replace(
            hour=expired_time.hour,
            minute=expired_time.minute,
            second=expired_time.second,
            microsecond=expired_time.microsecond,
        )
        expired_at = break_end_datetime + timedelta(minutes=15)
        return expired_at

    return created_at + timedelta(minutes=20)


def __get_available_working_time(target_datetime: datetime, working_days: List[WorkingDay]) -> (datetime, time):
    is_working_day = False
    while is_working_day is False:
        target_weekday = get_weekday_from_datetime(target_datetime)
        target_working_day = list(filter(lambda x: x.day == target_weekday, working_days))[0]
        is_working_day = target_working_day.is_workingday
        if is_working_day is False:
            target_datetime = target_datetime + timedelta(hours=24)

    available_datetime = target_datetime

    # now target_time is available working_day // let's return available day's work start time
    available_weekday = get_weekday_from_datetime(target_datetime)
    available_working_day = list(filter(lambda x: x.day == available_weekday, working_days))[0]
    return available_datetime, available_working_day.work_start_time
