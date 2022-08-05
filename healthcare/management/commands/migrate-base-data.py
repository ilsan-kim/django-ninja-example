import json

from django.core.management.base import BaseCommand

from account.models import User
from healthcare.models import Doctor, WorkingDay


class Command(BaseCommand):
    help = "Migrate base data for account & healthcare apps"

    def handle(self, *args, **options):
        user_data_path = "./migrate_data/user_data.json"
        doctor_data_path = "./migrate_data/doctor_data.json"
        workingday_data_path = "./migrate_data/workingday_data.json"

        with open(user_data_path, "r", encoding="utf-8") as file:
            user_data = json.load(file)

        with open(doctor_data_path, "r", encoding="utf-8") as file:
            doctor_data = json.load(file)

        with open(workingday_data_path, "r", encoding="utf-8") as file:
            workingday_data = json.load(file)

        # migrate user data >>>
        for user_json in user_data:
            try:
                User.objects.create_user(
                    id=user_json.get("id"),
                    username=user_json.get("username"),
                    password=user_json.get("password"),
                    nickname=user_json.get("nickname"),
                    role=user_json.get("role"),
                )
            except Exception as e:
                print(e)

        # migrate doctor data >>>
        for doctor_json in doctor_data:
            doctor = Doctor(
                id=doctor_json.get("id"),
                user_id=doctor_json.get("user_id"),
                name=doctor_json.get("name"),
                hospital_name=doctor_json.get("hospital_name"),
                department=doctor_json.get("department"),
                non_paid_object=doctor_json.get("non_paid_object"),
                is_approved=doctor_json.get("is_approved"),
            )
            doctor._workingday_set = [
                WorkingDay(
                    is_workingday=workingday.get("is_workingday"),
                    doctor_id=doctor.id,
                    day=workingday.get("day"),
                    work_start_time=workingday.get("work_start_time"),
                    work_end_time=workingday.get("work_end_time"),
                    break_start_time=workingday.get("break_start_time"),
                    break_end_time=workingday.get("break_end_time")
                ) for workingday in workingday_data if workingday.get("doctor_id") == doctor.id
            ]
            try:
                doctor.save()
            except Exception as e:
                print(e)

        print("data migration done")
