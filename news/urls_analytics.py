# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import NewsAnalyticsListView,NewsAnalyticsDetailView
from .rss import NewsAnalyticsFeed

urlpatterns = patterns('',
	# Главная страница
	url(r'^$', NewsAnalyticsListView.as_view(), name="news-analytics-list"),
        url(r'^rss/$', NewsAnalyticsFeed(),name="news-analytics-rss"),
        url(r'^(?P<slug>[-\w]+)/$', NewsAnalyticsDetailView.as_view(), name='news-analytics-detail'),
)
