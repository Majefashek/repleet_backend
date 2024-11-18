from django.db import models

# Create your models here.
class ReferenceTrack(models.Model):
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
    
    audio_file = models.FileField(upload_to='reference_tracks/',unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)

    def __str__(self):
        return f"{self.category} - {self.difficulty_level}"