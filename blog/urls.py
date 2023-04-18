# blog/urls.py
from django.urls import path
from .views import BlogListView, BlogDetailView #, post_list, post_detail, PostListView

# app_name = 'blog'

urlpatterns = [
    path("", BlogListView.as_view(), name="blog"),
    path("post/<slug>/", BlogDetailView.as_view(), name="post_detail"), # new
]
