from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser,PermissionsMixin,BaseUserManager
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    SKILL_LEVEL = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    ROLES=[
        ('User','User'),
        ('Teacher', 'Teacher'),
        ('Admin','Admin')
    ] 
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phonenumber = models.CharField(max_length=20, blank=True, null=True)
    fullName=models.CharField(max_length=50,null=True, blank=True)
    bio=models.CharField(max_length=1000,null=True,blank=True)
    skill_level=models.CharField(max_length=20,choices=SKILL_LEVEL, default='Beginner')
    role=models.CharField(max_length=20,choices=ROLES, default='User')
    genre_of_interest=models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
 

    objects = CustomUserManager()

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return({
            'refresh': str(refresh),
            'refresh': str(refresh.access_token),
        })

    def __str__(self):
        return self.email
    



class UserVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    pin_code = models.CharField(max_length=6)
    expiry_date = models.DateTimeField()  # Expiry date for the PIN code
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_expired(self):
        return timezone.now() > self.expiry_date

    def __str__(self):
        return f"Verification for {self.user.email}"
        




# Create your models here.
