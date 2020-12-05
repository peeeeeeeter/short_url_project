from django import forms

from .configs import SHORT_URL_MAX_LEN
from .logics import decode_short_url


class ShortUrlForm(forms.Form):

    url_input = forms.URLField()


class UrlPreviewForm(forms.Form):

    url_input = forms.URLField()


class GetOriginalUrlForm(forms.Form):

    short_url = forms.CharField(
        min_length=SHORT_URL_MAX_LEN, max_length=SHORT_URL_MAX_LEN)


    def clean_short_url(self):
        short_url = self.cleaned_data['short_url']

        try:
            decode_short_url(short_url)
        except (KeyError, ValueError):
            raise forms.ValidationError(
                'invalid short url'
            )

        return short_url
