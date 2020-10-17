from django.db import models


def upload_name(instance, filename):
    path = 'profile'
    return '{0}/user_{1}_{2}'.format(path, instance.user.id, filename)


class Perfil(models.Model):
    user = models.OneToOneField('auth.User', null=False,
        on_delete=models.CASCADE, related_name='user_perfil')
    provider = models.BooleanField('Provedor', default=False)
    fantasy_name = models.CharField('Nome fantasia', max_length=30)
    profession = models.CharField('Profissão', max_length=30)
    image = models.ImageField(verbose_name='Imagem',
        upload_to=upload_name, default=None, null=True, blank=True)
