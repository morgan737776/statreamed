from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import AppointmentViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
