from copy import deepcopy

from base_sizer.solver.attrib import BaseConstants
from .attrib import HyperConstants
from hyperconverged.exception import HXException
from .wl import WL_Raw, WL_Exchange, WL_VDI, WL_RDSH, INFRA_VDI, WL_VM, WL_DB, WL_OLTP, WL_OLAP, WL_ROBO, WL_ORACLE, WL_OOLAP, \
    WL_OOLTP, EPIC_CLUSTER, Veeam, Splunk, WL_VDI_HOME, WL_RDSH_HOME, CONTAINER, AIML, WL_ROBO_BACKUP
from .anthos_wl import WL_Anthos


class Workload(object):

    def __init__(self, workloads):

        self.vdi_user = 0
        self.rdsh_user = 0
        self.vm_user = 0
        self.db_user = 0
        self.raw_user = 0
        self.exchange_user = 0
        self.robo_user = 0
        self.oracle_user = 0
        self.wl_list = list()
        self.dr_exists = False
        self.current_cluster = ''
        self.load_wl(workloads)
        self.wl_dict = dict()

    def load_wl(self, workloads):

        herc_conf = self.settings_json[HyperConstants.HERCULES_CONF]

        for wl in workloads:

            if wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.RAW:
                new_wl = WL_Raw(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.EXCHANGE:
                new_wl = WL_Exchange(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.VDI:
                new_wl = WL_VDI(wl, herc_conf)
                if HyperConstants.VDI_DIRECTORY in new_wl.attrib and new_wl.attrib[HyperConstants.VDI_DIRECTORY]:
                    new_wl_home = WL_VDI_HOME(deepcopy(new_wl.attrib), herc_conf)
                    self.wl_list.append(new_wl_home)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.RDSH:
                new_wl = WL_RDSH(wl, herc_conf)
                if HyperConstants.RDSH_DIRECTORY in new_wl.attrib and new_wl.attrib[HyperConstants.RDSH_DIRECTORY]:
                    new_wl_home = WL_RDSH_HOME(deepcopy(new_wl.attrib), herc_conf)
                    self.wl_list.append(new_wl_home)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.VDI_INFRA:
                new_wl = INFRA_VDI(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.VSI:
                new_wl = WL_VM(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.DB:
                new_wl = WL_DB(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.OLTP:
                new_wl = WL_OLTP(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.OLAP:
                new_wl = WL_OLAP(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.ROBO:
                new_wl = WL_ROBO(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.ORACLE:
                new_wl = WL_ORACLE(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.OOLTP:
                new_wl = WL_OOLTP(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.OOLAP:
                new_wl = WL_OOLAP(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.EPIC:
                new_wl = EPIC_CLUSTER(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.VEEAM:
                new_wl = Veeam(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.SPLUNK:
                new_wl = Splunk(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.CONTAINER:
                new_wl = CONTAINER(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.AIML:
                new_wl = AIML(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.ANTHOS:
                new_wl = WL_Anthos(wl, herc_conf)

            elif wl[HyperConstants.INTERNAL_TYPE] == HyperConstants.ROBO_BACKUP:
                new_wl = WL_ROBO_BACKUP(wl, herc_conf)
                if HyperConstants.TAGGED_WL in new_wl.attrib and (not new_wl.attrib[HyperConstants.TAGGED_WL]):
                    robo_wl = deepcopy(wl)
                    robo_wl[HyperConstants.WL_TYPE] = HyperConstants.ROBO
                    robo_wl[HyperConstants.WL_NAME] += '_BACKUP'
                    robo_wl[HyperConstants.INTERNAL_TYPE] = HyperConstants.ROBO
                    robo_wl[HyperConstants.TAGGED_WL] = robo_wl[HyperConstants.WL_NAME]
                    
                    new_wl_robo = WL_ROBO(robo_wl, herc_conf)
                    self.wl_list.append(new_wl_robo)

            else:
                self.logger.error("%s Unknown Workload Type = %s" % (self.logger_header,
                                                                     wl[HyperConstants.INTERNAL_TYPE]))

                raise HXException("Unknown_WL |" + self.logger_header)

            self.update_replication_type(new_wl, herc_conf)

    def update_replication_type(self, new_wl, herc_conf):

        if HyperConstants.REPLICATION_FLAG in new_wl.attrib:

            if new_wl.attrib[HyperConstants.REPLICATION_FLAG]:

                secondary = deepcopy(new_wl)
                secondary.calc_cap_normal(HyperConstants.REPLICATED)

                if herc_conf != HyperConstants.DISABLED:
                    secondary.calc_cap_hercules()

                if secondary.num_inst > 1500:
                    msg = "The number of instances in a DR cluster can't be greater than 1500. " \
                          "Please split the workload: " + new_wl.attrib['wl_name']
                    raise HXException("DR_CLUSTER_LIMIT |" + msg)

                # If Primary is remote, set secondary to local, and reverse
                if new_wl.attrib[HyperConstants.REMOTE]:
                    new_wl.attrib[HyperConstants.REPLICATION_TYPE] = HyperConstants.REPLICATED
                    secondary.attrib[HyperConstants.REPLICATION_TYPE] = HyperConstants.NORMAL
                else:
                    new_wl.attrib[HyperConstants.REPLICATION_TYPE] = HyperConstants.NORMAL
                    secondary.attrib[HyperConstants.REPLICATION_TYPE] = HyperConstants.REPLICATED

                self.wl_list.append(secondary)
            else:
                new_wl.attrib[HyperConstants.REPLICATION_TYPE] = HyperConstants.ANY_CLUSTER

        self.wl_list.append(new_wl)

    # def get_workload_statistics_counts(self):
    #
    #     for wl in self.wl_list:
    #         if wl.attrib[BaseConstants.WL_TYPE] == HyperConstants.RAW:
    #             self.raw_user += 1
    #         elif wl.attrib[BaseConstants.WL_TYPE] == HyperConstants.EXCHANGE:
    #             self.exchange_user += 1
    #         elif wl.attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.VDI:
    #             self.vdi_user += int(wl.attrib[HyperConstants.NUM_DT])
    #         elif wl.attrib[BaseConstants.WL_TYPE] == HyperConstants.VSI:
    #             self.vm_user += int(wl.attrib[HyperConstants.NUM_VM])
    #         elif wl.attrib[BaseConstants.WL_TYPE] == HyperConstants.ROBO:
    #             self.robo_user += int(wl.attrib[HyperConstants.NUM_VM])
    #         elif wl.attrib[BaseConstants.WL_TYPE] == HyperConstants.DB:
    #             self.db_user += int(wl.attrib[HyperConstants.NUM_DB])
    #         elif wl.attrib[BaseConstants.WL_TYPE] == HyperConstants.ORACLE:
    #             self.oracle_user += int(wl.attrib[HyperConstants.NUM_DB])

    def filter_workload_list_to_cluster_type(self):

        for wl in self.wl_list:

            cluster_type = wl.attrib.get(HyperConstants.CLUSTER_TYPE, HyperConstants.NORMAL)
            wl_type = wl.attrib[BaseConstants.WL_TYPE]

            if wl_type == HyperConstants.RAW_FILE:
                wl_type = HyperConstants.RAW

            if wl_type == HyperConstants.AWR_FILE:
                wl_type = HyperConstants.ORACLE

            if wl_type == HyperConstants.ROBO and HyperConstants.TAGGED_WL in wl.attrib and  wl.attrib[HyperConstants.TAGGED_WL]:
                self.wl_dict[cluster_type][HyperConstants.ROBO_BACKUP_SECONDARY].append(wl)
            else:
                self.wl_dict[cluster_type][wl_type].append(wl)

        # self.get_workload_statistics_counts()

    def get_req(self, workload, cap):

        if not self.hercules:
            node_type = 'normal'
        else:
            node_type = 'hercules'

        return workload.capsum[node_type][cap]
