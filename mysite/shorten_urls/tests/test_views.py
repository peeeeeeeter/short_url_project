import http.client as httplib

from django.test import TestCase


class IndexViewTest(TestCase):

    url = ''

    def test_incorrect_url(self):
        r = self.client.get('/no/such/path')

        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_get_webpage_success(self):
        r = self.client.get(self.url)

        self.assertEqual(r.status_code, httplib.OK)
        self.assertTemplateUsed(r, 'shorten_urls/index.html')