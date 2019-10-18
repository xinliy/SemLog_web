from django.shortcuts import render
from django.http import HttpResponse
from pymongo import MongoClient
from bson.objectid import ObjectId
import cv2
import gridfs
import pandas as pd

import os
import json
import shutil
import time
import uuid
import glob
from multiprocessing.dummy import Pool
import itertools
import pprint

from web.website.imageViewer.utils import *

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
    print(os.listdir(x))
    print("Remove", x)
    print("Delete folder for:", time.time() - t1)
    return x


def search(request):
    t1 = time.time()
    if os.path.isdir(settings.IMAGE_ROOT) is False:
        print("Create image root.")
        os.makedirs(settings.IMAGE_ROOT)
    delete_path = os.listdir(settings.IMAGE_ROOT)
    delete_path = [os.path.join(settings.IMAGE_ROOT, i)
                   for i in delete_path]
    try:
        pool = Pool(12)
        pool.map(clean_folder, delete_path)
        pool.close()
        pool.join()
    except Exception as e:
        print(e)
        print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        pass
    try:
        shutil.rmtree(settings.IMAGE_ROOT)
    except Exception as e:
        print(e)
    print("Delete all folders for:", time.time() - t1)
    if os.path.isdir(settings.IMAGE_ROOT) is False:
        print("Create image root.")
        os.makedirs(settings.IMAGE_ROOT)

    return render(request, 'main.html')

def training(request):
    return render(request,'training_setting.html')

def start_training(request):
    training_dict=request.GET.dict()

    return HttpResponse('ok')

def update_database_info(request):
    """Show avaiable database-collection in real time with ajax."""
    return_dict = {}
    neglect_list = ['admin', 'config', 'local']
    if request.method == 'POST':
        print("enter update database!")
        print(request.POST.dict())
        target_ip = request.POST['ip_address']
        request.session['ip'] = request.POST['ip_address']
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
    return render(request, 'origin_size.html', dic)


def start_search(request):
    """Read the form and search the db, download images to static folder."""
    global OBJECT_LOGIC, NUM_OBJECT
    print("<------------------------------->")
    print("START SEARCH")
    print("<------------------------------->")
    t0 = time.time()

    # Read the input from teh user.
    if request.method == "GET":
        form_dict = request.GET.dict()
        d=Data(form_dict,request.session['ip'])
        request.session['user_id'] = d.user_id
        request.session['class_object_rgb_dict']=d.class_object_rgb_dict
        print("Input class_id_list is:", d.class_id_list)
        print("Retrieved object_id_list is:", d.object_id_list)
        print("class_object_mapping:",d.class_object_mapping)
        print('image_type_list:', d.image_type_list)
        print("rgb_dict:",d.object_rgb_dict)
        print("encoding_dict:",d.encoding_dict)
        print("class_object_rgb_dict:",d.class_object_rgb_dict) 

        if d.object_id_list==[]:
            return HttpResponse("<h1 class='ui header'>No result is found in the given scope!</h1>")
        # Create support db-collection to store processed data



        # loop all selected collections




        # def chunker_list(seq, size):
        #     return (seq[i::size] for i in range(size))
        # # Connect the db and get download image list
            
        # r = support_client.get_download_image_list()
        # print("Download list length:", len(r))
        # if len(r)>4000:
        #     r_list=chunker_list(r,5)
        #     for each_patch in r_list:
        #         print("patch length:",len(each_patch))
        #         pool = Pool(5)
        #         pool.starmap(m.download_one, zip(
        #         each_patch, itertools.repeat(settings.IMAGE_ROOT), itertools.repeat(str(user_id))))
        #         pool.close()
        #         pool.join()
        # else:
        #     # Parallel download images
        #     pool = Pool(5)
        #     pool.starmap(m.download_one, zip(
        #     r, itertools.repeat(settings.IMAGE_ROOT), itertools.repeat(str(user_id))))
        #     pool.close()
        #     pool.join()
        # for each_image in r:
            # m.download_one(each_image,settings.IMAGE_ROOT,str(user_id))
        print("Download objects Done with:", time.time() - t0)



        # Resize image
        if d.width != "" or d.height != "":
            for key, value in d.image_dir.items():
                d.image_path = d.image_path + value
            print("Enter resizing.", d.width)
            # print(image_path)
            pool = Pool(10)
            pool.starmap(resize_image, zip(
                d.image_path, itertools.repeat(d.width), itertools.repeat(d.height), itertools.repeat(d.flag_resize_type)))
            pool.close()
            pool.join()

        # Do object cutting
        if d.flag_bounding_box is True:
            d.generate_bounding_box()
        else:
            d.bounding_box_dictionary={}
        #     print("Start generate bounding box")
        #     bounding_box_dict = {}
        #     class_color_dict={}
        #     # pool = Pool(10)
        #     # pool.starmap(create_bounding_box)
        #     for object_id in object_id_list:
        #         rgb=object_rgb_dict[object_id]
        #         key_value = encoding_dict[object_id] if checkbox_object_pattern=='class' else object_id
        #         print(object_id,key_value)
        #         bounding_box_dict[key_value] = (create_bounding_box(
        #                                                             support_database_name, support_collection_name, ip, object_id,rgb, user_id,
        #                                                             image_type_list, flag_remove_background, bounding_box_width, bounding_box_height,
        #                                                             flag_stretch_background, flag_add_bounding_box_to_origin))
        #     sorted_keys=sorted(bounding_box_dict.keys())
        #     bounding_box_dictionary={key:bounding_box_dict[key] for key in sorted_keys}
        # else:
        #     bounding_box_dictionary={}



        return render(request, 'gallery.html',
                      {"object_id_list": d.object_id_list, "image_dir": d.image_dir, "bounding_box": d.bounding_box_dictionary})


