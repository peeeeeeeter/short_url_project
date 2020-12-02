import hashlib

from django.utils import timezone

from .configs import (CRAWL_URL_PREVIEW_TIMEOUT, SHORT_URL_MAX_LEN,
                      URL_B62_BASE_NUM, URL_B62_OFFSET_SIZE)
from .models import ShortUrl, UrlPreviewData, get_hashed_url_from_original_url
from .utils import UrlPreview, b62_decode, b62_encode


class ShortUrlLogics:

    def __init__(self, url, hash_algo=None, *args, **kwargs):
        self.url = url

        if hash_algo is None:
            hash_algo = hashlib.sha256()

        self.hash_algo = hash_algo

    def get_short_url_info(self):
        short_url_object = self.get_or_create_short_url()
        return {
            'short_url_path': short_url_object.short_url_path,
            'original_url': self.url,
        }

    def get_or_create_short_url(self):
        hashed_url = get_hashed_url_from_original_url(self.url, self.hash_algo)
        qs = ShortUrl.objects.filter(hashed_url=hashed_url)

        if not qs.exists():
            short_url_object = ShortUrl.objects.create(
                original_url=self.url,
                hashed_url=hashed_url,
            )
        elif qs.count() > 1:
            short_url_object = qs.get(original_url=self.url)
        else:
            short_url_object = qs[0]

        return short_url_object


class UrlPreviewDataLogic:

    def __init__(self, url):
        self.url = url

        short_url_logic = ShortUrlLogics(self.url)
        self.short_url_object = short_url_logic.get_or_create_short_url()

    def get_url_preview_data_info(self):
        preview_data = self.get_or_create_url_preview_data()
        if preview_data:
            return preview_data.as_dict()

        return {}

    def get_or_create_url_preview_data(self):
        short_url_object = self.short_url_object
        try:
            preview_data = short_url_object.preview_data
        except UrlPreviewData.DoesNotExist:
            preview_data = self.create_url_preview_data()
        else:
            if preview_data.last_update - timezone.now() > timezone.timedelta(days=1):
                preview_data = self.update_url_preview_data()

        return preview_data

    def update_url_preview_data(self):
        preview_data = self.get_url_preview_data()
        if not preview_data:
            return None

        url_preview_data = UrlPreviewData.objects.get(
            from_url=self.short_url_object)

        url_preview_data.title = preview_data['title']
        url_preview_data.description = preview_data['description']
        url_preview_data.url = preview_data['url']
        url_preview_data.image_url = preview_data['image']

        url_preview_data.save()
        return url_preview_data

    def create_url_preview_data(self):
        preview_data = self.get_url_preview_data()

        if not preview_data:
            return None

        url_preview_data = UrlPreviewData.objects.create(
            from_url=self.short_url_object,
            title=preview_data['title'],
            description=preview_data['description'],
            url=preview_data['url'],
            image_url=preview_data['image']
        )
        return url_preview_data

    def get_url_preview_data(self):
        preview = UrlPreview(self.url, timeout=CRAWL_URL_PREVIEW_TIMEOUT)
        preview.fire()

        preview_data = {}
        if preview.success:
            return preview.as_dict()

        return preview_data


def decode_short_url(short_url):
    if len(short_url) != SHORT_URL_MAX_LEN:
        raise ValueError(
            'short_url should have length = {}, not {}'.format(
                SHORT_URL_MAX_LEN, len(short_url))
        )

    raw_url_number = b62_decode(short_url)
    real_url_number = (raw_url_number - URL_B62_BASE_NUM) % URL_B62_OFFSET_SIZE
    return real_url_number
