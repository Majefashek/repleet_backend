
from rest_framework import serializers
from .models import Session, Request
from authentication.models import CustomUser
from rest_framework import serializers
from .models import MySession
class MySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MySession
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'user','teacher','start_time', 'end_time']

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'session', 'user', 'status']