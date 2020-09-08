from django.db import models


class Perfil(models.Model):
    user = models.OneToOneField('auth.User', null=False, on_delete=models.CASCADE)
    provider = models.BooleanField('Provedor', default=False)
    fantasy_name = models.CharField('Nome fantasia', max_length=30)
    profession = models.CharField('Profissão', max_length=30)
