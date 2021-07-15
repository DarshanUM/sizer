import logging
from math import ceil
from .attrib import HyperConstants
from base_sizer.solver.attrib import BaseConstants
from base_sizer.solver.node_sizing import Node

LOGGER = logging.getLogger(__name__)


class HyperConvergedNode(Node):

    """
    Class uses Node class properties and constructs the UI description, 
    summary & bom details etc
    """
    def __init__(self, name, hercules_avail, hx_boost_avail, attrib):

        Node.__init__(self, attrib)

        self.attrib = attrib
        self.name = name

        self.hercules_avail = hercules_avail
        self.hx_boost_avail = hx_boost_avail

        self.hercules_on = None
        self.hx_boost_on = None

        self.power_price = 0
        self.annual_support_os_price = 0
        self.server_hardware_price = 0
        self.software_price = 0
        self.rack_price = 0
        self.facilities_price = 0
        self.maintenances_price = 0
        self.opex_per_year = 0
        self.model_dict = dict()  # For adding dict with LABEL, TAG_NAME ETC
        self.total_opex = 0
        self.tco = 0
        self.vmware_price = 0
        self.total_capex = 0
        self.temp_dict = dict()
        self.calc_dict = dict()
        self.orignal_hdd_slot = dict()
        self.riser = list()

    def calculate_overhead(self, cap, hypervisor, storage_protocol=False):
        """
        calculate overhead values , inherites Node class properties
        :param cap: CPU, RAM, HDD, SSD, IOPS, VRAM
        :param hypervisor determines which hypervisor is being used -> ESXi or Hyper-V
        :param storage_protocol: tells which hypervisor is being used -> if iSCSI then True or if NFS then False
                                 by default it should be NFS
        :return: {CPU:2.0, RAM: 13 ... etc }
        """
        return Node.calculate_overhead(self, cap, hypervisor, storage_protocol)

    def calc_cap(self, cap):
        """
        iterates cap dict CPU, RAM, HDD, SSD, IOPS, VRAM and calls
        relevant function using self.cap_dict , inherited from Node class
        :return: self object
        """
        return Node.calc_cap(self, cap)

    def print_cap(self):
        """
        writes log details of capacities, Node class property
        :return: None
        """
        return Node.print_cap(self)

    def calc_capex_opex(self):
        """
        calculate & store capex & base_price, Node class Property
        :return: self
        """
        return Node.calc_capex_opex(self)

    def get_capex(self, num_nodes):
        """
        calculates, constructs dict of list of server hardware price
        :param num_nodes: integer
        :return: dict -> {LABEL: "Capex", VAL: [{TAG_NAME: value, TAG_VAL: value}]}
        """
        self.server_hardware_price = int(ceil(num_nodes * self.attrib[BaseConstants.CAPEX]))
        self.software_price = int(ceil(self.server_hardware_price * BaseConstants.SIZER_SOFTWARE_MARGIN/100.0))

        self.vmware_price = int(ceil(BaseConstants.SIZER_VM_WARE_PER_3_HOST *
                                     (num_nodes / float(BaseConstants.SIZER_VMWARE_HOST_LICENSE)) +
                                     (2 * BaseConstants.SIZER_VM_WARE_ADD_SUPPORT_PER_YEAR *
                                      (num_nodes / float(BaseConstants.SIZER_VMWARE_HOST_LICENSE)))))

        self.total_capex = int(round(float(self.server_hardware_price), 0))
        tag_list = [(HyperConstants.CAPEX_CPX, self.total_capex), ("Server", self.total_capex)]
        value_list = list()
        for details in tag_list:
            base_tag = dict(TAG_NAME="", TAG_VAL="")
            base_tag[HyperConstants.TAG_NAME] = details[0]
            base_tag[HyperConstants.TAG_VAL] = details[1]
            value_list.append(base_tag)

        capex = {HyperConstants.LABEL: "Capex",
                 HyperConstants.VAL: value_list}

        return capex

    @staticmethod
    def construct_tag_dict(name_list, values_list, high_light_list,
                           tco_value=0, validate=False):
        final_list = list()
        for index, value in enumerate(values_list):
            base_dict_tag = dict(TAG_NAME="", TAG_VAL="", HIGHLIGHT="")
            # general logic for construction of dict
            if not validate:
                base_dict_tag[HyperConstants.TAG_NAME] = name_list[index]
                base_dict_tag[HyperConstants.TAG_VAL] = values_list[index]
                base_dict_tag[HyperConstants.HIGHLIGHT] = high_light_list[index]
                final_list.append(base_dict_tag)
            else:
                # if workload input > 0
                get_value = values_list[index]
                if get_value:
                    base_dict_tag[HyperConstants.TAG_NAME] = name_list[index]
                    base_dict_tag[HyperConstants.TAG_VAL] = round(tco_value/float(get_value), 2)
                    base_dict_tag[HyperConstants.HIGHLIGHT] = high_light_list[index]
                    final_list.append(base_dict_tag)
        return final_list

    def get_opex(self, num_nodes, vdi_user, num_years=1):

        self.annual_support_os_price = \
            int(ceil(((HyperConstants.SIZER_SUPPORT_MARGIN * self.server_hardware_price/100.0) /
                      HyperConstants.SIZER_NUM_YEARS) + (BaseConstants.SIZER_VM_WARE_ADD_SUPPORT_PER_YEAR * num_nodes /
                                                         float(BaseConstants.SIZER_VMWARE_HOST_LICENSE)) +
                     (vdi_user * HyperConstants.SIZER_MS_WIN_VIRTUAL_PRICE)))

        sizer_hrs_total = HyperConstants.SIZER_HOURS_PER_YEAR * num_nodes

        self.power_price = ((self.attrib[HyperConstants.POWER] * 2 * sizer_hrs_total) +
                            (int(self.attrib[HyperConstants.TDP]) * HyperConstants.SIZER_HOURS_PER_YEAR * num_nodes)) *\
                           HyperConstants.SIZER_POWER_COST_PER_KWH/1000

        self.rack_price = num_nodes * self.attrib[HyperConstants.RACK_SPACE] * HyperConstants.SIZER_RACK_PER_MONTH * 12

        self.facilities_price = int(ceil(self.power_price + self.rack_price))

        self.maintenances_price = int(ceil(num_nodes * HyperConstants.SIZER_MAINTAINANCE_HOUR * 12 *
                                           HyperConstants.SIZER_MAINTAINANCE_PRICE))

        value_list = [self.annual_support_os_price, self.maintenances_price, self.facilities_price]

        value_list = [int(round(float(price), 0)) for price in value_list]
        self.total_opex = sum(value_list)
        value_list.insert(0, self.total_capex)

        LOGGER.info("Opex = %d" % self.total_opex)

        name_list = [HyperConstants.OPEX_OPX, "Support", "Maintenance", "Facilities"]
        high_light_list = ["True"] + 3 * ["False"]

        value_list = self.construct_tag_dict(name_list, value_list, high_light_list)
        self.opex_per_year = {HyperConstants.LABEL: "Annual Opex", HyperConstants.VAL: value_list}
        return self.opex_per_year

    def get_tco(self, num_nodes, num_years=1):
        cpx_total = self.total_capex
        opx_total = self.total_opex
        self.tco = int(cpx_total) + int(opx_total) * HyperConstants.SIZER_NUM_YEARS
        LOGGER.info("Total Cost = %d" % self.tco)
        return self.tco

    def get_summary(self, num_nodes, vdi_user, vm_user, db_user, raw_user,
                    robo_user, oracle_user):
        """
        constructs price summary report for each workload
        :param num_nodes: int
        :param vdi_user: int
        :param vm_user: int
        :param db_user: int
        :param raw_user: int
        :param robo_user: int
        :param oracle_user: int
        :return: {LABEL: "Summary", VAL: [{
        """

        price_per_user = list()
        tco_value = self.get_tco(num_nodes, 3)
        name_list = ["Total", "Capex", "Opex for 3 years"]
        value_list = [tco_value, int(self.total_capex),
                      int(self.total_opex * HyperConstants.SIZER_NUM_YEARS)]
        high_light_list = ["True", "False", "False"]

        # get value list for Total, Capex, Opex
        price_per_user.extend(self.construct_tag_dict(name_list, value_list,
                                                      high_light_list))

        # construction of dict for workload inputs

        name_list = ["Price per VDI", "Price per VM", "Price per DB",
                     "Price per RAW", "Price per ROBO", "Price per ORACLE"]
        value_list = [vdi_user, vm_user, db_user, raw_user, robo_user,
                      oracle_user]
        high_light_list = len(name_list) * ["False"]
        price_per_user.extend(self.construct_tag_dict(name_list, value_list, high_light_list, tco_value, True))
        summary = {HyperConstants.LABEL: "Summary", HyperConstants.VAL: price_per_user}
        return summary

    def update_values(self, key_list, obtained_dict):
        """
        updates given dictionary with values of self.attib where keys to
        be updated are passed in key_list
        :param key_list:
        :param obtained_dict:
        :return: self
        """
        for key in key_list:
            obtained_dict[key] = self.attrib.get(key)
        return self

    def construct_string(self, part_type):
        """
        Function used to construct description of each parts
        :param part_type: CPU, RAM, HDD, SSD, VRAM
        :return: base_string
        """
        if part_type == BaseConstants.CPU:

            base_string = str(self.model_dict[BaseConstants.CPU_CNT]) + "x" + self.attrib[HyperConstants.CPU_DESCR]

        elif part_type == BaseConstants.RAM:

            if '[CUSTOM]' in self.model_dict[HyperConstants.RAM_PART] or \
                    '[CUSTOM_6SLOT]' in self.model_dict[HyperConstants.RAM_PART]:

                base_string = \
                    str(self.model_dict[HyperConstants.TOTAL_RAM]) + ' ' + self.attrib[HyperConstants.RAM_DESCR]
                return base_string

            base_string = str(self.model_dict[HyperConstants.TOTAL_RAM]) + ' [' + \
                          str(self.model_dict[BaseConstants.RAM_SLOTS]) + 'x' + \
                          str(self.model_dict[BaseConstants.RAM_SIZE]) + ']' + " GiB "

            if self.additional_base_ram:
                sub_string = (self.attrib[HyperConstants.RAM_DESCR],
                              self.raw_base_ram, "Base Sticks, ",
                              self.additional_base_ram, "Add-On")
                base_string += "%s (%s %s %s %s)" % sub_string
            else:
                base_string += self.attrib[HyperConstants.RAM_DESCR]

        elif part_type == BaseConstants.HDD:

            base_string = str(self.model_dict[BaseConstants.HDD_SLOTS]) + "x" + \
                          str(self.model_dict[BaseConstants.HDD_SIZE]) + str(self.model_dict["HDD_GB_TB"]) + ', ' + \
                          ('2.5"', '3.5"')[self.attrib[HyperConstants.DISK_CAGE] == 'LFF']

            for disk_type in ["Optane", "NVMe"]:
                if disk_type in self.attrib[HyperConstants.BOM_HDD_DESCR]:
                    base_string += ' %s' % disk_type
                    break
            else:
                base_string += ' %s' % self.attrib[HyperConstants.HDD_TYPE]

            for encryption in ["FIPS", "SED"]:
                if encryption in self.attrib[HyperConstants.BOM_HDD_DESCR]:
                    base_string += ' (%s)' % encryption
                    break

            if self.additional_base_hdd:

                sub_string = (self.raw_base_hdd, "Base ", "+ ", self.additional_base_hdd,
                              "Add-On")

                base_string += " (%s %s %s %s %s)" % sub_string

        elif part_type == BaseConstants.SSD:

            base_string = str(self.model_dict[BaseConstants.SSD_SLOTS]) + "x" + \
                          str(self.model_dict[BaseConstants.SSD_SIZE]) + self.model_dict["SSD_GB_TB"]

            for cache_type in ["Optane", "NVMe", "SATA", "SAS"]:
                if cache_type in self.attrib[HyperConstants.BOM_SSD_DESCR]:
                    base_string += " %s" % cache_type
                    break

            for encryption in ["FIPS", "SED"]:
                if encryption in self.attrib[HyperConstants.BOM_SSD_DESCR]:
                    base_string += ' (%s)' % encryption
                    break

        else:

            base_string = str(self.attrib[HyperConstants.GPU_SLOTS]) + " slot for " + \
                          self.attrib[HyperConstants.GPU_DESCR]
        return base_string

    def get_model_details(self, gpu_used):
        """
        construct and return node model details
        :param gpu_used: True / False
        :return: self.model_dict
        """
        base_model_keys = [BaseConstants.SUBTYPE, BaseConstants.MODEL, BaseConstants.BASE_PRICE,
                           HyperConstants.RACK_SPACE, HyperConstants.POWER, BaseConstants.NODE_BASE_PRICE,
                           BaseConstants.CPU_CNT, BaseConstants.CORES_PER_CPU, BaseConstants.RAM_SLOTS,
                           BaseConstants.RAM_SIZE, BaseConstants.HDD_SLOTS, HyperConstants.DISK_CAGE,
                           BaseConstants.CLOCK_SPEED, HyperConstants.HDD_AVAILABILITY, HyperConstants.SSD_AVAILABILITY,
                           HyperConstants.CPU_AVAILABILITY, HyperConstants.SPECLNT, HyperConstants.GPU_AVAILABILITY,
                           HyperConstants.RAM_AVAILABILITY, HyperConstants.CORES_PER_CPU_PRESPECLNT,
                           BaseConstants.BASE_CPU_CLOCK]

        self.update_values(base_model_keys, self.model_dict)

        sizing_calculation_keys = [HyperConstants.RAW_CORES_TOTAL, HyperConstants.RAW_CORES_ADJSPECLNT,
                                   HyperConstants.CORES_TOTAL_POSTOVERHEAD, HyperConstants.RAW_VRAM_TOTAL,
                                   HyperConstants.CORES_TOTAL_POSTTHRESHOLD, HyperConstants.RAW_RAM_TOTAL,
                                   HyperConstants.RAM_TOTAL_POSTOVERHEAD, HyperConstants.HDD_OPRATIO,
                                   HyperConstants.RAM_TOTAL_POSTTHRESHOLD, HyperConstants.RAW_HDD_TOTAL,
                                   HyperConstants.HDD_TOTAL_POSTRF, HyperConstants.CPU_OPRATIO,
                                   HyperConstants.HDD_TOTAL_POSTOVERHEAD, HyperConstants.HDD_TOTAL_POSTTHRESHOLD,
                                   HyperConstants.RAW_IOPS_TOTAL, HyperConstants.RAM_OPRATIO,
                                   HyperConstants.IOPS_TOTAL_POSTIOPSCONV, HyperConstants.NODE_OVERHEAD,
                                   HyperConstants.THRESHOLD_KEY, HyperConstants.HIGHEST_RF,
                                   HyperConstants.SCALING_FACTOR]

        for key_details in sizing_calculation_keys:
            if key_details in self.attrib:
                self.calc_dict[key_details] = self.attrib[key_details]

        if BaseConstants.BUNDLE in self.attrib[BaseConstants.NODE_TYPE]:
            self.model_dict[BaseConstants.NODE_TYPE] = "Bundle"
        else:
            self.model_dict[BaseConstants.NODE_TYPE] = "CTO"

        self.model_dict[BaseConstants.OPEX_PER_YEAR] = self.total_opex
        temp_dict = dict()

        for part in HyperConstants.MODEL_DETAILS_LIST:
            if part == BaseConstants.CPU:
                self.model_dict[HyperConstants.CPU_CORES] = self.attrib[BaseConstants.CPU_CNT] * \
                                             self.attrib[BaseConstants.CORES_PER_CPU]

                if HyperConstants.CPU_PART in self.attrib and self.attrib[BaseConstants.CPU_CNT]:
                    self.update_values([HyperConstants.CPU_PART, HyperConstants.CPU_PRICE], self.model_dict)
                    temp_dict[part] = self.construct_string(part)

            elif part == BaseConstants.RAM:
                self.model_dict[HyperConstants.TOTAL_RAM] = self.attrib[BaseConstants.RAM_SLOTS] * \
                                                            self.attrib[BaseConstants.RAM_SIZE]

                if HyperConstants.RAM_PART in self.attrib and self.attrib[BaseConstants.RAM_SLOTS]:
                    self.update_values([HyperConstants.RAM_PART, HyperConstants.RAM_PRICE], self.model_dict)
                    temp_dict[part] = self.construct_string(part)

            elif part == BaseConstants.HDD:

                if self.attrib[BaseConstants.HDD_SIZE] >= 1000:
                    self.model_dict[BaseConstants.HDD_SIZE] = self.attrib[BaseConstants.HDD_SIZE] / 1000.0
                    unit = 'TB'
                else:
                    self.model_dict[BaseConstants.HDD_SIZE] = self.attrib[BaseConstants.HDD_SIZE]
                    unit = 'GB'

                if HyperConstants.HDD_PART in self.attrib and self.attrib[BaseConstants.HDD_SLOTS]:

                    self.update_values([HyperConstants.HDD_PART, HyperConstants.HDD_PRICE], self.model_dict)
                    self.model_dict["HDD_GB_TB"] = unit
                    temp_dict[part] = self.construct_string(part)

            elif part == BaseConstants.VRAM:
                self.update_values([HyperConstants.BOM_GPU_PART, HyperConstants.GPU_DESCR, HyperConstants.GPU_SLOTS,
                                    BaseConstants.VRAM], self.model_dict)

                if gpu_used:
                    if not self.attrib[HyperConstants.GPU_SLOTS]:
                        temp_dict[part] = self.construct_string(part)

            elif part == BaseConstants.SSD and HyperConstants.SSD_PART in self.attrib:

                if self.attrib[HyperConstants.SSD_OUTPUT_CAPACITY] >= 1000:
                    self.model_dict[BaseConstants.SSD_SIZE] = self.attrib[HyperConstants.SSD_OUTPUT_CAPACITY] / 1000.0
                    unit = "TB"
                else:
                    self.model_dict[BaseConstants.SSD_SIZE] = self.attrib[HyperConstants.SSD_OUTPUT_CAPACITY]
                    unit = "GB"

                if self.attrib[BaseConstants.SSD_SLOTS]:
                    self.update_values([HyperConstants.SSD_PART, HyperConstants.SSD_PRICE, BaseConstants.SSD_SLOTS],
                                       self.model_dict)
                    self.model_dict["SSD_GB_TB"] = unit
                    temp_dict[part] = self.construct_string(part)

            else:
                pass

        self.model_dict[BaseConstants.NODE_DESCR] = temp_dict
        self.model_dict[HyperConstants.SIZING_CALCULATION] = self.calc_dict
        return self.model_dict

    def get_bom_details(self):
        """
        construct bom json
        :return: self.temp_dict
        """
        for key_details in [HyperConstants.POWER, HyperConstants.BOM_NAME, HyperConstants.BOM_PACKAGE_NAME,
                            HyperConstants.BOM_FI_PACKAGE_NAME, HyperConstants.FI_OPTIONS,
                            HyperConstants.M5_DISK_PACKAGE, HyperConstants.BOM_CHASSIS_NAME,
                            HyperConstants.BOM_CHASSIS_COUNT, HyperConstants.BOM_RAID_NAME,
                            HyperConstants.BOM_SYSTEM_DRIVE, HyperConstants.BOM_BOOT_DRIVE, 'riser_options']:

            if key_details in self.attrib:
                self.temp_dict[key_details] = self.attrib[key_details]

        for part in HyperConstants.MODEL_DETAILS_LIST:

            if part == BaseConstants.CPU and HyperConstants.CPU_PART in self.attrib and \
                    self.attrib[BaseConstants.CPU_CNT]:

                self.update_values([BaseConstants.CPU_CNT, HyperConstants.BOM_CPU_DESCR, HyperConstants.BOM_CPU_PART],
                                   self.temp_dict)

            elif part == BaseConstants.RAM and HyperConstants.RAM_PART in self.attrib and \
                    self.attrib[BaseConstants.RAM_SLOTS]:

                self.temp_dict[HyperConstants.TOTAL_RAM] = self.attrib[BaseConstants.RAM_SLOTS] * \
                                                           self.attrib[BaseConstants.RAM_SIZE]

                self.temp_dict[HyperConstants.BOM_ADD_MEM_SLOTS] = (self.attrib[BaseConstants.RAM_SLOTS] -
                                                     self.attrib[BaseConstants.MIN_SLOTS])

                self.temp_dict[HyperConstants.BOM_MIN_SLOTS] = self.attrib[BaseConstants.MIN_SLOTS]

                self.update_values([BaseConstants.RAM_SLOTS, HyperConstants.BOM_RAM_PART, HyperConstants.BOM_RAM_DESCR,
                                    HyperConstants.BOM_ADD_MEM, HyperConstants.BOM_MIN_SLOTS], self.temp_dict)

            elif part == BaseConstants.HDD and HyperConstants.HDD_PART in self.attrib and \
                    self.attrib[BaseConstants.HDD_SLOTS]:

                self.update_values([BaseConstants.HDD_SLOTS, HyperConstants.BOM_HDD_DESCR, HyperConstants.BOM_HDD_PART],
                                   self.temp_dict)

            elif part == BaseConstants.SSD and HyperConstants.SSD_PART in self.attrib and \
                    self.attrib[BaseConstants.SSD_SLOTS]:

                self.update_values([BaseConstants.SSD_SLOTS, HyperConstants.BOM_SSD_DESCR,
                                    HyperConstants.BOM_SSD_PART], self.temp_dict)

                if self.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE,
                                                          HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE,
                                                          HyperConstants.ROBO_240, HyperConstants.ROBO_AF_240]:

                    if '40G-10G' in self.attrib[HyperConstants.SSD_PART]:
                        self.temp_dict[HyperConstants.BOM_10G_PART] = 'HX-E-TOPO1'
                        self.temp_dict[HyperConstants.BOM_10G_PART_COUNT] = 1

                    elif 'DUAL' in self.attrib[HyperConstants.SSD_PART]:
                        self.temp_dict[HyperConstants.BOM_DUAL_SWITCH_PART] = 'HX-E-TOPO2'
                        self.temp_dict[HyperConstants.BOM_DUAL_SWITCH_PART_COUNT] = 1

                    else:
                        self.temp_dict[HyperConstants.BOM_DUAL_SWITCH_PART] = 'HX-E-TOPO3'
                        self.temp_dict[HyperConstants.BOM_DUAL_SWITCH_PART_COUNT] = 1

                if self.hercules_on:
                    self.temp_dict[HyperConstants.BOM_HERCULES_PART] = 'HX-PCIE-OFFLOAD-1'
                    self.temp_dict[HyperConstants.BOM_HERCULES_COUNT] = 1

            elif part == BaseConstants.VRAM:
                if self.attrib[HyperConstants.GPU_SLOTS]:
                    self.update_values([HyperConstants.GPU_SLOTS, HyperConstants.BOM_GPU_DESCR,
                                        HyperConstants.BOM_GPU_PART], self.temp_dict)

        if self.riser:
            self.temp_dict['riser_bom_name'] = self.riser
            if self.orignal_hdd_slot:
                self.temp_dict['original_hdd_slot'] = self.orignal_hdd_slot

        return self.temp_dict

    def get_mod_lan(self):

        if self.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE,
                                                  HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE, 
                                                  HyperConstants.ROBO_240, HyperConstants.ROBO_AF_240]:

            ssd_part = self.attrib[HyperConstants.SSD_PART]

            for search, mod_lan in [('40G-10G', '10G/40G'), ('40G', '40G'), ('10G', '10G'), ('DUAL', 'Dual Switch')]:
                if search in ssd_part:
                    break
            else:
                mod_lan = 'Single Switch'

            mod_lan = mod_lan + ' modular LAN'
            return mod_lan

        else:

            return None
