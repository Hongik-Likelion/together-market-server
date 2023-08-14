from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError("email을 입력해주세요")

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.save(using=self.db)
        return user

    def create_superuser(self, email, **extra_fields):
        user = self.create_user(email, **extra_fields)
        user.is_superuser = True
        user.save(using=self.db)
        return user


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, null=False, unique=True)
    email = models.EmailField(unique=True)
    is_owner = models.BooleanField()
    nickname = models.CharField(max_length=10)
    profile = models.URLField()
    introduction = models.CharField(max_length=30)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nickname", "profile", "is_owner"]

    def __str__(self) -> str:
        return f"user_id={self.id} email={self.email} nickname={self.nickname}"


class BlackList(models.Model):
    black_list_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blocked_user_id = models.BigIntegerField(null=False, unique=True)
