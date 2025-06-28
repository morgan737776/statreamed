from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .models import ICD10, ServiceNomenclature
from rest_framework import serializers
from rest_framework.filters import SearchFilter

class ICD10Serializer(serializers.ModelSerializer):
    class Meta:
        model = ICD10
        fields = ['id', 'code', 'name', 'parent']

class ServiceNomenclatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceNomenclature
        fields = ['id', 'code', 'name']

class ICD10SearchView(ListAPIView):
    queryset = ICD10.objects.filter(is_active=True)
    serializer_class = ICD10Serializer
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']
    permission_classes = [IsAuthenticated]

class ServiceNomenclatureSearchView(ListAPIView):
    queryset = ServiceNomenclature.objects.filter(is_active=True)
    serializer_class = ServiceNomenclatureSerializer
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']
    permission_classes = [IsAuthenticated]
