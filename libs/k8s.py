from kubernetes import client,config
from k8s.models import K8sAuth
import yaml
from django.shortcuts import redirect

apiserver = "https://192.168.1.71:6443"

def auth_check(auth_type, token=None):
    if auth_type == "token":
        configuration = client.Configuration()
        configuration.host = apiserver # APISERVER地址
        # ca_file = os.path.join(os.getcwd(), "ca.crt")  # K8s集群CA证书（/etc/kubernetes/pki/ca.crt）
        # configuration.ssl_ca_cert = ca_file
        configuration.verify_ssl = False  # 启用证书验证
        configuration.api_key = {"authorization": "Bearer " + token}
        client.Configuration.set_default(configuration)
        core_api = client.CoreApi()
        try:
            core_api.get_api_versions()  # 查看k8s版本，由此验证token是否有效
            return True
        except Exception as e:
            return False
    elif auth_type == "kubeconfig":
        user_obj = K8sAuth.objects.get(token=token)
        try:
            json_content = yaml.load(user_obj.content, Loader=yaml.FullLoader)  # 将yaml转为json
        except:
            return False
        config.load_kube_config_from_dict(json_content)
        core_api = client.CoreApi()
        try:
            core_api.get_api_versions()  # 查看k8s版本，由此验证token是否有效
            return True
        except Exception as e:
            return False

# 视图登录认证装饰器
def self_login_required(func):
    def inner(request):
        is_login = request.session.get('is_login', False)
        if not is_login:
            return redirect('/login')
        else:
            return func(request)
    return inner

# 加载连接k8s api的认证配置
def load_auth_config(auth_type, token):
    if auth_type == "token":
        configuration = client.Configuration()
        configuration.host = apiserver # APISERVER地址
        # ca_file = os.path.join(os.getcwd(), "ca.crt")  # K8s集群CA证书（/etc/kubernetes/pki/ca.crt）
        # configuration.ssl_ca_cert = ca_file
        configuration.verify_ssl = False  # 启用证书验证
        configuration.api_key = {"authorization": "Bearer " + token}
        client.Configuration.set_default(configuration)
    elif auth_type == "kubeconfig":
        user_obj = K8sAuth.objects.get(token=token)
        json_content = yaml.load(user_obj.content, Loader=yaml.FullLoader)  # 将yaml转为json
        config.load_kube_config_from_dict(json_content)

# 资源创建时间格式化
from datetime import date, timedelta
def timestamp_format(timestamp):
    c = timestamp + timedelta(hours=8)
    t = date.strftime(c, '%Y-%m-%d %H:%M:%S')
    return t