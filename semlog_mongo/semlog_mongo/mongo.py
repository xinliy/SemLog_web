from pymongo import MongoClient
import os
import gridfs


class MongoDB():

    def __init__(self, database, collection,ip='127.0.0.1',port=27017):
        self.database = database
        self.collection = collection
        self.client = MongoClient(ip,port)[database][collection]

    def search(self, timestamp=None, object_id=None, view_id=None, image_type=None):
        """Input params to search for specific images.

        Args:
            timestamp(float): Filter out images taken larger than the timestamp.
            object_id(str): Id for a specific object.
            view_id(str): Id for a specific view.
            image_type(str): type for images. ("Color"|"Normal"|"Depth"|"Mask")

        Return:
            Result from the MongoDB.

        """

        pipeline = [{"$match": {"views": {"$exists": True}}}]

        if timestamp is not None:
            pipeline.append({"$match": {"timestamp": {"$lte": timestamp}}})
        pipeline.append({"$unwind": {"path": "$views"}})
        if object_id is not None:
            pipeline.append({"$match": {"views.entities.id": object_id}})

        if view_id is not None:
            pipeline.append({"$match": {"views.id": view_id}})
        pipeline.append({"$project": {"views.images": 1}})

        if image_type is not None:
            pipeline.append({"$unwind": {"path": "$views.images"}})
            pipeline.append({"$match": {"views.images.type": image_type}})
        return self.client.aggregate(pipeline)

    def download(self, image_list,abs_path=''):
        """Download images depending on the given image id list.

            Args:
                image_list: Result from the MongoDB.
                abs_path: absolute path for saving images.


        """
        image_list = [_ for _ in image_list]
        dic = {'Color': [], 'Depth': [], 'Mask': [], 'Normal': []}
        for images in image_list:
            for image in images['views']['images']:
                dic[image['type']].append(image['file_id'])
        for image_type, image_id_list in dic.items():
            if len(image_id_list) == 0:
                break
            print(image_type, len(image_id_list))
            path = abs_path+'/'+image_type
            if path not in os.listdir():
                os.makedirs(path)
            download_db = gridfs.GridFSBucket(
                MongoClient()[self.database], self.collection)
            for i in image_id_list:
                file = open(path + "/" + str(i) + ".png", "wb+")
                download_db.download_to_stream(file_id=i, destination=file)
        print(dic)
        print("Finish downloading.")

        # return dic



