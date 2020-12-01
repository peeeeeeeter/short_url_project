import hashlib

from .configs import (CRAWL_URL_PREVIEW_TIMEOUT, SHORT_URL_MAX_LEN,
                      URL_B62_BASE_NUM, URL_B62_OFFSET_SIZE)
from .models import ShortUrl, get_hashed_url_from_original_url
from .utils import UrlPreivew, b62_decode, b62_encode


class ShortUrlLogics:

    def __init__(self, url, hash_algo=None, *args, **kwargs):
        self.url = url

        if hash_algo is None:
            hash_algo = hashlib.sha256()

        self.hash_algo = hash_algo

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

        return {
            'short_url_path': short_url_object.short_url_path,
            'original_url': self.url,
        }

    def get_short_url_preview_data(self):
        preview = UrlPreivew(self.url, timeout=CRAWL_URL_PREVIEW_TIMEOUT)
        preview.fire()

        preview_data = {}
        if preview.success:
            preview_data = preview.as_dict()

        return preview_data

    def get_shor_url_data(self):
        data = {}

        short_url_data = self.get_or_create_short_url()
        data['short_url_path'] = short_url_data['short_url_path']
        data['original_url'] = short_url_data['original_url']

        preview_data = self.get_short_url_preview_data()
        data['preview_data'] = preview_data

        return data


def decode_short_url(short_url):
    if len(short_url) != SHORT_URL_MAX_LEN:
        raise ValueError(
            'short_url should have length = {}, not {}'.format(
                SHORT_URL_MAX_LEN, len(short_url))
        )

    raw_url_number = b62_decode(short_url)
    real_url_number = (raw_url_number - URL_B62_BASE_NUM) % URL_B62_OFFSET_SIZE
    return real_url_number
