import http.client as httplib
from unittest import mock

from django.test import TestCase, override_settings

from ..configs import CREATE_SHORT_URL_RATE_LIMIT
from ..models import ShortUrl
from ..utils import b62_encode


@override_settings(RATELIMIT_ENABLE=False)
class ShortUrlViewTest(TestCase):

    url = '/api/v1/short_urls'

    def test_incorrect_url(self):
        url = '/api/v1/short_urls/not-exists'
        form = {
            'url_input': 'https://www.google.com'
        }

        r = self.client.post(url, form)
        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_form_error(self):
        form = {
            'url_input': 'https://'
        }

        r = self.client.post(self.url, form)
        self.assertEqual(r.status_code, httplib.BAD_REQUEST)
        self.assertJSONEqual(r.content, {'url_input': ['Enter a valid URL.']})

    def test_success(self):
        url_input = 'https://www.google.com'
        form = {
            'url_input': url_input
        }

        r = self.client.post(self.url, form)

        self.assertEqual(r.status_code, httplib.OK)

        obj = ShortUrl.objects.get(original_url=url_input)
        self.assertJSONEqual(
            r.content,
            {
                'data': {
                    'short_url_path': obj.short_url_path,
                    'original_url': url_input,
                },
                'message': 'success'
            }
        )

    @override_settings(RATELIMIT_ENABLE=True)
    def test_rate_limit_exceed(self):
        url_input = 'https://www.google.com'
        form = {
            'url_input': url_input
        }

        rate_limit = int(CREATE_SHORT_URL_RATE_LIMIT.split('/')[0])

        for i in range(rate_limit):
            r = self.client.post(self.url, form)
            self.assertEqual(r.status_code, httplib.OK)

        r = self.client.post(self.url, form)
        self.assertEqual(r.status_code, httplib.FORBIDDEN)


class ShortUrlPreviewTest(TestCase):

    url = '/api/v1/short_urls/preview'

    def test_incorrect_url(self):
        url = '/api/v1/short_urls/not-exists'
        form = {
            'url_input': 'https://www.google.com'
        }

        r = self.client.post(url, form)
        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_form_error(self):
        form = {
            'url_input': ''
        }

        r = self.client.post(self.url, form)

        self.assertEqual(r.status_code, httplib.BAD_REQUEST)
        self.assertDictEqual(
            r.json(),
            {'url_input': ['This field is required.']}
        )

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_get_preview_data_failed(self, mock_get):
        mock_get.return_value = None
        form = {
            'url_input': 'https://www.google.com'
        }

        r = self.client.post(self.url, form)

        self.assertEqual(r.status_code, httplib.OK)
        self.assertDictEqual(
            r.json(),
            {'message': 'failed', 'data': {}}
        )

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_success(self, mock_get):
        mock_get.return_value = {
            'title': 'some title',
            'description': 'some description',
            'url': 'some url',
            'image': 'some image url',
        }
        form = {
            'url_input': 'https://www.google.com'
        }

        r = self.client.post(self.url, form)

        self.assertEqual(r.status_code, httplib.OK)
        self.assertDictEqual(
            r.json(),
            {
                'message': 'success',
                'data': {
                    'title': 'some title',
                    'description': 'some description',
                    'url': 'some url',
                    'image_url': 'some image url',
                }
            }
        )


class GetOriginalUrlViewTest(TestCase):

    url = '/api/v1/short_urls/original_url'

    def setUp(self):
        self.short_url_object = ShortUrl.objects.create(
            original_url='https://www.fake.com'
        )

    def test_incorrect_url(self):
        form = {
            'short_url': self.short_url_object.short_url_path
        }
        r = self.client.get('/api/v1/short_urls/xxxx', form)

        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_form_invalid_too_long(self):
        form = {
            'short_url': 'a' * 4
        }

        r = self.client.get(self.url, form)

        self.assertEqual(r.status_code, httplib.BAD_REQUEST)
        self.assertEqual(
            r.json(),
            {'message': 'failed', 'data': {}}
        )

    def test_form_invalid_too_short(self):
        form = {
            'short_url': 'a'
        }

        r = self.client.get(self.url, form)

        self.assertEqual(r.status_code, httplib.BAD_REQUEST)
        self.assertEqual(
            r.json(),
            {'message': 'failed', 'data': {}}
        )

    def test_form_invalid_invalid_chars(self):
        form = {
            'short_url': 'abcd@'
        }

        r = self.client.get(self.url, form)

        self.assertEqual(r.status_code, httplib.BAD_REQUEST)
        self.assertEqual(
            r.json(),
            {'message': 'failed', 'data': {}}
        )

    def test_get_get_object_not_found(self):
        form = {
            'short_url': 'abcde'
        }

        r = self.client.get(self.url, form)

        self.assertEqual(r.status_code, httplib.BAD_REQUEST)
        self.assertEqual(
            r.json(),
            {'message': 'failed', 'data': {}}
        )

    def test_get_success(self):
        form = {
            'short_url': self.short_url_object.short_url_path
        }
        r = self.client.get(self.url, form)

        self.assertEqual(r.status_code, httplib.OK)
        self.assertEqual(
            r.json(),
            {
                'message': 'success',
                'data': {
                    'original_url': 'https://www.fake.com',
                    'short_url_path': self.short_url_object.short_url_path,
                }
            }
        )
