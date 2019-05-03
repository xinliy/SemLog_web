# pyWeb

pyWeb is a light Django app that can connect to a images mongoDB and generate point cloud instantly.

**image type: Color/Depth/Mask/Normal**

Run in Docker:
Enter the root folder with Dockerfile

Run in cmd:

build -t django:v1 . 

docker run -p 8000:8000 -i -t django:v1

Visit the website in the browser 127.0.0.1:8000

One problem is Mongo Atlas cannot bind to all ip. So every time you run the app in different ip address. You need to add the new ip to whitelist.

