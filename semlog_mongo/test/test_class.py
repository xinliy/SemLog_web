from semlog_mongo.semlog_mongo.mongo import MongoDB
from bson.json_util import dumps
import pprint
ip = "mongodb+srv://admin:admin@semlog-cluster-fucxw.mongodb.net/test?retryWrites=true"
m=MongoDB(database="SemLog",collection="20",ip=ip)

result=m.get_object_rgb(object_id='8JIRrlcAGEOoY16vrYR1Sw',collection='20')
print(result)


