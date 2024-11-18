from rest_framework import serializers
from .models import ReferenceTrack

class ReferenceTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceTrack
        fields = '__all__'