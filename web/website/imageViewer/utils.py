from pymongo import MongoClient
import uuid
import gridfs
from web.website import settings
from bson.objectid import ObjectId
import os
import cv2
import pandas as pd
import itertools
from collections import ChainMap

try:
    from web.semlog_mongo.semlog_mongo.mongo import *
    from web.semlog_vis.semlog_vis.ImageCutter import cut_object, resize_image
    from web.website import settings
except Exception as e:
    print("Clone two submodules(semlog_mongo and semlog_vis) first before run the server.")
    os.system("git submodule init")
    os.system("git submodule update")
    from web.semlog_mongo.semlog_mongo.mongo import *
    from web.semlog_vis.semlog_vis.ImageCutter import cut_object, resize_image
    from web.website import settings


class Data():
    def __init__(self, form_dict, ip):
        print(form_dict)

        user_id = str(uuid.uuid4())
        object_id_list = []
        class_id_list = []
        image_type_list = []
        view_list = []
        bounding_box_dict = {}
        object_rgb_dict = {}
        class_to_object_dict = {}
        class_object_mapping = {}
        encoding_dict = {}
        object_logic = 'and'
        # support_database_name="semlog_web"
        search_pattern = 'entity_search'
        flag_bounding_box = False
        flag_remove_background = False
        flag_stretch_background = False
        flag_add_bounding_box_to_origin = False
        flag_ignore_duplicate_image = False
        flag_apply_filtering = False
        flag_class_ignore_duplicate_image = False
        flag_class_apply_filtering = False
        flag_split_bounding_box = False
        class_linear_distance_tolerance = 150
        class_angular_distance_tolerance = 0.005
        class_num_pixels_tolerance = 150
        linear_distance_tolerance = 50
        angular_distance_tolerance = 1

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
        linear_distance_tolerance = float(form_dict['linear_distance_tolerance'])
        angular_distance_tolerance = float(form_dict['angular_distance_tolerance'])
        class_linear_distance_tolerance = float(form_dict['class_linear_distance_tolerance'])
        class_angular_distance_tolerance = float(form_dict['class_angular_distance_tolerance'])
        class_num_pixels_tolerance = int(form_dict['class_num_pixels_tolerance'])

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
                flag_apply_filtering = True
            if key.startswith("checkbox_class_ignore_duplicate_image"):
                flag_class_ignore_duplicate_image = True
            if key.startswith("checkbox_class_ignore_duplicate_image"):
                flag_class_apply_filtering = True
            if key.startswith("checkbox_split_bounding_box"):
                flag_split_bounding_box = True
            if key.startswith('checkbox_search_pattern'):
                search_pattern = value
            if key.startswith("view_object_id") and value != '':
                v = value.split('-')
                if len(v) != 4:
                    raise ValueError("The input search gramma is wrong.")
                else:
                    view_list.append(v)
            if key.startswith('database_collection_list'):
                m = MongoClient(ip, 27017)
                if value == '':
                    # Append all available collections 
                    database_collection_list = []
                    neglect_list = ['admin', 'config', 'local', 'semlog_web']
                    db_list = m.list_database_names()
                    db_list = [i for i in db_list if i not in neglect_list]
                    for db in db_list:
                        for c in m[db].list_collection_names():
                            if '.' not in c:
                                database_collection_list.append(db + "$" + c)
                else:
                    # Convert all to available collections
                    database_collection_list = value.split("@")
                    database_collection_list = [
                        i for i in database_collection_list if i != ""]
                    new_list = []
                    for database_collection in database_collection_list:
                        dc = database_collection.split("$")
                        if dc[1] == "ALL":
                            extend_list = [dc[0] + "$" + i for i in m[dc[0]].list_collection_names() if '.' not in i]
                            new_list.extend(extend_list)
                        else:
                            new_list.append(database_collection)
                    database_collection_list = sorted(list(set(new_list)))
                    print("new db-col lists:", database_collection_list)

            # Get multiply objects/classes from input fields
            if key.startswith('object_id') and value != '':
                object_id_list.append(value)
            # if key.startswith('class_id') and value != '':
            #     class_id_list.append(value)
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

        if checkbox_object_pattern == 'class':
            self.class_object_rgb_dict = get_color_mapping_dict(ip, database_collection_list, object_id_list,
                                                                checkbox_object_pattern)
            object_rgb_dict = {}
            for i in list(self.class_object_rgb_dict.values()):
                for key, value in i.items():
                    object_rgb_dict[key] = value
            object_id_list = [list(i.keys()) for i in self.class_object_rgb_dict.values()]

            self.object_rgb_dict = object_rgb_dict
            self.object_id_list = list(itertools.chain(*object_id_list))
            self.class_id_list = list(self.class_object_rgb_dict.keys())
        else:
            self.object_rgb_dict = get_color_mapping_dict(ip, database_collection_list, object_id_list,
                                                          checkbox_object_pattern)
            self.object_id_list = object_id_list
            self.class_id_list = None

        self.image_type_list = image_type_list
        self.bounding_box_dict = bounding_box_dict
        self.object_logic = object_logic
        self.flag_bounding_box = flag_bounding_box
        self.flag_remove_background = flag_remove_background
        self.flag_stretch_background = flag_stretch_background
        self.flag_add_bounding_box_to_origin = flag_add_bounding_box_to_origin
        self.flag_ignore_duplicate_image = flag_ignore_duplicate_image
        self.flag_apply_filtering = flag_apply_filtering
        self.flag_class_ignore_duplicate_image = flag_class_ignore_duplicate_image
        self.flag_class_apply_filtering = flag_class_apply_filtering
        self.flag_split_bounding_box = flag_split_bounding_box
        self.class_linear_distance_tolerance = class_linear_distance_tolerance
        self.class_angular_distance_tolerance = class_angular_distance_tolerance
        self.class_num_pixels_tolerance = class_num_pixels_tolerance
        self.linear_distance_tolerance = linear_distance_tolerance
        self.angular_distance_tolerance = angular_distance_tolerance
        self.search_pattern = search_pattern
        self.percentage = percentage
        self.image_limit = image_limit
        self.checkbox_object_pattern = checkbox_object_pattern
        self.flag_resize_type = flag_resize_type
        self.width = width
        self.height = height
        self.database_collection_list = database_collection_list
        self.user_id = user_id
        self.ip = ip
        self.view_list = view_list


