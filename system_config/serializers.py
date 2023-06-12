from system_config.models import Credential, Notify
from rest_framework import serializers

class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = '__all__'
        read_only_fields = ('id', )  # 只用于序列化（读）

class NotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Notify
        fields = "__all__"
        read_only_fields = ("id", )
