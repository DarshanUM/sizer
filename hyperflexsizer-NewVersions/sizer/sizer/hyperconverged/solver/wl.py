import logging
from math import ceil
from collections import defaultdict
from copy import deepcopy
from django.core.exceptions import ObjectDoesNotExist

from base_sizer.solver.wl import WL, Infrastructure
from base_sizer.solver.attrib import BaseConstants
from .attrib import HyperConstants
from hyperconverged.models import SpecIntData

logger = logging.getLogger(__name__)


class WL_Raw(WL):

    def __init__(self, attrib, herc_conf):

        super(WL_Raw, self).__init__(attrib)

        self.num_inst = 1

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        if HyperConstants.RAW_OVERHEAD_PERCENTAGE not in self.attrib:
            if self.attrib[BaseConstants.WL_TYPE] == HyperConstants.RAW_FILE:
                self.attrib[HyperConstants.RAW_OVERHEAD_PERCENTAGE] = 10
            else:
                self.attrib[HyperConstants.RAW_OVERHEAD_PERCENTAGE] = 0

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        input_cpu = self.attrib.get(HyperConstants.CPU_MODEL, None)

        try:
            if not input_cpu:
                cpu_model = SpecIntData.objects.get(is_base_model=True)
            else:
                cpu_model = SpecIntData.objects.get(model=input_cpu)
        except ObjectDoesNotExist:
            raise Exception("Input CPU model doesn't exist")

        safety_overhead = self.attrib.get(HyperConstants.RAW_OVERHEAD_PERCENTAGE, 0) / 100.0

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                if self.attrib[HyperConstants.CPU_ATTRIBUTE] == HyperConstants.CPU_CLOCK:
                    vcpus = self.attrib[HyperConstants.CPU_CLOCK] / float(cpu_model.speed)
                    cpu_cores = vcpus / float(self.attrib[HyperConstants.VCPUS_PER_CORE])
                else:
                    cpu_cores = self.attrib[HyperConstants.VCPUS] / float(self.attrib[HyperConstants.VCPUS_PER_CORE])

                normalized_cores = cpu_cores * self.normalise_cpu(cpu_model)

                self.capsum['normal'][cap] = ceil(normalized_cores * (1 + safety_overhead))

            elif cap == BaseConstants.RAM:

                ram_size = self.unit_conversion(self.attrib[BaseConstants.RAM_SIZE],
                                                self.attrib[BaseConstants.RAM_SIZE_UNIT], 'GiB')

                ram_size /= float(self.attrib.get(HyperConstants.RAM_OPRATIO, 1))

                self.capsum['normal'][cap] = ram_size * (1 + safety_overhead)

            elif cap == BaseConstants.HDD:

                hdd_size = self.unit_conversion(self.attrib[BaseConstants.HDD_SIZE],
                                                self.attrib[BaseConstants.HDD_SIZE_UNIT])

                effective_hdd = hdd_size * (1 + safety_overhead)

                self.capsum['normal'][cap] = effective_hdd * self.compression * self.dedupe

                self.original_size = effective_hdd

            elif cap == BaseConstants.SSD:

                continue

            elif cap == BaseConstants.IOPS:

                # To handle corner case during resizing the old sceanrio.
                if HyperConstants.IO_BLOCK_SIZE in self.attrib :
                    self.original_iops_sum = {self.attrib[HyperConstants.IO_BLOCK_SIZE]: self.attrib[HyperConstants.IOPS_VALUE]}
                else:
                    self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: 0}

            elif cap == BaseConstants.VRAM:

                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp


