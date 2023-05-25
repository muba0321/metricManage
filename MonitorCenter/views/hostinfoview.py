from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from rest_framework.generics import get_object_or_404
from rest_framework.utils import json
from rest_framework.decorators import api_view

from MonitorCenter.models import MonitorObject, SysInfoManage, HostsInfo, HostSysMapping, HostObjMapping
from MonitorCenter.serializers import HostsInfoSerializer


def host_object_list(request):
    """
    主机信息：
    get请求返回主机IP信息
    post发送系统ID以及对象ID以及主机IP信息
    增加主机IP，关联系统和对象
    """
    if request.method == 'POST':
        # 创建主机记录
        serializer = HostsInfoSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"code": 0, 'status': 'success', 'host': serializer.data})
        else:
            return JsonResponse({'status': 'error', 'errors': serializer.errors})

    if request.method == 'GET':
        # 查询主机记录
        sysinfo = request.GET.get('sysinfo')
        obj_id = request.GET.get('obj_id')
        queryset = HostsInfo.objects.filter(is_deleted=False)
        if sysinfo:
            queryset = queryset.filter(systems=sysinfo)
        if obj_id:
            queryset = queryset.filter(objects=obj_id)
        serializer = HostsInfoSerializer(queryset, many=True)
        res = {"code": 0, "data": serializer.data, 'msg': "success"}
        # 添加返回的数据
        # 返回
        return HttpResponse(json.dumps(res))


