from django.contrib import admin
from django.urls import path, include
from ideas import views as idea

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", idea.main, name="home"),
    path("ideas/", include("ideas.urls")),
    path("devtools/", include("devtools.urls")),
]