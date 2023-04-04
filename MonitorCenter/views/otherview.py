from rest_framework.utils import json
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
# Create your views here.
from MonitorCenter import models
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from MonitorCenter.models import MonitorObject, Metrics, SysInfoManage, HostsInfo
from MonitorCenter.serializers import MonitorObjectSerializer, MetricsSerializer, SysInfoManageSerializer, \
    HostsInfoSerializer


@api_view(['POST'])
def login(request):
    # 先定义出返回数据的格式
    res = {"code": 20000, "data": None, 'data': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['GET'])
def info(request):
    # 先定义出返回数据的格式
    res = {"code": 20000, "data": {"roles": ["admin"], "introduction": "I am a super administrator",
                                   "avatar": "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
                                   "name": "Super Admin"}}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))
