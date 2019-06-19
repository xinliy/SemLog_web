from pymongo import MongoClient
import os
import gridfs
import shutil
import pprint
from multiprocessing import Pool


class MongoDB():

    def __init__(self, database, collection, ip='127.0.0.1', port=27017):
        self.database = database
        self.collection = collection
        self.client = MongoClient(ip, port)[database][collection]
        self.ip = ip
        self.port = port

    def get_download_image_list(self, num_object, object_logic='or'):
        """Get download image from pyweb collection.

        Args:
            num_object(int): number of objects in all, used only in AND logic
            object_logic('or'|'and'): OR for distinct union, AND for duplicate images with count of num_object

        Return:
            A list of dicts with file_id and image type.

        """

        client = MongoClient(self.ip, self.port)[self.database][self.collection + ".pyweb"]
        pipeline = []
        pipeline.append({"$group": {
            "_id": "$file_id",
            "count": {
                "$sum": 1
            },
            "file_id": {"$first": "$file_id"},
            "type": {"$first": "$type"}
        }})
        if object_logic == 'and':
            pipeline.append({
                "$match": {
                    "count": num_object
                }
            }),
        pipeline.append({
            "$project": {
                "file_id": 1,
                "type": 1,
                "_id": 0
            }
        })
        return list(client.aggregate(pipeline))

    def get_all_object(self):
        client=MongoClient(self.ip,self.port)[self.database][self.collection+".meta"]
        pipeline=[]
        pipeline.append({"$unwind":{"path":"$env.entities"}})
        pipeline.append({"$replaceRoot":{"newRoot":"$env.entities"}})
        pipeline.append({"$project":{"id":1,"_id":0}})
        result=list(client.aggregate(pipeline))
        result=[i['id'] for i in result]
        return result

    def get_object_by_class(self, class_list):
        """Get all objects from a given class

        Args:
            class_list:list of class names

        Returns:
            A list of object ids.

        """

        pipeline = []
        or_list = {"$match": {"$or": []}}
        pipeline.append({"$unwind": {"path": "$env.entities"}})
        for c in class_list:
            or_list['$match']['$or'].append({"env.entities.class": c})
        pipeline.append(or_list)
        pipeline.append({"$replaceRoot": {"newRoot": "$env.entities"}})
        result = list(self.client.aggregate(pipeline))
        id_list = [i['id'] for i in result]
        return id_list

    def search(self, time_from=None, time_until=None, object_id=None, view_id=None,
               image_type_list=None, percentage=0.0001,image_limit=None):
        """Input params to search for specific images.

        Args:
            time_from(float): timestamp larger or equal than
            time_until(float): timestamp smaller or equal than
            object_id(str): Id for a specific object
            view_id(str): Id for a specific view
            image_type_list(str): type for images
            percentage(float): least percentage of objects in images
            image_limit(int): number of images to be download

        Return:
            Result list from the MongoDB.

        """

        pipeline = [{"$match": {"views": {"$exists": 1}}}]

        if time_from is not None:
            pipeline.append({"$match": {"timestamp": {"$gte": time_from}}})
        if time_until is not None:
            pipeline.append({"$match": {"timestamp": {"$lte": time_until}}})

        pipeline.append({"$unwind": {"path": "$views"}})
        pipeline.append({"$match": {"views.entities.id": object_id}})
        pipeline.append({"$unwind": {"path": "$views.entities"}})
        pipeline.append({"$match": {"views.entities.id": object_id}})
        pipeline.append({"$addFields": {"views.images.object": object_id}})
        pipeline.append({"$addFields": {"views.images.size": {
            "$divide": ["$views.entities.num_pixels", {"$multiply": ["$views.res.x", "$views.res.y"]}]}}})

        if view_id is not None:
            pipeline.append({"$match": {"views.id": view_id}})
        pipeline.append({"$project": {"views.images": 1}})

        if image_type_list is not None:
            pipeline.append({"$unwind": {"path": "$views.images"}})
            or_list = {"$match": {"$or": []}}
            for image_type in image_type_list:
                or_list["$match"]["$or"].append({"views.images.type": image_type})
            pipeline.append(or_list)

        # Clean the results
        pipeline.append({"$unwind": {"path": "$views.images"}})
        pipeline.append({"$replaceRoot": {"newRoot": "$views.images"}})
        pipeline.append({"$match": {"size": {"$gte": percentage}}})

        if image_limit is not None:
            pipeline.append({"$limit":len(image_type_list)*image_limit})
        # pprint.pprint(pipeline)
        result = list(self.client.aggregate(pipeline))
        return result

    def download_one(self,image,abs_path='',header=''):
        """Multiprocessing version of download."""

        img_type=image['type']
        folder_path=os.path.join(abs_path,header+img_type)
        download_db = gridfs.GridFSBucket(
            MongoClient(self.ip, self.port)[self.database], self.collection)
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                print("make folder:",folder_path)
            except Exception as e:
                pass

        saving_path = os.path.join(abs_path, header+img_type, str(image['file_id']) + '.png')
        file = open(saving_path, "wb+")
        download_db.download_to_stream(file_id=image['file_id'], destination=file)
        return [img_type,saving_path]
        


    def download(self, image_list, abs_path='',header=''):
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
            path = os.path.join(abs_path, header+t)
            os.makedirs(path)

        for image in image_list:
            img_type = image['type']
            saving_path = os.path.join(abs_path, header+img_type, str(image['file_id']) + '.png')
            img_dir[img_type].append(saving_path)
            file = open(saving_path, "wb+")
            download_db.download_to_stream(file_id=image['file_id'], destination=file)

        return img_dir

    def get_object_rgb(self, object_id, collection):
        """Retrieve the rgb of an object.

            Args:
                object_id(str): Id for a specific object.
                collection(str): Name of the collection for access meta data.

        """
        client = MongoClient(self.ip, self.port)[self.database][collection]
        pipline = []
        pipline.append({"$unwind": {"path": "$env.entities"}})
        pipline.append({"$match": {"env.entities.id": object_id}})
        pipline.append({"$project": {"env.entities.mask_hex": 1}})
        h = list(client.aggregate(pipline))[0]['env']['entities']['mask_hex']
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
