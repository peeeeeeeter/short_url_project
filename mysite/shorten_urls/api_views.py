
import http.client as httplib

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import BaseFormView
from ratelimit.decorators import ratelimit

from .configs import CREATE_SHORT_URL_RATE_LIMIT
from .forms import GetOriginalUrlForm, ShortUrlForm, UrlPreviewForm
from .logics import ShortUrlLogics, UrlPreviewDataLogic, decode_short_url
from .models import ShortUrl
from .utils import b62_encode


@method_decorator(ratelimit(key='ip', rate=CREATE_SHORT_URL_RATE_LIMIT, method='POST', block=False), 'post')
@method_decorator(csrf_exempt, name='dispatch')
class ShortUrlView(BaseFormView):
    http_method_names = ['post']
    form_class = ShortUrlForm

    def post(self, request, *args, **kwargs):
        if request.limited:
            response = {
                'message': 'Rate limit exceed'
            }
            return JsonResponse(response, status=httplib.FORBIDDEN)

        return super(ShortUrlView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        response = {}

        url_input = form.cleaned_data['url_input']

        logic = ShortUrlLogics(url_input)

        response['data'] = logic.get_short_url_info()
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

        logic = UrlPreviewDataLogic(url_input)

        info = logic.get_url_preview_data_info()
        if not info:
            response['data'] = {}
            response['message'] = 'failed'
        else:
            response['data'] = {
                'title': info['title'],
                'description': info['description'],
                'url': info['url'],
                'image_url': info['image_url']
            }
            response['message'] = 'success'

        return JsonResponse(response, status=httplib.OK)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=httplib.BAD_REQUEST)


class GetOriginalUrlView(BaseDetailView):

    def get_object(self):
        form = GetOriginalUrlForm(self.request.GET)

        if form.is_valid():
            short_url = form.cleaned_data['short_url']
            url_id = decode_short_url(short_url)

            short_url_object = ShortUrl.objects.filter(id=url_id)
            return short_url_object.first()

        return

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = {}

        if self.object:
            response['data'] = {
                'original_url': self.object.original_url,
                'short_url_path': self.object.short_url_path,
            }
            response['message'] = 'success'
            return JsonResponse(response, status=httplib.OK)
        else:
            response['data'] = {}
            response['message'] = 'failed'

            return JsonResponse(response, status=httplib.BAD_REQUEST)
