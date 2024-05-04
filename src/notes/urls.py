from django.urls import path
from django.views import generic

from notes import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('create/', views.create_new_note, name='create_note'),
    path('update/<id>/', generic.View.as_view(), name='update_note'),
]  # type: ignore
