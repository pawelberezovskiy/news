# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import NewsAboutListView,NewsAboutDetailView
from .rss import NewsAboutFeed

urlpatterns = patterns('',
	# Главная страница
	url(r'^$', NewsAboutListView.as_view(), name="news-about-list"),
        url(r'^rss/$', NewsAboutFeed(),name="news-about-rss"),
        url(r'^(?P<slug>[-\w]+)/$', NewsAboutDetailView.as_view(), name='news-about-detail'),
)
