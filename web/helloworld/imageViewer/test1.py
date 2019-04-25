from django.shortcuts import render
import sys
from django.http import  HttpResponse
import os

sys.path.append("..")
from semlog_mongo.semlog_mongo.mongo import MongoDB
timestamp=object_id=view_id=image_type=None
m = MongoDB(database='SemLog', collection='20')
r = m.search(timestamp=0.1,image_type='Color')
saving_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
saving_path = saving_path + '/static'
print(type(r))
m.download(r, abs_path=saving_path)