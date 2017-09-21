from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^welcome', views.load_some_riddle, name='load'),
]
