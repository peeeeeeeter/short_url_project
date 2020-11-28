from .models import ShortUrl
from .utils import b62_encode


def get_short_url_logic(url):
    short_url_object, _ = ShortUrl.objects.get_or_create(
        original_url=url
    )

    number = short_url_object.id
    return {
        'short_url': b62_encode(number),
        'original_url': url
    }