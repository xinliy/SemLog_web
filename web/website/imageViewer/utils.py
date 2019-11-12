import uuid
import cv2
import itertools
import os
import pprint

from multiprocessing.dummy import Pool

try:
    from web.semlog_mongo.semlog_mongo.mongo import *
    from web.semlog_mongo.semlog_mongo.utils import *
    from web.semlog_vis.semlog_vis.image import *
    from web.website.settings import CONFIG_PATH
except Exception as e:
    os.system("git submodule init")
    os.system("git submodule update")
    from web.semlog_mongo.semlog_mongo.mongo import *
    from web.semlog_mongo.semlog_mongo.utils import *
    from web.semlog_vis.semlog_vis.image import *
    from web.website.settings import CONFIG_PATH


class WebsiteData():
    """Data is used to parse input from html.

        Attributes:
            form_dict: Input dict from html.
            ip: ip_address to MongoDB

    """

    def __init__(self, form_dict, ip):
        """Clean all inputs from form_dict."""

        pprint.pprint(form_dict)
        username,password=load_mongo_account(CONFIG_PATH)
        user_id = str(uuid.uuid4())
        database_collection_list = []
        object_id_list = []
        image_type_list = []
        view_list = []
        bounding_box_dict = {}
        search_pattern = 'entity_search'
        dataset_pattern = None
        flag_ignore_duplicate_image = False
        flag_apply_filtering = False
        flag_class_ignore_duplicate_image = False
        flag_class_apply_filtering = False
        flag_split_bounding_box = False
        padding_constant_color=None
        padding_type=None

        checkbox_object_pattern = form_dict['checkbox_object_pattern']
        flag_resize_type = form_dict['checkbox_resize_type']
        width = int(form_dict['width']) if form_dict['width'] != "" else ""
        height = int(form_dict['height']
                     ) if form_dict['height'] != "" else ""
        linear_distance_tolerance = float(form_dict['linear_distance_tolerance'])
        angular_distance_tolerance = float(form_dict['angular_distance_tolerance'])
        class_linear_distance_tolerance = float(form_dict['class_linear_distance_tolerance'])
        class_angular_distance_tolerance = float(form_dict['class_angular_distance_tolerance'])
        class_num_pixels_tolerance = int(form_dict['class_num_pixels_tolerance'])

        object_logic = form_dict['checkbox_object_logic']
        for (key, value) in form_dict.items():
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
            if key.startswith('checkbox_dataset_pattern'):
                dataset_pattern = value
            if key.startswith('padding_constant_color'):
                padding_constant_color=[int(i) for i in value.split(",")]
            if key.startswith("padding_type"):
                padding_type=value
            if key.startswith("view_object_id") and value != '':
                v = value.split('-')
                if len(v) != 4:
                    raise ValueError("The input search gramma is wrong.")
                else:
                    view_list.append(v)
            if key.startswith('db_id'):

                value=value.replace(" ","")
                m = MongoClient(ip, 27017,username=username,password=password)
                if value == '*.*':
                    # Append all available collections 
                    neglect_list = ['admin', 'config', 'local']
                    db_list = m.list_database_names()
                    db_list = [i for i in db_list if i not in neglect_list]
                    for db in db_list:
                        for c in m[db].list_collection_names():
                            if '.' not in c:
                                database_collection_list.append(db+"."+ c)
                elif '.' in value:
                    # Convert all to available collections
                    dc = value.split(".")
                    if dc[1] == "*":
                        extend_list = [dc[0]+"."+i  for i in m[dc[0]].list_collection_names() if '.' not in i]
                        database_collection_list.extend(extend_list)
                    else:
                        database_collection_list.append(value)

            # Get multiply objects/classes from input fields
            if key.startswith('object_id') and value != '':
                object_id_list.append(value)
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

        # Remove duplicate collecitons
        database_collection_list=list(set(database_collection_list))
        database_collection_list=[i.split(".") for i in database_collection_list]       
        print(database_collection_list)
        m = MongoDB(database_collection_list, ip,config_path=CONFIG_PATH)
        if checkbox_object_pattern == 'class':
            self.class_id_list=object_id_list.copy()
            print(object_id_list,checkbox_object_pattern)
            self.object_rgb_dict = m.get_object_rgb_dict(object_id_list, checkbox_object_pattern)
            print(self.object_rgb_dict)
            self.object_id_list = list(self.object_rgb_dict.keys())
        else:
            self.object_rgb_dict = m.get_object_rgb_dict(object_id_list, checkbox_object_pattern)
            self.object_id_list = object_id_list
            self.class_id_list = None

        self.image_type_list = image_type_list
        self.bounding_box_dict = bounding_box_dict
        self.object_logic = object_logic
        self.flag_ignore_duplicate_image = flag_ignore_duplicate_image
        self.flag_apply_filtering = flag_apply_filtering
        self.flag_class_ignore_duplicate_image = flag_class_ignore_duplicate_image
        self.flag_class_apply_filtering = flag_class_apply_filtering
        self.flag_split_bounding_box = flag_split_bounding_box
        self.similar_dict = {"linear_distance_tolerance": linear_distance_tolerance,
                             "angular_distance_tolerance": angular_distance_tolerance,
                             "class_linear_distance_tolerance": class_linear_distance_tolerance,
                             "class_angular_distance_tolerance": class_angular_distance_tolerance,
                             "class_num_pixels_tolerance": class_num_pixels_tolerance}
        self.search_pattern = search_pattern
        self.dataset_pattern = dataset_pattern
        self.checkbox_object_pattern = checkbox_object_pattern
        self.flag_resize_type = flag_resize_type
        self.width = width
        self.height = height
        self.padding_constant_color=padding_constant_color
        self.padding_type=padding_type
        self.database_collection_list = database_collection_list
        self.user_id = user_id
        self.ip = ip
        self.view_list = view_list

    def customize_image_resolution(self,image_dir):
        """Wrapper for three different resize functions for all images."""
        print(image_dir)
        if self.flag_resize_type=='pad':
            self.padding_type=convert_padding_type(self.padding_type)
            pad_all_images(image_dir,self.width,self.height,self.padding_type,self.padding_constant_color)
        else:
            resize_all_images(image_dir, self.width, self.height, self.flag_resize_type)

def convert_padding_type(padding_type):
    """Convert text input to cv2 padding type."""
    padding_type=padding_type.casefold()
    if 'constant' in padding_type:
        padding_type= cv2.BORDER_CONSTANT
    elif 'reflect' in padding_type:
        padding_type=cv2.BORDER_REFLECT
    elif 'reflect_101' in padding_type:
        padding_type=cv2.BORDER_REFLECT_101
    elif 'replicate' in padding_type:
        padding_type=cv2.BORDER_REPLICATE
    else:
        padding_type=cv2.BORDER_REFLECT
    return padding_type


