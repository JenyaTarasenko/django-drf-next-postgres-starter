# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ItemViewSet  

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')  # регистрируем ViewSet

# /api/items/ → список
# /api/items/<id>/ → детальная страница

urlpatterns = [
    path('', include(router.urls)),  # подключаем все маршруты из ViewSet
]