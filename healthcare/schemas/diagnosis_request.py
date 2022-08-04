import datetime
from typing import List

from ninja import Schema

from config.utils.schemas import Paginated


# Request of create diagnosis request
class DiagnosisRequestReq(Schema):
    doctor_id: int
    request_at: datetime.datetime = "2022-01-15T09:00:00Z"


class DiagnosisRequestRes(Schema):
    id: int
    patient_name: str
    doctor_name: str
    request_at: datetime.datetime
    request_expired_at: datetime.datetime


class PaginatedDiagnosisRequestRes(Paginated):
    data: List[DiagnosisRequestRes]
