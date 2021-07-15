import django
import os
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sizer.local_settings")

django.setup()

from hyperconverged.models import SpecIntData


def loaddata():

    fo = open('sizer/SpecInfo.csv', 'r')
    json_data =csv.DictReader(fo)
    for row in json_data:
        new_obj = SpecIntData()
        new_obj.model = row["Model"]
        new_obj.speed = row["Speed (GHz)"]
        new_obj.cores = row["Cores"]
        new_obj.blended_core = row["Blended/Core"]
        new_obj.save()
    return


loaddata()
