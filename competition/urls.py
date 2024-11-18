from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('upload-competition-tracks/', views.UploadCompetitionTracks.as_view(), name='upload_competition_track'), 
    path('competitions/', views.CompetitionCreateView.as_view(), name='create-competition'), 
    path('competitions/<int:competition_id>/',views.DeleteCompetition.as_view(), name='delete-competition'), 
    path('competitions/participants/add/',views.CompetitionParticipantCreateView.as_view(), name='create-participant'),  
    path('competitions/<int:competition_id>/participants/score/<int:pk>/', views.CompetitionParticipantScoreView.as_view(), name='update-participant-score'), 
    path('competitions/<int:competition_id>/top-participants/', views.TopParticipantsListView.as_view(), name='top-participants'), 
    path('competitions/audios/', views.UploadCompetitionTracks.as_view(), name='upload-audio'), 
    path('competitions/get/',views.ChallengeList.as_view(), name='list-competitions'), 
    path('competitions/<int:competition_id>/audios/',views.CompetitionAudioListView.as_view(), name='list-competition-audios'), 
    path('competition/add-existing-audio/',views.AddExistingAudioToCompetition.as_view(), name='add-existing-audio'),
]
 