from django.shortcuts import render
from django.http import HttpResponse

import json
import time
import pickle
from multiprocessing.dummy import Pool

from web.website.imageViewer.utils import *
from web.website.settings import IMAGE_ROOT,CONFIG_PATH
from web.image_path.image_path import *
from web.semlog_vis.semlog_vis.bounding_box import *
from web.semlog_vis.semlog_vis.image import *
import web.models.classifier.train as classifier_train



def clean_folder(x):
    """delete old folders."""

    t1 = time.time()
    try:
        shutil.rmtree(x)
    except exception as e:
        print(e)
    print(os.listdir(x))
    print("remove", x)
    print("delete folder for:", time.time() - t1)
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
    """Entrance for training the multiclass classifier."""
    dataset_pattern = request.session['dataset_pattern']
    user_id = request.session['user_id']
    class_list = request.session['class_id_list']
    if dataset_pattern == "classifier":
        classifier_train.train(
            dataset_path=os.path.join(IMAGE_ROOT, user_id, "BoundingBoxes"),
            class_list=class_list,
            model_saving_path=os.path.join(IMAGE_ROOT, user_id)
        )
    return HttpResponse("Model starts training. Progress can be seen in port 8097.")


def update_database_info(request):
    """Show avaiable database-collection in real time with ajax."""
    return_dict = {}
    neglect_list = ['admin', 'config', 'local', 'semlog_web']
    if request.method == 'POST':
        print("enter update database!")
        print(request.POST.dict())
        target_ip = request.POST['ip_address']
        request.session['ip'] = request.POST['ip_address']
        username,password=load_mongo_account(CONFIG_PATH)
        m = MongoClient(target_ip, 27017,username=username,password=password)
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
    """The most important function of the website.
        Read the form and search the db, download images to static folder."""

    # Read the input from teh user.
    form_dict = request.GET.dict()
    d = WebsiteData(form_dict, request.session['ip'])
    request.session['user_id'] = d.user_id
    request.session['dataset_pattern'] = d.dataset_pattern
    request.session['class_id_list'] = d.class_id_list

    # Create MongoDB instance
    mongoManager = MongoDB(d.database_collection_list, d.ip,config_path=CONFIG_PATH)

    # Search scan images
    if d.search_pattern=="scan_search":
        df=scan_search(ip=d.ip,db_collection=d.scan_collection,scan_class_list=d.scan_class_list,image_type_list=d.image_type_list,config_path=CONFIG_PATH)

    # Return error if no result for entity_search
    elif d.object_id_list is None and d.search_pattern == "entity_search":
        return HttpResponse("<h1 class='ui header'>No result is found in the given scope!</h1>")

    # Search entities
    elif d.search_pattern == "entity_search":
        print("ENTITY SEARCH")
        df = mongoManager.entity_search(
            object_id_list=d.object_id_list,
            class_id_list=d.class_id_list, object_pattern=d.checkbox_object_pattern,
            object_logic=d.object_logic,
            image_type_list=d.image_type_list, flag_ignore_similar_image=d.flag_ignore_duplicate_image,
            flag_class_ignore_similar_image=d.flag_class_ignore_duplicate_image)
        print("Search Done.")
    else:
        print("EVENT SEARCH")
        df = event_search(ip=d.ip, view_list=d.view_list,config_path=CONFIG_PATH)

    # Download images
    download_images(ip=d.ip, root_folder_path=IMAGE_ROOT,
                    root_folder_name=d.user_id, df=df,config_path=CONFIG_PATH)
    print("Download Done.")



    # Perform origin image crop if selected.
    if d.flag_split_bounding_box is True and d.search_pattern == "entity_search":

        image_dir = scan_images(root_folder_path=IMAGE_ROOT,
                                root_folder_name=d.user_id, image_type_list=d.image_type_list)
        crop_with_all_bounding_box(d.object_rgb_dict, image_dir)

    # Retrieve local image paths
    image_dir = scan_images(root_folder_path=IMAGE_ROOT, root_folder_name=d.user_id,
                            image_type_list=d.image_type_list, unnest=True)

    # Move scan images to the right folders
    if d.search_pattern=="scan_search":
        d.customize_image_resolution(image_dir)
        arrange_scan_by_class(df,IMAGE_ROOT,d.user_id)
    # Prepare dataset
    elif d.dataset_pattern == 'detection' and d.search_pattern == "entity_search":
        print("----------------Prepare dataset for object detection---------------------")

        d.customize_image_resolution(image_dir)
        df = calculate_bounding_box(
            df, d.object_rgb_dict, IMAGE_ROOT, d.user_id)
        df.to_csv(os.path.join(IMAGE_ROOT, d.user_id, 'info.csv'), index=False)

    elif d.dataset_pattern == 'classifier' and d.search_pattern == "entity_search":
        print("----------------Prepare dataset for classifier---------------------------")

        download_bounding_box(df, d.object_rgb_dict, IMAGE_ROOT, d.user_id)
        bounding_box_dict = scan_bb_images(
            IMAGE_ROOT, d.user_id, unnest=True)
        d.customize_image_resolution(bounding_box_dict)


    # Store static info in local json file
    info={'image_type_list':d.image_type_list,'object_id_list':d.object_id_list,'search_pattern':d.search_pattern}
    with open(os.path.join(IMAGE_ROOT,d.user_id,'info.json'),'w') as f:
        json.dump(info,f)

    return render(request,'make_your_choice.html')

def view_images(request):
    """Entrance of viewing mode of the website."""
    user_id=request.session['user_id']
    with open(os.path.join(IMAGE_ROOT,user_id,'info.json')) as f:
        info=json.load(f)
    object_id_list=info['object_id_list']
    image_type_list=info['image_type_list']
    search_pattern=info['search_pattern']
    image_dir=scan_images(IMAGE_ROOT,user_id,image_type_list)
    if search_pattern=="scan_search":
        bounding_box_dict=scan_bb_images(IMAGE_ROOT,user_id,folder_name="scans")
    else:
        bounding_box_dict=scan_bb_images(IMAGE_ROOT,user_id)


    return render(request, 'gallery.html',
                  {"object_id_list": object_id_list, "image_dir": image_dir, "bounding_box": bounding_box_dict})

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

    user_id = request.session['user_id']
    image_root = IMAGE_ROOT
    zip_target = os.path.join(image_root, user_id)
    zip_path = os.path.join(image_root, user_id, "Color_images.zip")
    make_archive(zip_target, zip_path)
    print("finish zip.")
    zip_file = open(zip_path, '+rb')
    response = HttpResponse(zip_file, content_type='application/zip')
    response[
        'Content-Disposition'] = 'attachment; filename=%s' % "dataset.zip"
    response['Content-Length'] = os.path.getsize(zip_path)
    zip_file.close()

    return response
