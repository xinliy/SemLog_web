from semlog_mongo.semlog_mongo.mongo import MongoDB
from bson.json_util import dumps
import pprint
ip = "mongodb+srv://admin:admin@semlog-cluster-fucxw.mongodb.net/test?retryWrites=true"
m=MongoDB(database="SemLog",collection="20",ip=ip)

result=m.search(timestamp=0.1)
# dir=m.download(result)
m.save_json(result,"./a.json")
# result=list(result)
# for i in result:
#     pprint.pprint(type(i['_id']))
# import json
# # y=json.dumps([i for i in result])
# # print(y)
# y=dumps(result)
# with open('test.json','w') as outfile:
#     json.dump(y,outfile)
