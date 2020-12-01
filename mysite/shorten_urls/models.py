import random

from django.db import models

from .configs import (URL_B62_BASE_NUM, URL_B62_OFFSET_RANGE,
                      URL_B62_OFFSET_SIZE)
from .utils import b62_encode


class BaseShortUrlManager(models.Manager):

    def create(self, original_url, random_offset=None,
               *args, **kwargs):

        if not random_offset:
            random_offset = random.randint(URL_B62_OFFSET_RANGE[0], URL_B62_OFFSET_RANGE[1])

        return super(BaseShortUrlManager, self).create(
            original_url=original_url,
            random_offset=random_offset,
            **kwargs)


class BaseShortUrl(models.Model):

    original_url = models.TextField()

    random_offset = models.SmallIntegerField()

    objects = BaseShortUrlManager()

    class Meta:
        abstract = True

    @property
    def url_id(self):
        base = URL_B62_BASE_NUM
        offset = URL_B62_OFFSET_SIZE * self.random_offset

        return self.id + base + offset

    @property
    def short_url_path(self):
        return b62_encode(self.url_id)


class ShortUrl(BaseShortUrl):

    original_url = models.TextField(unique=True)
