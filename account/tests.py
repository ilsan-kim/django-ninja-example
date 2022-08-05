from django.test import TestCase, Client

from config.utils.permissions import get_current_user
from account.models import User


# Create your tests here.
class AuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test_user",
            password="test_pw",
            role="PATIENT",
            nickname="test_nickname",
        )

    def test_register_success(self):
        data = {
            "username": "success_name",
            "password": "success_pw",
            "role": "PATIENT",
            "nickname": "success_nickname",
        }
        response = self.client.post("/api/auth/register", data=data, content_type="application/json")
        user_model = User.objects.filter(username="success_name").first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_model.username, "success_name")
        self.assertEqual(user_model.role, "PATIENT")
        self.assertEqual(user_model.nickname, "success_nickname")

    # failed by User.already_registered()
    def test_register_failed(self):
        data = {
            "username": "test_user",
            "password": "test_pw",
            "role": "PATIENT",
            "nickname": "test_nickname"
        }
        response = self.client.post("/api/auth/register", data=data, content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_login(self):
        data = {
            "username": "test_user",
            "password": "test_pw"
        }
        response = self.client.post("/api/auth/login", data=data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        res_body = response.json()
        token = res_body.get("token").get("access_token")
        user = get_current_user(token)
        self.assertEqual(user.username, "test_user")
        self.assertEqual(user.nickname, "test_nickname")
        self.assertEqual(user.role, "PATIENT")
