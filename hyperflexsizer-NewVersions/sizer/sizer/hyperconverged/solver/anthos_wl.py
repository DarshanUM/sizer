import logging
from math import ceil
from collections import defaultdict
from copy import deepcopy
from django.core.exceptions import ObjectDoesNotExist
from hyperconverged.exception import HXException
from base_sizer.solver.wl import WL, Infrastructure
from base_sizer.solver.attrib import BaseConstants
from .attrib import HyperConstants
from hyperconverged.models import SpecIntData

logger = logging.getLogger(__name__)

class WL_Anthos(WL):
    
    def __init__(self, attrib, herc_conf):

        super(WL_Anthos, self).__init__(attrib)

        max_user_cluster = 5
        load_balancer = 2
        controller_vm = 4
        self.pod_dict = dict()
        self.total_user_cluster = 0
        self.original_size = 0

        self.compression = (100 - self.attrib[HyperConstants.COMPRESSION_FACTOR]) / 100.0
        self.dedupe = (100 - self.attrib[HyperConstants.DEDUPE_FACTOR]) / 100.0
        self.herc_comp = (100 - HyperConstants.HERCULES_COMP) / 100.0

        for pod in self.attrib['pod_detail']:
            self.calc_pod(pod)

        total_admin_cluster  = ceil(self.total_user_cluster / max_user_cluster)
       
        # load balancer - CPU and RAM
        load_balancer_cpu = load_balancer *  self.attrib["controller_panel"]['load_balancer_cpu']
        load_balancer_ram = float(load_balancer *  self.unit_conversion(self.attrib["controller_panel"]['load_balancer_ram'],self.attrib["controller_panel"]['load_balancer_ram_unit'],'GiB'))


        # controller vm - CPU and RAM
        controller_vm_cpu = controller_vm *  self.attrib["controller_panel"]['controller_vm_cpu']
        controller_vm_ram = float(controller_vm *  self.unit_conversion(self.attrib["controller_panel"]['controller_vm_ram'],self.attrib["controller_panel"]['controller_vm_ram_unit'],'GiB'))

        # calculate control panel - CPU and RAM
        control_panel_cpu = load_balancer_cpu + controller_vm_cpu
        control_panel_ram = load_balancer_ram + controller_vm_ram


        #  calculate Anthos Master VMs - unit conversion is not taken here
        anthos_master_cpu = float(total_admin_cluster * 3 * self.attrib["anthos_master"]['vm_cpu'])
        anthos_master_ram = float(total_admin_cluster * 3 * self.unit_conversion(self.attrib["anthos_master"]['vm_ram'], self.attrib["anthos_master"]['vm_ram_unit'], 'GiB'))
        anthos_master_storage = float(total_admin_cluster * 3 * self.unit_conversion(self.attrib["anthos_master"]['vm_storage'],self.attrib["anthos_master"]['vm_storage_unit']))
        anthos_master_gc_ops = float(total_admin_cluster * self.unit_conversion(self.attrib["anthos_master"]['gc_ops_overhead'], self.attrib["anthos_master"]['gc_ops_overhead_unit']))
        anthos_master_etcd = float(total_admin_cluster * self.unit_conversion(self.attrib["anthos_master"]['etcd_anthos_master'],self.attrib["anthos_master"]['etcd_anthos_master_unit']))


        # self.original_size = self.capsum['normal'][BaseConstants.HDD]
        # for pod_name, details in self.pod_dict.iteritems():
        for cap in HyperConstants.WL_CAP_LIST:
            if cap == BaseConstants.CPU:
                self.capsum['normal'][cap] +=  control_panel_cpu + anthos_master_cpu
            elif cap == BaseConstants.RAM:
                self.capsum['normal'][cap] +=  control_panel_ram + anthos_master_ram
            elif cap == BaseConstants.HDD:
                self.capsum['normal'][cap] +=  anthos_master_storage + anthos_master_gc_ops + anthos_master_etcd
                self.original_size = self.capsum['normal'][BaseConstants.HDD]
                self.capsum['normal'][cap] = self.capsum['normal'][cap] * self.compression * self.dedupe
            elif cap == BaseConstants.SSD:
                continue
            elif cap == BaseConstants.IOPS:
                self.original_iops_sum = {self.attrib[HyperConstants.INTERNAL_TYPE]: 0}
            elif cap == BaseConstants.VRAM:
                continue

        if herc_conf != HyperConstants.DISABLED:
            self.calc_cap_hercules()

    def calc_pod(self, pod):
        pod_name = pod['pod_name']
        self.pod_dict[pod_name] = dict()

        max_worker_node_per_cluster = 100
        total_core_pod = float((pod['pod_cpu'] /1000) * pod['pod_quantity'])
        total_ram_pod = float(self.unit_conversion( pod['pod_ram'], pod['pod_ram_unit'], 'GiB') * pod['pod_quantity'])
        total_storage_pod = float(self.unit_conversion(pod['pod_storage'], pod['pod_storage_unit']) * pod['pod_quantity'])

        # overhead calculation
        # 50MilliCore+1% of worker node VM size
        cpu_overhead = 0.05 + ( 0.01 * pod['worker_node_cpu'])
        # 250MiB+5%
        ram_overhead = 0.25 + (0.05 * pod['worker_node_ram'])

        cpu_worker_node = float((total_core_pod + cpu_overhead) / pod['worker_node_cpu'])
        ram_worker_node = float((total_ram_pod + ram_overhead) / self.unit_conversion(pod['worker_node_ram'], pod['worker_node_ram_unit'], 'GiB'))

        max_worker_node = round(max(cpu_worker_node, ram_worker_node))
        max_user_cluster = ceil(cpu_worker_node / max_worker_node_per_cluster)

        # self.pod_dict[pod_name]['worker_node_req'] = cpu_worker_node
        # self.pod_dict[pod_name]['user_cluster_req'] = max_user_cluster
        self.total_user_cluster = self.total_user_cluster + max_user_cluster
        if (self.total_user_cluster > 1000):
            raise HXException("Total user cluster count ("+ self.total_user_cluster +") crossed the limit of 1000" + self.logger_header)
        
        # calculate User Master VMs
        if  pod['pod_ha']:
            user_master_cpu = max_user_cluster * 3 * self.attrib['user_vm_cpu']
            user_master_ram = max_user_cluster * 3 * self.unit_conversion(self.attrib['user_vm_ram'], self.attrib['user_vm_ram_unit'], 'GiB')
            user_master_storage = max_user_cluster * 3 * self.unit_conversion(self.attrib['user_vm_storage'], self.attrib['user_vm_storage_unit'])
            audit_log_storage = max_user_cluster * 3 * self.unit_conversion(self.attrib['audit_log'],self.attrib['audit_log_unit'])
            etcd_event_data = max_user_cluster * 3 * self.unit_conversion(self.attrib['etcd_event'],self.attrib['etcd_event_unit'])

        else:
            user_master_cpu = max_user_cluster * self.attrib['user_vm_cpu']
            user_master_ram = max_user_cluster * self.unit_conversion(self.attrib['user_vm_ram'], self.attrib['user_vm_ram_unit'], 'GiB')
            user_master_storage = max_user_cluster * self.unit_conversion(self.attrib['user_vm_storage'], self.attrib['user_vm_storage_unit'])
            # user_master_storage = max_user_cluster * self.attrib['user_vm_storage']
            audit_log_storage = max_user_cluster * self.unit_conversion(self.attrib['audit_log'],self.attrib['audit_log_unit'])
            etcd_event_data = max_user_cluster * self.unit_conversion(self.attrib['etcd_event'],self.attrib['etcd_event_unit'])

        
        # prometheous for storage
        if pod['prometheous_on']:
            prometheous = max_user_cluster * self.unit_conversion(self.attrib['prometheous_storage'], self.attrib['prometheous_storage_unit'])
        else:
            prometheous = 0

        # Worker Nodes Calculation -- may need unit conversion
        worker_node_cpu_req = max_worker_node * pod['worker_node_cpu']
        worker_node_ram_req = max_worker_node * self.unit_conversion(pod['worker_node_ram'],pod['worker_node_ram_unit'],'GiB')
        # worker_node_storage_req = max_worker_node * pod['worker_node_storage'] 
        worker_node_storage_req = total_storage_pod + (max_user_cluster * self.unit_conversion(self.attrib['gc_ops_overhead_user_vm'],self.attrib['gc_ops_overhead_user_vm_unit'])) 


        self.capsum['normal']['CPU']  += user_master_cpu + worker_node_cpu_req
        self.capsum['normal']['RAM'] += user_master_ram + worker_node_ram_req
        self.capsum['normal']['HDD'] += user_master_storage + worker_node_storage_req + audit_log_storage + etcd_event_data + prometheous
        
        # self.pod_dict[pod_name]['worker_user_cpu'] = user_master_cpu + worker_node_cpu_req


    def calc_cap_hercules(self):

        self.capsum['hercules'] = deepcopy(self.capsum['normal'])

        # self.capsum['hercules'][BaseConstants.HDD] = self.capsum['normal'][BaseConstants.HDD] * self.herc_comp
