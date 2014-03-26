# -*- coding: utf-8 -*-
import re
from django.contrib import admin
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline
from .forms import NewsAdminForm,NewsAnalyticsAdminForm,NewsAboutAdminForm,ArtNewsAdminForm,ArtArticlesAdminForm
from .models import News,NewsAbout,NewsAnalytics,Tag,ArtNews,ArtArticles,RealtySources

class TagAdmin(TranslationAdmin,admin.ModelAdmin):

    search_fields = ['name',]
    list_display = ('name',)
    field_exclude = ['site',] 
    list_display_links = ('name',)

    list_per_page = 50

    class Meta:
        model = Tag

    class Media:
           js =  ('/static/grappelli_modeltranslation/js/tabbed_translation_fields.js',
                  '/main/yandex_translate.js')
           css = {'screen': ('/static/grappelli_modeltranslation/css/tabbed_translation_fields.css',)}

    def queryset(self, request):
        qs = super(TagAdmin, self).queryset(request)
        return qs.filter(sites=get_current_site(request).id)


class NewsAdminBase(TranslationAdmin,admin.ModelAdmin):
    """
    Управление лотами
    Как будут отображаться поля лота в разделе администрирования
    """
    form = NewsAdminForm
    list_display = ('name','_descr','published_at', 'created_at', 'updated_at','is_active')
    list_display_links = ('name',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['id','slug','name','status']
    list_filter = ['status','is_active','tags']
    readonly_fields = ('created_at', 'updated_at')
    # имя продукта для генерации чистой ссылки
    prepopulated_fields = {'slug': ('name_ru',)}
    #autocompleate
    raw_id_fields = ('tags',)
    autocomplete_lookup_fields = {
        'm2m': ['tags'],
    }

    fieldsets = [
        (_(u'Название'), {'fields': ['name','slug']}),
        (_(u'Описание'), {'fields': ['description']}),
        (_(u'Изображение'), {'fields': ['image']}),
        (_(u'Теги'), {'fields': ['tags']}),
        (_(u'Статус'), {'fields': ['status','published_at','is_active','updated_at','created_at']}),
        (_(u'SEO'), {'fields': ['meta_description','meta_keywords']}),
    ]

    class Media:
           js =  ('/static/grappelli_modeltranslation/js/tabbed_translation_fields.js',
                  '/main/yandex_translate.js')
           css = {'screen': ('/static/grappelli_modeltranslation/css/tabbed_translation_fields.css',)}

    def _descr(self,instance):

        short_description = ''
        rex = re.compile(r'<p.*?>(.*?)</p>',re.S|re.M)
        match = rex.match(instance.description)
        if match:
            short_description_ = match.groups()[0].strip()
            if len(short_description) < 700: short_description = short_description_

        return mark_safe('%s' % (short_description) )

    _descr.allow_tags = True


    def queryset(self, request):
        qs = super(NewsAdminBase, self).queryset(request)
        return qs.filter(sites=get_current_site(request).id)


class NewsAdmin(NewsAdminBase):
    """
    Управление лотами
    Как будут отображаться поля лота в разделе администрирования
    """
    form = NewsAdminForm
    list_display = ('name','_descr','published_at', 'created_at', 'updated_at','is_featured','is_active')
    fieldsets = [
        (_(u'Название'), {'fields': ['name','slug']}),
        (_(u'Описание'), {'fields': ['description']}),
        (_(u'Изображение'), {'fields': ['image']}),
        (_(u'Теги'), {'fields': ['tags',]}),
        (_(u'Статус'), {'fields': ['status','published_at','is_active','is_featured','updated_at','created_at']}),
        (_(u'SEO'), {'fields': ['meta_description','meta_keywords']}),
    ]

class NewsAboutAdmin(NewsAdminBase):

    fieldsets = [
        (_(u'Название'), {'fields': ['name','slug']}),
        (_(u'Описание'), {'fields': ['description']}),
        (_(u'Изображение'), {'fields': ['image']}),
        (_(u'Теги'), {'fields': ['tags','sources']}),
        (_(u'Статус'), {'fields': ['status','published_at','is_active','updated_at','created_at']}),
        (_(u'SEO'), {'fields': ['meta_description','meta_keywords']}),
    ]


    raw_id_fields = ('tags','sources')
    autocomplete_lookup_fields = {
        'm2m': ['tags','sources'],
    }

    form = NewsAboutAdminForm


class NewsAnalyticsAdmin(NewsAdminBase):

    form = NewsAnalyticsAdminForm

class ArtNewsAdmin(NewsAdminBase):
    """
    Управление лотами
    Как будут отображаться поля лота в разделе администрирования
    """
    form = ArtNewsAdminForm
    fieldsets = [
        (_(u'Название'), {'fields': ['name','slug']}),
        (_(u'Описание'), {'fields': ['description']}),
        (_(u'Изображение'), {'fields': ['image']}),
        (_(u'Теги'), {'fields': ['tags',]}),
        (_(u'Статус'), {'fields': ['status','published_at','is_active','is_featured','updated_at','created_at']}),
        (_(u'SEO'), {'fields': ['meta_description','meta_keywords']}),
    ]

class ArtArticlesAdmin(NewsAdminBase):
    """
    Управление лотами
    Как будут отображаться поля лота в разделе администрирования
    """
    form = ArtArticlesAdminForm


class RealtySourcesAdmin(TranslationAdmin):
    """
    Управление товарами
    Как будут отображаться поля объекта в разделе администрирования
    """

    list_display = ('name','created_at','updated_at','created_by','updated_by', 'is_active',)
    list_display_links = ('name',)
    search_fields = ['id','name',]
    readonly_fields = ('created_at', 'updated_at',)
    model = RealtySources

    fieldsets = [
        (_(u'Название'), {'fields': ['name']}),
        (_(u'Логотип'), {'fields': ['image']}),
        (_(u'Ссылка'), {'fields': ['link']}),
        (_(u'Прочее'), {'fields': ['is_active','created_at','updated_at','created_by','updated_by']}),
    ]

    #autocompleate
#    raw_id_fields = ('lot',)
#    autocomplete_lookup_fields = {
#        'fk': ['lot'],
#    }

    class Media:
           js =  ('/static/grappelli_modeltranslation/js/tabbed_translation_fields.js',
                  '/main/yandex_translate.js',)
           css = {'screen': ('/static/grappelli_modeltranslation/css/tabbed_translation_fields.css',)}

    def queryset(self, request):
        qs = super(RealtySourcesAdmin, self).queryset(request)
        return qs.filter(sites=get_current_site(request).id)


if settings.SITE_ID == 1:
    admin.site.register(News, NewsAdmin)
    admin.site.register(NewsAbout, NewsAboutAdmin)
    admin.site.register(NewsAnalytics, NewsAnalyticsAdmin)
    admin.site.register(RealtySources, RealtySourcesAdmin)
if settings.SITE_ID == 2:
    admin.site.register(ArtNews, ArtNewsAdmin)
    admin.site.register(ArtArticles, ArtArticlesAdmin)

admin.site.register(Tag, TagAdmin)
