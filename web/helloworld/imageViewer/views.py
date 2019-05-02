from django.shortcuts import render
import sys
from django.http import HttpResponse
import pymongo
import os
# folder_root = os.path.abspath('../..')
# project_root = os.path.abspath('../../..')
# assert os.path.basename(folder_root) == 'web', print(
#     "The actual path is:", os.path.basename(folder_root))
# sys.path.append(project_root)
# import set_path
from semlog_mongo.semlog_mongo.mongo import MongoDB
from web.helloworld import settings
import json
import copy

# Create your views here.


# m = MongoDB(database='SemLog', collection='20')
# r=m.search(timestamp=0.3)
#
# # Get Upper folder address for image saving
# saving_path=os.path.abspath(os.path.join(os.getcwd(), ".."))
# saving_path=saving_path+'/static'
# m.download(r,abs_path=saving_path)


def search(request):
    return render(request, 'main.html')


def start_search(request):
    def convert_none(v):
        """Blank input cannot be recognized in pymongo. Convert to None."""
        return None if v == '' else v

    timestamp = object_id = view_id = image_type = None

    if request.method == 'GET':
        timestamp = convert_none(request.GET["timestamp"])
        object_id = convert_none(request.GET['object_id'])
        view_id = convert_none(request.GET['view_id'])
        image_type = convert_none(request.GET['image_type'])

    ip = "mongodb+srv://admin:admin@semlog-cluster-fucxw.mongodb.net/test?retryWrites=true"
    m = MongoDB(ip=ip, database='SemLog', collection='20')
    # Convert string input to be float
    if timestamp is not None:
        timestamp = float(timestamp)
    r = m.search(timestamp=timestamp, object_id=object_id, view_id=view_id,
                 image_type=image_type)
    # Get Upper folder address for image saving
    saving_path = os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."))
    saving_path=os.path.join(saving_path,'static')

    image_dir=m.download(r, abs_path=saving_path)
    m.save_json(r,os.path.join(settings.STATIC_ROOT,"image_info.json"))
    with open(os.path.join(settings.STATIC_ROOT,"image_dir.json"),"w") as outfile:
        json.dump(image_dir,outfile)

    return render(request, 'gallery.html', {'image_list': get_image_path()})


def gallery(request):

    return render(request, 'gallery.html', {'image_list': get_image_path()})


def get_image_path():
    image_list = []
    for root, dirs, files in os.walk(settings.IMAGE_ROOT):
        basename = os.path.basename(os.path.normpath(root))
        for file in files:
            if file.endswith(".png"):
                image_list.append(basename + '/' + file)
    return image_list
