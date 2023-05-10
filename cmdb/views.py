from rest_framework.viewsets import ModelViewSet

# 序列化
from cmdb.models import Idc, ServerGroup, Server
from cmdb.serializers import IdcSerializer, ServerGroupSerializer, ServerSerializer

# 过滤、搜索和排序
from rest_framework import filters  # 自带的搜索排序过滤器
from django_filters.rest_framework import DjangoFilterBackend  # 额外的过滤器

# 导入主机
from rest_framework.views import APIView
from rest_framework.response import Response
from system_config.models import Credential
from libs.ssh import SSH
import os, json, xlrd
from django.conf import settings
from django.http import FileResponse

class IdcViewSet(ModelViewSet):
    queryset = Idc.objects.all()
    serializer_class = IdcSerializer
    # 过滤排序
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name',)  # 指定可搜索的字段
    filter_fields = ('city',)  # 指定可过滤的字段
    ordering_fields = ('id')  # 指定可排序字段

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        res = {'code': 200, 'msg': '新建成功'}
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
            res = {'code': 500, 'msg': '该Idc名称关联其他主机，请先删除关联数据'}
        return Response(res)


class ServerGroupViewSet(ModelViewSet):
    queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer
    # 过滤排序
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name',)  # 指定可搜索的字段
    ordering_fields = ('id')  # 指定可排序字段

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        res = {'code': 200, 'msg': '新建成功'}
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
            res = {'code': 500, 'msg': '该Idc名称关联其他主机，请先删除关联数据'}
        return Response(res)

