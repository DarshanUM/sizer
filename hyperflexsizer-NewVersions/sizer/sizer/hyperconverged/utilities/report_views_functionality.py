import os
import mimetypes
from django.core.files.base import ContentFile
from django.http import HttpResponse
from sizer.local_settings import BASE_DIR

def get_bom_ppt_reports(request):
    file_name = request.GET.get("fname", "")
    file_path = os.path.join(BASE_DIR, file_name)
    file_obj = open(file_path, "rb")
    content = ContentFile(file_obj.read())
    file_obj.close()

    response = HttpResponse(content)
    format_name = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)
    content_disposition = 'attachment; filename="%s"' % (format_name)
    response['Content-Disposition'] = content_disposition
    content_type = mimetypes.guess_type(file_path)[0]
    response['Content-Type'] = content_type
    response['Content-Length'] = str(filesize)

    try:
        os.system("rm "+str(file_path))
    except OSError:
        pass

    return response


def get_excel_template(request):

    file_path = os.path.join(BASE_DIR, "sizer/BulkDB_Template.xlsx")
    file_obj = open(file_path, "rb")
    content = ContentFile(file_obj.read())
    file_obj.close()

    response = HttpResponse(content)
    format_name = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)
    content_disposition = 'attachment; filename="%s"' % (format_name)
    response['Content-Disposition'] = content_disposition
    content_type = mimetypes.guess_type(file_path)[0]
    response['Content-Type'] = content_type
    response['Content-Length'] = str(filesize)

    return response