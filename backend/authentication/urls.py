# pyrefly: ignore [missing-import]
from django.urls import path
from .views import CookieTokenObtainPairView, CookieTokenRefreshView,ProfileView,RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view()),#регистрация
    path("login/", CookieTokenObtainPairView.as_view()),#логин
    path("refresh/", CookieTokenRefreshView.as_view()),#обновление токена
    path("profile/", ProfileView.as_view()),#профиль
]