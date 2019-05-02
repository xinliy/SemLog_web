FROM python
RUN pip install psycopg2-binary numpy pandas Django Pillow pptk plyfile dj_database_url django_heroku pymongo dnspython\
&& mkdir -p /usr/src/app
 WORKDIR /usr/src/app
 COPY . /usr/src/app
 ENV PYTHONPATH="$PYTHONPATH:/usr/src/app"
 EXPOSE 8000
CMD [ "python", "./web/manage.py", "runserver", "0.0.0.0:8000"]
