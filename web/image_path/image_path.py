import os
import pandas as pd
from itertools import chain
import platform


def scan_images(root_folder_path, root_folder_name, image_type_list,unnest=False):
    """Scan images from image_root (except bounding box).

    Args:
        root_folder_path: Root path for images.
        root_folder_name: Root folder name.
        image_type_list: A list of image types.

    Returns:
        A dict with all images separated by image types.

    """
    # Create dict to frontend
    image_dir = {i: [] for i in image_type_list}
    root_folder = os.path.join(
        root_folder_path, root_folder_name)
    
    for image_type in image_type_list:
        image_type_folder = os.path.join(root_folder, image_type)
        # if os.path.isdir(folder_path) is False:
        #     os.mkdir(folder_path)
        image_list = os.listdir(image_type_folder)

        # Change to reletive img paths in Linux system.
        if platform.system()=="Linux" and unnest is False:
            image_dir[image_type] = [os.path.join(
                root_folder_name,image_type, i) for i in image_list]
        else:
            image_dir[image_type] = [os.path.join(
                image_type_folder, i) for i in image_list]
    if unnest is True:
        result=[]
        for path_list in image_dir.values():
            result.extend(path_list)
        return result
    return image_dir


def scan_bounding_box_images(root_folder_path, root_folder_name,unnest=False):
    """Scan local bounding box images.

    Args:
        root_folder_path: Root path for images.
        root_folder_name: Root folder name.

    Returns:
        A nested dict separated by object_id and then image types.

    """
    box_root=os.path.join(root_folder_path, root_folder_name,"BoundingBoxes")
    box_folders = os.listdir(box_root)
    bounding_box_dict = {}
    for each_folder in box_folders:
        image_paths = os.listdir(os.path.join(box_root,each_folder))

        if platform.system()=="Linux" and unnest is False:
            image_abs_paths = [os.path.join( root_folder_name,"BoundingBoxes", each_folder, i) for i in image_paths]
        else:
            image_abs_paths = [os.path.join(box_root, each_folder, i) for i in image_paths]
        name_list = each_folder.split("$")
        object_id = name_list[0]
        image_type = name_list[1]
        if object_id not in bounding_box_dict.keys():
            bounding_box_dict[object_id] = {}

        bounding_box_dict[object_id][image_type] = image_abs_paths
    
    if unnest is True:
        result=[]
        for type_path_list in bounding_box_dict.values():
            result.extend(type_path_list.values())
        result=list(chain(*result))
        return result

    return bounding_box_dict


def get_image_path_for_bounding_box(df, object_id, root_folder_path, root_folder_name):
    """Get image paths where the object exists.

    Args:
        df: Information Data frame.
        object_id: Target object.
        root_folder_path: Root path for images.
        root_folder_name: Root folder name.

    Returns:
        image_dir: A dict contains qualified image paths.
        image_type_list: A list of image types.
        class_name: The class of this object.

    """
    image_type_list = list(pd.unique(df['type']))
    r = df[df['object'] == object_id][['file_id', 'type', 'class']].to_dict('records')
    # Type to be cut
    image_dir = {i: [] for i in image_type_list}
    class_name = df[df.object == object_id]['class'][:1].values[0]
    if len(r) == 0:
        return df
    for image_info in r:
        image_dir[image_info["type"]].append(
            os.path.join(root_folder_path, root_folder_name, image_info["type"],
                         str(image_info["file_id"]) + ".png"))
    return image_dir, image_type_list, class_name
