from re import findall
from html.parser import HTMLParser


class GetHTMLParser(HTMLParser):

    def __init__(self, version_header, io_headers, host_headers, util_headers):

        HTMLParser.__init__(self)

        self.in_table = None
        self.in_td = False
        self.in_tr = False
        self.is_insecure = False
        self.row_data = list()

        self.extracted = dict()

        self.version_header = version_header

        self.io_headers = io_headers
        self.host_headers = host_headers
        self.util_headers = util_headers

    def handle_starttag(self, tag, attrs):

        if tag == 'table':
            for attr, value in attrs:
                if attr == 'summary':
                    if any(summary_string in value for summary_string in ["database instance", "host information",
                                                                          "IO profile", "CPU usage and wait statistics",
                                                                          "shared pool statistics",
                                                                          "memory statistics"]):
                        self.in_table = value

        elif tag == 'tr' and self.in_table:
            self.in_tr = True

        elif tag == 'td' and self.in_tr:
            self.in_td = True

    def handle_endtag(self, tag):

        if tag == 'table' and self.in_table:
            self.in_table = None

        elif tag == 'td' and self.in_td:
            self.in_td = False

        elif tag == 'tr' and self.in_tr:
            if self.row_data:
                self.extract_data()
                self.row_data = []
            self.in_tr = False

    def handle_data(self, data):
        if self.in_td:
            data = data.strip().replace(',', '')
            self.row_data.append(data)

    def extract_data(self):

        row_data = self.row_data
        if "database instance" in self.in_table:
            for data in row_data:
                version = findall(r'\d{1,2}\.\d{1,2}\.\d{1,2}\.\d{1,2}?', data)
                if version:
                    version = version[0].strip().split('.')
                    version = '.'.join(version[:2]), '.'.join(version[2:])
                    self.extracted[self.version_header] = version
                    break

        elif "host information" in self.in_table:
            index = 2
            for header in self.host_headers:
                self.extracted[header] = float(row_data[index])
                index += 1

        elif "IO profile" in self.in_table:
            for header in self.io_headers:
                if header in row_data[0] and header not in self.extracted:
                    self.extracted[header] = float(row_data[1])
                    break

        elif "memory statistics" in self.in_table:
            if "Host Mem (MB)" in row_data[0]:
                begin = float(row_data[1])
                end = float(row_data[2])
                self.extracted["Host Mem (MB)"] = float(max(begin , end))

        elif "shared pool statistics" in self.in_table:
            if "Memory Usage %" in row_data[0]:
                begin = float(row_data[1])
                end = float(row_data[2])
                self.extracted["Memory Usage %"] = float(max(begin , end))

        elif "CPU usage and wait statistics" in self.in_table:
            self.extracted[self.util_headers[0]] = float(row_data[0])
