import http.client as httplib

from django.test import TestCase

from ..models import ShortUrl
from ..utils import b62_encode


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
                    'short_url_path': b62_encode(obj.id),
                    'original_url': url_input,
                },
                'message': 'success'
            }
        )