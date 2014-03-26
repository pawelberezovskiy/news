# -*- coding: utf-8 -*-
import os,json,datetime,time,re
from django.core.serializers.json import DjangoJSONEncoder
from django.core import urlresolvers
from django.contrib.sites.models import get_current_site
from django.http import HttpResponseRedirect,HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response , render
from django.views.generic import ListView, DetailView
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
#from mptt.forms import TreeNodeChoiceField
#from django.utils import simplejson
#from modules.category.models import Category
from .models import News,NewsAbout,NewsAnalytics,Tag,ArtNews,ArtArticles
from .forms import NewsListForm

class NewsListViewBase(ListView):
    """
    :return: View for lot list
    """
    model = News
    type_filter = None
    template_name = 'news/news.html'
    context_object_name = 'items'
    title = None
    paginate_by = 10 #  сколько за раз выводить
    item_template = None
    ses_key_form = 'news_list_form'
    ses_key_list = 'news_list'
    __make_filter = False

    def dispatch(self, request, *args, **kwargs):
        #Инициализация формы
        if not self.request.is_ajax() and request.POST :
            self.form = NewsListForm(data = request.POST, model=self.model, type_filter = self.type_filter)
            self.__make_filter = True
        elif not self.request.is_ajax() and ( request.GET.has_key('tags') or  request.GET.has_key('name') ):
            self.form = NewsListForm(data = request.GET, model=self.model, type_filter = self.type_filter)
            self.__make_filter = True
        #Восстанавливаем из сессии
        elif self.request.session.has_key(self.ses_key_form):
            self.form = self.request.session.get(self.ses_key_form)
        else:
            self.form = NewsListForm(data = request.POST, model=self.model, type_filter = self.type_filter)


        return super(NewsListViewBase, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):

        items = []
        filters = {}
        if self.type_filter is not None: filters['status__in'] = self.type_filter

        if not self.request.is_ajax() and self.form.is_valid() and self.__make_filter:
            items = self.form.process_queryset(self.request)
            #Ограничим набор на будущее новым QS для будущего использования в JS и переходе назад
            self.request.session[self.ses_key_list]=items
            self.request.session[self.ses_key_form] = self.form
        elif self.request.GET.get('trace',False):
            # Просто идем назад
            if self.request.session.has_key(self.ses_key_list):
                items = self.request.session[self.ses_key_list]
            else:
                items = self.model.active.filter(**filters).order_by('-published_at')
                self.request.session[self.ses_key_list]=items

        elif self.request.is_ajax() and not self.request.POST and self.request.GET.has_key('page'):
            # к нам прилетел ajax запрос от пейджера. Скармливаем ему то что в сессии т.к. уже все давно выбрано
            if self.request.session.has_key(self.ses_key_list):
                items = self.request.session[self.ses_key_list]
            else:
                items = self.model.active.filter(**filters).order_by('-published_at')
                self.request.session[self.ses_key_list]=items
        else:
            #Остается только обычный GET запрос. Все просто.
            items = self.model.active.filter(**filters).order_by('-published_at')
            self.request.session[self.ses_key_list]=items
        return items

    def get_context_data(self, **kwargs):
        context = super(NewsListViewBase, self).get_context_data(**kwargs)
        # сохраняем значения нашей формы, для изменения необходимо произвести POST
        if self.request.POST or  not self.request.session.has_key(self.ses_key_form):
            self.request.session[self.ses_key_form] = NewsListForm(self.request.POST, model=self.model)

        #Список активных месяцев
        try:
            dates_current_year = int(self.form.data['year'])
        except Exception,e:
            dates_current_year = time.localtime()[0]

        if self.type_filter is not None:
            dates = self.model.active.filter(status__in=self.type_filter).dates('published_at','month')
        else:
            dates = self.model.active.all().dates('published_at','month')

        dates_arr = []
        for d in dates:
           if dates_current_year and d.year <> dates_current_year:continue
           dates_arr.append(d.month)

        #Давать ли пейджер?
        next_page = None
        if context['page_obj'].has_next() :next_page=context['page_obj'].next_page_number()

        #Собираем Теги
        if self.type_filter is not None:
            tags = Tag.objects.filter(sites=get_current_site(self.request),news_related__status__in=self.type_filter)
        else:
            tags = Tag.objects.filter(sites=get_current_site(self.request))

        context.update({
            'title': self.title,
            'dates': dates_arr,
            'form': self.form,
            'tags': tags,
            'next_page': next_page,
        })
        return context

    def post(self, request, **kwargs):
        self.show_results = False
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(object_list=self.object_list, form=self.form))

    def render_to_response(self, context, **response_kwargs):

        if self.request.is_ajax() and self.request.GET.has_key('page'):
            data = result = []

            next_page = None
            if context['page_obj'].has_next() :next_page=context['page_obj'].next_page_number()
            data = {
                    'items': [
                        (render_to_string(self.item_template,{'news':n}), ) for n in context['page_obj'].object_list],
                    'has_next': context['page_obj'].has_next(),
                    'next_page': next_page,
                }
            return HttpResponse(json.dumps(data), 'application/json')
        return super(NewsListViewBase, self).render_to_response(context, **response_kwargs)



