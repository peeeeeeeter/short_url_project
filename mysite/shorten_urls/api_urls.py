from django.urls import path, re_path

from . import api_views

urlpatterns = [
    re_path(r'^$', api_views.ShortUrlView.as_view()),
    re_path(r'^preview$', api_views.ShortUrlPreviewView.as_view()),

]