def crop_with_all_bounding_box(object_rgb_dict, image_dir):
    all_rgb = list(object_rgb_dict.values())
    print("all_rgb", all_rgb)
    mask_dir = image_dir['Mask']
    rgb_dir = image_dir['Color']
    default_shape = cv2.imread(mask_dir[1])
    coordinate_list = []

    for each_mask in mask_dir:
        hmin_list = []
        hmax_list = []
        wmin_list = []
        wmax_list = []
        for each_color in all_rgb:
            wmin, wmax, hmin, hmax = cut_object(each_mask, each_mask, each_color)
            hmin_list.append(hmin)
            hmax_list.append(hmax)
            wmin_list.append(wmin)
            wmax_list.append(wmax)
        hmin = min([i for i in hmin_list if i != -1])
        hmax = max(hmax_list)
        wmin = min([i for i in wmin_list if i != -1])
        wmax = max(wmax_list)
        coordinate_list.append([hmin, hmax, wmin, wmax])

    for (each_rgb, c) in zip(rgb_dir, coordinate_list):
        img = cv2.imread(each_rgb)
        img = img[c[2]:c[3], c[0]:c[1]]
        cv2.imwrite(each_rgb, img)


def event_search(ip, view_list):
    for s in view_list:

        print(s)
        client = MongoClient(ip)[s[0]][s[1]]
        m = MongoDB(s[0], s[1], ip=ip)
        image_info = search_single_image_by_view(client, timestamp=float(s[2]), view_id=s[3])

        info_df = pd.DataFrame(image_info)
        if 'df' in locals():
            df = df.append(info_df, ignore_index=True)
        else:
            df = info_df

        print("result images:", image_info)
        # download_agent=gridfs.GridFSBucket(
        # MongoClient(ip)[s[0]], s[1])
        # for each_image in image_info:
        #     m.download_one(download_agent,each_image,settings.IMAGE_ROOT,image_unique_name)
        # scann_images()
    df['file_id'] = df['file_id'].astype(str)
    return df


