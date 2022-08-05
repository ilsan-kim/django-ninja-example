from healthcare import models, schemas

DEPARTMENT_MAP = {
    "1": "정형외과",
    "2": "내과",
    "3": "한의사",
    "4": "일반의",
}


def map_department(department_entity: str) -> str:
    department_entity = department_entity.replace("0", "")
    department_entity = list(set(department_entity))
    return ",".join([DEPARTMENT_MAP.get(char, "") for char in department_entity])


def map_working_day(entity: models.WorkingDay) -> schemas.WorkingDay:
    return schemas.WorkingDay(
        is_workingday=entity.is_workingday,
        day=schemas.DayEnum(entity.day),
        work_start_time=entity.work_start_time,
        work_end_time=entity.work_end_time,
        break_start_time=entity.break_start_time,
        break_end_time=entity.break_end_time,
    )


def map_doctor(entity: models.Doctor) -> schemas.DoctorRes:
    return schemas.DoctorRes(
        id=entity.id,
        name=entity.name,
        hospital_name=entity.hospital_name,
        department=map_department(entity.department),
        non_paid_object=entity.non_paid_object,
        is_approved=entity.is_approved,
        working_days=[map_working_day(working_day) for working_day in entity.workingday_set.all()]
    )
