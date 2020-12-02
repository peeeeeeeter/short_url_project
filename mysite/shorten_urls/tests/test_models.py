import hashlib
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from ..models import ShortUrl, UrlPreviewData, get_hashed_url_from_original_url
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


class GetHashedUrlFromOriginalUrlTtest(TestCase):

    def test_success(self):
        original_url = 'http://www.fake.com'

        default_hash_algo = hashlib.sha256()
        default_hash_algo.update(original_url.encode('utf-8'))

        expected_hashed_url = default_hash_algo.hexdigest()
        self.assertEqual(
            get_hashed_url_from_original_url(original_url),
            expected_hashed_url[:32]
        )


class ShortUrlModelTest(TestCase):

    def setUp(self):
        self.hash_algo = hashlib.sha256()

    @mock.patch('shorten_urls.models.random')
    def test_create(self, mock_rand):
        mock_rand.randint.return_value = 1

        original_url = 'https://www.google.com'
        short_url = ShortUrl.objects.create(
            original_url=original_url
        )

        self.hash_algo.update(original_url.encode('utf-8'))
        expected_url = self.hash_algo.hexdigest()[:32]

        self.assertEqual(short_url.original_url, original_url)
        self.assertEqual(short_url.hashed_url, expected_url)
        self.assertEqual(short_url.random_offset, 1)

    def test_create_by_specifing_hashed_url(self):
        original_url = 'https://www.google.com'
        short_url = ShortUrl.objects.create(
            original_url=original_url,
            hashed_url='abcdefg'
        )

        self.assertEqual(short_url.original_url, original_url)
        self.assertEqual(short_url.hashed_url, 'abcdefg')


class UrlPreviewDataModelTest(TestCase):

    def setUp(self):
        self.short_url_object = ShortUrl.objects.create(
            original_url='https://www.fake.com'
        )

    def test_create_success(self):
        url_preview_data = UrlPreviewData.objects.create(
            from_url=self.short_url_object,
            title='some title',
            description='some description',
            url='some url',
            image_url='some image url'
        )

        last_update_time = url_preview_data.last_update

        self.assertDictEqual(
            url_preview_data.as_dict(),
            {
                'original_url': 'https://www.fake.com',
                'title': 'some title',
                'description': 'some description',
                'url': 'some url',
                'image_url': 'some image url',
                'last_update': last_update_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
