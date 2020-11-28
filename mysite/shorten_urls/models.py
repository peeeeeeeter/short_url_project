from django.db import models


class BaseShortUrl(models.Model):

    original_url = models.TextField()

    class Meta:
        abstract = True


class ShortUrl(BaseShortUrl):

    original_url = models.TextField(db_index=True)
