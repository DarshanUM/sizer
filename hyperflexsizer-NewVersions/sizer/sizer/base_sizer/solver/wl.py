
"""Base calculation file for all the workloads."""
import logging
from collections import defaultdict

from hyperconverged.solver.attrib import HyperConstants
from hyperconverged.models import SpecIntData

logger = logging.getLogger(__name__)


class WL(object):
    def __init__(self, attrib):
        self.attrib = attrib

        self.capsum = {
            'hercules': defaultdict(int),
            'normal': defaultdict(int)
        }

        self.original_iops_sum = None

    def print_attrib(self):
        for key in self.attrib.keys():
            logger.info(key + " = %s" % self.attrib[key])

    def print_cap(self):
        logger.info(self.attrib[HyperConstants.WL_NAME])
        for cap in HyperConstants.CAP_LIST:
            logger.info(cap + " = %d" % self.cap[cap])

    def fits_in(self, node, threshold_factor):
        for cap in HyperConstants.CAP_LIST:
            if node.cap[cap] * threshold_factor[cap] < self.cap[cap]:
                return False

        return True

    def to_json(self):
        return self.attrib

    @staticmethod
    def normalise_cpu(host_cpu=None):

        if not host_cpu:
            return 1

        if host_cpu.blended_core_2017:
            base_blended_core = SpecIntData.objects.get(is_base_model=True).blended_core_2017
            host_blended_core = host_cpu.blended_core_2017
        else:
            base_blended_core = SpecIntData.objects.get(is_base_model=True).blended_core_2006
            host_blended_core = host_cpu.blended_core_2006

        return host_blended_core / float(base_blended_core)

    @staticmethod
    def unit_conversion(num, unit, req_unit='GB'):

        if req_unit == 'GB':
            if unit == 'TB':
                return num * 1000
            elif unit == 'GiB':
                return num * HyperConstants.GIB_TO_GB_CONVERSION
            elif unit == 'TiB':
                return num * HyperConstants.TIB_TO_TB_CONVERSION * 1000
            else:
                return num

        elif req_unit == 'GiB':
            if unit == 'TiB':
                return num * 1024
            elif unit == 'GB':
                return num / HyperConstants.GIB_TO_GB_CONVERSION
            elif unit == 'TB':
                return (num / HyperConstants.TIB_TO_TB_CONVERSION) * 1024
            else:
                return num


class Infrastructure(object):

    def __init__(self, vm_details):

        self.vm_details = vm_details
        self.compression = None
        self.dedupe = None

        self.original_size = 0

        self.capsum = {
            'hercules': defaultdict(int),
            'normal': defaultdict(int)
        }

        self.log_vm_details()

    def log_vm_details(self):

        for vm in self.vm_details:
            logger.info(vm + ': ' + str(self.vm_details[vm]))
