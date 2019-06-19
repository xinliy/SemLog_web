import os
import sys 
print(os.listdir(os.getcwd()))
sys.path.append(os.getcwd())
import website
from semlog_mongo.semlog_mongo.mongo import MongoDB
m=MongoDB('SemLog',"LookingAtTable.meta")
l=m.get_object_by_class(['IAICeilingLight'])
print(l)



