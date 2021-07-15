from re import findall, split
from math import ceil
from copy import deepcopy
from itertools import chain
from .html_parser import GetHTMLParser


class OracleAwr(object):

    def __init__(self, recvd_file):

        self.file = recvd_file
        self.file.seek(0)

        self.errors = []

        self.version_header = 'Release'

        self.io_headers = ['Total (MB)']
        self.host_headers = ['CPUs', 'Cores', 'Sockets', 'Memory(GB)']
        self.util_headers = ['% of total CPU for Instance', 'Memory Usage %', 'Host Mem (MB)']

        self.response = dict()

    def construct_response(self, is_html):

        if is_html:
            req_data = self.extract_html_data()
            if self.errors:
                return self
        else:
            req_data = self.extract_txt_data()

        self.validate(req_data)

        if self.errors:
            return self

        self.perform_calc(req_data)

        return self

    def validate(self, extracted):

        if self.version_header in extracted:
            # comparing min version '11.2.0.4' in two parts
            min_version_support = [11.2, 0.4]

            if float(extracted['Release'][0]) < min_version_support[0] or \
                    (float(extracted['Release'][0]) == min_version_support[0] and
                     float(extracted['Release'][1]) < min_version_support[1]):
                self.errors.append("Oracle AWR file upload for versions below %s.%s is not supported" %
                                   (min_version_support[0], min_version_support[1]))
        else:
            self.errors.append("Oracle version details are missing or invalid version number")

        if not self.errors:

            for header in self.host_headers:
                if header not in extracted:
                    self.errors.append("\"%s\" is missing from Host info section" % header)

            for header in self.io_headers:
                if header not in extracted:
                    self.errors.append("\"%s\" is missing from IO Profile section" % header)

        if self.errors:
            self.errors.append("Kindly use the latest version of Oracle AWR")

    def perform_calc(self, extracted):

        vcpus_per_db = int(extracted['Cores'])
        ram_per_db = ceil(max(extracted['Memory(GB)'], extracted['Host Mem (MB)'] / 1024.0))
        avg_iops_per_db = int(self.normalise_blocks(extracted))
        avg_mbps_per_db = int(extracted['Total (MB)'])

        base_dict = {'vcpus_per_db': vcpus_per_db,
                     'ram_per_db': ram_per_db,
                     'avg_iops_per_db': avg_iops_per_db,
                     'avg_mbps_per_db': avg_mbps_per_db}

        provisioned = deepcopy(base_dict)
        utilized = deepcopy(base_dict)

        utilized['vcpus_per_db'] = ceil(extracted['Cores'] * extracted['% of total CPU for Instance'] / 100)
        utilized['ram_per_db'] = int(ram_per_db * extracted['Memory Usage %'] / 100)

        self.response['utilized'] = utilized
        self.response['provisioned'] = provisioned

    @staticmethod
    def normalise_blocks(extracted):

        # Other block sizes should be normalised to this
        block_size = 8

        # convert to KB as block sizes are measured in KB
        normalised_iops = extracted['Total (MB)'] * 1024.0 / float(block_size)
        return normalised_iops

    def extract_txt_data(self):

        info = dict()

        line_list = self.file.readlines()

        for index, line in enumerate(line_list):

            if line == '\n':
                continue

            line = line.strip().replace(':', '')

            if self.version_header in line and self.version_header not in info:
                version = findall(r'\d{1,2}\.\d{1,2}\.\d{1,2}\.\d{1,2}?', line_list[index+2])
                if version:
                    version = version[0].strip().split('.')
                    version = '.'.join(version[:2]), '.'.join(version[2:])
                    info[self.version_header] = version

            if any(line.startswith(label) for label in self.io_headers + self.util_headers):

                line = split('\s{2,}', line)

                if line[0] in ['Memory Usage %', 'Host Mem (MB)']:
                    begin = float(line[1].replace(',', ''))
                    end = float(line[2].replace(',', ''))
                    info[line[0]] = float(max(begin, end))
                    continue

                info[line[0]] = float(line[1].replace(',', ''))
                continue

            else:

                line = split('\s{1,}', line)

                if all(label in line for label in self.host_headers):

                    value_line = line_list[index + 2].strip()
                    value_line = split('\s{1,}', value_line)

                    for index in [-1, -2, -3, -4]:
                        info[line[index]] = float(value_line[index].replace(',', ''))

        return info

    def extract_html_data(self):

        parser = GetHTMLParser(self.version_header, self.io_headers, self.host_headers, self.util_headers)

        try:
            parser.feed(self.file.read())
        except Exception:
            self.errors.append("Error while parsing html data. Kindly upload a valid html file")

        return parser.extracted
