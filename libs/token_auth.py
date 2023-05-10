from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

#修改密码
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import AllowAny



class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            res = {'code': 200,'msg': '认证成功','token': token.key,'username': user.username,}
            return Response(res)
        else:
            res = {'code': 500,'msg': '用户名或密码错误！',}
            return Response(res)


class ChangeUserPasswordView(APIView):
    #permission_classes = (AllowAny,)  # AllowAny 允许所有用户（登录不需要身份认证）
    def post(self, request):
        print(request.data)
        username = request.data.get("username")  #前端post请求给你的用户名称
        old_password = request.data.get("old_password")  # 前端修改新密码二次是否一致
        new_password = request.data.get("new_password")
        try:
            user = User.objects.get(username=username)  #User模块判断用户在数据库中是否存在
        except:
            res = {'code': 500, 'msg': '用户不存在！'}
            return Response(res)

        if check_password(old_password, user.password):
            user.password = make_password(new_password)
            user.save()
            res = {'code': 200, 'msg': '修改密码成功'}
        else:
            res = {'code': 500, 'msg': '原密码不正确！'}
        return Response(res)
