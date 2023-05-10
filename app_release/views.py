from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from app_release.models import Env, Project, App, ReleaseConfig, ReleaseApply
from app_release.serializers import EnvSerializer, ProjectSerializer, AppSerializer, ReleaseConfigSerializer, ReleaseApplySerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from system_config.models import Credential
from libs.gitlab import Git, git_repo_auth
from django.conf import settings
import os, json

class EnvViewSet(ModelViewSet):
    queryset = Env.objects.all()
    serializer_class = EnvSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name',)  # 指定可搜索字段
    # filter_fields = ('name',)  # 指定过滤字段

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('name',)
    # filter_fields = ('name',)

class AppViewSet(ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('name',)
    filter_fields = ('project',)

class ReleaseConfigViewSet(ModelViewSet):
    queryset = ReleaseConfig.objects.all()
    serializer_class = ReleaseConfigSerializer

class ReleaseApplyViewSet(ModelViewSet):
    queryset = ReleaseApply.objects.all()
    serializer_class = ReleaseApplySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('title',)
    #filter_fields = ('status',)


class GitView(APIView):
    def get(self, request):
        git_repo = request.query_params.get('git_repo')
        git_credential_id = int(request.query_params.get('git_credential_id'))

        # 未携带凭据访问仓库
        if git_credential_id:
            cred_obj = Credential.objects.get(id=git_credential_id)
            username = cred_obj.username
            password = cred_obj.password
            git_repo = git_repo_auth(git_repo, username, password)
            git = Git(git_repo, os.path.join(settings.BASE_DIR, "repos"))
            git.get_repo()
            branch = git.get_branch()
            res = {'code': 200, 'msg': '获取成功', 'data': branch}
            return Response(res)

        git = Git(git_repo, os.path.join(settings.BASE_DIR, "repos"))
        git.get_repo()
        branch = git.get_branch()
        res = {'code': 200, 'msg': '获取成功', 'data': branch}
        return Response(res)
