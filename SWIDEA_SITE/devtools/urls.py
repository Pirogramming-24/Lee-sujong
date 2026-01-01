from django.urls import path
from . import views

app_name = "devtools"

urlpatterns = [
    path("", views.main, name="main"),
    path("create/", views.devtool_create, name="create"),
    path("<int:pk>/", views.devtool_detail, name="detail"),
    path("<int:pk>/update/", views.devtool_update, name="update"),
    path("<int:pk>/delete/", views.devtool_delete, name="delete"),
]