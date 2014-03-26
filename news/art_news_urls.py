# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import ArtNewsListView,ArtNewsDetailView
from .rss import ArtNewsFeed

urlpatterns = patterns('',
	# Главная страница
	url(r'^$', ArtNewsListView.as_view(), name="news-list"),
        url(r'^rss/$', ArtNewsFeed(),name="news-rss"),
        url(r'^(?P<slug>[-\w]+)/$', ArtNewsDetailView.as_view(), name='news-detail'),
)
