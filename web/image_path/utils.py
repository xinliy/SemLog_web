import os


def absoluteFilePaths(directory):
    path_list = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            path_list.append(os.path.abspath(os.path.join(dirpath, f)))
    return path_list

def create_a_folder(folder_path):
    if not os.path.exists(folder_path):
        print("Create a folder:",folder_path)
        os.makedirs(folder_path)
