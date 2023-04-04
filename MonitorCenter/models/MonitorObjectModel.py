from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


# Create your models here.

class MonitorObject(models.Model):
    """
        监控对象层级：
        """
    object_layer = (
        ('local_service', '本地服务'),
        ('container', '容器服务'),
    )
    sysinfo_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    sysinfo_object_id = models.PositiveIntegerField()
    sysinfo = GenericForeignKey('sysinfo_content_type', 'sysinfo_object_id')
    # 监控模块类型
    object_type = models.CharField(choices=object_layer, max_length=64, default='container',
                                   verbose_name="监控模块类型")
    # 监控对象名称
    object_name = models.CharField(max_length=64, verbose_name='监控模块名称')
    # 监控对象创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
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

