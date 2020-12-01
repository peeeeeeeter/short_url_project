import http.client as httplib

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

    # TODO: mock logic
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
