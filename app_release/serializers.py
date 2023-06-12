from app_release.models import Env, Project, App, ReleaseConfig, ReleaseApply
from rest_framework import serializers

class EnvSerializer(serializers.ModelSerializer):
    """
    发布环境序列化类
    """
    class Meta:
        model = Env
        fields = "__all__"
        read_only_fields = ("id",) # 仅用于序列化（只读）字段，反序列化（更新）可不传

class ProjectSerializer(serializers.ModelSerializer):
    """
    项目序列化类
    """
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ("id",)

class AppSerializer(serializers.ModelSerializer):
    """
    服务器序列化类
    """
    project = ProjectSerializer(read_only=True)  #一对多加入关联表

    class Meta:
        model = App
        fields = "__all__"
        read_only_fields = ("id", )

class ReleaseConfigSerializer(serializers.ModelSerializer):
    """
    发布配置序列化类
    """
    app = AppSerializer(read_only=True) #一对多加入关联表
    env = EnvSerializer(read_only=True) #一对多加入关联表

    class Meta:
        model = ReleaseConfig
        fields = "__all__"
        read_only_fields = ("id","create_time")

# 自定义过滤器
from django_filters import rest_framework as filters

class ReleaseConfigFilter(filters.FilterSet):
    app = filters.CharFilter(field_name="app__id")
    env = filters.CharFilter(field_name="env__id")
    class Meta:
        model = ReleaseConfig
        fields = ("app", "env")

class ReleaseApplySerializer(serializers.ModelSerializer):
    """
    发布申请序列化类
    """
    release_config = ReleaseConfigSerializer(read_only=True)

    class Meta:
        model = ReleaseApply
        fields = "__all__"
        read_only_fields = ("id",)


class ReleaseApplyFilter(filters.FilterSet):
    env = filters.CharFilter(field_name="release_config__env__id")
    app = filters.CharFilter(field_name="release_config__app__id")
    class Meta:
        model = ReleaseApply
        fields = ("app", "env")