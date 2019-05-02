import os,sys
folder_root=os.path.abspath('../..')
project_root=os.path.abspath('../../..')
assert os.path.basename(folder_root) =='web',print("The actual path is:",os.path.basename(folder_root))
sys.path.append(project_root)