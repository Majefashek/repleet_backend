from rest_framework import serializers
from .models import AudioTrack  # Adjust the import based on your project structure

class AudioTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioTrack
        fields = '__all__' 