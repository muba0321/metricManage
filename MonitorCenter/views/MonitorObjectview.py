from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework.utils import json

# Create your views here.
from MonitorCenter import models
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from MonitorCenter.custom_db import get_third_party_data
from MonitorCenter.models import MonitorObject, Metrics, SysInfoManage, HostsInfo
from MonitorCenter.serializers import MonitorObjectSerializer, MetricsSerializer, SysInfoManageSerializer, \
    HostsInfoSerializer

@api_view(['POST'])
def create_monitor_object(request):
    serializer = MonitorObjectSerializer(data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data['object_name']
        sysinfo_table_name = 'sysinfomanage'
        sysinfo_object_id = serializer.validated_data['sysinfo_object_id']

        query = f"SELECT * FROM {sysinfo_table_name} WHERE id={sysinfo_object_id}"
        third_party_data = get_third_party_data(query)

        sysinfo_content_type = ContentType.objects.get_or_create(
            app_label='MonitorCenter',
            model=sysinfo_table_name
        )[0]

        my_model = MonitorObject(
            object_name=name,
            sysinfo_content_type=sysinfo_content_type,
            sysinfo_object_id=sysinfo_object_id,
        )
        my_model.save()
        return Response({"code": 20000, "status": "success", "message": "MonitorObject created and linked"},
                        status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_monitor_objects_by_system(request, system_id):
    # 获取与指定系统ID关联的所有监控对象，排除逻辑删除的记录
    monitor_objects = MonitorObject.objects.filter(sysinfo_object_id=system_id, is_deleted=False)

    # 序列化查询结果
    serializer = MonitorObjectSerializer(monitor_objects, many=True)

    # 以JSON格式返回结果
    res = {"code": 20000, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


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
        res = {"code": 20000, "data": serializer.data, 'msg': "success"}
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
    res = {"code": 20000, 'msg': "success"}
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
        res = {"code": 20000, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))

    elif request.method == 'POST':
        serializer = MonitorObjectSerializer(monitor_object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = {"code": 20000, "data": serializer.data, 'msg': "success"}
            # 添加返回的数据
            # 返回
            return HttpResponse(json.dumps(res))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        monitor_object.delete()
        res = {"code": 20000, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))


# def index(request):
#     """
#     监控对象视图.首页获取信息
#     :param request:
#     :return:
#     """
#     MonitorObject = models.MonitorObject.objects.all()
#     return render(request, 'MonitorCenter/index.html', locals())


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

        res = {"code": 20000, "data": serializer.data, 'msg': "success"}
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
    res = {"code": 20000, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))
