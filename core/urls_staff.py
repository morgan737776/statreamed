from django.urls import path
from . import views_staff

# URL-адреса для управления персоналом - временно отключено
# Используется пространство имен 'core'
urlpatterns = [
    # Specialist (Staff) URLs - временно заменены на placeholder функции
    path('', views_staff.specialist_list, name='staff_specialist_list'),
    path('create/', views_staff.specialist_create, name='staff_specialist_create'),
    path('<int:pk>/update/', views_staff.specialist_update, name='staff_specialist_update'),
    path('<int:pk>/delete/', views_staff.specialist_delete, name='staff_specialist_delete'),

    # Specialization URLs - временно отключены
    # path('specializations/', views_staff.SpecializationListView.as_view(), name='staff_specialization_list'),
    # path('specializations/create/', views_staff.SpecializationCreateView.as_view(), name='staff_specialization_create'),
    # path('specializations/<int:pk>/update/', views_staff.SpecializationUpdateView.as_view(), name='staff_specialization_update'),
    # path('specializations/<int:pk>/delete/', views_staff.SpecializationDeleteView.as_view(), name='staff_specialization_delete'),
]
