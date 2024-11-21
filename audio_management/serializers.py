from rest_framework import serializers
from .models import AudioTrack,MyReferenceTracks

class AudioTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioTrack
        fields = '__all__' 


class ReferenceTracksSerializer(serializers.ModelSerializer):
    audio=audio = AudioTrackSerializer()
    class Meta:
        model = MyReferenceTracks
        fields = '__all__'