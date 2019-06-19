from django.shortcuts import render
from semlog_vis.semlog_vis.PointCloudGenerator import PointCloudGenerator
import os
from website.settings import IMAGE_ROOT
from pymongo import MongoClient


def create_pc(request):
    """Create point clouds depending on the image clicked."""
    img_path = request.GET['img_path']
    print("point cloud dict:", request.GET.dict())
    user_id=request.session['user_id']

    if 'Color' in img_path:
        img_id = os.path.basename(os.path.normpath(img_path))[:-4]
        hex_id = int(img_id, 16)
        depth_hex_id = str(hex(hex_id + 1))[2:]
        depth_img_path=img_path.replace("Color","Depth").replace(img_id,depth_hex_id)
        depth_img_path=depth_img_path.replace(img_id,depth_hex_id)
        print(("color mode",depth_img_path))
        # depth_img_path = os.path.join(IMAGE_ROOT, user_id+'Depth', str(hex(depth_hex_id))[2:] + ".png")
    elif 'Depth' in img_path:
        depth_img_path = img_path
    elif 'Mask' in img_path:
        img_id = os.path.basename(os.path.normpath(img_path))[:-4]
        hex_id = int(img_id, 16)
        depth_hex_id = str(hex(hex_id - 1))[2:]

        depth_img_path=img_path.replace("Mask","Depth").replace(img_id,depth_hex_id)
        # depth_img_path = os.path.join(IMAGE_ROOT, user_id+'Depth', str(hex(depth_hex_id))[2:] + ".png")
    elif 'Normal' in img_path:
        img_id = os.path.basename(os.path.normpath(img_path))[:-4]
        hex_id = int(img_id, 16)
        depth_hex_id = str(hex(hex_id - 2))[2:]
        depth_img_path=img_path.replace("Normal","Depth").replace(img_id,depth_hex_id)
        # depth_img_path = os.path.join(IMAGE_ROOT, user_id+'Depth', str(hex(depth_hex_id))[2:] + ".png")

    # Calculate PointCloud
    generator = PointCloudGenerator(rgb_file=img_path, depth_file=depth_img_path,
                                    focal_length=360, scalingfactor=10)
    # Calculate 3d position
    generator.calculate()

    # Remove the alpha column
    data = generator.df[:6]
    data = data.T
    data = data.tolist()
    dic = {"point": data}

    return render(request, 'point_cloud_template.html', dic)
