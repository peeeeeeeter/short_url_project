from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<str:short_url>', views.ShortUrlRedirectView.as_view()),
    re_path(r'^$', views.IndexView.as_view()),
]