from math import ceil
from collections import defaultdict

from django.core.exceptions import ObjectDoesNotExist

from hyperconverged.solver.sizing import HyperConvergedSizer
from hyperconverged.models import Node, Part, SpecIntData, IopsConvFactor,Thresholds
from hyperconverged.solver.node_sizing import HyperConvergedNode
from hyperconverged.solver.utilization_class import UtilizationGenerator

from base_sizer.solver.attrib import BaseConstants
from .attrib import HyperConstants
from copy import deepcopy

from hyperconverged.strings import SUPPORTED_CLUSTERS, ROBO_WL, AF_WL, HYPER_WL, VEEAM_WL
from hyperconverged.exception import RXException
from hyperconverged.serializer.CalculatorSerializer import ReverseSizerCalculatorSerializer

Threshold = dict()
Threshold["All Flash"] = dict()
Threshold["Hybrid"] = dict()
Threshold["All Flash"][0] = {"CPU": 80.0,
                             "RAM": 92.0,
                             "DISK": 65.0}
Threshold["All Flash"][1] = {"CPU": 90.0,
                             "RAM": 92.0,
                             "DISK": 70.0}
Threshold["All Flash"][2] = {"CPU": 93.0,
                             "RAM": 93.0,
                             "DISK": 75.0}
Threshold["All Flash"][3] = {"CPU": 100,
                             "RAM": 100,
                             "DISK": 75}

Threshold["Hybrid"][0] = {"CPU": 80.0,
                          "RAM": 92.0,
                          "DISK": 65.0}
Threshold["Hybrid"][1] = {"CPU": 90.0,
                          "RAM": 92.0,
                          "DISK": 65.0}
Threshold["Hybrid"][2] = {"CPU": 93.0,
                          "RAM": 93.0,
                          "DISK": 70.0}
Threshold["Hybrid"][3] = {"CPU": 100,
                          "RAM": 100,
                          "DISK": 70}

IOPS_DESC = defaultdict(str)
IOPS_DESC['VDI'] = "Workload Model: 20K IO Block Size, 100% Write"
IOPS_DESC['OLAP'] = "Workload Model: 64K IO Block Size, 100% Write"
IOPS_DESC['VDI_INFRA'] = "Workload Model: 20K IO Block Size, 100% Write"
IOPS_DESC['VSI'] = "Workload Model: 8K IO Block Size, 70/30 Read/Write"
IOPS_DESC['DB'] = "Workload Model: 8K IO Block Size, 70/30 Read/Write"
IOPS_DESC['ORACLE'] = "Workload Model: 8K IO Block Size, 70/30 Read/Write"
IOPS_DESC['ROBO'] = "Workload Model: 8K IO Block Size, 70/30 Read/Write"
IOPS_DESC['EXCHANGE'] = "Workload Model: Mixture of 32K IO Block Size 60/40 Read/Write, " \
                        "\n16K IO Block Size 100% Write and 8K IO Block Size 70/30 Read/Write"

IOPS_DESC['EPIC'] = "Workload Model: 20K IO Block Size, 100% Write"
IOPS_DESC['VEEAM'] = "Performance was not modelled for this workload"
IOPS_DESC['SPLUNK'] = "Workload Model: 8K IO Block Size, 70/30 Read/Write"
IOPS_DESC['RDSH'] = "Workload Model: 20K IO Block Size, 100% Write"
IOPS_DESC['CONTAINER'] = "Workload Model: 8K IO Block Size, 70/30 Read/Write"
IOPS_DESC['AIML'] = "Performance was not modelled for this workload"
IOPS_DESC['RAW'] = "Performance was not modelled for this workload"
IOPS_DESC['RAW_FILE'] = "Performance was not modelled for this workload"
IOPS_DESC['AWR_FILE'] = "Workload Model: 8K IO Block Size, 70/30 Read/Write"

