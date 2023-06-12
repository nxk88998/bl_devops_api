from kubernetes import client, config

config.kube_config.load_kube_config(config_file="admin.conf")
# 获取API的CoreV1Api版本对象
# v1 = client.CoreV1Api()
#
# v2 = client.CoreApi()



try:
    print("3333333333333")
    v1 = client.CoreApi()  # 查看k8s版本，由此验证token是否有效
    v2 = v1.get_api_versions()
    print(v2)
    res = {'code': 200, 'msg': '导入集群成功'}
    print(res)
except Exception as e:
    # return False
    res = {'code': 500, 'msg': '导入集群验证失败'}
    print(res)




# for ns in v1.list_namespace().items:
#     print(ns.metadata.name)


# json_content = yaml.load(user_obj, Loader=yaml.FullLoader)  # 将yaml转为json
# config.load_kube_config_from_dict(json_content)
# core_api = client.CoreApi()