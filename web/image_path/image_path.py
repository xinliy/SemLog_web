import os
import pandas as pd
from itertools import chain
import platform
import shutil
from web.image_path.utils import *


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

# def scan_scan_images(root_folder_path,root_folder_name):
#     scan_root=os.path.join(root_folder_path, root_folder_name,"scans")
#     if not os.path.isdir(scan_root):
#         return {}
#     scan_folders = os.listdir(scan_root)
#     bounding_box_dict = {}
#     for each_class_folder in scan_folders:
#         type_folder_paths=os.listdir(os.path.join(scan_root,each_class_folder))

        # if platform.system()=="Linux":


def scan_bb_images(root_folder_path, root_folder_name,unnest=False,folder_name="BoundingBoxes"):
    """Scan local bounding box images.

    Args:
        root_folder_path: Root path for images.
        root_folder_name: Root folder name.

    Returns:
        A nested dict separated by object_id and then image types.

    """
    box_root=os.path.join(root_folder_path, root_folder_name,folder_name)
    if not os.path.isdir(box_root):
        return {}
    box_folders = os.listdir(box_root)
    bounding_box_dict = {}
    for each_folder in box_folders:
        image_paths = os.listdir(os.path.join(box_root,each_folder))

        if platform.system()=="Linux" and unnest is False:
            image_abs_paths = [os.path.join( root_folder_name,folder_name, each_folder, i) for i in image_paths]
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

def arrange_scan_by_class(scan_df,root_folder_path,root_folder_name):

    scan_root_folder=os.path.join(root_folder_path,root_folder_name,'scans')

    # Create scan folder
    create_a_folder(scan_root_folder)

    # Create sub folders by class name
    class_list=list(scan_df['class'].unique())
    class_path_list=[os.path.join(scan_root_folder,i) for i in class_list]
    map(create_a_folder,class_path_list)

    # Retrieve image type list via local folder name
    image_type_list=[i for i in
                     os.listdir(os.path.join(root_folder_path,root_folder_name))
                     if i in ['Color','Depth','Normal','Mask','Unlit']]

    # Iterate rows in scan_df and move images to the right folder
    for _,row in scan_df.iterrows():

        # Create the target folder
        new_image_folder=os.path.join(scan_root_folder,row['class']+"$"+row['type']+"$"+"scans")
        create_a_folder(new_image_folder)

        old_image_path=os.path.join(root_folder_path,root_folder_name,row['type'],str(row['file_id'])+'.png')
        new_image_path=os.path.join(new_image_folder,str(row['file_id'])+'.png')

        shutil.move(old_image_path,new_image_path)




