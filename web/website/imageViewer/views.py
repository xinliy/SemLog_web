from django.shortcuts import render
from django.http import HttpResponse
from pymongo import MongoClient
from bson.objectid import ObjectId
import cv2

import os
import json
import shutil
import time
import uuid
import glob
from multiprocessing.dummy import Pool
import itertools
import pprint

try:
    from web.semlog_mongo.semlog_mongo.mongo import MongoDB
    from web.semlog_vis.semlog_vis.ImageCutter import cut_object, resize_image
    from web.website import settings
except Exception as e:
    print("Clone two submodules(semlog_mongo and semlog_vis) first before run the server.")
    os.system("git submodule init")
    os.system("git submodule update")
    from web.semlog_mongo.semlog_mongo.mongo import MongoDB
    from web.semlog_vis.semlog_vis.ImageCutter import cut_object, resize_image
    from web.website import settings


# Global variable
OBJECT_LOGIC = 'and'
NUM_OBJECT = 1


def convert_none(v):
    """Blank input cannot be recognized in pymongo. Convert to None."""
    return None if v == '' else v


def clean_folder(x):
    """Delete old folders."""

    t1 = time.time()
    try:
        shutil.rmtree(x)
    except Exception as e:
        print(e)
    print("Remove", x)
    print("Delete folder for:", time.time() - t1)
    return x


def search(request):
    t1 = time.time()
    if os.path.isdir(settings.IMAGE_ROOT) is False:
        print("Create image root.")
        os.makedirs(settings.IMAGE_ROOT)
    delete_path = os.listdir(settings.IMAGE_ROOT)
    delete_path = [os.path.join(settings.IMAGE_ROOT, i) for i in delete_path]
    pool = Pool(12)
    pool.map(clean_folder, delete_path)
    pool.close()
    pool.join()
    try:
        shutil.rmtree(settings.IMAGE_ROOT)
    except Exception as e:
        pass
    print("Delete all folders for:", time.time() - t1)

    return render(request, 'main.html')


def update_database_info(request):
    """Show avaiable database-collection in real time with ajax."""
    return_dict = {}
    neglect_list = ['admin', 'config', 'local']
    if request.method == 'POST':
        print("enter update database!")
        print(request.POST.dict())
        target_ip = request.POST['ip_address']
        request.session['ip']=request.POST['ip_address']
        m = MongoClient(target_ip, 27017)
        db_list = m.list_database_names()
        db_list = [i for i in db_list if i not in neglect_list]
        for db in db_list:
            return_dict[db] = [
                i for i in m[db].list_collection_names() if "." not in i]

        return_dict = json.dumps(return_dict)
        print(return_dict)

        return HttpResponse(return_dict)
    else:
        return HttpResponse("Failed!")


def show_one_image(request):
    img_path = request.GET['img_path']
    dic = {}
    dic['img_path'] = img_path
    return render(request, 'a.html', dic)


