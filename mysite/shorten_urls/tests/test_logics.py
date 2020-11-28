from django.test import TestCase

from ..logics import get_short_url_logic
from ..models import ShortUrl


class GetShortUrlLogicTest(TestCase):

    def test_success_by_create(self):
        self.assertEqual(ShortUrl.objects.count(), 0)

        url_1 = 'https://www.google.com'
        result = get_short_url_logic(url_1)

        self.assertDictEqual(
            result,
            {'short_url' : '1', 'original_url': url_1}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

        url_2 = 'https://www.google.com/?key=value'
        result = get_short_url_logic(url_2)

        self.assertDictEqual(
            result,
            {'short_url' : '2', 'original_url': url_2}
        )
        self.assertEqual(ShortUrl.objects.count(), 2)

    def test_success_by_get(self):
        self.assertEqual(ShortUrl.objects.count(), 0)

        url = 'https://www.google.com'
        short_url_object = ShortUrl.objects.create(
            original_url=url
        )

        result = get_short_url_logic(url)
        self.assertDictEqual(
            result,
            {'short_url' : '1', 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

        result = get_short_url_logic(url)
        self.assertDictEqual(
            result,
            {'short_url' : '1', 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

    def test_success_with_larget_id(self):
        url = 'https://www.google.com'
        short_url_object = ShortUrl.objects.create(
            id=123456789,
            original_url=url
        )

        result = get_short_url_logic(url)
        self.assertDictEqual(
            result,
            {'short_url' : '8m0Kx', 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)
