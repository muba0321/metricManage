from django.urls import path, re_path

from MonitorCenter import views

app_name = 'MonitorCenter'

urlpatterns = [
    path('user/login', views.otherview.login),
    path('user/info', views.otherview.info),
    path('sync/hosts/', views.sync_hosts),
    path('sync/objects/', views.sync_objects),
    path('sync/xcobjects/', views.sync_xcobjects),
    path('sync/system/', views.sync_system_info),
    path('test/', views.test),
    # 对象接口路径
    # path('objects/', views.MonitorObjectview.index, name='index'),
    path('monitor_objects/system/<int:system_id>/', views.get_monitor_objects_by_system, name='get_monitor_objects_by_system'),
    path('monitor_objects/update/<int:monitor_object_id>/', views.update_monitor_object, name='update_monitor_object'),
    path('monitor_objects/delete/<int:monitor_object_id>/', views.delete_monitor_object, name='delete_monitor_object'),
    path('create-object-link-system/', views.create_object_and_link_system, name='create_object_link_system'),
    re_path(r'^objects/api/$', views.monitor_object_list),
    path('objects/api/<int:id>/', views.get_monitor_object),
    path('object-system-relation/', views.create_object_system_relation, name='object_system_relation'),

    # 指标接口路径
    path('metrics/', views.MetricsListCreateView.as_view(), name='metrics-list-create'),
    path('metrics/<int:id>/', views.MetricsRetrieveUpdateDestroyView.as_view(), name='metrics-retrieve-update-destroy'),
    path('metrics/update/<int:sys_id>/<int:metric_id>/', views.update_metric_by_sys_metric_id),
    path('metrics/sysinfo/', views.create_metrics_with_sys_info, name='create_metrics_with_sys_info'),
    path('metrics/sysinfo/<int:sys_id>/<int:metric_type>/', views.get_metrics_by_sys_id),
    path('metrics/create_with_hosts/', views.create_metrics_with_hosts),
    path('metrics_object_relation/', views.create_metric_object_relation),
    path('metrics_system_relation/', views.associate_metric_and_system, name='associate_metric_and_system'),
    path('sys_metric_objects/<int:sys_id>/<int:id>/', views.get_objects_by_sys_and_metric, name='get_objects_by_sys_and_metric'),
    path('sys_metric_hosts/<int:sys_id>/<int:id>/', views.get_hosts_by_sys_and_metric, name='get_hosts_by_sys_and_metric'),
    path('remove_hostByMetric_Sys/<int:metric_id>/<int:sys_id>/', views.remove_hosts_from_metric_and_sys, name='remove_host_from_metric_and_sys'),
    path('remove_objectByMetric_Sys/<int:metric_id>/<int:sys_id>/', views.remove_objects_from_metric_and_sys, name='remove_object_from_metric_and_sys'),
    path('metrics/add_common_metric_to_all_sys/', views.add_metrics_to_all_sys),
    path('metrics_summary/<int:sys_id>/<int:metric_type>/', views.metrics_summary),
    # 系统信息接口路径
    re_path(r'^sysinfo/api/$', views.sysinfoview.sysinfo_object_list),
    re_path(r'^sysinfo/api/(?P<pk>[0-9]+)$', views.sysinfoview.sysinfo_object_detail),
    # 主机信息接口路径
    path('hostinfo/api/', views.host_object_list),
    path('hostinfo/api/sysinfo/<int:sys_id>/', views.host_sys_list),
    path('hostdetail/api/<int:host_id>/', views.host_object_detail),
    path('host_object_mapping/api/add/', views.add_host_object_mapping, name='add_host_object_mapping'),
    path('host_object_mapping/api/remove/', views.remove_host_object_mapping, name='remove_host_object_mapping'),
    path('host_object_mapping/api/get/<int:object_id>/', views.get_hosts_by_object_id, name='get_host_object_mapping'),
    path('add_host_sys_mapping/', views.add_host_sys_mapping),
    path('remove_host_sys_mapping/', views.remove_host_sys_mapping),
    path('hosts_by_sys_id/<int:sys_id>/', views.get_hosts_by_sys_id),
    path('create_host_and_sys_mapping/', views.create_host_and_sys_mapping, name='create_host_and_sys_mapping'),
 ]