class WL_VDI(WL):

    def __init__(self, attrib, herc_conf):

        super(WL_VDI, self).__init__(attrib)

        self.num_inst = self.attrib[HyperConstants.NUM_DT]

        defaults = {HyperConstants.DT_INFLIGHT_DEDUPE: 35,
                    HyperConstants.IMAGE_DEDUPE: 45,
                    HyperConstants.DT_REPLICATION_FACTOR: 0}

        for key, def_value in defaults.items():
            if key not in self.attrib:
                self.attrib[key] = def_value

        self.attrib[HyperConstants.INFLIGHT_DATA] = max(6, self.attrib[HyperConstants.RAM_PER_DT] * 2)

        if not self.attrib[HyperConstants.DT_REPLICATION_FACTOR]:
            self.attrib[HyperConstants.DT_REPLICATION_MULT] = 1
        else:
            self.attrib[HyperConstants.DT_REPLICATION_MULT] = self.attrib[HyperConstants.DT_REPLICATION_FACTOR]

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        base_cpu = SpecIntData.objects.get(is_base_model=True)
        num_active_dts = (self.attrib[HyperConstants.CONCURRENCY] / 100.0) * self.num_inst

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.capsum['normal'][HyperConstants.CLOCK] = (self.attrib[HyperConstants.DT_CLOCK_SPEED] / 1000.0) * \
                                                              num_active_dts

                self.capsum['normal'][cap] = \
                    self.capsum['normal'][HyperConstants.CLOCK] / float(base_cpu.speed) * self.normalise_cpu()

            elif cap == BaseConstants.RAM:

                if HyperConstants.RAM_PER_DT_UNIT not in self.attrib:
                    self.attrib[HyperConstants.RAM_PER_DT_UNIT] = 'GiB'

                ram_per_desktop = self.unit_conversion(self.attrib[HyperConstants.RAM_PER_DT],
                                                self.attrib[HyperConstants.RAM_PER_DT_UNIT], 'GiB')

                self.capsum['normal'][cap] = ram_per_desktop * num_active_dts

            elif cap == BaseConstants.HDD:

                inflight_dedupe = (100 - self.attrib[HyperConstants.DT_INFLIGHT_DEDUPE]) / 100.0

                image_dedupe = (100 - self.attrib[HyperConstants.IMAGE_DEDUPE]) / 100.0

                inflight_size = self.attrib[HyperConstants.INFLIGHT_DATA]

                if self.attrib[HyperConstants.VDI_DIRECTORY] == 0:
                    hdd_size = 0
                else:
                    hdd_size = self.unit_conversion(self.attrib[HyperConstants.HDD_PER_DT],
                                                    self.attrib[HyperConstants.HDD_PER_DT_UNIT])

                image_size = self.unit_conversion(self.attrib[HyperConstants.GOLD_IMG_SIZE],
                                                 self.attrib[HyperConstants.GOLD_IMG_SIZE_UNIT])

                snapshot_factor = self.attrib[HyperConstants.DT_SNAPSHOTS] * 0.02 + 1

                if self.attrib[HyperConstants.DT_PROV_TYPE] in [HyperConstants.VIEW_FULL]:

                    self.user_data = hdd_size * self.compression * self.dedupe
                    self.os_data = (image_dedupe * image_size)

                    self.capsum['normal'][cap] = self.num_inst * (self.user_data + self.os_data) * snapshot_factor

                    self.original_size = self.num_inst * (hdd_size + image_size) * snapshot_factor
                else:

                    self.user_data = hdd_size * self.compression * self.dedupe
                    self.os_data = inflight_size * inflight_dedupe

                    self.capsum['normal'][cap] = self.num_inst * (self.user_data + self.os_data) * snapshot_factor + \
                                                 image_size

                    self.original_size = self.num_inst * (hdd_size + inflight_size) * snapshot_factor + image_size

            elif cap == BaseConstants.SSD:

                ssd_multiplier = self.attrib[HyperConstants.DT_WORKING_SET_SIZE] / 100.0

                if self.attrib[HyperConstants.DT_PROV_TYPE] in [HyperConstants.VIEW_FULL]:

                    self.capsum['normal'][cap] = (self.user_data + self.os_data) * self.num_inst * ssd_multiplier

                else:

                    self.capsum['normal'][cap] = ((self.user_data + self.os_data) * self.num_inst + image_size) * \
                                                 ssd_multiplier

            elif cap == BaseConstants.IOPS:

                os_iops_per_dt = self.attrib[HyperConstants.IOPS_PER_DT]

                total_os_iops = os_iops_per_dt * num_active_dts

                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: total_os_iops}

            elif cap == BaseConstants.VRAM:

                if not self.attrib[HyperConstants.GPU_STATUS]:
                    self.frame_buff = 0
                else:
                    self.frame_buff = int(self.attrib[HyperConstants.VIDEO_RAM])

                # As UI Parses Data in MiB, converting data to GiB
                self.capsum['normal'][cap] = self.num_inst * self.frame_buff / 1024

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.HDD:

                image_size = self.unit_conversion(self.attrib[HyperConstants.GOLD_IMG_SIZE],
                                                  self.attrib[HyperConstants.GOLD_IMG_SIZE_UNIT])

                snapshot_factor = self.attrib[HyperConstants.DT_SNAPSHOTS] * 0.02 + 1

                self.user_data *= self.herc_comp

                if self.attrib[HyperConstants.DT_PROV_TYPE] in [HyperConstants.VIEW_FULL]:

                    self.capsum['hercules'][cap] = self.num_inst * (self.user_data + self.os_data) * snapshot_factor
                else:
                    self.capsum['hercules'][cap] = self.num_inst * (self.user_data + self.os_data) * snapshot_factor + \
                                                   image_size

            elif cap == BaseConstants.SSD:

                ssd_multiplier = self.attrib[HyperConstants.DT_WORKING_SET_SIZE] / 100.0

                if self.attrib[HyperConstants.DT_PROV_TYPE] in [HyperConstants.VIEW_FULL]:
                    self.capsum['hercules'][cap] = (self.user_data + self.os_data) * self.num_inst * ssd_multiplier

                else:
                    self.capsum['hercules'][cap] = ((self.user_data + self.os_data) * self.num_inst + image_size) * \
                                                   ssd_multiplier


class WL_VDI_HOME(WL):

    def __init__(self, attrib, herc_conf):

        super(WL_VDI_HOME, self).__init__(attrib)

        self.num_inst = self.attrib[HyperConstants.NUM_DT]
        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

        self.attrib['internal_type'] = HyperConstants.VDI_HOME

        self.attrib = {attr: self.attrib[attr] for attr in ['profile','primary_wl_name','replication_factor',
                                                            'wl_name','wl_type', 'fault_tolerance', 'number_of_vms',
                                                            'internal_type', 'cluster_type', 'concurrency',
                                                            'storage_protocol']}

    def calc_cap_normal(self):

        self.attrib['primary_wl_name'] = self.attrib[BaseConstants.WL_NAME]
        self.attrib[BaseConstants.WL_NAME] += "_HOME"

        total_iops = float(self.attrib[HyperConstants.USER_DATA_IOPS] * self.num_inst)

        total_hdd_size = float(WL.unit_conversion(self.attrib[HyperConstants.HDD_PER_DT],
                                                    self.attrib[HyperConstants.HDD_PER_DT_UNIT]) * self.num_inst)

        for profile, vm_details in HyperConstants.HOME_CONFIG.items():

            if profile == 'Small' or profile == 'Medium':
                if vm_details['max_data'] >= total_hdd_size and vm_details['max_iops'] >= total_iops:
                    vm_count = 1
                    self.attrib['profile'] = profile
                    break
            elif profile == 'Large':
                vm_count = max(total_hdd_size / vm_details['max_data'],
                               total_iops / vm_details['max_iops'])
                vm_count = int(ceil(vm_count))
                self.attrib['profile'] = profile

        self.attrib['number_of_vms'] = vm_count

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                num_active_vms = self.attrib[HyperConstants.CONCURRENCY] / 100.0 * self.attrib['number_of_vms']

                self.capsum['normal'][cap] = float(HyperConstants.HOME_CONFIG[profile]['cpu']) * \
                                             WL.normalise_cpu() * num_active_vms

            elif cap == BaseConstants.RAM:

                num_active_vms = self.attrib[HyperConstants.CONCURRENCY] / 100.0 * self.attrib['number_of_vms']

                self.capsum['normal'][cap] = HyperConstants.HOME_CONFIG[profile]['ram'] * num_active_vms

            elif cap == BaseConstants.HDD:

                self.original_size = 0

            elif cap == BaseConstants.IOPS:

                user_iops_per_dt = self.attrib[HyperConstants.USER_DATA_IOPS]

                total_user_iops = user_iops_per_dt * self.num_inst
                self.original_iops_sum = {HyperConstants.VDI_HOME: total_user_iops}

            else:
                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])


