from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from utils.baseview import BaseView

from hyperconverged.views.filter_option_views import RevSizerBaseFilter
from hyperconverged.serializer.CalculatorSerializer import BenchSheetSerializer

DEDUPE_SAVING = 35
COMPRESSION_SAVING = 35
# the maximum VM size should 2TB*#nodes
DISK_MAX = 2000
# threads supported by each node is assumed to be 100
THREADS_PER_NODE = 100


class BenchSheetCalc(BaseView):

    def __init__(self):
        self.node = ''
        self.hdd_capacity = 0
        self.ssd_capacity = 0
        self.hdd_num = 0
        self.num_node = 0
        self.num_vm_per_node = 0
        self.num_vm = 0
        self.rf = 0
        self.data = dict()
        self.vm_size_pre_saving = 0
        self.vm_size_post_saving = 0
        self.working_set_percent = 0
        self.threads_per_vm = 0
        self.vm_size_unit = 'GB'

    @staticmethod
    def get(request):
        """
        Imports the RevSizerBaseFilter class and calls its abstract method which returns the required fields along with nodename
        :param request:
        :return: list of dictionaries that correspond to node and its hdd slots, hdd options, ssd options
        """
        requirements = ["ssd_options", "hdd_options", "num_nodes", "rf"]
        return Response(RevSizerBaseFilter.filter_node_attrib(requirements))

    def core_calculations(self):
        """
        performs the main calculations
        :return: creates objecr attriutes - VM size, workind set size
        """
        # VM size calculation
        # minimum of 2TB per node or normal calculation i.e. nodes * disk_cap * #disks * 0.92/rf
        dedupe = (100 - DEDUPE_SAVING) / 100.0
        compression = (100 - COMPRESSION_SAVING) / 100.0
        self.vm_size_pre_saving = min(0.3*self.num_node*self.hdd_capacity*self.hdd_num*0.92/self.rf,
                                      DISK_MAX*self.num_node)
        self.vm_size_post_saving = self.vm_size_pre_saving / (self.num_vm * dedupe * compression)

        # Thread count calculation
        self.threads_per_vm = int(THREADS_PER_NODE / self.num_vm_per_node)

        # cache size calculations - SSD size (%) in terms of total disk before dedupe and compression
        if 'AF' in self.node:
            self.working_set_percent = 100
        else:
            # for now have hard coded the node cache factor to be 0.73 for 220 nodes and 0.78 for 240s
            if "220" in self.node:
                node_cache_factor = 0.73
            elif "240" in self.node:
                node_cache_factor = 0.78
            else:
                raise Exception("Not yet implemented")
            self.ssd_capacity = self.ssd_capacity * self.num_node * node_cache_factor
            self.working_set_percent = min(self.ssd_capacity*100.0/self.vm_size_pre_saving, 100)

    def construct_response(self):
        """
        used to construct response using the object attributes
        :return:
        """
        response = dict()
        response["dedupe"] = "{0:.1f}".format(DEDUPE_SAVING)
        response["compression"] = "{0:.1f}".format(COMPRESSION_SAVING)
        response["no_of_vms"] = self.num_vm
        response["threads"] = self.threads_per_vm
        response["vm_size"] = "{0:.1f}".format(self.vm_size_post_saving)
        response["vm_size_unit"] = self.vm_size_unit
        if self.working_set_percent < 1:
            response["working_set_percent"] = "{0:.1f}".format(1)
        else:
            response["working_set_percent"] = "{0:.1f}".format(self.working_set_percent)

        return response

    def gb_tb_convert(self):
        if self.vm_size_post_saving > 1000:
            self.vm_size_unit = 'TB'
            self.vm_size_post_saving /= 1000.0

    def post(self, request):
        self.data = JSONParser().parse(request)
        serializer = BenchSheetSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)
        self.node = self.data["node"]
        self.num_node = self.data["no_of_nodes"]
        self.num_vm_per_node = self.data.get("no_of_vms", 3)
        self.num_vm = self.num_vm_per_node * self.num_node
        self.rf = self.data["rf"]
        self.hdd_num = self.data["disks_per_node"]
        self.hdd_capacity = self.data["disk_capacity"]
        self.ssd_capacity = self.data["cache_size"]
        self.core_calculations()
        self.gb_tb_convert()
        return Response(self.construct_response())
