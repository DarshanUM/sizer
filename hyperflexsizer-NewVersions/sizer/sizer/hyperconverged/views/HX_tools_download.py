from utils.baseview import BaseView
from rest_framework.response import Response

from hyperconverged.views.utility_views import get_configs


class ProfilerDownload(BaseView):

    # @feature_decorator('Profiler Download')
    @staticmethod
    def post(request, format=None):
        """
        To download profiler ova

        if os.environ.has_key('OPENSHIFT_REPO_DIR'):
            from local_settings import OVA_BASE_DIR
        else:
            from sizer.local_settings import OVA_BASE_DIR
        ova_file_name = os.listdir(OVA_BASE_DIR)
        fpath = os.path.join(OVA_BASE_DIR, ova_file_name[0])
        fpath = os.path.abspath(fpath)

        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(fpath, 'rb'), chunk_size),
                                         content_type=mimetypes.guess_type(fpath)[0])
        response['Content-Length'] = os.path.getsize(fpath)
        response['Content-Disposition'] = "attachment; filename=%s" % fpath
        return Response(fpath)
        """
        # As cisco tickets are not resolved, currently validatsing and providing option
        # to download via Cisco Box.
        return Response(get_configs("Profiler")["profiler_url"])


class BenchDownload(BaseView):

    # @feature_decorator('Bench Download')
    @staticmethod
    def post(request, format=None):
        return Response(get_configs("Bench")["bench_url"])
