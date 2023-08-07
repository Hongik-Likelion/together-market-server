from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    is_owner = models.BooleanField()
    email = models.EmailField(unique=True)

    objects = UserManager()
    USERNAME_FIELD = "email"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nickname = models.CharField(max_length=20)
    profile = models.URLField()
    introduction = models.CharField(max_length=50)