class ServerViewSet(ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    # 过滤排序
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name','hostname', 'public_ip', 'private_ip')  # 指定可搜索的字段
    filter_fields = ('idc', 'server_group')  # 指定可过滤的字段
    ordering_fields = ('id',)  # 指定可排序的字段


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        res = {'code': 200, 'msg': '新建主机成功'}
        return Response(res)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)


        # 处理多表关系
        # 一对多  获取前端提交信息将hostname为唯一id，将修改的idc数据替换到server.idc当前数据并保存
        hostname = request.data.get('hostname')
        idc_id = int(request.data.get('idc'))
        idc_obj = Idc.objects.get(id=idc_id)
        server_obj = Server.objects.get(hostname=hostname)
        server_obj.idc = idc_obj
        server_obj.save()

        # 多对多 获取传递分组的ID，获取当前server唯一关联ID，并清空分组内容，重新载入新传递的分组数据

        group_id_list = request.data.get('server_group')
        server = Server.objects.get(hostname=hostname)
        server.server_group.clear()  # 取消所有关联的组
        a1 = server.server_group
        server.server_group.add(*group_id_list)  # 重新添加
        res = {'code': 200, 'msg': '修改成功'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功'}
        return Response(res)

class CreateHostView(APIView):
    def post(self, request):
        idc_id = int(request.data.get('idc')) # 机房id
        server_group_id_list = request.data.get('server_group') # 分组id
        name = request.data.get('name')
        hostname = request.data.get('hostname')
        ssh_ip = request.data.get('ssh_ip')
        ssh_port = int(request.data.get('ssh_port'))
        credential_id = int(request.data.get('credential'))  # 凭据ID
        note = request.data.get('note')

        # 如果主机存在直接返回
        server = Server.objects.filter(hostname=hostname)
        print(server)
        print(hostname)
        if server:
            res = {'code': 500, 'msg': '主机已存在！'}
            return Response(res)


        # 判断传入凭证是密码还是秘钥
        credential = Credential.objects.get(id=credential_id)

        username = credential.username

        if credential.auth_mode == 1:
            password = credential.password
            ssh = SSH(ssh_ip, ssh_port, username, password=password)
        else:
            private_key = credential.private_key
            ssh = SSH(ssh_ip, ssh_port, username, key=private_key)
        # 测试
        result = ssh.test()

        if result['code'] == 200:
            local_file = os.path.join(settings.BASE_DIR, 'cmdb', 'files', 'host_collect.py')
            remote_file = os.path.join('/tmp/host_collect.py')
            ssh.scp(local_file, remote_file)
            result = ssh.command('python %s' %remote_file)
            print(result)

            # 服务器基本信息入库
            if result['code'] == 200:
                data = json.loads(result['data'])
                # 如果主机名与实际主机名不一致返回
                if data['hostname'] != hostname:
                    res = {'code': 500, 'msg': '输入主机名与实际主机名不一致！'}
                    return Response(res)

                idc = Idc.objects.get(id=idc_id)
                server_obj = Server.objects.create(
                    idc=idc, # 一对多，传入是一个对象
                    credential=credential,
                    name=name,
                    hostname=hostname,
                    ssh_ip=ssh_ip,
                    ssh_port=ssh_port,
                    is_verified='verified',
                    note=note
                )
                # 处理分组多对多
                for group_id in server_group_id_list:
                    group = ServerGroup.objects.get(id=group_id) # 获取分组对象
                    server_obj.server_group.add(group)  # 将服务器添加到分组

                # 服务器配置信息入库
                data = json.loads(result['data'])
                Server.objects.filter(hostname=hostname).update(**data)
                res = {'code': 200, 'msg': '添加主机成功并同步配置'}
            else:
                res = {'code': 500, 'msg': '主机配置信息同步失败！错误：%s' %result['msg']}
        else:
            res = {'code': 500, 'msg': '%s' %result['msg']}
        return Response(res)

class ExcelCreateHostView(APIView):
    # 下载主机模板文件
    def get(self, request):
        file_name = 'host.xlsx'
        file_path = os.path.join(settings.BASE_DIR, 'cmdb', 'files', file_name)
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=%s' %file_name
        # result = {'code': 200, 'msg': '获取文件成功'}
        return response
    # 导入主机模板文件
    def post(self, request):
        excel_file_obj = request.data.get('file')
        idc_id = int(request.data.get('idc'))
        server_group_id = int(request.data.get('server_group'))

        try:
            data = xlrd.open_workbook(filename=None, file_contents=excel_file_obj.read())
            print('上传文件成功')
        except Exception:
            result = {'code': 500, 'msg': '请上传Excel文件！'}
            return Response(result)
        table = data.sheets()[0]  # 打开第一个工作表
        nrows = table.nrows  # 获取表的行数
        # ncole = table.ncols  # 获取列数

        idc = Idc.objects.get(id=idc_id)
        server_group = ServerGroup.objects.get(id=server_group_id)
        try:
            for i in range(nrows): # 循环行
                if i != 0:  # 跳过标题行
                    name = table.row_values(i)[0]
                    hostname = table.row_values(i)[1]
                    ssh_ip = table.row_values(i)[2]
                    ssh_port = table.row_values(i)[3]
                    note = table.row_values(i)[4]

                    server = Server.objects.create(
                        idc=idc,
                        name=name,
                        hostname=hostname,
                        ssh_ip=ssh_ip,
                        ssh_port=ssh_port,
                        note=note
                    )
                    server.server_group.add(server_group)
            result = {'code': 200, 'msg': '导入成功'}
        except Exception as e:
            result = {'code': 500, 'msg': '导入异常！%s' %e}

        return Response(result)


class HostCollectView(APIView):
    def get(self, request):
        hostname = request.query_params.get('hostname')
        server = Server.objects.get(hostname=hostname)

        ssh_ip = server.ssh_ip
        ssh_port = server.ssh_port

        # 未绑定凭据并且没有选择凭据
        credential_id = request.query_params.get('credential_id')
        if not server.credential and not credential_id:
            result = {'code': 500, 'msg': '未发现凭据，请选择！'}
            return Response(result)
        elif server.credential:
            credential_id = int(server.credential.id)
        elif credential_id:
            credential_id = int(request.query_params.get('credential_id'))

        credential = Credential.objects.get(id=credential_id)

        username = credential.username
        if credential.auth_mode == 1:
            password = credential.password
            ssh = SSH(ssh_ip, ssh_port, username, password=password)
        else:
            private_key = credential.private_key
            ssh = SSH(ssh_ip, ssh_port, username, key=private_key)

#         # 先SSH基本测试
        test = ssh.test()
        if test['code'] == 200:
            local_file = os.path.join(settings.BASE_DIR, 'cmdb', 'files', 'host_collect.py')
            remote_file = os.path.join('/tmp/host_collect.py')
            ssh.scp(local_file, remote_file)
            result = ssh.command('python %s' %remote_file)

            if result['code'] == 200:  # 采集脚本执行成功
                # 再进一步判断客户端采集脚本提交结果

                data = json.loads(result['data'])
                print(data)
                Server.objects.filter(hostname=hostname).update(**data)

                # 更新凭据ID
                server = Server.objects.get(hostname=hostname)
                server.credential = credential
                server.is_verified = 'verified'
                server.save()

                result = {'code': 200, 'msg': '主机配置同步成功'}

            else:
                result = {'code': 500, 'msg': '主机配置同步失败！错误：%s' %result['msg']}
        else:
            result = {'code': 500, 'msg': 'SSH连接异常！错误：%s' %test['msg']}

        return Response(result)


from rest_framework.viewsets import ModelViewSet
from system_config.serializers import CredentialSerializer
from system_config.models import Credential
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class CredentialViewSet(ModelViewSet):

    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name', 'note')
    filter_fields = ('auth_mode',)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        res = {'code': 200, 'msg': '更新成功'}
        return Response(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        res = {'code': 200, 'msg': '创建成功'}
        return Response(res)

