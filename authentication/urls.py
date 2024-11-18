from django.urls import path
from . import views

urlpatterns = [
    path('user/<int:user_id>/',views.GetUserByIdView.as_view(), name='get-user-by-id'),
    path('verify-email/',views.VerifyPinView.as_view(),name='verify_pin'),  
    path('login/', views.UserTokenObtainPairView.as_view(), name='login'),
    path('signup/',views.SignUp.as_view(), name='register'),
    #path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),  
    path('update-user/', views.UpdateUserDetails.as_view(), name='update'),
    path('request-password-change/', views.PasswordRequestChange.as_view(), name='password-change'),
    path('reset-password/', views.PasswordReset.as_view(),name='password-reset'),
    path('get-user/',views.GetUserDetailsView.as_view(),name='get_user'),
     path('upload-profile-image/', views.ProfileImageUploadView.as_view(), name='upload-profile-image'),
]
