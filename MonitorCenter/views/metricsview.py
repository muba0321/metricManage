import json
from datetime import datetime

from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render
# Create your views here.
from MonitorCenter import models
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from MonitorCenter.models import *
from MonitorCenter.models.MetricsModel import MetricsSysInfoManage
from MonitorCenter.serializers import MonitorObjectSerializer, MetricsSerializer, SysInfoManageSerializer, \
    HostsInfoSerializer


class MetricsListCreateView(generics.ListCreateAPIView):
    queryset = Metrics.objects.filter(is_deleted=False)
    serializer_class = MetricsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        res = {"code": 20000, "data": serializer.data, 'msg': "success"}
        return JsonResponse(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            res = {"code": 20000, "data": serializer.data, 'msg': "success"}
            return JsonResponse(res)
        return JsonResponse({"code": 20000, "msg": "Failed to create", "errors": serializer.errors})


class MetricsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Metrics.objects.all()
    serializer_class = MetricsSerializer
    lookup_field = 'id'
    # 添加这一行以允许 DELETE 方法
    http_method_names = ['get', 'put', 'patch', 'delete']

    # 重写 retrieve 方法
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {'code': 20000, 'data': serializer.data}
        return Response(response_data)

    # 重写 update 方法
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            response_data = {'code': 20000, 'data': serializer.data}
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 重写 partial_update 方法
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data = {'code': 20000, 'data': serializer.data}
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        instance.is_deleted = True
        instance.save()
        response_data = {'code': 20000, 'message': 'success'}
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


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
        res = {"code": 20000, "data": metric_serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))
    return JsonResponse(metric_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_metrics_by_sys_id(request, sys_id):
    try:
        sys_info = SysInfoManage.objects.get(pk=sys_id)
    except SysInfoManage.DoesNotExist:
        return JsonResponse({'error': 'System does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    metrics = sys_info.metrics_set.all()
    serializer = MetricsSerializer(metrics, many=True)
    res = {"code": 20000, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['POST'])
def create_metrics_with_hosts(request):
    # 获取POST请求中的数据
    metrics_id = request.data.get('metrics_id')
    host_ips = request.data.get('host_ips')

    # 检查指标是否存在
    try:
        metrics = Metrics.objects.get(id=metrics_id)
    except Metrics.DoesNotExist:
        return Response({'error': 'metric not found'}, status=404)

    # 关联多个主机IP
    for ip in host_ips:
        hosts_info, created = HostsInfo.objects.get_or_create(ip_address=ip)
        MetricsHostsInfo.objects.create(hosts_info=hosts_info, metric=metrics)

    return Response({'code': 20000, 'success': 'metrics created with hosts'}, status=201)


def metric(request):
    """
    监控指标视图
    :param request:
    :return:
    """
    # Metrics = models.Metrics.objects.all()
    sysabb = request.GET.get("sys_abb", "value")
    # 临时加上一个临时值，等后面前端对上了再注释下面临时赋值
    sysabb = "pipeline"
    sysinfo_obj = SysInfoManage.objects.get(Sys_abbreviation=sysabb)
    Metrics = sysinfo_obj.metrics_sys.all()
    return render(request, 'MonitorCenter/metric.html', locals())
