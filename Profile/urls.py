from django.urls import path
from . import views 
urlpatterns = [
    path('', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('delete_account/', views.delete_account_request, name='delete_account'),
    path('verify_delete/', views.delete_account_verify, name='verify_delete'),
]
