# from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from registration.models import User, Interest
from utilities.conver_images import img_convert


class Contact(models.Model):
    user = models.ForeignKey(
        User, related_name='friends', on_delete=models.CASCADE, blank=True)
    friends = models.ManyToManyField(User, blank=True)

    interests = models.ManyToManyField(Interest, blank=True)
    avatar = models.ImageField(upload_to='images', blank=True)



    def __str__(self):
        return self.user.username

def post_save_user_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            Contact.objects.create(user=instance)
        except:
            pass

post_save.connect(post_save_user_model_receiver, sender=settings.AUTH_USER_MODEL)

class Message(models.Model):
    contact = models.ForeignKey(
        Contact, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.contact.user.username


class Chat(models.Model):
    author = models.ForeignKey(Contact, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, blank=True, default='')
    participants = models.ManyToManyField(
        Contact, related_name='chats', blank=True)
    messages = models.ManyToManyField(Message, related_name='messages_all', blank=True)

    def __str__(self):
        return "{}".format(self.title)


class Deal(models.Model):

    user = models.ForeignKey(User, related_name='user1', on_delete=models.CASCADE, verbose_name='Юзер')
    partner = models.ForeignKey(User, related_name='user2', on_delete=models.CASCADE, verbose_name='Партнер')
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}-{self.partner}'