
Development Guide
=====================================

Structure Design
-----------------
Refer to `Features <./Features.html>`__ for understanding of important structure designs in LightGBM.

Classes and Code Structure
----------------------------

important Classes
~~~~~~~~~~~~~~~~~

+-------------------------+----------------------------------------------------------------------------------------+
| Class                   | Description                                                                            |
+=========================+========================================================================================+
| ``WebsiteData``         | Compile form data received from the website input. Clean and restructure               |
+-------------------------+----------------------------------------------------------------------------------------+
| ``MongoDB``             | Data structure used for querying multiple collections, downloading images              |
+-------------------------+----------------------------------------------------------------------------------------+
| ``PointCloudGenerator`` | Generate point cloud matrix from RGB and depth image pairs                             |
+-------------------------+----------------------------------------------------------------------------------------+
| ``Config``              | Stores parameters and configurations                                                   |
+-------------------------+----------------------------------------------------------------------------------------+

Code Structure
~~~~~~~~~~~~~~
+----------------------------------+--------------------------------------------------------------------------+
| Path                             | Description                                                              |
+==================================+==========================================================================+
| ./web/image_path                 | Functions for retrieving local image files                               |
+----------------------------------+--------------------------------------------------------------------------+
| ./web/models                     | Implementations of vision algorithms                                     |
+----------------------------------+--------------------------------------------------------------------------+
| ./web/semlog_mongo               | Implementations of python interface to MongoDB                           |
+----------------------------------+--------------------------------------------------------------------------+
| ./web/semlog_vis                 | Implementations of image manipulations                                   |
+----------------------------------+--------------------------------------------------------------------------+
| ./web/staticfiles                | JS and CSS used in the website                                           |
+----------------------------------+--------------------------------------------------------------------------+
| ./web/website/imageViewer        | Django application for connecting the website with all another functions |
+----------------------------------+--------------------------------------------------------------------------+
| ./web/website/pointCloudViewer   | Implementations of dynamic calculation and visualization of point clouds |
+----------------------------------+--------------------------------------------------------------------------+
| ./web/website/static             | Root folder for saving images in the server side                         |
+----------------------------------+--------------------------------------------------------------------------+
| ./web/website/template           | html files with Django template language                                 | 
+----------------------------------+--------------------------------------------------------------------------+



Questions
---------

Refer to `FAQ <./FAQ.html>`__.

Also feel free to open `issues <https://github.com/robcog-iai/semlog_web/issues>`__ if you met problems.







