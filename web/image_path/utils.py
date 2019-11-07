import os


def absoluteFilePaths(directory):
    path_list = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            path_list.append(os.path.abspath(os.path.join(dirpath, f)))
    return path_list
