
from django.contrib import admin
from django.urls import path,include
from .  views import  *

urlpatterns = [
    #path('analyze-audio-features/', views.AudioFeatureAnalyzer.as_view(), name='audio_extractor'),
    path('compare_audios/',CompareTwoAudiosEndpoint.as_view(), name='grade_audio_performance')
]
