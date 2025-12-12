from django.urls import path
from . import views 
urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('password_reset_request/', views.password_reset_request, name='password_reset_request'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password_form/', views.reset_password_form, name='reset_password_form'),
]
