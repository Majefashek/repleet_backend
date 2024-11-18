from django.db import models
from audio_management.models import AudioTrack
from authentication.models import CustomUser

class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    name = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES,blank=True,null=True)  # Assuming Difficulty is a string
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by=models.ForeignKey(CustomUser, blank=True,null=True,on_delete=models.CASCADE)

class ChallengeAudio(models.Model):
    challenge= models.ForeignKey(Challenge,on_delete=models.CASCADE)
    audio_id = models.ForeignKey(AudioTrack, on_delete=models.CASCADE)  

class ChallengeParticipant(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    participant_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    participant_score = models.IntegerField(default=0)

# Create your models here.
