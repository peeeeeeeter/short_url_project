import hashlib
import random

from django.db import models
from django.utils import timezone

from .configs import (HASHED_URL_LENGTH, URL_B62_BASE_NUM,
                      URL_B62_OFFSET_RANGE, URL_B62_OFFSET_SIZE)
from .utils import b62_encode


class BaseShortUrlManager(models.Manager):

    def create(self, original_url, random_offset=None,
               *args, **kwargs):

        if not random_offset:
            random_offset = random.randint(
                URL_B62_OFFSET_RANGE[0], URL_B62_OFFSET_RANGE[1])

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


def get_hashed_url_from_original_url(original_url, hash_algo=None):
    if hash_algo is None:
        hash_algo = hashlib.sha256()

    hash_algo.update(original_url.encode('utf-8'))
    hashed_url = hash_algo.hexdigest()[:HASHED_URL_LENGTH]
    return hashed_url


class ShortUrlManager(BaseShortUrlManager):

    def create(self, original_url, hashed_url='',
               *args, **kwargs):
        if not hashed_url:
            hashed_url = get_hashed_url_from_original_url(original_url)

        return super(ShortUrlManager, self).create(
            original_url=original_url,
            hashed_url=hashed_url,
            **kwargs
        )


class ShortUrl(BaseShortUrl):

    original_url = models.TextField(unique=True)
    hashed_url = models.CharField(max_length=HASHED_URL_LENGTH, db_index=True)

    objects = ShortUrlManager()

    def __str__(self):
        return self.original_url


class UrlPreviewData(models.Model):

    from_url = models.OneToOneField(
        ShortUrl, on_delete=models.CASCADE,
        related_name='preview_data',
    )

    title = models.CharField(max_length=256)
    description = models.CharField(max_length=500)
    url = models.URLField(max_length=256)
    image_url = models.URLField(max_length=256)

    last_update = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return {
            'original_url': str(self.from_url),
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'image_url': self.image_url,
            'last_update': self.last_update.strftime('%Y-%m-%d %H:%M:%S')
        }