class WL_RDSH(WL):

    def __init__(self, attrib, herc_conf):

        super(WL_RDSH, self).__init__(attrib)

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.num_vms = int(ceil(self.attrib['total_users'] / self.attrib['sessions_per_vm']))

        # Amount of GHz required by one VM
        self.clock_per_vm = (self.attrib[HyperConstants.CLOCK_PER_SESSION] / 1000.0) * self.attrib['sessions_per_vm']

        # Minimum physical cores needed.
        min_cores_per_vm = self.attrib['vcpus_per_vm'] / float(self.attrib['max_vcpus_per_core'])
        self.max_clock_per_core = self.clock_per_vm / min_cores_per_vm

        self.original_iops_sum = dict()
        self.original_size = 0

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        base_cpu = SpecIntData.objects.get(is_base_model=True)

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.capsum['normal'][cap] = (self.attrib[HyperConstants.CLOCK_PER_SESSION] / 1000.0) * \
                                             self.attrib['total_users'] / base_cpu.speed * WL.normalise_cpu()

            elif cap == BaseConstants.RAM:

                if HyperConstants.RAM_PER_VM_UNIT not in self.attrib:
                    self.attrib[HyperConstants.RAM_PER_VM_UNIT] = 'GiB'

                ram_per_vm = self.unit_conversion(self.attrib[HyperConstants.RAM_PER_VM],
                                                       self.attrib[HyperConstants.RAM_PER_VM_UNIT], 'GiB')

                self.capsum['normal'][cap] = ram_per_vm * self.num_vms

            elif cap == BaseConstants.HDD:

                if self.attrib[HyperConstants.RDSH_DIRECTORY] == 0:
                    hdd_size = 0
                else:
                    hdd_size = self.unit_conversion(self.attrib[HyperConstants.HDD_PER_USER],
                                                    self.attrib[HyperConstants.HDD_PER_USER_UNIT])

                image_size = self.unit_conversion(self.attrib[HyperConstants.OS_PER_VM],
                                                  self.attrib[HyperConstants.OS_PER_VM_UNIT])

                self.user_data = hdd_size * self.attrib['total_users']

                self.os_data = image_size * self.num_vms

                self.original_size =  self.user_data + self.os_data

                self.capsum['normal'][cap] = (self.user_data * self.compression * self.dedupe) + self.os_data

            elif cap == BaseConstants.SSD:

                ssd_multiplier = self.attrib[HyperConstants.VM_WORKING_SET_SIZE] / 100.0

                self.capsum['normal'][cap] = (self.user_data + self.os_data) * ssd_multiplier

            elif cap == BaseConstants.IOPS:

                self.original_iops_sum[self.attrib[HyperConstants.INTERNAL_TYPE]] = 0

            elif cap == BaseConstants.VRAM:

                # As UI Parses Data in MiB, converting data to GiB

                if not self.attrib[HyperConstants.GPU_STATUS]:
                    self.frame_buff = 0
                else:
                    self.frame_buff = int(self.attrib[HyperConstants.VIDEO_RAM])

                self.capsum['normal'][cap] = self.num_vms * self.frame_buff / 1024

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        for cap in HyperConstants.WL_CAP_LIST:
            if cap == BaseConstants.HDD:
                self.capsum['hercules'][cap] = (self.user_data * self.compression * self.dedupe * self.herc_comp) + \
                                               self.os_data


class WL_RDSH_HOME(WL):

    def __init__(self, attrib, herc_conf):

        super(WL_RDSH_HOME,self).__init__(attrib)

        self.num_inst = self.attrib['total_users']
        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

        self.attrib['internal_type'] = HyperConstants.RDSH_HOME

        self.attrib = {attr: self.attrib[attr] for attr in ['profile','primary_wl_name','replication_factor',
                                                            'wl_name','wl_type', 'fault_tolerance', 'number_of_vms',
                                                            'internal_type', 'cluster_type', 'storage_protocol']}

    def calc_cap_normal(self):

        self.attrib['primary_wl_name'] = self.attrib[BaseConstants.WL_NAME]
        self.attrib[BaseConstants.WL_NAME] += "_HOME"

        total_iops = float(self.attrib[HyperConstants.USER_DATA_IOPS] * self.num_inst)

        total_hdd_size = float(WL.unit_conversion(self.attrib[HyperConstants.HDD_PER_USER],
                                                  self.attrib[HyperConstants.HDD_PER_USER_UNIT]) * self.num_inst)

        for profile, vm_details in HyperConstants.HOME_CONFIG.items():

            if profile == 'Small' or profile == 'Medium':
                if vm_details['max_data'] >= total_hdd_size and vm_details['max_iops'] >= total_iops:
                    vm_count = 1
                    self.attrib['profile'] = profile
                    break
            elif profile == 'Large':
                vm_count = max(total_hdd_size / vm_details['max_data'],
                               total_iops / vm_details['max_iops'])
                vm_count = int(ceil(vm_count))
                self.attrib['profile'] = profile

        self.attrib['number_of_vms'] = vm_count

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.capsum['normal'][cap] = float(HyperConstants.HOME_CONFIG[profile]['cpu']) * \
                                             WL.normalise_cpu() * self.attrib['number_of_vms']

            elif cap == BaseConstants.RAM:

                self.capsum['normal'][cap] = HyperConstants.HOME_CONFIG[profile]['ram'] * self.attrib['number_of_vms']

            elif cap == BaseConstants.HDD:

                self.original_size = 0

            elif cap == BaseConstants.IOPS:

                user_iops_per_vm = self.attrib[HyperConstants.USER_DATA_IOPS]

                total_user_iops = user_iops_per_vm * self.num_inst
                self.original_iops_sum = {HyperConstants.RDSH_HOME: total_user_iops}

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])


