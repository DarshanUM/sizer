from .attrib import BaseConstants
from hyperconverged.solver.attrib import HyperConstants
import logging
from math import ceil

logger = logging.getLogger(__name__)


class PartsTable(object):

    """
    A class used to construct list of dictionaries for each component
    self.table will be like {"CPU": {"parts_list": list(), "max_node": 2}
    """
    def __init__(self):
        self.table = {}
        self.base_dict = {}
        self.components = [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.HDD, BaseConstants.SSD,
                           BaseConstants.GPU]
        # max node for each component
        self.node_max = [2, 24, 23, 1, 2]
        for index, component in enumerate(self.components):
            self.base_dict[component] = {}
            self.base_dict[component][BaseConstants.PARTS_LIST] = list()
            self.base_dict[component][BaseConstants.MAX_NODE] = self.node_max[index]
        self.parts_list = list()

    def add_part(self, pid):
        """
        Initialize part dict object, {"E5-2690v4":{}}
        """
        self.table[pid] = dict()

    def is_part_valid(self, pid):
        """
        Return True if part is found, else return False
        """
        if pid in self.table:
            return True
        else:
            return False

    def add_part_attrib(self, pid, key, value):
        """
        Add component details of part
        """
        self.table[pid][key] = value

    def get_part_attrib(self, pid, key):
        """
        Return selected parts selected component
        """
        if key == BaseConstants.AVAILABILITY:
            return self.table[pid].get(key, True)

        return self.table[pid][key]

    def is_part_attrib(self, pid, key):
        """
        Return True if attrib is present
        """
        if key in self.table[pid]:
            return True

        return False

    def update_part_details_to_node(self, part, model, new_node):
        reference_dict = {
            BaseConstants.CPU: {BaseConstants.CLOCK_SPEED: BaseConstants.CLOCK_SPEED,
                                BaseConstants.CORES_PER_CPU: BaseConstants.CAPACITY,
                                HyperConstants.SPECLNT: HyperConstants.SPECLNT,
                                HyperConstants.CPU_DESCR: HyperConstants.DESCRIPTION,
                                HyperConstants.TDP: HyperConstants.TDP,
                                HyperConstants.BOM_CPU_PART: HyperConstants.BOM_NAME,
                                HyperConstants.BOM_CPU_DESCR: HyperConstants.BOM_DESCR},

            BaseConstants.RAM: {BaseConstants.RAM_SIZE: BaseConstants.CAPACITY,
                                HyperConstants.RAM_DESCR: HyperConstants.DESCRIPTION,
                                HyperConstants.BOM_RAM_PART: HyperConstants.BOM_NAME,
                                HyperConstants.BOM_RAM_DESCR: HyperConstants.BOM_DESCR,
                                HyperConstants.BOM_ADD_MEM: HyperConstants.BOM_ADD_MEM},

            BaseConstants.HDD: {BaseConstants.HDD_SIZE: BaseConstants.CAPACITY,
                                HyperConstants.HDD_DESCR: HyperConstants.DESCRIPTION,
                                HyperConstants.HDD_TYPE: HyperConstants.HDD_TYPE,
                                HyperConstants.BOM_HDD_PART: HyperConstants.BOM_NAME,
                                HyperConstants.BOM_HDD_DESCR: HyperConstants.BOM_DESCR},

            BaseConstants.SSD: {HyperConstants.SSD_DESCR: HyperConstants.DESCRIPTION,
                                HyperConstants.SSD_OUTPUT_CAPACITY: HyperConstants.OUTPUT_CAPACITY,
                                BaseConstants.SSD_SIZE: BaseConstants.CAPACITY,
                                HyperConstants.BOM_SSD_PART: HyperConstants.BOM_NAME,
                                HyperConstants.BOM_SSD_DESCR: HyperConstants.BOM_DESCR},

            BaseConstants.VRAM: {HyperConstants.GPU_DESCR: HyperConstants.DESCRIPTION,
                                 HyperConstants.BOM_GPU_PART: HyperConstants.BOM_NAME,
                                 HyperConstants.BOM_GPU_DESCR: HyperConstants.BOM_DESCR,
                                 HyperConstants.GPU_CAP: BaseConstants.CAPACITY}
            }

        for lhs, rhs in reference_dict[part].items():
            new_node.attrib[lhs] = self.get_part_attrib(model, rhs)
        return new_node

    def add_part_list(self, part_type, pid):
        """
        Add component to list object if does not exist
        """
        self.parts_list = self.base_dict[part_type].get(BaseConstants.PARTS_LIST)
        if pid not in self.parts_list:
            self.parts_list.append(pid)

    def flush_part_list(self):

        for component in self.components:
            self.base_dict[component][BaseConstants.PARTS_LIST] = list()

    @staticmethod
    def swap_part_key(part_type):
        """
        During class Initialization key maintained as GPU, SSD
        and while querying it will be VRAM / GPU, IOPS / SSD so to do
        instead of validating mutilpe checks in multiple functions added a
        standalone function
        """
        if part_type == BaseConstants.VRAM:
            return BaseConstants.GPU
        elif part_type == BaseConstants.IOPS:
            return BaseConstants.SSD
        else:
            return part_type

    def get_part_list(self, part_type):
        """
        Return selected component details list
        """
        part_type = self.swap_part_key(part_type)
        if part_type not in self.base_dict:
            raise Exception("Invalid Part Type.")
        else:
            return self.base_dict[part_type][BaseConstants.PARTS_LIST]

    def print_info(self):
        """
        print-logger details
        """
        logger.info("Parts = %d" % len(self.table.keys()))
        for pid in self.table.keys():
            logger.info("pid - %s" % pid)
            for key in self.table[pid]:
                logger.info(key + " = %s" % self.table[pid][key])


