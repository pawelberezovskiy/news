# -*- coding: utf-8 -*-

from modeltranslation.translator import translator, TranslationOptions
from modules.news.models import News,NewsAbout,NewsAnalytics,Tag,ArtArticles,ArtNews,RealtySources


class NewsTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class NewsAboutTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class NewsAnalyticsTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class ArtNewsTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class ArtArticlesTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class RealtySourcesTranslationOptions(TranslationOptions):
    fields = ('name',)

class TagTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(News, NewsTranslationOptions)
translator.register(NewsAbout, NewsAboutTranslationOptions)
translator.register(NewsAnalytics, NewsAnalyticsTranslationOptions)
translator.register(ArtNews, ArtNewsTranslationOptions)
translator.register(ArtArticles, ArtArticlesTranslationOptions)
translator.register(Tag, TagTranslationOptions)
translator.register(RealtySources, RealtySourcesTranslationOptions)

