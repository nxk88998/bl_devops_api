from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from app_release.models import Env, Project, App, ReleaseConfig, ReleaseApply,HistoryVersion
from app_release.serializers import EnvSerializer, ProjectSerializer, AppSerializer, ReleaseConfigSerializer, ReleaseApplySerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from system_config.models import Credential,Notify
from libs.gitlab import Git, git_repo_auth
from django.conf import settings
import os, json
from libs.ansible_cicd import AnsibleApi
from datetime import datetime, timedelta
from cmdb.models import Server
from libs.dingding import dingtalk_msg

class EnvViewSet(ModelViewSet):
    queryset = Env.objects.all()
    serializer_class = EnvSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name','english_name')  # 指定可搜索字段
    # filter_fields = ('name',)  # 指定过滤字段

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

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('name','english_name')
    # filter_fields = ('name',)
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

class AppViewSet(ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('name','english_name')
    filter_fields = ('project',)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # 处理一对多关系
        project = request.data.get('project')
        project_obj = Project.objects.get(id=project)
        del request.data['project']
        App.objects.create(project=project_obj, **request.data)

        res = {'code': 200, 'msg': '创建成功'}
        print(res)
        return Response(res)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        # 处理一对多关系
        project = request.data.get('project')
        project_obj = Project.objects.get(id=project)
        del request.data['project']
        App.objects.filter(id=pk).update(project=project_obj, **request.data)

        res = {'code': 200, 'msg': '修改成功'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            res = {'code': 200, 'msg': '删除成功'}
        except Exception as e:
            res = {'code': 500, 'msg': '该环境关联有其他项目，请先删除关联的项目再操作！'}
        return Response(res)

class ReleaseConfigViewSet(ModelViewSet):
    queryset = ReleaseConfig.objects.all()
    serializer_class = ReleaseConfigSerializer

    filter_backends = [DjangoFilterBackend]  # 指定django_filters进行过滤
    # 指定自定义过滤器
    from .serializers import ReleaseConfigFilter
    filterset_class = ReleaseConfigFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        res = {'code': 200, 'msg': '获取成功', 'data': serializer.data}
        return Response(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        print(request.data)
        app = request.data.get('app')
        env = request.data.get('env')

        config = ReleaseConfig.objects.filter(app=app, env=env)
        if config:
            res = {'code': 500, 'msg': '该环境配置已存在！'}
            return Response(res)

        # 处理一对多关系
        app_obj = App.objects.get(id=app)
        env_obj = Env.objects.get(id=env)
        del request.data['app']
        del request.data['env']
        ReleaseConfig.objects.create(app=app_obj, env=env_obj, **request.data)

        res = {'code': 200, 'msg': '创建成功'}
        return Response(res)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        # 处理一对多关系
        app = request.data.get('app')['id']
        env = request.data.get('env')['id']
        app_obj = App.objects.get(id=app)
        env_obj = Env.objects.get(id=env)
        del request.data['app']
        del request.data['env']
        ReleaseConfig.objects.filter(id=pk).update(app=app_obj, env=env_obj, **request.data)

        res = {'code': 200, 'msg': '修改成功'}
        return Response(res)

class ReleaseApplyViewSet(ModelViewSet):
    queryset = ReleaseApply.objects.all()
    serializer_class = ReleaseApplySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('title',)

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]  # 指定django_filters进行过滤
    # 指定自定义过滤器
    from .serializers import ReleaseApplyFilter
    filterset_class = ReleaseApplyFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        res = {'code': 200, 'msg': '获取成功', 'data': serializer.data}
        return Response(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        release_config_id = request.data.get('release_config')
        title = request.data.get('title')
        branch = request.data.get('branch')
        server_ids = request.data.get('server_ids')
        note = request.data.get('note')

        ReleaseApply.objects.create(
            release_config=ReleaseConfig.objects.get(id=release_config_id),
            title=title,
            branch=branch,
            server_ids=server_ids,
            status=1,
            note=note
        )

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
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功'}
        return Response(res)

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

class DeployView(APIView):
    def post(self, request):
        print(request.data)
        # 发布申请相关信息
        branch = request.data.get('branch')
        server_ids = request.data.get('server_ids')

        # 发布配置相关信息
        config = request.data.get('release_config')
        git_repo = config['git_repo']
        source_file = config['source_file']
        pre_checkout_script = config['pre_checkout_script']
        post_checkout_script = config['post_checkout_script']
        dst_dir = config['dst_dir']
        history_version_dir = config['history_version_dir']
        history_version_number = config['history_version_number']
        pre_deploy_script = config['pre_deploy_script']
        post_deploy_script = config['post_deploy_script']
        notify_id = config['notify_id']
        note = config['note']

        # 将脚本写入文件
        with open('/tmp/pre_checkout_script.sh', 'w') as f:
            if not pre_checkout_script:
                f.write("echo '未发现检出前脚本...\n'")
            f.write(pre_checkout_script)
        with open('/tmp/post_checkout_script.sh', 'w') as f:
            if not post_checkout_script:
                f.write("echo '未发现检出后脚本...\n'")
            f.write(post_checkout_script)
        with open('/tmp/pre_deploy_script.sh', 'w') as f:
            if not pre_deploy_script:
                f.write("echo '未发现部署前脚本...\n'")
            f.write(pre_deploy_script)
        with open('/tmp/post_deploy_script.sh', 'w') as f:
            if not post_deploy_script:
                f.write("echo '未发现部署后脚本...\n'")
            f.write(post_deploy_script)

        # 版本标识：项目名称-应用名称-时间
        project_name = config['app']['project']['english_name']
        app_name = config['app']['english_name']
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        version_id = "%s-%s-%s" %(project_name, app_name, timestamp)

        ansible = AnsibleApi()
        # 设置全局变量（playbook文件用）
        ansible.variable_manager._extra_vars = {
            "git_repo": git_repo,
            "branch": branch,
            "dst_dir": dst_dir,
            "history_version_dir": history_version_dir,
            "history_version_number": history_version_number,
            "app_name": app_name,
            "version_id": version_id,
            "source_file": source_file,
            "notify_id": notify_id,
            "note": note
        }

        # 创建一个组
        ansible.inventory.add_group('webservers')
        # 向组内添加主机
        for i in server_ids:
            server_obj = Server.objects.get(id=i)
            ssh_ip = server_obj.ssh_ip
            ssh_port = server_obj.ssh_port

            if server_obj.credential:
                ssh_user = server_obj.credential.username
                if server_obj.credential.auth_mode == 1:
                    ssh_pass = server_obj.credential.password
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_pass', value=ssh_pass)
                else:
                    ssh_key = server_obj.credential.private_key
                    key_file = "/tmp/ssh_key"
                    with open(key_file, 'w') as f:
                        f.write(ssh_key)
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_private_key_file', value=key_file)
            else:
                ssh_user = 'root'

            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_port', value=ssh_port)
            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_user', value=ssh_user)
            ansible.inventory.add_host(host=ssh_ip, group="webservers")
        playbook_file = os.path.join(settings.BASE_DIR, 'app_release/files/deploy.yaml')
        status = ansible.playbook_run([playbook_file])  # 返回一个状态码，0是正常，非0是有任务异常
        #print(json.dumps(ansible.get_result()))
        result = ansible.get_result()


        if status == 0:
            ReleaseApply.objects.filter(id=request.data.get('id')).update(status=3, deploy_result=result)
            dingtalk_msg("发布通知：%s, 发布成功." %version_id)
            res = {'code': 200, 'msg': '发布成功', 'data': result}
        else:
            ReleaseApply.objects.filter(id=request.data.get('id')).update(status=4, deploy_result=result)
            dingtalk_msg("发布通知：%s, 发布异常！" % version_id)
            res = {'code': 200, 'msg': '发布异常！', 'data': result}


        # 记录发布版本
        project_id = config['app']['project']['id']
        env_id = config['env']['id']
        app_id = config['app']['id']
        title = request.data.get('title')

        HistoryVersion.objects.create(
            project_id=project_id,
            env_id=env_id,
            app_id=app_id,
            title=title,
            server_ids=server_ids,
            version_id=version_id,
            note=note
        )

        return Response(res)

class RollbackView(APIView):
    def post(self, request):
        dst_dir = request.data.get('dst_dir')
        history_version_dir = request.data.get('history_version_dir')
        # apply_id = request.data.get('apply_id')
        version_id = request.data.get('version_id')
        server_ids = request.data.get('server_ids')
        post_rollback_script = request.data.get('post_rollback_script')

        with open('/tmp/post_rollback_script.sh', 'w') as f:
            f.write(post_rollback_script)

        ansible = AnsibleApi()
        # 将发布配置部分变量传递给playbook使用
        extra_vars = {
            "dst_dir": dst_dir,
            "history_version_dir": history_version_dir,
            "version_id": version_id,
        }
        ansible.variable_manager._extra_vars = extra_vars

        # 创建一个分组
        ansible.inventory.add_group("webservers")
        for i in server_ids:
            server_obj = Server.objects.get(id=i)
            # ssh_ip、ssh_port、ssh用户名、ssh密码
            ssh_ip = server_obj.ssh_ip
            ssh_port = server_obj.ssh_port
            if server_obj.credential:
                ssh_user = server_obj.credential.username
                if server_obj.credential.auth_mode == 1:
                    ssh_pass = server_obj.credential.password
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_pass', value=ssh_pass)
                else:
                    ssh_key = server_obj.credential.private_key
                    key_file = "/tmp/.ssh_key"
                    with open(key_file, 'w') as f:
                        f.write(ssh_key)
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_private_key_file',
                                                               value=key_file)
            else:
                ssh_user = 'root'

            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_port', value=ssh_port)
            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_user', value=ssh_user)
            # 向组内添加主机
            ansible.inventory.add_host(host=ssh_ip, group="webservers")

        playbook = os.path.join(settings.BASE_DIR, 'app_release/files/rollback.yaml')
        ansible.playbook_run([playbook])
        res = {'code': 200, 'msg': '获取成功', 'data': ansible.get_result()}

class ApplyEchartView(APIView):
    def get(self, request):
        end = datetime.now()
        start = end - timedelta(30)
        queryset = ReleaseApply.objects.filter(release_time__range=[start, end])
        import pandas as pd
        date_range = pd.date_range(start=datetime.strftime(start, "%Y-%m-%d"), end=datetime.strftime(end, "%Y-%m-%d"))

        x_data = []
        y_fail_data = []
        y_success_data = []

        for date in date_range:
            date = datetime.strftime(date, "%Y-%m-%d")
            x_data.append(date)
            y_fail_n = 0
            y_success_n = 0
            for i in queryset:
                date_time = datetime.strftime(i.release_time, "%Y-%m-%d")
                if date == date_time:
                    if i.status == 3:  # 3 发布成功
                        y_success_n += 1
                    elif i.status == 4:  # 4 发布失败
                        y_fail_n += 1
            y_fail_data.append(y_fail_n)
            y_success_data.append(y_success_n)
        data = {'y_fail_data': y_fail_data, 'y_success_data': y_success_data, 'x_data': x_data}
        res = {'data': data, 'code': 200, 'msg': '成功'}
        return Response(res)

