#python manage.py makemigrations  && python manage.py migrate
from django.urls import path, include,re_path
from libs.token_auth import CustomAuthToken,ChangeUserPasswordView
from cmdb.views import CreateHostView,ExcelCreateHostView,HostCollectView
from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='接口文档')

#CMDB发布系统
urlpatterns = [
    re_path('^api/login/$', CustomAuthToken.as_view()),  #用户登入接口
    re_path('^api/change_password/$', ChangeUserPasswordView.as_view()), #用户密码修改接口
    re_path('^api/cmdb/create_host/$', CreateHostView.as_view()),  #创建主机接口
    re_path('^api/cmdb/excel_create_host/$', ExcelCreateHostView.as_view()),  #批量文件导入主机接口
    re_path('^api/cmdb/host_collect/$', HostCollectView.as_view()),
    re_path('^docs/$',schema_view)
]

from cmdb.views import IdcViewSet, ServerGroupViewSet, ServerViewSet
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'idc', IdcViewSet, basename="idc")   #机房接口
router.register(r'server_group', ServerGroupViewSet, basename="server_group")  #服务器组接口
router.register(r'server', ServerViewSet, basename="server")  #服务器接口

urlpatterns += [
    path('api/cmdb/', include(router.urls))   #CMDB自动api路由展示
]



# 发布系统
from app_release.views import EnvViewSet, ProjectViewSet, AppViewSet, ReleaseConfigViewSet, ReleaseApplyViewSet
router.register(r'app_release/env', EnvViewSet, basename="env")
router.register(r'app_release/project', ProjectViewSet, basename="project")
router.register(r'app_release/app', AppViewSet, basename="app")
router.register(r'app_release/config', ReleaseConfigViewSet, basename="config")
router.register(r'app_release/apply', ReleaseApplyViewSet, basename="apply")

urlpatterns += [
    path('api/app_release/', include(router.urls))   #发布系统自动api路由展示
]



#系统配置
from system_config.views import CredentialViewSet
router.register(r'credential', CredentialViewSet, basename="credential")  #私钥接口

urlpatterns += [
    path('api/config/', include(router.urls))  #凭据自动api路由展示
]


# from webhooks import views
#
# urlpatterns = [
#     re_path(r'^gitlab-webhoook/something/$', views.gitlab_webhook, name='gitlab-webhook-something'),
#     # re_path(r'^gitlab-webhoook/register/$', views.gitlab_webhook_register, name='gitlab-webhook-register'),
#     # re_path('^api/login/$', CustomAuthToken.as_view()),  # 用户登入接口
# ]
