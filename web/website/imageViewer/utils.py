from pymongo import MongoClient
import uuid
import gridfs
from web.website import settings
from bson.objectid import ObjectId
import os
import cv2
try:
    from web.semlog_mongo.semlog_mongo.mongo import MongoDB,search_single_image_by_view
    from web.semlog_vis.semlog_vis.ImageCutter import cut_object, resize_image
    from web.website import settings
except Exception as e:
    print("Clone two submodules(semlog_mongo and semlog_vis) first before run the server.")
    os.system("git submodule init")
    os.system("git submodule update")
    from web.semlog_mongo.semlog_mongo.mongo import MongoDB
    from web.semlog_vis.semlog_vis.ImageCutter import cut_object, resize_image
    from web.website import settings



class Data():
    def __init__(self,form_dict,ip):
        print(form_dict)

        user_id=str(uuid.uuid4())
        object_id_list = []
        class_id_list = []
        image_type_list = []
        view_list=[]
        bounding_box_dict = {}
        object_rgb_dict={}
        class_to_object_dict={}
        class_object_mapping={}
        encoding_dict={}
        object_logic = 'and'
        support_database_name="semlog_web"
        search_pattern='entity_search'
        time_from = None
        time_until = None
        flag_bounding_box = False
        flag_remove_background = False
        flag_stretch_background = False
        flag_add_bounding_box_to_origin = False
        flag_ignore_duplicate_image = False
        flag_apply_filtering=False
        flag_class_ignore_duplicate_image=False
        flag_class_apply_filtering=False
        class_linear_distance_tolerance=150
        class_angular_distance_tolerance=0.005
        class_num_pixels_tolerance=150
        linear_distance_tolerance=50
        angular_distance_tolerance=1

        percentage = form_dict['percentage']
        image_limit = int(form_dict['image_limit'])
        checkbox_object_pattern = form_dict['checkbox_object_pattern']
        flag_resize_type = form_dict['checkbox_resize_type']
        # time_from = form_dict['time_from']
        # time_until = form_dict['time_until']
        width = int(form_dict['width']) if form_dict['width'] != "" else ""
        height = int(form_dict['height']
                        ) if form_dict['height'] != "" else ""
        bounding_box_width = int(
            form_dict['bounding_box_width']) if form_dict['bounding_box_width'] != "" else ""
        bounding_box_height = int(form_dict['bounding_box_height']
                                    ) if form_dict['bounding_box_height'] != "" else ""
        linear_distance_tolerance=float(form_dict['linear_distance_tolerance'])
        angular_distance_tolerance=float(form_dict['angular_distance_tolerance'])
        class_linear_distance_tolerance=float(form_dict['class_linear_distance_tolerance'])
        class_angular_distance_tolerance=float(form_dict['class_angular_distance_tolerance'])
        class_num_pixels_tolerance=int(form_dict['class_num_pixels_tolerance'])

        percentage = None if percentage == "" else float(percentage)
        object_logic = form_dict['checkbox_object_logic']
        for (key, value) in form_dict.items():
            if key.startswith("checkbox_add_bounding_box_to_origin"):
                flag_add_bounding_box_to_origin = True
            if key.startswith("checkbox_stretch_background"):
                flag_stretch_background = True
            if key.startswith("checkbox_remove_background"):
                flag_remove_background = True
            if key.startswith("checkbox_bounding_box"):
                flag_bounding_box = True
            if key.startswith("checkbox_ignore_duplicate_image"):
                flag_ignore_duplicate_image = True
            if key.startswith("checkbox_apply_filtering"):
                flag_apply_filtering=True
            if key.startswith("checkbox_class_ignore_duplicate_image"):
                flag_class_ignore_duplicate_image = True
            if key.startswith("checkbox_class_ignore_duplicate_image"):
                flag_class_apply_filtering = True
            if key.startswith('checkbox_search_pattern'):
                search_pattern=value
            if key.startswith("view_object_id"):
                v=value.split('-')
                if len(v)!=4:
                    raise ValueError("The input search gramma is wrong.")
                else:
                    view_list.append(v)
            if key.startswith('database_collection_list'):
                m = MongoClient(ip, 27017)
                if value=='':
                    # Append all available collections 
                    database_collection_list=[]
                    neglect_list = ['admin', 'config', 'local','semlog_web']
                    db_list = m.list_database_names()
                    db_list = [i for i in db_list if i not in neglect_list]
                    for db in db_list:
                        for c in m[db].list_collection_names():
                            if '.' not in c:
                                database_collection_list.append(db+"$"+c)
                else:
                    # Convert all to available collections
                    database_collection_list = value.split("@")
                    database_collection_list = [
                        i for i in database_collection_list if i != ""]
                    new_list=[]
                    for database_collection in database_collection_list:
                        dc=database_collection.split("$")
                        if dc[1]=="ALL":
                            extend_list=[dc[0]+"$"+i for i in m[dc[0]].list_collection_names() if '.' not in i]
                            new_list.extend(extend_list)
                        else:
                            new_list.append(database_collection)
                    database_collection_list=sorted(list(set(new_list)))
                    print("new lsit:",database_collection_list)

            # Get multiply objects/classes from input fields
            if key.startswith('object_id') and value != '':
                object_id_list.append(value)
            if key.startswith('class_id') and value != '':
                class_id_list.append(value)
            # Get selected image type checkbox
            if key.startswith('rgb'):
                image_type_list.append('Color')
            if key.startswith('depth'):
                image_type_list.append('Depth')
            if key.startswith('normal'):
                image_type_list.append('Normal')
            if key.startswith('mask'):
                image_type_list.append('Mask')

            # Get the logic of object/class
            if key.startswith('checkbox_object_logic'):
                if value != 'and':
                    object_logic = 'or'

        # Remove blank input

        # Convert time to float
        # if len(d['database_collection_list']) != 1:
        #     time_from = time_until = None
        # if time_from is not None:
        #     time_from = float(time_from) if time_from != "" else None
        # if time_until is not None:
        #     time_until = float(time_until) if time_until != "" else None

        class_object_rgb_dict={}
        if checkbox_object_pattern == 'class':
            print("Target pattern -> class")
            class_id_list = object_id_list.copy()
            object_id_list = []
            class_object_mapping={i:[] for i in class_id_list}
            print("Search range:", database_collection_list)
            for database_collection in database_collection_list:
                database_collection = database_collection.split("$")
                print("Enter database_collection:", database_collection)
                DB = database_collection[0]
                COLLECTION = database_collection[1]
                m = MongoDB(
                    database=DB, collection=COLLECTION + ".meta", ip=ip)
                # object_id_list = object_id_list + \
                    # m.get_object_by_class(class_id_list)
                class_object_dict=m.get_object_list_by_class_list(class_id_list)
                for key,value in class_object_dict.items():
                    if value not in class_object_mapping[key]:
                        class_object_mapping[key].extend(value)
                for objects in class_object_dict.values():
                    object_id_list.extend(objects)
                for object_id in object_id_list:
                    if object_id not in object_rgb_dict.keys():
                        rgb=m.get_object_rgb(object_id) 
                        if rgb is not None:
                            object_rgb_dict[object_id]=rgb
            object_id_list=[]
            for objects in class_object_mapping.values():
                object_id_list.extend(objects)
            object_id_list=list(set(object_id_list))

            class_to_object_dict={}
            for key,value in class_object_mapping.items():
                class_to_object_dict[key]=list(set(value))
            # Encode name 
            encoding_dict={}
            for k,v in class_to_object_dict.items():
                for i,object_id in enumerate(v):
                    encoding_dict[object_id]=k+str(i+1)
            for _each_class_name,_object_id_list in class_object_mapping.items():
                class_object_rgb_dict[_each_class_name]={i:object_rgb_dict[i] for i in _object_id_list}



        self.object_id_list=object_id_list
        self.class_id_list=class_id_list
        self.image_type_list=image_type_list
        self.bounding_box_dict=[]
        self.object_rgb_dict={}
        self.object_logic=object_logic
        self.time_from=time_from
        self.time_until=time_until
        self.flag_bounding_box=flag_bounding_box
        self.flag_remove_background=flag_remove_background
        self.flag_stretch_background=flag_stretch_background
        self.flag_add_bounding_box_to_origin=flag_add_bounding_box_to_origin
        self.flag_ignore_duplicate_image=flag_ignore_duplicate_image
        self.flag_apply_filtering=flag_apply_filtering
        self.flag_class_ignore_duplicate_image=flag_class_ignore_duplicate_image
        self.flag_class_apply_filtering=flag_class_apply_filtering
        self.class_linear_distance_tolerance=class_linear_distance_tolerance
        self.class_angular_distance_tolerance=class_angular_distance_tolerance
        self.class_num_pixels_tolerance=class_num_pixels_tolerance
        self.linear_distance_tolerance=linear_distance_tolerance
        self.angular_distance_tolerance=angular_distance_tolerance
        self.search_pattern=search_pattern
        self.percentage=percentage
        self.image_limit=image_limit
        self.checkbox_object_pattern=checkbox_object_pattern
        self.flag_resize_type=flag_resize_type
        self.width=width
        self.height=height
        self.bounding_box_width=bounding_box_width
        self.bounding_box_height=bounding_box_height
        self.database_collection_list=database_collection_list
        self.class_object_rgb_dict=class_object_rgb_dict
        self.class_to_object_dict=class_to_object_dict
        self.class_object_mapping=class_object_mapping
        self.encoding_dict=encoding_dict
        self.object_rgb_dict=object_rgb_dict
        self.image_dir={"Color": [], "Depth": [], "Mask": [], "Normal": []}
        self.image_path=[]
        self.num_object=len(object_id_list)
        self.support_database_name=support_database_name
        self.support_collection_name=user_id+"."+"info"
        self.user_id=user_id
        self.ip=ip
        self.view_id=None
        self.view_list=view_list
        m=MongoClient(ip)[support_database_name]
        self.support_client = MongoDB(
        ip=ip, database=self.support_database_name, collection=self.support_collection_name)
        self.bounding_box_dict={}
        self.class_color_dict={}
        # Delete old user info
        for _collection_name in m.list_collection_names():
            try:
                m[_collection_name].drop()
            except Exception as e:
                print(e)


    def event_search(self):
        for s in self.view_list:
            print(s)
            client=MongoClient(self.ip)[s[0]][s[1]]
            m=MongoDB(s[0],s[1],ip=self.ip)
            image_info=search_single_image_by_view(client,timestamp=float(s[3]),view_id=s[2])
            print("result images:",image_info)
            download_agent=gridfs.GridFSBucket(
            MongoClient(self.ip)[s[0]], s[1])
            for each_image in image_info:
                m.download_one(download_agent,each_image,settings.IMAGE_ROOT,str(self.user_id))
        self.scann_images()
           
            



    def entity_search(self):
        for database_collection in self.database_collection_list:
            database_collection = database_collection.split("$")
            print("Enter database_collection:", database_collection)
            database_name = database_collection[0]
            collection_name = database_collection[1]
            print(database_name, collection_name)

            #------------Perform filtering function----------------#

            m = MongoDB(ip=self.ip, database=database_name,
                        collection=collection_name)
            if self.flag_apply_filtering is True:
                m.check_and_update_duplicate(self.linear_distance_tolerance,self.angular_distance_tolerance)



            if self.checkbox_object_pattern=="class" and self.flag_class_apply_filtering is True:
                print("Enter per class filtering function.")
                m.check_and_update_duplicate_per_class(class_list=self.class_id_list,
                    num_pixels_tolerance=self.class_num_pixels_tolerance,
                    linear_distance_tolerance=self.class_linear_distance_tolerance,
                    angular_distance_tolerance=self.class_angular_distance_tolerance,
                    flag_ignore_duplicate_image=self.flag_ignore_duplicate_image)


            # If no entry for object id/class, search for all
            if self.object_id_list==[] and self.checkbox_object_pattern=="id":
                self.object_id_list=m.get_all_object()
            print("object_id_list", self.object_id_list)

            # Search all objects and store into pyweb collection
            if self.object_logic=="and" and self.checkbox_object_pattern=='class':
                image_info=m.search_class_by_and(self.time_from,self.time_until,self.class_id_list,
                    image_type_list=self.image_type_list,flag_ignore_duplicate_image=self.flag_ignore_duplicate_image)
            elif self.object_logic=="and" and self.checkbox_object_pattern=='id':
                image_info=m.search_object_by_and(self.time_from,self.time_until,self.class_id_list,
                    image_type_list=self.image_type_list,flag_ignore_duplicate_image=self.flag_ignore_duplicate_image)
            else:
                try:
                    image_info = m.search(self.time_from, self.time_until, self.object_id_list, self.view_id, self.image_type_list, self.percentage,
                                          int(self.image_limit / len(self.database_collection_list)),self.flag_ignore_duplicate_image,self.flag_class_ignore_duplicate_image)


                except Exception as e:
                    print(e)
            print("Length of result:",len(image_info))
            if len(image_info)!=0:
                self.support_client.insert_many(image_info)
            download_agent=gridfs.GridFSBucket(
            MongoClient(self.ip)[database_name], collection_name)
            for each_image in image_info:
                m.download_one(download_agent,each_image,settings.IMAGE_ROOT,str(self.user_id))
        self.scann_images()

    def scann_images(self):
        # Create dict to frontend
        for image_type in self.image_type_list:
            folder_path = os.path.join(
                settings.IMAGE_ROOT, self.user_id + image_type)
            if os.path.isdir(folder_path) is False:
                os.mkdir(folder_path)
            image_list = os.listdir(folder_path)
            self.image_dir[image_type] = [os.path.join(
                folder_path, i) for i in image_list]


    def generate_bounding_box(self):
        for object_id in self.object_id_list:
            rgb=self.object_rgb_dict[object_id]
            key_value = self.encoding_dict[object_id] if self.checkbox_object_pattern=='class' else object_id
            print(object_id,key_value)
            self.bounding_box_dict[key_value] = self.create_object_bounding_box(object_id,rgb)
        sorted_keys=sorted(self.bounding_box_dict.keys())
        print(self.bounding_box_dict)
        self.bounding_box_dictionary={key:self.bounding_box_dict[key] for key in sorted_keys}

    def create_object_bounding_box(self, object_id,rgb):

        pipeline = []
        r=self.support_client.get_download_list_by_id(object_id)
        support_client=MongoClient(host=self.ip)[self.support_database_name][self.support_collection_name]
        print("length of bounding box:",len(r))

        # Type to be cut
        image_dir = {"Color": [], "Depth": [], "Mask": [], "Normal": []}
        if len(r)==0:
            return image_dir
        class_name=r[0]['class']
        for image_info in r:
            image_dir[image_info["type"]].append(
        os.path.join(settings.IMAGE_ROOT, self.user_id + image_info["type"],
        str(image_info["file_id"]) + ".png"))

        print("<------------------------------->")
        print("Object id: %s, rgb_color: %s" % (object_id, rgb))
        print("<------------------------------->")

        # Create dict and folder
        for t in self.image_type_list:
            if t!="Color":
                continue
            folder_name = self.user_id + "_" + object_id + "_" + t + 'boundingBox'
            folder_map = t + "_cut"
            image_dir[folder_map] = []
            rgb_img_list = sorted(image_dir[t])
            mask_img_list = sorted(image_dir['Mask'])
            saving_folder = os.path.join(settings.IMAGE_ROOT, folder_name)
            print("****length of rgb_img_list****:", len(rgb_img_list))

            # Read resolution of origin image and add to info collection
            if len(rgb_img_list) == 0:
                origin_width = origin_height = 0
            else:
                # print(rgb_img_list)
                sample_img = cv2.imread(rgb_img_list[0])
                origin_width, origin_height = sample_img.shape[
                    1], sample_img.shape[0]
            print("width", origin_width)
            print('height', origin_height)
            # print(origin_width,origin_height)

            if not os.path.isdir(saving_folder):
               os.makedirs(saving_folder)
            count = 0

            # Create and save cut images
            for rgb_img, mask_img in zip(rgb_img_list, mask_img_list):
                img_saving_path = os.path.join(
                    saving_folder, os.path.basename(rgb_img[:-4])+"_"+class_name+'.png')

                # Cut object and update location to the collection
                wmin, wmax, hmin, hmax = cut_object(rgb_img, mask_img, rgb, saving_path=img_saving_path,
                                                    flag_remove_background=self.flag_remove_background,
                                                    width=self.bounding_box_width, height=self.bounding_box_height, flag_stretch_background=self.flag_stretch_background,
                                                    flag_add_bounding_box_to_origin=self.flag_add_bounding_box_to_origin)
                if wmin == -1:
                    print("ignore this bounding box!")
                    continue
                wmin = 1 if wmin == 0 else wmin
                wmax = 1 if wmax == 0 else wmax
                hmin = 1 if hmin == 0 else hmin
                hmax = 1 if hmax == 0 else hmax
                if "Color" in rgb_img:
                    image_type = "Color"
                elif "Depth" in rgb_img:
                    image_type = "Depth"
                elif "Mask" in rgb_img:
                    image_type = "Mask"
                elif "Normal" in rgb_img:
                    image_type = "Normal"
                if list(support_client.find({"object": object_id, "file_id": ObjectId(
                        os.path.basename(rgb_img)[:-4]), "type": image_type})) == []:
                    support_client.insert({"object": object_id, "file_id": ObjectId(
                        os.path.basename(rgb_img)[:-4]), 'type': image_type}, {"$set": {"wmin": int(hmin), "wmax": int(hmax), "hmin": int(wmin), "hmax": int(wmax), "class": class_name, "x_center": ((wmax + wmin) / 2) / origin_width, "y_center": ((hmax + hmin) / 2) / origin_height, "width": (wmax - wmin) / origin_width, "height": (hmax - hmin) / origin_height}})

                support_client.update({"object": object_id, "file_id": ObjectId(
                    os.path.basename(rgb_img)[:-4])}, {"$set": {"wmin": int(hmin), "wmax": int(hmax), "hmin": int(wmin), "hmax": int(wmax), "class": class_name, "x_center": ((wmax + wmin) / 2) / origin_width, "y_center": ((hmax + hmin) / 2) / origin_height, "width": (wmax - wmin) / origin_width, "height": (hmax - hmin) / origin_height}})
                count = count + 1

                image_dir[folder_map].append(img_saving_path)
            print("object:", object_id)
            print('update time:', count)

        image_dir = {key: image_dir[key] for key in list(
            image_dir.keys()) if key.endswith("_cut")}
        print("object cutting finished")
        return image_dir
