import math
import random

from django.test import TestCase, Client

from account.models import User
from healthcare.models import Doctor, WorkingDay
from healthcare.tests.doctor_test_data import (
    REGISTER_SUCCESS, REGISTER_FAILED_BY_TIME_ERROR, REGISTER_FAILED_BY_DEPARTMENT_CODE_ERROR,
    REGISTER_FAILED_BY_DEPARTMENT_LENGTH_ERROR, REGISTER_FAILED_BY_WORKINGDAY_LENGTH_ERROR,
    REGISTER_FAILED_BY_WORKINGDAY_DAY_ERROR, SCHEMA_LIST_OF_REGISTER_DOCTORS
)


class DoctorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test_user",
            password="test_pw",
            role="DOCTOR",
            nickname="test_nickname",
        )

        user_data = {"username": "test_user", "password": "test_pw"}
        login_resp = self.client.post("/api/auth/login", data=user_data, content_type="application/json")
        login_body = login_resp.json()
        token = login_body.get("token").get("access_token")
        self.token = token
        self.login_header = {
            "HTTP_Authorization": f"Bearer {token}"
        }

    def test_register_doctor_success(self):
        data = REGISTER_SUCCESS
        response = self.client.post(
            "/api/doctor/register", data=data, content_type="application/json", **self.login_header
        )
        self.assertEqual(response.status_code, 200)

    def test_register_doctor_failed_by_time_error(self):
        data = REGISTER_FAILED_BY_TIME_ERROR
        response = self.client.post(
            "/api/doctor/register", data=data, content_type="application/json", **self.login_header
        )
        error_msg = response.json().get("detail")[0].get("msg")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(error_msg, "invalid time format")

    def test_register_doctor_failed_by_dep_code_error(self):
        data = REGISTER_FAILED_BY_DEPARTMENT_CODE_ERROR
        response = self.client.post(
            "/api/doctor/register", data=data, content_type="application/json", **self.login_header
        )
        error_msg = response.json().get("detail")[0].get("msg")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(error_msg, "error on department code / not supported code")

    def test_register_doctor_failed_by_dep_length_error(self):
        data = REGISTER_FAILED_BY_DEPARTMENT_LENGTH_ERROR
        response = self.client.post(
            "/api/doctor/register", data=data, content_type="application/json", **self.login_header
        )
        error_msg = response.json().get("detail")[0].get("msg")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(error_msg, "error on department code / now only support 4 departments")

    def test_register_doctor_failed_by_workingday_length_error(self):
        data = REGISTER_FAILED_BY_WORKINGDAY_LENGTH_ERROR
        response = self.client.post(
            "/api/doctor/register", data=data, content_type="application/json", **self.login_header
        )
        error_msg = response.json().get("detail")[0].get("msg")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(error_msg, "length of working_days must to be 7")

    def test_register_doctor_failed_by_workingday_day_error(self):
        data = REGISTER_FAILED_BY_WORKINGDAY_DAY_ERROR
        response = self.client.post(
            "/api/doctor/register", data=data, content_type="application/json", **self.login_header
        )
        error_msg = response.json().get("detail")[0].get("msg")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(error_msg, "entered value of working days not suitable")

    def test_list_doctors(self):
        num_doctors = 24
        DoctorTest.__gen_nums_of_doctors(num_doctors)
        response = self.client.get("/api/doctor")
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get("total_count"), num_doctors)
        self.assertEqual(body.get("page_count"), math.ceil(num_doctors/10))
        self.assertEqual(len(body.get("data")), 10)

    def test_list_doctors_with_query(self):
        num_doctors = 24
        q1, q2 = "정형외과", "1"
        DoctorTest.__gen_nums_of_doctors(num_doctors)
        response = self.client.get(f"/api/doctor?q={q1} {q2}")
        body = response.json()
        data_list = body.get("data")
        for data in data_list:
            self.assertEqual(
                ((f"{q1}" in data.get("department")) | (f"{q1}" in data.get("non_paid_object"))), True)
            self.assertEqual(
                ((f"{q2}" in data.get("hospital_name")) | (f"{q2}" in data.get("name"))), True
            )

    def test_list_doctors_with_time(self):
        num_doctors = 24
        DoctorTest.__gen_nums_of_doctors(num_doctors)
        # 휴식시간
        time1 = "2022-08-18T12:30:00"
        response1 = self.client.get(f"/api/doctor?time={time1}")
        body1 = response1.json()
        total_count1 = body1.get("total_count")

        # 업무시간
        time2 = "2022-08-18T14:30:00"
        response2 = self.client.get(f"/api/doctor?time={time2}")
        body2 = response2.json()
        total_count2 = body2.get("total_count")

        # 휴일
        time3 = "2023-08-19T14:30:00"
        response3 = self.client.get(f"/api/doctor?time={time3}")
        body3 = response3.json()
        total_count3 = body3.get("total_count")

        self.assertEqual(total_count1, 0)
        self.assertEqual(total_count2, num_doctors)
        self.assertEqual(total_count3, 0)

    @staticmethod
    def __gen_nums_of_doctors(num: int):
        non_paid_objects = ["탈모약", "다이어트약"]
        for i in range(num):
            v = f"{i}"
            user = User.objects.create_user(username=v, password=v, role="DOCTOR", nickname=v)
            doctor = Doctor(
                user=user, name=f"doctor_{v}", hospital_name=f"hospital_{v}",
                department=DoctorTest.__gen_rand_dep_codes(), non_paid_object=random.choice(non_paid_objects)
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

    @staticmethod
    def __gen_rand_dep_codes():
        a = ["0", "1", "2", "3", "4"]
        t = ""
        for i in range(4):
            t += random.choice(a)
        return t
