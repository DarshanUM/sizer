from django.urls import path

from .views.scenario_solve_views import ScenarioSolve, ResultDetails, ScenarioFetch
from .views.scenario_clone_views import ScenarioClone
from .views.file_download_views import GenerateReport, DownloadReport, SizingCalcReport, GenerateBOMExcel, \
     DownloadBOMExcel
from .views.HX_tools_download import ProfilerDownload, BenchDownload
from .views.file_handler_views import ProcessEsxStat
from .views.utility_views import SizerUsers, VersionDetails
from .views.home_page_views import HomePage, AutoArchive
from .views.scenario_share_views import ShareScenario
from .views.resize_views import ReSizeScenario
from .views.filter_option_views import SizerFilter
from .views.utility_views import GetFIOptions, GetHxPerfNumbers, GetCpuModels
from .views.reverse_sizer_views import ReverseSizerCalculator
from .views.bench_sheet_calc import BenchSheetCalc
from .views.file_download_views import DownloadExcelTemplate
from .views.upload_bom_views import BOMExcelInfo
from .views.profiler_api_views import ClaimProfileData

urlpatterns = [

    path(r'scenarios', HomePage.as_view()),

    path(r'scenarios/autoarchive', AutoArchive.as_view()),

    path(r'scenarios/<int:id>/clone', ScenarioClone.as_view()),

    path(r'scenario', ScenarioFetch.as_view()),

    path(r'scenarios/<int:id>', ScenarioSolve.as_view()),

    path(r'scenarios/<int:id>/report', GenerateReport.as_view()),
    path(r'scenarios/report/download', DownloadReport.as_view()),

    path(r'scenarios/<int:id>/bom', GenerateBOMExcel.as_view()),
    path(r'scenarios/bom/download', DownloadBOMExcel.as_view()),

    path(r'scenarios/bomexcelinfo', BOMExcelInfo.as_view()),

    path(r'scenarios/template/download', DownloadExcelTemplate.as_view()),

    path(r'scenarios/<int:id>/resize', ReSizeScenario.as_view()),
    path(r'scenarios/<int:id>/shares', ShareScenario.as_view()),

    path(r'Node/filterlist/', SizerFilter.as_view()),
    path(r'Node/filist/', GetFIOptions.as_view()),

    path(r'results/result_detail/<int:scenario_id>', ResultDetails.as_view()),

    path(r'version', VersionDetails.as_view()),

    path(r'processesxstat', ProcessEsxStat.as_view()),

    path(r'users', SizerUsers.as_view()),

    path(r'downloadprofiler', ProfilerDownload.as_view()),
    path(r'downloadbench', BenchDownload.as_view()),

    path(r'reversesizer', ReverseSizerCalculator.as_view()),
    path(r'reversesizerfilter', ReverseSizerCalculator.as_view()),

    path(r'benchsheet', BenchSheetCalc.as_view()),

    path(r'fixed_config_report', SizingCalcReport.as_view()),
    path(r'hxperfnumbers', GetHxPerfNumbers.as_view()),
    path(r'cpumodels', GetCpuModels.as_view()),
    path(r'scenarios/claimprofiledata', ClaimProfileData.as_view())
]
