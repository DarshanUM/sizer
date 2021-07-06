from .attrib import BaseConstants
from .node_sizing import PartsTable
import logging

logger = logging.getLogger(__name__)

SIZING_OBJ_CAPEX = 'Minimum Capex'
SIZING_OBJ_TCO = 'Minimum TCO'

SIZING_LEVEL_AGGR = 'Aggregate Level Sizing'
SIZING_LEVEL_NODE = 'Node Level Sizing'

OPEX_YEARS = 5
RESULT_SIZE = 3
TOP_VALUE = 10

COUNT = 'count'
NODE = 'node'
NUM = 'num'
PART = 'part'
PRICE = 'price'
SIZE = 'size'


class Sizer(object):
    def __init__(self, part_json, node_json, scen_json):

        self.parts_table = ""
        self.usable_node_list = list()
        self.load_parts(part_json)
        self.load_nodes(node_json)
        self.load_wl(scen_json)
        
        self.print_info()
        
        self.find_usable_nodes()
        
        self.wl_sum = dict()
        for cap in BaseConstants.CAP_LIST:
            self.wl_sum[cap] = sum(wl.num_inst * wl.cap[cap] for wl in self.wl_list)

    def load_parts(self, part_list):

        self.parts_table = PartsTable()

        for part in part_list:
            pid = part[BaseConstants.PART_ID]
            self.parts_table.add_part(pid)

            for key in part.keys():
                if key != BaseConstants.PART_ID:
                    self.parts_table.add_part_attrib(pid, key, part[key])

    def print_info(self):
        logger.info("WL = %d" % len(self.wl_list))
        for wl in self.wl_list:
            wl.print_cap()

    def find_usable_nodes(self):
        for node in self.node_list:
            add = True

            for wl in self.wl_list:
                if not wl.fits_in(node):
                    add = False
                    break

            if add:
                self.usable_node_list.append(node)

    def solve(self, obj=SIZING_OBJ_CAPEX, level=SIZING_LEVEL_NODE):
        pass

    def add_result(self, node, num, price):
        if not self.result:
            self.result.insert(0, {NODE: node, NUM: num, PRICE: price})
            return
        
        for index in range(0, len(self.result)):
            if ((price < self.result[index][PRICE]) or
                    ((price == self.result[index][PRICE]) and (num < self.result[index][NUM]))):

                self.result.insert(index, {NODE: node,
                                           NUM: num,
                                           PRICE: price})
                return

        self.result.insert(index + 1, {NODE: node,
                                       NUM: num,
                                       PRICE: price})

    def print_result(self, level):
        logger.info(level)
        logger.info("WL Total")
        for cap in BaseConstants.CAP_LIST:
            logger.info(cap + " = %s" % self.wl_sum[cap])

        for i in range(0, min(TOP_VALUE, len(self.result))):
            logger.info("#%d :" % (i + 1))
            logger.info("Price = %d" % self.result[i][PRICE])
            logger.info("Num = %d" % self.result[i][NUM])
            self.result[i][NODE].print_cap()