class ReverseSizer(object):

    def __init__(self, data):

        self.node_overheads = dict()
        self.node = None
        self.response = dict()
        self.threshold_info = { "CPU": 80.0,"RAM": 92.0, "DISK": 65.0 }
        self.data = data

        # node properties
        self.num_nodes = 0
        self.cpu = ''
        self.num_compute_nodes = 0
        self.ram_cap = 0
        self.disks_per_node = 0
        self.disk_capacity = 0
        self.node_type = ''
        self.workload_type = ''
        self.empty_fixed_wl_type = 'VSI' 
        self.num_nodes_ft = 0
        self.hypervisor = None
        self.hercules_on = None
        self.hx_boost_on = None

        self.hercules_comp = 1.0

        # scenario settings
        self.compression = 0
        self.dedupe = 0
        self.ft = 0
        self.rf = 0
        self.threshold_num = 1
        self.initialise_setup()
        self.calculate_overhead()
        
        # 5120 [Sky] 
        self.ref_iop_cpu_specint =1.132723

    def initialise_setup(self):

        node_properties = self.data['node_properties']
        scenario_settings = self.data['scenario_settings']
        self.node = Node.objects.get(name=node_properties["node"], status=True)

        if "AF" in self.node.name:
            self.node_type = "All Flash"
        else:
            self.node_type = "Hybrid"

        if len(scenario_settings['workloads_type']):
            self.workload_type = scenario_settings['workloads_type'][0]
        
        self.num_nodes = node_properties["no_of_nodes"]
        self.num_compute_nodes = node_properties["no_of_computes"]

        self.ram_cap = node_properties["ram"][1] * sum(node_properties["ram"][2])
        self.cpu = node_properties["cpu"]

        self.disks_per_node = node_properties["disks_per_node"]
        self.disk_capacity = node_properties["disk_capacity"][0]

        disk_part = Part.objects.filter(name=node_properties["disk_capacity"][1])
        if disk_part:
            if HyperConstants.CUSTOM in disk_part[0].part_json:
                overhead = disk_part[0].part_json[HyperConstants.CUSTOM][BaseConstants.STATIC_OVERHEAD]
                self.node.node_json[BaseConstants.STATIC_OVERHEAD] = deepcopy(overhead)

        self.compression = float(100 - scenario_settings["compression_factor"]) / 100
        self.dedupe = float(100 - scenario_settings["dedupe_factor"]) / 100

        self.ft = scenario_settings["ft"]
        self.rf = scenario_settings["rf"]
        self.threshold_num = scenario_settings["threshold"]
        self.hypervisor = scenario_settings["hypervisor"]

        self.hercules_on = scenario_settings["hercules_conf"] == HyperConstants.FORCED
        self.hx_boost_on = scenario_settings["hx_boost_conf"] == HyperConstants.FORCED

        if self.hercules_on:
            self.hercules_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        self.num_nodes_ft = self.num_nodes - self.ft

    def calculate_overhead(self):

        for cap in ["CPU", "HDD", "RAM"]:

            if BaseConstants.STATIC_OVERHEAD not in self.node.node_json:
                self.node_overheads[cap] = 0
            else:
                self.node_overheads[cap] = \
                    float(self.node.node_json[BaseConstants.STATIC_OVERHEAD][self.hypervisor][cap])

                if cap == "CPU" and self.hx_boost_on:
                    self.node_overheads[cap] += 2

    def check_validity(self):

        try:
            self.node = Node.objects.get(name=self.data["node"], status=True)
        except ObjectDoesNotExist:
            error_msg = "Node does not exist in DB"
            return False, error_msg
        return True, None

    def get_overhead(self, cap):

        if cap == BaseConstants.HDD:
            return (100 - self.node_overheads[BaseConstants.HDD]) / 100
        elif cap == BaseConstants.CPU:
            return self.node_overheads[BaseConstants.CPU]
        elif cap == BaseConstants.RAM:
            return self.node_overheads[BaseConstants.RAM]

    def get_threshold(self, cap):

        if cap == BaseConstants.HDD:
            if "AF" in self.node.name:
                cap = HyperConstants.LFF_HDD
            elif self.node.name.endswith('L'):
                cap = HyperConstants.ALL_FLASH_HDD

        if self.workload_type:
            threshold_data = Thresholds.objects.get(threshold_category=self.threshold_num, threshold_key = cap, workload_type = self.workload_type)
        else:
            threshold_data = Thresholds.objects.get(threshold_category=self.threshold_num, threshold_key = cap, workload_type = self.empty_fixed_wl_type)
        # return Threshold[self.node_type][self.threshold_num][cap] / 100
        if cap == BaseConstants.HDD or cap == HyperConstants.LFF_HDD or cap == HyperConstants.ALL_FLASH_HDD:
            self.threshold_info["DISK"] = threshold_data.threshold_value
        else:
            self.threshold_info[cap] = threshold_data.threshold_value

        return threshold_data.threshold_value / 100

    def core_calculations(self):

        effective_node_count = self.num_nodes_ft + self.num_compute_nodes

        hdd_threshold_value = self.get_threshold(BaseConstants.HDD)
        cpu_threshold_value = self.get_threshold(BaseConstants.CPU)
        ram_threshold_value = self.get_threshold(BaseConstants.RAM)
        
        #Threshold[self.node_type][self.threshold_num]
        self.response['thresholds'] = self.threshold_info 

        # the below calculation is for disk capacity
        disk_cap_per_node = self.disks_per_node * self.disk_capacity
        disk_usable_cap = self.get_overhead(BaseConstants.HDD) * disk_cap_per_node / self.rf

        self.response['disk_capacity'] = dict()
        self.response['disk_capacity']['usable'] = disk_usable_cap * self.num_nodes

        effective_disk_per_node = disk_usable_cap / (self.compression * self.dedupe * self.hercules_comp)
        self.response['disk_capacity']['effective'] = effective_disk_per_node * self.num_nodes

        
        disk_available_cap = effective_disk_per_node * hdd_threshold_value
        self.response['disk_capacity']['available'] = disk_available_cap * self.num_nodes

        # the below calculation is for CPU cores
        cores = self.cpu[1] * effective_node_count * self.node.node_json[BaseConstants.CPU_CNT][0]
        total_cpu_overhead = self.get_overhead(BaseConstants.CPU) * self.num_nodes_ft
        speclnt = self.cpu[4]
        cores_pre_spec = (cores - total_cpu_overhead) * cpu_threshold_value
        cores_post_spec = ((cores * speclnt) - total_cpu_overhead) * cpu_threshold_value

        self.response['cores'] = dict()
        self.response['cores']['pre_spec'] = int(ceil(cores_pre_spec))
        self.response['cores']['post_spec'] = int(ceil(cores_post_spec))

        self.response['cores']['total_cores'] = self.cpu[1] * self.node.node_json[BaseConstants.CPU_CNT][0]
        self.response['cores']['speclnt'] = self.cpu[4]

        self.response['overhead'] = dict()
        self.response['overhead'][BaseConstants.CPU] = self.get_overhead(BaseConstants.CPU)
        self.response['overhead'][BaseConstants.RAM] = self.get_overhead(BaseConstants.RAM)
        self.response['overhead'][BaseConstants.HDD] = self.get_overhead(BaseConstants.HDD)

        self.response['reserve'] = dict()
        self.response['reserve'][BaseConstants.CPU] = cpu_threshold_value
        self.response['reserve'][BaseConstants.RAM] = ram_threshold_value
        self.response['reserve'][BaseConstants.HDD] = hdd_threshold_value

        # below calculation is for RAM
        ram = self.ram_cap * effective_node_count
        total_ram_overhead = self.get_overhead(BaseConstants.RAM) * self.num_nodes_ft
        self.response['total_ram'] = "{0:.1f}".format(ram)
        self.response['ram'] = "{0:.1f}".format((ram - total_ram_overhead) * ram_threshold_value)

    def calculation_gb_tb(self):

        storage_cap_keys = self.response['disk_capacity'].keys()
        for key in list(storage_cap_keys):

            if self.response['disk_capacity'][key] >= 1000:
                division_factor = 1000.0
                self.response['disk_capacity'][key + "_unit"] = "TB"
                unit_mul_factor = HyperConstants.TB_TO_TIB_CONVERSION
                self.response['disk_capacity'][key + "_binaryunit"] = "TiB"
            else:
                division_factor = 1
                self.response['disk_capacity'][key + "_unit"] = "GB"
                unit_mul_factor = HyperConstants.GB_TO_GIB_CONVERSION
                self.response['disk_capacity'][key + "_binaryunit"] = "GiB"

            self.response['disk_capacity'][key + "_binarybyte"] = \
                "{0:.1f}".format(self.response['disk_capacity'][key] / division_factor * unit_mul_factor)

            self.response['disk_capacity'][key] = \
                "{0:.1f}".format(self.response['disk_capacity'][key] / division_factor)

    def cal_iops_available(self):
        
        try:
            node_properties = self.data['node_properties']
            ssd_name = node_properties['cache_size'][1]
            # TODO remove the hard coded value and uncomment the below line
            wl_type = node_properties['io_block_size']
            hyperv = 0 if self.hypervisor == "esxi" else 1
            rf_str = 'RF2' if self.rf == 2 else 'RF3'
            current_cpu_specint = node_properties['cpu'][4]
            iops_data = IopsConvFactor.objects.get(hypervisor = hyperv, 
                                                        threshold = self.threshold_num, replication_factor = rf_str, 
                                                        workload_type = wl_type, part_name = ssd_name )
            iops_conv_factor = iops_data.iops_conv_factor
            
            
            threshold_data = Thresholds.objects.get(threshold_category=self.threshold_num, threshold_key = 'IOPS', workload_type = wl_type )
            threshold = (threshold_data.threshold_value/100.0)
            
            pcnt_increase = 0
            if self.hercules_on:
                pcnt_increase += HyperConstants.HERCULES_IOPS[wl_type]
            if self.hx_boost_on:
                pcnt_increase += HyperConstants.HX_BOOST_IOPS[wl_type]
            
            iops_conv_factor *= (1 + pcnt_increase / 100.0)
            
            iops_conv_factor *= threshold
            
            iops_conv_factor *= current_cpu_specint / self.ref_iop_cpu_specint
            
            total_iops = int(iops_conv_factor/ 1000.0) * self.num_nodes_ft 
            
            self.response['iops'] = dict()
            self.response['iops']['total_iops'] = str(total_iops) + 'K'
            self.response['iops']['iops_desc'] = IOPS_DESC[wl_type]
        except:
            #do nothing
            pass
        
    def get_usable_resources(self):

        self.core_calculations()
        self.calculation_gb_tb()
        self.cal_iops_available()
        return self.response


