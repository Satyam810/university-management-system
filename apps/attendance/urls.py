"""Attendance URL configuration."""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_home, name='home'),
    path('faculty/', views.faculty_dashboard, name='faculty_dashboard'),
    path('generate/<int:semester_course_id>/', views.generate_qr, name='generate_qr'),
    path('scan/', views.scan_qr, name='scan_qr'),
    path('session/<str:session_id>/', views.session_records, name='session_records'),
    path('session/<str:session_id>/csv/', views.download_attendance_csv, name='download_csv'),
    path('student/', views.student_view, name='student_view'),
]
