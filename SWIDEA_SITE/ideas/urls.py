from django.urls import path
from .import views

app_name = "ideas"

urlpatterns = [
    path("", views.main, name="main"),
    path("ideas/create/", views.idea_create, name="create"),
    path("ideas/<int:pk>/", views.idea_detail, name="detail"), 
    path("ideas/<int:pk>/update/", views.idea_update, name="update"),
    path("ideas/<int:pk>/delete/", views.idea_delete, name="delete"),
    path("ideas/<int:pk>/toggle-star/", views.idea_toggle_star, name="toggle"),
    path("ideas/<int:pk>/interest/", views.idea_interest, name="interest"),
]