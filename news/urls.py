# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import NewsListView,NewsDetailView
from .rss import NewsFeed

urlpatterns = patterns('',
	# Главная страница
	url(r'^$', NewsListView.as_view(), name="news-list"),
        url(r'^rss/$', NewsFeed(),name="news-rss"),
        url(r'^(?P<slug>[-\w]+)/$', NewsDetailView.as_view(), name='news-detail'),
)
