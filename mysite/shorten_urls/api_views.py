
import http.client as httplib

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import BaseFormView

from .forms import ShortUrlForm, UrlPreviewForm
from .logics import ShortUrlLogics
from .utils import b62_encode


@method_decorator(csrf_exempt, name='dispatch')
class ShortUrlView(BaseFormView):
    http_method_names = ['post']
    form_class = ShortUrlForm

    def form_valid(self, form):
        response = {}

        url_input = form.cleaned_data['url_input']

        logic = ShortUrlLogics(url_input)

        response['data'] = logic.get_or_create_short_url()
        response['message'] = 'success'

        return JsonResponse(response, status=httplib.OK)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=httplib.BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ShortUrlPreviewView(BaseFormView):
    http_method_names = ['post']
    form_class = UrlPreviewForm

    def form_valid(self, form):
        response = {}

        url_input = form.cleaned_data['url_input']

        logic = ShortUrlLogics(url_input)

        response['data'] = logic.get_short_url_preview_data()
        response['message'] = 'success'

        return JsonResponse(response, status=httplib.OK)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=httplib.BAD_REQUEST)
