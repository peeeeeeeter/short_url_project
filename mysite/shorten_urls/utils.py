import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from .configs import (B62_ALPHABET, ENCODE_NUM_MAX, REVERSE_B62_ALPHABET,
                      SHORT_URL_MAX_LEN)


def b62_encode(number):
    result = []
    alphabet_Len = len(B62_ALPHABET)

    if not isinstance(number, int):
        raise ValueError('number must be positive integer')
    elif not 1 <= number <= ENCODE_NUM_MAX:
        raise ValueError(
            'number must be in range 1 to {}, not {}'.format(ENCODE_NUM_MAX, number))

    while number:
        result.append(B62_ALPHABET[number % alphabet_Len])
        number //= alphabet_Len

    return ''.join(reversed(result))


def b62_decode(string, maxlen=SHORT_URL_MAX_LEN):

    if not isinstance(string, str):
        raise ValueError('string must be a instance of str')
    elif not 1 <= len(string) <= maxlen:
        raise ValueError(
            'string length must be in range 1 to {}'.format(SHORT_URL_MAX_LEN))

    number = 0
    for index, char in enumerate(reversed(string)):
        number += pow(62, index) * REVERSE_B62_ALPHABET[char]

    return number


class BaseUrlPreview:

    def __init__(self, url, timeout=None, headers=None, parser='html.parser',
                 *args, **kwargs):
        self.url = url
        self.timeout = timeout
        self.headers = headers
        self.parser = parser
        self._success = False

    def fire(self):
        try:
            res = requests.get(self.url,
                timeout=self.timeout, headers=self.headers)
        except RequestException:
            return

        self._success = True
        self.soup = BeautifulSoup(res.content, self.parser)

    @property
    def success(self):
        return self._success


class OpenGraphPreviewMixin:

    def _og_get_title(self, soup):
        title_tag = soup.find('meta', attrs={'property': 'og:title'})

        if title_tag:
            return title_tag.get('content', '')
        return ''

    def _og_get_description(self, soup):
        description_tag = soup.find('meta', attrs={'property': 'og:description'})

        if description_tag:
            return description_tag.get('content', '')
        return ''

    def _og_get_url(self, soup):
        url_tag = soup.find('meta', attrs={'property': 'og:url'})

        if url_tag:
            return url_tag.get('content', '')
        return ''

    def _og_get_img(self, soup):
        img_tag = soup.find('meta', attrs={'property': 'og:image'})

        if img_tag:
            return img_tag.get('content', '')
        return ''


class UrlPreview(OpenGraphPreviewMixin, BaseUrlPreview):

    title_tags = ['title', 'h1', 'h2']
    description_tags = ['p']
    img_tags = ['img']

    def _fallback_by_tags(self, soup, tags):
        for tag in tags:
            element = soup.find(tag)
            if element and element.text:
                return element.text

        return ''

    def get_title(self):
        title = self._og_get_title(self.soup)

        if not title:
            title = self._fallback_by_tags(self.soup, self.title_tags)

        return title

    def get_description(self):
        description = self._og_get_description(self.soup)

        if not description:
            description = self._fallback_by_tags(self.soup, self.description_tags)

        return description

    def get_url(self):
        url = self._og_get_url(self.soup)

        if not url:
            url = self.url

        return url

    def get_img(self):
        img = self._og_get_img(self.soup)

        if img:
            return img

        for tag in self.img_tags:
            img_tag = self.soup.find(tag)

            if img_tag and img_tag.get('src'):
                return img_tag.get('src')

        return ''

    def as_dict(self):
        title = self.get_title()
        description = self.get_description()
        url = self.get_url()
        img = self.get_img()

        return {
            'title': title,
            'description': description,
            'url': url,
            'image': img
        }
