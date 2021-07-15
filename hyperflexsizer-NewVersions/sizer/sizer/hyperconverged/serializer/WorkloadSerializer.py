import hyperconverged.strings as strings
from hyperconverged.serializer.CalculatorSerializer import NodeAttributesSerializer
from hyperconverged.solver.attrib import HyperConstants

from rest_framework import serializers

import logging
logger = logging.getLogger(__name__)

REPORT_FORMAT = ["PPT", "PDF"]
BOM_FORMAT = ["XLSX"]


class JSONSerializerField(serializers.Field):

    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class VdiSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.VDI)
    wl_name = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=True)
    num_desktops = serializers.IntegerField(required=True)
    vcpus_per_desktop = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=False)
    ram_per_desktop = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_desktop_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_iops_per_desktop = serializers.IntegerField(required=True)
    user_iops = serializers.IntegerField(required=True)
    disk_per_desktop = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    disk_per_desktop_unit = serializers.ChoiceField(choices=strings.UNITS)
    gold_image_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    gold_image_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    provisioning_type = serializers.CharField(max_length=60)
    status = serializers.BooleanField(default=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    working_set = serializers.IntegerField(default=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=4)
    clock_per_desktop = serializers.IntegerField(required=True)
    concurrency = serializers.IntegerField(required=True)
    cluster_type = serializers.ChoiceField(choices=['normal'])
    gpu_users = serializers.IntegerField(min_value=0, max_value=1)
    video_RAM = serializers.ChoiceField(choices=['512', '1024', '2048', '3072', '4096', '6144', '8192', '12288',
                                                 '16384', '24576', '32768'])


class RdshSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.RDSH)
    wl_name = serializers.CharField(required=True)
    broker_type = serializers.CharField(required=True)
    vcpus_per_vm = serializers.IntegerField(required=True)
    total_users = serializers.IntegerField(required=True)
    sessions_per_vm = serializers.IntegerField(required=True)
    max_vcpus_per_core = serializers.DecimalField(required=True, max_digits=3, decimal_places=2)
    ram_per_vm = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_vm_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    os_per_vm = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    status = serializers.BooleanField(default=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=4)
    clock_per_session = serializers.IntegerField(required=True)
    cluster_type = serializers.ChoiceField(choices=['normal'])
    gpu_users = serializers.IntegerField(min_value=0, max_value=1)
    video_RAM = serializers.ChoiceField(choices=['8192', '12288', '16384', '24576', '32768'])


class VMSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.VSI)
    wl_name = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=True)
    num_vms = serializers.IntegerField(required=True)
    vcpus_per_vm = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_vm = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_vm_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_iops_per_vm = serializers.IntegerField(required=True)
    disk_per_vm = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    disk_per_vm_unit = serializers.ChoiceField(choices=strings.UNITS)
    base_image_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    base_image_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    status = serializers.BooleanField(default=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    snapshots = serializers.IntegerField(required=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=4)
    remote = serializers.BooleanField(default=False)
    replication_amt = serializers.IntegerField(required=True)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)


class DBSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.DB)
    wl_name = serializers.CharField(required=True)
    db_type = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=True)
    num_db_instances = serializers.IntegerField(required=True)
    vcpus_per_db = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_db = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_db_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_iops_per_db = serializers.IntegerField(required=True)
    db_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    db_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    metadata_size = serializers.IntegerField(required=True)
    remote = serializers.BooleanField(default=False)
    replication_amt = serializers.IntegerField(required=True)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)


class OLTPSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.DB)
    wl_name = serializers.CharField(required=True)
    db_type = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=True)
    num_db_instances = serializers.IntegerField(required=True)
    vcpus_per_db = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_db = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_db_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_iops_per_db = serializers.IntegerField(required=True)
    db_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    db_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    metadata_size = serializers.IntegerField(required=True)
    remote = serializers.BooleanField(default=False)
    replication_amt = serializers.IntegerField(required=True)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)


class OLAPSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.DB)
    wl_name = serializers.CharField(required=True)
    db_type = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=True)
    num_db_instances = serializers.IntegerField(required=True)
    vcpus_per_db = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_db = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_db_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_mbps_per_db = serializers.IntegerField(required=True)
    db_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    db_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    metadata_size = serializers.IntegerField(required=True)
    remote = serializers.BooleanField(default=False)
    replication_amt = serializers.IntegerField(required=True)


class ROBOSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.ROBO)
    wl_name = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=True)
    num_vms = serializers.IntegerField(required=True)
    vcpus_per_vm = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_vm = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_vm_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_iops_per_vm = serializers.IntegerField(required=True)
    disk_per_vm = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    disk_per_vm_unit = serializers.ChoiceField(choices=strings.UNITS)
    base_image_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    base_image_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    status = serializers.BooleanField(default=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    snapshots = serializers.IntegerField(required=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=4)
    cluster_type = serializers.ChoiceField(choices=['normal'])
    mod_lan = serializers.ChoiceField(choices=strings.ROBO_LAN)


class RawSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.RAW + strings.RAW_FILE)
    wl_name = serializers.CharField(required=True)
    vcpus = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    cpu_clock = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    cpu_attribute = serializers.ChoiceField(choices=[HyperConstants.VCPUS, HyperConstants.CPU_CLOCK])
    cpu_model = serializers.CharField(required=False)
    ram_size = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    ram_size_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    ram_opratio = serializers.IntegerField(required=False)
    hdd_size = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    hdd_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    ssd_size = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    ssd_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    iops = serializers.IntegerField(required=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)


class ExchangeSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.EXCHANGE)
    wl_name = serializers.CharField(required=True)
    vcpus = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_size_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    hdd_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ssd_size = serializers.IntegerField(required=True)
    EXCHANGE_16KB = serializers.IntegerField(required=True)
    EXCHANGE_32KB = serializers.IntegerField(required=True)
    EXCHANGE_64KB = serializers.IntegerField(required=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)


class ORACLESerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.ORACLE + strings.AWR_FILE)
    wl_name = serializers.CharField(required=True)
    db_type = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=False )
    num_db_instances = serializers.IntegerField(required=False)
    cpu_model = serializers.CharField(required=False)
    vcpus_per_db = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_db = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_db_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_iops_per_db = serializers.IntegerField(required=True)
    db_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    db_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    metadata_size = serializers.IntegerField(required=True)
    remote = serializers.BooleanField(default=False)
    replication_amt = serializers.IntegerField(required=True)


class OOLTPSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.ORACLE + strings.AWR_FILE)
    wl_name = serializers.CharField(required=True)
    db_type = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=False)
    num_db_instances = serializers.IntegerField(required=False)
    cpu_model = serializers.CharField(required=False)
    vcpus_per_db = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_db = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_db_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_iops_per_db = serializers.IntegerField(required=True)
    db_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    db_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    metadata_size = serializers.IntegerField(required=True)
    remote = serializers.BooleanField(default=False)
    replication_amt = serializers.IntegerField(required=True)


class OOLAPSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.ORACLE + strings.AWR_FILE)
    wl_name = serializers.CharField(required=True)
    db_type = serializers.CharField(required=True)
    profile_type = serializers.CharField(required=False)
    num_db_instances = serializers.IntegerField(required=False)
    cpu_model = serializers.CharField(required=False)
    vcpus_per_db = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_db = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_db_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    avg_mbps_per_db = serializers.IntegerField(required=True)
    db_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    db_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    metadata_size = serializers.IntegerField(required=True)
    remote = serializers.BooleanField(default=False)
    replication_amt = serializers.IntegerField(required=True)


