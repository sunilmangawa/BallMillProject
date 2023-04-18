# blog/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post

class BlogListView(ListView):
    model = Post
    template_name = "blog.html"

class BlogDetailView(DetailView): # new
    model = Post
    template_name = "post_detail.html"
