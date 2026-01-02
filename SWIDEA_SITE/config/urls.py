from django.contrib import admin
from django.urls import path, include
from ideas import views as idea
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", idea.main, name="home"),
    path("ideas/", include("ideas.urls")),
    path("devtools/", include("devtools.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)