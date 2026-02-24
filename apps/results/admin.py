from django.contrib import admin
from .models import Grade, SemesterResult


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester_course', 'grade_point', 'created_by', 'created_at']


@admin.register(SemesterResult)
class SemesterResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'gpa', 'classification', 'total_credits']
