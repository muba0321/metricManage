from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import get_object_or_404
from rest_framework.utils import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from MonitorCenter.models import MonitorObject, SysInfoManage, MonitorObjectSystem, Metrics, MetricsHostsInfo, \
    MetricsMonitorObject, HostsInfo
from MonitorCenter.serializers import MonitorObjectSerializer

@api_view(['POST'])
def create_object_and_link_system(request):
    # 创建对象
    serializer = MonitorObjectSerializer(data=request.data)
    if serializer.is_valid():
        new_object = serializer.save()
        object_id = new_object.id
    else:
        return Response(serializer.errors, status=400)

    # 关联系统
    system_id = request.data.get('system_id')
    if system_id:
        try:
            system = SysInfoManage.objects.get(id=system_id)
        except SysInfoManage.DoesNotExist:
            return Response({"error": "System not found"}, status=404)

        object_system_relation = MonitorObjectSystem(monitor_object_id=object_id, sys_info_manage_id=system_id)
        object_system_relation.save()
        return Response({"code": 0, "message": "Object created and linked to system successfully"}, status=201)
    else:
        return Response({"error": "System ID is required"}, status=400)


@api_view(['GET'])
def get_monitor_objects_by_system(request, system_id):
    # 获取与指定系统ID关联的所有监控对象，排除逻辑删除的记录
    object_system_relations = MonitorObjectSystem.objects.filter(sys_info_manage_id=system_id)
    monitor_object_ids = [relation.monitor_object_id for relation in object_system_relations]
    monitor_objects = MonitorObject.objects.filter(id__in=monitor_object_ids, is_deleted=False)

    # 序列化查询结果
    serializer = MonitorObjectSerializer(monitor_objects, many=True)

    # 以JSON格式返回结果
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    return Response(res)


@api_view(['PATCH'])
def update_monitor_object(request, monitor_object_id):
    try:
        monitor_object = MonitorObject.objects.get(pk=monitor_object_id)
    except MonitorObject.DoesNotExist:
        return HttpResponse(status=404)

    data = request.data
    serializer = MonitorObjectSerializer(monitor_object, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        res = {"code": 0, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))
    else:
        return JsonResponse(serializer.errors, status=400)


@api_view(['DELETE'])
def delete_monitor_object(request, monitor_object_id):
    try:
        monitor_object = MonitorObject.objects.get(pk=monitor_object_id)
    except MonitorObject.DoesNotExist:
        return HttpResponse(status=404)

    monitor_object.is_deleted = True
    monitor_object.save()
    res = {"code": 0, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['GET', 'POST', 'DELETE'])
def monitor_object_detail(request, pk):
    """
        监控对象：
        判断是否存在返回404
        get请求返回监控对象信息
        post请求更新信息，失败返回400
        删除数据，返回204
    """
    try:
        monitor_object = MonitorObject.objects.get(pk=pk)
    except MonitorObject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MonitorObjectSerializer(monitor_object)
        res = {"code": 0, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))

    elif request.method == 'POST':
        serializer = MonitorObjectSerializer(monitor_object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = {"code": 0, "data": serializer.data, 'msg': "success"}
            # 添加返回的数据
            # 返回
            return HttpResponse(json.dumps(res))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        monitor_object.delete()
        res = {"code": 0, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))


@api_view(['GET'])
def monitor_object_list(request):
    """
        监控对象的接口
        第一个是get返回全部的监控对象信息
        第二个是post创建数据，如果能保存就返回201，否则返回400
    """
    if request.method == 'GET':
        monitor_objects = MonitorObject.objects.filter(is_deleted=False)
        serializer = MonitorObjectSerializer(monitor_objects, many=True)

        res = {"code": 0, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))


@api_view(['GET'])
def get_monitor_object(request, id):
    """
        获取指定ID的监控对象信息
    """
    try:
        monitor_object = MonitorObject.objects.get(pk=id, is_deleted=False)
    except MonitorObject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = MonitorObjectSerializer(monitor_object)
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['POST'])
def create_object_system_relation(request):
    object_id = request.data.get('object_id')
    system_ids = request.data.get('system_ids', [])

    monitor_object = get_object_or_404(MonitorObject, pk=object_id)
    for system_id in system_ids:
        sys_info_manage = get_object_or_404(SysInfoManage, pk=system_id)
        monitor_object_system = MonitorObjectSystem(monitor_object=monitor_object, sys_info_manage=sys_info_manage)
        monitor_object_system.save()

    serializer = MonitorObjectSerializer(monitor_object)
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))

