from rest_framework import serializers
from predictor.models import *

class CropDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropDetails
        fields = "__all__"