class WL_VM(WL):

    def __init__(self, attrib, herc_conf):

        super(WL_VM, self).__init__(attrib)

        self.num_inst = 0

        if HyperConstants.VM_SNAPSHOTS not in self.attrib:
            self.attrib[HyperConstants.VM_SNAPSHOTS] = 0

        if not self.attrib[HyperConstants.VM_REPLICATION_FACTOR]:
            self.attrib[HyperConstants.VM_REPLICATION_MULT] = 1
        else:
            self.attrib[HyperConstants.VM_REPLICATION_MULT] = self.attrib[HyperConstants.VM_REPLICATION_FACTOR]

        if HyperConstants.REPLICATION_AMT not in self.attrib:
            self.attrib[HyperConstants.REPLICATION_AMT] = 100

        if 'remote' not in self.attrib:
            self.attrib['remote'] = False

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self, work_load_type=HyperConstants.NORMAL):

        if work_load_type == HyperConstants.REPLICATED:
            self.num_inst = int(ceil(self.attrib[HyperConstants.REPLICATION_AMT] *
                                     self.attrib[HyperConstants.NUM_VM] / 100.0))
        else:
            self.num_inst = self.attrib[HyperConstants.NUM_VM]

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.capsum['normal'][cap] = \
                    (float(self.attrib[HyperConstants.VCPUS_PER_VM]) /
                     float(self.attrib[HyperConstants.VCPUS_PER_CORE])) * self.normalise_cpu() * self.num_inst

            elif cap == BaseConstants.RAM:

                if HyperConstants.RAM_PER_VM_UNIT not in self.attrib:
                    self.attrib[HyperConstants.RAM_PER_VM_UNIT] = 'GiB'

                ram_per_vm = self.unit_conversion(self.attrib[HyperConstants.RAM_PER_VM],
                                                  self.attrib[HyperConstants.RAM_PER_VM_UNIT], 'GiB')

                self.capsum['normal'][cap] = ram_per_vm * self.num_inst

            elif cap == BaseConstants.HDD:

                hdd_size = self.unit_conversion(self.attrib[HyperConstants.HDD_PER_VM],
                                                self.attrib[HyperConstants.HDD_PER_VM_UNIT])

                image_size = self.unit_conversion(self.attrib[HyperConstants.VM_BASE_IMG_SIZE],
                                                  self.attrib[HyperConstants.VM_BASE_IMG_SIZE_UNIT])

                self.capsum['normal'][cap] = \
                    self.num_inst * (hdd_size + image_size +
                                     (0.02 * hdd_size * self.attrib[HyperConstants.VM_SNAPSHOTS])) * \
                    self.compression * self.dedupe

                self.original_size = \
                    self.num_inst * (hdd_size + image_size + (0.02 * hdd_size *
                                                              self.attrib[HyperConstants.VM_SNAPSHOTS]))

            elif cap == BaseConstants.SSD:

                ssd_multiplier = self.attrib[HyperConstants.VM_WORKING_SET_SIZE] / 100.0 * self.dedupe

                self.capsum['normal'][cap] = self.original_size * ssd_multiplier

            elif cap == BaseConstants.IOPS:

                iops_per_vm = self.attrib[HyperConstants.IOPS_PER_VM]

                if work_load_type == HyperConstants.NORMAL:

                    num_replicated_vms = int(ceil(self.attrib[HyperConstants.NUM_VM] *
                                                  self.attrib[HyperConstants.REPLICATION_AMT] / 100.0))

                    total_iops = iops_per_vm * ((self.num_inst - num_replicated_vms) + (num_replicated_vms * 1.3))

                    self.replication_traffic = iops_per_vm * num_replicated_vms * 0.3

                elif work_load_type == HyperConstants.REPLICATED and self.attrib[HyperConstants.REPLICATION_AMT]:

                    total_iops = iops_per_vm * self.num_inst * 1.3

                    self.replication_traffic = iops_per_vm * self.num_inst * 0.3

                else:

                    total_iops = iops_per_vm * self.num_inst

                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: total_iops}

            elif cap == BaseConstants.VRAM:

                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp


class Wldb(object):

    """Base class for calculation."""

    def __init__(self, attrib):

        self.methods_dict = {BaseConstants.CPU: "get_cpu_value",
                             BaseConstants.RAM: "get_ram_value",
                             BaseConstants.HDD: "get_hdd_value",
                             BaseConstants.SSD: "get_ssd_value",
                             BaseConstants.IOPS: "get_iops_value"}

        self.attrib = attrib
        self.num_inst = 0

        self.capsum = {
            'hercules': defaultdict(int),
            'normal': defaultdict(int)
        }

    def set_comp_dedupe(self, comp_fac, dedupe_fac):

        self.compression = (100 - comp_fac) / 100.0
        self.dedupe = (100 - dedupe_fac) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

    def get_cpu_value(self):

        """Calculating CPU value."""
        cpu_capacity = \
            float(self.attrib[HyperConstants.VCPUS_PER_DB]) / float(self.attrib[HyperConstants.VCPUS_PER_CORE])

        cpu_model = None

        if self.attrib[BaseConstants.WL_TYPE] == HyperConstants.AWR_FILE:

            input_cpu = self.attrib.get(HyperConstants.CPU_MODEL, None)

            try:
                if not input_cpu:
                    cpu_model = SpecIntData.objects.get(is_base_model=True)
                else:
                    cpu_model = SpecIntData.objects.get(model=input_cpu)
            except ObjectDoesNotExist:
                raise Exception("Input CPU model doesn't exist")

        cpu_capacity *= WL.normalise_cpu(cpu_model)

        return self.num_inst * cpu_capacity

    def get_ram_value(self):

        """Calculating RAM value."""

        if HyperConstants.RAM_PER_DB_UNIT not in self.attrib:
            self.attrib[HyperConstants.RAM_PER_DB_UNIT] = 'GiB'

        ram_capacity = WL.unit_conversion(self.attrib[HyperConstants.RAM_PER_DB],
                                                self.attrib[HyperConstants.RAM_PER_DB_UNIT], 'GiB')

        return self.num_inst * ram_capacity

    def get_ssd_value(self):

        """Calculating SSD value."""

        ssd_capacity = WL.unit_conversion(self.attrib[HyperConstants.DB_SIZE],
                                          self.attrib[HyperConstants.DB_SIZE_UNIT]) * 0.2 * self.dedupe
        return self.num_inst * ssd_capacity

    def get_hdd_value(self, node_type):

        """Calculating HDD value."""

        db_size = WL.unit_conversion(self.attrib[HyperConstants.DB_SIZE],
                                      self.attrib[HyperConstants.DB_SIZE_UNIT])

        total_base_size = db_size * (1 + (self.attrib[HyperConstants.META_DATA] / 100.0))

        original_size = self.num_inst * total_base_size

        if node_type == 'normal':

            hdd_capacity = total_base_size * self.compression * self.dedupe

            total_hdd_capacity = self.num_inst * hdd_capacity

        elif node_type == 'hercules':

            hdd_capacity = total_base_size * self.compression * self.dedupe * self.herc_comp

            total_hdd_capacity = self.num_inst * hdd_capacity

        return total_hdd_capacity, original_size

    def get_iops_value(self, work_load_type):

        """Calculating IOPS value."""
        iops_cap = self.attrib[HyperConstants.IOPS_PER_DB]

        if work_load_type == HyperConstants.NORMAL:

            num_replicated_dbs = int(ceil(self.num_inst * self.attrib[HyperConstants.REPLICATION_AMT] / 100.0))

            iops_value = \
                iops_cap * ((self.num_inst - num_replicated_dbs) + (num_replicated_dbs * 1.3))

            self.replication_traffic = iops_cap * num_replicated_dbs * 0.3

        elif work_load_type == HyperConstants.REPLICATED and self.attrib[HyperConstants.REPLICATION_AMT]:

            iops_value = iops_cap * self.num_inst * 1.3

            self.replication_traffic = iops_cap * self.num_inst * 0.3

        else:

            iops_value = iops_cap * self.num_inst

        return iops_value

    def calc_cap_normal(self, work_load_type=HyperConstants.NORMAL):

        """Calculating caplist for workload. """
        if self.attrib[BaseConstants.WL_TYPE] == HyperConstants.AWR_FILE:
            self.attrib[HyperConstants.NUM_DB] = 1

        if work_load_type == HyperConstants.REPLICATED:
            self.num_inst = int(ceil(self.attrib[HyperConstants.REPLICATION_AMT] *
                                     self.attrib[HyperConstants.NUM_DB] / 100.0))
        else:
            self.num_inst = self.attrib[HyperConstants.NUM_DB]

        self.set_comp_dedupe(self.attrib[HyperConstants.COMPRESSION_FACTOR],
                             self.attrib[HyperConstants.DEDUPE_FACTOR])

        for cap in HyperConstants.WL_CAP_LIST:

            if cap in self.methods_dict:

                func_name = getattr(self, self.methods_dict[cap])

                if cap == BaseConstants.HDD:

                    self.capsum['normal'][cap], self.original_size = func_name('normal')

                elif cap == BaseConstants.IOPS:

                    self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: func_name(work_load_type)}

                else:
                    self.capsum['normal'][cap] = func_name()

        return True

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        for cap in HyperConstants.WL_CAP_LIST:

            if cap in self.methods_dict:

                func_name = getattr(self, self.methods_dict[cap])

                if cap == BaseConstants.HDD:

                    self.capsum['hercules'][cap], _ = func_name('hercules')

    def to_json(self):
        """returning attrib values."""
        return self.attrib


