from .attrib import HyperConstants
from copy import deepcopy


class Cluster(object):

    def __init__(self):
        self.cluster_types = [HyperConstants.NORMAL, HyperConstants.STRETCH]
        self.cluster_result = list()
        self.result = list()
        self.current_cluster = ""
        self.wl_dict = dict()
        self.init_cluster_wl_dict()

    def init_cluster_wl_dict(self):
        wl_base = {HyperConstants.VDI: list(),
                   HyperConstants.RDSH: list(),
                   HyperConstants.VDI_INFRA: list(),
                   HyperConstants.VSI: list(),
                   HyperConstants.DB: list(),
                   HyperConstants.ORACLE: list(),
                   HyperConstants.RAW: list(),
                   HyperConstants.EXCHANGE: list(),
                   HyperConstants.ROBO: list(),
                   HyperConstants.EPIC: list(),
                   HyperConstants.VEEAM: list(),
                   HyperConstants.SPLUNK: list(),
                   HyperConstants.CONTAINER: list(),
                   HyperConstants.AIML: list(),
                   HyperConstants.ANTHOS: list(),
                   HyperConstants.ROBO_BACKUP: list(),
                   HyperConstants.ROBO_BACKUP_SECONDARY: list()}

        for cluster_type in self.cluster_types:
            self.wl_dict[cluster_type] = deepcopy(wl_base)