def create_bounding_box(support_database, support_collection, ip, object_id,rgb, user_id, img_type, flag_remove_background, bounding_box_width, bounding_box_height,
                        flag_stretch_background, flag_add_bounding_box_to_origin):

    support_database_name = "semlog_web"
    support_collection_name = user_id + "." + "info"
    support_client = MongoDB(database=support_database_name,collection=support_collection_name,ip=ip)
    pipeline = []
    r=support_client.get_download_list_by_id(object_id)
    support_client=MongoClient(host=ip)[support_database_name][support_collection_name]
    print("length of bounding box:",len(r))


    # if object_logic == 'and':
    #     m = MongoDB(support_database_name, support_collection_name, ip)
    #     r = m.get_download_list_by_id()
    # else:
    #     pipeline.append({"$match": {"object": object_id}})
    #     pipeline.append({"$project": {"file_id": 1, "type": 1, "_id": 0}})
    #     r = list(support_client.aggregate(pipeline))

    # Type to be cut

    image_dir = {"Color": [], "Depth": [], "Mask": [], "Normal": []}
    if len(r)==0:
        return image_dir
    class_name=r[0]['class']
    for image_info in r:
        image_dir[image_info["type"]].append(
    os.path.join(settings.IMAGE_ROOT, user_id + image_info["type"],
    str(image_info["file_id"]) + ".png"))


    # Init MongoDB and get the corresponding color, class name
    # m = MongoDB(ip=ip, database=database, collection=collection)
    # rgb = m.get_object_rgb(object_id, collection=collection + ".meta")
    # class_name = MongoDB(ip=ip, database=database, collection=collection +
                         # ".meta").get_class_by_object_id(object_id)

    print("<------------------------------->")
    print("Object id: %s, rgb_color: %s" % (object_id, rgb))
    print("<------------------------------->")

    # Create dict and folder
    for t in img_type:
        # if t!="Color":
        #     continue
        folder_name = user_id + "_" + object_id + "_" + t + 'boundingBox'
        folder_map = t + "_cut"
        image_dir[folder_map] = []
        rgb_img_list = sorted(image_dir[t])
        mask_img_list = sorted(image_dir['Mask'])
        saving_folder = os.path.join(settings.IMAGE_ROOT, folder_name)
        print("****length of rgb_img_list****:", len(rgb_img_list))

        # Read resolution of origin image and add to info collection
        if len(rgb_img_list) == 0:
            origin_width = origin_height = 0
        else:
            # print(rgb_img_list)
            sample_img = cv2.imread(rgb_img_list[0])
            origin_width, origin_height = sample_img.shape[
                1], sample_img.shape[0]
        print("width", origin_width)
        print('height', origin_height)
        # print(origin_width,origin_height)

        if not os.path.isdir(saving_folder):
           os.makedirs(saving_folder)
        count = 0

        # Create and save cut images
        for rgb_img, mask_img in zip(rgb_img_list, mask_img_list):
            img_saving_path = os.path.join(
                saving_folder, os.path.basename(rgb_img[:-4])+"_"+class_name+'.png')

            # Cut object and update location to the collection
            wmin, wmax, hmin, hmax = cut_object(rgb_img, mask_img, rgb, saving_path=img_saving_path,
                                                flag_remove_background=flag_remove_background,
                                                width=bounding_box_width, height=bounding_box_height, flag_stretch_background=flag_stretch_background,
                                                flag_add_bounding_box_to_origin=flag_add_bounding_box_to_origin)
            if wmin == -1:
                print("ignore this bounding box!")
                continue
            wmin = 1 if wmin == 0 else wmin
            wmax = 1 if wmax == 0 else wmax
            hmin = 1 if hmin == 0 else hmin
            hmax = 1 if hmax == 0 else hmax
            if "Color" in rgb_img:
                image_type = "Color"
            elif "Depth" in rgb_img:
                image_type = "Depth"
            elif "Mask" in rgb_img:
                image_type = "Mask"
            elif "Normal" in rgb_img:
                image_type = "Normal"
            if list(support_client.find({"object": object_id, "file_id": ObjectId(
                    os.path.basename(rgb_img)[:-4]), "type": image_type})) == []:
                support_client.insert({"object": object_id, "file_id": ObjectId(
                    os.path.basename(rgb_img)[:-4]), 'type': image_type}, {"$set": {"wmin": int(hmin), "wmax": int(hmax), "hmin": int(wmin), "hmax": int(wmax), "class": class_name, "x_center": ((wmax + wmin) / 2) / origin_width, "y_center": ((hmax + hmin) / 2) / origin_height, "width": (wmax - wmin) / origin_width, "height": (hmax - hmin) / origin_height}})

            support_client.update({"object": object_id, "file_id": ObjectId(
                os.path.basename(rgb_img)[:-4])}, {"$set": {"wmin": int(hmin), "wmax": int(hmax), "hmin": int(wmin), "hmax": int(wmax), "class": class_name, "x_center": ((wmax + wmin) / 2) / origin_width, "y_center": ((hmax + hmin) / 2) / origin_height, "width": (wmax - wmin) / origin_width, "height": (hmax - hmin) / origin_height}})
            count = count + 1

            image_dir[folder_map].append(img_saving_path)
        print("object:", object_id)
        print('update time:', count)

    image_dir = {key: image_dir[key] for key in list(
        image_dir.keys()) if key.endswith("_cut")}
    print("object cutting finished")
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