class WL_DB(Wldb):

    def __init__(self, attrib, herc_conf):

        Wldb.__init__(self, attrib)

        self.num_inst = 0

        if self.attrib[HyperConstants.DB_REPLICATION_FACTOR] == 0:
            self.attrib[HyperConstants.DB_REPLICATION_MULT] = 1
        else:
            self.attrib[HyperConstants.DB_REPLICATION_MULT] = self.attrib[HyperConstants.DB_REPLICATION_FACTOR]

        if HyperConstants.REPLICATION_AMT not in self.attrib:
            self.attrib[HyperConstants.REPLICATION_AMT] = 100

        if 'remote' not in self.attrib:
            self.attrib['remote'] = False

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()


class WL_OLTP(WL_DB):
    pass


class WL_OLAP(WL_DB):

    def get_iops_value(self, work_load_type):

        iops_cap = self.attrib[HyperConstants.MBPS_PER_DB] / (64.0/1024)

        if work_load_type == HyperConstants.NORMAL:

            num_replicated_dbs = int(ceil(self.num_inst * self.attrib[HyperConstants.REPLICATION_AMT] / 100.0))

            iops_value = \
                iops_cap * ((self.num_inst - num_replicated_dbs) + (num_replicated_dbs * 1.3))

            self.replication_traffic = iops_cap * num_replicated_dbs * 0.3

        elif work_load_type == HyperConstants.REPLICATED and self.attrib[HyperConstants.REPLICATION_AMT]:

            iops_value = iops_cap * self.num_inst * 1.05

            self.replication_traffic = iops_cap * self.num_inst * 0.05

        else:
            iops_value = iops_cap * self.num_inst

        return iops_value


class WL_ROBO(WL):

    def __init__(self, attrib, herc_conf):

        super(WL_ROBO, self).__init__(attrib)

        self.num_inst = self.attrib[HyperConstants.NUM_VM]

        if HyperConstants.VM_SNAPSHOTS not in self.attrib:
            self.attrib[HyperConstants.VM_SNAPSHOTS] = 0

        if self.attrib[HyperConstants.VM_REPLICATION_FACTOR] == 0:
            self.attrib[HyperConstants.VM_REPLICATION_MULT] = 1
        else:
            self.attrib[HyperConstants.VM_REPLICATION_MULT] = self.attrib[HyperConstants.VM_REPLICATION_FACTOR]

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.capsum['normal'][cap] = float(self.attrib[HyperConstants.VCPUS_PER_VM]) / \
                                             float(self.attrib[HyperConstants.VCPUS_PER_CORE]) * \
                                             self.normalise_cpu() * self.num_inst

            elif cap == BaseConstants.RAM:

                if HyperConstants.RAM_PER_VM_UNIT not in self.attrib:
                    self.attrib[HyperConstants.RAM_PER_VM_UNIT] = 'GiB'

                ram_per_vm = self.unit_conversion(self.attrib[HyperConstants.RAM_PER_VM],
                                                  self.attrib[HyperConstants.RAM_PER_VM_UNIT], 'GiB')

                self.capsum['normal'][cap] = ram_per_vm * self.num_inst

            elif cap == BaseConstants.HDD:

                hdd_size = self.unit_conversion(self.attrib[HyperConstants.HDD_PER_VM],
                                                self.attrib[HyperConstants.HDD_PER_VM_UNIT])

                image_size = self.unit_conversion(self.attrib[HyperConstants.VM_BASE_IMG_SIZE],
                                                  self.attrib[HyperConstants.VM_BASE_IMG_SIZE_UNIT])

                self.capsum['normal'][cap] = \
                    self.num_inst * (hdd_size + image_size + (0.02 * hdd_size *
                                                              self.attrib[HyperConstants.VM_SNAPSHOTS])) * \
                    self.compression * self.dedupe

                self.original_size = \
                    self.num_inst * (hdd_size + image_size + (0.02 * hdd_size *
                                                              self.attrib[HyperConstants.VM_SNAPSHOTS]))

            elif cap == BaseConstants.SSD:

                ssd_multiplier = self.attrib[HyperConstants.VM_WORKING_SET_SIZE] / 100.0 * self.dedupe

                self.capsum['normal'][cap] = self.original_size * ssd_multiplier

            elif cap == BaseConstants.IOPS:

                iops_per_vm = self.attrib[HyperConstants.IOPS_PER_VM]

                total_iops = iops_per_vm * self.num_inst

                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: total_iops}

            elif cap == BaseConstants.VRAM:

                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp


