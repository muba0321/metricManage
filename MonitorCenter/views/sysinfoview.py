from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework.utils import json

# Create your views here.
from MonitorCenter import models
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from MonitorCenter.models import MonitorObject, Metrics, SysInfoManage, HostsInfo
from MonitorCenter.serializers import MonitorObjectSerializer, MetricsSerializer, SysInfoManageSerializer, \
    HostsInfoSerializer


@api_view(['GET', 'POST'])
def sysinfo_object_list(request):
    """
        监控对象的接口
        第一个是get返回全部的监控对象信息
        第二个是post创建数据，如果能保存就返回201，否则返回400
    """
    if request.method == 'GET':
        sysinfo_objects = SysInfoManage.objects.all()
        serializer = SysInfoManageSerializer(sysinfo_objects, many=True)
        res = {"code": 0, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))

    elif request.method == 'POST':
        serializer = SysInfoManageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = {"code": 0, "data": serializer.data, 'msg': "success"}
            # 添加返回的数据
            # 返回
            return HttpResponse(json.dumps(res))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
def sysinfo_object_detail(request, pk):
    """
        系统信息：
        判断是否存在返回404
        get请求返回监控对象信息
        post请求更新信息，失败返回400
        删除数据，返回204
    """
    try:
        sysinfo_object = SysInfoManage.objects.get(pk=pk)
    except SysInfoManage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SysInfoManageSerializer(sysinfo_object)
        res = {"code": 0, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))
    elif request.method == 'POST':
        serializer = SysInfoManageSerializer(sysinfo_object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = {"code": 0, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
            return HttpResponse(json.dumps(res))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        sysinfo_object.delete()
        res = {"code": 0, 'status': 'success', 'msg': 'removed'}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))