class Node(object):

    __slots__ = ["raw_cap", "attrib", "cap", "overhead",
                 "server_hardware_price", "software_price", "storage_ref_dict",
                 "network_price", "vmware_price", "total_capex",
                 "cap_dict", "raw_base_ram", "additional_base_ram",
                 "raw_base_hdd", "additional_base_hdd"]

    BTU_CONV_FACTOR = 0.00029307107
    COST_PER_KWH = 0.11
    HOURS_PER_YEAR = 8760
    MONTHS_PER_YEAR = 12
    RACK_COST_MONTH = 50
    HRS_PER_MONTH = 3.2

    def __init__(self, attrib):
        self.attrib = attrib
        self.raw_cap = dict()  # Holds value of raw capacity of caps {CPU:1}
        self.cap = dict()
        self.overhead = dict()  # Holds Overhead value of caps {CPU:0}
        self.hdd_ssd_overhead = dict()
        self.server_hardware_price = 0
        self.software_price = 0
        self.network_price = 0
        self.vmware_price = 0
        self.total_capex = 0
        self.raw_base_ram = 0
        self.additional_base_ram = 0
        self.raw_base_hdd = 0
        self.additional_base_hdd = 0

        self.storage_ref_dict = {
            BaseConstants.HDD: {
                BaseConstants.SIZE: BaseConstants.HDD_SIZE,
                BaseConstants.SLOTS: BaseConstants.HDD_SLOTS
            },
            BaseConstants.SSD: {
                BaseConstants.SIZE: BaseConstants.SSD_SIZE,
                BaseConstants.SLOTS: BaseConstants.SSD_SLOTS
            }
        }

        self.cap_dict = {BaseConstants.CPU: "calculate_cpu_usable_capacity",
                         BaseConstants.RAM: "calculate_ram_usable_capacity",
                         BaseConstants.HDD: "calculate_storage_usable_capacity",
                         BaseConstants.SSD: "calculate_storage_usable_capacity",
                         BaseConstants.IOPS: "calculate_iops_usable_capacity",
                         BaseConstants.VRAM: "calculate_gpu_usable_capacity"
                         }

    def calculate_cpu_usable_capacity(self, cap):
        """
        calculate CPU usable capacity
        raw = CPU_CNT * CORES_PER_CPU
        usable = raw - overhead value of CPU
        :param cap:
        :return: self
        """
        self.raw_cap[cap] = self.attrib[BaseConstants.CPU_CNT] * self.attrib[BaseConstants.CORES_PER_CPU]
        self.cap[cap] = self.raw_cap[cap] - self.overhead[cap]
        return self

    def calculate_clock_usable_capacity(self, cap):
        """
        raw = CLOCK_SPEED * raw of CPU - 10.8
        :param cap: CLOCK
        :return: self
        """
        self.raw_cap[cap] = self.attrib[BaseConstants.CLOCK_SPEED] * self.raw_cap[BaseConstants.CPU] - 10.8

    def calculate_ram_usable_capacity(self, cap):
        """
        raw = RAM_SLOTS * RAM_SIZE
        usable = raw - overhead value of RAM
        base_ram = RAM_MIN_SLOTS * RAM_SIZE
        additional_ram = ( RAM_SLOTS - RAM_MIN_SLOTS ) * RAM_SIZE
        :param cap: RAM
        :return: self
        """
        self.raw_cap[cap] = self.attrib[BaseConstants.RAM_SLOTS] * self.attrib[BaseConstants.RAM_SIZE]
        self.cap[cap] = self.raw_cap[cap] - self.overhead[cap]
        self.raw_base_ram = self.attrib[BaseConstants.MIN_SLOTS]
        self.additional_base_ram = (self.attrib[BaseConstants.RAM_SLOTS] - self.attrib[BaseConstants.MIN_SLOTS])
        return self

    def calculate_storage_usable_capacity(self, cap):
        """
        usable storage capacity calculation for HDD & SSD
        :param cap: HDD / SSD
        :return: self
        """
        # HDD_SLOTS if HDD else SSD_SLOTS if SSD
        slots_key = self.storage_ref_dict[cap][BaseConstants.SLOTS]
        # HDD_SIZE if HDD else SSD_SIZE if SSD
        size_key = self.storage_ref_dict[cap][BaseConstants.SIZE]
        slots = self.attrib[slots_key]
        size = self.attrib[size_key]
        self.raw_cap[cap] = slots * size
        self.cap[cap] = slots * (size - self.hdd_ssd_overhead.get(size_key, 0))

        if cap == BaseConstants.HDD:
            self.raw_base_hdd = self.attrib[BaseConstants.MIN_HDD_SLOTS]
            self.additional_base_hdd = self.attrib[BaseConstants.HDD_SLOTS] - self.raw_base_hdd
            return self
        else:
            return self

    def calculate_gpu_usable_capacity(self, cap):
        """
        calculate VRAM / IOPS usable capacity
        :param cap: VRAM / IOPS
        :return: self
        """
        self.raw_cap[cap] = self.attrib[cap]
        self.cap[cap] = self.raw_cap[cap] - self.overhead[cap]
        return self

    def calculate_iops_usable_capacity(self, cap):
        """
        calculate VRAM / IOPS usable capacity
        :param cap: VRAM / IOPS
        :return: self
        """
        return self.calculate_gpu_usable_capacity(cap)

    def calculate_overhead(self, cap, hypervisor, storage_protocol):
        """
        calculate overhead values
        :param cap: CPU, RAM, HDD, SSD, IOPS, VRAM
        :param hypervisor: tells which hypervisor is being used -> ESXi or Hyper-V
        :param storage_protocol: tells which hypervisor is being used -> if iSCSI then True or if NFS then False
                                 by default it should be NFS
        :return: {CPU:2.0, RAM: 13 ... etc }
        """

        if BaseConstants.STATIC_OVERHEAD not in self.attrib:
            self.overhead[cap] = 0

        else:
            if cap in self.attrib[BaseConstants.STATIC_OVERHEAD][hypervisor]:
                if cap == BaseConstants.HDD or cap == BaseConstants.SSD:

                    # HDD_SLOTS if HDD else SSD_SLOTS if SSD
                    slots_key = self.storage_ref_dict[cap][BaseConstants.SLOTS]

                    # HDD_SIZE if HDD else SSD_SIZE if SSD
                    size_key = self.storage_ref_dict[cap][BaseConstants.SIZE]

                    round_value = float(self.attrib[BaseConstants.STATIC_OVERHEAD][hypervisor][cap]) / 100

                    self.hdd_ssd_overhead[size_key] = round_value * self.attrib[size_key]
                    self.overhead[cap] = self.attrib[slots_key] * self.hdd_ssd_overhead[size_key]
                else:
                    self.overhead[cap] = self.attrib[BaseConstants.STATIC_OVERHEAD][hypervisor][cap]
            else:
                self.overhead[cap] = 0

        if cap == BaseConstants.CPU and self.overhead[cap] and self.hx_boost_on:
            self.overhead[cap] += 2

        if storage_protocol and cap == BaseConstants.RAM and self.overhead[cap]:
            self.overhead[cap] += 2

        return self

    def calc_cap(self, cap):
        """
        iterates cap dict CPU, RAM, HDD, SSD, IOPS, VRAM and calls
        relevant function using self.cap_dict
        :return: self object
        """
        get_function = getattr(self, self.cap_dict[cap])
        get_function(cap)
        return self

    def calc_capex_opex(self):
        """
        calculate & store capex & base_price
        :return: self
        """
        self.attrib[BaseConstants.CAPEX] = self.attrib[BaseConstants.BASE_PRICE]
        self.attrib[BaseConstants.OPEX_PER_YEAR] = 0
        return self

    def get_capex(self, num_nodes):
        sizer_margin = (1 - BaseConstants.SIZER_GROSS_MARGIN / 100.0)

        self.server_hardware_price = int(ceil(num_nodes * self.attrib[BaseConstants.CAPEX] * sizer_margin))

        self.software_price = int(ceil(self.server_hardware_price * BaseConstants.SIZER_SOFTWARE_MARGIN / 100.0))

        self.network_price = int(ceil(2 * num_nodes * BaseConstants.SIZER_PRICE_PER_PORT))

        self.vmware_price = int(ceil(BaseConstants.SIZER_VM_WARE_PER_3_HOST *
                                     (num_nodes / float(BaseConstants.SIZER_VMWARE_HOST_LICENSE)) +
                                     (2 * BaseConstants.SIZER_VM_WARE_ADD_SUPPORT_PER_YEAR *
                                      (num_nodes / float(BaseConstants.SIZER_VMWARE_HOST_LICENSE)))))

        capex_keys = [BaseConstants.SIZER_SERVER, BaseConstants.SIZER_NETWORK, BaseConstants.SIZER_SOFTWARE,
                      BaseConstants.SIZER_VMWARE, BaseConstants.SIZER_TOTAL_CAPEX]

        capex_list = [self.server_hardware_price, self.network_price,
                      self.software_price, self.vmware_price]

        capex_values = [int(round(float(capex)/1000, 0)) for capex in capex_list]
        self.total_capex = sum(capex_values)
        capex_values.append(self.total_capex)

        capex = dict(zip(capex_keys, capex_values))
        return capex

    def get_tco(self, num_nodes, vdi_user, num_years=1):

        pass
    
    def print_attrib(self):
        for key in self.attrib.keys():
            logger.info(key + " = %s" % self.attrib[key])
        
    def print_cap(self):
        logger.info(self.attrib[BaseConstants.MODEL])

        for cap in BaseConstants.CAP_LIST:
            logger.info(cap + " = %s" % self.cap[cap])

        logger.info("Capex = %d, Opex/Year = %d " % (self.attrib[BaseConstants.CAPEX],
                                                     self.attrib[BaseConstants.OPEX_PER_YEAR]))
