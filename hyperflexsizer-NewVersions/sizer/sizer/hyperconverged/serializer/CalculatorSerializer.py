from rest_framework import serializers

class NodeAttributesSerializer(serializers.Serializer):

    node = serializers.CharField(max_length=100)
    cpu = serializers.ListField(required=True)
    disk_capacity = serializers.ListField(required=True)
    disks_per_node = serializers.IntegerField()
    no_of_nodes = serializers.IntegerField()
    no_of_computes = serializers.IntegerField()
    ram = serializers.ListField(required=True)
    cache_size = serializers.ListField(required=True)
    supported_workloads = serializers.ListField(required=False)


class ScenarioSettingSerializer(serializers.Serializer):

    compression_factor = serializers.IntegerField(min_value=0, max_value=99)
    dedupe_factor = serializers.IntegerField(min_value=0, max_value=99)
    ft = serializers.ChoiceField(choices=[0, 1, 2])
    threshold = serializers.ChoiceField(choices=[0, 1, 2, 3])
    rf = serializers.ChoiceField(choices=[2, 3])


class ReverseSizerCalculatorSerializer(serializers.Serializer):

    node_properties = NodeAttributesSerializer()
    scenario_settings = ScenarioSettingSerializer(required=False)


class BenchSheetSerializer(serializers.Serializer):

    node = serializers.CharField(max_length=100)
    disk_capacity = serializers.IntegerField()
    disks_per_node = serializers.IntegerField()
    rf = serializers.ChoiceField(choices=[2, 3])
    cache_size = serializers.IntegerField()
    no_of_nodes = serializers.IntegerField()
    no_of_vms = serializers.IntegerField(required=False)

