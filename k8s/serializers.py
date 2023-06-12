from k8s.models import K8sAuth
from rest_framework import serializers

class K8sAuthSerializer(serializers.ModelSerializer):
    """
    发布环境序列化类
    """
    class Meta:
        model = K8sAuth
        fields = "__all__"
        read_only_fields = ("id",) # 仅用于序列化（只读）字段，反序列化（更新）可不传