class WL_ORACLE(WL_DB):
    pass


class WL_OOLTP(WL_DB):
    pass


class WL_OOLAP(WL_OLAP):
    pass


class WL_Exchange(WL_Raw):

    def calc_cap_normal(self):

        safety_overhead = self.attrib.get(HyperConstants.RAW_OVERHEAD_PERCENTAGE, 0) / 100.0

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                cpu_cores = \
                    self.attrib[HyperConstants.VCPUS] / float(self.attrib[HyperConstants.VCPUS_PER_CORE]) * \
                    self.normalise_cpu()

                self.capsum['normal'][cap] = cpu_cores * (1 + safety_overhead)

            elif cap == BaseConstants.RAM:

                if BaseConstants.RAM_SIZE_UNIT not in self.attrib:
                    self.attrib[BaseConstants.RAM_SIZE_UNIT] = 'GiB'

                ram_size = self.unit_conversion(self.attrib[BaseConstants.RAM_SIZE],
                                                self.attrib[BaseConstants.RAM_SIZE_UNIT], 'GiB')

                self.capsum['normal'][cap] = ceil(ram_size * (1 + safety_overhead))

            elif cap == BaseConstants.HDD:

                eff_hdd = self.attrib[BaseConstants.HDD_SIZE] * (1 + safety_overhead)

                self.capsum['normal'][cap] = eff_hdd * self.compression * self.dedupe

                self.original_size = eff_hdd

            elif cap == BaseConstants.SSD:

                self.capsum['normal'][cap] = self.attrib[BaseConstants.SSD_SIZE] * self.dedupe * \
                                             self.attrib[HyperConstants.RAW_WORKING_SET_SIZE] / 100.0

            elif cap == BaseConstants.IOPS:

                self.original_iops_sum = {HyperConstants.EXCHANGE_32KB: self.attrib[HyperConstants.EXCHANGE_32KB],
                                          HyperConstants.EXCHANGE_16KB: self.attrib[HyperConstants.EXCHANGE_16KB],
                                          HyperConstants.EXCHANGE_64KB: self.attrib[HyperConstants.EXCHANGE_64KB]}

            elif cap == BaseConstants.VRAM:

                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp


class INFRA_VDI(Infrastructure):

    def __init__(self, attrib, herc_conf):

        self.attrib = attrib
        super(INFRA_VDI, self).__init__(self.attrib['vm_details'])

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.original_iops_sum = None

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def to_json(self):

        return self.attrib

    def calc_cap_normal(self):

        for cap in HyperConstants.WL_CAP_LIST:

            for vm_detail in self.vm_details.values():

                if cap == BaseConstants.CPU:

                    self.capsum['normal'][cap] += \
                        float(vm_detail[HyperConstants.VCPUS_PER_VM]) / self.attrib[HyperConstants.VCPUS_PER_CORE] *  \
                        WL.normalise_cpu() * vm_detail[HyperConstants.NUM_VM]

                elif cap == BaseConstants.RAM:

                    if HyperConstants.RAM_PER_VM_UNIT not in vm_detail:
                        vm_detail[HyperConstants.RAM_PER_VM_UNIT] = 'GiB'

                    ram_per_vm = WL.unit_conversion(vm_detail[HyperConstants.RAM_PER_VM],
                                                        vm_detail[HyperConstants.RAM_PER_VM_UNIT], 'GiB')

                    self.capsum['normal'][cap] += \
                        ram_per_vm / float(self.attrib[HyperConstants.RAM_OPRATIO]) * \
                        vm_detail[HyperConstants.NUM_VM]

                elif cap == BaseConstants.HDD:

                    hdd_size = WL.unit_conversion(vm_detail[HyperConstants.HDD_PER_VM],
                                                  vm_detail[HyperConstants.HDD_PER_VM_UNIT])

                    self.capsum['normal'][cap] += \
                        vm_detail[HyperConstants.NUM_VM] * hdd_size * self.compression * self.dedupe

                    self.original_size += hdd_size * vm_detail[HyperConstants.NUM_VM]

                elif cap == BaseConstants.SSD:

                    continue

                elif cap == BaseConstants.IOPS:

                    self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: 0}

                elif cap == BaseConstants.VRAM:

                    continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp


class EPIC_DATACENTRE(WL):

    def __init__(self, attrib, herc_conf):

        super(EPIC_DATACENTRE, self).__init__(attrib)
        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.original_size = 0
        self.original_iops_sum = None

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        user_concurrency = self.attrib['concurrent_user_pcnt'] / 100.0
        num_clusters = self.attrib['num_clusters']
        users = round(user_concurrency * self.attrib['total_users'] / float(num_clusters))
        ex_hosts_per_cluster = round(user_concurrency * self.attrib['expected_hosts'] / float(num_clusters))

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                if self.attrib['cpu'] == 'Intel 6150':
                    self.attrib['cpu'] = 'Intel Gold 6150'
                elif self.attrib['cpu'] == 'Intel 8168':
                    self.attrib['cpu'] = 'Intel Platinum 8168'

                input_cpu = SpecIntData.objects.get(model=self.attrib['cpu'])
                total_clock_per_host = 2 * input_cpu.speed * input_cpu.cores

                self.capsum['normal'][cap] = \
                    total_clock_per_host * self.normalise_cpu(input_cpu) / self.attrib['users_per_host'] * users

            elif cap == BaseConstants.RAM:

                if HyperConstants.RAM_PER_GUEST_UNIT not in self.attrib:
                    self.attrib[HyperConstants.RAM_PER_GUEST_UNIT] = 'GiB'

                ram_per_guest = self.unit_conversion(self.attrib['ram_per_guest'],
                                                       self.attrib['ram_per_guest_unit'], 'GiB')

                self.capsum['normal'][cap] = \
                    ram_per_guest * self.attrib['guests_per_host'] * ex_hosts_per_cluster

            elif cap == BaseConstants.HDD:

                # 70 GB per host is fixed constant
                hdd_per_guest = 70
                hdd_size = self.attrib['guests_per_host'] * hdd_per_guest

                self.capsum['normal'][cap] = hdd_size * self.compression * self.dedupe * ex_hosts_per_cluster

                self.original_size = hdd_size * ex_hosts_per_cluster

            elif cap == BaseConstants.SSD:

                continue

            elif cap == BaseConstants.IOPS:

                total_iops = 1000
                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: total_iops}

            elif cap == BaseConstants.VRAM:

                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp


