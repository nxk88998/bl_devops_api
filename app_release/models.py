from django.db import models

class Env(models.Model):
    name = models.CharField(max_length=30, verbose_name="环境名称")
    english_name = models.CharField(max_length=30, unique=True, verbose_name="英文名称")
    note = models.TextField(null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'app_release_env'
        verbose_name_plural = '环境管理'
        ordering = ('-id',)
    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=30, verbose_name="项目名称")
    english_name = models.CharField(max_length=30, unique=True, verbose_name="英文名称")
    note = models.TextField(null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'app_release_project'
        verbose_name_plural = '项目管理'
        ordering = ('-id',)
    def __str__(self):
        return self.name

class App(models.Model):
    name = models.CharField(max_length=30, verbose_name="应用名称")
    english_name = models.CharField(max_length=30, unique=True, verbose_name="英文名称")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name="所属项目")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'app_release_app'
        verbose_name_plural = '应用管理'
        ordering = ('-id',)
    def __str__(self):
        return self.name

class ReleaseConfig(models.Model):
    app = models.ForeignKey(App, on_delete=models.PROTECT, verbose_name="应用名称")
    env = models.ForeignKey(Env, on_delete=models.PROTECT, verbose_name="发布环境")
    server_ids = models.JSONField(max_length=100, verbose_name="目标主机")
    git_repo = models.CharField(max_length=100, verbose_name="Git仓库")
    git_credential_id = models.IntegerField(null=True, blank=True, verbose_name="凭据ID")
    notify_id = models.IntegerField(null=True, blank=True,verbose_name="消息通知ID")
    note = models.TextField(null=True, blank=True, verbose_name="备注")

    source_file = models.CharField(max_length=200, default="*", verbose_name="源文件")
    global_variables = models.TextField(null=True, blank=True, verbose_name="自定义全局变量")
    pre_checkout_script = models.TextField(null=True, blank=True, verbose_name="代码检出前执行脚本")
    post_checkout_script = models.TextField(null=True, blank=True, verbose_name="代码检出后执行脚本")

    dst_dir = models.CharField(max_length=100, verbose_name="服务器部署路径")
    history_version_dir = models.CharField(max_length=100, verbose_name="历史版本路径")
    history_version_number = models.IntegerField(default=7, verbose_name="历史版本保留数")
    pre_deploy_script = models.TextField(null=True, blank=True, verbose_name="部署前执行脚本")
    post_deploy_script = models.TextField(null=True, blank=True, verbose_name="部署后执行脚本")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'app_release_config'
        verbose_name_plural = '发布配置'
        ordering = ('-id',)
    def __str__(self):
        return self.app

class ReleaseApply(models.Model):
    release_config = models.ForeignKey(ReleaseConfig, on_delete=models.PROTECT, verbose_name="发布配置")
    title = models.CharField(max_length=30, verbose_name="发布标题")
    branch = models.CharField(max_length=100, verbose_name="代码分支")
    server_ids = models.JSONField(max_length=100, verbose_name="目标主机")
    version_id = models.CharField(max_length=30, unique=True, verbose_name="版本标识")  # 自动生成，例如应用名称-分支-时间
    status_choice = (
        (1, "待发布"),
        (2, "发布中"),
        (3, "发布成功"),
        (4, "发布异常")
    )
    status = models.IntegerField(choices=status_choice, default=1, verbose_name="发布状态")
    note = models.TextField(null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    release_time = models.DateTimeField(auto_now=True, verbose_name="发布时间")

    class Meta:
        db_table = 'app_release_apply'
        verbose_name_plural = '发布申请'
        ordering = ('-id',)
    def __str__(self):
        return self.title


class Notify(models.Model):
    notify_choice = (
        (1, "邮件"),
        (2, "钉钉"),
        (3, "企业微信")
    )
    name = models.CharField(max_length=50, verbose_name="名称")
    notify_mode = models.IntegerField(choices=notify_choice, default=1, verbose_name="通知方式")
    email_recipient = models.CharField(max_length=200, null=True, blank=True, verbose_name="邮件收件人")
    dingding_webhook = models.CharField(max_length=100, null=True, blank=True, verbose_name="钉钉Webhook")
    weixin_webhook = models.CharField(max_length=100, null=True, blank=True, verbose_name="企业Webhook")
    note = models.TextField(null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "system_config_notify"
        verbose_name_plural = "通知管理"
        ordering = ('-id',)

    def __str__(self):
        return self.name

