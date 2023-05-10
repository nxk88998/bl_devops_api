from ansible.plugins.callback import CallbackBase
from ansible.parsing.dataloader import DataLoader  # 用于读取YAML和JSON格式的文件
from ansible.vars.manager import VariableManager  # 用于存储各类变量信息
from ansible.inventory.manager import InventoryManager  # 用于导入资产文件
from ansible.playbook.play import Play  # 存储执行hosts的角色信息
from ansible.executor.task_queue_manager import TaskQueueManager  # ansible底层用到的任务队列
from ansible.module_utils.common.collections import ImmutableDict
from ansible import context
from ansible.executor.playbook_executor import PlaybookExecutor  # 核心类执行playbook
import ansible.constants as C
import shutil, json

# Create a callback plugin so we can capture the output
class ResultsCollectorJSONCallback(CallbackBase):
    """
    return data
    {
        "task_name1": {
            "success": {
                "192.168.1.71": {},
                "192.168.1.72": {}
            },
            "failed": {
                "192.168.1.71": {}
            },
            "unreachable": {
                "192.168.1.73": {}
            }
        }
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = {}

    # 初始化数据格式
    def __init_result_dict(self, result):
        if not result._task.name in self.result:
            self.result[result._task.name] = {
                "success": {},
                "failed": {},
                "unreachable": {}
            }

    # 执行成功
    def v2_runner_on_ok(self, result, *args, **kwargs):
        print("[%s] -> %s" % (result._task.name, result._host.get_name()))
        self.__init_result_dict(result)
        self.result[result._task.name]["success"][result._host.get_name()] = result._result

    # 执行失败
    def v2_runner_on_failed(self, result, *args, **kwargs):
        print("[%s] -> %s，执行失败！" % (result._task.name, result._host.get_name()))
        self.__init_result_dict(result)
        self.result[result._task.name]["failed"][result._host.get_name()] = result._result

    # 主机不可达
    def v2_runner_on_unreachable(self, result):
        print("[%s] -> %s，主机不可达！" % (result._task.name, result._host.get_name()))
        self.__init_result_dict(result)
        self.result[result._task.name]["unreachable"][result._host.get_name()] = result._result

class AnsibleApi():
    def __init__(self,
        connection = 'smart',  # 连接方式 local 本地方式，smart ssh方式
        remote_user = None,  # 远程用户
        ack_pass = None,  # 提示输入密码
        sudo = None, sudo_user = None, ask_sudo_pass = None,
        module_path = None,  # 模块路径，可以指定一个自定义模块的路径
        become = None,  # 是否提权
        become_method = None,  # 提权方式 默认 sudo 可以是 su
        become_user = None,  # 提权后，要成为的用户，并非登录用户
        check = False, diff = False,
        listhosts = None, listtasks = None, listtags = None,
        verbosity = 3,
        syntax = None,
        start_at_task = None,
        inventory = None
        ):
        context.CLIARGS = ImmutableDict(
            connection=connection,
            remote_user=remote_user,
            ack_pass=ack_pass,
            sudo=sudo,
            sudo_user=sudo_user,
            ask_sudo_pass=ask_sudo_pass,
            module_path=module_path,
            become=become,
            become_method=become_method,
            become_user=become_user,
            verbosity=verbosity,
            listhosts=listhosts,
            listtasks=listtasks,
            listtags=listtags,
            syntax=syntax,
            start_at_task=start_at_task,
        )
        self.loader = DataLoader()  # 数据解析器，用于解析资产清单文件（hosts）中的数据和变量。
        self.passwords = dict()  # 密码这里是必须使用的一个参数，假如通过了公钥信任，也可以给一个空字典
        self.results_callback = ResultsCollectorJSONCallback()  # 实例化回调类
        self.inventory = inventory if inventory else "localhost"
        self.inventory = InventoryManager(loader=self.loader, sources=self.inventory)  # 指定资产清单文件
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)  # 变量管理器，会资产清单文件汇总获取定义好的变量

    def command_run(self, hosts="localhost", task_list=None):
        play_source = dict(
            name="Ansible Play",
            hosts=hosts,
            gather_facts='no',
            tasks=task_list  # 任务列表
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords=self.passwords,
            stdout_callback=self.results_callback,
        )

        try:
            result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
        finally:
            # we always need to cleanup child procs and the structures we use to communicate with them
            tqm.cleanup()
            if self.loader:
                self.loader.cleanup_all_tmp_files()

    def playbook_run(self, playbook_path):
        playbook = PlaybookExecutor(
            playbooks=playbook_path,
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords=self.passwords
        )
        # 将执行的输出交给回调结果函数处理使
        playbook._tqm._stdout_callback = self.results_callback

        result = playbook.run()
        return result

    def get_result(self):
        return self.results_callback.result

if __name__ == "__main__":
    # ansible = AnsibleApi(inventory="/etc/ansible/hosts")
    # tasks = [
    #     dict(action=dict(module='shell', args='ls')),
    #     dict(action=dict(module='shell', args='df -h')),
    # ]
    # ansible.command_run(hosts="webservers", task_list=tasks)
    # print(ansible.get_result)

    # ansible.playbook_run(['/root/deploy.yaml'])
    # print(json.dumps(ansible.get_result()))

    ansible = AnsibleApi()
    pre_checkout_script = "ls"
    post_checkout_script = "ls"
    pre_deploy_script = "ls"
    post_deploy_script = "ls"

    with open('/tmp/pre_checkout_script.sh', 'w') as f:
        f.write(pre_checkout_script)
    with open('/tmp/post_checkout_script.sh', 'w') as f:
        f.write(post_checkout_script)
    with open('/tmp/pre_deploy_script.sh', 'w') as f:
        f.write(pre_deploy_script)
    with open('/tmp/post_deploy_script.sh', 'w') as f:
        f.write(post_deploy_script)

    # 设置全局变量（playbook文件用）
    ansible.variable_manager._extra_vars = {
        "git_repo": "https://gitee.com/alianglab/web",
        "branch": "master",
        "dst_dir": "/data",
        "history_version_dir": '/backup',
        "history_version_number": 7,
        "app_name": "portal",
        "version_id": "dev-ec-portal",
        "source_file": "*",
        "notify_id": 1,
        "note": "测试"
    }

    # 创建一个组
    ansible.inventory.add_group('webservers')
    # 向组内添加主机
    server_list = ['192.168.43.224']
    for ip in server_list:
        ssh_port = 22
        ssh_user = 'root'
        ssh_pass = '123123'
        # 针对主机设置变量
        ansible.variable_manager.set_host_variable(host=ip, varname='ansible_ssh_port', value=ssh_port)
        ansible.variable_manager.set_host_variable(host=ip, varname='ansible_ssh_user', value=ssh_user)
        ansible.variable_manager.set_host_variable(host=ip, varname='ansible_ssh_pass', value=ssh_pass)
        ansible.inventory.add_host(host=ip, group="webservers")
    ansible.playbook_run(["/root/deploy.yaml"])
    print(json.dumps(ansible.get_result()))