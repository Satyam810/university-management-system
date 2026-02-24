from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('', views.academics_home, name='home'),
    path('departments/', views.department_list, name='department_list'),
    path('courses/', views.course_list, name='course_list'),
    path('semesters/', views.semester_list, name='semester_list'),
    path('semesters/<int:semester_id>/courses/', views.semester_course_list, name='semester_course_list'),
    path('faculty/my-students/', views.faculty_my_students, name='faculty_my_students'),
]