class BasicVmSerializer(serializers.Serializer):

    vcpus_per_vm = serializers.IntegerField(required=False)
    ram_per_vm = serializers.DecimalField(max_digits=10, decimal_places=1, required=False)
    ram_per_vm_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    disk_per_vm = serializers.DecimalField(max_digits=10, decimal_places=1, required=False)
    disk_per_vm_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    num_vms = serializers.IntegerField(required=True)
    avg_iops_per_vm = serializers.IntegerField(required=False)


class VdiInfraSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.VDI_INFRA)
    wl_name = serializers.CharField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_opratio = serializers.IntegerField(required=False)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    vm_details = serializers.DictField(child=BasicVmSerializer())
    infra_type = serializers.ChoiceField(choices=strings.VDI_INFRA_TYPES)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)


class EpicDcSerializer(serializers.Serializer):

    dc_name = serializers.CharField(required=True)
    concurrent_user_pcnt = serializers.IntegerField(required=True, min_value=0, max_value=200)
    num_clusters = serializers.IntegerField(required=True, min_value=1, max_value=6)


class EpicSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.EPIC)
    wl_name = serializers.CharField(required=True)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    replication_factor = serializers.IntegerField(default=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=0)
    datacentres = serializers.ListField(child=EpicDcSerializer())
    total_users = serializers.IntegerField(required=True, min_value=1, max_value=100000)
    cpu = serializers.CharField(required=True)
    users_per_host = serializers.IntegerField(required=True, min_value=1, max_value=500)
    ram_per_guest = serializers.IntegerField(required=True, min_value=1, max_value=128)
    ram_per_guest_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    guests_per_host = serializers.IntegerField(required=True, min_value=1, max_value=10000)
    expected_hosts = serializers.IntegerField(required=True, min_value=1, max_value=200)


class VeeamSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.VEEAM)
    wl_name = serializers.CharField(required=True)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    replication_factor = serializers.IntegerField(default=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    hdd_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    hdd_size_unit = serializers.ChoiceField(choices=strings.UNITS)


class StorageAccSerializer(serializers.Serializer):

    hot = serializers.IntegerField()
    cold = serializers.IntegerField(required=False)
    frozen = serializers.IntegerField(required=False)
    warm = serializers.IntegerField(required=False)


class SplunkSerializer(serializers.Serializer):

    wl_type = serializers.ChoiceField(choices=strings.SPLUNK)
    wl_name = serializers.CharField(required=True)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    dedupe_factor = serializers.IntegerField(default=True)
    replication_factor = serializers.IntegerField(default=True)
    app_rf = serializers.IntegerField(required=False)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    daily_data_ingest = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    daily_data_ingest_unit = serializers.ChoiceField(choices=strings.UNITS)
    storage_acc = StorageAccSerializer()
    acc_type = serializers.ChoiceField(choices=['hx+splunk', 'hx+splunk_smartstore'])
    profile_type = serializers.ChoiceField(choices=['Enterprise Security', 'App for VMWare',
                                                    'IT Service Intelligence', 'ITOA (IT Operations Analytics)'])
    max_vol_ind = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    max_vol_ind_unit = serializers.ChoiceField(choices=strings.UNITS)
    vm_details = serializers.DictField(child=BasicVmSerializer())


class ContainerSerializer(serializers.Serializer):
    wl_type = serializers.ChoiceField(choices=strings.CONTAINER)
    wl_name = serializers.CharField(required=True)
    container_type = serializers.CharField(required=True)
    num_containers = serializers.IntegerField(required=True)
    vcpus_per_container = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_container = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    ram_per_container_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    iops_per_container = serializers.IntegerField(required=True)
    disk_per_container = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    disk_per_container_unit = serializers.ChoiceField(choices=strings.UNITS)
    base_image_size = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    base_image_size_unit = serializers.ChoiceField(choices=strings.UNITS)
    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=4)
    remote = serializers.BooleanField(default=False)
    replication_amt = serializers.IntegerField(required=True)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    working_set = serializers.IntegerField(default=True)

