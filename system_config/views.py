from rest_framework.viewsets import ModelViewSet
from system_config.serializers import CredentialSerializer,NotifySerializer
from system_config.models import Credential, Notify
#过滤、搜索和排序
from rest_framework import filters #自带的搜索排序过滤器
from django_filters.rest_framework import DjangoFilterBackend  #额外的过滤器
from rest_framework.response import Response

class CredentialViewSet(ModelViewSet):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    #过滤排序
    filter_backends = [filters.SearchFilter, filters.OrderingFilter,DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name',)  # 指定可搜索的字段
    filter_fields = ('username',)  # 指定可过滤的字段
    ordering_fields = ('id')   # 指定可排序字段


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        res = {'code': 200, 'msg': '新建凭据成功'}
        return Response(res)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        res = {'code': 200, 'msg': '修改凭据成功'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            res = {'code': 200, 'msg': '删除凭据成功'}
        except Exception as e:
            res = {'code': 500, 'msg': '该Idc名称关联其他主机，请先删除关联数据'}
        return Response(res)

class NotifyViewSet(ModelViewSet):
    queryset = Notify.objects.all()
    serializer_class = NotifySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name',)  # 指定可搜索的字段
    ordering_fields = ('id',)  # 指定可排序的字段

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        res = {'code': 200, 'msg': '创建成功'}
        return Response(res)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        res = {'code': 200, 'msg': '修改成功'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            res = {'code': 200, 'msg': '删除成功'}
        except Exception as e:
            res = {'code': 500, 'msg': '该凭据关联有其他主机，请先删除关联的主机再操作！'}
        return Response(res)