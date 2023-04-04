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
        res = {"code": 20000, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))

    elif request.method == 'POST':
        serializer = SysInfoManageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SysInfoManageSerializer(sysinfo_object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        sysinfo_object.delete()
        return Response(status=status.HTTP_200_OK)


def sysindex(request):
    """
    系统信息视图
    :param request:
    :return:
    """
    SysInfoManage = models.SysInfoManage.objects.all()
    return render(request, 'MonitorCenter/sysindex.html', locals())


# def import_excel(self, request):
#     """导入excel表数据"""
#     excel_file = request.FILES.get('excel_file', '')  # 获取前端上传的文件
#     file_type = excel_file.name.split('.')[1]  # 拿到文件后缀
#     if file_type in ['xlsx', 'xls']:  # 支持这两种文件格式
#         # 打开工作文件
#         data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
#         tables = data.sheets()  # 得到excel中数据表sheets1，sheets2...
#         # 循环获取每个数据表中的数据并写入数据库
#         for table in tables:
#             rows = table.nrows  # 总行数
#             try:
#                 # 控制数据库事务交易
#                 from django.db import transaction
#                 with transaction.atomic():
#                     # 获取数据表中的每一行数据写入设计好的数据库表
#                     for row in range(1, rows):  # 从1开始是为了去掉表头
#                         row_values = table.row_values(row)  # 每一行的数据
#                         SysInfoManage.objects.create(
#                             number=row_values[0],
#                             name=row_values[1],
#                             linkman=row_values[2],
#                             phone=row_values[3],
#                             hyperlink=row_values[4],
#                             remarks=row_values[5])
#             except:
#                 return restful.error(message='解析excel文件或者数据插入错误！')
#         return restful.success()
#     else:
#         return restful.error(message='上传文件类型错误！')
