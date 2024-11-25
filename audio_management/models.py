from django.db import models
from authentication.models import CustomUser
from django.core.exceptions import ValidationError

# Create your models here.
class AudioTrack(models.Model):
    CATEGORY_CHOICES = [
        ('Piano', 'Piano'),
        ('Guitar', 'Guitar'),
        ('Drum', 'Drum'),
        ('Vocals', 'Vocals'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    GENRE_CHOICES = [  # New field for music genres
        ('Pop', 'Pop'),
        ('Rock', 'Rock'),
        ('Classical', 'Classical'),
        ('Jazz', 'Jazz'),
        ('Blues', 'Blues'),
        ('Hip-Hop/Rap', 'Hip-Hop/Rap'),
        ('R&B', 'R&B'),
        ('Country', 'Country'),
        ('Reggae', 'Reggae'),
        ('Soul', 'Soul'),
        ('Metal', 'Metal'),
        ('Gospel', 'Gospel'),
    ]

    ELEMENT_CHOICES = [  # New field for musical elements
        ('Chord Progression', 'Chord Progression'),
        ('Solo Runs', 'Solo Runs'),
        ('Chord P & Solo Runs', 'Chord P & Solo Runs'),
    ]

    LENGTH_CHOICES = [  # New field for music length
        ('Part of Music', 'Part of Music'),
        ('Full Music', 'Full Music'),
    ]
    
    audio_file = models.FileField(upload_to='reference_tracks/', unique=True,blank=True,null=True)
    name=models.CharField(max_length=200,null=True,blank=True)
    artist=models.CharField(max_length=200,blank=True,null=True)
    description=models.CharField(max_length=200,blank=True,null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES,blank=True,null=True)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES,blank=True,null=True)
    
    # New fields for challenge setup
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES,blank=True,null=True)  # Genre of the music
    musical_element = models.CharField(max_length=50, choices=ELEMENT_CHOICES,blank=True,null=True)  # Musical elements
    music_length = models.CharField(max_length=20, choices=LENGTH_CHOICES,blank=True,null=True)  # Length of the music

    def __str__(self):
        return f"{self.category} - {self.difficulty_level} - {self.genre} - {self.musical_element} - {self.music_length}"
    

class MyReferenceTracks(models.Model):
    audio = models.ForeignKey(AudioTrack, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Check if the uploaded_by user has the role of 'Admin'
        if self.uploaded_by.role != 'Admin':
            raise ValidationError('Only users with the role of Admin can upload reference tracks.')
        super().save(*args, **kwargs)