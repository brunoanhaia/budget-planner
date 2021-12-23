from django.db import models

from django.db import models

class Client(models.Model):
    cpf=models.CharField(max_length=11)
    nick_name=models.CharField(max_length=50)