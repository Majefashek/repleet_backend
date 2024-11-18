from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Session, Request 
from .serializers import SessionSerializer, RequestSerializer 
from authentication.serializers import CustomUserSerializer
from authentication.models import CustomUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MySession
from .serializers import MySessionSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

class UserPagination(PageNumberPagination):
    page_size = 10 

class MySessionCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Create a new session",
        request_body=MySessionSerializer,
        responses={
            201: openapi.Response('Session created', MySessionSerializer),
            400: openapi.Response('Invalid data', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'success': openapi.Schema(type=openapi.TYPE_BOOLEAN), 'data': openapi.Schema(type=openapi.TYPE_OBJECT)}))
        }
    )
    def post(self, request):
        serializer = MySessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class MySessionUpdateStatusView(APIView):
    @swagger_auto_schema(
        operation_description="Update the status of a session",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)}),
        responses={
            200: openapi.Response('Status updated', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'success': openapi.Schema(type=openapi.TYPE_BOOLEAN), 'data': openapi.Schema(type=openapi.TYPE_OBJECT)})),
            404: openapi.Response('Session not found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'success': openapi.Schema(type=openapi.TYPE_BOOLEAN), 'data': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: openapi.Response('Invalid status', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'success': openapi.Schema(type=openapi.TYPE_BOOLEAN), 'data': openapi.Schema(type=openapi.TYPE_STRING)}))
        }
    )
    def patch(self, request, pk):
        try:
            session = MySession.objects.get(pk=pk)
        except MySession.DoesNotExist:
            return Response({'success': False, 'data': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        status = request.data.get('status')
        if status in ['accepted', 'rejected']:
            session.status = status
            session.save()
            return Response({'success': True, 'data': {'status': session.status}}, status=200)
        return Response({'success': False, 'data': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

class MySessionListView(APIView):
    pagination_class = UserPagination

    @swagger_auto_schema(
        operation_description="Retrieve sessions by status with pagination",
        responses={
            200: openapi.Response('Success', MySessionSerializer(many=True)),
        }
    )
    def get(self, request, status_filter):
        paginator = self.pagination_class()
        sessions = MySession.objects.filter(status=status_filter)
        page = paginator.paginate_queryset(sessions, request)
        serializer = MySessionSerializer(page, many=True)
        return paginator.get_paginated_response({'success': True, 'data': serializer.data})

class TeacherListView(APIView):
    pagination_class = UserPagination
    serializer_class = CustomUserSerializer  
    @swagger_auto_schema(
        operation_description="Retrieve a list of teachers",
        responses={200: openapi.Response('Success', CustomUserSerializer(many=True))}
    )
    def get(self, request, *args, **kwargs):
        paginator = self.pagination_class()
        queryset = CustomUser.objects.filter(role='Teacher')
        page = paginator.paginate_queryset(queryset,request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response({
            'success': True,
            'data': serializer.data,
            'message': 'Teachers retrieved successfully.'
        })
