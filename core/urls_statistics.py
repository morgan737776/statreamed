from django.urls import path
from .api_statistics import StatisticsView

urlpatterns = [
    path('api/statistics/', StatisticsView.as_view(), name='api_statistics'),
]
