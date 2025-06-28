from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.routers import DefaultRouter
from .models import Appointment
from .serializers import AppointmentSerializer

router = DefaultRouter()


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def update_time(self, request, pk=None):
        """
        Обновляет время приема при перетаскивании в календаре
        """
        appointment = self.get_object()
        
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        if not start_time or not end_time:
            return Response({"error": "start_time и end_time обязательны"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointment.start_datetime = start_time
            appointment.end_datetime = end_time
            appointment.save()
            
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Регистрируем ViewSet в router
router.register(r'appointments', AppointmentViewSet)
