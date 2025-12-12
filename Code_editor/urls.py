from django.urls import path
from .views import code_editor

urlpatterns = [
    path('', code_editor, name='code_editor'),
]
