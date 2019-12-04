
Features
=====================================
This is a conceptual overview of how SemlogWeb works. We assum familiarity with at least one NoSQL database (in our case we use MongoDB) and basic image processing methods.

.. contents:: **Contents**
    :depth: 1
    :local:
    :backlinks: none



Framework overview
--------------------
Many robotic applications have been built in Virtual Realities and are widely used in researches.
However, these are mostly only composed with elementary interface for camera setup and data sampling.
Our original intention for SemlogWeb is to bridge the gap between all Virtual Realities and perception model.

.. figure:: images/framework.png
   :scale: 100%
   :align: center

   Overview of the proposed framework

The framework contains three components. First is knowledge-based database in which a photorealistic synthetic environment is created for usage of computer vision.
The world state and sampled image data are stored in the NoSQL database.

The second component is data processing. Both the **Scope Constrain** and **Data Normalization** are available before an synthetic image dataset is generated.

The last component is perception models. SemlogWeb can be connected to many computer vision algorithms. Follow the `Demo <./Demo.html>`__ to go through an example.

Database structure
-------------------
Give the abundant synthetic image data in the Unreal Engine, images are stored by tasks and episodes.
For example, one task could be "Clean the table" or "Move the Strawberry jam to the fridge". 
Multiple participants would equip VR equipments and finish the task in the virtual environment. 
One attempt carried by one participant is stored as an episode in the database. 
Therefore one task (mapped as one database) will contains many episodes (mapped as one collection).

.. figure:: images/mongodb.png
   :scale: 80%
   :align: center

   The database structure in MongoDB





