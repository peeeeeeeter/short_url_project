from django import forms


class LongUrlForm(forms.Form):

    url_input = forms.URLField()