def start_search(request):
    """Read the form and search the db, download images to static folder."""
    global OBJECT_LOGIC, NUM_OBJECT
    print("<------------------------------->")
    print("START SEARCH")
    print("<------------------------------->")
    t0 = time.time()

    # Read the input from teh user.
    if request.method == "GET":
        user_id = str(uuid.uuid4())
        request.session['user_id'] = user_id
        form_dict = request.GET.dict()
        object_id_list = []
        class_id_list = []
        image_type_list = []
        bounding_box_dict = {}
        object_logic = 'and'
        time_from = None
        time_until = None
        flag_bounding_box = False
        flag_remove_background = False
        flag_stretch_background = False
        flag_add_bounding_box_to_origin = False
        ip=request.session['ip']

        print("<------------------------------->")
        print("GET INPUT", request.GET.dict())
        print("<------------------------------->")

        # Read input from the form
        percentage = form_dict['percentage']
        image_limit = int(form_dict['image_limit'])
        checkbox_object_pattern = form_dict['checkbox_object_pattern']
        flag_resize_type = form_dict['checkbox_resize_type']
        time_from = form_dict['time_from']
        time_until = form_dict['time_until']
        width = int(request.GET['width']) if request.GET['width'] != "" else ""
        height = int(request.GET['height']
                     ) if request.GET['height'] != "" else ""
        bounding_box_width = int(
            request.GET['bounding_box_width']) if request.GET['bounding_box_width'] != "" else ""
        bounding_box_height = int(request.GET['bounding_box_height']
                                  ) if request.GET['bounding_box_height'] != "" else ""

        percentage = 0.0000001 if percentage == "" else float(percentage)
        OBJECT_LOGIC = object_logic = form_dict['checkbox_object_logic']

        # Read input from forms
        for key, value in form_dict.items():
            if key.startswith("checkbox_add_bounding_box_to_origin"):
                flag_add_bounding_box_to_origin = True
            if key.startswith("checkbox_stretch_background"):
                flag_stretch_background = True
            if key.startswith("checkbox_remove_background"):
                flag_remove_background = True
            if key.startswith("checkbox_bounding_box"):
                flag_bounding_box = True
            if key.startswith('database_collection_list'):
                database_collection_list = value.split("_")
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
        database_collection_list = [
            i for i in database_collection_list if i != ""]

        # Conditional branch for class searching
        if checkbox_object_pattern == 'class':
            print("Target pattern -> class")
            class_id_list = object_id_list
            object_id_list = []
            print("Search range:", database_collection_list)
            for database_collection in database_collection_list:
                database_collection = database_collection.split("->")
                print("Enter database_collection:", database_collection)
                DB = database_collection[0]
                COLLECTION = database_collection[1]
                m = MongoDB(
                    database=DB, collection=COLLECTION + ".meta", ip=ip)
                object_id_list = object_id_list + \
                    m.get_object_by_class(class_id_list)
                # class_object_list=m.get_object_list_by_class_list(cl)
                print("Input class_id_list is:", class_id_list)
                print("Retrieved object_id_list is:", object_id_list)
                print('image_type_list', image_type_list)
        else:
            print("Target pattern -> id")
            print(object_id_list)
        # Change to list in the future
        view_id = None

        # Convert time to float
        if len(database_collection_list) != 1:
            time_from = time_until = None
        if time_from is not None:
            time_from = float(time_from)
        if time_until is not None:
            time_until = float(time_until)

        # Remove blank input
        database_collection_list = [
            i for i in database_collection_list if i != '']
        image_dir = {"Color": [], "Depth": [], "Mask": [], "Normal": []}
        image_path = []
        num_object = len(object_id_list)

        # loop all selected collections
        for database_collection in database_collection_list:
            database_collection = database_collection.split("->")
            print("Enter database_collection:", database_collection)
            database_name = database_collection[0]
            collection_name = database_collection[1]
            m = MongoClient(ip)[database_name]
            support_collection_name = collection_name + "." + user_id + "." + "info"

            support_collection_client = MongoClient(ip)[database_name][support_collection_name]
            print("Support collection created at:%s,%s,%s" %
                  (ip,database_name,support_collection_name))
            # Drop former collection, May cause problem if multi different dbs
            # are selected
            for c in m.list_collection_names():
                if ".info" in c:
                    m[c].drop()
                    print("drop old collection")
            print("object_id_list", object_id_list)

            print(ip,database_name,collection_name)

            # Search all objects and store into pyweb collection
            for object_id in object_id_list:
                m = MongoDB(ip=ip, database=database_name, collection=collection_name)
                try:
                    image_info = m.search(time_from, time_until, object_id, view_id, image_type_list, percentage,
                                                 int(
                                                     image_limit / len(database_collection_list)))

                    print("Object_id: %s,num of images: %s" %
                          (object_id, len(image_info)))
                    support_collection_client.insert_many(image_info)
                    print("Search images successfully for:", object_id)
                except Exception as e:
                    print("object_id: %s has no images in this condition!" %
                          object_id)
                    print(e)
            print("Search objects Done with:", time.time() - t0)


            # Connect the db and get download image list
            database = MongoDB(ip=ip, database=database_name, collection=collection_name)
            r = database.get_download_image_list(
                num_object=len(object_id_list), object_logic=object_logic, user_id=user_id)
            print("Download list length:",len(r))

            # Parallel download images
            pool = Pool(10)
            pool.starmap(database.download_one, zip(
                r, itertools.repeat(settings.IMAGE_ROOT), itertools.repeat(str(user_id))))
            pool.close()
            pool.join()
            print("Download objects Done with:", time.time() - t0)

            # Do object cutting
            if flag_bounding_box is True:
                print("Start generate bounding box")
                bounding_box_dict = {key: [] for key in object_id_list}
                pool = Pool(10)
                for object_id in object_id_list:
                    bounding_box_dict[object_id] = (create_bounding_box(
                        database_name, collection_name, ip, object_logic, object_id, user_id, num_object,
                        image_type_list, flag_remove_background, bounding_box_width, bounding_box_height,
                        flag_stretch_background, flag_add_bounding_box_to_origin))

            # Create dict to frontend
            for image_type in image_type_list:
                folder_path = os.path.join(
                    settings.IMAGE_ROOT, user_id + image_type)
                if os.path.isdir(folder_path) is False:
                    os.mkdir(folder_path)
                image_list = os.listdir(folder_path)
                image_dir[image_type] = [os.path.join(
                    folder_path, i) for i in image_list]
            NUM_OBJECT = len(object_id_list)

            # Resize image
            if width != "" or height != "":
                for key, value in image_dir.items():
                    image_path = image_path + value
                print("Enter resizing.", width)
                pool = Pool(10)
                pool.starmap(resize_image, zip(
                    image_path, itertools.repeat(width), itertools.repeat(height), itertools.repeat(flag_resize_type)))
                pool.close()
                pool.join()

        return render(request, 'gallery.html',
                      {"object_id_list": object_id_list, "image_dir": image_dir, "bounding_box": bounding_box_dict})


