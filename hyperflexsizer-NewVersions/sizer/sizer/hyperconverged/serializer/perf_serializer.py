from rest_framework import serializers
from hyperconverged.models import HxPerfNumbers


class HxGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = HxPerfNumbers
        fields = ('server_type', 'hypervisor', 'wl_type', 'threshold', 'node_substring', 'ssd_string',
                  'replication_factor', 'iops_type', 'iops_value')
