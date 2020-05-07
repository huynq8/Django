'''
Created on Oct 28, 2017

@author: LAP11401-local
'''
from django.conf.urls import url
from first_app import views
urlpatterns = [
    url(r'^convertjunos/$', views.convertjunos, name='tool'),
    url(r'^hitcount/$', views.hitcount, name='tool'),
    url(r'^generate_campus/$', views.generate_campus, name='tool'),
    url(r'^result_generate_campus/$', views.result_generate_campus, name='tool'),
    url(r'^regular/$', views.regular, name='tool'),
    url(r'^searchrule/$', views.searchrule, name='tool'),
    url(r'^resultsearchrule/$', views.resultsearchrule, name='tool'),
    url(r'^parse_firewall/$', views.parse_firewall, name='tool'),
    url(r'^result_parse_firewall/$', views.result_parse_firewall, name='tool'),
    url(r'^$', views.homepage, name='homepage'),
    url(r'^(\S+)/$', views.homepage, name='tool'),
    #url(r'^resultconvertjunos', views.resultconvertjunos, name = 'resultconvertjunos'),
]
