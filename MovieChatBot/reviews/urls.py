from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.review_list, name="list"),
    path("<int:pk>/", views.review_detail, name="detail"),
    path("create/", views.review_create, name="create"),
    path("<int:pk>/update/", views.review_update, name="update"),
    path("<int:pk>/delete/", views.review_delete, name="delete"),
    path("tmdb/sync/", views.tmdb_sync_popular, name="tmdb_sync"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)