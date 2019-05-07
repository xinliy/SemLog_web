from django.shortcuts import render
from web.website.json_loader import get_image_dir
from semlog_vis.semlog_vis.PointCloudGenerator import PointCloudGenerator


def create_pc(request):
    """Create point clouds depending on the image clicked."""
    index = 0
    img_type = ["Color", "Depth", "Mask", "Normal"]
    img_path = request.GET['img_path']
    image_dir = get_image_dir()

    # Search for the position of the image
    for t in img_type:
        if t in img_path:
            index = image_dir[t].index(img_path)
            print("The index of the clicked image is:", index)
            break
    # Locate the correspond depth image
    depth_img_path = image_dir['Depth'][index]

    # Calculate PointCloud
    generator = PointCloudGenerator(rgb_file=img_path, depth_file=depth_img_path,
                                    focal_length=320, scalingfactor=10)
    # Calculate 3d position
    generator.calculate()

    # Remove the alpha column
    data = generator.df[:6]
    data = data.T
    data = data.tolist()
    dic = {"point": data}

    return render(request, 'point_cloud_template.html', dic)
