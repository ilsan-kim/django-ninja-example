from datetime import timedelta

from django.test import TestCase, Client
from django.utils import timezone

from account.models import User
from healthcare.models import Doctor, WorkingDay, DiagnosisRequest
from healthcare.tests.doctor_test_data import SCHEMA_LIST_OF_REGISTER_DOCTORS
from healthcare.utils import get_weekday_from_datetime


class DiagnosisRequestTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(
            username="test_patient",
            password="test_pw",
            role="PATIENT",
            nickname="test_patient"
        )
        patient_data = {"username": "test_patient", "password": "test_pw"}
        patient_login_resp = self.client.post("/api/auth/login", data=patient_data, content_type="application/json")
        patient_login_body = patient_login_resp.json()
        self.patient_token = patient_login_body.get("token").get("access_token")
        self.patient_header = {
            "HTTP_Authorization": f"Bearer {self.patient_token}"
        }

        self.doctor_user: User = User.objects.create_user(
            username="test_doctor",
            password="test_pw",
            role="DOCTOR",
            nickname="test_doctor"
        )
        doctor = Doctor(
            user=self.doctor_user, name="test_doctor", hospital_name="test_hospital", department="1234", non_paid_object="탈모약"
        )
        doctor._workingday_set = [
            WorkingDay(
                is_workingday=working_day.is_workingday,
                doctor=doctor, day=working_day.day,
                work_start_time=working_day.work_start_time,
                work_end_time=working_day.work_end_time,
                break_start_time=working_day.break_start_time,
                break_end_time=working_day.break_end_time,
            ) for working_day in SCHEMA_LIST_OF_REGISTER_DOCTORS
        ]
        doctor.save()
        doctor_data = {"username": "test_doctor", "password": "test_pw"}
        doctor_login_resp = self.client.post("/api/auth/login", data=doctor_data, content_type="application/json")
        doctor_login_body = doctor_login_resp.json()
        self.doctor_token = doctor_login_body.get("token").get("access_token")
        self.doctor_header = {
            "HTTP_Authorization": f"Bearer {self.doctor_token}"
        }

        self.doctor: Doctor = doctor

    def test_request_diagnosis_request(self):
        # today_time = timezone.now().time()
        # test_day = get_weekday_from_datetime(timezone.now())
        # today_working_day = list(filter(lambda x: x.day == test_day, self.doctor.workingday_set.all()))[0]

        # 휴일
        request_1 = {"request_at": "2023-08-19T14:30:00Z", "doctor_id": self.doctor.id}
        request_1_resp = self.client.post(
            "/api/diagnosis-request/request", data=request_1, content_type="application/json", **self.patient_header
        )
        self.assertEqual(request_1_resp.status_code, 403)

        # 영업시간 외
        request_2 = {"request_at": "2023-08-18T08:00:00Z", "doctor_id": self.doctor.id}
        request_2_resp = self.client.post(
            "/api/diagnosis-request/request", data=request_2, content_type="application/json", **self.patient_header
        )
        self.assertEqual(request_2_resp.status_code, 403)

        # 휴식시간
        request_3 = {"request_at": "2023-08-18T12:30:00Z", "doctor_id": self.doctor.id}
        request_3_resp = self.client.post(
            "/api/diagnosis-request/request", data=request_3, content_type="application/json", **self.patient_header
        )
        self.assertEqual(request_3_resp.status_code, 403)

        # 정상
        request_4 = {"request_at": "2023-08-18T14:00:00Z", "doctor_id": self.doctor.id}
        request_4_resp = self.client.post(
            "/api/diagnosis-request/request", data=request_4, content_type="application/json", **self.patient_header
        )
        request_4_body = request_4_resp.json()
        self.assertEqual(request_4_resp.status_code, 200)
        self.assertEqual(request_4_body.get("request_at"), "2023-08-18T14:00:00Z")

    def test_list_diagnosis_request(self):
        success_request_at = "2023-08-18T14:00:00Z"

        # success request
        diagnosis_request_1 = DiagnosisRequest(
            user=self.patient, doctor_id=self.doctor.id,
            request_at=success_request_at, request_expired_at="2099-01-01T00:00:00Z"
        )
        diagnosis_request_1.save()

        # success request
        diagnosis_request_2 = DiagnosisRequest(
            user=self.patient, doctor_id=self.doctor.id,
            request_at=success_request_at, request_expired_at="2099-01-01T00:00:00Z"
        )
        diagnosis_request_2.save()

        # expired request
        diagnosis_request_3 = DiagnosisRequest(
            user=self.patient, doctor_id=self.doctor.id,
            request_at=success_request_at, request_expired_at=timezone.now() - timedelta(hours=24)
        )
        diagnosis_request_3.save()

        # approved request
        diagnosis_request_4 = DiagnosisRequest(
            user=self.patient, doctor_id=self.doctor.id,
            request_at=success_request_at, request_expired_at="2099-01-01T00:00:00Z", is_approved=True
        )
        diagnosis_request_4.save()

        resp = self.client.get("/api/diagnosis-request", **self.doctor_header)
        body = resp.json()
        self.assertEqual(len(body.get("data")), 2)

    def test_approve_diagnosis_request(self):
        success_request_at = "2023-08-18T14:00:00Z"

        # 승낙 가능
        available_request = DiagnosisRequest(
            user=self.patient, doctor_id=self.doctor.id,
            request_at=success_request_at, request_expired_at="2099-01-01T00:00:00Z"
        )
        available_request.save()
        available_request_resp = self.client.post(
            f"/api/diagnosis-request/{available_request.id}/approve", **self.doctor_header
        )
        self.assertEqual(available_request_resp.status_code, 200)

        # 이미 승낙됨
        already_approved = DiagnosisRequest(
            user=self.patient, doctor_id=self.doctor.id,
            request_at=success_request_at, request_expired_at="2099-01-01T00:00:00Z", is_approved=True
        )
        already_approved.save()
        already_approved_resp = self.client.post(
            f"/api/diagnosis-request/{already_approved.id}/approve", **self.doctor_header
        )
        self.assertEqual(already_approved_resp.status_code, 403)

        # 희망 진료 시간 지남
        passed_request = DiagnosisRequest(
            user=self.patient, doctor_id=self.doctor.id,
            request_at=timezone.now() - timedelta(hours=1), request_expired_at="2099-01-01T00:00:00Z",
        )
        passed_request.save()
        passed_request_resp = self.client.post(
            f"/api/diagnosis-request/{passed_request.id}/approve", **self.doctor_header
        )
        self.assertEqual(passed_request_resp.status_code, 403)

        # 승낙 제한 시간 지남
        expired_request = DiagnosisRequest(
            user=self.patient, doctor_id=self.doctor.id,
            request_at=success_request_at, request_expired_at=timezone.now() - timedelta(hours=1), is_approved=True
        )
        expired_request.save()
        expired_request_resp = self.client.post(
            f"/api/diagnosis-request/{expired_request.id}/approve", **self.doctor_header
        )
        self.assertEqual(expired_request_resp.status_code, 403)
