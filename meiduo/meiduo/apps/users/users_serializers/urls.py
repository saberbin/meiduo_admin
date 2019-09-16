from django.conf.urls import url
from . import views
from rest_framework import routers

urlpatterns = [
    url(r'^register/$', views.UserRegisterView.as_view()),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.UserPhoneCountView.as_view()),
    url(r'^login/$', views.UserLoginView.as_view()),
    url(r'^logout/$', views.UserLogoutView.as_view()),
    url(r'^find_password/$', views.UserFPView.as_view()),
    url(r'^users/(?P<user_id>\d+)/password/$', views.UserFPChangePasswordView.as_view()),

    url(r'^info/$', views.UserInfoView.as_view()),
    url(r'^emails/$', views.UsereEmailsView.as_view()),
    url(r'^emails/verification/$', views.UserEmailVerificationView.as_view()),
    url(r'^addresses/$', views.UserAddressView.as_view()),
    url(r'^addresses/create/$', views.UserAddressCreateView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/$', views.UserAddressUpdateView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.UserAddressDefaultView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UserAddressTitleView.as_view()),
    url(r'^password/$', views.UserChangePasswordView.as_view()),

]


# user address viewset
router = routers.DefaultRouter()
router.register(r'permission/admins', views.UserAddressViewSet, base_name='address')
urlpatterns += router.urls
# print(router.urls)
