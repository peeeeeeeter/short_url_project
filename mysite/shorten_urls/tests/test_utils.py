from unittest import mock

from bs4 import BeautifulSoup
from django.test import TestCase
from requests.exceptions import RequestException

from ..configs import B62_ALPHABET
from ..utils import (BaseUrlPreview, OpenGraphPreviewMixin, UrlPreview,
                     b62_decode, b62_encode)


class B62EncoddeTest(TestCase):

    def test_number_is_string(self):
        number = '12345'
        with self.assertRaises(ValueError):
            b62_encode(number)

    def test_number_is_float(self):
        number = 123.0
        with self.assertRaises(ValueError):
            b62_encode(number)

    def test_not_positive_integer(self):
        number = 0
        with self.assertRaises(ValueError):
            b62_encode(number)

    def test_number_exceed_max_val(self):
        number = int(8 * 1e9 + 1)
        with self.assertRaises(ValueError):
            b62_encode(number)

    def test_success(self):
        number = 123456789
        result = b62_encode(number)

        self.assertEqual(result, '8m0Kx')


class B62DecodeTest(TestCase):

    def test_string_is_not_str(self):
        string = 12345
        with self.assertRaises(ValueError):
            b62_decode(string)

    def test_string_is_empty(self):
        string = ''
        with self.assertRaises(ValueError):
            b62_decode(string)

    def test_string_exceed_max_length(self):
        string = 'abcdefg'
        with self.assertRaises(ValueError):
            b62_decode(string)

    def test_success(self):
        string = '8m0Kx'
        decode = b62_decode(string)
        self.assertEqual(decode, 123456789)


class BaseUrlPreviewTest(TestCase):

    url = 'https://www.google.com'

    @mock.patch('shorten_urls.utils.requests')
    def test_fire_request_failed(self, mock_request):
        mock_request.get.side_effect = RequestException

        r = BaseUrlPreview(self.url)
        r.fire()
        self.assertFalse(r.success)

    @mock.patch('shorten_urls.utils.requests')
    def test_fire_request_success(self, mock_request):
        mock_request.get.return_value.content = '''
        <html>
            <head>
                <title>The Dormouse's story</title>
            </head>
            <body>
            <p class="title">
                <b>
                    The Dormouse's story
                </b>
            </p>
            </body>
        '''
        r = BaseUrlPreview(self.url)
        r.fire()
        self.assertTrue(r.success)


class OpenGraphPreviewMixinTest(TestCase):

    def setUp(self):
        self.parser = 'html.parser'
        self.html = '''
        <html>
            <head>
                {meta_title}
                {meta_description}
                {meta_url}
                {meta_image}
            </head>
            <body>
                <h1>hello, test</h1>
            </body>
        </html>
        '''
        self.meta_template = '<meta property={property} content={content}>'
        self.meta_title = self.meta_template.format(
            property='"og:title"', content='"Facebook"')
        self.meta_description = self.meta_template.format(
            property='"og:description"', content='"This is Facebook webpage."')
        self.meta_url = self.meta_template.format(
            property='"og:url"', content='"https://www.facebook.com"')
        self.meta_img = self.meta_template.format(
            property='"og:image"', content='"https://www.facebook.com/images/fb_icon_325x325.png"')

    def test_og_get_title_not_found(self):
        html = self.html.format(
            meta_title='',
            meta_description=self.meta_description,
            meta_url=self.meta_url, meta_image=self.meta_img
        )
        soup = BeautifulSoup(html, self.parser)

        obj = OpenGraphPreviewMixin()
        title = obj._og_get_title(soup)

        self.assertEqual(title, '')

    def test_og_get_title_found(self):
        expect_title = 'Facebook'
        title_content = '"{}"'.format(expect_title)
        meta_title = self.meta_template.format(property='"og:title"', content=title_content)

        html = self.html.format(
            meta_title=meta_title,
            meta_description=self.meta_description,
            meta_url=self.meta_url, meta_image=self.meta_img
        )
        soup = BeautifulSoup(html, self.parser)

        obj = OpenGraphPreviewMixin()
        title = obj._og_get_title(soup)

        self.assertEqual(title, expect_title)

    def test_og_get_description_not_found(self):
        html = self.html.format(
            meta_title=self.meta_title,
            meta_description='',
            meta_url=self.meta_url, meta_image=self.meta_img
        )
        soup = BeautifulSoup(html, self.parser)

        obj = OpenGraphPreviewMixin()
        description = obj._og_get_description(soup)

        self.assertEqual(description, '')

    def test_og_get_description_found(self):
        expect_description = 'This is Facebook webpage.'
        description_content = '"{}"'.format(expect_description)
        meta_description = self.meta_template.format(
            property='"og:description"', content=description_content)

        html = self.html.format(
            meta_title=self.meta_title,
            meta_description=meta_description,
            meta_url=self.meta_url, meta_image=self.meta_img
        )
        soup = BeautifulSoup(html, self.parser)

        obj = OpenGraphPreviewMixin()
        description = obj._og_get_description(soup)

        self.assertEqual(description, expect_description)

    def test_og_get_url_not_found(self):
        html = self.html.format(
            meta_title=self.meta_title, meta_description=self.meta_description,
            meta_url='',
            meta_image=self.meta_img
        )
        soup = BeautifulSoup(html, self.parser)

        obj = OpenGraphPreviewMixin()
        url = obj._og_get_url(soup)

        self.assertEqual(url, '')

    def test_og_get_url_found(self):
        expect_url = 'https://www.facebook.com'
        url_content = '"{}"'.format(expect_url)
        meta_url = self.meta_template.format(property='"og:url"', content=url_content)

        html = self.html.format(
            meta_title=self.meta_title, meta_description=self.meta_description,
            meta_url=meta_url,
            meta_image=self.meta_img
        )
        soup = BeautifulSoup(html, self.parser)

        obj = OpenGraphPreviewMixin()
        url = obj._og_get_url(soup)

        self.assertEqual(url, expect_url)

    def test_og_get_img_not_found(self):
        html = self.html.format(
            meta_title=self.meta_title, meta_description=self.meta_description,
            meta_url=self.meta_url,
            meta_image=''
        )
        soup = BeautifulSoup(html, self.parser)

        obj = OpenGraphPreviewMixin()
        img = obj._og_get_img(soup)

        self.assertEqual(img, '')

    def test_og_get_img_found(self):
        expect_img = 'https://www.facebook.com/images/fb_icon_325x325.png'
        img_content = '"{}"'.format(expect_img)
        meta_img = self.meta_template.format(property='"og:image"', content=img_content)

        html = self.html.format(
            meta_title=self.meta_title, meta_description=self.meta_description,
            meta_url=self.meta_url,
            meta_image=meta_img
        )
        soup = BeautifulSoup(html, self.parser)

        obj = OpenGraphPreviewMixin()
        img = obj._og_get_img(soup)

        self.assertEqual(img, expect_img)


