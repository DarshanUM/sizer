from utils.baseview import BaseView

from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response

from hyperconverged.serializer.CalculatorSerializer import ReverseSizerCalculatorSerializer
from hyperconverged.solver.reverse_sizing import ReverseSizer
from hyperconverged.views.filter_option_views import RevSizerBaseFilter


Threshold = dict()
Threshold["All Flash"] = dict()
Threshold["Hybrid"] = dict()
Threshold["All Flash"][0] = {"CPU": 80.0,
                             "RAM": 92.0,
                             "DISK": 65.0}
Threshold["All Flash"][1] = {"CPU": 90.0,
                             "RAM": 92.0,
                             "DISK": 70.0}
Threshold["All Flash"][2] = {"CPU": 93.0,
                             "RAM": 93.0,
                             "DISK": 75.0}

Threshold["Hybrid"][0] = {"CPU": 80.0,
                          "RAM": 92.0,
                          "DISK": 65.0}
Threshold["Hybrid"][1] = {"CPU": 90.0,
                          "RAM": 92.0,
                          "DISK": 65.0}
Threshold["Hybrid"][2] = {"CPU": 93.0,
                          "RAM": 93.0,
                          "DISK": 70.0}


class ReverseSizerCalculator(BaseView):

    @staticmethod
    def get(request):

        requirements = ["hypervisor", "cpu_options", "hdd_options", "ram_options", "compute_nodes", "rf",
                        "ssd_options", "workload_options", "node_type", "hercules_avail", "hx_boost_avail"]

        return Response(RevSizerBaseFilter.filter_node_attrib(requirements))

    @staticmethod
    def post(request):
        data = JSONParser().parse(request)
        serializer = ReverseSizerCalculatorSerializer(data=data)
        if serializer.is_valid():
            new_calc = ReverseSizer(data)
            node_usables = new_calc.get_usable_resources()
            return Response(node_usables)
        else:
            return Response({'status': 'error',
                             'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