def apply_similar_filtering(ip, database_collection_list, flag_apply_filtering, flag_class_apply_filtering,
                            linear_distance_tolerance, angular_distance_tolerance,
                            class_id_list, class_num_pixels_tolerance, class_linear_distance_tolerance,
                            class_angular_distance_tolerance):
    for database_collection in database_collection_list:
        database_collection = database_collection.split("$")
        print("Enter database_collection:", database_collection)
        database_name = database_collection[0]
        collection_name = database_collection[1]
        print(database_name, collection_name)

        # ------------Perform filtering function----------------#

        m = MongoDB(ip=ip, database=database_name,
                    collection=collection_name)
        if flag_apply_filtering is True:
            m.check_and_update_similar(linear_distance_tolerance, angular_distance_tolerance)
        if class_id_list is not None and flag_class_apply_filtering is True:
            print("Enter per class filtering function.")
            m.check_and_update_similar_per_class(class_list=class_id_list,
                                                 num_pixels_tolerance=class_num_pixels_tolerance,
                                                 linear_distance_tolerance=class_linear_distance_tolerance,
                                                 angular_distance_tolerance=class_angular_distance_tolerance)


def entity_search(ip, database_collection_list, object_id_list, class_id_list, object_pattern, object_logic,
                  image_type_list, flag_ignore_similar_image, flag_class_ignore_similar_image):
    '''Function for searching MongoDB with entity conditions.
        
        Args:
            ip: The ip address of MongoDB, ex: '127.0.0.1'
            database_collection_list: a list of databases and collections, ex: ['db1$collection2','db13$collection10']
            object_id_list: a list of object_ids
            class_id_list: a list of classes
            object_pattern('id'|'class'): Search with object ids or classes
            object_logic('and'|'or'): Search with which logic
            image_type_list(['Color',"Depth","Mask","Normal"]): type of images
            flag_ignore_similar_image(True|False)
            flag_class_ignore_similar_image(True|False)

        Return:
            A pandas Dataframe contains all qualified images
        '''
    for database_collection in database_collection_list:
        database_collection = database_collection.split("$")
        print("Enter database_collection:", database_collection)
        database_name = database_collection[0]
        collection_name = database_collection[1]
        print(database_name, collection_name)

        # ------------Perform filtering function----------------#

        m = MongoDB(ip=ip, database=database_name,
                    collection=collection_name)

        # If no entry for object id/class, search for all
        if object_id_list == [] and object_pattern == "id":
            object_id_list = m.get_all_object()
            print("object_id_list", object_id_list)

        if object_logic == "and" and object_pattern == 'class':
            image_info = m.search_class_by_and(class_id_list=class_id_list,
                                               image_type_list=image_type_list,
                                               flag_ignore_duplicate_image=flag_ignore_similar_image)
        elif object_logic == "and" and object_pattern == 'id':
            image_info = m.search_object_by_and(object_id_list=object_id_list,
                                                image_type_list=image_type_list,
                                                flag_ignore_duplicate_image=flag_ignore_similar_image)
        else:
            try:
                image_info = m.search(object_id_list=object_id_list, image_type_list=image_type_list,
                                      flag_ignore_duplicate_image=flag_ignore_similar_image,
                                      flag_ignore_duplicate_object=flag_class_ignore_similar_image)
            except Exception as e:
                print(e)
        print("Length of result:", len(image_info))
        if len(image_info) != 0:
            info_df = pd.DataFrame(image_info)
            if 'df' in locals():
                df = df.append(info_df, ignore_index=True)
            else:
                df = info_df
        print("df:", df.shape)
    df['file_id'] = df['file_id'].astype(str)
    df.to_csv('test.csv')
    return df


def scan_images(image_root, folder_header, image_type_list):
    # Create dict to frontend
    image_dir = {i: [] for i in image_type_list}
    root_folder = os.path.join(
        image_root, folder_header)
    for image_type in image_type_list:
        image_type_folder = os.path.join(root_folder, image_type)
        # if os.path.isdir(folder_path) is False:
        #     os.mkdir(folder_path)
        image_list = os.listdir(image_type_folder)
        image_dir[image_type] = [os.path.join(
            image_type_folder, i) for i in image_list]
    return image_dir


