import http.client as httplib

from django.test import TestCase

from ..models import ShortUrl
from ..utils import b62_encode


class IndexViewTest(TestCase):

    url = ''

    def test_incorrect_url(self):
        r = self.client.get('/no/such/path')

        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_get_webpage_success(self):
        r = self.client.get(self.url)

        self.assertEqual(r.status_code, httplib.OK)
        self.assertTemplateUsed(r, 'shorten_urls/index.html')


class ShortUrlRedirectViewTest(TestCase):

    error_message = '<h1>404 Not Found</h1>'

    def setUp(self):
        self.short_url_object = ShortUrl.objects.create(
            original_url='https://www.fake.com',
            random_offset=1
        )

    def test_short_url_too_long(self):
        r = self.client.get('/abcdefg')
        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_short_url_too_short(self):
        r = self.client.get('/abcd')
        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_short_url_contains_invalid_chars(self):
        r = self.client.get('/abcd@')
        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_short_url_not_exist(self):
        short_url_path = b62_encode(int(1E8) + 9999)
        r = self.client.get('/{}'.format(short_url_path))

        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_success(self):
        short_url_path = self.short_url_object.short_url_path
        r = self.client.get('/{}'.format(short_url_path))

        self.assertRedirects(
            r,
            self.short_url_object.original_url,
            fetch_redirect_response=False
        )
