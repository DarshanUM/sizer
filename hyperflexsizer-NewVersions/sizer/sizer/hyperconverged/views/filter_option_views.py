from copy import deepcopy
from utils.baseview import BaseView
from collections import defaultdict

from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from hyperconverged.solver.sizing import HyperConvergedSizer

from hyperconverged.models import Node, Part
from base_sizer.solver.attrib import BaseConstants
from hyperconverged.solver.attrib import HyperConstants
from hyperconverged.strings import ROBO_WL, AF_WL, HYPER_WL, VEEAM_WL


class RevSizerBaseFilter(object):

    @staticmethod
    def filter_node_attrib(requirements):
        """
        method is used to fetch nodes from DB and construct dictionaries with info based on requirements list.
        it is used by reverse sizer and bench sheet calculator.
        :param requirements:
        :return:
        """
        node_query = Node.objects.filter(status=True).exclude(node_json__contains="compute").order_by("sort_index")

        if "compute_nodes" in requirements:

            compute_node_query = Node.objects.filter(node_json__contains="compute", status=True).order_by("name")
            compute_parts = dict()
            compute_dict_list = list()

            for compute_node in compute_node_query:

                node_json = compute_node.node_json
                compute_dict = dict()
                compute_dict["name"] = compute_node.name

                for key in ["cpu_options", "ram_options", "node_type"]:

                    if key == "cpu_options":

                        compute_dict[key] = list()

                        for cpu in node_json["cpu_options"]:

                            # if 'UCS' in compute_dict["name"]:
                            #    cpu = cpu[:-5]

                            if cpu not in compute_parts:
                                compute_parts[cpu] = Part.objects.get(name=cpu)

                            compute_dict[key].append([cpu, compute_parts[cpu].part_json[BaseConstants.CAPACITY],
                                                      compute_parts[cpu].part_json[HyperConstants.FREQUENCY],
                                                      compute_parts[cpu].part_json[HyperConstants.RAM_LIMIT],
                                                      compute_parts[cpu].part_json[HyperConstants.SPECLNT]])
                    elif key == "node_type":

                        compute_dict[key] = node_json["type"]

                    elif key == "ram_options":

                        compute_dict[key] = list()

                        for ram_slot in node_json["ram_slots"]:

                            for ram_part in node_json[key]:

                                # if 'UCS' in compute_dict["name"]:
                                #    ram_part = ram_part[:-5]

                                if ram_part not in compute_parts:
                                    compute_parts[ram_part] = Part.objects.get(name=ram_part)

                                if '[CUSTOM]' in ram_part:

                                    if ram_slot != 12:
                                        continue

                                    split_rams = compute_parts[ram_part].part_json['split_name'].split('#')

                                    for index, sub_ram_part in enumerate(split_rams):

                                        if sub_ram_part not in compute_parts:
                                            compute_parts[sub_ram_part] = Part.objects.get(name=sub_ram_part)

                                        split_rams[index] = \
                                            compute_parts[sub_ram_part].part_json[BaseConstants.CAPACITY]

                                elif '[CUSTOM_6SLOT]' in ram_part:

                                    if ram_slot != 12:
                                        continue

                                    split_rams = compute_parts[ram_part].part_json['split_name'].split('#')

                                    for index, sub_ram_part in enumerate(split_rams):

                                        if sub_ram_part not in compute_parts:
                                            compute_parts[sub_ram_part] = Part.objects.get(name=sub_ram_part)

                                        split_rams[index] = \
                                            compute_parts[sub_ram_part].part_json[BaseConstants.CAPACITY]

                                    compute_dict[key].append([ram_part, 6, split_rams])
                                    continue

                                else:

                                    split_rams = [compute_parts[ram_part].part_json[BaseConstants.CAPACITY]]

                                compute_dict[key].append([ram_part, ram_slot, split_rams])

                compute_dict_list.append(compute_dict)

        response = dict()
        node_parts = dict()
        response['node_details'] = list()

        for node in node_query:

            node_json = node.node_json

            if node_json[BaseConstants.SUBTYPE] in [HyperConstants.EPIC_NODE, HyperConstants.AIML_NODE]:
                continue

            detail_dict = dict()
            detail_dict["node_name"] = node.name

            for key in requirements:

                if key == "node_type":

                    detail_dict[key] = node_json["type"]

                elif key == 'hercules_avail':

                    detail_dict[key] = node.hercules_avail

                elif key == 'hx_boost_avail':

                    detail_dict[key] = node.hx_boost_avail

                elif key == 'hypervisor':

                    if 'SED' in node.name or '[NVME]' in node.name or \
                            node_json[BaseConstants.SUBTYPE] in ['robo', 'veeam', 'robo_allflash', 'allnvme',
                                                                 'robo_two_node', 'robo_allflash_two_node',
                                                                 'robo_240', 'robo_af_240']:
                        detail_dict[key] = ['esxi']
                    else:
                        detail_dict[key] = ['hyperv', 'esxi']

                elif key == "rf":

                    detail_dict[key] = [2] if node_json[BaseConstants.SUBTYPE] in \
                                              [HyperConstants.ROBO_TWO_NODE, HyperConstants.AF_ROBO_TWO_NODE] else [2, 3]

                elif key == "cpu_options":

                    cascade_cpu_list = list()
                    sky_cpu_list = list()
                    detail_dict[key] = list()

                    for cpu in node_json[key]:

                        if cpu not in node_parts:
                            node_parts[cpu] = Part.objects.get(name=cpu)

                        if 'Cascade' in cpu:

                            cpu_list = cascade_cpu_list

                        else:

                            cpu_list = sky_cpu_list

                        cpu_list.append([cpu,
                                         node_parts[cpu].part_json[BaseConstants.CAPACITY],
                                         node_parts[cpu].part_json[HyperConstants.FREQUENCY],
                                         node_parts[cpu].part_json[HyperConstants.RAM_LIMIT],
                                         node_parts[cpu].part_json[HyperConstants.SPECLNT]])

                    cascade_cpu_list.sort(key=lambda x: x[0:4])
                    sky_cpu_list.sort(key=lambda x: x[0:4])

                    detail_dict[key] = cascade_cpu_list + sky_cpu_list

                elif key == "ram_options":

                    detail_dict[key] = list()

                    for ram_slot in node_json["ram_slots"]:

                        for ram_part in node_json[key]:

                            if ram_part not in node_parts:
                                node_parts[ram_part] = Part.objects.get(name=ram_part)

                            if '[CUSTOM]' in ram_part:

                                if ram_slot != 12:
                                    continue

                                split_rams = node_parts[ram_part].part_json['split_name'].split('#')

                                for index, sub_ram_part in enumerate(split_rams):

                                    if sub_ram_part not in node_parts:
                                        node_parts[sub_ram_part] = Part.objects.get(name=sub_ram_part)

                                    split_rams[index] = node_parts[sub_ram_part].part_json[BaseConstants.CAPACITY]

                            elif '[CUSTOM_6SLOT]' in ram_part:

                                if ram_slot != 12:
                                    continue

                                split_rams = node_parts[ram_part].part_json['split_name'].split('#')

                                for index, sub_ram_part in enumerate(split_rams):

                                    if sub_ram_part not in node_parts:
                                        node_parts[sub_ram_part] = Part.objects.get(name=sub_ram_part)

                                    split_rams[index] = node_parts[sub_ram_part].part_json[BaseConstants.CAPACITY]

                                detail_dict[key].append([ram_part, 6, split_rams])
                                continue

                            else:

                                split_rams = [node_parts[ram_part].part_json[BaseConstants.CAPACITY]]

                            detail_dict[key].append([ram_part, ram_slot, split_rams])

                    detail_dict[key].sort(key=lambda x: x[1] * sum(x[2]))

                elif key == "hdd_options":

                    detail_dict[key] = list()

                    cluster_limits = dict.fromkeys(detail_dict['hypervisor'])

                    for hypervisor in cluster_limits:

                        min_cluster = HyperConvergedSizer.get_minimum_size(node_json[BaseConstants.SUBTYPE], 0,
                                                                           HyperConstants.NORMAL, 2)

                        max_cluster = \
                            HyperConvergedSizer.get_max_cluster_value(node_json[BaseConstants.SUBTYPE],
                                                                      node_json[HyperConstants.DISK_CAGE], hypervisor,
                                                                      HyperConstants.NORMAL)

                        cluster_limits[hypervisor] = list(range(min_cluster, max_cluster + 1))

                    for hdd_part in node_json[key]:

                        if hdd_part not in node_parts:
                            node_parts[hdd_part] = Part.objects.get(name=hdd_part)

                        hdd_name = node_parts[hdd_part].name

                        if hdd_name != '12TB [CAP][HDD-LFF][M5][1]':
                            avail_hypervisors = detail_dict['hypervisor']
                        else:
                            avail_hypervisors = ['esxi']

                        hdd_cap = node_parts[hdd_part].part_json[BaseConstants.CAPACITY]

                        if HyperConstants.CUSTOM not in node_parts[hdd_part].part_json:

                            hdd_details = [hdd_cap, hdd_name, list(range(min(node_json['hdd_slots']),
                                                                    max(node_json['hdd_slots']) + 1)),
                                           cluster_limits, avail_hypervisors]

                        else:

                            custom_params = node_parts[hdd_part].part_json[HyperConstants.CUSTOM]

                            custom_slots = custom_params['hdd_slots']
                            custom_subtype = custom_params[BaseConstants.SUBTYPE]

                            custom_max = dict()

                            for hypervisor in avail_hypervisors:

                                custom_max[hypervisor] = \
                                    HyperConvergedSizer.get_max_cluster_value(custom_subtype,
                                                                              node_json[HyperConstants.DISK_CAGE],
                                                                              hypervisor, HyperConstants.NORMAL)

                            custom_limits = \
                                {hypervisor: [i for i in cluster_limits[hypervisor] if i <= custom_max[hypervisor]]
                                 for hypervisor in avail_hypervisors}

                            hdd_details = [hdd_cap, hdd_name, list(range(min(custom_slots), max(custom_slots) + 1)),
                                           custom_limits, avail_hypervisors]

                        detail_dict[key].append(hdd_details)
                        detail_dict[key].sort(key=lambda x: x[0])

                elif key == "compute_nodes":

                    detail_dict[key] = list()

                    if node_json[BaseConstants.SUBTYPE] in ['robo', 'robo_allflash', 'robo_240', 'robo_af_240',
                                                            'robo_two_node', 'robo_allflash_two_node']:
                        continue

                    for compute_dict in compute_dict_list:

                        cpu_options = \
                            list(filter(lambda x: x in compute_dict['cpu_options'], detail_dict['cpu_options']))

                        ram_options = \
                            list(filter(lambda x: x in compute_dict['ram_options'], detail_dict['ram_options']))

                        if cpu_options and ram_options and compute_dict["node_type"] == node_json["type"]:

                            supported_compute = deepcopy(compute_dict)
                            supported_compute["cpu_options"] = cpu_options
                            supported_compute["ram_options"] = ram_options
                            detail_dict[key].append(supported_compute)

                elif key == "ssd_options":

                    detail_dict[key] = list()

                    for ssd_part in node_json["ssd_options"]:
                        if ssd_part not in node_parts:
                            node_parts[ssd_part] = Part.objects.get(name=ssd_part)

                        ssd_part_cap = node_parts[ssd_part].part_json[HyperConstants.OUTPUT_CAPACITY]
                        ssd_part_name = node_parts[ssd_part].name

                        if '40G-10G' in ssd_part_name:
                            modular_lan = ' [10G/40G]'
                        elif '40G' in ssd_part_name:
                            modular_lan = ' [40G]'
                        elif '10G' in ssd_part_name:
                            modular_lan = ' [10G]'
                        elif 'DUAL' in ssd_part_name:
                            modular_lan = ' [Dual Switch]'
                        else:
                            modular_lan = ''

                        disk_type = ''

                        if "COLDSTREAM" in ssd_part_name:
                            disk_type = ' [Optane]'
                        else:
                            for disk in ["NVMe", "SATA", "SAS"]:
                                if disk in node_parts[ssd_part_name].part_json['description']:
                                    disk_type = ' [' + disk + ']'
                                    break

                        ssd_part_cap = str(ssd_part_cap) + disk_type + modular_lan

                        detail_dict[key].append([ssd_part_cap, ssd_part_name])

                    detail_dict[key].sort(key=lambda x: node_parts[x[1]].part_json[HyperConstants.OUTPUT_CAPACITY])

                elif key == 'workload_options':

                    detail_dict[key] = list()

                    if "robo" in node_json[BaseConstants.SUBTYPE]:
                        detail_dict[key] = ROBO_WL
                    elif "all-flash" in node_json[BaseConstants.SUBTYPE]:
                        detail_dict[key] = AF_WL
                    elif "hyperconverged" in node_json[BaseConstants.SUBTYPE]:
                        detail_dict[key] = HYPER_WL
                    elif "veeam" in node_json[BaseConstants.SUBTYPE]:
                        detail_dict[key] = VEEAM_WL
                    elif "allnvme" in node_json[BaseConstants.SUBTYPE]:
                        detail_dict[key] = AF_WL
                    elif "lff_12tb" in node_json[BaseConstants.SUBTYPE]:
                        detail_dict[key] = AF_WL

                else:

                    raise Exception("Not yet implemented")

            response['node_details'].append(detail_dict)

        response['excluded_wls'] = {'esxi': list(),
                                    'hyperv': ['SPLUNK', 'VEEAM', 'ROBO']}

        return response


