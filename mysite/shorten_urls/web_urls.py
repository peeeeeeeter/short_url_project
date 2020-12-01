from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^(?P<short_url>[a-zA-Z0-9]{5})$', views.ShortUrlRedirectView.as_view()),
    re_path(r'^$', views.IndexView.as_view()),
]
