from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.assignment_list, name='list'),
    path('create/<int:semester_course_id>/', views.assignment_create, name='create'),
    path('<int:pk>/', views.assignment_detail, name='detail'),
    path('<int:assignment_id>/submit/', views.submission_create, name='submit'),
    path('submission/<int:pk>/grade/', views.submission_grade, name='grade'),
]
