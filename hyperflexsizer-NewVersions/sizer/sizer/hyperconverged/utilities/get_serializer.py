from hyperconverged.solver.attrib import HyperConstants
from base_sizer.solver.attrib import BaseConstants


def get_wl_serializer_details(wl_list):

    serializer_data = {HyperConstants.RAW: list(),
                       HyperConstants.EXCHANGE: list(),
                       HyperConstants.VDI: list(),
                       HyperConstants.RDSH: list(),
                       HyperConstants.VSI: list(),
                       HyperConstants.DB: list(),
                       HyperConstants.OLTP: list(),
                       HyperConstants.OLAP: list(),
                       HyperConstants.ROBO: list(),
                       HyperConstants.ORACLE: list(),
                       HyperConstants.OOLAP: list(),
                       HyperConstants.OOLTP: list(),
                       HyperConstants.VDI_INFRA: list(),
                       HyperConstants.EPIC: list(),
                       HyperConstants.VEEAM: list(),
                       HyperConstants.SPLUNK: list(),
                       HyperConstants.CONTAINER: list(),
                       HyperConstants.AIML: list(),
                       HyperConstants.ANTHOS: list(),
                       HyperConstants.ROBO_BACKUP: list()}
                    #    HyperConstants.ROBO_BACKUP_SECONDARY: list()}

    replication_enabled = False

    for wl_type in wl_list:

        if wl_type[BaseConstants.WL_TYPE] in [HyperConstants.VSI, HyperConstants.ORACLE, HyperConstants.DB,
                                              HyperConstants.AWR_FILE]:

            remote_flag = wl_type.get("remote_replication_enabled", False)
            if not remote_flag:
                wl_type["replication_amt"] = 0
            else:
                replication_enabled = True

        if wl_type[BaseConstants.WL_TYPE] in [HyperConstants.ORACLE, HyperConstants.DB, HyperConstants.AWR_FILE]:

            if wl_type[BaseConstants.WL_TYPE] == HyperConstants.DB and wl_type['db_type'] == HyperConstants.OLTP:
                internal_type = HyperConstants.OLTP

            elif wl_type[BaseConstants.WL_TYPE] == HyperConstants.DB and wl_type['db_type'] == HyperConstants.OLAP:
                internal_type = HyperConstants.OLAP

            elif wl_type[BaseConstants.WL_TYPE] == HyperConstants.ORACLE and wl_type['db_type'] == HyperConstants.OLTP:
                internal_type = HyperConstants.OOLTP

            elif wl_type[BaseConstants.WL_TYPE] == HyperConstants.ORACLE and wl_type['db_type'] == HyperConstants.OLAP:
                internal_type = HyperConstants.OOLAP

            elif wl_type[BaseConstants.WL_TYPE] == HyperConstants.AWR_FILE and wl_type['db_type'] == HyperConstants.OLTP:
                internal_type = HyperConstants.OOLTP

            elif wl_type[BaseConstants.WL_TYPE] == HyperConstants.AWR_FILE and wl_type['db_type'] == HyperConstants.OLAP:
                internal_type = HyperConstants.OOLAP

        elif wl_type[BaseConstants.WL_TYPE] == HyperConstants.RAW_FILE:
            internal_type = HyperConstants.RAW

        else:
            internal_type = wl_type[BaseConstants.WL_TYPE]

        if internal_type in serializer_data:
            wl_type[HyperConstants.INTERNAL_TYPE] = internal_type
            serializer_data[internal_type].append(wl_type)

    # remove empty workload list
    for key in list(serializer_data.keys()):
        if not serializer_data[key]:
            del serializer_data[key]

    return serializer_data, replication_enabled