@api_view(['GET', 'PATCH', 'DELETE'])
def host_object_detail(request, host_id):
    if request.method == 'GET':
        # 查询指定ID的主机记录
        try:
            host = HostsInfo.objects.get(id=host_id, is_deleted=False)
            serializer = HostsInfoSerializer(host)
            return JsonResponse({"code": 0, 'status': 'success', 'host': serializer.data})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Host not found'})

    elif request.method == 'PATCH':
        # 更新主机记录
        data = json.loads(request.body)
        try:
            host = HostsInfo.objects.get(id=host_id)
            serializer = HostsInfoSerializer(host, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return JsonResponse({"code": 0, 'status': 'success', 'host': serializer.data})
            else:
                return JsonResponse({'status': 'error', 'errors': serializer.errors})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Host not found'})

    elif request.method == 'DELETE':
        # 删除（逻辑删除）主机记录
        try:
            host = HostsInfo.objects.get(id=host_id)
            host.is_deleted = True
            host.save()
            serializer = HostsInfoSerializer(host)
            return JsonResponse({"code": 0, 'status': 'success', 'host': serializer.data})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Host not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def host_sys_list(request, sys_id):
    # ...
    queryset = HostsInfo.objects.filter(is_deleted=False, sysinfo_content_type__model='sysinfomanage',
                                        sysinfo_object_id=sys_id)
    serializer = HostsInfoSerializer(queryset, many=True)
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


def add_host_object_mapping(request):
    """
    添加主机与监控对象的映射关系
    """
    try:
        host_id = request.GET.get('host_id')
        obj_id = request.GET.get('object_id')
    except KeyError:
        return JsonResponse({'status': 'error', 'errors': 'host_id or obj_id not provided'})

    if not host_id or not obj_id:
        return JsonResponse({'status': 'error', 'errors': 'host_id or obj_id not provided'})

    try:
        host = HostsInfo.objects.get(pk=host_id)
        obj = MonitorObject.objects.get(pk=obj_id)
    except (HostsInfo.DoesNotExist, MonitorObject.DoesNotExist):
        return JsonResponse({'status': 'error', 'errors': 'HostsInfo or MonitorObject does not exist'})

    mapping, created = HostObjMapping.objects.get_or_create(host=host, object=obj)

    if created:
        return JsonResponse({"code": 0, 'status': 'success', 'msg': 'Mapping created'})
    else:
        return JsonResponse({'status': 'success', 'msg': 'Mapping already exists'})


@api_view(['DELETE'])
def remove_host_object_mapping(request):
    """
    移除主机与监控对象的映射关系
    """
    host_id = request.GET.get('host_id')
    obj_id = request.GET.get('object_id')

    if not host_id or not obj_id:
        return JsonResponse({'status': 'error', 'errors': 'host_id or obj_id not provided'})

    try:
        mapping = HostObjMapping.objects.get(host_id=host_id, object_id=obj_id)
    except HostObjMapping.DoesNotExist:
        return JsonResponse({'status': 'error', 'errors': 'Mapping does not exist'})

    mapping.delete()

    return JsonResponse({"code": 0, 'status': 'success', 'msg': 'Mapping removed'})


# 根据对象ID查询主机
def get_hosts_by_object_id(request, object_id):
    object = get_object_or_404(MonitorObject, id=object_id)
    host_mappings = HostObjMapping.objects.filter(object=object)
    hosts = [mapping.host for mapping in host_mappings]
    serializer = HostsInfoSerializer(hosts, many=True)
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    return HttpResponse(json.dumps(res))


# 主机和系统的增加关联
def add_host_sys_mapping(request):
    host_id = request.GET.get('host_id')
    sys_id = request.GET.get('sys_id')

    if not host_id or not sys_id:
        return JsonResponse({'status': 'error', 'errors': 'host_id or sys_id not provided'})

    host = get_object_or_404(HostsInfo, pk=host_id)
    sys = get_object_or_404(SysInfoManage, pk=sys_id)

    mapping, created = HostSysMapping.objects.get_or_create(host=host, sys_info=sys)

    if created:
        return JsonResponse({"code": 0, 'status': 'success', 'msg': 'Mapping created'})
    else:
        return JsonResponse({'status': 'success', 'msg': 'Mapping already exists'})


# 删除主机和系统关联
def remove_host_sys_mapping(request):
    host_id = request.GET.get('host_id')
    sys_id = request.GET.get('sys_id')

    if not host_id or not sys_id:
        return JsonResponse({'status': 'error', 'errors': 'host_id or sys_id not provided'})

    mapping = get_object_or_404(HostSysMapping, host_id=host_id, sys_info_id=sys_id)

    mapping.delete()

    return JsonResponse({"code": 0, 'status': 'success', 'msg': 'Mapping removed'})


# 查询根据系统ID返回主机信息
def get_hosts_by_sys_id(request, sys_id):
    sys = get_object_or_404(SysInfoManage, id=sys_id)
    host_mappings = HostSysMapping.objects.filter(sys_info=sys)
    hosts = [mapping.host for mapping in host_mappings if not mapping.host.is_deleted]
    serializer = HostsInfoSerializer(hosts, many=True)
    res = {"code": 0, "data": serializer.data, 'msg': "success"}
    return HttpResponse(json.dumps(res))


@api_view(['POST'])
def create_host_and_sys_mapping(request):
    """
    新建主机信息并在主机和系统的中间表里创建关联关系
    """
    sys_id = request.data.get('sys_id')
    ip_address = request.data.get('ip_address')
    mem_size = request.data.get('mem_size')
    disk_size = request.data.get('disk_size')
    cpu_hz = request.data.get('cpu_hz')
    host_name = request.data.get('host_name')
    os_disrtro = request.data.get('os_disrtro')


    if not sys_id or not ip_address:
        return JsonResponse({'status': 'error', 'errors': 'sys_id or ip_address not provided'})

    sys = get_object_or_404(SysInfoManage, pk=sys_id)

    # 创建 HostsInfo 实例
    host_data = {'ip_address': ip_address, 'mem_size': mem_size, 'disk_size': disk_size, 'cpu_hz': cpu_hz, 'host_name': host_name, 'os_disrtro': os_disrtro}
    host_serializer = HostsInfoSerializer(data=host_data)
    if host_serializer.is_valid():
        host = host_serializer.save()
    else:
        return JsonResponse({'status': 'error', 'errors': host_serializer.errors})

    # 创建 HostSysMapping 实例
    mapping, created = HostSysMapping.objects.get_or_create(host=host, sys_info=sys)

    if created:
        return JsonResponse({"code": 0, 'status': 'success', 'msg': 'Host created and mapping created'})
    else:
        return JsonResponse({'status': 'success', 'msg': 'Host created and mapping already exists'})
