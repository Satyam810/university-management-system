"""
Attendance models: QRSession, AttendanceRecord.
Smart QR-based attendance with time-limited validity.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class QRSession(models.Model):
    """Dynamic QR session - valid for 2-5 minutes."""
    session_id = models.CharField(max_length=64, unique=True, editable=False)
    semester_course = models.ForeignKey(
        'academics.SemesterCourse',
        on_delete=models.CASCADE,
        related_name='qr_sessions'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_qr_sessions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"QR Session {self.session_id[:8]} - {self.semester_course}"

    def save(self, *args, **kwargs):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        """Check if QR is still valid (within time window)."""
        return self.is_active and timezone.now() < self.valid_until


class AttendanceRecord(models.Model):
    """Individual attendance record - prevents duplicates."""
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('LATE', 'Late'),
        ('ABSENT', 'Absent'),
    ]
    qr_session = models.ForeignKey(
        QRSession,
        on_delete=models.CASCADE,
        related_name='records'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role': 'STUDENT'}
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    marked_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        unique_together = ['qr_session', 'student']
        ordering = ['-marked_at']

    def __str__(self):
        return f"{self.student} - {self.status} at {self.marked_at}"
