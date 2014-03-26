# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import ArtArticlesListView,ArtArticlesDetailView
from .rss import ArtArticlesFeed

urlpatterns = patterns('',
	# Главная страница
	url(r'^$', ArtArticlesListView.as_view(), name="articles-list"),
        url(r'^rss/$', ArtArticlesFeed(),name="articles-rss"),
        url(r'^(?P<slug>[-\w]+)/$', ArtArticlesDetailView.as_view(), name='articles-detail'),
)
