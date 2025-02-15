from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUserModel(AbstractUser):
    PROFILE_PICTURE_UPLOAD_TO = 'profile_pictures/'
    
    profile_picture = models.ImageField(_("Photo de Profil"), upload_to=PROFILE_PICTURE_UPLOAD_TO, blank=True, null=True)