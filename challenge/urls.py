from django.urls import path
from .views import*
urlpatterns = [
    path('challenges/get/', ChallengeList.as_view(), name='challenge-list'),  # Endpoint for all challenges
    path('challenges/user/<int:user_id>/', UserChallenges.as_view(), name='user-challenges'),
    path('challenges/add/',ChallengeCreateView.as_view(), name='create-challenge'),
    path('challenges/<int:challenge_id>/audio/', ChallengeAudioListView.as_view(), name='challenge-audio-list'),
    path('challenges/<int:challenge_id>/participants/', ChallengeParticipantCreateView.as_view(), name='create-participant'),
    path('challenges/<int:challenge_id>/participants/<int:pk>/score/', ChallengeParticipantScoreView.as_view(), name='update-participant-score'),
    path('challenges/<int:challenge_id>/', DeleteChallenge.as_view(), name='delete-challenge'),
    path('challenges/<int:challenge_id>/top-participants/', TopParticipantsListView.as_view(), name='top-participants'),
    path('challenges/<int:challenge_id>/upload-tracks/', UploadChallengeTracks.as_view(), name='upload-challenge-tracks'),
    path('challenges/add-audio/', AddExistingAudioToChallenge.as_view(), name='add-existing-audio'),
]