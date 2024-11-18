from django.urls import path
from .views import *
urlpatterns = [
    path('sessions/', MySessionCreateView.as_view(), name='create_session'),
    path('sessions/<int:pk>/status/', MySessionUpdateStatusView.as_view(), name='update_session_status'),
    path('sessions/status/<str:status_filter>/', MySessionListView.as_view(), name='list_sessions_by_status'),
    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
]