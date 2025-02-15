from django.urls import path
from .views import (
    CheckUserExistsView, 
)

urlpatterns = [
    path('check-user/', CheckUserExistsView.as_view(), name='check_user_exists'),
] 