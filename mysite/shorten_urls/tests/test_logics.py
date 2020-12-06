from unittest import mock

from django.test import TestCase
from django.utils import timezone
from requests.exceptions import RequestException

from . import MockResposne
from ..configs import URL_B62_BASE_NUM, URL_B62_OFFSET_SIZE
from ..logics import ShortUrlLogics, UrlPreviewDataLogic, decode_short_url
from ..models import ShortUrl, UrlPreviewData
from ..utils import b62_encode


class ShortUrlLogicsTest(TestCase):


    @mock.patch('shorten_urls.models.random')
    def test_get_or_create_short_url_success_by_create(self, mock_random):
        mock_random.randint.return_value = 1

        self.assertEqual(ShortUrl.objects.count(), 0)

        # first short url
        url_1 = 'https://www.google.com'
        logic = ShortUrlLogics(url_1)
        result_1 = logic.get_or_create_short_url()

        self.assertEqual(ShortUrl.objects.count(), 1)

        # second but different short url
        url_2 = 'https://www.google.com/?key=value'
        logic = ShortUrlLogics(url_2)
        result_2 = logic.get_or_create_short_url()

        self.assertEqual(ShortUrl.objects.count(), 2)

    @mock.patch('shorten_urls.models.random')
    def test_get_or_create_short_url_success_by_get(self, mock_rand):
        mock_rand.randint.return_value = 1

        self.assertEqual(ShortUrl.objects.count(), 0)

        url = 'https://www.google.com'
        short_url_object = ShortUrl.objects.create(
            original_url=url
        )

        logic = ShortUrlLogics(url)
        result_1 = logic.get_or_create_short_url()

        self.assertEqual(ShortUrl.objects.count(), 1)

        # same url
        logic = ShortUrlLogics(url)
        result_2 = logic.get_or_create_short_url()

        self.assertEqual(ShortUrl.objects.count(), 1)
        self.assertEqual(result_1, result_2)

    @mock.patch('shorten_urls.models.random')
    def test_get_or_create_short_url_success_with_larget_id(self, mock_rand):
        mock_rand.randint.return_value = 1

        url = 'https://www.google.com'
        ShortUrl.objects.create(
            id=123456789,
            original_url=url
        )
        logic = ShortUrlLogics(url)
        result = logic.get_or_create_short_url()

        expect_short_url_path = b62_encode(2 * int(1E8) + 123456789)
        self.assertEqual(result.short_url_path, expect_short_url_path)
        self.assertEqual(ShortUrl.objects.count(), 1)

    @mock.patch('shorten_urls.models.get_hashed_url_from_original_url')
    @mock.patch('shorten_urls.logics.get_hashed_url_from_original_url')
    @mock.patch('shorten_urls.models.random')
    def test_get_or_create_short_url_success_when_hash_collision_occurs(self, mock_rand,
                                                                        mock_logic_hash,
                                                                        mock_model_hash):
        mock_rand.randint.return_value = 1
        url_1 = 'https://www.google.com'
        url_2 = 'https://www.fake.com'
        mock_model_hash.return_value = mock_logic_hash.return_value = 'a' * 32

        ShortUrl.objects.create(
            original_url=url_1,
        )
        ShortUrl.objects.create(
            original_url=url_2,
        )

        logic = ShortUrlLogics(url_1)
        result = logic.get_or_create_short_url()

        expect_short_url_path = b62_encode(2 * int(1E8) + 1)
        self.assertEqual(result.short_url_path, expect_short_url_path)
        self.assertEqual(
            ShortUrl.objects.filter(hashed_url='a' * 32).count(),
            2
        )

    @mock.patch('shorten_urls.logics.ShortUrlLogics.get_or_create_short_url')
    def test_get_short_url_info(self, mock_get_or_create):
        url = 'https://www.fake.com'
        short_url = ShortUrl.objects.create(
            original_url=url,
            random_offset=1
        )
        mock_get_or_create.return_value = short_url

        logic = ShortUrlLogics(url)
        result = logic.get_short_url_info()

        expect_short_url_path = b62_encode(2 * int(1E8) + 1)
        self.assertDictEqual(
            result,
             {
                 'short_url_path': expect_short_url_path,
                 'original_url': url
             }
        )


