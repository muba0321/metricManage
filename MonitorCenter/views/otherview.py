from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from rest_framework.utils import json
import requests
from django.http import HttpResponse, JsonResponse
from rest_framework import exceptions
from rest_framework.decorators import api_view
import logging
from MonitorCenter.models import MonitorObject, HostsInfo, SysInfoManage, MetricsHostsInfo, MetricsMonitorObject, \
    Metrics, MonitorObjectSystem, HostSysMapping


def check_access_key(request):
    access_key = request.META.get('HTTP_ACCESS_KEY')
    if not access_key:
        raise exceptions.AuthenticationFailed('No access key provided')

    # Replace 'your_valid_key' with your actual valid access key
    if access_key != 'hduiwheidwoehoehwfhlkrhfhsjhfishfiu':
        raise exceptions.AuthenticationFailed('Invalid access key')


@api_view(['POST'])
def login(request):
    # 先定义出返回数据的格式
    res = {"code": 0, "data": None, 'message': "success"}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


@api_view(['GET'])
def info(request):
    # 先定义出返回数据的格式
    res = {"code": 0, "data": {"roles": ["admin"], "introduction": "I am a super administrator",
                               "avatar": "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
                               "name": "Super Admin"}}
    # 添加返回的数据
    # 返回
    return HttpResponse(json.dumps(res))


# 同步服务器信息
@csrf_exempt
def sync_hosts(request):
    hosturl = "http://192.168.50.3:5000/thanos-cmdb/v1/systemRelation/relate/system/host/"

    all_thanos_ids = list(filter(None, SysInfoManage.get_all_system_ids()))
    for thanos_id in all_thanos_ids:
        params = {
            "systemId": thanos_id,
        }
        response = requests.get(hosturl, params=params)
        data = response.json()
        hosts = data.get('data', [])
        # hosts = [value for key, value in hosts_dict.items() if key.isdigit()]

        ip_addresses_from_api = set(host['ip'] for host in hosts if 'ip' in host)

        # 获取所有标记为 'auto' 的本地主机,加个系统的逻辑回头

        local_hosts = HostsInfo.objects.filter(create_type='auto', thanos_id=thanos_id)

        # 然后，使用这些id获取主机

        sys_info_manage = SysInfoManage.objects.filter(thanos_id=thanos_id).first()
        # 检查每一个本地主机
        for local_host in local_hosts:
            # 如果本地主机的IP不在接口返回的IP集合中，将其标记为逻辑删除
            if local_host.ip_address not in ip_addresses_from_api:
                local_host.is_deleted = True
                local_host.save()

        for host_data in hosts:
            ip_address = host_data['ip']
            host, created = HostsInfo.objects.get_or_create(ip_address=ip_address, thanos_id=thanos_id)
            # 更新其它属性
            # 你可以在这里添加需要更新的属性，例如：
            host.mem_size = host_data['memSize']
            host.disk_size = host_data['diskSize']
            host.cpu_hz = host_data['cpuHz']
            host.thanos_id = host_data['id']
            host.thanos_status = host_data['status']
            host.host_name = host_data['hostName']
            host.os_disrtro = host_data['osDistro']
            host.create_type = 'auto'
            host.is_deleted = False  # 重置删除标志，因为这个主机现在在接口返回的数据中
            host.save()

            HostSysMapping.objects.get_or_create(host=host, sys_info=sys_info_manage)
    res = {"code": 0, "msg": "success"}
    # 返回
    return HttpResponse(json.dumps(res))


