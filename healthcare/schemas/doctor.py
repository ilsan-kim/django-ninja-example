from enum import Enum
from typing import List, Optional
from datetime import time

from ninja import Schema
from pydantic import validator

from config.utils.schemas import Paginated


# Day of week Enum Class
class DayEnum(str, Enum):
    Monday = "MON"
    Tuesday = "TUE"
    Wednesday = "WED"
    Thursday = "THU"
    Friday = "FRI"
    Saturday = "SAT"
    Sunday = "SUN"


# WorkingDay class
class WorkingDay(Schema):
    is_workingday: bool = True
    day: DayEnum
    work_start_time: time = "09:00"
    work_end_time: time = "17:00"
    break_start_time: Optional[time] = "00:00"
    break_end_time: Optional[time] = "00:00"


# Doctor base class
class DoctorBase(Schema):
    hospital_name: str = "리버풀병원"
    name: str = "헨더슨"
    department: str = "1234"
    non_paid_object: Optional[str]
    working_days: List[WorkingDay]


# Response of doctor
class DoctorRes(DoctorBase):
    id: int


# Request of register doctor
class DoctorRegisterReq(DoctorBase):
    @validator("department")
    def validate_department(cls, v):
        if len(v) >= 5:
            raise ValueError("error on department code / now only support 4 departments")
        for code in v:
            if int(code) >= 5:
                raise ValueError("error on department code / not supported code")
        return v

    @validator("working_days")
    def validate_working_days(cls, v):
        weekday_map = {"MON": True, "TUE": True, "WED": True, "THU": True, "FRI": True, "SAT": True, "SUN": True}
        for x in v:
            try:
                del weekday_map[x.day.value]
            except KeyError:
                continue
        if len(weekday_map) != 0:
            raise ValueError("entered value of working days not suitable")

        if len(v) != 7:
            raise ValueError("length of working_days must to be 7")

        return v


# Response of paginated doctor
class PaginatedDoctorResp(Paginated):
    data: List[DoctorRes]
