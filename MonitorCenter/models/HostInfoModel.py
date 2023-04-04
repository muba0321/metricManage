from django.db import models
from django.contrib.auth.models import User
from .SysInfoManageModel import *
from .MonitorObjectModel import *


class HostsInfo(models.Model):
    ip_address = models.CharField(max_length=64, verbose_name='IP地址')
    objects = models.ManyToManyField(MonitorObject, through='HostObjMapping', related_name='hostinfo_objects')
    systems = models.ManyToManyField(SysInfoManage, through='HostSysMapping', related_name='hostinfo_systems')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_deleted = models.BooleanField(default=False, verbose_name='已删除')

    class Meta:
        verbose_name = '主机IP信息管理'
        verbose_name_plural = '主机IP信息管理'
        ordering = ['-create_time']
        db_table = 'hostinfo'
        app_label = 'MonitorCenter'


class HostSysMapping(models.Model):
    host = models.ForeignKey(HostsInfo, on_delete=models.CASCADE, verbose_name='主机ID')
    sys_info = models.ForeignKey(SysInfoManage, on_delete=models.CASCADE, verbose_name='系统ID')

    class Meta:
        db_table = 'hostsysmapping'
        verbose_name = '主机与系统关联'
        verbose_name_plural = '主机与系统关联'

    def __str__(self):
        return self.host.ip_address + '-' + self.sys_info.system_name


class HostObjMapping(models.Model):
    host = models.ForeignKey(HostsInfo, on_delete=models.CASCADE, verbose_name='主机ID')
    object = models.ForeignKey(MonitorObject, on_delete=models.CASCADE, verbose_name='对象ID')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'host_obj_mapping'
        app_label = 'MonitorCenter'
        verbose_name = '主机-对象映射关系'
        verbose_name_plural = '主机-对象映射关系'