class AIMLSerializer(serializers.Serializer):
    wl_type = serializers.ChoiceField(choices=strings.AIML)
    wl_name = serializers.CharField(required=True)
    cluster_type = serializers.ChoiceField(choices=strings.CLUSTER_TYPES)
    num_data_scientists = serializers.IntegerField(required=True)
    input_type = serializers.ChoiceField(choices=['Text Input', 'Video', 'Custom'])
    expected_util = serializers.ChoiceField(choices=['PoC', 'Serious Development'])

    vcpus_per_ds = serializers.IntegerField(required=True)
    vcpus_per_core = serializers.IntegerField(required=True)
    ram_per_ds = serializers.DecimalField(max_digits=10, decimal_places=1, required=False)
    ram_per_ds_unit = serializers.ChoiceField(choices=strings.UNITS, required=False)
    gpu_per_ds = serializers.IntegerField(required=True)
    enablestorage = serializers.BooleanField(default=False)
    disk_per_ds = serializers.DecimalField(max_digits=10, decimal_places=1, required=True)
    disk_per_ds_unit = serializers.ChoiceField(choices=strings.UNITS)

    replication_factor = serializers.IntegerField(default=True)
    compression_factor = serializers.IntegerField(default=True)
    dedupe_factor = serializers.IntegerField(default=True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)


class FilterSerializer(serializers.Serializer):
    Node_Type = serializers.ListField(required=True, child=serializers.CharField(required=False))
    Compute_Type = serializers.ListField(required=True, child=serializers.CharField(required=False))
    CPU_Type = serializers.ListField(required=True, child=serializers.CharField(required=False))
    Clock = serializers.ListField(required=True, child=serializers.CharField(required=False))
    RAM_Slots = serializers.ListField(required=True, child=serializers.IntegerField(required=False))
    RAM_Options = serializers.ListField(required=True, child=serializers.CharField(required=False))
    Disk_Options = serializers.ListField(required=True, child=serializers.CharField(required=False))
    GPU_Type = serializers.ListField(required=True, child=serializers.CharField(required=False))


class SettingSerializer(serializers.Serializer):

    filters = FilterSerializer(required=False)
    node_properties = NodeAttributesSerializer(required=False)


