# -*- coding: utf-8 -*-

import os
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.contrib.auth.models import User
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
#full text searching
from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField

#from filebrowser.fields import FileBrowseField

class CommonActiveManager(models.Manager):
    """Класс менеджер для фильтрации активных объектов"""
    def get_query_set(self):
        if hasattr(self.model,'sites'):
            return super(CommonActiveManager, self).get_query_set().filter(is_active=True,sites=settings.SITE_ID)
        else:
            return super(CommonActiveManager, self).get_query_set().filter(is_active=True)


STATUS_CHOICES = (
    (0,_(u'Черновик')),
    (1,_(u'Опубликовано')),
    (1,_(u'Архив')),
    )

TYPE_CHOICES = (
    (0,_(u'Новости')),
    (1,_(u'О нас')),
    (2,_(u'Аналитика')),
    )


class Tag(models.Model):
    """
    A tag.
    """
    name = models.CharField(_('name'), max_length=50, unique=True, db_index=True)
    sites = models.ForeignKey(Site, default=settings.SITE_ID)

    class Meta:
        ordering = ('name',)
        verbose_name = _(u'Тег')
        verbose_name_plural = _(u'Теги')

    def __unicode__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)


class SourcesBase(models.Model):

    name = models.CharField(_(u'Название'), max_length=255,  blank=False, null=False)
    image = models.ImageField(_(u'логотип'),
                      upload_to="news_about_logos/",
                      help_text=_(u'логотип'),
                      blank=True,null=True
    )
    link = models.CharField(_(u"Ссылка"),max_length=256,blank=True,null=True)

    #Служебные
    is_active =  models.BooleanField(_(u"Активно"),default=False,blank=False,null=False)
    objects = models.Manager()
    active = CommonActiveManager()
    created_at = models.DateTimeField(_(u'Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Обновлено'), auto_now=True)
    created_by = models.ForeignKey(User, verbose_name=_(u'владелец'), default=1,
        help_text=_(u'Владелец, ответственный за этот объект.'),related_name="%(class)s_created")
    updated_by = models.ForeignKey(User, verbose_name=_(u'обновил'), default=1,
        help_text=_(u'Обновил этот объект.'),related_name="%(class)s_updated")
    sites = models.ForeignKey(Site, default=settings.SITE_ID)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)


class RealtySources(SourcesBase):

    class Meta:
        db_table = 'news_about_logos'
        ordering = ['-created_at']
        verbose_name = _(u'источники')
        verbose_name_plural = _(u'источники')


class NewsBase(models.Model):
    """Базовый класс для новостей"""
    published_at = models.DateTimeField(_(u'Опубликовать'), blank=False, null=False)
    name = models.CharField(_(u'Название'), max_length=255,  blank=False, null=False)
    slug = models.SlugField(_(u'Короткое название'), 
                            max_length=255, unique=True,
                            help_text=_(u'Уникальное название для продукта в URL, создается от имени.')
    )

#    short_description  = models.TextField(_(u'Описание для анонса'),blank=False, null=False)
    description  = models.TextField(_(u'Подробное описание'),blank=True, null=False)
    tags = models.ManyToManyField(Tag,
                            verbose_name=u"Теги",
                            blank=True,null=False,
                            related_name="%(class)s_related",
    )
    #Служебные
    is_active =  models.BooleanField(_(u"Активно"),default=False,blank=False,null=False)
    status = models.IntegerField(_(u'Тип'), choices=STATUS_CHOICES,default=1,blank=False,null=False)
    objects = models.Manager()
    active = CommonActiveManager()
    created_at = models.DateTimeField(_(u'Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Обновлено'), auto_now=True)
    meta_keywords = models.CharField(_(u'Ключевые слова META'), max_length=512,
                                     help_text=_(u'Набор слов через запятую для SEO в meta теге'),blank=True,null=True)
    meta_description = models.CharField(_(u'Meta описание'), max_length=512,
                                        help_text=_(u'Короткое описание в meta теге'),blank=True,null=True)
    sites = models.ForeignKey(Site, default=settings.SITE_ID)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        verbose_name = _(u'новость')
        verbose_name_plural = _(u'новости')

    def __unicode__(self):
        return self.name


    def get_next_absolute_url(self):
        next = News.active.filter(id__gt=self.id, status = self.status)
        if next:
            return    next[0].get_absolute_url()
        return False

    def get_prev_absolute_url(self):
        prev = News.active.filter(id__lt=self.id, status = self.status)
        if prev:
            return    prev[0].get_absolute_url()
        return False

    @permalink
    def get_absolute_url(self):
        """Генерация постоянных ссылок на новости"""
        return ('news-detail', (), {'slug': self.slug})


