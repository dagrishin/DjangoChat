# from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from utilities.conver_images import img_convert


class User(AbstractUser):
    avatar = models.ImageField(upload_to='images', blank=True)


class Interest(models.Model):

    name = models.CharField(verbose_name='Интересы', max_length=255)
    desc = models.TextField(verbose_name='Описание', blank=True)

    def __str__(self):
        return self.name
