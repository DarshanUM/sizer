from math import ceil
from base_sizer.solver.attrib import BaseConstants
from .attrib import HyperConstants


class SeedNode(object):
    @staticmethod
    def cpu_parts_price_calculation(key, model_details, parts_object, node, price_factor):

        node, model_number = update_part_name_price_details(key, model_details, parts_object, node, price_factor)

        node.attrib[BaseConstants.CORES_PER_CPU] = \
            node.attrib[BaseConstants.CORES_PER_CPU] * node.attrib[HyperConstants.SPECLNT]

        node.attrib[BaseConstants.CPU_CNT] = 2

        cpu_price = parts_object.get_part_attrib(model_number, price_factor)

        cpu_total_price = calculate_total_part_price(cpu_price, node.attrib[BaseConstants.CPU_CNT])

        return node, cpu_total_price

    @staticmethod
    def ram_parts_price_calculation(key, model_details, parts_object, node, price_factor, slots):

        node, model_number = update_part_name_price_details(key, model_details, parts_object, node, price_factor)

        node.attrib[BaseConstants.MIN_SLOTS] = min(slots)

        if not model_details[key][2]:
            ram_per_server = node.attrib[BaseConstants.MIN_SLOTS]
        else:
            ram_per_server = model_details[key][1] / model_details[key][2]

        node.attrib[BaseConstants.RAM_SLOTS] = min(ram_per_server, max(slots))

        if node.attrib[BaseConstants.RAM_SLOTS] < node.attrib[BaseConstants.MIN_SLOTS]:
            node.attrib[BaseConstants.RAM_SLOTS] = node.attrib[BaseConstants.MIN_SLOTS]

        if '[CUSTOM]' in model_details[key][0]:
            node.attrib[BaseConstants.RAM_SLOTS] = 12
        elif '[CUSTOM_6SLOT]' in model_details[key][0]:
            node.attrib[BaseConstants.RAM_SLOTS] = 6

        ram_price = parts_object.get_part_attrib(model_number, price_factor)

        ram_total_price = calculate_total_part_price(ram_price, node.attrib[BaseConstants.RAM_SLOTS])

        return node, ram_total_price

    @staticmethod
    def hdd_parts_price_calculation(key, model_details, parts_object, node, price_factor, slots):

        node, model_number = update_part_name_price_details(key, model_details, parts_object, node, price_factor)

        if node.attrib[BaseConstants.SUBTYPE] == HyperConstants.COMPUTE:
            node.attrib[BaseConstants.HDD_SLOTS] = 0
            node.attrib[BaseConstants.MIN_HDD_SLOTS] = 0
        else:
            hdd_per_server = int(ceil(model_details[key][1] / float(model_details[BaseConstants.CPU][2])))
            hdd_per_server = min(hdd_per_server, max(slots))
            hdd_per_server = max(hdd_per_server, min(slots))
            node.attrib[BaseConstants.MIN_HDD_SLOTS] = min(slots)
            node.attrib[BaseConstants.HDD_SLOTS] = hdd_per_server

        hdd_price = parts_object.get_part_attrib(model_number, price_factor)

        hdd_total_price = calculate_total_part_price(hdd_price, node.attrib[BaseConstants.HDD_SLOTS])

        return node, hdd_total_price

    @staticmethod
    def ssd_parts_price_calculation(key, model_details, parts_object, node, price_factor):

        node, model_number = update_part_name_price_details(key, model_details, parts_object, node, price_factor)

        if node.attrib[BaseConstants.SUBTYPE] == HyperConstants.COMPUTE:
            node.attrib[BaseConstants.IOPS] = 0
        else:
            node.attrib[BaseConstants.IOPS] = 1

        ssd_price = parts_object.get_part_attrib(model_number, price_factor)

        ssd_total_price = calculate_total_part_price(ssd_price, node.attrib[BaseConstants.IOPS])

        node.attrib[BaseConstants.SSD_SLOTS] = node.attrib[BaseConstants.IOPS]

        node.attrib[HyperConstants.SSD_FULL_SIZE] = node.attrib[BaseConstants.SSD_SIZE]

        return node, ssd_total_price

    @staticmethod
    def gpu_parts_price_calculation(key, model_details, parts_object, node, price_factor, max_slots_per_node):

        max_slots_per_node /= parts_object.get_part_attrib(model_details[key][0], HyperConstants.PCIE_REQ)

        node, model_number = update_part_name_price_details(key, model_details, parts_object, node, price_factor)

        gpu_per_server = int(ceil(model_details[key][1] / float(model_details[BaseConstants.CPU][2])))

        total_gpu = gpu_per_server * model_details[BaseConstants.CPU][2]

        node.attrib[HyperConstants.GPU_SLOTS] = min(gpu_per_server, max_slots_per_node)

        node.attrib[HyperConstants.GPU_CAP] = \
            node.attrib[HyperConstants.GPU_CAP] / HyperConstants.GB_TO_GIB_CONVERSION_FACTOR

        node.attrib[BaseConstants.VRAM] = node.attrib[HyperConstants.GPU_SLOTS] * node.attrib[HyperConstants.GPU_CAP]

        gpu_price = parts_object.get_part_attrib(model_number, price_factor)

        gpu_total_price = calculate_total_part_price(gpu_price, total_gpu)

        return node, gpu_total_price


def calculate_total_part_price(component_price, components_required):
    return component_price * components_required


def update_part_name_price_details(key, model_details, parts_object, node, price_factor):

    mapper = {BaseConstants.CPU: [HyperConstants.CPU_PART, HyperConstants.CPU_PRICE],
              BaseConstants.RAM: [HyperConstants.RAM_PART, HyperConstants.RAM_PRICE],
              BaseConstants.HDD: [HyperConstants.HDD_PART, HyperConstants.HDD_PRICE],
              BaseConstants.SSD: [HyperConstants.SSD_PART, HyperConstants.SSD_PRICE],
              BaseConstants.VRAM: [HyperConstants.GPU_PART, HyperConstants.GPU_PRICE]}

    part_dict = mapper[key]

    model_number = model_details[key][0]
    node.attrib[part_dict[0]] = model_number
    node.attrib[part_dict[1]] = price_factor
    node = parts_object.update_part_details_to_node(key, model_number, node)

    return node, model_number
