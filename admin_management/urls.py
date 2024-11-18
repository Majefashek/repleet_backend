from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('create-admin/', views.CreateAdminUserView.as_view(), name='create_admin'), 
]
