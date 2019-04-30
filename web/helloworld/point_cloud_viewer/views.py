from django.shortcuts import render
import sys
sys.path.append("..")
import os
import numpy as np

def showPC(request):
    data=np.load('staticfiles/pc.npy')
    data=data.T
    data=data.tolist()
    dic={"point":data}

    return render(request,'point_cloud_template.html',dic)
    # return render(request,'t.html')