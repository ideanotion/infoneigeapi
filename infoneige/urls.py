from django.conf.urls import patterns, include, url
from rest_framework import routers
from api import views
from api.models import *
from django.contrib import admin

from rest_framework.routers import Route, SimpleRouter

admin.autodiscover()
router = routers.SimpleRouter()
router.register(r'streets', views.StreetList.as_view(), base_name='Street')
router.register(r'cotes', views.StreetList.as_view(), base_name='Cote')

urlpatterns = patterns('api.views',
	#url(r'^', include(router.urls)),
	url(r'^$', 'api_root'),
	url(r'^load/street/$', views.street_load, name='load-street'),
	url(r'^load/cote/$', views.cote_load, name='load-cote'),
	url(r'^load/wsdl/$', views.wsdl_load, name='load-wsdl'),
	url(r'^streets/$', views.StreetList.as_view(), name='Street-list'),
	url(r'^streets/(?P<id>[0-9]+)/$', views.StreetDetails.as_view(), name='Street-detail'),
	url(r'^cotes/$', views.CoteList.as_view(), name='Cote-list'),
	url(r'^cotes/(?P<id>[0-9]+)/$', views.CoteDetails.as_view(), name='Cote-detail'),
)