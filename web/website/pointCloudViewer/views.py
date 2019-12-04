from django.shortcuts import render
from semlog_vis.semlog_vis.point_cloud import PointCloudGenerator
import os
from website.settings import IMAGE_ROOT
from pymongo import MongoClient
import cv2


def create_pc(request):
    """Create point clouds depending on the image clicked."""
    img_path = request.GET['img_path']
    color_folder=os.path.dirname(img_path)
    print("Color folder:",color_folder)
    color_image_list=sorted(os.listdir(color_folder))
    color_image=os.path.basename(os.path.normpath(img_path))
    if "boundingBox" in img_path:
        flag_depth_conversion=False
    else:
        flag_depth_conversion=True
    img=cv2.imread(img_path)
    width=img.shape[1]
    print(img.shape,width)
    print("point cloud dict:", request.GET.dict())
    user_id=request.session['user_id']

    if 'Color' in img_path:
        depth_folder=color_folder.replace("Color","Depth")
        depth_image_list=sorted(os.listdir(depth_folder))
        loc_index=color_image_list.index(color_image)
        depth_image=depth_image_list[loc_index]
        depth_img_path=os.path.join(depth_folder,depth_image)
    elif 'Depth' in img_path:
        depth_img_path = img_path
    elif 'Mask' in img_path:
        depth_folder=color_folder.replace("Color","Mask")
        depth_image_list=sorted(os.listdir(depth_folder))
        loc_index=color_image_list.index(color_image)
        depth_image=depth_image_list[loc_index]
        depth_img_path=os.path.join(depth_folder,depth_image)
    elif 'Normal' in img_path:
        depth_folder=color_folder.replace("Color","Normal")
        depth_image_list=sorted(os.listdir(depth_folder))
        loc_index=color_image_list.index(color_image)
        depth_image=depth_image_list[loc_index]
        depth_img_path=os.path.join(depth_folder,depth_image)


    # Calculate PointCloud
    generator = PointCloudGenerator(rgb_file=img_path, depth_file=depth_img_path,
                                    focal_length=width//2, scalingfactor=10)
    # Calculate 3d position
    print(flag_depth_conversion)
    generator.calculate(flag_depth_conversion)

    # Remove the alpha column
    data = generator.df[:6]
    data = data.T
    data = data.tolist()
    dic = {"point": data}

    return render(request, 'point_cloud_template.html', dic)