# 同步服务信息
@csrf_exempt
def sync_objects(request):
    serviceurl = "http://192.168.50.3:5001/thanos-cmdb/v1/serviceinfo/page"

    all_thanos_ids = list(filter(None, SysInfoManage.get_all_system_ids()))
    for thanos_id in all_thanos_ids:
        #body = {
        #    "systemId": thanos_id,
        #}
        response = requests.get(serviceurl)
        data = response.json()
        services = data.get('data', {}).get('result', [])
        if not services:
            continue
        # 从 "result" 键对应的列表中获取服务信息

        object_name_from_api = set(service['name'] for service in services)

        # 获取所有标记为 'auto' 的本地主机
        local_objects = MonitorObject.objects.filter(create_type='auto', is_xc='False', thanos_id=thanos_id)

        # 检查每一个本地主机
        for local_object in local_objects:
            # 如果本地主机的IP不在接口返回的IP集合中，将其标记为逻辑删除
            if local_object.object_name not in object_name_from_api:
                local_object.is_deleted = True
                local_object.save()
        sys_info_manage = SysInfoManage.objects.get(thanos_id=thanos_id)
        for service_data in services:
            object_name = service_data['name']
            if service_data['isContainerApp'] == "Y":
                object_type = 'container'
            else:
                object_type = 'local_service'

            objects = MonitorObject.objects.exclude(is_xc='True').filter(object_name=object_name, thanos_id=thanos_id)

            if not objects.exists():
                objects = [MonitorObject.objects.create(object_name=object_name, object_type=object_type)]

            for object in objects:
                # 更新对象的属性
                object.object_desc = service_data['fullName']
                object.is_xc = service_data['new']
                object.thanos_id = service_data['id']
                object.object_type = object_type
                object.create_type = 'auto'
                object.is_deleted = False  # 重置删除标志，因为这个主机现在在接口返回的数据中
                object.save()

                MonitorObjectSystem.objects.create(monitor_object=object, sys_info_manage=sys_info_manage)
    res = {"code": 0, "msg": "success"}
    # 返回
    return HttpResponse(json.dumps(res))


# 同步信创服务信息
@csrf_exempt
def sync_xcobjects(request):

    xcserviceurl = "http://192.168.50.3:5002/thanos-cmdb/v1/cceAppinfo/"

    all_thanos_ids = list(filter(None, SysInfoManage.get_all_system_ids()))
    for thanos_id in all_thanos_ids:
        params = {
            "systemId": thanos_id,
        }
    # params = {
    #     "systemId": "2",
    # }
        response = requests.get(xcserviceurl, params=params)
        data = response.json()
        #xcservices = data['data']  # 直接访问 "data" 键对应的字典
        xcservices = data['data']  # 从 "result" 键对应的列表中获取服务信息
        if not xcservices:
            continue

        xcobject_name_from_api = set(xcservice['name'] for xcservice in xcservices)
        # xcobject_name_from_api = set(xcservices[key]['name'] for key in xcservices if isinstance(xcservices[key], dict))

        # 获取所有标记为 'auto' 的本地主机
        local_objects = MonitorObject.objects.filter(create_type='auto', is_xc='True', thanos_id=thanos_id)

        # 检查每一个本地主机
        for local_object in local_objects:
            # 如果本地主机的IP不在接口返回的IP集合中，将其标记为逻辑删除
            if local_object.object_name not in xcobject_name_from_api:
                local_object.is_deleted = True
                local_object.save()

        sys_info_manage = SysInfoManage.objects.get(thanos_id=thanos_id)

        for xcservice_data in xcservices:  # 使用 items() 方法遍历字典
            if isinstance(xcservice_data, dict):  # 如果服务数据是字典，才进行处理
                object_name = xcservice_data['name']
                object_type = 'container'

                # 使用 get 方法找到相应的对象，如果找不到就创建
                try:
                    objects = MonitorObject.objects.exclude(is_xc='False').get(object_name=object_name,  thanos_id=thanos_id)
                except MonitorObject.DoesNotExist:
                    objects = MonitorObject.objects.create(object_name=object_name, object_type=object_type)

                # 更新对象的属性
                objects.object_desc = xcservice_data['namespace']
                objects.is_xc = xcservice_data['new']
                objects.thanos_id = xcservice_data['id']
                objects.object_type = object_type
                objects.create_type = 'auto'
                objects.is_deleted = False  # 重置删除标志，因为这个主机现在在接口返回的数据中
                objects.save()
    res = {"code": 0, "msg": "success"}
    # 返回
    return HttpResponse(json.dumps(res))


