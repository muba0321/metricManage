from rest_framework import serializers
from MonitorCenter.models import MonitorObject, Metrics, SysInfoManage, HostsInfo


class ChoiceField(serializers.Field):
    def __init__(self, model_field, **kwargs):
        self._choices = model_field.choices
        super(ChoiceField, self).__init__(**kwargs)

    def to_representation(self, value):
        return {
            'value': value,
            'display': self._get_display(value)
        }

    def _get_display(self, value):
        for choice in self._choices:
            if choice[0] == value:
                return choice[1]
        return None

    def to_internal_value(self, data):
        for choice in self._choices:
            if choice[0] == data:
                return data
        raise serializers.ValidationError(f"Invalid value for choice field: {data}")


class SysInfoManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysInfoManage
        fields = '__all__'
        read_only_fields = ('id', 'create_time')


class MonitorObjectSerializer(serializers.ModelSerializer):
    object_type = ChoiceField(MonitorObject._meta.get_field('object_type'))
    sysinfo_object_id = SysInfoManageSerializer(many=True, read_only=True)

    class Meta:
        model = MonitorObject
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'sysinfo_object_id')


class HostsInfoSerializer(serializers.ModelSerializer):
    object_name = serializers.ReadOnlyField(source='obj_id.object_name')

    class Meta:
        model = HostsInfo
        fields = ['id', 'ip_address', 'object_name', 'create_time', 'update_time', 'is_deleted']
        read_only_fields = ('id', 'create_time')


class MetricsSerializer(serializers.ModelSerializer):
    collect_type = ChoiceField(Metrics._meta.get_field('collect_type'))
    metric_type = ChoiceField(Metrics._meta.get_field('metric_type'))
    trigger_rule = ChoiceField(Metrics._meta.get_field('trigger_rule'))

    class Meta:
        model = Metrics
        fields = '__all__'
        read_only_fields = ('id', 'create_time')


class DetailedMetricSerializer(serializers.ModelSerializer):
    monitor_objects = MonitorObjectSerializer(many=True, read_only=True)
    hosts_info = HostsInfoSerializer(many=True, read_only=True)
    sys_info_manages = SysInfoManageSerializer(many=True, read_only=True)
    collect_type = ChoiceField(Metrics._meta.get_field('collect_type'))
    metric_type = ChoiceField(Metrics._meta.get_field('metric_type'))
    trigger_rule = ChoiceField(Metrics._meta.get_field('trigger_rule'))

    class Meta:
        model = Metrics
        fields = ['id', 'metric_ID', 'metric_name', 'metric_type', 'metric_desc', 'Threshold', 'Threshold', 'metric_unit', 'collect_type', 'trigger_rule', 'create_time', 'monitor_objects', 'hosts_info', 'sys_info_manages']
