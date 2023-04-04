from django.urls import path, re_path

from MonitorCenter import views

app_name = 'MonitorCenter'

urlpatterns = [
    path('user/login', views.otherview.login),
    path('user/info', views.otherview.info),
    # 对象接口路径
    # path('objects/', views.MonitorObjectview.index, name='index'),
    path('monitor_objects/system/<int:system_id>/', views.get_monitor_objects_by_system, name='get_monitor_objects_by_system'),
    path('monitor_objects/update/<int:monitor_object_id>/', views.update_monitor_object, name='update_monitor_object'),
    path('monitor_objects/delete/<int:monitor_object_id>/', views.delete_monitor_object, name='delete_monitor_object'),
    path('create_monitor_object/', views.create_monitor_object, name='create_monitor_object'),
    re_path(r'^objects/api/$', views.MonitorObjectview.monitor_object_list),
    path('objects/api/<int:id>/', views.get_monitor_object),
    # re_path(r'^objects/api/(?P<pk>[0-9]+)$', views.MonitorObjectview.monitor_object_detail),

    # 指标接口路径
    path('metrics/', views.MetricsListCreateView.as_view(), name='metrics-list-create'),
    path('metrics/<int:id>/', views.MetricsRetrieveUpdateDestroyView.as_view(), name='metrics-retrieve-update-destroy'),
    path('metrics/sysinfo/', views.create_metrics_with_sys_info, name='create_metrics_with_sys_info'),
    path('metrics/sysinfo/<int:sys_id>/', views.get_metrics_by_sys_id),
    path('metrics/create_with_hosts/', views.create_metrics_with_hosts),
    # 系统信息接口路径
    # re_path(r'^add_sysmetrics/api/$', views.metricsview.add_sys_metrics),
    path('sys/', views.sysinfoview.sysindex, name='sysindex'),
    re_path(r'^sysinfo/api/$', views.sysinfoview.sysinfo_object_list),
    re_path(r'^sysinfo/api/(?P<pk>[0-9]+)$', views.sysinfoview.sysinfo_object_detail),
    # 主机信息接口路径
    path('hostinfo/api/', views.host_object_list),
    path('hostinfo/api/sysinfo/<int:sys_id>/', views.host_sys_list),
    # re_path(r'^hostinfo/api/(?P<pk>[0-9]+)$', views.hostinfoview.hostinfo_detail),
    path('hostdetail/api/<int:host_id>/', views.host_object_detail),
    path('host_object_mapping/api/add/', views.add_host_object_mapping, name='add_host_object_mapping'),
    path('host_object_mapping/api/remove/', views.remove_host_object_mapping, name='remove_host_object_mapping'),
    path('host_object_mapping/api/get/<int:object_id>/', views.get_hosts_by_object_id, name='get_host_object_mapping'),
    path('add_host_sys_mapping/', views.add_host_sys_mapping),
    path('remove_host_sys_mapping/', views.remove_host_sys_mapping),
    path('hosts_by_sys_id/<int:sys_id>/', views.get_hosts_by_sys_id),
    path('create_host_and_sys_mapping/', views.create_host_and_sys_mapping, name='create_host_and_sys_mapping'),
 ]
