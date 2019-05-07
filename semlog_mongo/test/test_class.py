from semlog_mongo.semlog_mongo.mongo import MongoDB
import pprint
ip = "mongodb+srv://admin:admin@semlog-cluster-fucxw.mongodb.net/test?retryWrites=true"
m=MongoDB(database="SemLog",collection="20",ip=ip)

# m.download(m.search(timestamp=0.3,object_id='UfxqNeTP2EWmYtwW0iR-PA'))
r=m.search(timestamp=0.3)
r=m.download(r)
pprint.pprint(r)
# result=m.get_object_rgb(object_id='8JIRrlcAGEOoY16vrYR1Sw',collection='20')
# print(result)


# pr=cProfile.Profile()
# pr.enable()
# m.download(m.search(timestamp=0.3,object_id='UfxqNeTP2EWmYtwW0iR-PA'))
# pr.disable()
# pr.print_stats(sort="calls")
