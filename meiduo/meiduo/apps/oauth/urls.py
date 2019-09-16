from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/login/$', views.QQLoginView.as_view()),
    url(r'^oauth_callback/$', views.OAuthCallBackView.as_view()),
    url(r'^sina/login/$', views.WeiBoLoginView.as_view()),
    url(r'^sina_callback/$', views.WeiBoCallBackView.as_view()),

    # http://www.meiduo.site:8000/sina_callback?code=c5599dacd1349a6e45ebbdcb5d963627
    url(r'^oauth/sina/user/$', views.SinaUserView.as_view()),
]
