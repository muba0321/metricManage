from django.db import models
from django.contrib.auth.models import User
from .MetricsModel import *


class SysInfoManage(models.Model):
    sys_level_layer = (
        ('first_level_layer', '一级系统'),
        ('second_level_layer', '二级系统'),
        ('third_level_layer', '三级系统'),
    )
    Sys_name = models.CharField(max_length=64, verbose_name='系统全称')
    Sys_abbreviation = models.CharField(max_length=64,  unique=True, verbose_name='系统简称')
    Sys_level = models.CharField(choices=sys_level_layer, max_length=64, default='third_level_layer',
                                 verbose_name='系统等级')
    thanos_id = models.IntegerField(verbose_name='thanos上对应的系统ID', null=True, blank=True)
    Sys_dev_pricipal = models.CharField(max_length=32, verbose_name='系统开发负责人', null=True, blank=True)
    Sys_ops_pricipal = models.CharField(max_length=32, verbose_name='系统运维负责人', null=True, blank=True)
    Sys_bussi_pricipal = models.CharField(max_length=32, verbose_name='系统总负责人', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '<%s>  %s' % (self.get_Sys_level_display(), self.Sys_level)

    @staticmethod
    def get_all_system_ids():
        return list(SysInfoManage.objects.values_list('thanos_id', flat=True))

    class Meta:
        verbose_name = '系统信息管理'
        verbose_name_plural = '系统信息管理'
        ordering = ['-create_time']
        db_table = 'sysinfomanage'
        app_label = 'MonitorCenter'
