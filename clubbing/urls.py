from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^load$', views.get_initial_page, name='load'),
]