class EPIC_CLUSTER(object):

    def __init__(self, attrib, herc_conf):

        self.datacentres = deepcopy(attrib['datacentres'])
        self.attrib = deepcopy(attrib)
        del self.attrib['datacentres']
        self.hc = herc_conf
        self.construct_dc(self.hc)

    def construct_dc(self, hc):

        for index in range(len(self.datacentres)):

            self.datacentres[index].update(self.attrib)
            self.datacentres[index] = EPIC_DATACENTRE(self.datacentres[index], hc)


class Veeam(WL):

    def __init__(self, attrib, herc_conf):

        super(Veeam, self).__init__(attrib)

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.original_size = 0
        self.original_iops_sum = None

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.attrib[HyperConstants.VCPUS_PER_CORE] = 1
                self.attrib[HyperConstants.VCPUS_PER_VM] = 10

                self.capsum['normal'][cap] = \
                    self.attrib[HyperConstants.VCPUS_PER_VM] / self.attrib[HyperConstants.VCPUS_PER_CORE]

            elif cap == BaseConstants.RAM:

                self.attrib[HyperConstants.RAM_OPRATIO] = 1
                self.attrib[HyperConstants.RAM_PER_VM] = 256

                self.capsum['normal'][cap] = \
                    self.attrib[HyperConstants.RAM_PER_VM] / self.attrib[HyperConstants.RAM_OPRATIO]

            elif cap == BaseConstants.HDD:

                hdd_size = self.unit_conversion(self.attrib['hdd_size'],
                                                self.attrib['hdd_size_unit'])

                self.capsum['normal'][cap] = hdd_size * self.compression * self.dedupe

                self.original_size = hdd_size

            elif cap == BaseConstants.SSD:

                continue

            elif cap == BaseConstants.IOPS:

                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: 0}

            elif cap == BaseConstants.VRAM:

                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp


class Splunk(WL):

    def __init__(self, attrib, herc_conf):

        super(Splunk, self).__init__(attrib)

        default_compression = 50
        self.compression = (100 - default_compression) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.app_rf = self.attrib.get('app_rf', 2)

        self.original_size = 0
        self.original_iops_sum = None

        self.vm_details = self.attrib['vm_details']

        self.max_vol_ind = self.unit_conversion(attrib['max_vol_ind'],
                                                attrib['max_vol_ind_unit'])

        self.daily_data_rate = self.unit_conversion(attrib['daily_data_ingest'],
                                                    attrib['daily_data_ingest_unit'])

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.attrib[HyperConstants.VCPUS_PER_CORE] = 1

                for _, vm_resources in self.vm_details.items():

                    self.capsum['normal'][cap] += \
                        vm_resources[HyperConstants.NUM_VM] * vm_resources[HyperConstants.VCPUS_PER_VM] / \
                        self.attrib[HyperConstants.VCPUS_PER_CORE]

            elif cap == BaseConstants.RAM:

                for _, vm_resources in self.vm_details.items():

                    if HyperConstants.RAM_PER_VM_UNIT not in vm_resources:
                        vm_resources[HyperConstants.RAM_PER_VM_UNIT] = 'GiB'

                    ram_per_vm = self.unit_conversion(vm_resources[HyperConstants.RAM_PER_VM],
                                                        vm_resources[HyperConstants.RAM_PER_VM_UNIT], 'GiB')

                    self.capsum['normal'][cap] += \
                        vm_resources[HyperConstants.NUM_VM] * ram_per_vm

            elif cap == BaseConstants.HDD:

                if self.attrib['acc_type'] == 'hx+splunk':

                    total_days = self.app_rf * (self.attrib['storage_acc']['hot'] + self.attrib['storage_acc']['cold'] +
                                                self.attrib['storage_acc']['frozen'])

                elif self.attrib['acc_type'] == 'hx+splunk_smartstore':

                    total_days = (self.attrib['storage_acc']['hot'] * 2) + self.attrib['storage_acc']['warm']

                self.capsum['normal'][cap] = self.daily_data_rate * self.compression * self.dedupe * total_days

                self.original_size = self.daily_data_rate * total_days

            elif cap == BaseConstants.SSD:

                continue

            elif cap == BaseConstants.IOPS:

                total_iops = 0

                for _, vm_resources in self.vm_details.items():

                    total_iops += vm_resources[HyperConstants.NUM_VM] * vm_resources[HyperConstants.IOPS_PER_VM]

                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: total_iops}

            elif cap == BaseConstants.VRAM:

                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp


