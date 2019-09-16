from django.conf.urls import url
from .home import home_views
from .user import user_views
from .good import sku_views, spu_views, spu_specs_views, channels_views, brands_views, orders_views
from .good import image_views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
from meiduo_admin.sysmanage import permission_views


urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^statistical/total_count/$', home_views.UserTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', home_views.UserDayIncrementCountView.as_view()),
    url(r'^statistical/day_active/$', home_views.UserDayActiveCountView.as_view()),
    url(r'^statistical/day_orders/$', home_views.UserDayOrdersCountView.as_view()),
    url(r'^statistical/goods_day_views/$', home_views.UserGoodsDayCountView.as_view()),
    url(r'^statistical/month_increment/$', home_views.UserMonthIncrementCountView.as_view()),
    url(r'^users/$', user_views.UserView.as_view()),
    url(r'^skus/categories/$', sku_views.SKUCategoryView.as_view()),
    url(r'^goods/simple/$', sku_views.SKUSPUSimpleView.as_view()),

    url(r'^goods/(?P<spu_id>\d+)/specs/$', sku_views.SPUSpecificationView.as_view()),
    url(r'^goods/brands/simple/$', spu_views.SPUBrandSimpleView.as_view()),
    url(r'^goods/channel/categories/$', spu_views.SPUCategoryView.as_view()),
    url(r'^goods/channel/categories/(?P<category_id>\d+)/$', spu_views.SPUSubsCategoryView.as_view()),
    # url(r'^goods/images/$', spu_views.SPUImageUploadView.as_view()),

    # spec option 路由
    url(r'^goods/specs/simple/$', spu_specs_views.SpecsSimpleView.as_view()),
    # 频道
    url(r'^goods/categories/$', channels_views.ChannelsCatrgoryView.as_view()),
    url(r'^goods/channel_types/$', channels_views.ChannelsTypeView.as_view()),
    # 图片ｓｋｕ列表
    url(r'skus/simple/$', image_views.SKUImageSimpleView.as_view()),

    # order　订单详情展示
    # url(r'orders/(?P<pk>\d+)/$', orders_views.OrderDetailView.as_view()),

    # permission
    url(r'permission/content_types/$', permission_views.PermissionContentTypeView.as_view()),
    # permission group simple
    url(r'permission/simple/$', permission_views.PermissionGroupSimpleView.as_view()),
    url(r'ermission/groups/simple/$', permission_views.PermissionUserGroupSimpleView.as_view()),

]
# # order 订单管理orders
# router = routers.DefaultRouter()
# router.register(r'orders', orders_views.OrdersViewSet, base_name='orders')
# urlpatterns += router.urls

# order 订单管理orders
router = routers.DefaultRouter()
router.register(r'orders', orders_views.OrdersReaderOnlyViewSet, base_name='orders')
urlpatterns += router.urls

# 图片管理
router = routers.DefaultRouter()
router.register(r'skus/images', image_views.SKUImagesViewSet, base_name='images')
urlpatterns += router.urls

router = routers.SimpleRouter()
router.register(r'skus', sku_views.SKUViewSet, base_name='skus')
urlpatterns += router.urls

# spu规格表管理
# PS:如果"goods/specs"此路由在"goods"路由后面，会匹配不到此路由，需要注意
router = routers.DefaultRouter()
router.register(r'goods/specs', spu_specs_views.SPUSpecViewSet, base_name='specs')
urlpatterns += router.urls

# SPU option管理
router = routers.SimpleRouter()
router.register(r'specs/options', spu_specs_views.SPecsOptionViewSet, base_name='options')
urlpatterns += router.urls

# goods channels 路由
router = routers.SimpleRouter()
router.register(r'goods/channels', channels_views.ChannelsViewSet, base_name='channels')
urlpatterns += router.urls

# brands管理路由
router = routers.SimpleRouter()
router.register(r'goods/brands', brands_views.BrandsViewSet, base_name='brands')
urlpatterns += router.urls

# SPU
router = routers.SimpleRouter()
router.register(r'goods', spu_views.SPUViewSet, base_name='goods')
urlpatterns += router.urls

# permission管理
router = routers.DefaultRouter()
router.register(r'permission/perms', permission_views.PermissionViewSet, base_name='author')
urlpatterns += router.urls

# permission group
router = routers.DefaultRouter()
router.register(r'permission/perms', permission_views.PermissionViewSet, base_name='author')
urlpatterns += router.urls

# 用户组权限
router = routers.DefaultRouter()
router.register(r'permission/groups', permission_views.PermissionGroupsViewSet, base_name='groups')
urlpatterns += router.urls

# permission/admins
router = routers.DefaultRouter()
router.register(r'permission/admins', permission_views.PermissionAdminViewSet, base_name='admins')
urlpatterns += router.urls

