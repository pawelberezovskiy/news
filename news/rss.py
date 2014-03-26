# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from .models import News , NewsAbout, NewsAnalytics,  ArtNews, ArtArticles

class NewsFeed(Feed):
    title = _(u"Последние новости")
    link = "/news/rss/"
    description = _(u"Последние новости")

    def items(self):
        return News.active.order_by('-published_at')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description


class NewsAboutFeed(Feed):
    title = _(u"Последние новости")
    link = "/news_about/rss/"
    description = _(u"Последние новости")

    def items(self):
        return NewsAbout.active.order_by('-published_at')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description


class NewsAnalyticsFeed(Feed):
    title = _(u"Последние новости")
    link = "/news_analytics/rss/"
    description = _(u"Последние новости")

    def items(self):
        return NewsAnalytics.active.order_by('-published_at')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description


class ArtNewsFeed(Feed):
    title = _(u"Последние новости")
    link = "/news/rss/"
    description = _(u"Последние новости")

    def items(self):
        return ArtNews.active.order_by('-published_at')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

class ArtArticlesFeed(Feed):
    title = _(u"Последние статьи")
    link = "/articles/rss/"
    description = _(u"Последние статьи")

    def items(self):
        return ArtArticles.active.order_by('-published_at')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description
