from django.db import models
from datetime import date
from jsonfield import JSONField

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser


class Node(models.Model):
    name = models.TextField()
    sort_index = models.IntegerField(default=5000)
    hercules_avail = models.BooleanField(default=False)
    hx_boost_avail = models.BooleanField(default=False)
    node_json = JSONField()
    type = models.CharField(max_length=200)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Part(models.Model):
    name = models.TextField()
    part_json = JSONField()
    part_name = models.TextField()
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class IopsConvFactor(models.Model):
    REP_FACTOR_CHOICES = (("RF2", "two redundant replica"),
                          ("RF3", "three redundant replica"))

    THRESHOLD_CHOICES = ((0, "conservative"),
                         (1, "standard"),
                         (2, "aggressive"))

    WORKLOAD_CHOICES = (("VDI", "Virtual Desktop Infrastructure"),
                        ("RDSH", "Remote Desktop Session Host "),
                        ("VSI", "Virtual Server Infrastructure"),
                        ("OLTP", "On-line Transaction Processing"),
                        ("OLAP", "On-line Analytical Processing"),
                        ("OOLTP", "Oracle On-line Transaction Processing"),
                        ("OOLAP", "Oracle On-line Analytical Processing"),
                        ("RAW", "Raw Workload"),
                        ("EXCHANGE_16KB", "16KB IO/s Exchange Server"),
                        ("EXCHANGE_32KB", "32KB IO/s Exchange Server"),
                        ("EXCHANGE_64KB", "64KB IO/s Exchange Server"),
                        ("ROBO", "Robo workload"),
                        ("SPLUNK", "Splunk workload"),
                        ("EPIC", "Epic workload"),
                        ("VEEAM", "VEEAM workload"),
                        ("VDI_INFRA", "VDI Infrastructure workload"),
                        ("EDGE", "EDGE workload"),
                        ("CONTAINER", "CONTAINER workload"),
                        ("AIML", "Artificial Intelligence/Machine Learning workload"))
    HYPERVISOR_CHOICES = ((0, 'ESXi'),
                          (1, 'Hyper-V'))

    id = models.AutoField(primary_key=True)
    threshold = models.IntegerField(default=None, choices=THRESHOLD_CHOICES)
    iops_conv_factor = models.IntegerField(default=0)
    replication_factor = models.CharField(max_length=10, choices=REP_FACTOR_CHOICES)
    workload_type = models.CharField(max_length=30, choices=WORKLOAD_CHOICES)
    part_name = models.CharField(max_length=30)
    hypervisor = models.IntegerField(default=0, choices=HYPERVISOR_CHOICES)
    iscsi_iops = models.IntegerField(default=0)

    class Meta:
        unique_together = ('threshold', 'workload_type', 'part_name', 'replication_factor', 'hypervisor')


class Scenario(models.Model):
    SIZING_TYPE_CHOICES = (('optimal', 'OPTMIAL NODE SIZING'),
                           ('fixed', 'FIXED NODE SIZING'),
                           ('hybrid', 'OPTMIAL AND FIXED NODE SIZING'))
    SCEN_TAB_CHOICES = (('general', 'MARK AS GENERAL'), ('archive', 'MOVE TO ARCHIVE'), ('fav', 'MARK AS FAVOURITE'))

    name = models.TextField()
    workload_json = JSONField()
    workload_result = JSONField()
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    settings_json = JSONField()
    username = models.TextField()
    sizing_type = models.CharField(max_length=30, choices=SIZING_TYPE_CHOICES)
    scen_label = models.CharField(max_length=30, choices=SCEN_TAB_CHOICES, default='general')

    def __unicode__(self):
        return self.name

    def initialize_scenario(self, serializer):
        self.name = serializer.data['name']
        self.settings_json = {}
        self.status = True
        self.workload_json = {}
        self.workload_result = []
        self.save()


class Results(models.Model):
    result_json = JSONField()
    settings_json = JSONField()
    scenario_id = models.IntegerField()
    created_date = models.DateTimeField(auto_now=True)
    name = models.TextField()
    error_json = JSONField()


class Thresholds(models.Model):
    threshold_key = models.TextField()
    threshold_value = models.IntegerField()
    threshold_category = models.IntegerField()
    workload_type = models.TextField()


class SpecIntData(models.Model):
    model = models.CharField(max_length=100)
    speed = models.FloatField(default=0)
    cores = models.IntegerField(default=0)
    blended_core_2006 = models.FloatField(default=0)
    blended_core_2017 = models.FloatField(default=0)
    is_base_model = models.BooleanField(default=False)

    class Meta:
        unique_together = ('model', 'speed', 'cores')


