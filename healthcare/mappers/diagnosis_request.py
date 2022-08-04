from healthcare import models, schemas


def map_diagnosis_request(entity: models.DiagnosisRequest) -> schemas.DiagnosisRequestRes:
    return schemas.DiagnosisRequestRes(
        id=entity.id,
        patient_name=entity.user.nickname,
        doctor_name=entity.doctor.name,
        request_at=entity.request_at,
        request_expired_at=entity.request_expired_at,
    )
