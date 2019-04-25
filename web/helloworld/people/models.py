from django.db import models


# class Person(models.Model):
# 	name=models.CharField(max_length=30)
# 	age=models.IntegerField()

# 	def __unicode__(self):
# 		return self.name
# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=30)
    date = models.CharField(max_length=30)
    subject = models.CharField(max_length=30)
    content = models.CharField(max_length=100)
    # person=models.ForeignKey(Person,on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField()


class E_article(models.Model):
    tool = models.CharField(max_length=30)
    a_title = models.CharField(max_length=30)
    a_id = models.CharField(max_length=30)
    s_id=models.IntegerField()


class T_article(models.Model):
    s_id = models.IntegerField()
    a_id = models.CharField(max_length=30)
