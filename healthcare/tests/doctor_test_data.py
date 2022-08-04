from healthcare import schemas

REGISTER_SUCCESS = {
    "hospital_name": "김안과",
    "name": "피카츄",
    "department": "1111",
    "non_paid_object": "탈모약",
    "working_days": [
        {
            "is_workingday": True,
            "day": "MON",
            "work_start_time": "09:00",
            "work_end_time": "17:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "TUE",
            "work_start_time": "09:00",
            "work_end_time": "17:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "WED",
            "work_start_time": "09:00",
            "work_end_time": "17:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "THU",
            "work_start_time": "09:00",
            "work_end_time": "17:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "FRI",
            "work_start_time": "09:00",
            "work_end_time": "17:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SAT",
            "work_start_time": "09:00",
            "work_end_time": "17:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SUN",
            "work_start_time": "09:00",
            "work_end_time": "17:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        }
    ]
}

REGISTER_FAILED_BY_TIME_ERROR = {
    "hospital_name": "김안과",
    "name": "피카츄",
    "department": "1004",
    "non_paid_object": "탈모약",
    "working_days": [
        {
            "is_workingday": True,
            "day": "MON",
            "work_start_time": "09:00",
            "work_end_time": "25:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "TUE",
            "work_start_time": "09:00",
            "work_end_time": "25:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "WED",
            "work_start_time": "09:00",
            "work_end_time": "25:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "THU",
            "work_start_time": "09:00",
            "work_end_time": "25:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "FRI",
            "work_start_time": "09:00",
            "work_end_time": "25:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SAT",
            "work_start_time": "09:00",
            "work_end_time": "25:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SUN",
            "work_start_time": "09:00",
            "work_end_time": "25:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        }
    ]
}

REGISTER_FAILED_BY_DEPARTMENT_LENGTH_ERROR = {
    "hospital_name": "김안과",
    "name": "피카츄",
    "department": "12344",
    "non_paid_object": "탈모약",
    "working_days": [
        {
            "is_workingday": True,
            "day": "MON",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "TUE",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "WED",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "THU",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "FRI",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SAT",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SUN",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        }
    ]
}

REGISTER_FAILED_BY_DEPARTMENT_CODE_ERROR = {
    "hospital_name": "김안과",
    "name": "피카츄",
    "department": "5678",
    "non_paid_object": "탈모약",
    "working_days": [
        {
            "is_workingday": True,
            "day": "MON",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "TUE",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "WED",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "THU",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "FRI",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SAT",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SUN",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        }
    ]
}

REGISTER_FAILED_BY_WORKINGDAY_LENGTH_ERROR = {
    "hospital_name": "김안과",
    "name": "피카츄",
    "department": "1234",
    "non_paid_object": "탈모약",
    "working_days": [
        {
            "is_workingday": True,
            "day": "MON",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "TUE",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "WED",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "THU",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "FRI",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SAT",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SUN",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "MON",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        }
    ]
}

REGISTER_FAILED_BY_WORKINGDAY_DAY_ERROR = {
    "hospital_name": "김안과",
    "name": "피카츄",
    "department": "1234",
    "non_paid_object": "탈모약",
    "working_days": [
        {
            "is_workingday": True,
            "day": "MON",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "MON",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "WED",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "THU",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "FRI",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SAT",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        },
        {
            "is_workingday": True,
            "day": "SUN",
            "work_start_time": "09:00",
            "work_end_time": "23:00",
            "break_start_time": "12:00",
            "break_end_time": "13:00"
        }
    ]
}

SCHEMA_LIST_OF_REGISTER_DOCTORS = [
    schemas.WorkingDay(
        is_workingday=True, day="MON", work_start_time="09:00", work_end_time="23:00",
        break_start_time="12:00", break_end_time="13:00"
    ),
    schemas.WorkingDay(
        is_workingday=True, day="TUE", work_start_time="09:00", work_end_time="23:00",
        break_start_time="12:00", break_end_time="13:00"
    ),
    schemas.WorkingDay(
        is_workingday=True, day="WED", work_start_time="09:00", work_end_time="23:00",
        break_start_time="12:00", break_end_time="13:00"
    ),
    schemas.WorkingDay(
        is_workingday=True, day="THU", work_start_time="09:00", work_end_time="23:00",
        break_start_time="12:00", break_end_time="13:00"
    ),
    schemas.WorkingDay(
        is_workingday=True, day="FRI", work_start_time="09:00", work_end_time="23:00",
        break_start_time="12:00", break_end_time="13:00"
    ),
    schemas.WorkingDay(
        is_workingday=False, day="SAT", work_start_time="09:00", work_end_time="23:00",
        break_start_time="12:00", break_end_time="13:00"
    ),
    schemas.WorkingDay(
        is_workingday=False, day="SUN", work_start_time="09:00", work_end_time="23:00",
        break_start_time="12:00", break_end_time="13:00"
    ),
]