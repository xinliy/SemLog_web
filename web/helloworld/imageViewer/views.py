from django.shortcuts import render
import sys
from django.http import HttpResponse
import pymongo
import os

sys.path.append("..")
from semlog_mongo.semlog_mongo.mongo import MongoDB


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
        print("is none!")
        return None if v == '' else v

    timestamp = object_id = view_id = image_type = None

    if request.method == 'GET':
        timestamp = convert_none(request.GET["timestamp"])
        object_id = convert_none(request.GET['object_id'])
        view_id = convert_none(request.GET['view_id'])
        image_type = convert_none(request.GET['image_type'])

    m = MongoDB(database='SemLog', collection='20')
    if timestamp is not None:
        timestamp = float(timestamp)
    print(object_id)
    r = m.search(timestamp=timestamp, object_id=object_id,view_id=view_id,
                 image_type=image_type)
    r = [i for i in r]
    # # print((r))
    # c=pymongo.MongoClient()['SemLog']['20'].find_one()

    html = "<html><body>" + str(r) + "</body></html>"
    return HttpResponse(html)
