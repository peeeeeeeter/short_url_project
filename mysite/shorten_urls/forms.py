from django import forms


class ShortUrlForm(forms.Form):

    url_input = forms.URLField()


class UrlPreviewForm(forms.Form):

    url_input = forms.URLField()