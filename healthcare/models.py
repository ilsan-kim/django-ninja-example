import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Doctor(models.Model):
    user = models.ForeignKey(User, related_name="doctor", on_delete=models.CASCADE, unique=True)
    name = models.CharField(max_length=32)
    hospital_name = models.CharField(max_length=128)
    department = models.CharField(max_length=4)
    non_paid_object = models.CharField(max_length=64, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    @classmethod
    def already_registered(cls, user_id: int) -> bool:
        doctor = cls.objects.filter(user__id=user_id).first()
        if doctor is not None:
            return True
        return False

    def save(self, *args, **kwargs):
        super(Doctor, self).save(*args, **kwargs)
        for working_day in self._workingday_set:
            working_day.save()


class WorkingDay(models.Model):
    # enum fields
    DAY = (
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday"),
    )

    day = models.CharField(choices=DAY, max_length=3)
    is_workingday = models.BooleanField(default=True)
    work_start_time = models.TimeField(default="09:00")
    work_end_time = models.TimeField(default="17:00")
    break_start_time = models.TimeField(default="00:00")
    break_end_time = models.TimeField(default="00:00")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.is_workingday is False:
            self.work_start_time = "00:00"
            self.work_end_time = "00:00"
            self.break_start_time = "00:00"
            self.break_end_time = "00:00"
        super(WorkingDay, self).save(*args, **kwargs)


class DiagnosisRequest(models.Model):
    user = models.ForeignKey(User, related_name="diagnosis", on_delete=models.CASCADE, unique=False)
    doctor = models.ForeignKey(Doctor, related_name="diagnosis", on_delete=models.CASCADE, unique=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    request_at = models.DateTimeField()
    request_expired_at = models.DateTimeField()
