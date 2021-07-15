import json
import os

from utils.baseview import BaseView
from rest_framework.response import Response
from rest_framework import status
from sizer.local_settings import BASE_DIR

class GetHelpDetails(BaseView):

    def get(self, format=None):
        """
        To get help page
        """
        data = self.get_video_details()

        if not data:
            return Response({'status': 'error',
                             'errorMessage': 'Training videos are missing from webapps/dist/videos folder.'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(data)

    def get_video_details(self):

        response_data = list()

        video_path = os.path.join(BASE_DIR, "webapps/dist/videos/")
        if not os.path.isdir(video_path):
            return response_data

        video_info_path = os.path.join(BASE_DIR, "webapps/dist/videos/videos.info")
        if not os.path.exists(video_info_path):
            return response_data

        file_list = [line.rstrip('\n') for line in open(video_info_path)]

        for ifile in file_list:
            ipath = "webapps/dist/videos/" + ifile
            fipath = os.path.join(BASE_DIR, ipath)
            if not os.path.exists(fipath):
                continue

            with open(fipath, 'r', encoding='utf-8') as f_file:
                info_data=f_file.read()
                info = json.loads(info_data)
                response_data.append(info)

        return response_data