def download_label(request):

    user_id = str(request.session['user_id'])
    class_object_rgb_dict=request.session['class_object_rgb_dict']
    ip = request.session['ip']
    support_database_name = "semlog_web"
    support_collection_name = user_id + "." + "info"
    m = MongoDB(ip=ip, database=support_database_name,
                collection=support_collection_name)
    class_list = MongoClient(host=ip)[support_database_name][
        support_collection_name].distinct('class')
    class_list=sorted(class_list)
    print("distinct class is", class_list)
    print("mask_mapping is:",class_object_rgb_dict)
    label_info = m.get_label_from_info()

    label_folder_name = "label_info"
    text_file_name = "class.txt"
    mask_file_name = "mask.json"
    label_folder_path = os.path.join(
        settings.IMAGE_ROOT, user_id + "_" + label_folder_name)
    image_label_folder_path = os.path.join(label_folder_path, 'image_label')
    text_file_path = os.path.join(label_folder_path, text_file_name)
    mask_file_path=os.path.join(label_folder_path,mask_file_name)
    # print(label_folder_path)

    # Create label info folder and add class name
    os.makedirs(label_folder_path)
    os.makedirs(image_label_folder_path)
    with open(text_file_path, 'w') as class_file:
        for _class_name in class_list:
            class_file.write('%s\n' % _class_name)
    with open(mask_file_path,'w') as mask_file:
        json.dump(class_object_rgb_dict,mask_file)

    for _each_image_info in label_info:
        _image_name = str(_each_image_info['_id'])
        # _txt=os.path.join(image_label_folder_path,str(_image_name)+".txt")
        _txt = os.path.join(image_label_folder_path, "train.txt")

        # pprint.pprint(_each_image_info)
        for i, _each_label in enumerate(_each_image_info['class_list']):
            if "hmax" not in _each_label.keys():
                continue
            _class_index = class_list.index(_each_label['class'])
            txt_file = open(_txt, 'a')
            if i == 0:  # first loop
                txt_file.write('%s %s,%s,%s,%s,%s' % (os.path.join(user_id + "Color", _image_name + ".png"), _each_label[
                               'wmin'], _each_label['hmin'], _each_label['wmax'], _each_label['hmax'], _class_index))
            else:
                txt_file.write(' %s,%s,%s,%s,%s' % (_each_label['wmin'], _each_label[
                               'hmin'], _each_label['wmax'], _each_label['hmax'], _class_index))
            if i == len(_each_image_info['class_list']) - 1:  # last loop
                txt_file.write("\n")

    return HttpResponse("Download successfully!")