class WorkloadAdder(object):

    def __init__(self, settings_json, workload_list):

        """
        this class is used to create a json that can be sent to hyperconverged' s sizing function
        :param workload_list: used to send workloads
        :param settings_json:used to send settings such as heterogenous, node_properties etc
        """


        self.input_wls = set()

        for wl in workload_list:
            self.input_wls.add(wl[BaseConstants.WL_TYPE])

        self.solver_node = dict()
        self.solver_settings = dict()
        settings_json = settings_json[0]
        self.node_properties = settings_json['node_properties']
        self.scenario_settings = settings_json
        self.base_cpu = SpecIntData.objects.get(is_base_model=True)
        self.current_cpu = None

        hxnode = self.validate_node(self.node_properties['node'],
                                    self.node_properties['cache_size'][1],
                                    self.node_properties['disk_capacity'][1])

        self.hx_node = \
            HyperConvergedNode(self.node_properties['node'],
                               self.scenario_settings[HyperConstants.HERCULES_CONF] == HyperConstants.FORCED,
                               self.scenario_settings[HyperConstants.HX_BOOST_CONF] == HyperConstants.FORCED,
                               hxnode)

        self.hx_node.hercules_on = self.scenario_settings[HyperConstants.HERCULES_CONF] == HyperConstants.FORCED
        self.hx_node.hx_boost_on = self.scenario_settings[HyperConstants.HX_BOOST_CONF] == HyperConstants.FORCED

        if self.node_properties['no_of_computes']:
            computenode = self.validate_node(self.node_properties['compute_node'])
            self.compute_node = HyperConvergedNode(self.node_properties['compute_node'], False, False, computenode)

            intersect_slots = list(filter(lambda x: x in self.compute_node.attrib["cpu_socket_count"],
                                     self.hx_node.attrib["cpu_socket_count"]))

            if not intersect_slots:
                intersect_slots = [2]

            self.hx_node.attrib["cpu_socket_count"] = intersect_slots
            self.compute_node.attrib["cpu_socket_count"] = intersect_slots

        self.accessories = list()

        self.validate_workloads(workload_list)
        self.check_cluster_type(workload_list)
        self.check_for_gpu(workload_list)

        self.scenario_settings['rf'], self.scenario_settings['ft'] = self.get_rf_ft(workload_list)
        self.validate_cluster()

        self.rf_string = 'RF2' if self.scenario_settings['rf'] == 2 else 'RF3'
        self.configure_settings()

        parts_json = list()
        for part in Part.objects.all():
            part.part_json['name'] = part.name
            parts_json.append(part.part_json)

        self.solver_object = HyperConvergedSizer(parts_json, None, workload_list, self.solver_settings,
                                                 'reverse_sizing_scen')
        self.validate_large_vm_ram_limit(self.node_properties)
        self.solver_object.Fault_Tolerance = self.scenario_settings['ft']
        self.solver_object.RF_String = self.rf_string
        self.parts_table = self.solver_object.parts_table
        self.iops_conv_fac = self.solver_object.iops_conv_fac
        self.get_scaled_conv_fac = self.solver_object.get_scaled_conv_fac
        self.response = list()

    @staticmethod
    def check_cluster_type(workloads):

        replicated_wl = list()
        stretch_wl = list()
        epic_wl = list()

        for wl in workloads:

            if wl.get('remote_replication_enabled', False):
                replicated_wl.append(str(wl['wl_name']))

            if wl[HyperConstants.CLUSTER_TYPE] == HyperConstants.STRETCH:
                stretch_wl.append(str(wl['wl_name']))

            if wl[BaseConstants.WL_TYPE] == HyperConstants.EPIC:
                epic_wl.append(str(wl['wl_name']))

        if replicated_wl:
            raise RXException('replication workloads' + '|' + str(replicated_wl))
        elif stretch_wl:
            raise RXException('stretched workloads' + '|' + str(stretch_wl))
        elif epic_wl:
            raise RXException('epic workloads' + '|' + str(epic_wl))

    @staticmethod
    def check_for_gpu(workloads):
        gpu_wl = list()
        for wl in workloads:
            if wl.get('gpu_users', 0):
                gpu_wl.append(wl['wl_name'])
        if gpu_wl:
            raise RXException('gpu wl' + '|' + str(gpu_wl))

    @staticmethod
    def validate_node(nodename, cache=None, disk=None):

        try:
            node_object = Node.objects.get(name=nodename)
            node = node_object.node_json
        except Node.DoesNotExist:
            raise RXException('renamed node' + ' | ' + str(nodename))

        if not node_object.status:
            raise RXException('deprecated ' + ' | ' + str(nodename))

        if cache:
            try:
                Part.objects.get(name=cache)
            except Part.DoesNotExist:
                raise RXException('renamed part' + ' | ')

        if disk:
            try:
                Part.objects.get(name=disk)
            except Part.DoesNotExist:
                raise RXException('renamed part' + ' | ')

        return node

    def validate_cluster(self):

        # condition to check for FT compatibility
        if self.scenario_settings['ft'] == 2:
            if self.node_properties['no_of_nodes'] < 5 and self.scenario_settings['rf'] == 3:
                raise RXException('minimum node ft' + '|' + 'RF3' + '|' + '5')
            elif self.node_properties['no_of_nodes'] < 4 and self.scenario_settings['rf'] == 2:
                raise RXException('minimum node ft' + '|' + 'RF2' + '|' + '4')

        if not any(len(set(supported_cluster) & self.input_wls) == len(self.input_wls)
                   for supported_cluster in SUPPORTED_CLUSTERS):
            raise RXException('wrong cluster type' + '|' + str(SUPPORTED_CLUSTERS))

    def validate_workloads(self, workloads):

        error_workloads = list()
        robo_workloads = list()
        robo_min_nodes = list()
        vdi_workloads = list()
        subtype = self.hx_node.attrib[BaseConstants.SUBTYPE]

        hyp_workloads = list()
        hypervisor = self.scenario_settings['hypervisor']

        if 'robo' in subtype:
            wl_options = ROBO_WL
        elif 'all-flash' in subtype or 'allnvme' in subtype:
            wl_options = AF_WL
        elif 'veeam' in subtype:
            wl_options = VEEAM_WL
        else:
            wl_options = HYPER_WL

        for wl in workloads:

            wl_type = wl[BaseConstants.WL_TYPE]

            if wl_type not in wl_options:
                error_workloads.append(str(wl[BaseConstants.WL_NAME]))

            if wl_type in [HyperConstants.SPLUNK, HyperConstants.VEEAM] and hypervisor == 'hyperv':
                hyp_workloads.append(str(wl[BaseConstants.WL_NAME]))

            if (wl_type in [HyperConstants.ROBO, HyperConstants.ROBO_BACKUP_SECONDARY]) and wl['replication_factor'] == 3:
                if subtype in [HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE]:
                    robo_workloads.append(str(wl[BaseConstants.WL_NAME]))

                if self.node_properties['no_of_nodes'] < 3:
                    robo_min_nodes.append(str(wl[BaseConstants.WL_NAME]))

            if wl_type in [HyperConstants.VDI, HyperConstants.RDSH, HyperConstants.VDI_INFRA] and \
                    self.hx_node.attrib[HyperConstants.DISK_CAGE] == HyperConstants.LARGE_FORM_FACTOR:
                vdi_workloads.append(str(wl[BaseConstants.WL_NAME]))

        if error_workloads:
            raise RXException('wrong wl type' + '|' + str(error_workloads))

        if robo_workloads:
            raise RXException('wrong robo wl type' + '|' + str(robo_workloads))

        if robo_min_nodes:
            raise RXException('wrong min node' + '|' + str(robo_min_nodes))

        if hyp_workloads:
            raise RXException('wrong hypervisor' + '|' + str(hyp_workloads))

        if vdi_workloads:
            raise RXException('wrong wl lff' + '|' + str(vdi_workloads))

        if any(wl.get(HyperConstants.VDI_DIRECTORY, False) or wl.get(HyperConstants.RDSH_DIRECTORY, False) for wl in workloads):

            if self.scenario_settings['hypervisor'] == 'hyperv':

                raise RXException("home_directory_hyperv")

            if self.scenario_settings['node_properties']['node'] and \
                    not 'AF' in self.scenario_settings['node_properties']['node']:

                raise RXException("home_directory_AF")

    @staticmethod
    def get_rf_ft(workload_list):
        # To support fixed_config without workload.
        if not workload_list:
            return 3, 1
        replication_factors = list()
        fault_tolerance = list()
        for workload in workload_list:
            replication_factors.append(workload['replication_factor'])
            fault_tolerance.append(workload['fault_tolerance'])

        return max(replication_factors), max(fault_tolerance)

    def configure_settings(self):
        """
        solver setting configuration
        :return:
        """
        self.solver_settings['heterogenous'] = True if self.node_properties['no_of_computes'] else False
        self.solver_settings['result_name'] = 'Fixed_Config'
        self.solver_settings['threshold'] = self.scenario_settings['threshold']
        self.solver_settings['fault_tolerance'] = self.scenario_settings['ft']
        self.solver_settings['replication_factor'] = self.scenario_settings['rf']
        self.solver_settings['hypervisor'] = self.scenario_settings['hypervisor']
        self.solver_settings[HyperConstants.HERCULES_CONF] = self.scenario_settings[HyperConstants.HERCULES_CONF]
        self.solver_settings[HyperConstants.HX_BOOST_CONF] = self.scenario_settings[HyperConstants.HX_BOOST_CONF]

    def configure_node(self, node_object):
        """
        configure node to get utilisation from HyperconvergedSizer object
        :return:
        """
        def configure_cpu():

            node_object.attrib[HyperConstants.CPU_PART] = self.node_properties['cpu'][0]
            self.current_cpu = node_object.attrib[HyperConstants.CPU_PART]

            node_object.attrib[HyperConstants.CPU_AVAILABILITY] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.CPU_PART],
                                                 BaseConstants.AVAILABILITY)

            node_object.attrib[BaseConstants.CLOCK_SPEED] = self.node_properties['cpu'][2]

            node_object.attrib[BaseConstants.BASE_CPU_CLOCK] = self.base_cpu.speed

            node_object.attrib[HyperConstants.CORES_PER_CPU_PRESPECLNT] = self.node_properties['cpu'][1]

            node_object.attrib[BaseConstants.CPU_CNT] = node_object.attrib[BaseConstants.CPU_CNT][0]

            node_object.attrib[HyperConstants.SPECLNT] = self.node_properties['cpu'][4]

            node_object.attrib[BaseConstants.CORES_PER_CPU] = \
                node_object.attrib[HyperConstants.SPECLNT] * node_object.attrib[HyperConstants.CORES_PER_CPU_PRESPECLNT]

            node_object.attrib[HyperConstants.CPU_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.CPU_PART],
                                                 HyperConstants.DESCRIPTION)

            node_object.attrib[HyperConstants.TDP] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.CPU_PART], HyperConstants.TDP)

            node_object.attrib[HyperConstants.CPU_PRICE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.CPU_PART], HyperConstants.CTO_PRICE)

            node_object.attrib[HyperConstants.BOM_CPU_PART] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.CPU_PART], HyperConstants.BOM_NAME)

            node_object.attrib[HyperConstants.BOM_CPU_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.CPU_PART],
                                                 HyperConstants.BOM_DESCR)

            if node_object.attrib[BaseConstants.SUBTYPE] == 'compute' and \
                    'UCS' in node_object.attrib[HyperConstants.BOM_NAME]:

                node_object.attrib[HyperConstants.CPU_PART] += '[UCS]'

        def configure_ram():

            """ram configuration"""

            node_object.attrib[HyperConstants.RAM_PART] = self.node_properties['ram'][0]

            node_object.attrib[HyperConstants.RAM_AVAILABILITY] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.RAM_PART],
                                                 BaseConstants.AVAILABILITY)

            node_object.attrib[BaseConstants.RAM_SIZE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.RAM_PART], BaseConstants.CAPACITY)

            min_ram_slots = min(node_object.attrib[BaseConstants.RAM_SLOTS])

            node_object.attrib[BaseConstants.RAM_SLOTS] = int(self.node_properties['ram'][1])

            node_object.attrib[HyperConstants.RAM_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.RAM_PART],
                                                 HyperConstants.DESCRIPTION)

            if node_object.attrib[HyperConstants.TYPE] == BaseConstants.CTO:
                node_object.attrib[BaseConstants.MIN_SLOTS] = node_object.attrib[BaseConstants.RAM_SLOTS]
            else:
                node_object.attrib[BaseConstants.MIN_SLOTS] = min_ram_slots

            node_object.attrib[HyperConstants.RAM_PRICE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.RAM_PART],
                                                 HyperConstants.CTO_PRICE)

            node_object.attrib[HyperConstants.BOM_RAM_PART] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.RAM_PART], HyperConstants.BOM_NAME)

            node_object.attrib[HyperConstants.BOM_RAM_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.RAM_PART],
                                                 HyperConstants.BOM_DESCR)

            node_object.attrib[HyperConstants.BOM_ADD_MEM] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.RAM_PART],
                                                 HyperConstants.BOM_ADD_MEM)

            if node_object.attrib[BaseConstants.SUBTYPE] == 'compute' and \
                    'UCS' in node_object.attrib[HyperConstants.BOM_NAME]:
                node_object.attrib[HyperConstants.RAM_PART] += '[UCS]'

        def configure_hdd():

            node_object.attrib[HyperConstants.HDD_PART] = self.node_properties['disk_capacity'][1]

            node_object.attrib[HyperConstants.HDD_AVAILABILITY] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART],
                                                 BaseConstants.AVAILABILITY)

            node_object.attrib[BaseConstants.MIN_HDD_SLOTS] = min(node_object.attrib[BaseConstants.HDD_SLOTS])
            node_object.attrib[BaseConstants.MAX_HDD_SLOTS] = max(node_object.attrib[BaseConstants.HDD_SLOTS])

            if node_object.attrib[BaseConstants.SUBTYPE] == 'compute':
                node_object.attrib[BaseConstants.HDD_SLOTS] = 0
            else:
                node_object.attrib[BaseConstants.HDD_SLOTS] = self.node_properties['disks_per_node']

            node_object.attrib[BaseConstants.HDD_SIZE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART], BaseConstants.CAPACITY)

            node_object.attrib[HyperConstants.HDD_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART],
                                                 HyperConstants.DESCRIPTION)

            node_object.attrib[HyperConstants.HDD_TYPE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART], HyperConstants.HDD_TYPE)

            node_object.attrib[HyperConstants.HDD_PRICE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART], HyperConstants.CTO_PRICE)

            node_object.attrib[HyperConstants.BOM_HDD_PART] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART], HyperConstants.BOM_NAME)

            node_object.attrib[HyperConstants.BOM_HDD_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART],
                                                 HyperConstants.BOM_DESCR)

            if self.parts_table.is_part_attrib(node_object.attrib[HyperConstants.HDD_PART], HyperConstants.CUSTOM):
                custom_properties = self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART],
                                                                     HyperConstants.CUSTOM)

                node_object.attrib[BaseConstants.STATIC_OVERHEAD] = \
                    deepcopy(custom_properties[BaseConstants.STATIC_OVERHEAD])

            excess_slots = node_object.attrib[BaseConstants.HDD_SLOTS] - node_object.attrib[BaseConstants.MIN_HDD_SLOTS]

            if node_object.attrib[HyperConstants.TYPE] == BaseConstants.BUNDLE and excess_slots > 0:

                total_extra_hdds = self.node_properties['no_of_nodes'] * excess_slots

                hdd_add_part = self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.HDD_PART], 'hdd_add_part')

                hdd_accessories = self.solver_object.get_additional_hdd_parts(hdd_add_part, total_extra_hdds)

                for accessory in hdd_accessories:
                    self.accessories.append(accessory)

        def configure_ssd():

            node_object.attrib[HyperConstants.SSD_PART] = self.node_properties['cache_size'][1]

            if node_object.attrib[BaseConstants.SUBTYPE] == 'compute':
                ssd_per_server = 0
                node_object.attrib[BaseConstants.IOPS] = 0
            else:
                ssd_per_server = 1
                node_object.attrib[BaseConstants.IOPS] = 1

            node_object.attrib[BaseConstants.SSD_SLOTS] = ssd_per_server

            node_object.attrib[BaseConstants.SSD_SIZE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.SSD_PART], BaseConstants.CAPACITY)

            node_object.attrib[HyperConstants.SSD_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.SSD_PART],
                                                 HyperConstants.DESCRIPTION)

            node_object.attrib[HyperConstants.SSD_FULL_SIZE] = node_object.attrib[BaseConstants.SSD_SIZE]

            node_object.attrib[HyperConstants.SSD_OUTPUT_CAPACITY] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.SSD_PART],
                                                 HyperConstants.OUTPUT_CAPACITY)

            node_object.attrib[HyperConstants.SSD_PRICE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.SSD_PART], HyperConstants.CTO_PRICE)

            node_object.attrib[HyperConstants.SSD_AVAILABILITY] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.SSD_PART],
                                                 BaseConstants.AVAILABILITY)

            node_object.attrib[BaseConstants.IOPS_CONV_FAC] = \
                deepcopy(self.iops_conv_fac[node_object.attrib[HyperConstants.SSD_PART]]
                         [self.scenario_settings['threshold']])
            
            if node_object.attrib[BaseConstants.SUBTYPE] in [HyperConstants.ROBO_NODE, HyperConstants.AF_ROBO_NODE,
                                                             HyperConstants.ROBO_TWO_NODE,
                                                             HyperConstants.AF_ROBO_TWO_NODE, 
                                                             HyperConstants.ROBO_240, HyperConstants.ROBO_AF_240] \
                    and node_object.attrib[HyperConstants.TYPE] == BaseConstants.CTO:

                if 'iops_hdd_slots' in node_object.attrib:
                    max_diff = node_object.attrib['iops_hdd_slots'] - node_object.attrib[BaseConstants.MIN_HDD_SLOTS]

                else:
                    max_diff = node_object.attrib[BaseConstants.MAX_HDD_SLOTS] - \
                                node_object.attrib[BaseConstants.MIN_HDD_SLOTS]

                node_object.attrib[BaseConstants.IOPS_CONV_FAC][self.rf_string][HyperConstants.ROBO] = \
                    self.get_scaled_conv_fac(node_object.attrib[HyperConstants.SSD_PART],
                                             node_object.attrib[BaseConstants.HDD_SLOTS], max_diff,
                                             node_object.hercules_on, node_object.hx_boost_on)

            for wl_type in node_object.attrib[BaseConstants.IOPS_CONV_FAC][self.rf_string]:
                node_object.attrib[BaseConstants.IOPS_CONV_FAC][self.rf_string][wl_type][0] *= \
                    self.parts_table.get_part_attrib(self.current_cpu, HyperConstants.SPECLNT) / \
                    self.parts_table.get_part_attrib(HyperConstants.REF_IOPS_CPU, HyperConstants.SPECLNT)

            node_object.attrib[HyperConstants.BOM_SSD_PART] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.SSD_PART], HyperConstants.BOM_NAME)

            node_object.attrib[HyperConstants.BOM_SSD_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.SSD_PART],
                                                 HyperConstants.BOM_DESCR)

        def configure_vram():

            if node_object.attrib[BaseConstants.SUBTYPE] == 'compute':
                node_object.attrib[HyperConstants.GPU_PART] = 'UCSC-GPU-M10'
            else:
                node_object.attrib[HyperConstants.GPU_PART] = 'HX-GPU-M10'

            node_object.attrib[HyperConstants.GPU_AVAILABILITY] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.GPU_PART],
                                                 BaseConstants.AVAILABILITY)

            node_object.attrib[HyperConstants.GPU_SLOTS] = 0

            node_object.attrib[HyperConstants.GPU_CAP] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.GPU_PART], BaseConstants.CAPACITY)

            node_object.attrib[HyperConstants.GPU_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.GPU_PART],
                                                 HyperConstants.DESCRIPTION)

            node_object.attrib[HyperConstants.GPU_PRICE] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.GPU_PART], HyperConstants.CTO_PRICE)

            node_object.attrib[HyperConstants.VRAM] = \
                node_object.attrib[HyperConstants.GPU_SLOTS] * node_object.attrib[HyperConstants.GPU_CAP]

            node_object.attrib[HyperConstants.BOM_GPU_PART] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.GPU_PART], HyperConstants.BOM_NAME)

            node_object.attrib[HyperConstants.BOM_GPU_DESCR] = \
                self.parts_table.get_part_attrib(node_object.attrib[HyperConstants.GPU_PART],
                                                 HyperConstants.BOM_DESCR)

        configure_cpu()
        configure_ram()
        configure_hdd()
        configure_ssd()
        configure_vram()

        for cap in HyperConstants.WL_CAP_LIST:
            node_object.calculate_overhead(cap, self.solver_settings['hypervisor'])
            node_object.calc_cap(cap)
        node_object.calc_capex_opex()

    def get_threshold_key(self, threshold_key):

        """
        in utilization dictionary that is sent to UI, the resource names are different from those in threshold
        dictionary. hence a mapping is required
        :param threshold_key:
        :return:
        """
        if threshold_key == 'Storage Capacity':
            if 'AF' in self.node_properties['node']:
                return HyperConstants.ALL_FLASH_HDD

            if self.hx_node.attrib[HyperConstants.DISK_CAGE] == HyperConstants.LARGE_FORM_FACTOR:
                return HyperConstants.LFF_HDD

            return BaseConstants.HDD

        elif threshold_key == 'Cache':
            return BaseConstants.SSD
        elif threshold_key == 'Storage IOPS':
            return BaseConstants.IOPS
        elif threshold_key == "GPU Users":
            return BaseConstants.VRAM
        else:
            return threshold_key

    def validate_utilizations(self, util_list, wl_type):
        """
        Validates if the utilizations have exceeded 100% first and then checks if they have crossed the threshold.
        :param util_list:
        :param wl_type:
        :return:
        """
        '''
        handles >100% validation
        '''
        resource_exceeded = list()
        for util_dict in util_list:

            if not util_dict[HyperConstants.UTIL_STATUS]:
                continue

            if util_dict['wl_util'] > 100 or util_dict['ft_util'] > 100:
                resource_exceeded.append(util_dict['tag_name'])

        if resource_exceeded:
            raise RXException('too large workload' + '|' + str(resource_exceeded))

        '''
        handles >threshold validation
        '''
        threshold_exceeded = list()
        for util_dict in util_list:

            if not util_dict[HyperConstants.UTIL_STATUS]:
                continue

            threshold_percent = self.solver_object.get_threshold_value(wl_type,
                                                                       self.get_threshold_key(util_dict['tag_name']))
            # to convert fractionl value into percentage
            threshold_percent *= 100.0
            if util_dict['wl_util'] > threshold_percent or util_dict['ft_util'] > threshold_percent:
                threshold_exceeded.append(util_dict['tag_name'])

        if threshold_exceeded:
            raise RXException('threshold exceeded' + '|' + str(threshold_exceeded))

    def get_util(self):

        self.configure_node(self.hx_node)

        node_dict = {'node': self.hx_node,
                     'accessory': self.accessories,
                     'num': self.node_properties['no_of_nodes'],
                     'num_compute': self.node_properties['no_of_computes'],
                     'price': 0}

        if self.node_properties['no_of_computes']:

            self.configure_node(self.compute_node)
            node_dict['compute'] = self.compute_node

        else:

            node_dict['compute'] = None

        workload_list = self.solver_object.wl_list
        settings_dict = self.solver_settings

        cluster_data = [[[node_dict, workload_list, settings_dict]]]
        response = UtilizationGenerator(self.solver_object).build_multi_cluster_json(cluster_data)
        return response

    @staticmethod
    def get_sizing_calculator_result(scenario_settings):

        sizingcalc_req = defaultdict(dict)

        sizingcalc_req['node_properties'] = scenario_settings['node_properties']

        if 'cluster_properties' in scenario_settings:
            sizingcalc_req['scenario_settings'] = scenario_settings['cluster_properties']
        else:
            sizingcalc_req['scenario_settings']['rf'] = 3
            sizingcalc_req['scenario_settings']['ft'] = 0
            sizingcalc_req['scenario_settings']['compression_factor'] = 20
            sizingcalc_req['scenario_settings']['dedupe_factor'] = 10

        if 'workloads_type' in scenario_settings:
            sizingcalc_req['scenario_settings']['workloads_type'] = scenario_settings['workloads_type']
        else:
            sizingcalc_req['scenario_settings']['workloads_type'] = list()
        sizingcalc_req['scenario_settings']['threshold'] = scenario_settings['threshold']
        sizingcalc_req['scenario_settings']['hypervisor'] = scenario_settings['hypervisor']
        sizingcalc_req['scenario_settings']['hercules_conf'] = scenario_settings['hercules_conf']
        sizingcalc_req['scenario_settings']['hx_boost_conf'] = scenario_settings['hx_boost_conf']

        try:
            serializer = ReverseSizerCalculatorSerializer(data=sizingcalc_req)
            if serializer.is_valid():
                new_calc = ReverseSizer(sizingcalc_req)
                node_usables = new_calc.get_usable_resources()
                node_usables['result_name'] = 'Sizing Calculator'
                return node_usables
            else:
                raise RXException('sizingcalculator' + '|' + "Sizing calculator exception")
        except:
            raise RXException('sizingcalculator' + '|' + "Sizing calculator exception")
        
    def validate_large_vm_ram_limit(self, node_properties):
        """
         1. checks for large VM Issue
         2. valdate CPU ram limit
        """
        
        cpu_core = node_properties['cpu'][1]
        cpu_spec_int = node_properties['cpu'][4]
        cpu_slot = self.hx_node.attrib[BaseConstants.CPU_CNT][0]
        curr_core_per_node = cpu_core * cpu_spec_int * cpu_slot

        ram_slot = node_properties['ram'][1]
        ram_size = (node_properties['ram'][2])[0]
        current_ram_capacity = ram_slot * ram_size
        
        self.solver_object.find_large_vm_partition(self.solver_object.wl_list)
        
        # validates large VM issue 
        if(self.solver_object.is_large_vm):
            
            cpu_overhead_amt = self.hx_node.attrib[BaseConstants.STATIC_OVERHEAD][self.solver_settings['hypervisor']].get(BaseConstants.CPU, 0)
            ram_overhead_amt = self.hx_node.attrib[BaseConstants.STATIC_OVERHEAD][self.solver_settings['hypervisor']].get(BaseConstants.RAM, 0)
            
            total_node = node_properties['no_of_computes'] + node_properties['no_of_nodes']
            num_large_vms = max(self.solver_object.num_large_vms_cpu, self.solver_object.num_large_vms_ram)
            vm_per_node = ceil(num_large_vms / float(total_node))
            
            if(((vm_per_node * self.solver_object.large_cpu_req) + cpu_overhead_amt > curr_core_per_node) or \
                ((vm_per_node * self.solver_object.large_ram_req) + ram_overhead_amt > current_ram_capacity)):
                raise RXException('Large_Vm_Limit' + '|' + str(self.input_wls))
        
        # validates CPU ram limit
        current_cpu_ram_limit = node_properties['cpu'][3] * cpu_slot
        if(current_ram_capacity > current_cpu_ram_limit):
            raise RXException('CPU_RAM_Limit' + '|' + str(current_cpu_ram_limit))
