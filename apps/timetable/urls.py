from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.timetable_view, name='view'),
    path('admin/', views.timetable_admin, name='admin'),
]
