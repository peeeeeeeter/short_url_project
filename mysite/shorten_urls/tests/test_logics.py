from unittest import mock

from django.test import TestCase

from ..configs import URL_B62_BASE_NUM, URL_B62_OFFSET_SIZE
from ..logics import ShortUrlLogics, decode_short_url
from ..models import ShortUrl
from ..utils import b62_encode


class ShortUrlLogicsTest(TestCase):


    @mock.patch('shorten_urls.models.random')
    def test_get_or_create_url_success_by_create(self, mock_random):
        mock_random.randint.return_value = 1

        self.assertEqual(ShortUrl.objects.count(), 0)

        url_1 = 'https://www.google.com'
        logic = ShortUrlLogics(url_1)
        result = logic.get_or_create_short_url()

        expect_short_url_path = b62_encode(2*int(1E8) + 1)
        self.assertDictEqual(
            result,
            {'short_url_path' : expect_short_url_path, 'original_url': url_1}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

        url_2 = 'https://www.google.com/?key=value'
        logic = ShortUrlLogics(url_2)
        result = logic.get_or_create_short_url()

        expect_short_url_path_2 = b62_encode(2*int(1E8) + 2)
        self.assertDictEqual(
            result,
            {'short_url_path' : expect_short_url_path_2, 'original_url': url_2}
        )
        self.assertEqual(ShortUrl.objects.count(), 2)

    @mock.patch('shorten_urls.models.random')
    def test_get_or_create_url_success_by_get(self, mock_rand):
        mock_rand.randint.return_value = 1

        self.assertEqual(ShortUrl.objects.count(), 0)

        url = 'https://www.google.com'
        short_url_object = ShortUrl.objects.create(
            original_url=url
        )

        logic = ShortUrlLogics(url)
        result = logic.get_or_create_short_url()

        expect_short_url_path = b62_encode(2*int(1E8) + 1)
        self.assertDictEqual(
            result,
            {'short_url_path' : expect_short_url_path, 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

        logic = ShortUrlLogics(url)
        result = logic.get_or_create_short_url()

        self.assertDictEqual(
            result,
            {'short_url_path' : expect_short_url_path, 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

    @mock.patch('shorten_urls.models.random')
    def test_get_or_create_url_success_with_larget_id(self, mock_rand):
        mock_rand.randint.return_value = 1

        url = 'https://www.google.com'
        short_url_object = ShortUrl.objects.create(
            id=123456789,
            original_url=url
        )
        logic = ShortUrlLogics(url)
        result = logic.get_or_create_short_url()

        expect_short_url_path = b62_encode(2*int(1E8) + 123456789)
        self.assertDictEqual(
            result,
            {'short_url_path' : expect_short_url_path, 'original_url': url}
        )
        self.assertEqual(ShortUrl.objects.count(), 1)


class DecodeShortUrlTest(TestCase):

    def test_short_url_too_long(self):
        short_url = 'abcdefg'

        with self.assertRaises(ValueError):
            decode_short_url(short_url)

    def test_short_url_too_short(self):
        short_url = 'a'

        with self.assertRaises(ValueError):
            decode_short_url(short_url)

    def test_success(self):
        url_id = 25
        pseudo_random_url_id = url_id + URL_B62_BASE_NUM + 3 * URL_B62_OFFSET_SIZE
        short_url = b62_encode(pseudo_random_url_id)

        self.assertEqual(
            decode_short_url(short_url),
            url_id
        )
