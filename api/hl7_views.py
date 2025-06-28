from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Patient
from hl7apy.core import Message

class HL7PatientList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patients = Patient.objects.all()
        messages = []
        for p in patients:
            msg = Message("ADT_A01")
            msg.msh.msh_3 = "REHAB_CENTER"
            msg.msh.msh_9 = "ADT^A01"
            msg.pid.pid_3 = str(p.id)
            msg.pid.pid_5 = f"{p.last_name}^{p.first_name}^{p.middle_name or ''}"
            msg.pid.pid_7 = p.birth_date.strftime('%Y%m%d') if p.birth_date else ''
            msg.pid.pid_8 = p.gender[0].upper() if p.gender else ''
            msg.pid.pid_13 = p.phone or ''
            messages.append(msg.to_er7())
        return Response({'hl7_messages': messages})

class HL7PatientDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            p = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        msg = Message("ADT_A01")
        msg.msh.msh_3 = "REHAB_CENTER"
        msg.msh.msh_9 = "ADT^A01"
        msg.pid.pid_3 = str(p.id)
        msg.pid.pid_5 = f"{p.last_name}^{p.first_name}^{p.middle_name or ''}"
        msg.pid.pid_7 = p.birth_date.strftime('%Y%m%d') if p.birth_date else ''
        msg.pid.pid_8 = p.gender[0].upper() if p.gender else ''
        msg.pid.pid_13 = p.phone or ''
        return Response({'hl7_message': msg.to_er7()})
