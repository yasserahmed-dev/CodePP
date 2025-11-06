from django.urls import path
from . import views 
urlpatterns = [
    path('login',views.login_view,name = 'login'),
    path('logout',views.logout_view,name = 'logout'),
    path('signup',views.signup,name = 'signup'),
    path('password_reset',views.password_reset,name = 'password_reset'),
    path('verify_otp',views.verify_otp,name = 'verify_otp'),
    path('reset_password_form',views.reset_password_form,name = 'reset_password_form'),
]
 