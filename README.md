# SemLog Web

SemLog Web is an integrated framework written in Python with a concise web UI that bridges between knownledge-based virtual environment and numerous computer vision models.
Documentations: https://xinliy.github.io/SemLog_web/


## Getting Started

Go to "**semlog_web/web/example**" and click "DEMO.ipynb" to directly get a picture of SemLog Web's main features.
You can also install dependencies to deploy the framework locally

### Prerequisites

You need to retrieve an instance of SemLog database to use this framework.

### Installing

1. Install **Miniconda - Python 3.7** from https://docs.conda.io/en/latest/miniconda.html
- In "Advanced options", tick both options (Add Anaconda to my PATH environment)
- Note: You can test if Python is installed by enter "python" in your terminal.

2. Open terminal, run
```        
pip install django pillow opencv-python pandas numpy matplotlib pymongo django_heroku dnspython open3d-python
```

3. clone the repo 
```
git clone https://github.com/robcog-iai/semlog_web.git
```

4. make sure the **local MongoDB** is running.

5. Open a terminal and enter the "**SemLog_web/web**" folder, run
```
python manage.py runserver
```

6. Open your browser and visit the website via the address "**localhost:8000**".


End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Go to "**semlog_web/web/example**", run
```
jupyter notebook
```
And check all important features in the framework.


## Deployment

Open your browser and visit the website via the address "**localhost:8000**" to deploy it locally, or use

```
python manage.py runserver TARGET_IP
```
To deploy the website in local network

## Documentation

Full official documentation can be viewed at https://xinliy.github.io/SemLog_web/index.html

## Built With
* [Django](https://www.djangoproject.com/) - The web framework used
* [MongoDB](https://www.mongodb.com/) - The database used
* [Pytorch](https://pytorch.org/) - The deep learning framework used to build the detection demo
* [Three.js](https://threejs.org/) - The UI JavaScript framework used for dynamic point cloud generation



## Authors

* **Xiaoyue Zhang** - *Author* - [xinliy](https://github.com/xinliy)


## License

This project is licensed under the BSD-3-Clause License

## Acknowledgments

* This framework is developed by Xiaoyue Zhang in the Institute of Artificial Intelligence, University of Bremen, under the supervision of Andrei Haidu