class NewsDetailViewBase(DetailView):
    """
    :return: View for news item
    """
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'
    title = _(u"Новости")
    sitetree_current_url = "/news/"

    def get_context_data(self, **kwargs):
        context = super(NewsDetailViewBase, self).get_context_data(**kwargs)
        tags = Tag.objects.filter(sites=get_current_site(self.request))
        if self.request.session.has_key('news_form'):
            form = self.request.session.get('news_form')
        else: form = NewsListForm(data = self.request.POST, model=self.model)

        context.update({
            'title': self.title,
            'tags': tags,
            'form': form,
            'sitetree_current_url':self.sitetree_current_url,
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            data=[]
            return HttpResponse(json.dumps(data), 'application/javascript')
        return super(NewsDetailViewBase, self).render_to_response(context, **response_kwargs)


class NewsDetailView(NewsDetailViewBase):
    """
    :return: View for news item
    """
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'
    sitetree_current_url = '/news/'


class NewsListView(NewsListViewBase):
    """
    :return: View for lot list
    """
    model = News
    template_name = 'news/news.html'
    context_object_name = 'items'
    paginate_by = 10 #  сколько за раз выводить
    title =  _(u"Новости")
    item_template = 'news/includes/news_item.html'
    type_filter = [0,1,2]
    ses_key_form = 'news_list_form'
    ses_key_list = 'news_list'


class NewsAboutListView(NewsListViewBase):
    """
    :return: View for lot list
    """
    model = NewsAbout
    template_name = 'news_about/news.html'
    context_object_name = 'items'
    paginate_by = 10 #  сколько за раз выводить
    title =  _(u"СМИ о нас")
    item_template = 'news_about/includes/news_item.html'
    type_filter = [0,1,2]
    ses_key_form = 'news_about_list_form'
    ses_key_list = 'news_about_list'


class NewsAboutDetailView(NewsDetailViewBase):
    """
    :return: View for news item
    """
    model = NewsAbout
    template_name = 'news_about/news_detail.html'
    context_object_name = 'news'
    sitetree_current_url = '/news_about/'
    title =  _(u"СМИ о нас")


class NewsAnalyticsListView(NewsListViewBase):
    """
    :return: View for lot list
    """
    model = NewsAnalytics
    template_name = 'news_analytics/news.html'
    context_object_name = 'items'
    paginate_by = 10 #  сколько за раз выводить
    title =  _(u"Аналитика")
    item_template = 'news_analytics/includes/news_item.html'
    type_filter = [0,1,2]
    ses_key_form = 'news_analytics_list_form'
    ses_key_list = 'news_analytics_list'


class NewsAnalyticsDetailView(NewsDetailViewBase):
    """
    :return: View for news item
    """
    model = NewsAnalytics
    template_name = 'news_analytics/news_detail.html'
    context_object_name = 'news'
    sitetree_current_url = '/news_analytics/'
    title =  _(u"Аналитика")


class ArtArticlesListView(NewsListViewBase):
    """
    :return: View for lot list
    """
    model = ArtArticles
    template_name = 'articles/articles.html'
    context_object_name = 'items'
    paginate_by = 10 #  сколько за раз выводить
    title = _(u"Статьи")
    item_template = 'articles/includes/articles_item.html'
    ses_key_form = 'art_articles_list_form'
    ses_key_list = 'art_articles_list'


class ArtArticlesDetailView(NewsDetailViewBase):
    """
    :return: View for news item
    """
    model = ArtArticles
    template_name = 'articles/articles_detail.html'
    context_object_name = 'articles'
    title = _(u"Статьи")


class ArtNewsListView(NewsListViewBase):
    """
    :return: View for lot list
    """
    model = ArtNews
    template_name = 'news/news.html'
    context_object_name = 'items'
    paginate_by = 10 #  сколько за раз выводить
    title = _(u"Новости")
    item_template = 'news/includes/news_item.html'
    ses_key_form = 'art_news_list_form'
    ses_key_list = 'art_news_list'


class ArtNewsDetailView(NewsDetailViewBase):
    """
    :return: View for news item
    """
    model = ArtNews
    template_name = 'news/news_detail.html'
    context_object_name = 'articles'
    title = _(u"Новости")

