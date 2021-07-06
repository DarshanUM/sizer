
class InitThreshold(object):

    def __init__(self, threshold_factor):
        self.threshold_factor = threshold_factor


class Hypervisor(InitThreshold):

    def __init__(self, threshold_factor, hypervisor):
        InitThreshold.__init__(self, threshold_factor)
        self.hypervisor = hypervisor

    def get_hypervisor_value(self):
        if self.hypervisor == 'esxi':
            hypervisor_int = 0
        else:
            hypervisor_int = 1
        return hypervisor_int
