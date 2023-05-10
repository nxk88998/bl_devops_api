import paramiko
from io import StringIO

class SSH():
    def __init__(self, ip, port, username, password=None, key=None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.key = key

    def command(self, command):
        # 绑定实例
        ssh = paramiko.SSHClient()
        # AutoAddPolicy()自动添加主机keys
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if self.password:
                ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password)
            else:
                cache = StringIO(self.key) # 将文本转为文件对象
                key = paramiko.RSAKey.from_private_key(cache)
                # 使用key登录
                ssh.connect(hostname=self.ip, port=self.port, username=self.username, pkey=key)

        except Exception as e:
            return {'code': 500, 'msg': 'SSH连接失败!错误: %s' %e}

        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read()
        error = stderr.read()

        if not error:
            ssh.close()
            return {'code': 200, 'msg': '执行命令成功！', 'data': result}
        else:
            ssh.close()
            return {'code': 500, 'msg': '执行命令失败！错误：%s' %error}

    def scp(self, local_file, remote_file):
        s = paramiko.Transport((self.ip, self.port))
        try:
            if self.password:
                s.connect(username=self.username, password=self.password)
            else:
                cache = StringIO(self.key)  # 将文本转为文件对象
                key = paramiko.RSAKey.from_private_key(cache)
                s.connect(username=self.username, pkey=key)
            sftp = paramiko.SFTPClient.from_transport(s)
        except Exception as e:
            return {'code': 500, 'msg': 'SSH连接失败！错误：%s' %e}
        try:
            sftp.put(local_file, remote_file)
            s.close()
            return {'code': 200, 'msg': '上传文件成功！'}
        except Exception as e:
            return {'code': 500, 'msg': '上传文件失败！错误：%s' % e}

    def test(self):
        result = self.command('ls /opt')
        return result

if __name__ == "__main__":
    ssh = SSH('192.168.43.224', 22, 'root','123123')
    result = ssh.command('ls /tmp')
    print(result)
    result = ssh.scp('token_auth.py', '/tmp/token_auth.py')
    print(result)