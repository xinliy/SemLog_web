
Installation Guide
=====================================

Here is the guide for the build of SemlogWeb.

All instructions below are aimed to compile 64-bit version of SemlogWeb.

.. contents:: **Contents**
    :depth: 1
    :local:
    :backlinks: none


Windows
~~~~~~~

From Command Line
*****************

1. Install `Miniconda - Python 3.7 <https://docs.conda.io/en/latest/miniconda.html>`_.
2. Install third-party libraries from ``requirement.txt``,

   .. code::

     python -m pip install -r requirements.txt
3. Install third-party libraries from requirement.txt,

   .. code::

     git clone https://github.com/robcog-iai/semlog_web.git

4. Install `MongoDB <https://docs.mongodb.com/manual/installation/>`_.
5. Choose a disk for example ``D:``, create a directory ``D:/db/data``, then start MongoDB sever in the terminal of D:

   .. code::

     mongod

6. Open another terminal to the directory than contains the ``dump`` folder (Contains the database from RobCog),then run this command to add the database

   .. code::

     mongorestore .


Linux
~~~~~
Installation in Linux is mostly the same as in Windows. Make sure to grant write authority to the root folder.





