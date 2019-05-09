from pymongo import MongoClient
import os
import gridfs
import shutil
from multiprocessing import Pool


class MongoDB():

    def __init__(self, database, collection, ip='127.0.0.1', port=27017):
        self.database = database
        self.collection = collection
        self.client = MongoClient(ip, port)[database][collection]
        self.ip = ip
        self.port = port

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

        # Clean the results
        pipeline.append({"$unwind": {"path": "$views.images"}})
        pipeline.append({"$replaceRoot": {"newRoot": "$views.images"}})
        return list(self.client.aggregate(pipeline))

    def download(self, image_list, abs_path=''):
        """Download images depending on the given image id list.
        Multiprocessing downloading should be added in the future.

            Args:
                image_list: Result from the MongoDB.
                abs_path: absolute path for saving images.


        """
        img_dir = {'Color': [], 'Depth': [], 'Mask': [], 'Normal': []}

        download_db = gridfs.GridFSBucket(
            MongoClient(self.ip, self.port)[self.database], self.collection)

        for t in ['Color', 'Depth', 'Mask', 'Normal']:
            path = os.path.join(abs_path, t)
            if os.path.exists(path):
                shutil.rmtree(path)
                print("removed path:", path)
            os.makedirs(path)

        for image in image_list:
            img_type = image['type']
            saving_path = os.path.join(abs_path, img_type, str(image['file_id']) + '.png')
            img_dir[img_type].append(saving_path)
            file = open(saving_path, "wb+")
            download_db.download_to_stream(file_id=image['file_id'], destination=file)

        print(img_dir)
        return img_dir

    # def download(self, image_list, abs_path=''):
    #     """Download images depending on the given image id list.
    #     Multiprocessing downloading should be added in the future.
    #
    #         Args:
    #             image_list: Result from the MongoDB.
    #             abs_path: absolute path for saving images.
    #
    #
    #     """

    def get_object_rgb(self, object_id, collection):
        """Retrieve the rgb of an object.

            Args:
                object_id(str): Id for a specific object.
                collection(str): Name of the collection for access meta data.

        """
        client = MongoClient(self.ip, self.port)[self.database][collection]["meta"]
        pipline = []
        pipline.append({"$unwind": {"path": "$env.entities"}})
        pipline.append({"$match": {"env.entities.id": object_id}})
        pipline.append({"$project": {"env.entities.mask_hex": 1}})
        h = list(client.aggregate(pipline))[0]['env']['entities']['mask_hex']
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    # @staticmethod
    # def save_json(data, path):
    #
    #     for i in data:
    #         print(i)
    #
    #     data = dumps(data,json_options=RELAXED_JSON_OPTIONS)
    #     # data=data.replace('\"','')
    #
    #     print("type",type(data))
    #     with open(path, 'w') as outfile:
    #         json.dump(data, outfile)
    #     print("Saved json data to:", path)
