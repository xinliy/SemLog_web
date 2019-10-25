import uuid
import cv2
import itertools
import os

from multiprocessing.dummy import Pool

try:
    from web.semlog_mongo.semlog_mongo.mongo import *
    from web.semlog_mongo.semlog_mongo.utils import *
    from web.semlog_vis.semlog_vis.ImageCutter import cut_object, resize_image
except Exception as e:
    os.system("git submodule init")
    os.system("git submodule update")
    from web.semlog_mongo.semlog_mongo.mongo import *
    from web.semlog_mongo.semlog_mongo.utils import *
    from web.semlog_vis.semlog_vis.ImageCutter import cut_object, resize_image


class Data():
    """Data is used to parse input from html.

        Attributes:
            form_dict: Input dict from html.
            ip: ip_address to MongoDB

    """

    def __init__(self, form_dict, ip):
        """Clean all inputs from form_dict."""

        print(form_dict)
        user_id = str(uuid.uuid4())
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
                                database_collection_list.append([db, c])
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
                    database_collection_list = [i.split("$") for i in database_collection_list]
                    print("new db-col lists:", database_collection_list)

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

        m = MongoDB(database_collection_list, ip)
        if checkbox_object_pattern == 'class':
            self.class_object_rgb_dict = m.get_color_mapping_dict(object_id_list, checkbox_object_pattern)
            object_rgb_dict = {}
            for i in list(self.class_object_rgb_dict.values()):
                for key, value in i.items():
                    object_rgb_dict[key] = value
            object_id_list = [list(i.keys()) for i in self.class_object_rgb_dict.values()]

            self.object_rgb_dict = object_rgb_dict
            self.object_id_list = list(itertools.chain(*object_id_list))
            self.class_id_list = list(self.class_object_rgb_dict.keys())
        else:
            self.object_rgb_dict = m.get_color_mapping_dict(object_id_list, checkbox_object_pattern)
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
        self.database_collection_list = database_collection_list
        self.user_id = user_id
        self.ip = ip
        self.view_list = view_list


def crop_with_all_bounding_box(object_rgb_dict, image_dir):
    """Crop full images with max boundary of all objects.

        Args:
            object_rgb_dict: A dict contains objects and their mask colors.
            image_dir: A dict contains all target images
    """

    all_rgb = list(object_rgb_dict.values())
    print("all_rgb", all_rgb)
    mask_dir = image_dir['Mask']
    rgb_dir = image_dir['Color']
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


def scan_images(image_root, folder_header, image_type_list):
    """Scan images from image_root (except bounding box).

    Args:
        image_root: Root path for images.
        folder_header: Root folder name.
        image_type_list: A list of image types.

    Returns:
        A dict with all images separated by image types.

    """
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
    """Scan local bounding box images.

    Args:
        image_root: Root path for images.
        folder_header: Root folder name.

    Returns:
        A nested dict separated by object_id and then image types.

    """
    all_folders = os.listdir(os.path.join(image_root, folder_header))
    box_folders = [i for i in all_folders if 'boundingBox' in i]
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


def get_image_path_for_bounding_box(df, object_id, image_root, folder_header):
    """Get image paths where the object exists.

    Args:
        df: Information Data frame.
        object_id: Target object.
        image_root: Root path for images.
        folder_header: Root folder name.

    Returns:
        image_dir: A dict contains qualified image paths.
        image_type_list: A list of image types.
        class_name: The class of this object.

    """
    image_type_list = list(pd.unique(df['type']))
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
    return image_dir, image_type_list, class_name


def download_bounding_box(df, object_rgb_dict, image_root, folder_header):
    """Main function for download bounding boxes.

    Args:
        df: Information Data Frame.
        object_rgb_dict: A dict maps object id to mask colors.
        image_root: Root path for images.
        folder_header: Root folder name.

    """
    def download_bounding_box_by_object(object_id, rgb):
        """Support function for downloading bounding box.

        Args:
            df: Information Data Frame.
            object_id: Target object.
            rgb: Mask color of targe object.
            image_root: Root path for images.
            folder_header: Root folder name.

        """
        image_dir, image_type_list, class_name = get_image_path_for_bounding_box(df, object_id, image_root, folder_header)
        print("<------------------------------->")
        print("Object id: %s, rgb_color: %s" % (object_id, rgb))
        print("<------------------------------->")

        for t in image_type_list:
            if t != "Color":
                continue
            folder_name = object_id + "$" + t + "$" + 'boundingBox'
            rgb_img_list = sorted(image_dir[t])
            mask_img_list = sorted(image_dir['Mask'])
            saving_folder = os.path.join(image_root, folder_header, folder_name)
            print("****length of rgb_img_list****:", len(rgb_img_list))
            if not os.path.isdir(saving_folder):
                os.makedirs(saving_folder)
            # Create and save cut images
            for rgb_img, mask_img in zip(rgb_img_list, mask_img_list):
                img_saving_path = os.path.join(
                    saving_folder, os.path.basename(rgb_img[:-4]) + "_" + class_name + '.png')
                cut_object(rgb_img, mask_img, rgb, saving_path=img_saving_path)

    for object_id, rgb in object_rgb_dict.items():
        rgb = object_rgb_dict[object_id]
        download_bounding_box_by_object(object_id, rgb)



def calculate_bounding_box(df, object_rgb_dict, image_root, folder_header):
    """Main function for calculate bounding boxes.

    Args:
        df: Information Data Frame.
        object_rgb_dict: A dict maps object id to mask colors.
        image_root: Root path for images.
        folder_header: Root folder name.

    """

    def calculate_bounding_box_by_object(object_id, rgb):
        """Support function for calculating bounding box.

        Args:
            df: Information Data Frame.
            object_id: Target object.
            rgb: Mask color of targe object.
            image_root: Root path for images.
            folder_header: Root folder name.
            bounding_box_columns: columns for storing coordinates of bounding boxes.

        """
        image_dir, image_type_list, class_name = get_image_path_for_bounding_box(df, object_id, image_root, folder_header)
        print("<------------------------------->")
        print("Object id: %s, rgb_color: %s" % (object_id, rgb))
        print("<------------------------------->")

        # Create dict and folder
        for t in image_type_list:
            if t != "Mask":
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
            count = 0

            # Create and save cut images
            for rgb_img, mask_img in zip(rgb_img_list, mask_img_list):

                # Cut object and update location to the collection
                wmin, wmax, hmin, hmax = cut_object(rgb_img, mask_img, rgb)
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


    bounding_box_columns = ['wmin', 'wmax', 'hmin', 'hmax', 'x_center', 'y_center', 'width', 'height']
    for col in bounding_box_columns:
        df[col] = ""
    for object_id, rgb in object_rgb_dict.items():
        rgb = object_rgb_dict[object_id]
        df = calculate_bounding_box_by_object(df, object_id, rgb, image_root, folder_header, bounding_box_columns)
    return df



def resize_images(image_dir, width, height, resize_type):
    """Multiprocessing function for resize images.

    Args:
        image_dir: A dict of images to be resized.
        width: Target width.
        height: Target height.
        resize_type: Stretch or sclae depending on the input.


    """
    if width == "" and height == "":
        return 0
    print("Enter resizing image.")
    image_path = []
    for key, value in image_dir.items():
        image_path = image_path + value
    print("Enter resizing.", width)
    print(image_path)
    pool = Pool(10)
    pool.starmap(resize_image, zip(
        image_path, itertools.repeat(width), itertools.repeat(height), itertools.repeat(resize_type)))
    pool.close()
    pool.join()
