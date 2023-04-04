from rest_framework import serializers
from MonitorCenter.models import MonitorObject, Metrics, SysInfoManage, HostsInfo


class MonitorObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitorObject
        fields = '__all__'
        read_only_fields = ('id', 'create_time')


class SysInfoManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysInfoManage
        fields = '__all__'
        read_only_fields = ('id', 'create_time')


class HostsInfoSerializer(serializers.ModelSerializer):
    object_name = serializers.ReadOnlyField(source='obj_id.object_name')

    class Meta:
        model = HostsInfo
        fields = ['id', 'ip_address', 'object_name', 'create_time', 'update_time', 'is_deleted']
        read_only_fields = ('id', 'create_time')


class MetricsSerializer(serializers.ModelSerializer):
    hosts_info = HostsInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Metrics
        fields = '__all__'
        read_only_fields = ('id', 'create_time')
