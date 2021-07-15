from rest_framework import serializers
from hyperconverged.models import Part,Node
from rest_framework.validators import UniqueValidator
from hyperconverged.serializer.WorkloadSerializer import JSONSerializerField

node_types = ['configurable', 'fixed']


class ConfNodeSerializer(serializers.Serializer):

    id = serializers.CharField(required=False)
    vendor = serializers.CharField(required=True)
    name = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Node.objects.filter(status=True))])
    type = serializers.ChoiceField(node_types)

    cpu_socket_count = serializers.ListField(required=True,
                                             child=serializers.IntegerField(required=True,
                                                                            min_value=1,
                                                                            max_value=4))
    cpu_options = serializers.ListField(required=True,
                                        child=serializers.CharField(required=True))

    ram_slots = serializers.ListField(required=False,
                                      child=serializers.IntegerField(required=True,
                                                                     min_value=1,
                                                                     max_value=32))
    ram_options = serializers.ListField(required=True,
                                        child=serializers.CharField(required=True))

    generic_rules = serializers.ListField(required=False,
                                          child=serializers.IntegerField(required=False,
                                                                         min_value=1,
                                                                         max_value=2))

    specific_rules = serializers.ListField(required=False,
                                          child=serializers.IntegerField(required=False,
                                                                         min_value=3,
                                                                         max_value=14))

    hdd_slots = serializers.ListField(required=True,
                                      child=serializers.IntegerField(required=True,
                                                                     min_value=1,
                                                                     max_value=100))

    hdd_options = serializers.ListField(required=True,
                                        child=serializers.CharField(required=True))

    ssd_slots = serializers.ListField(required=True,
                                      child=serializers.IntegerField(required=True,
                                                                     min_value=1,
                                                                     max_value=100))

    ssd_options = serializers.ListField(required=True,
                                        child=serializers.CharField(required=True))

    iops = serializers.IntegerField(required=True)
    base_price = serializers.IntegerField(required=True)
    rack_space = serializers.IntegerField(required=True)
    power = serializers.IntegerField(required=True)
    btu = serializers.IntegerField(required=True)
    status = serializers.BooleanField(default=True)
    iops_conversion_factor = JSONSerializerField(required=True)
    static_overhead = JSONSerializerField(required=True)
    
    pcie_slots = serializers.ListField(required=True, child=serializers.IntegerField(required=True))
    gpu_options = serializers.ListField(required=True, child=serializers.CharField(required=True))


class ConfPutNodeSerializer(serializers.Serializer):

    id = serializers.CharField(required=False)
    vendor = serializers.CharField(required=True)

    type = serializers.ChoiceField(node_types)
    cpu_socket_count = serializers.ListField(required=True,
                                             child=serializers.IntegerField(required=True,
                                                                            min_value=1,
                                                                            max_value=4))
    cpu_options = serializers.ListField(required=True,
                                        child=serializers.CharField(required=True))
    ram_slots = serializers.ListField(required=False,
                                      child=serializers.IntegerField(required=True,
                                                                     min_value=1,
                                                                     max_value=32))
    ram_options = serializers.ListField(required=True,
                                        child=serializers.CharField(required=True))

    generic_rules = serializers.ListField(required=False,
                                          child=serializers.IntegerField(required=False,
                                                                         min_value=1,
                                                                         max_value=2))

    specific_rules = serializers.ListField(required=False,
                                           child=serializers.IntegerField(required=False,
                                                                          min_value=3,
                                                                          max_value=14))

    hdd_slots = serializers.ListField(required=True,
                                      child=serializers.IntegerField(required=True,
                                                                     min_value=1,
                                                                     max_value=100))
    hdd_options = serializers.ListField(required=True,
                                        child=serializers.CharField(required=True))
    ssd_slots = serializers.ListField(required=True,
                                      child=serializers.IntegerField(required=True,
                                                                     min_value=1,
                                                                     max_value=100))
    ssd_options = serializers.ListField(required=True,
                                        child=serializers.CharField(required=True))
    iops = serializers.IntegerField(required=True)
    base_price = serializers.IntegerField(required=True)
    rack_space = serializers.IntegerField(required=True)
    power = serializers.IntegerField(required=True)
    btu = serializers.IntegerField(required=True)
    status = serializers.BooleanField(default=True)
    iops_conversion_factor = JSONSerializerField(required=True)
    static_overhead = JSONSerializerField(required=True)
    pcie_slots = serializers.ListField(required=True, child=serializers.IntegerField(required=True))
    gpu_options = serializers.ListField(required=True, child=serializers.CharField(required=True))


class FixedNodePutSerializer(serializers.Serializer):

    id = serializers.CharField(required=False)
    vendor = serializers.CharField(required=True)
    name = serializers.CharField(required=True,
                                 validators=[UniqueValidator(queryset=Node.objects.filter(status=True))])
    type = serializers.ChoiceField(node_types)
    cpu_socket_count = serializers.IntegerField(required=True, min_value=1, max_value=4)
    cores_per_cpu = serializers.IntegerField(required=True, min_value=1, max_value=32)
    ram_slots = serializers.IntegerField(required=False, min_value=1, max_value=32)
    ram_size = serializers.IntegerField(required=True, min_value=1, max_value=1024)
    hdd_slots = serializers.IntegerField(required=True, min_value=1, max_value=100)
    hdd_size = serializers.IntegerField(required=True, min_value=100, max_value=10000)
    ssd_slots = serializers.IntegerField(required=True, min_value=1, max_value=100)
    ssd_size = serializers.IntegerField(required=True, min_value=100, max_value=2000)
    iops = serializers.IntegerField(required=True)
    base_price = serializers.IntegerField(required=True)
    rack_space = serializers.IntegerField(required=True)
    power = serializers.IntegerField(required=True)
    btu = serializers.IntegerField(required=True)
    status = serializers.BooleanField(default=True)


class FixedNodeSerializer(serializers.Serializer):

    id = serializers.CharField(required=False)
    vendor = serializers.CharField(required=True)
    name = serializers.CharField(required=True,
                                 validators=[UniqueValidator(queryset=Node.objects.filter(status=True))])
    type = serializers.ChoiceField(node_types)
    cpu_socket_count = serializers.IntegerField(required=True, min_value=1, max_value=4)
    cores_per_cpu = serializers.IntegerField(required=True, min_value=1, max_value=32)
    ram_slots = serializers.IntegerField(required=False, min_value=1, max_value=32)
    ram_size = serializers.IntegerField(required=True, min_value=1, max_value=1024)
    hdd_slots = serializers.IntegerField(required=True, min_value=1, max_value=100)
    hdd_size = serializers.IntegerField(required=True, min_value=100, max_value=10000)
    ssd_slots = serializers.IntegerField(required=True, min_value=1, max_value=100)
    ssd_size = serializers.IntegerField(required=True, min_value=100, max_value=2000)
    iops = serializers.IntegerField(required=True)
    base_price = serializers.IntegerField(required=True)
    rack_space = serializers.IntegerField(required=True)
    power = serializers.IntegerField(required=True)
    btu = serializers.IntegerField(required=True)
    status = serializers.BooleanField(default=True)


class NodeGetSerializer(serializers.Serializer):

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    node_json = JSONSerializerField()
    created_date = serializers.DateTimeField()
    status = serializers.BooleanField(default=True)


class NodeListGetSerializer(serializers.Serializer):

    name = serializers.CharField()
