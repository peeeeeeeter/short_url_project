from django.test import TestCase

from ..models import ShortUrl


class ShortUrlModelTest(TestCase):

    def test_create(self):
        original_url = 'https://www.google.com'
        short_url = ShortUrl.objects.create(
            original_url=original_url
        )

        self.assertEqual(short_url.original_url, original_url)