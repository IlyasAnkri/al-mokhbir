from django.contrib.auth.models import User
from django.db import models

class NewsSource(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    url = models.URLField()
    source_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class BotSetting(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    premium_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Premium' if self.is_premium else 'Free'}"

