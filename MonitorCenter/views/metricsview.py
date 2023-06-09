import json
from datetime import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny

# Create your views here.
from MonitorCenter import models
from rest_framework import status, generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from MonitorCenter.models import *
from MonitorCenter.models.MetricsModel import MetricsSysInfoManage, MetricsHostsInfo
from MonitorCenter.models.SysInfoManageModel import SysInfoManage
from MonitorCenter.serializers import MonitorObjectSerializer, MetricsSerializer, SysInfoManageSerializer, \
    HostsInfoSerializer, DetailedMetricSerializer
from MonitorCenter.views.otherview import check_access_key


class MetricsListCreateView(generics.ListCreateAPIView):
    queryset = Metrics.objects.filter(is_deleted=False)
    serializer_class = MetricsSerializer

    def list(self, request, *args, **kwargs):
        # 获取查询参数metric_type
        metric_type = request.GET.get('metric_type', None)

        queryset = self.filter_queryset(self.get_queryset())

        # 根据外部输入的变量返回指标类型为系统层级和自定义层级的指标
        if metric_type == "系统层级":
            queryset = queryset.filter(metric_type=0)  # 0 corresponds to 系统层级 in your choices
        elif metric_type == "自定义":
            queryset = queryset.filter(metric_type=1)  # 1 corresponds to 自定义 in your choices

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DetailedMetricSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DetailedMetricSerializer(queryset, many=True)
        res = {"code": 0, "data": serializer.data, 'msg': "success"}
        return JsonResponse(res)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)
    #     res = {"code": 20000, "data": serializer.data, 'msg': "success"}
    #     return JsonResponse(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            res = {"code": 0, "data": serializer.data, 'msg': "success"}
            return JsonResponse(res)
        return JsonResponse({"msg": "Failed to create", "errors": serializer.errors})


