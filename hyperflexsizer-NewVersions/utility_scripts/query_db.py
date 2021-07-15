import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sizer.local_settings")

django.setup()

from hyperconverged.models import Part

part_list = Part.objects.all()

for part in part_list:

    part_json = part.part_json
