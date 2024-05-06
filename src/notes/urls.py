from django.urls import path

from notes import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('note/create/', views.create_new_note, name='create_note'),
    path('note/update/<id>/', views.update_note, name='update_note'),
    path('note/retrieve/<id>/', views.retrieve_note, name='retrieve_note'),
    path('note/archive/<id>/', views.archive_note, name='archive_note'),
    path('note/delete/<id>/', views.delete_note, name='delete_note'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/update/<id>/', views.update_category, name='update_category'),
]  # type: ignore
