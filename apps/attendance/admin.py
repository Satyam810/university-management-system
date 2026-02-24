from django.contrib import admin
from .models import QRSession, AttendanceRecord


@admin.register(QRSession)
class QRSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'semester_course', 'created_by', 'created_at', 'valid_until', 'is_active']
    list_filter = ['is_active', 'created_at']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'qr_session', 'status', 'is_late', 'marked_at']
    list_filter = ['status', 'is_late']
