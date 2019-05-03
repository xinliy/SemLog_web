import json
import web.website.settings as settings
import os

def get_image_dir():
    with open(os.path.join(settings.STATIC_ROOT, "image_dir.json"), 'r') as readfile:
        image_dir = json.load(readfile)
    return image_dir

def save_image_dir(image_dir):
    with open(os.path.join(settings.STATIC_ROOT, "image_dir.json"), "w") as outfile:
        json.dump(image_dir, outfile)