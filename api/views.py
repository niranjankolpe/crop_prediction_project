from rest_framework.response import Response
from rest_framework.decorators import api_view
from predictor.models import *
from api.serializers import *
from django.shortcuts import render, redirect

@api_view(['GET'])
def getData(request):
    records = CropDetails.objects.all()
    serializer = CropDetailsSerializer(records, many=True)
    return Response(serializer.data)

@api_view(["POST"])
def addData(request):
    serializer = CropDetailsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)