# 同步系统信息方法
@csrf_exempt
def sync_system_info(request):
    import requests
    response = requests.get('http://192.168.50.3:5003/thanos-cmdb/v1/system/list')
    data = response.json()

    if data["code"] == 0 and data["succeed"] is True:
        for remote_system in data["data"]["result"]:
            try:
                # 按照 thanos_id 查询对象
                system = SysInfoManage.objects.get(Sys_abbreviation=remote_system["name"])
                # 更新系统的其他信息
                system.Sys_name = remote_system["fullName"]
                system.Sys_abbreviation = remote_system["name"]
                system.Sys_dev_pricipal = remote_system["contantName"]
                system.Sys_ops_pricipal = remote_system["bizContantName"]
                system.Sys_bussi_pricipal = remote_system["businessContactName"]
                system.save()
            except SysInfoManage.DoesNotExist:
                # 如果没有找到对应的 thanos_id，那么创建新的对象
                new_system = SysInfoManage(
                    Sys_name=remote_system["fullName"],
                    Sys_abbreviation=remote_system["name"],
                    Sys_dev_pricipal=remote_system["contantName"],
                    Sys_ops_pricipal=remote_system["bizContantName"],
                    Sys_bussi_pricipal=remote_system["businessContactName"],
                    thanos_id=remote_system["id"]
                )
                new_system.save()
    res = {"code": 0, "msg": "success"}
    # 返回
    return HttpResponse(json.dumps(res))


# headers = {
#     "Authorization": "ddhiuewkhdwjhedwjedhkwjhdkdheakdjknaedebadlhl",
#     # 添加更多头部信息
# }

# headers = {
#     "Content-Type": "application/json",
#     "Authorization": "Your Token"
# }
# # 定义 body
# body = {
#     "key1": "value1",
#     "key2": "value2"
# }
# params = {
#     "key1": "value1",
#     "key2": "value2"
# }
# response = requests.post('http://thanos_api/get_all_systems', headers=headers, json=body)
# response = requests.get(serviceurl, headers=headers, params=params)


@csrf_exempt
def metrics_summary(request, sys_id, metric_type):
    # 获取指定的系统
    sys_info = SysInfoManage.objects.get(id=sys_id)

    # 获取满足条件的所有指标
    if metric_type == 0:
        metrics = Metrics.objects.filter(metric_type=0)
    elif metric_type != 0:
        metrics = Metrics.objects.exclude(metric_type=0)

    # 创建一个字典来存储每个指标的统计信息
    metrics_data = []

    # 计算系统总主机数和总对象模块数
    total_hosts_count = MetricsHostsInfo.objects.filter(sys_info_manages=sys_info).count()
    total_objects_count = MetricsMonitorObject.objects.filter(sys_info_manages=sys_info).count()

    for metric in metrics:
        # 计算关联主机数和关联对象数
        related_hosts_count = MetricsHostsInfo.objects.filter(metric=metric, sys_info_manages=sys_info).count()
        related_objects_count = MetricsMonitorObject.objects.filter(metric=metric, sys_info_manages=sys_info).count()

        # 计算主机和对象的覆盖率
        host_coverage = related_hosts_count / total_hosts_count if total_hosts_count > 0 else 0
        object_coverage = related_objects_count / total_objects_count if total_objects_count > 0 else 0

        # 添加指标的统计信息到列表
        metrics_data.append({
            "id": metric.id,
            "metric_name": metric.metric_name,
            "metric_ID": metric.metric_ID,
            "related_hosts_count": related_hosts_count,
            "related_objects_count": related_objects_count,
            "host_coverage": host_coverage,
            "object_coverage": object_coverage,
        })

    # 创建返回的结果
    res = {
        "code": 0,
        "data": metrics_data,
        "msg": "success",
    }

    # 返回结果
    return JsonResponse(res)


# 同步服务信息
@csrf_exempt
def test(request):
    all_thanos_ids = list(filter(None, SysInfoManage.get_all_system_ids()))
    for thanos_id in all_thanos_ids:
        print(thanos_id)
    return HttpResponse()  # 返回一个空的 HttpResponse