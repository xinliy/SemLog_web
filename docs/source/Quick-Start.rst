
Quick Start
=====================================
This is a quick start guide for SemlogWeb.

Follow the `Installation Guide <./Installation-Guide.html>`__ to install SemlogWeb first.

Access with browser
-------------------
SemlogWeb can be viewed in the browser (Chrome preferred).

For example, the source code is in ``D:``, open a new terminal to ``D:\semlog_web\web`` and run

   .. code::

     python manage.py runserver

Then you can evaluate the website by visiting ``http://127.0.0.1:8000/`` in Chrome.

To access the database, if MongoDB is set in ``F:``, open a new terminal to ``F:`` and run

   .. code::

     mongod

Therefore the MongoDB server is running. You are able to utilize all functionalities via the website.

Access with Python interface
----------------------------
If you want to use individual function of SemlogWeb, there is also a DEMO written in Jupyter Notebook for quick start.

Open a new terminal to ``D:\semlog_web\web\example``, run

   .. code::

     jupyter notebook
Then you should be able to view a short demo in your browser.

Try to run cells one by one to go through these important functions. You can view generated images in local directory after the download API is called