class UrlPreviewDataLogicTest(TestCase):

    def setUp(self):
        self.url = 'https://www.fake.com'

    def test_init_will_create_short_url_object_if_not_had_one(self):
        url_preview_logic = UrlPreviewDataLogic(self.url)

        self.assertEqual(
            url_preview_logic.short_url_object.original_url,
            self.url
        )
        self.assertEqual(ShortUrl.objects.count(), 1)

    def test_init_will_get_short_url_object(self):
        short_url_object = ShortUrl.objects.create(self.url)

        url_preview_logic = UrlPreviewDataLogic(self.url)

        self.assertEqual(
            url_preview_logic.short_url_object, short_url_object
        )
        self.assertEqual(ShortUrl.objects.count(), 1)


    @mock.patch('shorten_urls.utils.requests')
    def test_get_url_preview_data_failed(self, mock_request):
        mock_request.get.side_effect = RequestException
        url_preview_logic = UrlPreviewDataLogic(self.url)

        self.assertDictEqual(
            url_preview_logic.get_url_preview_data(),
            {}
        )

    @mock.patch('shorten_urls.utils.requests')
    def test_get_url_preview_data_success(self, mock_requests):
        html = '''
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
        meta_template = '<meta property={property} content={content}>'
        meta_title = meta_template.format(
            property='"og:title"', content='"fake website"')
        meta_description = meta_template.format(
            property='"og:description"', content='"This is a fake website."')
        meta_url = meta_template.format(
            property='"og:url"', content='"https://www.fakeweb.com"')
        meta_img = meta_template.format(
            property='"og:image"', content='"https://www.fakeweb.com/img1"')

        html = html.format(
            meta_title=meta_title,
            meta_description=meta_description,
            meta_url=meta_url,
            meta_image=meta_img
        )

        mock_requests.get.return_value = MockResposne(content=html)

        url_preview_logic = UrlPreviewDataLogic(self.url)
        expect_data = {
            'title': 'fake website',
            'description': 'This is a fake website.',
            'url': 'https://www.fakeweb.com',
            'image': 'https://www.fakeweb.com/img1'
        }

        self.assertDictEqual(
            url_preview_logic.get_url_preview_data(),
            expect_data
        )

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_create_url_preview_data_failed(self, mock_get):
        mock_get.return_value = None
        url_preview_logic = UrlPreviewDataLogic(self.url)

        self.assertIsNone(url_preview_logic.create_url_preview_data())

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_create_url_preview_data_success(self, mock_get):
        mock_get.return_value = {
            'title': 'some title',
            'description': 'some description',
            'url': 'https://www.fake.com',
            'image': 'https://www.fake.com/static/img1'
        }

        url_preview_logic = UrlPreviewDataLogic(self.url)
        preview_object = url_preview_logic.create_url_preview_data()

        self.assertEqual(str(preview_object.from_url), self.url)
        self.assertEqual(preview_object.title, 'some title')
        self.assertEqual(preview_object.description, 'some description')
        self.assertEqual(preview_object.url, 'https://www.fake.com')
        self.assertEqual(preview_object.image_url, 'https://www.fake.com/static/img1')

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_update_url_preview_data_failed(self, mock_get):
        mock_get.return_value = None

        url_preview_logic = UrlPreviewDataLogic(self.url)
        self.assertIsNone(url_preview_logic.update_url_preview_data())

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_update_url_preview_data_success(self, mock_get):
        url_preview_logic = UrlPreviewDataLogic(self.url)
        UrlPreviewData.objects.create(
            from_url=url_preview_logic.short_url_object,
            title='old title', description='old description',
            url='https://www.oldurl.com',
            image_url='https://www.oldurl.com/static/img1'
        )

        mock_get.return_value = {
            'title': 'some title',
            'description': 'some description',
            'url': 'https://www.fake.com',
            'image': 'https://www.fake.com/static/img1'
        }

        new_object = url_preview_logic.update_url_preview_data()

        self.assertEqual(str(new_object.from_url), self.url)
        self.assertEqual(new_object.title, 'some title')
        self.assertEqual(new_object.description, 'some description')
        self.assertEqual(new_object.url, 'https://www.fake.com')
        self.assertEqual(new_object.image_url, 'https://www.fake.com/static/img1')

        self.assertEqual(UrlPreviewData.objects.count(), 1)

    def test_get_or_create_success_by_get(self):
        url_preview_logic = UrlPreviewDataLogic(self.url)
        UrlPreviewData.objects.create(
            from_url=url_preview_logic.short_url_object,
            title='title', description='description',
            url='https://www.fake.com',
            image_url='https://www.fake.com/static/img1'
        )

        preview_object = url_preview_logic.get_or_create_url_preview_data()
        self.assertEqual(UrlPreviewData.objects.count(), 1)

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_get_or_create_success_by_create(self, mock_get):
        mock_get.return_value = {
            'title': 'some title',
            'description': 'some description',
            'url': 'https://www.fake.com',
            'image': 'https://www.fake.com/static/img1'
        }

        url_preview_logic = UrlPreviewDataLogic(self.url)
        preview_object = url_preview_logic.get_or_create_url_preview_data()

        self.assertEqual(str(preview_object.from_url), self.url)
        self.assertEqual(preview_object.title, 'some title')
        self.assertEqual(preview_object.description, 'some description')
        self.assertEqual(preview_object.url, 'https://www.fake.com')
        self.assertEqual(preview_object.image_url, 'https://www.fake.com/static/img1')

        self.assertEqual(UrlPreviewData.objects.count(), 1)

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_get_or_create_failed_because_can_not_get_data(self, mock_get):
        mock_get.return_value = None
        url_preview_logic = UrlPreviewDataLogic(self.url)

        self.assertIsNone(url_preview_logic.get_or_create_url_preview_data())

    @mock.patch('shorten_urls.logics.timezone')
    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_url_preview_data')
    def test_get_or_create_success_and_update(self, mock_get, mock_tz):
        mock_get.return_value = {
            'title': 'some title',
            'description': 'some description',
            'url': 'https://www.fake.com',
            'image': 'https://www.fake.com/static/img1'
        }

        url_preview_logic = UrlPreviewDataLogic(self.url)

        UrlPreviewData.objects.create(
            from_url=url_preview_logic.short_url_object,
            title='old title', description='old description',
            url='https://www.oldurl.com',
            image_url='https://www.oldurl.com/static/img1',
        )

        two_days_ago = timezone.now() - timezone.timedelta(days=2)
        mock_tz.timedelta = timezone.timedelta
        mock_tz.now.return_value = two_days_ago

        new_object = url_preview_logic.get_or_create_url_preview_data()

        self.assertEqual(str(new_object.from_url), self.url)
        self.assertEqual(new_object.title, 'some title')
        self.assertEqual(new_object.description, 'some description')
        self.assertEqual(new_object.url, 'https://www.fake.com')
        self.assertEqual(new_object.image_url, 'https://www.fake.com/static/img1')

        self.assertEqual(UrlPreviewData.objects.count(), 1)

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_or_create_url_preview_data')
    def test_get_url_preview_data_info_failed(self, mock_get_or_create):
        mock_get_or_create.return_value = None

        url_preview_logic = UrlPreviewDataLogic(self.url)
        self.assertDictEqual(
            url_preview_logic.get_url_preview_data_info(),
            {}
        )

    @mock.patch('shorten_urls.logics.UrlPreviewDataLogic.get_or_create_url_preview_data')
    def test_get_url_preview_data_info_success(self, mock_get_or_create):
        url_preview_logic = UrlPreviewDataLogic(self.url)
        preview_object = UrlPreviewData.objects.create(
            from_url=url_preview_logic.short_url_object,
            title='some title', description='some description',
            url='https://www.fake.com',
            image_url='https://www.fake.com/static/img1'
        )
        last_update_time = preview_object.last_update

        mock_get_or_create.return_value = preview_object

        self.assertDictEqual(
            url_preview_logic.get_url_preview_data_info(),
            {
                'original_url': 'https://www.fake.com',
                'title': 'some title',
                'description': 'some description',
                'url': 'https://www.fake.com',
                'image_url': 'https://www.fake.com/static/img1',
                'last_update': last_update_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        )


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
