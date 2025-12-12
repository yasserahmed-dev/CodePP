from django.urls import path
from . import views 
urlpatterns = [
    path('test400/', views.error_400),
    path('test403/', views.error_403),
    path('test404/', views.error_404),
    path('test500/', views.error_500),

    path('', views.home, name='home'),
]