class UrlPreviewTest(TestCase):

    def setUp(self):
        self.fake_url = 'https://www.fakeurl.com'
        self.html = '''
        <html>
            <head>
                {meta_title}
                {meta_description}
                {meta_url}
                {meta_image}
                {title}
            </head>
            <body>
                {h1_1}
                {h2_1}
                {p_1}
                {img_1}
                {h1_2}
                {h2_2}
                {p_2}
                {img_2}
            </body>
        </html>
        '''
        self.meta_template = '<meta property={property} content={content}>'
        self.meta_title = self.meta_template.format(
            property='"og:title"', content='"Facebook"')
        self.meta_description = self.meta_template.format(
            property='"og:description"', content='"This is Facebook webpage."')
        self.meta_url = self.meta_template.format(
            property='"og:url"', content='"https://www.facebook.com"')
        self.meta_img = self.meta_template.format(
            property='"og:image"', content='"https://www.facebook.com/images/fb_icon_325x325.png"')

        self.title = '<title>This is a title</title>'
        self.h1_1 = '<h1>This is the first h1 tag</h1>'
        self.h2_1 = '<h2>This is the first h2 tag</h2>'
        self.p_1 = '<p>This is the first p tag</p>'
        self.img_1 = '<img src="www.first.url.com">'

        self.h1_2 = '<h1>This is the second h1 tag</h1>'
        self.h2_2 = '<h2>This is the second h2 tag</h2>'
        self.p_2 = '<p>This is the second p tag</p>'
        self.img_2 = '<img src="www.second.url.com">'

    @mock.patch('shorten_urls.utils.requests')
    def test_get_title_without_fallback(self, mock_request):
        expect_title = 'Facebook'
        title_content = '"{}"'.format(expect_title)
        meta_title = self.meta_template.format(
            property='"og:title"', content=title_content
        )
        html = self.html.format(
            meta_title=meta_title,
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image=self.meta_img, title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1, img_1=self.img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_title(), expect_title)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_title_fallback_to_title_tag(self, mock_request):
        expect_title = 'my title'
        title = '<title>{}</title>'.format(expect_title)
        html = self.html.format(
            meta_title='',
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image=self.meta_img, title=title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1, img_1=self.img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_title(), expect_title)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_title_fallback_to_h1_tag(self, mock_request):
        expect_title = 'my title'
        h1_1 = '<h1>{}</h1>'.format(expect_title)
        html = self.html.format(
            meta_title='',
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image=self.meta_img,
            title='',
            h1_1=h1_1, h2_1=self.h2_1, p_1=self.p_1, img_1=self.img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_title(), expect_title)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_title_fallback_to_h2_tag(self, mock_request):
        expect_title = 'my title'
        h2_1 = '<h2>{}</h2>'.format(expect_title)
        html = self.html.format(
            meta_title='',
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image=self.meta_img,
            title='', h1_1='',
            h2_1=h2_1,
            p_1=self.p_1, img_1=self.img_1, h1_2='',
            h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_title(), expect_title)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_title_empty(self, mock_request):
        html = self.html.format(
            meta_title='',
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image=self.meta_img,
            title='', h1_1='', h2_1='',
            p_1=self.p_1, img_1=self.img_1,
            h1_2='', h2_2='',
            p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_title(), '')

    @mock.patch('shorten_urls.utils.requests')
    def test_get_description_without_fallback(self, mock_request):
        expect_description = 'This is Facebook webpage.'
        description_content = '"{}"'.format(expect_description)
        meta_description = self.meta_template.format(
            property='"og:description"', content=description_content
        )
        html = self.html.format(
            meta_title=self.meta_title,
            meta_description=meta_description,
            meta_url=self.meta_url, meta_image=self.meta_img, title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1, img_1=self.img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_description(), expect_description)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_description_fallback_to_p_tag(self, mock_request):
        expect_description = 'This is Facebook webpage.'
        p_1 = '<p>{}</p>'.format(expect_description)

        html = self.html.format(
            meta_title=self.meta_title,
            meta_description='',
            meta_url=self.meta_url, meta_image=self.meta_img, title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1,
            p_1=p_1,
            img_1=self.img_1, h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_description(), expect_description)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_description_empty(self, mock_request):
        html = self.html.format(
            meta_title=self.meta_title,
            meta_description='',
            meta_url=self.meta_url, meta_image=self.meta_img, title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1,
            p_1='',
            img_1=self.img_1, h1_2=self.h1_2, h2_2=self.h2_2,
            p_2='',
            img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_description(), '')

    @mock.patch('shorten_urls.utils.requests')
    def test_get_url_without_fallback(self, mock_request):
        expect_url = 'https://www.facebook.com'
        url_content = '"{}"'.format(expect_url)
        meta_url = self.meta_template.format(
            property='"og:url"', content=url_content
        )
        html = self.html.format(
            meta_title=self.meta_title, meta_description=self.meta_description,
            meta_url=meta_url,
            meta_image=self.meta_img, title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1, img_1=self.img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_url(), expect_url)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_url_fallback_to_request_url(self, mock_request):
        html = self.html.format(
            meta_title=self.meta_title, meta_description=self.meta_description,
            meta_url='',
            meta_image=self.meta_img, title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1, img_1=self.img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_url(), self.fake_url)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_image_without_fallback(self, mock_request):
        expect_img = 'www.img.com'
        img_content = '"{}"'.format(expect_img)
        meta_image = self.meta_template.format(
            property='"og:image"', content=img_content
        )
        html = self.html.format(
            meta_title=self.meta_title,
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image=meta_image,
            title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1, img_1=self.img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_img(), expect_img)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_image_fallback_to_img_tag(self, mock_request):
        expect_img = 'www.img.com'
        img_1 = '<img src="{}">'.format(expect_img)
        html = self.html.format(
            meta_title=self.meta_title,
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image='',
            title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1,
            img_1=img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_img(), expect_img)

    @mock.patch('shorten_urls.utils.requests')
    def test_get_image_empty(self, mock_request):
        html = self.html.format(
            meta_title=self.meta_title,
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image='',
            title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1,
            img_1='',
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2,
            img_2=''
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertEqual(preview.get_img(), '')

    @mock.patch('shorten_urls.utils.requests')
    def test_as_dict(self, mock_request):
        html = self.html.format(
            meta_title=self.meta_title,
            meta_description=self.meta_description, meta_url=self.meta_url,
            meta_image=self.meta_img, title=self.title,
            h1_1=self.h1_1, h2_1=self.h2_1, p_1=self.p_1, img_1=self.img_1,
            h1_2=self.h1_2, h2_2=self.h2_2, p_2=self.p_2, img_2=self.img_2
        )
        mock_request.get.return_value.content = html

        preview = UrlPreview(self.fake_url)
        preview.fire()
        self.assertDictEqual(
            preview.as_dict(),
            {
                'title': 'Facebook',
                'description': 'This is Facebook webpage.',
                'url': 'https://www.facebook.com',
                'image': 'https://www.facebook.com/images/fb_icon_325x325.png'
            }
        )
