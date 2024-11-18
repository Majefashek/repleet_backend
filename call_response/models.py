from django.db import models
from authentication.models import CustomUser
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.utils import timezone  # Adjust the import based on your project structure

class MySession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(CustomUser, related_name='sessions', on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, related_name='teaching_sessions', on_delete=models.CASCADE)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        # Automatically set status to expired if the end_time has passed
        if self.end_time < timezone.now():
            self.status = 'expired'
        super().save(*args, **kwargs)

    def clean(self):
        # Ensure that the teacher has the role of 'Teacher'
        if self.teacher.role != 'Teacher':
            raise ValidationError('The selected teacher must have the role of Teacher.')



class Session(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                             related_name='my_sessions',
                             null=True, blank=True)
    
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                                related_name='my_teaching_sessions',
                                null=True,blank=True)
    status = models.CharField(max_length=20, default='pending')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def clean(self):
        if self.teacher.role != 'Teacher':
            raise ValidationError({'teacher': 'The selected user is not a teacher.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session for {self.user.username} with {self.teacher.username} from {self.start_time} to {self.end_time}"

class Request(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')  

    def __str__(self):
        return f"Request from {self.user.username} for session {self.session.id} - Status: {self.status}"

