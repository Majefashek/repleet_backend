from django.urls import path
from .views import UploadReferenceTrackView, ReferenceTracksByDifficultyView, DeleteReferenceTrackView

urlpatterns = [
    path('upload-reference-track/', UploadReferenceTrackView.as_view(), name='upload-reference-track'),
    path('reference-tracks/difficulty/', ReferenceTracksByDifficultyView.as_view(), name='reference-tracks-by-difficulty'),
     path('reference-tracks/delete/<int:track_id>/', DeleteReferenceTrackView.as_view(), name='delete-reference-track'),
]