# Generated by Django 4.1.7 on 2023-03-24 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SysInfoManage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Sys_name', models.CharField(max_length=64, verbose_name='系统全称')),
                ('Sys_abbreviation', models.CharField(max_length=64, verbose_name='系统简称')),
                ('Sys_level', models.CharField(choices=[('first_level_layer', '一级系统'), ('second_level_layer', '二级系统'), ('third_level_layer', '三级系统')], default='third_level_layer', max_length=64, verbose_name='系统等级')),
                ('Sys_dev_pricipal', models.CharField(max_length=32, verbose_name='系统开发负责人')),
                ('Sys_ops_pricipal', models.CharField(max_length=32, verbose_name='系统运维负责人')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '系统信息管理',
                'verbose_name_plural': '系统信息管理',
                'db_table': 'sysinfomanage',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='MonitorObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sysinfo_object_id', models.PositiveIntegerField()),
                ('object_type', models.CharField(choices=[('local_service', '本地服务'), ('container', '容器服务')], default='container', max_length=64, verbose_name='监控模块类型')),
                ('object_name', models.CharField(max_length=64, verbose_name='监控模块名称')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新日期')),
                ('sysinfo_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': '监控对象表',
                'verbose_name_plural': '监控对象表',
                'db_table': 'monitorobject',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='Metrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_ID', models.CharField(max_length=256, unique=True, verbose_name='监控指标ID')),
                ('metric_name', models.CharField(max_length=64, unique=True, verbose_name='指标名称')),
                ('metric_type', models.SmallIntegerField(choices=[(0, '系统层级'), (1, '自定义'), (2, '模块层级')], default=0, verbose_name='指标类型')),
                ('metric_desc', models.CharField(max_length=256, verbose_name='指标描述')),
                ('Threshold', models.IntegerField(default=0, verbose_name='阈值')),
                ('metric_unit', models.CharField(max_length=256, verbose_name='指标单位')),
                ('collect_type', models.SmallIntegerField(choices=[(0, 'Agent'), (1, '插件'), (2, '协议')], default=0, verbose_name='指标采集类型')),
                ('trigger_rule', models.CharField(choices=[('greater', '>'), ('less', '<'), ('equal', '='), ('unequal', '≠'), ('greater_equal', '≥'), ('less_equal', '≤')], default='less', max_length=256, verbose_name='触发规则')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新日期')),
                ('metrics_sys', models.ManyToManyField(related_name='metrics_sys', to='MonitorCenter.sysinfomanage')),
                ('monitor_object_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MonitorCenter.monitorobject')),
            ],
            options={
                'verbose_name': '监控指标表',
                'verbose_name_plural': '监控指标表',
                'db_table': 'metrics',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='HostsInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=64, verbose_name='IP地址')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('obj_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MonitorCenter.monitorobject', verbose_name='对象模块ID')),
                ('sys_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MonitorCenter.sysinfomanage', verbose_name='系统ID')),
            ],
            options={
                'verbose_name': '主机IP信息管理',
                'verbose_name_plural': '主机IP信息管理',
                'db_table': 'hostinfo',
                'ordering': ['-create_time'],
            },
        ),
    ]