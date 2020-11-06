from django.db import models


URL_AMAZON_S3 = 'https://week-calendar-app.s3.us-east-2.amazonaws.com'


class Company(models.Model):
    name = models.CharField('Nome', max_length=30, blank=False, null=False)

    def __str__(self):
        return self.name


def upload_name(instance, filename):
    return f'{instance.user.id}-{filename}'


class Perfil(models.Model):
    user = models.OneToOneField('auth.User', null=False,
                                on_delete=models.CASCADE,
                                related_name='user_perfil')
    provider = models.BooleanField('Provedor', default=False)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    fantasy_name = models.CharField('Nome fantasia', max_length=30)
    profession = models.CharField('Profissão', max_length=30)
    image = models.ImageField(verbose_name='Imagem',
                              upload_to=upload_name,
                              default='profile-default',
                              null=True,
                              blank=True)

    def __str__(self):
        return '{} - {}'.format(self.user.get_full_name(), self.company)

    def image_name(self):
        return f'{URL_AMAZON_S3}/media/{self.image.name}'
