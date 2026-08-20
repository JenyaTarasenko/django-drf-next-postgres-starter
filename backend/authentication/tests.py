from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(APITestCase):
    """Authentication endpoint tests."""

    def setUp(self):
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.refresh_url = "/api/auth/refresh/"
        self.profile_url = "/api/auth/profile/"

    # ---------- REGISTER ----------
    def test_register_success(self):
        """Успешная регистрация."""
        data = {
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "testpassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.username, "testuser1")
        self.assertEqual(user.email, "test1@example.com")

    def test_register_missing_fields(self):
        """Регистрация с отсутствующими обязательными данными."""
        data = {"username": "testuser2"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Регистрация с уже существующим username."""
        User.objects.create_user(
            username="testuser3", email="dup3@example.com", password="pass321"
        )
        data = {"username": "testuser3", "email": "unique3@example.com", "password": "pass321"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_register_duplicate_email(self):
        """Регистрация с уже существующим email."""
        User.objects.create_user(
            username="unique4", email="dup4@example.com", password="pass321"
        )
        data = {"username": "unique5", "email": "dup4@example.com", "password": "pass321"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    # ---------- LOGIN ----------
    def test_login_success(self):
        """Успешный login с правильными credentials."""
        User.objects.create_user(
            username="loginuser", email="login@example.com", password="secret123"
        )
        data = {"username": "loginuser", "password": "secret123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_login_wrong_password(self):
        """Login с неправильным password."""
        User.objects.create_user(
            username="loginuser2", email="login2@example.com", password="secret123"
        )
        data = {"username": "loginuser2", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_login_nonexistent_user(self):
        """Login с несуществующим пользователем."""
        data = {"username": "nonexistent", "password": "anypass"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_access_token_cookie(self):
        """Проверить наличие access_token cookie после login."""
        User.objects.create_user(
            username="loginuser3", email="login3@example.com", password="secret123"
        )
        data = {"username": "loginuser3", "password": "secret123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertTrue(
            "access_token" in response.cookies,
            "access_token cookie should be set",
        )
        self.assertTrue(
            response.cookies["access_token"].get("httponly"),
            "access_token should be HttpOnly",
        )

    def test_login_refresh_token_cookie(self):
        """Проверить наличие refresh_token cookie после login."""
        User.objects.create_user(
            username="loginuser4", email="login4@example.com", password="secret123"
        )
        data = {"username": "loginuser4", "password": "secret123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertTrue(
            "refresh_token" in response.cookies,
            "refresh_token cookie should be set",
        )
        self.assertTrue(
            response.cookies["refresh_token"].get("httponly"),
            "refresh_token should be HttpOnly",
        )

    def test_login_cookie_attributes(self):
        """Проверить основные cookie attributes."""
        User.objects.create_user(
            username="loginuser5", email="login5@example.com", password="secret123"
        )
        data = {"username": "loginuser5", "password": "secret123"}
        response = self.client.post(self.login_url, data, format="json")
        access_cookie = response.cookies.get("access_token", None)
        refresh_cookie = response.cookies.get("refresh_token", None)
        self.assertIsNotNone(access_cookie, "access_token cookie should exist")
        self.assertIsNotNone(refresh_cookie, "refresh_token cookie should exist")
        self.assertEqual(access_cookie["samesite"], "Lax")
        self.assertEqual(refresh_cookie["samesite"], "Lax")

    # ---------- REFRESH ----------
    def test_refresh_valid_token(self):
        """Refresh с валидным refresh_token cookie."""
        user = User.objects.create_user(
            username="refreshuser", email="refresh@example.com", password="secret123"
        )
        # Сначала логин для получения refresh_token
        login_data = {"username": "refreshuser", "password": "secret123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        self.assertTrue(
            "refresh_token" in login_response.cookies,
            "refresh_token should be set during login",
        )

        # Теперь делаем refresh
        refresh_response = self.client.post(self.refresh_url, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", refresh_response.data)

    def test_refresh_no_token(self):
        """Refresh без refresh_token."""
        # Убедимся, что cookies очищены
        self.client.cookies = {}
        refresh_response = self.client.post(self.refresh_url, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(refresh_response.data["detail"], "Refresh token not found")

    def test_refresh_invalid_token(self):
        """Refresh с невалидным refresh_token."""
        # Устанавливаем невалидный токен в cookie
        self.client.cookies["refresh_token"] = "invalidtoken123"
        refresh_response = self.client.post(self.refresh_url, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- PROFILE ----------
    def test_profile_no_token(self):
        """Запрос без access token → должен быть 401."""
        response = self.client.get(self.profile_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_with_valid_token(self):
        """Запрос с валидным access token cookie → должен быть 200."""
        user = User.objects.create_user(
            username="profileuser", email="profile@example.com", password="secret123"
        )
        # Логин для установки cookies
        login_data = {"username": "profileuser", "password": "secret123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Делаем запрос профиля - cookies должны отправиться автоматически
        profile_response = self.client.get(self.profile_url, format="json")
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertIn("id", profile_response.data)
        self.assertIn("username", profile_response.data)
        self.assertIn("email", profile_response.data)
        self.assertEqual(profile_response.data["username"], "profileuser")

    def test_profile_invalid_token(self):
        """Запрос с невалидным access token → должен быть 401."""
        # Устанавливаем невалидный токен
        self.client.cookies["access_token"] = "invalidtoken123"
        response = self.client.get(self.profile_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_user_data(self):
        """Проверить, что возвращаются данные правильного пользователя."""
        user = User.objects.create_user(
            username="datac user", email="data@example.com", password="secret123"
        )
        login_data = {"username": "datac user", "password": "secret123"}
        login_response = self.client.post(self.login_url, login_data, format="json")

        profile_response = self.client.get(self.profile_url, format="json")
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["username"], "datac user")
        self.assertEqual(profile_response.data["email"], "data@example.com")
        self.assertEqual(profile_response.data["id"], user.id)