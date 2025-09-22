from django.db import models

# Create your models here.
class Usersystem(models.Model):

    Username = models.CharField(max_length=100)
    Password = models.CharField(max_length=100)


