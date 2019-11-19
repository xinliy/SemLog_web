"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
import sys

sys.path.append("..")
from .imageViewer import views as image_views
from .point_cloud_viewer import views as pc_views

urlpatterns = [
    path(r'', image_views.search),
    path(r'start_search/', image_views.start_search),
    path(r'create_pc/', pc_views.create_pc),
    path(r'update_database_info/', image_views.update_database_info),
    path(r'show_one_image/',image_views.show_one_image),
    path(r'download/',image_views.download),
    path(r'training/',image_views.training),
    path(r'view_images/',image_views.view_images),
    # path(r'start_training/',image_views.start_training)
]