class News(NewsBase):

    image = models.ImageField(_(u'Изображение'),
                      upload_to="news/",
                      help_text=_(u'изображение в новости'),
                      blank=True,null=True
    )
    is_featured = models.BooleanField(_(u'Особенный'), default=False) # Отображать на главной в текущем разделе

    search_index = VectorField()

    search_manager_ru = SearchManager(
        fields=('name','description'),
        config='ru',
        search_field='search_index',
        auto_update_search_field=True
   )

    search_manager_en = SearchManager(
        fields=('name','description'),
        config='en',
        search_field='search_index',
        auto_update_search_field=True
   )

    class Meta:
        db_table = 'news'
        verbose_name = _(u'новость')
        verbose_name_plural = _(u'новости')


class NewsAbout(NewsBase):

    image = models.ImageField(_(u'Изображение'),
                      upload_to="news_about/",
                      help_text=_(u'изображение в новости'),
                      blank=True,null=True
    )
    search_index = VectorField()

    search_manager_ru = SearchManager(
        fields=('name','description'),
        config='ru',
        search_field='search_index',
        auto_update_search_field=True
   )

    search_manager_en = SearchManager(
        fields=('name','description'),
        config='en',
        search_field='search_index',
        auto_update_search_field=True
   )

    sources = models.ManyToManyField(RealtySources,
                            verbose_name=u"Источники",
                            blank=True,null=False,
                            related_name="%(class)s_related",
    )

    class Meta:
        db_table = 'news_about'
        verbose_name = _(u'СМИ о нас')
        verbose_name_plural = _(u'СМИ о нас')

    def get_next_absolute_url(self):
        next = NewsAbout.active.filter(id__gt=self.id, status = self.status)
        if next:
            return    next[0].get_absolute_url()
        return False

    def get_prev_absolute_url(self):
        prev = NewsAbout.active.filter(id__lt=self.id, status = self.status)
        if prev:
            return    prev[0].get_absolute_url()
        return False

    @permalink
    def get_absolute_url(self):
        """Генерация постоянных ссылок на новости"""
        return ('news-about-detail', (), {'slug': self.slug})

class NewsAnalytics(NewsBase):

    image = models.ImageField(_(u'Изображение'),
                      upload_to="news_analytics/",
                      help_text=_(u'изображение в новости'),
                      blank=True,null=True
    )
    search_index = VectorField()

    search_manager_ru = SearchManager(
        fields=('name','description'),
        config='ru',
        search_field='search_index',
        auto_update_search_field=True
   )

    search_manager_en = SearchManager(
        fields=('name','description'),
        config='en',
        search_field='search_index',
        auto_update_search_field=True
   )

    class Meta:
        db_table = 'news_anlytics'
        verbose_name = _(u'Аналитика')
        verbose_name_plural = _(u'Аналитика')

    def get_next_absolute_url(self):
        next = NewsAnalytics.active.filter(id__gt=self.id, status = self.status)
        if next:
            return    next[0].get_absolute_url()
        return False

    def get_prev_absolute_url(self):
        prev = NewsAnalytics.active.filter(id__lt=self.id, status = self.status)
        if prev:
            return    prev[0].get_absolute_url()
        return False

    @permalink
    def get_absolute_url(self):
        """Генерация постоянных ссылок на новости"""
        return ('news-analytics-detail', (), {'slug': self.slug})


class ArtNews(NewsBase):

    image = models.ImageField(_(u'Изображение'),
                      upload_to="news/",
                      help_text=_(u'изображение в новости'),
                      blank=True,null=True
    )

    is_featured = models.BooleanField(_(u'Особенный'), default=False) # Отображать на главной в текущем разделе

    search_index = VectorField()

    search_manager_ru = SearchManager(
        fields=('name','description'),
        config='ru',
        search_field='search_index',
        auto_update_search_field=True
   )

    search_manager_en = SearchManager(
        fields=('name','description'),
        config='en',
        search_field='search_index',
        auto_update_search_field=True
   )



    class Meta:
        db_table = 'art_news'
        verbose_name = _(u'новость')
        verbose_name_plural = _(u'новости')

class ArtArticles(NewsBase):

    image = models.ImageField(_(u'Изображение'),
                      upload_to="articles/",
                      help_text=_(u'изображение в статье'),
                      blank=True,null=True
    )
    search_index = VectorField()

    search_manager_ru = SearchManager(
        fields=('name','description'),
        config='ru',
        search_field='search_index',
        auto_update_search_field=True
   )

    search_manager_en = SearchManager(
        fields=('name','description'),
        config='en',
        search_field='search_index',
        auto_update_search_field=True
   )

    class Meta:
        db_table = 'art_articles'
        verbose_name = _(u'статью')
        verbose_name_plural = _(u'статьи')

    @permalink
    def get_absolute_url(self):
        """Генерация постоянных ссылок на новости"""
        return ('articles-detail', (), {'slug': self.slug})

    def get_next_absolute_url(self):
        next = ArtArticles.active.filter(id__gt=self.id).order_by('created_at')
        if next:
            return    next[0].get_absolute_url()
        return False

    def get_prev_absolute_url(self):
        prev = ArtArticles.active.filter(id__lt=self.id).order_by('-created_at')
        if prev:
            return    prev[0].get_absolute_url()
        return False