class CONTAINER(WL):

    def __init__(self, attrib, herc_conf):

        super(CONTAINER, self).__init__(attrib)

        self.num_inst = self.attrib[HyperConstants.NUM_CONTAINERS]

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.original_iops_sum = dict()
        self.original_size = 0

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.capsum['normal'][cap] = \
                    (float(self.attrib[HyperConstants.VCPUS_PER_CONTAINER]) /
                     float(self.attrib[HyperConstants.VCPUS_PER_CORE])) * self.normalise_cpu() * self.num_inst

            elif cap == BaseConstants.RAM:

                if HyperConstants.RAM_PER_CONTAINER_UNIT not in self.attrib:
                    self.attrib[HyperConstants.RAM_PER_CONTAINER_UNIT] = 'GiB'

                ram_per_container = self.unit_conversion(self.attrib[HyperConstants.RAM_PER_CONTAINER],
                                                       self.attrib[HyperConstants.RAM_PER_CONTAINER_UNIT], 'GiB')

                self.capsum['normal'][cap] = ram_per_container * self.num_inst

            elif cap == BaseConstants.HDD:

                hdd_size = self.unit_conversion(self.attrib[HyperConstants.HDD_PER_CONTAINER],
                                                self.attrib[HyperConstants.HDD_PER_CONTAINER_UNIT])

                image_size = self.unit_conversion(self.attrib[HyperConstants.BASE_IMG_SIZE],
                                                  self.attrib[HyperConstants.BASE_IMG_SIZE_UNIT])

                self.capsum['normal'][cap] = \
                    self.num_inst * (hdd_size + image_size) * self.compression * self.dedupe

                self.original_size = self.num_inst * (hdd_size + image_size)

            elif cap == BaseConstants.SSD:

                ssd_multiplier = self.attrib[HyperConstants.WORKING_SET_SIZE] / 100.0 * self.dedupe

                self.capsum['normal'][cap] = self.original_size * ssd_multiplier

            elif cap == BaseConstants.IOPS:

                total_iops = self.attrib[HyperConstants.IOPS_PER_CONTAINER] * self.num_inst

                self.original_iops_sum[HyperConstants.CONTAINER] = total_iops

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp

class AIML(WL):

    def __init__(self, attrib, herc_conf):

        super(AIML, self).__init__(attrib)

        self.num_ds = self.attrib[HyperConstants.NUM_DATA_SCIENTISTS]

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.original_iops_sum = None
        self.original_size = 0

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.capsum['normal'][cap] = \
                    (float(self.attrib[HyperConstants.VCPUS_PER_DS]) /
                     float(self.attrib[HyperConstants.VCPUS_PER_CORE])) * self.normalise_cpu() * self.num_ds

            elif cap == BaseConstants.RAM:

                if HyperConstants.RAM_PER_DS_UNIT not in self.attrib:
                    self.attrib[HyperConstants.RAM_PER_DS_UNIT] = 'GiB'

                ram_size = self.unit_conversion(self.attrib[HyperConstants.RAM_PER_DS],
                                                self.attrib[HyperConstants.RAM_PER_DS_UNIT], 'GiB')

                self.capsum['normal'][cap] = ram_size * self.num_ds

            elif cap == BaseConstants.HDD:

                hdd_size = self.unit_conversion(self.attrib[HyperConstants.HDD_PER_DS],
                                                self.attrib[HyperConstants.HDD_PER_DS_UNIT])

                self.capsum['normal'][cap] = \
                    self.num_ds * hdd_size * self.compression * self.dedupe

                self.original_size = self.num_ds * hdd_size

            elif cap == BaseConstants.SSD:

                continue

            elif cap == BaseConstants.IOPS:

                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: 0}

            elif cap == BaseConstants.VRAM:

                if self.attrib['input_type'] == "Video":
                    self.attrib['gpu_type'] = 'V100'
                else:
                    self.attrib['gpu_type'] = 'T4'

                # Here 16GiB of vRAM is allocated to each GPU [either T4 or V100]
                self.capsum['normal'][cap] = self.attrib[HyperConstants.GPU_PER_DS] * self.num_ds * 16.0

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

class WL_ROBO_BACKUP(WL):
    
    def __init__(self, attrib, herc_conf):

        super(WL_ROBO_BACKUP, self).__init__(attrib)

        self.num_inst = self.attrib[HyperConstants.NUM_VM]

        if HyperConstants.VM_SNAPSHOTS not in self.attrib:
            self.attrib[HyperConstants.VM_SNAPSHOTS] = 0

        if self.attrib[HyperConstants.BACKUP_REPLICATION_FACTOR] == 0:
            self.attrib[HyperConstants.VM_REPLICATION_MULT] = 1
        else:
            self.attrib[HyperConstants.VM_REPLICATION_MULT] = self.attrib[HyperConstants.BACKUP_REPLICATION_FACTOR]

        self.compression = (100 - self.attrib[HyperConstants.BACKUP_COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.BACKUP_DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.calc_cap_normal()

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_cap_normal(self):

        for cap in HyperConstants.WL_CAP_LIST:

            if cap == BaseConstants.CPU:

                self.capsum['normal'][cap] = 0

            elif cap == BaseConstants.RAM:

                if HyperConstants.RAM_PER_VM_UNIT not in self.attrib:
                    self.attrib[HyperConstants.RAM_PER_VM_UNIT] = 'GiB'

                ram_per_vm = 0

                self.capsum['normal'][cap] = ram_per_vm * self.num_inst

            elif cap == BaseConstants.HDD:

                hdd_size = self.unit_conversion(self.attrib[HyperConstants.HDD_PER_VM],
                                                self.attrib[HyperConstants.HDD_PER_VM_UNIT])

                image_size = self.unit_conversion(self.attrib[HyperConstants.VM_BASE_IMG_SIZE],
                                                  self.attrib[HyperConstants.VM_BASE_IMG_SIZE_UNIT])

                self.capsum['normal'][cap] = \
                    (self.num_inst * (hdd_size + image_size + (0.02 * hdd_size * \
                        self.attrib[HyperConstants.VM_SNAPSHOTS]))) * self.attrib[HyperConstants.NUM_OF_SITES]*\
                            self.compression * self.dedupe

                self.total_size = \
                    self.num_inst * (hdd_size + image_size + (0.02 * hdd_size * \
                        self.attrib[HyperConstants.VM_SNAPSHOTS]))
                
                self.original_size = self.total_size * self.attrib[HyperConstants.NUM_OF_SITES]

            elif cap == BaseConstants.SSD:

                ssd_multiplier = self.attrib[HyperConstants.VM_WORKING_SET_SIZE] / 100.0 * self.dedupe

                self.capsum['normal'][cap] = (self.original_size * ssd_multiplier) * self.attrib[HyperConstants.NUM_OF_SITES]

            elif cap == BaseConstants.IOPS:

                iops_per_vm = self.attrib[HyperConstants.IOPS_PER_VM]

                total_iops = iops_per_vm * self.num_inst

                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: total_iops}

            elif cap == BaseConstants.VRAM:

                continue

    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp
