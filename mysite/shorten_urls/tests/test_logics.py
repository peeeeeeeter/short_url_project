from django.test import TestCase

from ..logics import ShortUrlLogics
from ..models import ShortUrl


class ShortUrlLogicsTest(TestCase):

    def test_get_or_create_url_success_by_create(self):
        self.assertEqual(ShortUrl.objects.count(), 0)

        url_1 = 'https://www.google.com'
        logic = ShortUrlLogics(url_1)
        result = logic.get_or_create_short_url()

        self.assertDictEqual(
            result,
            {'short_url_path' : '1', 'original_url': url_1}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

        url_2 = 'https://www.google.com/?key=value'
        logic = ShortUrlLogics(url_2)
        result = logic.get_or_create_short_url()

        self.assertDictEqual(
            result,
            {'short_url_path' : '2', 'original_url': url_2}
        )
        self.assertEqual(ShortUrl.objects.count(), 2)

    def test_get_or_create_url_success_by_get(self):
        self.assertEqual(ShortUrl.objects.count(), 0)

        url = 'https://www.google.com'
        short_url_object = ShortUrl.objects.create(
            original_url=url
        )

        logic = ShortUrlLogics(url)
        result = logic.get_or_create_short_url()

        self.assertDictEqual(
            result,
            {'short_url_path' : '1', 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

        logic = ShortUrlLogics(url)
        result = logic.get_or_create_short_url()

        self.assertDictEqual(
            result,
            {'short_url_path' : '1', 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

    def test_get_or_create_url_success_with_larget_id(self):
        url = 'https://www.google.com'
        short_url_object = ShortUrl.objects.create(
            id=123456789,
            original_url=url
        )

        logic = ShortUrlLogics(url)
        result = logic.get_or_create_short_url()

        self.assertDictEqual(
            result,
            {'short_url_path' : '8m0Kx', 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)
