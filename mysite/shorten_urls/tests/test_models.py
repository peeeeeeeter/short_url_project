from unittest import mock
from django.test import TestCase

from ..models import ShortUrl
from ..utils import b62_encode


class BaseShortUrlModelTest(TestCase):

    @mock.patch('shorten_urls.models.random')
    def test_create_success(self, mock_random):
        mock_random.randint.return_value = 1

        original_url = 'https://www.google.com'
        short_url = ShortUrl.objects.create(
            original_url=original_url
        )

        self.assertEqual(short_url.original_url, original_url)
        self.assertEqual(short_url.random_offset, 1)

    def test_create_with_specifing_random_offset(self):
        original_url = 'https://www.google.com'
        random_offset = 2
        short_url = ShortUrl.objects.create(
            original_url=original_url,
            random_offset=random_offset
        )

        self.assertEqual(short_url.original_url, original_url)
        self.assertEqual(short_url.random_offset, 2)

    def test_property_url_id(self):
        original_url = 'https://www.google.com'
        random_offset = 3
        short_url = ShortUrl.objects.create(
            original_url=original_url,
            random_offset=random_offset
        )

        expect_url_id = int(1E8) + 3 * int(1E8) + short_url.id
        self.assertEqual(short_url.url_id, expect_url_id)

    def test_property_short_url_path(self):
        original_url = 'https://www.google.com'
        random_offset = 3
        short_url = ShortUrl.objects.create(
            original_url=original_url,
            random_offset=random_offset
        )

        expect_short_url_path = b62_encode(int(1E8) + 3 * int(1E8) + short_url.id)
        self.assertEqual(short_url.short_url_path, expect_short_url_path)


class ShortUrlModelTest(TestCase):

    def test_create(self):
        original_url = 'https://www.google.com'
        short_url = ShortUrl.objects.create(
            original_url=original_url
        )

        self.assertEqual(short_url.original_url, original_url)