class SizerFilter(BaseView):

    """Get Filter options for the output."""
    """ Skylak CPU and RAM are deprecated from 10Mar 2021"""

    @staticmethod
    def get(request, format=None):

        types_of_server_nodes = ["M5_server", "M6_server"]
        # Commented as this query is failing in Production Using "speclnt" instead
        # qry_object = Part.objects.filter(part_json__contains='"type": "CPU"').exclude(name__contains="[UCS]").order_by(
        #     "name")
        #qry_object = Part.objects.filter(part_json__contains='speclnt', status= True).exclude(name__contains="[UCS]").order_by(
         #   "name")

        qry_object = Part.objects.filter(part_json__contains='speclnt', status=True).order_by("name")

        '''below dictionary has been created to map server types with corresponding CPU.
        the cpu addition is based on whether we have the string 'M5' in the server_type 
        attribute of part_json. [0:-7] is written in order to remove '_server' from the string'''
        server_cpu_dict = dict()
        for server_type in types_of_server_nodes:
            server_cpu_dict[server_type] = qry_object.filter(part_json__contains=server_type[0:-7])

        json = defaultdict(list)

        # coldstream = optane
        base_tags = ["bundle", "cto", "all-flash", "hybrid", "sed", "ssd-sed", "fips", "nvme", "esxi", "hyperv",
                     'coldstream', 'lff', 'recommended', "cascade", "icelake", "hercules_avail", "hx_boost_avail",
                     "all-nvme", "single_cpu"] + types_of_server_nodes

        reference_tag = lambda input_tag: deepcopy(input_tag)

        # HyperFlex node filters -M5
        for node_name in HyperConstants.base_node_list:

            tags = reference_tag(base_tags)

            if node_name not in ['HXAF-240', 'HX240C', 'HX240C [LFF]']:
                tags.remove('hercules_avail')

            if node_name not in ['HXAF-220', 'HXAF-240', 'HXAF-220 [NVME]']:
                tags.remove('hx_boost_avail')

            if 'NVME' not in node_name:
                tags.remove('all-nvme')

            if node_name not in ['HXAF-220 [1 CPU]', 'HX220C [1 CPU]']:
                tags.remove('single_cpu')

            if 'AF' not in node_name:
                tags.remove('all-flash')

            if 'SP' not in node_name:
                tags.remove('bundle')

                if 'LFF' in node_name:
                    tags.remove('sed')
                    tags.remove("nvme")
                else:
                    tags.remove('lff')
            else:
                tags.remove('recommended')
                tags.remove('cto')

                if 'LFF' not in node_name:
                    tags.remove('lff')

            if 'NVME' in node_name:
                tags.remove("sed")
                tags.remove('fips')

            if node_name in ['HXAF-E-220', 'HX-E-220', 'HXAF-240 [SD EDGE]', 'HX240C [SD EDGE]',
                             'HXAF-E-240', 'HX-E-240']:

                tags.remove("sed")
                tags.remove("nvme")
                tags.remove('hyperv')

            if node_name not in ['HXAF-220', 'HXAF-240', 'HXAF-220 [NVME]']:
                tags.remove('fips')

            if node_name not in ['HXAF-220', 'HXAF-240', 'HXAF-220 [NVME]', 'HXAF-SP-220', 'HXAF-SP-240']:
                tags.remove('coldstream')

            tags.remove('M6_server')
            tags.remove('icelake')

            node_json = dict()
            node_json['name'] = node_name
            node_json['tags'] = tags
            json["Node_Type"].append(node_json)

        # Compute node filters - M5
        for node_name in ["HX-B200", "HX-C220", "HX-C240", "HX-C480"]:

            tags = reference_tag(base_tags)
            node_json = dict()

            if node_name in ["HX-B200", "HX-C220", "HX-C240", "HX-C480"]:
                tags.remove('bundle')

            tags.remove('M6_server')
            tags.remove('icelake')

            node_json['name'] = node_name
            node_json['tags'] = tags
            json['Compute_Type'].append(node_json)

        # HyperFlex node filters -M6
        for node_name in HyperConstants.base_m6node_list:

            tags = reference_tag(base_tags)

            # if node_name not in ['HXAF-240', 'HX240C', 'HX240C [LFF]']:
            #    tags.remove('hercules_avail')

            # if node_name not in ['HXAF-220', 'HXAF-240', 'HXAF-220 [NVME]']:
            #    tags.remove('hx_boost_avail')

            if 'NVME' not in node_name:
                tags.remove('all-nvme')

            # if node_name not in ['HXAF-220 [1 CPU]', 'HX220C [1 CPU]']:
            #    tags.remove('single_cpu')

            if 'AF' not in node_name:
                tags.remove('all-flash')

            if 'SP' not in node_name:
                tags.remove('bundle')

                if 'LFF' in node_name:
                    tags.remove('sed')
                    tags.remove("nvme")
                else:
                    tags.remove('lff')
            else:
                tags.remove('recommended')
                tags.remove('cto')

            if 'NVME' in node_name:
                tags.remove("sed")
                tags.remove('fips')

            if node_name in ['HXAF-E-220', 'HX-E-220', 'HXAF-E-240', 'HX-E-240']:
                tags.remove("sed")
                tags.remove("nvme")
                tags.remove('hyperv')

            if node_name not in ['HXAF-220', 'HXAF-240', 'HXAF-220 [NVME]']:
                tags.remove('coldstream')

            tags.remove('M5_server')
            tags.remove('icelake')

            node_json = dict()
            node_json['name'] = node_name
            node_json['tags'] = tags
            json["Node_Type"].append(node_json)

        # Compute node filters -M6
        for node_name in ["UCSC-C220", "UCSC-C240"]:

            tags = reference_tag(base_tags)
            node_json = dict()

            if 'SP' not in node_name:
                tags.remove('bundle')

            tags.remove('M5_server')
            tags.remove('cascade')

            node_json['name'] = node_name
            node_json['tags'] = tags
            json['Compute_Type'].append(node_json)

        # CPU filters - M5 and M6
        clock_tags = defaultdict(set)

        cascade_cpu_list = list()
        icelake_cpu_list = list()

        for cpu_server_type, list_of_cpu in server_cpu_dict.items():

            server_tags_removal = list(server_cpu_dict.keys())
            # the below line ensures that the corresponding server type tag is retained in the tags list
            server_tags_removal.remove(cpu_server_type)

            for cpu in list_of_cpu:

                tags = reference_tag(base_tags)

                cpu.name = cpu.name.split()[0]
                for tag in server_tags_removal:
                    tags.remove(tag)

                if 'icelake' in cpu.part_json['filter_tag']:
                    tags.remove('cascade')
                    tags.remove('recommended')
                else:
                    tags.remove('icelake')

                    if 'recommended' not in cpu.part_json['filter_tag']:
                        tags.remove('recommended')

                # the below condition is a special case that requires few CPU to not appear in bundle only option
                if cpu_server_type == 'M5_server' and cpu.name not in ['3106', '4114', '6130', '6140', '6148',
                                                                       '4214R', '5220R', '6240R', '4210R', '6248R']:
                    tags.remove('bundle')

                # below condition is for CPU which support single CPU for HX-220
                if cpu.name not in ["4214R", "5218R", "5220R", "6226R", "6230R", "6238R", "6240R", "6314U", "8351N"]:
                    tags.remove('single_cpu')

                if cpu_server_type == 'M6_server':
                    tags.remove('bundle')

                part_json = dict()
                cpu_clock = '%.1f' % float(cpu.part_json['frequency'])
                cpu_cores = cpu.part_json['capacity']
                part_json['name'] = '%s (%s, %s)' % (cpu.name, cpu_cores, cpu_clock)
                part_json['clock_speed'] = cpu_clock
                part_json['tags'] = tags
                clock_tags[cpu_clock] = clock_tags[cpu_clock].union(tags)

                if 'cascade' in cpu.part_json['filter_tag']:
                    cascade_cpu_list.append(part_json)
                if 'icelake' in cpu.part_json['filter_tag']:
                    icelake_cpu_list.append(part_json)

        cascade_cpu_list.sort(key=lambda x: x['name'].split()[0])
        icelake_cpu_list.sort(key=lambda x: x['name'].split()[0])
        json['CPU_Type'] = cascade_cpu_list + icelake_cpu_list

        clock_tags = [(clock_speed, tags_union) for clock_speed, tags_union in clock_tags.items()]

        # Clock filters - M5 and M6
        for clock_speed, tags_union in sorted(clock_tags, key=lambda x: x[0]):

            part_json = dict()
            part_json['name'] = clock_speed
            part_json['tags'] = list(tags_union)
            json['Clock'].append(part_json)

        # RAM slot filters - M5
        for ram_slot_number in [8, 12, 16, 24]:

            tags = reference_tag(base_tags)
            part_json = dict()
            tags.remove('icelake')
            tags.remove('M6_server')
            part_json['name'] = ram_slot_number
            part_json['tags'] = tags
            json["RAM_Slots"].append(part_json)

        # RAM slot filters - M6
        for ram_slot_number in [8, 12, 16, 24]:
            tags = reference_tag(base_tags)
            tags.remove('M5_server')
            tags.remove('bundle')
            tags.remove('cascade')
            part_json = dict()
            part_json['name'] = ram_slot_number
            part_json['tags'] = tags
            json["RAM_Slots"].append(part_json)

        # RAM filters - M5
        for part_name in ["16GiB DDR4", "32GiB DDR4", "16GiB+32GiB DDR4", "64GiB DDR4", "32GiB+64GiB DDR4",
                          "128GiB DDR4", "64GiB+128GiB DDR4"]:

            tags = reference_tag(base_tags)

            if part_name in ['16GiB+32GiB DDR4', '32GiB+64GiB DDR4', '64GiB+128GiB DDR4']:
                tags.remove('bundle')

            tags.remove('M6_server')
            tags.remove('icelake')

            part_json = dict()
            part_json['name'] = part_name
            part_json['tags'] = tags
            json["RAM_Options"].append(part_json)

        # RAM filters - M6
        for part_name in ["16GiB DDR4", "32GiB DDR4", "64GiB DDR4", "128GiB DDR4"]:
            tags = reference_tag(base_tags)
            tags.remove('M5_server')
            tags.remove('bundle')
            tags.remove('cascade')
            part_json = dict()
            part_json['name'] = part_name
            part_json['tags'] = tags
            json["RAM_Options"].append(part_json)

        # Storage Disk filters - M5
        for disk_option in ["800GB [SSD]", "960GB [SSD]", "1TB [NVMe]", "1.2TB [HDD]", "1.8TB [HDD]", "2.4TB [HDD]",
                            "3.8TB [SSD]", "4TB [NVMe]", "6TB [HDD]", "7.6TB [SSD]", "8TB [HDD]", "8TB [NVMe]",
                            "12TB [HDD]", "1.9TB [SSD]"]:

            tags = reference_tag(base_tags)

            if disk_option not in ["6TB [HDD]", "8TB [HDD]", "12TB [HDD]"]:
                tags.remove('lff')

            if disk_option == "12TB [HDD]":
                tags.remove('hyperv')

            if disk_option in ["6TB [HDD]", "12TB [HDD]", "800GB [SSD]"]:
                tags.remove('bundle')

            if 'HDD' in disk_option:
                tags.remove('all-flash')

            if disk_option not in ['1.2TB [HDD]', '800GB [SSD]', '960GB [SSD]', '3.8TB [SSD]', "7.6TB [SSD]",
                                   '2.4TB [HDD]', '1.9TB [SSD]']:
                tags.remove('sed')

            if disk_option not in ['960GB [SSD]', '3.8TB [SSD]', "7.6TB [SSD]"]:
                tags.remove('fips')

            if 'NVMe' not in disk_option:
                tags.remove('nvme')
                tags.remove('all-nvme')

            tags.remove('M6_server')
            tags.remove('icelake')

            part_json = dict()
            part_json['name'] = disk_option
            part_json['tags'] = tags
            json["Disk_Options"].append(part_json)

        # Storage Disk filters - M6
        for disk_option in ["1.2TB [HDD]", "1.8TB [HDD]", "2.4TB [HDD]", "16TB [HDD]", "12TB [HDD]", "8TB [HDD]",
                            "6TB [HDD]", "960GB [SSD]", "1.9TB [SSD]", "3.8TB [SSD]", "7.6TB [SSD]", "3.8TB [NVMe]",
                            "7.6TB [NVMe]", "1.9TB [NVMe]"]:

            tags = reference_tag(base_tags)

            if disk_option not in ["16TB [HDD]", "12TB [HDD]", "8TB [HDD]", "6TB [HDD]"]:
                tags.remove('lff')

            tags.remove('bundle')

            if 'HDD' in disk_option:
                tags.remove('all-flash')

            if disk_option not in ["1.2TB [HDD]", "2.4TB [HDD]", "960GB [SSD]", "3.8TB [SSD]", "7.6TB [SSD]"]:
                tags.remove('sed')

            if 'NVMe' not in disk_option:
                tags.remove('nvme')
                tags.remove('all-nvme')

            tags.remove('M5_server')
            tags.remove('cascade')

            part_json = dict()
            part_json['name'] = disk_option
            part_json['tags'] = tags
            json["Disk_Options"].append(part_json)

        # Cache Disk filters - M5
        for disk_option in ["375GB [Optane]", "480GB", "800GB", "1.6TB", "3.2TB"]:

            tags = reference_tag(base_tags)

            if disk_option != '3.2TB':
                tags.remove('lff')

            if disk_option != '375GB [Optane]':
                tags.remove('coldstream')

            if disk_option not in ['375GB [Optane]', '1.6TB']:
                tags.remove('nvme')
                tags.remove('all-nvme')
                tags.remove('single_cpu')

            if disk_option not in ['800GB', '1.6TB']:
                tags.remove('ssd-sed')
                tags.remove('sed')

            if disk_option != '800GB':
                tags.remove('fips')

            tags.remove('M6_server')
            tags.remove('icelake')

            part_json = dict()
            part_json['name'] = disk_option
            part_json['tags'] = tags
            json["Cache_Options"].append(part_json)

        # Cache Disk filters - M6
        for disk_option in ["480GB", "800GB", "1.6TB", "3.2TB", "375GB [Optane]"]:

            tags = reference_tag(base_tags)

            if disk_option != '3.2TB':
                tags.remove('lff')

            if disk_option != '375GB [Optane]':
                tags.remove('coldstream')

            if disk_option in ['375GB [Optane]']:
                tags.remove('nvme')
                tags.remove('all-nvme')
                tags.remove('single_cpu')

            if disk_option not in ["800GB", "1.6TB"]:
                tags.remove('ssd-sed')
                tags.remove('sed')

            tags.remove('fips')

            tags.remove('M5_server')
            tags.remove('cascade')

            part_json = dict()
            part_json['name'] = disk_option
            part_json['tags'] = tags
            json["Cache_Options"].append(part_json)

        # GPU filters - M5
        for gpu_option in ["M10", "P40", "7150X2", "V100", "T4", "RTX6000", "RTX8000"]:

            tags = reference_tag(base_tags)
            tags.remove('M6_server')
            tags.remove('icelake')
            gpu_json = dict()
            gpu_json['name'] = gpu_option
            gpu_json['tags'] = tags
            json['GPU_Type'].append(gpu_json)

        # GPU filters - M6
        for gpu_option in ["A10", "A100", "T4"]:
            tags = reference_tag(base_tags)
            tags.remove('M5_server')
            tags.remove('bundle')
            tags.remove('cascade')
            gpu_json = dict()
            gpu_json['name'] = gpu_option
            gpu_json['tags'] = tags
            json['GPU_Type'].append(gpu_json)

        for riser_option in ["Storage", "PCI-E"]:
            tags = reference_tag(base_tags)
            tags.remove('M5_server')
            tags.remove('cascade')
            riser_json = dict()
            riser_json['name'] = riser_option
            riser_json['tags'] = tags
            json['Riser_Options'].append(riser_json)

        return Response(json)
