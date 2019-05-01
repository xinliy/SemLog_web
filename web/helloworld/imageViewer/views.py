from django.shortcuts import render
import sys
from django.http import HttpResponse
import pymongo
import os

sys.path.append("..")
from semlog_mongo.semlog_mongo.mongo import MongoDB
from web.helloworld import settings

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

    ip="mongodb+srv://admin:admin@semlog-cluster-fucxw.mongodb.net/test?retryWrites=true"
    m = MongoDB(ip=ip,database='SemLog', collection='20')
    # Convert string input to be float
    if timestamp is not None:
        timestamp = float(timestamp)
    print(object_id)
    r = m.search(timestamp=timestamp, object_id=object_id, view_id=view_id,
                 image_type=image_type)
    # r = [i for i in r]

    # Get Upper folder address for image saving
    saving_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    saving_path = saving_path + '/static'
    m.download(r, abs_path=saving_path)

    html = "<html><body>" + "Download Success!" + "</body></html>"
    return HttpResponse(html)


def gallery(request):
    image_list = []
    for root, dirs, files in os.walk(settings.IMAGE_ROOT):
        basename=os.path.basename(os.path.normpath(root))
        for file in files:
            if file.endswith(".png"):
                image_list.append(basename+'/'+file)
    print(image_list)
    return render(request,'gallery.html',{'image_list':image_list})