class HxPerfNumbers(models.Model):
    REP_FACTOR_CHOICES = (("RF3", "three redundant replica"),)

    THRESHOLD_CHOICES = ((1, "standard"),)

    WORKLOAD_CHOICES = (("OLTP/VSI", "Virtual Server Infrastructure"),
                        ("OLAP", "On-line Analytical Processing"))

    HYPERVISOR_CHOICES = ((0, 'ESXi'),)

    SERVER_TYPE_CHOICES = (("M5", "M5-Server"),)

    NODE_CHOICES = (("All-Flash", "HX220|HX240"),)

    IOPS_TYPE_CHOICES = (("8K|70% Read|30% Write|100% Random (IOPS)", "8K 70/30 workload (IOPS)"),
                         ("16K|100% Read|100% Write|100% Random (IOPS)", "16K 100% read/write (IOPS)"),
                         ("32K|60% Read|40% Write|100% Random (IOPS)", "32K 60% read 40% write (IOPS)"),
                         ("64K|100% Seq Read (MB/s)", "64K 100% seq read (MB/s)"),
                         ("128K|100% Random (IOPS)", "128K (IOPS)"))

    server_type = models.CharField(max_length=10, choices=SERVER_TYPE_CHOICES)
    hypervisor = models.IntegerField(default=None, choices=HYPERVISOR_CHOICES)
    wl_type = models.CharField(max_length=30, choices=WORKLOAD_CHOICES)
    threshold = models.IntegerField(default=None, choices=THRESHOLD_CHOICES)
    node_substring = models.CharField(max_length=10, choices=NODE_CHOICES)
    ssd_string = models.CharField(max_length=30)
    replication_factor = models.CharField(max_length=10, choices=REP_FACTOR_CHOICES)
    iops_type = models.CharField(max_length=50, choices=IOPS_TYPE_CHOICES)
    iops_value = models.IntegerField(default=0)

    class Meta:
        db_table = "hx_perf_numbers"


class User(AbstractBaseUser, PermissionsMixin):

    LANGUAGE_CHOICES = (("english", "ENGLISH"), ("japanese", "JAPANESE"))

    password = models.CharField(max_length=100)
    last_login = models.DateTimeField(auto_now=True)
    is_superuser = models.IntegerField(default=0)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    is_staff = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    date_joined = models.DateTimeField(auto_now_add=True)
    company = models.CharField(default='', max_length=100)
    emp_id = models.CharField(default='', max_length=10)
    accesslevel = models.IntegerField()
    iops_access = models.BooleanField(default=False)
    home_page_desc = models.BooleanField(default=True)
    fixed_sizing_desc = models.BooleanField(default=True)
    optimal_sizing_desc = models.BooleanField(default=True)
    scenario_per_page = models.IntegerField(default=10)
    language = models.CharField(default="english", choices=LANGUAGE_CHOICES, max_length=20)
    theme = models.CharField(default="light", max_length=20)
    home_disclaimer = models.DateField(default=date(2001, 1, 1))
    banner_version = models.CharField(default='9.8.0', max_length=100)
    price_list = models.CharField(default='', max_length=15)

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'


class SharedScenario(models.Model):
    scenario_id = models.IntegerField()
    username = models.TextField()
    userid = models.TextField()
    acl = models.BooleanField(default=True)
    email = models.TextField()
    is_secure = models.BooleanField(default=False)


class Rules(models.Model):
    rule_id = models.IntegerField(primary_key=True)
    rule_json = JSONField()


class feature_permission(models.Model):
    feature = models.TextField(default='')
    access_level = models.IntegerField(default=0)


class LaeUsers(models.Model):
    username = models.TextField()


class FixedResults(models.Model):
    result_json = JSONField()
    cluster_name = models.TextField()
    scenario_id = models.IntegerField()
    created_date = models.DateTimeField(auto_now=True)
    error_json = JSONField()
    settings_json = JSONField()


class CCWData(models.Model):
    product_id = models.TextField()
    product_path = models.TextField()
    product_reference = models.TextField()
    product_parent = models.TextField(default='')


class UploadBomExcelInfo(models.Model):
    bom_input_json = JSONField()
    username = models.TextField()
    is_completed = models.BooleanField(default=False)
    transaction_datetime = models.DateTimeField()


class EstimateDetails(models.Model):
    scenario_id = models.IntegerField()
    scenario_name = models.TextField()
    estimate_id = models.TextField()
    estimate_name = models.TextField()
    estimate_response = models.TextField()
    is_updated = models.SmallIntegerField(default=0)
    created_datetime = models.DateTimeField()


class ApiDetails(models.Model):
    api_id = models.AutoField(primary_key=True)
    scenario_id = models.IntegerField()
    api_name = models.IntegerField(default=0)
    api_token = models.TextField(unique=True)
    is_claimed = models.BooleanField(default=False)
    transaction_datetime = models.DateTimeField()