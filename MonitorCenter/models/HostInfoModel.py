from django.db import models
from django.contrib.auth.models import User
from .SysInfoManageModel import *
from .MonitorObjectModel import *
from .SysInfoManageModel import SysInfoManage


class HostsInfo(models.Model):
    # 主机IP
    ip_address = models.CharField(max_length=64, verbose_name='IP地址')
    # 内存大小
    mem_size = models.IntegerField(verbose_name="内存大小", null=True, blank=True)
    # 磁盘大小
    disk_size = models.IntegerField(verbose_name="磁盘大小", null=True, blank=True)
    # cpu的总hz
    cpu_hz = models.IntegerField(verbose_name="CPU大小", null=True, blank=True)
    # thanos系统内的id
    thanos_id = models.SmallIntegerField(verbose_name="thanos的服务器ID", null=True, blank=True)
    # thanos内的状态
    thanos_status = models.CharField(max_length=64, verbose_name="thanos上服务器状态", null=True, blank=True)
    # 主机名
    host_name = models.CharField(max_length=64, verbose_name="主机名", null=True, blank=True)
    # 操作系统
    os_disrtro = models.CharField(max_length=64, verbose_name="系统名", null=True, blank=True)
    # 数据创建方式
    create_type = models.CharField(max_length=64, verbose_name="创建方式", null=True, blank=True, default='artificial')
    # 多对多关联对象模块
    objects = models.ManyToManyField(MonitorObject, through='HostObjMapping', related_name='hostinfo_objects')
    # 多对多关联系统
    systems = models.ManyToManyField(SysInfoManage, through='HostSysMapping', related_name='hostinfo_systems')
    # 创建日期
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    # 更新日期
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # 逻辑删除
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