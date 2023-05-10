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
from libs.ansible_cicd import AnsibleApi
from datetime import datetime, timedelta
from cmdb.models import Server

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


class DeployView(APIView):
    def post(self, request):

        # 发布申请相关信息
        apply_id = int(request.data.get('id'))
        branch = request.data.get('branch')
        server_ids = request.data.get('server_ids')

        # 发布配置相关信息
        release_config = request.data.get('release_config')
        git_repo = release_config['git_repo']
        source_file = release_config['source_file']
        pre_checkout_script = release_config['pre_checkout_script']
        post_checkout_script = release_config['post_checkout_script']
        dst_dir = release_config['dst_dir']
        history_version_dir = release_config['history_version_dir']
        history_version_number = release_config['history_version_number']
        pre_deploy_script = release_config['pre_deploy_script']
        post_deploy_script = release_config['post_deploy_script']
        notify_id = release_config['notify_id']
        note = release_config['note']

        app_name = release_config['app']['english_name']
        # 版本标识：项目名称-应用名称-时间
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        version_id = "%s-%s-%s" %(release_config['app']['project']['english_name'], release_config['app']['english_name'], timestamp)

        # 将脚本写入文件
        with open('/tmp/pre_checkout_script.sh', 'w') as f:
            f.write(pre_checkout_script)
        with open('/tmp/post_checkout_script.sh', 'w') as f:
            f.write(post_checkout_script)
        with open('/tmp/pre_deploy_script.sh', 'w') as f:
            f.write(pre_deploy_script)
        with open('/tmp/post_deploy_script.sh', 'w') as f:
            f.write(post_deploy_script)

        git_credential_id = release_config['git_credential_id']
        if git_credential_id != 0:
            credential = Credential.objects.get(id=git_credential_id)
            git_repo = git_repo_auth(git_repo, credential.username, credential.password)

        ansible = AnsibleApi()
        # 将发布配置部分变量传递给playbook使用
        extra_vars = {
            "git_repo": git_repo,
            "branch": branch,
            "dst_dir": dst_dir,
            "history_version_dir": history_version_dir,
            "history_version_number": history_version_number,
            "app_name": app_name,
            "version_id": version_id,
            "source_file": source_file
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
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_private_key_file', value=key_file)
            else:
                ssh_user = 'root'
            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_port', value=ssh_port)
            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_user', value=ssh_user)
            # 向组内添加主机
            ansible.inventory.add_host(host=ssh_ip,group="webservers")

        playbook = os.path.join(settings.BASE_DIR, 'app_release/files/deploy.yaml')
        status = ansible.playbook_run([playbook]) # 返回一个状态码，0是正常，非0是有任务异常
        result = ansible.get_result()

        if status == 0:
            ReleaseApply.objects.filter(id=apply_id).update(status=3, deploy_result=result)
            #notify("通知：%s, 发布成功" %version_id)
            res = {'code': 200, 'msg': '发布成功', 'data': result}
        else:
            ReleaseApply.objects.filter(id=apply_id).update(status=4, deploy_result=result)
            #notify("通知：%s, 发布失败！" % version_id)
            res = {'code': 500, 'msg': '发布异常！', 'data': result}
        return Response(res)
