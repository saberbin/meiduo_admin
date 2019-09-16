from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^image_codes/(?P<image_code_id>.+)/$', views.ImageCodeView.as_view()),
    url(r'sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/$', views.FindPasswordCheckView.as_view()),
    url(r'^sms_codes/$', views.FindPasswordSendSmsCodeView.as_view()),
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/password/token/$', views.FPSmsCodeVCheckView.as_view()),
]
