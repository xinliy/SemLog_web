from django.shortcuts import render
from django.http import HttpResponse

import json
import time
from multiprocessing.dummy import Pool

from web.website.imageViewer.utils import *
from web.website.settings import IMAGE_ROOT
from web.image_path.image_path import *
from web.semlog_vis.semlog_vis.bounding_box import *
from web.semlog_vis.semlog_vis.image import *

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
    """Delete old folders before search."""
    t1 = time.time()
    if os.path.isdir(IMAGE_ROOT) is False:
        print("Create image root.")
        os.makedirs(IMAGE_ROOT)
    delete_path = os.listdir(IMAGE_ROOT)
    delete_path = [os.path.join(IMAGE_ROOT, i)
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
        shutil.rmtree(IMAGE_ROOT)
    except Exception as e:
        print(e)
    print("Delete all folders for:", time.time() - t1)
    if os.path.isdir(IMAGE_ROOT) is False:
        print("Create image root.")
        os.makedirs(IMAGE_ROOT)

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

    # Read the input from teh user.
    form_dict = request.GET.dict()
    d = WebsiteData(form_dict, request.session['ip'])
    request.session['user_id'] = d.user_id

    mongoManager = MongoDB(d.database_collection_list, d.ip)

    if d.object_id_list == [] and d.search_pattern == "entity_search":
        return HttpResponse("<h1 class='ui header'>No result is found in the given scope!</h1>")

    if d.flag_apply_filtering is True or d.flag_class_apply_filtering is True:
        print('---------------------------APPLY FILTERING---------------------------')
        mongoManager.apply_similar_filtering(d.flag_apply_filtering, d.class_id_list, d.similar_dict)
    if d.search_pattern == "entity_search":
        print("ENTITY SEARCH")
        df = mongoManager.entity_search(
            object_id_list=d.object_id_list,
            class_id_list=d.class_id_list, object_pattern=d.checkbox_object_pattern,
            object_logic=d.object_logic,
            image_type_list=d.image_type_list, flag_ignore_similar_image=d.flag_ignore_duplicate_image,
            flag_class_ignore_similar_image=d.flag_class_ignore_duplicate_image)
    else:
        print("EVENT SEARCH")
        df = event_search(ip=d.ip, view_list=d.view_list)

    download_images(ip=d.ip, root_folder_path=IMAGE_ROOT, root_folder_name=d.user_id, df=df)

    if d.flag_split_bounding_box is not True and d.search_pattern == "entity_search":

        image_dir = scan_images(root_folder_path=IMAGE_ROOT, root_folder_name=d.user_id, image_type_list=d.image_type_list)
        crop_with_all_bounding_box(d.object_rgb_dict, image_dir)

    image_dir = scan_images(root_folder_path=IMAGE_ROOT, root_folder_name=d.user_id, image_type_list=d.image_type_list,unnest=True)
    if d.dataset_pattern == 'detection' and d.search_pattern == "entity_search":
        print("----------------Prepare dataset for object detection---------------------")
        image_dir = scan_images(root_folder_path=IMAGE_ROOT, root_folder_name=d.user_id, image_type_list=d.image_type_list,unnest=True)
        d.customize_image_resolution(image_dir)
        df = calculate_bounding_box(df, d.object_rgb_dict, IMAGE_ROOT, d.user_id)
        bounding_box_dict = {}
        df.to_csv(os.path.join(IMAGE_ROOT, d.user_id, 'info.csv'), index=False)
    elif d.dataset_pattern == 'classifier' and d.search_pattern == "entity_search":
        print("----------------Prepare dataset for classifier---------------------------")
        download_bounding_box(df, d.object_rgb_dict, IMAGE_ROOT, d.user_id)
        bounding_box_dict = scan_bounding_box_images(IMAGE_ROOT, d.user_id)
        print(bounding_box_dict.values())
        # bounding_box_dir = {}
        # for (key, value) in bounding_box_dict.items():
            # images = list(itertools.chain(*value.values()))
            # bounding_box_dir[key] = images
        bounding_box_dict=scan_bounding_box_images(IMAGE_ROOT,d.user_id,unnest=True)
        d.customize_image_resolution(bounding_box_dict)
    else:
        bounding_box_dict = {}
    image_dir=scan_images(IMAGE_ROOT,d.user_id,d.image_type_list)
    bounding_box_dict=scan_bounding_box_images(IMAGE_ROOT,d.user_id)

    return render(request, 'gallery.html',
                  {"object_id_list": d.object_id_list, "image_dir": image_dir, "bounding_box": bounding_box_dict})


def download(request):
    """Download images as .zip file. """

    def make_archive(source, destination):
        print(source, destination)
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        print(source, destination, archive_from, archive_to)
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s' % (name, format), destination)

    img_type = request.GET['img_type']
    user_id = request.session['user_id']
    image_root = IMAGE_ROOT
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
