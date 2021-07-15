import logging
import logging.config
logger = logging.getLogger(__name__)

# error messages
ERR_MSG = "error_message"


class HXException(Exception):

    def __init__(self, message):

        return_msg = self.process_exception(message)
        super(HXException, self).__init__(return_msg)

    @staticmethod
    def process_exception(message):

        parsed_exception = message.split('|')

        if 'unsupported operand' in message:
            msg = 'Invalid input data. Data of wrong datatype.'
            error_code = 1

        elif 'Unfeasible' in message:
            msg = 'No valid sizing possible. Split workloads into new cluster.'
            error_code = 2

        elif 'WL_Too_Large' in message:

            workload = str(parsed_exception[1][1:-1]).replace("'", "")

            msg = 'A workload is too large to fit into one cluster. ' \
                  'Split the following workloads into smaller workloads.'
            msg += '<br />Workloads: '
            msg += workload
            error_code = 3

        elif 'No_HC_Nodes' in message:
            msg = 'No SmartPlay hyperconverged nodes have been chosen, due to filters. Please change the filters.'
            error_code = 6

        elif 'No_Compute_Nodes' in message:
            msg = 'No compute nodes have been chosen, for Hyperflex + Compute, due to filters. ' \
                  'Please change the filters.'
            error_code = 7

        elif 'Invalid Database' in message:
            msg = message
            error_code = 8

        elif 'No_Settings_Json' in message:
            msg = 'No settings json provided.'
            error_code = 9

        elif 'No_GPU_Nodes' in message:
            msg = 'No GPU nodes found, with a GPU workload added.'
            error_code = 10

        elif 'No_DB_Nodes' in message:
            msg = 'No All-Flash nodes found, with a DB workload added.'
            error_code = 11

        elif 'No_Compute_Node_Combinations' in message:
            msg = 'No compute nodes available due to filters.'
            error_code = 12

        elif 'Missing_Threshold_Value' in message:
            msg = 'A threshold value is missing in the database.'
            error_code = 13

        elif 'No_ROBO_Nodes' in message:
            msg = 'No Edge nodes have been chosen, with a Edge workload, due to filters. Please change the filters.'
            error_code = 14

        elif 'No_CTO_HC_Nodes' in message:
            msg = 'No CTO hyperconverged nodes have been chosen, due to filters. Please change the filters.'
            error_code = 15

        elif 'ROBO_Unsupported' in message:
            msg = 'Edge is not supported for All-Flash Clusters. Please check the Lowest_Cost option for the ' \
                  'sizing result.'
            error_code = 16

        elif 'No_Part_Combination' in message:

            msg = 'No Part Combination was found for the given workload requirements. Please change the filters.'
            error_code = 17
            
        elif 'Large_Vm_Limit' in message:
            
            workload = str(parsed_exception[1][1:-1]).replace("'", "")

            msg = 'One or more workload requirement has large CPU/RAM requirement which cannot be satisfied by the current filters.'
            msg += '<br />Recommendation: Split the following workloads in half.'
            msg += '<br />Workloads: '
            msg += workload
            error_code = 27

        elif 'WL_Exceeds_Cap' in message:

            workload = str(parsed_exception[1][1:-1]).replace("'", "")

            cap = parsed_exception[2].strip()
            error_part = parsed_exception[3].strip()
            error_node_count = parsed_exception[5].strip()
            error_cluster_count = parsed_exception[6].strip()
            wl_type = parsed_exception[7].strip()
            hypervisor = parsed_exception[11].strip()

            msg = 'One or more workloads have exceeded the maximum ' + cap + ' limits.'
            if cap in 'HDD':
                msg += '<br />Note this includes dedupe, compression, and replication.'
            msg += '<br />Projected Sizing Constraint: ' + error_part
            msg += '<br />Projected Node Count: ' + error_node_count + ' (Max Cluster Size : ' + error_cluster_count +')'
            msg += '<br />Recommendations:'
            if cap in ['CPU', 'RAM', 'GPU_USERS'] and wl_type not in 'ROBO' and hypervisor != 'hyperv':
                msg += '<br />- Toggle to "HX + Compute"'
            msg += '<br />- Split the following workloads into smaller workloads: '
            msg += workload
            error_code = 17

        elif 'CONTAINER_IOPS' in message:

            workload = str(parsed_exception[1][1:-1]).replace("'", "")

            error_part = parsed_exception[2].strip()
            error_node_count = parsed_exception[4].strip()
            error_cluster_count = parsed_exception[5].strip()

            msg = 'Container workloads can use a maximum of %s nodes for IO operations.' % error_cluster_count
            msg += '<br />Projected Sizing Constraint: ' + error_part
            msg += '<br />Projected Node Count: ' + error_node_count
            msg += '<br />Recommendations:'
            msg += '<br />- Split the following workloads into smaller workloads: '
            msg += workload

            error_code = 18

        elif 'Part_Overhead_Exceeded' in message:

            workload = str(parsed_exception[1][1:-1]).replace("'", "")

            msg = 'One or more workloads have exceeded the maximum cluster limits.'
            msg += '<br />Recommendation: Split the following workloads in half.'
            msg += '<br />Workloads: '
            msg += workload
            error_code = 18

        elif 'CSV format' in message:
            msg = 'CSV data is not in correct format or data is not present.'
            error_code = 22

        elif 'Unknown_WL' in message:
            msg = 'Unknown Workload type was passed to the sizing function.'
            error_code = 23

        elif 'No_Usable_Part' in message:
            cap_type = parsed_exception[1]
            msg = 'No usable ' + cap_type + ' due to filters. Please check the filters.'
            error_code = 24

        elif 'M10_1TB_Limit' in message:

            workload = str(parsed_exception[1][1:-1]).replace("'", "")

            msg = 'RAM limit for nodes exceeded due to 1 TB limit on M10 GPU Cards.'
            msg += '<br />Please split the workloads, or change the filters.'
            msg += '<br />Workloads: '
            msg += workload
            error_code = 25

        elif 'CPU_RAM_Limit' in message:

            workload = str(parsed_exception[1][1:-1]).replace("'", "")

            msg = 'RAM limit for nodes exceeded due to the Memory limit of selected CPUs'
            msg += '<br />Please split the workloads, or change the filters.'
            msg += '<br />Workloads: '
            msg += workload
            error_code = 25

        elif '512_MB_Unsupported' in message:
            msg = '512 MB VRAM Desktops unsupported for Pascal Series GPUs.'
            msg += '<br />Please change the filters to include a non-Pascal Series GPU.'
            error_code = 26

        elif 'Data_Issue' in message:
            msg = 'Potential data issue in the database has been detected.'
            msg += '<br />Please contact the HxSizer team to triage the issue.'
            error_code = 40

        elif 'Unauthorized Access' in message:
            msg = 'Unauthorized Access'
            error_code = 0

        elif 'No Hyperflex nodes' in message:
            msg = parsed_exception[0]
            error_code = 6

        elif 'Unable to find a CPU' in message:
            msg = parsed_exception[0]
            error_code = 7

        elif 'SPLUNK_AF_Nodes' in message:
            msg = 'No All-Flash nodes found, with a Splunk workload added.'
            error_code = 11

        elif "DR_CLUSTER_LIMIT" in message:
            msg = parsed_exception[1]
            error_code = 2

        elif "DEBUG_INFO" in message:
            msg = parsed_exception[1]
            error_code = 42

        elif "SSD parts unavailable" in message:
            msg = "Available SSD parts do not support the required throughput"
            error_code = 43

        elif "AIML DS" in message:
            msg = message.split('|')
            workload = str(msg[2][1:-1]).replace("'", "")

            msg = "Number of Data-Scientists with Video-Serious requirement has exceeded maximum possible compute " \
                  "nodes i.e. " + msg[1]
            msg += "<br />Please split the workloads"
            msg += '<br />Workloads: '
            msg += workload
            error_code = 44

        elif "GPU_Single_Cluster" in message:
            msg = "None of the GPUs support all workloads\' frame buffer requirements."
            msg += "<br />Hence placement in a single cluster isn't possible. Please change the filters."
            error_code = 45

        elif "ROBO_WL_RF3" in message:
            msg = "No Edge nodes have been chosen to support Edge workloads with RF3. Please change the filters."
            error_code = 45

        else:
            logger.error(message)
            msg = 'Unknown Error. Check Server Logs.'
            error_code = 0

        if msg:
            scen_id = ""
            if len(message.split('|')) > 1:
                scen_id = message.split('|')[-2]
            logger.error('|%s| %s |%s' %(scen_id,msg,error_code))
            logger.info('|%s| Finish Sizing' %(scen_id))
            return msg

        return None