def scan_bounding_box_images(image_root, folder_header):
    all_folders = os.listdir(os.path.join(image_root, folder_header))
    box_folders = [i for i in all_folders if 'boundingBox' in i]
    object_id_list = []
    image_type_list = []
    boundingBox_dict = {}
    for each_folder in box_folders:
        image_paths = os.listdir(os.path.join(image_root, folder_header, each_folder))
        image_abs_paths = [os.path.join(image_root, folder_header, each_folder, i) for i in image_paths]
        name_list = each_folder.split("$")
        print(name_list)
        object_id = name_list[0]
        image_type = name_list[1]
        if object_id not in boundingBox_dict.keys():
            boundingBox_dict[object_id] = {}
        boundingBox_dict[object_id][image_type] = image_abs_paths
    return boundingBox_dict


def generate_bounding_box(df, object_rgb_dict, image_root, folder_header):
    bounding_box_dict = {}
    bounding_box_columns = ['wmin', 'wmax', 'hmin', 'hmax', 'x_center', 'y_center', 'width', 'height']
    for col in bounding_box_columns:
        df[col] = ""

    for object_id, rgb in object_rgb_dict.items():
        rgb = object_rgb_dict[object_id]
        df = create_object_bounding_box(df, object_id, rgb, image_root, folder_header)
    return df


def create_object_bounding_box(df, object_id, rgb, image_root, folder_header):
    image_type_list = list(pd.unique(df['type']))
    bounding_box_columns = ['wmin', 'wmax', 'hmin', 'hmax', 'x_center', 'y_center', 'width', 'height']
    r = df[df['object'] == object_id][['file_id', 'type', 'class']].to_dict('records')
    print("length of bounding box:", len(r))
    # Type to be cut
    image_dir = {i: [] for i in image_type_list}
    class_name = df[df.object == object_id]['class'][:1].values[0]
    if len(r) == 0:
        return df
    for image_info in r:
        image_dir[image_info["type"]].append(
            os.path.join(image_root, folder_header, image_info["type"],
                         str(image_info["file_id"]) + ".png"))

    print("<------------------------------->")
    print("Object id: %s, rgb_color: %s" % (object_id, rgb))
    print("<------------------------------->")

    # Create dict and folder
    for t in image_type_list:
        if t != "Color":
            continue
        folder_name = object_id + "$" + t + "$" + 'boundingBox'
        rgb_img_list = sorted(image_dir[t])
        mask_img_list = sorted(image_dir['Mask'])
        saving_folder = os.path.join(image_root, folder_header, folder_name)
        print("****length of rgb_img_list****:", len(rgb_img_list))

        # Read resolution of origin image and add to info collection
        if len(rgb_img_list) == 0:
            origin_width = origin_height = 0
        else:
            sample_img = cv2.imread(rgb_img_list[0])
            origin_width, origin_height = sample_img.shape[
                                              1], sample_img.shape[0]
        print("width", origin_width)
        print('height', origin_height)

        if not os.path.isdir(saving_folder):
            os.makedirs(saving_folder)
        count = 0

        # Create and save cut images
        for rgb_img, mask_img in zip(rgb_img_list, mask_img_list):
            img_saving_path = os.path.join(
                saving_folder, os.path.basename(rgb_img[:-4]) + "_" + class_name + '.png')

            # Cut object and update location to the collection
            wmin, wmax, hmin, hmax = cut_object(rgb_img, mask_img, rgb, saving_path=img_saving_path)
            if wmin == -1:
                print("ignore this bounding box!")
                continue
            wmin = 1 if wmin == 0 else wmin
            wmax = 1 if wmax == 0 else wmax
            hmin = 1 if hmin == 0 else hmin
            hmax = 1 if hmax == 0 else hmax

            wmin = int(hmin)
            wmax = int(hmax)
            hmin = int(wmin)
            hmax = int(wmax)
            x_center = ((wmax + wmin) / 2) / origin_width
            y_center = ((hmax + hmin) / 2) / origin_height
            width = (wmax - wmin) / origin_width
            height = (hmax - hmin) / origin_height
            update_values = [wmin, wmax, hmin, hmax, x_center, y_center, width, height]
            file_id = os.path.basename(rgb_img)[:-4]

            if df.loc[(df.object == object_id) & (df.file_id == file_id), bounding_box_columns]['wmin'].values == "":
                df.loc[(df.object == object_id) & (df.file_id == file_id), bounding_box_columns] = update_values

            count = count + 1

        print("object:", object_id)
        print('update time:', count)

    print("object cutting finished")
    return df
