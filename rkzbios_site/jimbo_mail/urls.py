from django.conf.urls import patterns, url

from .views import unsubscribe, subscribe, confirm, subsciption_succeeded

urlpatterns = patterns('',
    url(r'^/unsubscribe/(?P<token>[0-9a-f-]+)/$', unsubscribe,name ='wnd-email-unsubscribe'),
    url(r'^/confirm/(?P<token>[0-9a-f-]+)/$', confirm, name = 'wnd-email-confirm-subscription'),
    url(r'^/subscribe/$', subscribe, name = 'wnd-subscribe-email'),
    url(r'^/subsciption_succeeded/$', subsciption_succeeded, name = 'wnd-email-subsciption-succeeded'),
)
