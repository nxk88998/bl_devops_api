# coding=utf-8
from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.

class Gitlab_Webhook(models.Model):
    ''' Model for webhook of gitlab

    '''
    repo_name = models.CharField(
        verbose_name = _(u'repository name'),
        help_text = _(u' '),
        max_length = 255
    )
    repo_url = models.CharField(
        verbose_name = _(u'repository url'),
        help_text = _(u' '),
        max_length = 255
    )
    object_kind = models.CharField(
        verbose_name = _(u'object_kind value'),
        help_text = _(u'push, tag_push, issue, note'),
        max_length = 255
    )
    project_id = models.IntegerField(
        verbose_name = _(u'project_id value'),
        help_text = _(u'Your project id in gitlab'),
        default = 0
    )
    http_x_gitlab_event = models.CharField(
        verbose_name = _(u'X-Gitlab-Event in request header'),
        help_text = _(u'Push Hook, Tag Push Hook, Issue Hook, Note Hook'),
        max_length = 255
    )

    def __unicode__(self):
        return u'%s %s' % (self.repo_name, self.object_kind)