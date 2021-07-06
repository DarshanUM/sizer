import logging


class SizerLogger(object):

    def __init__(self, scenario_id):
        self.logger = logging.getLogger(__name__)
        self.logger_header = '| ' + str(scenario_id) + ' | ' + self.result_name