@csrf_exempt
@require_http_methods(["POST"])
def update_metric_by_sys_metric_id(request, sys_id, metric_id):
    try:
        # Load the JSON data from the request
        data = json.loads(request.body)

        # Get the Metric and MetricsSysInfoManage instances
        metric = get_object_or_404(Metrics, id=metric_id)
        metrics_sys_info_manage_instance = get_object_or_404(MetricsSysInfoManage, metric=metric, sys_info_id=sys_id)

        # Update fields in the Metrics model
        if 'metric_ID' in data:
            metric.metric_ID = data['metric_ID']
        if 'metric_name' in data:
            metric.metric_name = data['metric_name']
        if 'metric_type' in data:
            metric.metric_type = data['metric_type']
        if 'metric_desc' in data:
            metric.metric_desc = data['metric_desc']
        if 'metric_unit' in data:
            metric.metric_unit = data['metric_unit']
        if 'collect_type' in data:
            metric.collect_type = data['collect_type']

        # Save changes to the Metrics instance
        metric.save()

        # Update fields in the MetricsSysInfoManage model
        if 'Threshold' in data:
            metrics_sys_info_manage_instance.Threshold = data['Threshold']
        if 'trigger_rule' in data:
            metrics_sys_info_manage_instance.trigger_rule = data['trigger_rule']

        # Save changes to the MetricsSysInfoManage instance
        metrics_sys_info_manage_instance.save()

        return JsonResponse({'code': 0, "message": "Update successful."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


class MetricsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Metrics.objects.all()
    serializer_class = DetailedMetricSerializer
    lookup_field = 'id'
    # 添加这一行以允许 DELETE 方法
    http_method_names = ['get', 'put', 'patch', 'delete']

    # 重写 retrieve 方法
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {'code': 0, 'data': serializer.data}
        return Response(response_data)

    # 重写 update 方法
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            response_data = {'code': 0, 'data': serializer.data}
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 重写 partial_update 方法
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data = {'code': 0, 'data': serializer.data}
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        instance.is_deleted = True
        instance.save()
        response_data = {'code': 0, 'message': 'success'}
        return Response(response_data)


@api_view(['POST'])
def create_metrics_with_sys_info(request):
    data = request.data
    sys_id = data.get('sys_id')
    metric_data = {
        'metric_ID': data.get('metric_ID'),
        'metric_name': data.get('metric_name'),
        'metric_type': data.get('metric_type'),
        'metric_desc': data.get('metric_desc'),
        'Threshold': data.get('Threshold'),
        'metric_unit': data.get('metric_unit'),
        'collect_type': data.get('collect_type'),
        'trigger_rule': data.get('trigger_rule'),
    }
    metric_serializer = MetricsSerializer(data=metric_data)
    if metric_serializer.is_valid():
        metric_instance = metric_serializer.save()
        sys_instance = SysInfoManage.objects.get(pk=sys_id)
        MetricsSysInfoManage.objects.create(metric=metric_instance, sys_info=sys_instance)
        res = {"code": 0, "data": metric_serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))
    return JsonResponse(metric_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def get_metrics_by_sys_id(request, sys_id, metric_type):
#     try:
#         sys_info = SysInfoManage.objects.get(pk=sys_id)
#     except SysInfoManage.DoesNotExist:
#         return JsonResponse({'error': 'System does not exist.'}, status=status.HTTP_404_NOT_FOUND)
#
#     # convert the metric_type string to an integer
#     metric_type = int(metric_type)
#
#     if metric_type is not None:
#         if metric_type == 0:
#             metrics = sys_info.metrics_set.filter(Q(is_deleted=False) & Q(metric_type=0))
#         else:
#             metrics = sys_info.metrics_set.filter(Q(is_deleted=False) & ~Q(metric_type=0))
#     else:
#         metrics = sys_info.metrics_set.filter(is_deleted=False)
#
#     serializer = DetailedMetricSerializer(metrics, many=True)
#     res = {"code": 0, "data": serializer.data, 'msg': "success"}
#     return HttpResponse(json.dumps(res))
#
#
class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Metrics):
            return str(o)
        return super().default(o)


def get_metrics_by_sys_id(request, sys_id, metric_type):
    try:
        sys_info = SysInfoManage.objects.get(pk=sys_id)
    except SysInfoManage.DoesNotExist:
        return JsonResponse({'error': 'System does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    # convert the metric_type string to an integer
    metric_type = int(metric_type)

    if metric_type is not None:
        if metric_type == 0:
            metrics = sys_info.metrics_set.filter(Q(is_deleted=False) & Q(metric_type=0))
        else:
            metrics = sys_info.metrics_set.filter(Q(is_deleted=False) & ~Q(metric_type=0))
    else:
        metrics = sys_info.metrics_set.filter(is_deleted=False)

    # Modify here, change each metric to dictionary and modify the Threshold and trigger_rule field
    metrics_data = []
    for metric in metrics:
        metrics_sys_info_manage_instance = MetricsSysInfoManage.objects.get(metric=metric, sys_info=sys_info)
        # Specify the fields that you don't want to include in the dictionary
        metric_dict = model_to_dict(metric, exclude=['monitor_objects', 'hosts_info', 'sys_info_manages', 'metric_type',
                                                     'collect_type', 'trigger_rule'])

        # Check if threshold and trigger_rule are set in metrics_sys_info_manage_instance
        if metrics_sys_info_manage_instance and metrics_sys_info_manage_instance.Threshold is not None:
            metric_dict['Threshold'] = metrics_sys_info_manage_instance.Threshold
        else:
            metric_dict['Threshold'] = metric.Threshold

        if metrics_sys_info_manage_instance and metrics_sys_info_manage_instance.trigger_rule:
            metric_dict['trigger_rule'] = {'value': metrics_sys_info_manage_instance.trigger_rule,
                                           'display': metrics_sys_info_manage_instance.get_trigger_rule_display()}
        else:
            metric_dict['trigger_rule'] = metric.trigger_rule_display

        metric_dict['metric_type'] = metric.metric_type_display
        metric_dict['collect_type'] = metric.collect_type_display

        metrics_data.append(metric_dict)

    res = {"code": 0, "data": metrics_data, 'msg': "success"}
    return HttpResponse(json.dumps(res, cls=CustomJSONEncoder))


@api_view(['POST'])
def create_metrics_with_hosts(request):
    # 获取POST请求中的数据
    metrics_id = request.data.get('metrics_id')
    host_ips = request.data.get('host_ips')
    sys_id = request.data.get('sys_id')

    # 检查指标是否存在
    try:
        metrics = Metrics.objects.get(id=metrics_id)
    except Metrics.DoesNotExist:
        return Response({'error': 'metric not found'}, status=404)

    # 获取系统信息
    try:
        sys_info_manages = SysInfoManage.objects.get(id=sys_id)
    except SysInfoManage.DoesNotExist:
        return Response({'error': 'system not found'}, status=404)

    # 关联多个主机IP
    for ip in host_ips:
        hosts_info, created = HostsInfo.objects.get_or_create(id=ip)
        MetricsHostsInfo.objects.get_or_create(hosts_info=hosts_info, metric=metrics, sys_info_manages=sys_info_manages)

    return Response({'code': 0, 'success': 'metrics created with hosts'}, status=201)


@api_view(['POST'])
def create_metric_object_relation(request):
    metric_id = request.data.get('metric_id')
    object_ids = request.data.get('object_ids', [])
    sys_id = request.data.get('sys_id')

    metric = get_object_or_404(Metrics, pk=metric_id)

    # 获取系统信息
    try:
        sys_info_manages = SysInfoManage.objects.get(id=sys_id)
    except SysInfoManage.DoesNotExist:
        return Response({'error': 'system not found'}, status=404)

    for object_id in object_ids:
        monitor_object = get_object_or_404(MonitorObject, pk=object_id)
        MetricsMonitorObject.objects.get_or_create(metric=metric, monitor_object=monitor_object,
                                                   sys_info_manages=sys_info_manages)

    metric.save()
    serializer = MetricsSerializer(metric)
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['POST'])
def associate_metric_and_system(request):
    metric_ids = request.data.get('metric_ids', [])
    system_id = request.data.get('system_id', [])

    if not system_id:
        return Response({"code": 40000, "msg": "系统ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)

    system = SysInfoManage.objects.filter(id__in=system_id)
    metrics = Metrics.objects.filter(id__in=metric_ids)

    for system in system:
        for metric in metrics:
            system.metrics.add(metric)
    res = {"code": 0, 'msg': "Metrics associated with systems successfully."}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['GET'])
def get_objects_by_sys_and_metric(request, sys_id, id):
    sys_info = get_object_or_404(SysInfoManage, pk=sys_id)
    metric = get_object_or_404(Metrics, pk=id)

    metrics_monitor_objects = MetricsMonitorObject.objects.filter(sys_info_manages=sys_info, metric=metric)
    monitor_objects = [mmo.monitor_object for mmo in metrics_monitor_objects if not mmo.monitor_object.is_deleted]

    serializer = MonitorObjectSerializer(monitor_objects, many=True)
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['GET'])
def get_hosts_by_sys_and_metric(request, sys_id, id):
    sys_info = get_object_or_404(SysInfoManage, pk=sys_id)
    metric = get_object_or_404(Metrics, pk=id)

    metrics_hosts_infos = MetricsHostsInfo.objects.filter(sys_info_manages=sys_info, metric=metric)
    hosts = [mhi.hosts_info for mhi in metrics_hosts_infos if not mhi.hosts_info.is_deleted]

    serializer = HostsInfoSerializer(hosts, many=True)
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['DELETE'])
def remove_hosts_from_metric_and_sys(request, metric_id, sys_id):
    hosts_ids = request.data.get('host_ids', [])
    sys_info = get_object_or_404(SysInfoManage, pk=sys_id)
    metric = get_object_or_404(Metrics, pk=metric_id)

    for host_id in hosts_ids:
        host = get_object_or_404(HostsInfo, pk=host_id)
        metrics_host_infos = MetricsHostsInfo.objects.filter(sys_info_manages=sys_info, metric=metric, hosts_info=host)
        for metrics_host_info in metrics_host_infos:
            metrics_host_info.delete()
    res = {"code": 0, 'msg': "hosts removed from metric and sys"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['DELETE'])
def remove_objects_from_metric_and_sys(request, metric_id, sys_id):
    objects_ids = request.data.get('object_ids', [])
    sys_info = get_object_or_404(SysInfoManage, pk=sys_id)
    metric = get_object_or_404(Metrics, pk=metric_id)

    for object_id in objects_ids:
        monitor_object = get_object_or_404(MonitorObject, pk=object_id)
        try:
            metrics_monitor_object = MetricsMonitorObject.objects.filter(sys_info_manages=sys_info, metric=metric,
                                                                         monitor_object=monitor_object)
            metrics_monitor_object.delete()
        except MetricsMonitorObject.DoesNotExist:
            pass
    res = {"code": 0, 'msg': "objects removed from metric and sys"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@csrf_exempt
def add_metrics_to_all_sys(request):
    # 获取所有 metric_type 为0的指标
    metrics = Metrics.objects.filter(metric_type=0)

    # 获取所有的系统
    systems = SysInfoManage.objects.all()

    # 遍历每一个系统
    for sys_info in systems:
        # 遍历每一个指标
        for metric in metrics:
            # 检查该指标是否已经与该系统关联
            if not metric.sys_info_manages.filter(id=sys_info.id).exists():
                # 如果未关联，则创建新的关联
                metric.sys_info_manages.add(sys_info)

    # 构造返回结果
    res = {"code": 0, 'msg': "common metrics added to all systems"}
    return HttpResponse(json.dumps(res))