class RXException(Exception):
    def __init__(self, error):
        return_msg = self.process_exception(error)
        super(RXException, self).__init__(return_msg)

    @staticmethod
    def process_exception(error):

        parsed_exception = error.split('|')
        message = ''
        if 'wrong wl type' in parsed_exception[0]:
            base_string = "Currently selected node doesn't support the following workloads: "
            workloads = str(parsed_exception[1][1:-1])
            message = base_string + workloads.replace("'", "")

        if 'wrong robo wl type' in parsed_exception[0]:
            base_string = "Currently selected node doesn't support the following RF3 workloads: "
            workloads = str(parsed_exception[1][1:-1])
            message = base_string + workloads.replace("'", "")

        if 'wrong min node' in parsed_exception[0]:
            base_string = "Minimum 3 Hyperflex Edge nodes are required to support the following RF3 workloads: "
            workloads = str(parsed_exception[1][1:-1])
            message = base_string + workloads.replace("'", "")

        if 'wrong hypervisor' in parsed_exception[0]:
            base_string = "Currently selected hypervisor doesn't support the following workloads: "
            workloads = str(parsed_exception[1][1:-1])
            message = base_string + workloads.replace("'", "")

        if 'wrong wl lff' in parsed_exception[0]:
            base_string = "Currently selected LFF node doesn't support the following workloads: "
            workloads = str(parsed_exception[1][1:-1])
            message = base_string + workloads.replace("'", "")

        elif 'wrong cluster type' in parsed_exception[0]:
            base_string = "Workloads entered cannot be placed into one cluster.<br />Standard Clustering formats are: "
            supported_clusters = str(parsed_exception[1][1:-1])
            message = base_string + supported_clusters.replace("'", "")

        elif 'too large workload' in parsed_exception[0]:
            base_string = "Following workload requirements cannot be satisfied by the current node configuration: "
            resources_exceeded = str(parsed_exception[1][1:-1])
            message = base_string + resources_exceeded.replace("'", "")

        elif 'replication' in parsed_exception[0]:
            message = "Replication is not allowed on a fixed Node Configuration."

        elif 'epic' in parsed_exception[0]:
            message = "Epic workloads are not allowed on a fixed Node Configuration."

        elif 'stretched' in parsed_exception[0]:
            base_string = "Stretched workloads aren't supported in Fixed Config Sizing: "
            stretched_wl = str(parsed_exception[1][1:-1])
            message = base_string + stretched_wl.replace("'", "")

        elif 'gpu' in parsed_exception[0]:
            message = "GPU workloads currently aren't supported in Fixed Config Sizing."

        elif 'threshold' in parsed_exception[0]:
            base_string = "Following workload requirements exceed the best practice reserves: "
            threshold_exceeded = str(parsed_exception[1][1:-1])
            message = base_string + threshold_exceeded.replace("'", "")

        elif 'minimum node' in parsed_exception[0]:
            message = "Clusters with " + parsed_exception[1] + " and Performance Headroom of 2 must have a minimum of "\
                      + parsed_exception[2] + " HyperFlex Nodes. Workload requirements for infrastructure ("+ parsed_exception[1] + " and N+2) do not match the fixed cluster settings"

        elif 'warning' in parsed_exception[0]:
            message = 'Warning: Compute Nodes will be lost on node failure.'

        elif 'deprecated' in parsed_exception[0]:
            message = "The node " + parsed_exception[1] + " has been EOLed. Please select a different node."

        elif 'renamed node' in parsed_exception[0]:
            message = "The node " + parsed_exception[1] + " does not exist in the database. " \
                                                          "Please change the node type in the Customize Tab"
        elif 'sizingcalculator' in parsed_exception[0]:
            message = 'Warning: Failed to get Sizing Calculator Result.'

        elif 'renamed part' in parsed_exception[0]:
            message = "The Disk/Cache does not exist in the database. Please change the filters in the Customize Tab"
            
        elif 'Large_Vm_Limit' in parsed_exception[0]:
            message = "One or more workload requirement has large CPU/RAM requirement which cannot be satisfied by the current node configuration."

        elif 'CPU_RAM_Limit' in parsed_exception[0]:
            ram_limit  = str(parsed_exception[1])
            message = 'RAM limit for nodes exceeded due to the Memory limit of selected CPUs. RAM limit is =' + ram_limit
            message += '<br />Please split the workloads, or change the filters.'

        elif 'home_directory_AF' in parsed_exception[0]:
            message = "Home Directories are currently supported only on All-Flash nodes. Please change the filters"
        
        elif 'home_directory_hyperv' in parsed_exception[0]:
            message = "Home Directories are currently not supported with Hyper-V. Please change the filters"

        if message:
            return message
