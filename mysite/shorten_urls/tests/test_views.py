import http.client as httplib

from django.test import TestCase


class IndexViewTest(TestCase):

    url = '/web/index'

    def test_incorrect_url(self):
        r = self.client.get('/web/not-exists')

        self.assertEqual(r.status_code, httplib.NOT_FOUND)

    def test_get_webpage_success(self):
        r = self.client.get(self.url)

        self.assertEqual(r.status_code, httplib.OK)
        self.assertTemplateUsed(r, 'shorten_urls/index.html')