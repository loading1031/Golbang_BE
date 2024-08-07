'''
MVP demo ver 0.0.8
2024.08.02
events/urls.py

역할: participant 앱 내의 URL API 엔드포인트 설정
현재 기능: 이벤트 수정
'''
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParticipantViewSet

# end point: api/v1/participants
router = DefaultRouter()
router.register(r'', ParticipantViewSet,'participants')

urlpatterns = [
    path('', include(router.urls)),
]