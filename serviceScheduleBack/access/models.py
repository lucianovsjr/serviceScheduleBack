from django.db import models


URL_AMAZON_S3 = 'https://week-calendar-app.s3.us-east-2.amazonaws.com'

def upload_name(instance, filename):
    return f'{instance.user.id}-{filename}'


class Perfil(models.Model):
    user = models.OneToOneField('auth.User', null=False,
            on_delete=models.CASCADE, related_name='user_perfil')
    provider = models.BooleanField('Provedor', default=False)
    fantasy_name = models.CharField('Nome fantasia', max_length=30)
    profession = models.CharField('Profissão', max_length=30)
    image = models.ImageField(verbose_name='Imagem',
            upload_to=upload_name, default='profile-default', null=True,
            blank=True)

    def image_name(self):
        return f'{URL_AMAZON_S3}/{self.image.name}'
