from django.urls import path

from . import views

app_name = 'skills'

urlpatterns = [
    path('tree/<int:pk>/', views.tree_detail, name='tree_detail'),
    path('skill/<int:pk>/toggle/', views.toggle_skill, name='toggle_skill'),
]
