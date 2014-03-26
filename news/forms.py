# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
import calendar,datetime,time
from modules.news.models import News,NewsAnalytics,NewsAbout,ArtNews,ArtArticles

class NewsAdminForm(forms.ModelForm):
    class Meta:
        model = News
        widgets = {
#            'short_description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
#            'short_description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'tags': forms.CheckboxSelectMultiple,
        }

class NewsAnalyticsAdminForm(forms.ModelForm):
    class Meta:
        model = NewsAnalytics
        widgets = {
#            'short_description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
#            'short_description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'tags': forms.CheckboxSelectMultiple,
        }

class NewsAboutAdminForm(forms.ModelForm):
    class Meta:
        model = NewsAbout
        widgets = {
#            'short_description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
#            'short_description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'tags': forms.CheckboxSelectMultiple,
            'sources': forms.CheckboxSelectMultiple,
        }


class ArtNewsAdminForm(forms.ModelForm):
    class Meta:
        model = ArtNews
        widgets = {
#            'short_description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
#            'short_description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'tags': forms.CheckboxSelectMultiple,
        }

class ArtArticlesAdminForm(forms.ModelForm):
    class Meta:
        model = ArtArticles
        widgets = {
#            'short_description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
#            'short_description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_ru' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'description_en' : TinyMCE(attrs={'cols': 200, 'rows': 400}),
            'tags': forms.CheckboxSelectMultiple,
        }

class NewsListForm(forms.Form):

    choices = []
    choises_month = []
    type_filter = None

    tags  =  forms.CharField(required=False,widget=forms.HiddenInput())
    year = forms.ChoiceField(label=_(u'Год'), required=False, choices = choices )
    month = forms.IntegerField(required=False,widget=forms.HiddenInput())
    name  = forms.CharField(label=_(u'Название'), required=False, max_length=128  )

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', News)
        self.type_filter = kwargs.pop('type_filter', None)
        super(NewsListForm, self).__init__(*args, **kwargs)
        choices = []
        if self.type_filter:
            year_list =  self.model.active.filter(status__in = self.type_filter).dates('published_at','month')
        else:
            year_list =  self.model.active.all().dates('published_at','month')


        for y in year_list:
            year = (y.year,y.year)
            if year not in self.choices: self.choices.append(year)

        dates_arr = {}
        for d in year_list:
#           if d.year <> dates_current_year:continue
#           dates_arr.append(d.month)
            if not dates_arr.has_key(d.year):dates_arr[d.year] = []
            if d.month not in dates_arr[d.year]: dates_arr[d.year].append(d.month)
        self.choises_month = dates_arr

        #self.choices.sort(reverse=True)
        self.fields['year'].choices = self.choices


    def clean(self):
        cleaned_data = super(NewsListForm, self).clean()
        #year, month, day = time.localtime()[:3]
        if cleaned_data.has_key('year'):
            try:
                year = int(cleaned_data.get('year'))
                cleaned_data['year'] = year
#                if year < 2000 or year >2100:
#                    raise ValidationError("Wrong data")
            except Exception, e:
                pass


        if cleaned_data.has_key('month'):
            try:
                month = int(cleaned_data.get('month'))
                cleaned_data['month'] = month
            except Exception, e:
                pass
        return cleaned_data

    def process_queryset(self,request ,sort=True):
        filters = {}
        month = self.cleaned_data.get('month')
        year  = self.cleaned_data.get('year')
        tags  = self.cleaned_data.get('tags')
        if self.type_filter is not None: filters['status__in'] = self.type_filter

        if tags:
            filters['tags__name'] = tags
        if  year and month:
            #build data range
            nday_max = calendar.monthrange( year,month)[1]
            date_min = datetime.date (year, month, 1)
            date_max = datetime.date (year, month, 1) + datetime.timedelta (days = nday_max)
            filters['published_at__gte'] = date_min
            filters['published_at__lt']  = date_max
        elif year:
            #build data range
            date_min = datetime.date (year, 1, 1)
            date_max = datetime.date (year, 12, 31)# + datetime.timedelta (days = nday_max)
            filters['published_at__gte'] = date_min
            filters['published_at__lt']  = date_max

        result = self.model.active.filter(**filters)
        text = self.cleaned_data.get('name')

        if text:
            if request.LANGUAGE_CODE == 'ru':
                result =  self.model.search_manager_ru.search(text)
            else:
                result =  self.model.search_manager_en.search(text)
            if filters:
                filters['is_active'] = True
                result = result.filter(**filters)

        return result



