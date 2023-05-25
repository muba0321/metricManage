from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from MonitorCenter.models.SysInfoManageModel import SysInfoManage


# Create your models here.

class MonitorObject(models.Model):
    """
        监控对象层级：
        """
    object_layer = (
        ('local_service', '本地服务'),
        ('container', '容器服务'),
    )
    # 监控模块类型
    object_type = models.CharField(choices=object_layer, max_length=64, default='container',
                                   verbose_name="监控模块类型")
    # 监控对象名称
    object_name = models.CharField(max_length=64, verbose_name='监控模块名称', null=True, blank=True)
    object_desc = models.CharField(max_length=64, verbose_name='监控对象描述', null=True, blank=True)
    thanos_id = models.IntegerField(verbose_name='thanos的id', null=True, blank=True)
    is_xc = models.CharField(max_length=64, verbose_name="是否是信创", null=True, blank=True)
    create_type = models.CharField(max_length=64, verbose_name="创建方式", null=True, blank=True, default='artificial')
    # 监控对象创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    sysinfo_object_id = models.ManyToManyField(SysInfoManage, through='MonitorObjectSystem',
                                               related_name='monitor_objects')
    # 监控对象更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新日期')
    # 逻辑删除字段
    is_deleted = models.BooleanField(default=False, verbose_name='已删除')

    def __str__(self):
        return '<%s>  %s' % (self.get_object_type_display(), self.object_name)

    class Meta:
        verbose_name = '监控对象表'
        verbose_name_plural = '监控对象表'
        ordering = ['-create_time']
        db_table = 'monitorobject'
        app_label = 'MonitorCenter'


class MonitorObjectSystem(models.Model):
    monitor_object = models.ForeignKey(MonitorObject, on_delete=models.CASCADE)
    sys_info_manage = models.ForeignKey(SysInfoManage, on_delete=models.CASCADE)

    class Meta:
        db_table = 'monitor_object_system'
