from django.db import models
from django.contrib.auth.models import UserManager, AbstractUser


# Create your models here.
class User(AbstractUser):
    # enum fields
    ROLE = (
        ("PATIENT", "Patient"),
        ("DOCTOR", "Doctor")
    )

    username = models.CharField(unique=True, max_length=128)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=32)
    role = models.CharField(choices=ROLE, default="PATIENT", max_length=32)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    @classmethod
    def already_registered(cls, username: str) -> bool:
        user = cls.objects.filter(username=username).first()
        if user is not None:
            return True
        return False

    def get_user_role(self) -> str:
        return self.role
