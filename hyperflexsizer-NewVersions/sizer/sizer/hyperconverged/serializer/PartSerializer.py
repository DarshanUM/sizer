from rest_framework import serializers
from hyperconverged.models import Part
from rest_framework.validators import UniqueValidator
from hyperconverged.serializer.WorkloadSerializer import JSONSerializerField


class PartSerializer(serializers.Serializer):

    name = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Part.objects.all())])
    capacity = serializers.IntegerField(required=True)
    id = serializers.IntegerField(required=False)
    unit_price = serializers.IntegerField(required=True)
    description = serializers.CharField(required=True)
    frequency = serializers.CharField(required=False)
    l3_cache = serializers.CharField(required=False)
    tdp = serializers.CharField(required=False)
    speclnt = serializers.CharField(required=False)
    encryption = serializers.CharField(required=False)


class PartGetSerializer(serializers.Serializer):

    id = serializers.CharField(read_only=True)
    part_json = JSONSerializerField()
    created_date = serializers.DateTimeField()
    status = serializers.BooleanField(default=True)


class PartPutSerializer(serializers.Serializer):

    capacity = serializers.IntegerField(required=True)
    unit_price = serializers.IntegerField(required=True)
