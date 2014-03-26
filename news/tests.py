# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse
import datetime

from .models import News


class  NewsTestCase(TestCase):
    def setUp(self):
        self.first = News.objects.create( published_at=datetime.datetime.now(), name_ru = u'Проверка',name_en='Testing',slug = "test", description_ru=u'Проверка_test_'*500 ,status  = True , sites = 1 )
        self.second = News.objects.create( published_at=datetime.datetime.now(), name_ru = u'Проверка1',name_en='Testing1',slug = "test1", description_ru=u'Проверка_test_'*500 ,status  = True , sites = 1 )

    def testCreating(self):
        self.assertEqual(self.first.description_ru, 'Проверка_test_'*500)

    def test_term_view(self):
        response = self.client.get(reverse("news-list"))
        self.assertTrue(response.status_code == 200)
