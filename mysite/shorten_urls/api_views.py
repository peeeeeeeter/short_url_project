
import http.client as httplib

from django.http import JsonResponse
from django.views.generic.edit import BaseFormView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .forms import LongUrlForm
from .logics import get_short_url_logic
from .utils import b62_encode

@method_decorator(csrf_exempt, name='dispatch')
class ShortUrlView(BaseFormView):
    http_method_names = ['post']
    form_class = LongUrlForm

    def form_valid(self, form):
        response = {}

        url_input = form.cleaned_data['url_input']

        response['data'] = get_short_url_logic(url_input)
        response['message'] = 'success'

        return JsonResponse(response, status=httplib.OK)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=httplib.BAD_REQUEST)
