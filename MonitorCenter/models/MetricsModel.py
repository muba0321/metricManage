from django.db import models
from django.contrib.auth.models import User
from MonitorCenter.models import *


class Metrics(models.Model):
    collect_type = (
        (0, 'Agent'),
        (1, '插件'),
        (2, '脚本')
    )
    metrics_type = (
        (0, '公共指标'),
        (1, '自定义'),
        (2, '模块层级')
    )
    trigger_rule_type = (
        ('greater', '>'),
        ('less', '<'),
        ('equal', '='),
        ('unequal', '≠'),
        ('greater_equal', '≥'),
        ('less_equal', '≤')
    )
    # 指标ID，例如：BCLinux-001
    metric_ID = models.CharField(max_length=256, unique=True, verbose_name="监控指标ID")
    # 监控指标名称
    metric_name = models.CharField(max_length=64, unique=True, verbose_name='指标名称')
    # 监控指标类型
    metric_type = models.SmallIntegerField(choices=metrics_type, default=0, verbose_name='指标类型')
    # 监控指标描述
    metric_desc = models.CharField(max_length=256, verbose_name='指标描述', null=True, blank=True)
    # 阈值
    Threshold = models.CharField(max_length=256, verbose_name='阈值', null=True, blank=True)
    # 监控指标单位
    metric_unit = models.CharField(max_length=256, null=True, blank=True, verbose_name='指标单位')
    # 监控指标采集类型
    collect_type = models.SmallIntegerField(choices=collect_type, default=0, verbose_name='指标采集类型')
    # 触发规则
    trigger_rule = models.CharField(max_length=256, choices=trigger_rule_type, verbose_name='触发规则', null=True, blank=True)
    # 指标创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    # 指标更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新日期')
    # 逻辑删除
    is_deleted = models.BooleanField(default=False, verbose_name='已删除')
    # 通过中间表关联对象模块
    monitor_objects = models.ManyToManyField('MonitorObject', through='MetricsMonitorObject')
    # 通过中间表关联主机信息
    hosts_info = models.ManyToManyField('HostsInfo', through='MetricsHostsInfo')
    # 通过中间表关联系统信息
    sys_info_manages = models.ManyToManyField('SysInfoManage', through='MetricsSysInfoManage')

    def __str__(self):
        return '<%s>  %s' % (self.get_collect_type_display(), self.collect_type)

    def __str__(self):
        return '<%s>  %s' % (self.get_trigger_rule_display(), self.collect_type)

    @property
    def metric_type_display(self):
        return {'value': self.metric_type, 'display': self.get_metric_type_display()}

    @property
    def collect_type_display(self):
        return {'value': self.collect_type, 'display': self.get_collect_type_display()}

    @property
    def trigger_rule_display(self):
        return {'value': self.trigger_rule, 'display': self.get_trigger_rule_display()}

    class Meta:
        verbose_name = '监控指标表'
        verbose_name_plural = '监控指标表'
        ordering = ['-create_time']
        db_table = 'metrics'
        app_label = 'MonitorCenter'


class MetricsMonitorObject(models.Model):
    metric = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    monitor_object = models.ForeignKey('MonitorObject', on_delete=models.CASCADE)
    sys_info_manages = models.ForeignKey('SysInfoManage', on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ('metric', 'monitor_object', 'sys_info_manages')


class MetricsHostsInfo(models.Model):
    metric = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    hosts_info = models.ForeignKey('HostsInfo', on_delete=models.CASCADE)
    sys_info_manages = models.ForeignKey('SysInfoManage', on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ('metric', 'hosts_info', 'sys_info_manages')


class MetricsSysInfoManage(models.Model):
    trigger_rule_type = (
        ('greater', '>'),
        ('less', '<'),
        ('equal', '='),
        ('unequal', '≠'),
        ('greater_equal', '≥'),
        ('less_equal', '≤')
    )
    metric = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    sys_info = models.ForeignKey('SysInfoManage', on_delete=models.CASCADE)
    trigger_rule = models.CharField(max_length=256, choices=trigger_rule_type, verbose_name='触发规则', null=True, blank=True)
    Threshold = models.CharField(max_length=256, verbose_name='阈值', null=True, blank=True)
