from django.shortcuts import render
import os
from semlog_mongo.semlog_mongo.mongo import MongoDB
from semlog_vis.semlog_vis.ImageCutter import cut_object
from web.website import settings
import json
import shutil

# Global variable
IP = "mongodb+srv://admin:admin@semlog-cluster-fucxw.mongodb.net/test?retryWrites=true"
DB='SemLog'
COLLECTION='20'


def search(request):
    return render(request, 'main.html')


def start_search(request):
    """Read the form and search the db, download images to static folder."""

    def convert_none(v):
        """Blank input cannot be recognized in pymongo. Convert to None."""
        return None if v == '' else v

    timestamp = object_id = view_id = image_type = None

    # Read the input from teh user.
    if request.method == 'GET':
        timestamp = convert_none(request.GET["timestamp"])
        object_id = convert_none(request.GET['object_id'])
        view_id = convert_none(request.GET['view_id'])
        image_type = convert_none(request.GET['image_type'])

    m = MongoDB(ip=IP, database=DB, collection=COLLECTION)

    # Convert string input to be float.
    if timestamp is not None:
        timestamp = float(timestamp)
    r = m.search(timestamp=timestamp, object_id=object_id, view_id=view_id,
                 image_type=image_type)

    # Save image paths to json.
    image_dir = m.download(r, abs_path=settings.IMAGE_ROOT)
    with open(os.path.join(settings.STATIC_ROOT, "image_dir.json"), "w") as outfile:
        json.dump(image_dir, outfile)
    with open(os.path.join(settings.STATIC_ROOT, "object_id.json"), "w") as outfile:
        json.dump(object_id, outfile)

    return render(request,'gallery.html',image_dir)


def object_cut(request):
    """Cut the object out depending on the object_id."""

    # Type to be cut
    img_type=['Color','Depth','Mask','Normal']
    print("Cut button is clicked")
    with open(os.path.join(settings.STATIC_ROOT,"object_id.json"),'r') as readfile:
        object_id=json.load(readfile)

    print("The object_id is:",object_id)
    # Init MongoDB and get the corresponding color
    m = MongoDB(ip=IP, database=DB, collection=COLLECTION)
    rgb = m.get_object_rgb(object_id, collection=COLLECTION)

    # Read the image paths from image_dir
    with open(os.path.join(settings.STATIC_ROOT,"image_dir.json"),'r') as readfile:
        image_dir=json.load(readfile)

    # Create dict and folder
    for t in img_type:
        folder_name=t+'_cut'
        image_dir[folder_name]=[]
        rgb_img_list=image_dir[t]
        mask_img_list=image_dir['Mask']
        saving_path=os.path.join(settings.IMAGE_ROOT,folder_name)

        # Remove old files
        if os.path.exists(saving_path):
            shutil.rmtree(saving_path)
        os.makedirs(saving_path)

        # Create and save cut images
        for rgb_img, mask_img in zip(rgb_img_list, mask_img_list):
            img_saving_path=os.path.join(saving_path, os.path.basename(rgb_img))
            cut_object(rgb_img, mask_img, rgb, saving_path=img_saving_path)
            image_dir[folder_name].append(img_saving_path)
            print("Saved cut images at:",img_saving_path)

    # Save cut image paths to image_dir
    with open(os.path.join(settings.STATIC_ROOT, "image_dir.json"), "w") as outfile:
        json.dump(image_dir, outfile)

    print("Cut object successfully!")

    # Point to gallery_cut.html and send the image_dir to html
    return render(request,'gallery_cut.html',image_dir)

