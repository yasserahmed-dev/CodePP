from django.urls import path
from . import views 
urlpatterns = [
    path('test400/', views.error_400),
    path('test403/', views.error_403),
    path('test404/', views.error_404),
    path('test500/', views.error_500),
    path('',views.home,name = 'home'),
    path('profile',views.profile,name = 'profile'),
    path('edit_profile',views.edit_profile,name = 'edit_profile'),
    path('change_password',views.change_password,name = 'change_password'),
    path('delete_account/', views.delete_account_request, name='delete_account_request'),
    path('delete_account/verify/', views.delete_account_verify, name='delete_account_verify'),
]
