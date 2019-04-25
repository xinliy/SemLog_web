import sys
sys.path.append("..")

from semlog_mongo.mongo import MongoDB


db=MongoDB("SemLog","20")

l=db.search(object_id='hf-T8iy_c0CxIwAUOw7zrQ')
db.download(l)