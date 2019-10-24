from django.shortcuts import render
from django.http import HttpResponse

import json
import time
from multiprocessing.dummy import Pool

from web.website.imageViewer.utils import *

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
    return render(request, 'training_setting.html')


def start_training(request):
    training_dict = request.GET.dict()

    return HttpResponse('ok')


def update_database_info(request):
    """Show avaiable database-collection in real time with ajax."""
    return_dict = {}
    neglect_list = ['admin', 'config', 'local', 'semlog_web']
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
    print("<------------------------------->")
    print("START SEARCH")
    print("<------------------------------->")

    # Read the input from teh user.
    form_dict = request.GET.dict()
    d = Data(form_dict, request.session['ip'])
    request.session['user_id'] = d.user_id

    if d.object_id_list == [] and d.search_pattern == "entity_search":
        return HttpResponse("<h1 class='ui header'>No result is found in the given scope!</h1>")

    if d.flag_apply_filtering is True or d.flag_class_apply_filtering is True:
        apply_similar_filtering(d.ip, d.database_collection_list, d.flag_apply_filtering,
                                d.flag_class_apply_filtering, d.linear_distance_tolerance,
                                d.angular_distance_tolerance, d.class_id_list, d.class_num_pixels_tolerance,
                                d.class_linear_distance_tolerance, d.class_angular_distance_tolerance)
    if d.search_pattern == "entity_search":
        print("ENTITY SEARCH")
        df = entity_search(ip=d.ip, database_collection_list=d.database_collection_list,
                           object_id_list=d.object_id_list,
                           class_id_list=d.class_id_list, object_pattern=d.checkbox_object_pattern,
                           object_logic=d.object_logic,
                           image_type_list=d.image_type_list, flag_ignore_similar_image=d.flag_ignore_duplicate_image,
                           flag_class_ignore_similar_image=d.flag_class_ignore_duplicate_image)
    else:
        print("EVENT SEARCH")
        df = event_search(ip=d.ip, view_list=d.view_list)

    download_images_by_df(ip=d.ip, image_root=settings.IMAGE_ROOT, folder_header=d.user_id, df=df)
    image_dir = scan_images(image_root=settings.IMAGE_ROOT, folder_header=d.user_id, image_type_list=d.image_type_list)

    if d.flag_split_bounding_box is not True and d.flag_bounding_box is True and d.search_pattern == "entity_search":
        crop_with_all_bounding_box(d.object_rgb_dict, image_dir)

    # Resize image
    if d.width != "" or d.height != "":
        print("Enter resizing image.")
        image_path = []
        for key, value in image_dir.items():
            image_path = image_path + value
        print("Enter resizing.", d.width)
        pool = Pool(10)
        pool.starmap(resize_image, zip(
            image_path, itertools.repeat(d.width), itertools.repeat(d.height), itertools.repeat(d.flag_resize_type)))
        pool.close()
        pool.join()

    # Do object cutting
    if d.flag_bounding_box is True and d.search_pattern == "entity_search":
        df = generate_bounding_box(df, d.object_rgb_dict, settings.IMAGE_ROOT, d.user_id)
    bounding_box_dict = scan_bounding_box_images(settings.IMAGE_ROOT, d.user_id)
    df.to_csv(os.path.join(settings.IMAGE_ROOT, d.user_id, 'info.csv'), index=False)

    return render(request, 'gallery.html',
                  {"object_id_list": d.object_id_list, "image_dir": image_dir, "bounding_box": bounding_box_dict})


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
    zip_target = os.path.join(image_root, user_id, img_type)
    zip_path = os.path.join(image_root, user_id, "Color_images.zip")
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
    class_object_rgb_dict = request.session['class_object_rgb_dict']
    ip = request.session['ip']
    support_database_name = "semlog_web"
    support_collection_name = user_id + "." + "info"
    m = MongoDB(ip=ip, database=support_database_name,
                collection=support_collection_name)
    class_list = MongoClient(host=ip)[support_database_name][
        support_collection_name].distinct('class')
    class_list = sorted(class_list)
    print("distinct class is", class_list)
    print("mask_mapping is:", class_object_rgb_dict)
    label_info = m.get_label_from_info()

    label_folder_name = "label_info"
    text_file_name = "class.txt"
    mask_file_name = "mask.json"
    label_folder_path = os.path.join(
        settings.IMAGE_ROOT, user_id + "_" + label_folder_name)
    image_label_folder_path = os.path.join(label_folder_path, 'image_label')
    text_file_path = os.path.join(label_folder_path, text_file_name)
    mask_file_path = os.path.join(label_folder_path, mask_file_name)
    # print(label_folder_path)

    # Create label info folder and add class name
    os.makedirs(label_folder_path)
    os.makedirs(image_label_folder_path)
    with open(text_file_path, 'w') as class_file:
        for _class_name in class_list:
            class_file.write('%s\n' % _class_name)
    with open(mask_file_path, 'w') as mask_file:
        json.dump(class_object_rgb_dict, mask_file)

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
                txt_file.write(
                    '%s %s,%s,%s,%s,%s' % (os.path.join(user_id + "Color", _image_name + ".png"), _each_label[
                        'wmin'], _each_label['hmin'], _each_label['wmax'], _each_label['hmax'], _class_index))
            else:
                txt_file.write(' %s,%s,%s,%s,%s' % (_each_label['wmin'], _each_label[
                    'hmin'], _each_label['wmax'], _each_label['hmax'], _class_index))
            if i == len(_each_image_info['class_list']) - 1:  # last loop
                txt_file.write("\n")

    return HttpResponse("Download successfully!")
