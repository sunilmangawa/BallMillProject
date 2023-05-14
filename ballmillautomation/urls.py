# django_project/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic.base import TemplateView # new
from devicedata.views import products, about_us, contact_us, terms_and_conditions

urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")), # new
    path("accounts/", include("django.contrib.auth.urls")), # new

    path("", TemplateView.as_view(template_name="home.html"), name="home"), # new
    path('about-us/', about_us, name='about_us'),
    path('contact-us/', contact_us, name='contact_us'),
    path('products/', products, name='products'),
    path('terms-and-conditions/', terms_and_conditions, name='terms_and_conditions'),

    path("blog/", include("blog.urls")), # new , namespace='blog'
    path('devicedata/', include('devicedata.urls')),#new
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)