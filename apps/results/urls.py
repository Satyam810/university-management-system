from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('', views.results_home, name='home'),
    path('student/', views.student_results, name='student_results'),
    path('faculty/', views.faculty_courses, name='faculty_courses'),
    path('upload/<int:semester_course_id>/', views.upload_grades, name='upload_grades'),
    path('course/<int:semester_course_id>/', views.course_grades, name='course_grades'),
]