class WorkloadPostSerializer(serializers.Serializer):

    VDI = VdiSerializer(required=False, many=True)
    RDSH = RdshSerializer(required=False, many=True)
    VM = VMSerializer(required=False, many=True)
    DB = DBSerializer(required=False, many=True)
    RAW = RawSerializer(required=False, many=True)
    OLTP = OLTPSerializer(required=False, many=True)
    OLAP = OLAPSerializer(required=False, many=True)
    ROBO = ROBOSerializer(required=False, many=True)
    ORACLE = ORACLESerializer(required=False, many=True)
    OOLTP = OOLTPSerializer(required=False, many=True)
    OOLAP = OOLAPSerializer(required=False, many=True)
    EXCHANGE = ExchangeSerializer(required=False, many=True)
    VDI_INFRA = VdiInfraSerializer(required=False, many=True)
    EPIC = EpicSerializer(required=False, many=True)
    VEEAM = VeeamSerializer(required=False, many=True)
    SPLUNK = SplunkSerializer(required=False, many=True)
    CONTAINER = ContainerSerializer(required=False, many=True)
    AIML = AIMLSerializer(required=False, many=True)

    settings_json = SettingSerializer()
    sizing_type = serializers.ChoiceField(choices=strings.SIZING_TYPES)

    def validate_VM(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_VDI(self, value_input):

        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_DB(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_RAW(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_EXCHANGE(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_OLTP(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_OLAP(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_ROBO(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_ORACLE(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_OOLTP(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_OOLAP(self, value_input):
        is_exist = None
        for data in value_input:
            for key, value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                            raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_VDI_INFRA(self, value_input):
        is_exist = None
        for data in value_input:
            for key,value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                             raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_EPIC(self, value_input):
        is_exist = None
        for data in value_input:
            for key,value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                             raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_VEEAM(self, value_input):
        is_exist = None
        for data in value_input:
            for key,value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                             raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_SPLUNK(self, value_input):
        is_exist = None
        for data in value_input:
            for key,value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                             raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input

    def validate_AIML(self, value_input):
        is_exist = None
        for data in value_input:
            for key,value in data.items():
                if key == "wl_name":
                    if is_exist:
                        if value == is_exist:
                             raise serializers.ValidationError([{'error': "Workload name can not be same."}])
                    else:
                        is_exist = value
        return value_input


class WorkloadSerializer(serializers.Serializer):

    username = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    status = serializers.BooleanField(default=True)

    def create(self, validated_data):
        """
        Create and return a new `Workload` instance, given the validated data.
        """
        return validated_data


class WorkloadGetSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)
    workload_json = JSONSerializerField()
    workload_result = JSONSerializerField()
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
    settings_json = JSONSerializerField(required=False)
    username = serializers.CharField()
    sizing_type = serializers.ChoiceField(choices=strings.SIZING_TYPES)
    scen_label = serializers.CharField()


class WorkloadGetDetailSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)
    workload_json = JSONSerializerField()
    workload_result = JSONSerializerField()
    created_date = serializers.DateTimeField()
    settings_json = JSONSerializerField(required=False)
    updated_date = serializers.DateTimeField()
    sizing_type = serializers.ChoiceField(choices=strings.SIZING_TYPES)
    scen_label = serializers.CharField()


class ScenarioGetSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)


class ScenarioGetBasicSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField()
    setting_json = JSONSerializerField(required=False)


class CloneSettingsSerializer(serializers.Serializer):

    account = serializers.CharField()
    deal_id = serializers.CharField()


class ScenarioCloneSerializer(serializers.Serializer):

    name = serializers.CharField()
    settings_json = CloneSettingsSerializer()


class GenerateReportSerializer(serializers.Serializer):

    type = serializers.ChoiceField(REPORT_FORMAT)
    download = serializers.BooleanField(required=False)
    email = serializers.BooleanField(required=False)


class ResultsSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    result_json = JSONSerializerField()
    settings_json = JSONSerializerField()
    scenario_id = serializers.IntegerField()
    created_date = serializers.DateTimeField()
    name = serializers.CharField()


class GenerateBOMexcelSerializer(serializers.Serializer):

    type = serializers.ChoiceField(BOM_FORMAT)
    download = serializers.BooleanField(required = False)
    email = serializers.BooleanField(required = False)
    nodetype = serializers.CharField()


class SharedScenarioSerializer(serializers.Serializer):

    users_list = JSONSerializerField()


class UCSizerSerializer(serializers.Serializer):
    vcpus = serializers.IntegerField(required = False)
    ram_size = serializers.IntegerField()
    ram_size_unit = serializers.ChoiceField(choices=['GB', 'GiB', 'TB', 'TiB'])
    hdd_size = serializers.IntegerField()
    hdd_size_unit = serializers.ChoiceField(choices=['GB', 'GiB', 'TB', 'TiB'])
    cpu_clock = serializers.DecimalField(max_digits=10, decimal_places=2, required = False)
    cpu_attribute = serializers.ChoiceField(choices=[HyperConstants.VCPUS, HyperConstants.CPU_CLOCK], required = True)
    fault_tolerance = serializers.IntegerField(required=True, min_value=0, max_value=2)
    nodetype = serializers.ChoiceField(choices=[HyperConstants.BUNDLE_ONLY, HyperConstants.CTO_ONLY, "all"],
                                       required = False)


class FixedResultsSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    result_json = JSONSerializerField()
    scenario_id = serializers.IntegerField()
    created_date = serializers.DateTimeField()
    cluster_name = serializers.CharField()