def create_bounding_box(database, collection, ip, object_logic, object_id, user_id,
                        num_object, img_type, flag_remove_background, bounding_box_width, bounding_box_height,
                        flag_stretch_background, flag_add_bounding_box_to_origin):

    client = MongoClient(ip)[database][collection +
                                       "." + user_id + "." + "info"]
    pipeline = []

    if object_logic == 'and':
        m = MongoDB(database, collection, ip)
        r = m.get_download_image_list(
            num_object, object_logic='and', user_id=user_id)
    else:
        pipeline.append({"$match": {"object": object_id}})
        pipeline.append({"$project": {"file_id": 1, "type": 1, "_id": 0}})
        r = list(client.aggregate(pipeline))

    # Type to be cut
    image_dir = {"Color": [], "Depth": [], "Mask": [], "Normal": []}
    for image_info in r:
        image_dir[image_info["type"]].append(
            os.path.join(settings.IMAGE_ROOT, user_id + image_info["type"], str(image_info["file_id"]) + ".png"))

    # Init MongoDB and get the corresponding color
    m = MongoDB(ip=ip, database=database, collection=collection)
    rgb = m.get_object_rgb(object_id, collection=collection + ".meta")

    print("<------------------------------->")
    print("Object id: %s, rgb_color: %s" % (object_id, rgb))
    print("<------------------------------->")

    # Create dict and folder
    for t in img_type:
        folder_name = user_id + "_" + object_id + "_" + t + 'boundingBox'
        folder_map = t + "_cut"
        image_dir[folder_map] = []
        rgb_img_list = sorted(image_dir[t])
        mask_img_list = sorted(image_dir['Mask'])
        saving_folder = os.path.join(settings.IMAGE_ROOT, folder_name)

        # Read resolution of origin image and add to info collection
        sample_img=cv2.imread(rgb_img_list[0])
        origin_width,origin_height=sample_img.shape[1],sample_img.shape[0]
        print(origin_width,origin_height)

        os.makedirs(saving_folder)

        # Create and save cut images
        for rgb_img, mask_img in zip(rgb_img_list, mask_img_list):
            img_saving_path = os.path.join(
                saving_folder, os.path.basename(rgb_img))

            # Cut object and update location to the collection
            wmin, wmax, hmin, hmax = cut_object(rgb_img, mask_img, rgb, saving_path=img_saving_path,
                                                flag_remove_background=flag_remove_background,
                                                width=bounding_box_width, height=bounding_box_height, flag_stretch_background=flag_stretch_background,
                                                flag_add_bounding_box_to_origin=flag_add_bounding_box_to_origin)
            client.update({"object": object_id, "file_id": ObjectId(
                os.path.basename(rgb_img)[:-4])}, {"$set": {"x_center":((wmax+wmin)/2)/origin_width,"y_center":((hmax+hmin)/2)/origin_height,"width":(wmax-wmin)/origin_width,"height":(hmax-hmin)/origin_height}})

            image_dir[folder_map].append(img_saving_path)

    image_dir = {key: image_dir[key] for key in list(
        image_dir.keys()) if key.endswith("_cut")}
    return image_dir


def make_archive(source, destination):
    """Support function for download"""

    print(source, destination)
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    print(source, destination, archive_from, archive_to)
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)


def download(request):
    """Download images as .zip file. """

    img_type = request.GET['img_type']
    user_id = request.session['user_id']
    image_root = settings.IMAGE_ROOT
    zip_target = os.path.join(image_root, user_id + img_type)
    zip_path = os.path.join(image_root, "Color_images.zip")
    make_archive(zip_target, zip_path)
    print("finish zip.")
    zip_file = open(zip_path, '+rb')
    response = HttpResponse(zip_file, content_type='application/zip')
    response[
        'Content-Disposition'] = 'attachment; filename=%s' % img_type + "_images.zip"
    response['Content-Length'] = os.path.getsize(zip_path)
    zip_file.close()

    return response
