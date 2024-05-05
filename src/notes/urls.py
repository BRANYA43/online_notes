from django.urls import path

from notes import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('create/', views.create_new_note, name='create_note'),
    path('update/<id>/', views.update_note, name='update_note'),
    path('retrieve/<id>/', views.retrieve_note, name='retrieve_note'),
]  # type: ignore
