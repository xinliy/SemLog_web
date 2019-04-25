from django.shortcuts import render
from django.db import models
import sys
sys.path.append("..")
from .models import *


def addArticle(request):
    return render(request, 'addArticle.html')

def imprint(request):
    return render(request,'imprint.html')


def addok(request):
    return render(request, 'addok.html')


def add(request):

    # 获取参数book_name,author,author_age
    if request.method == "GET":
        article_title = request.GET["article_title"]
        article_date = request.GET["article_date"]
        # article_subject = request.GET["article_subject"]
        article_content = request.GET["article_content"]
        article_tool = request.GET["article_tool"]
        # author_name = request.GET["author"]
        # author_age = request.GET["author_age"]
        subject = request.GET['subject']

    # from models import Person, Book
    article = Article(title=article_title, date=article_date,
                      subject=subject, content=article_content)
    article.save()
    # if article_subject=="e":
    if subject == 'engineering':
        e_article = E_article()
        e_article.tool = article_tool
        # e_article.a_title = article.title
        e_article.a_id = article.id
        e_article.s_id = 1
        e_article.save()

    # elif article_subject=='t':
    elif subject == 'theoretical':
        t_article = T_article()
        t_article.a_id = article.id
        t_article.s_id = 2
        t_article.save()

    # person1=Person.objects.filter(name=author_name)
    # if person1.exists()!= 0:
    # 	article.person_id=person1[0].id

    # else:

        #  person=Person()
        #  person.name=author_name
        #  person.age=author_age
        #  person.save()
        #  article.person_id=person.id

    # article.save()

    from django.http import HttpResponseRedirect
    return HttpResponseRedirect('/addok/')


def IndexView(request):
        # persons=Person.objects.all()
    articles = Article.objects.all()
    e_articles = E_article.objects.all()
    t_articles = T_article.objects.all()

    d = {}
    # d['person_list']=persons
    d['article_list'] = articles
    d['e_article_list'] = e_articles
    d['t_article_list'] = t_articles
    return render(request, 'index.html', d)
