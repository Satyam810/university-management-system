"""
AI utilities: attendance risk prediction, academic risk detection.
"""
from django.db.models import Count
from apps.attendance.models import QRSession, AttendanceRecord
from apps.academics.models import Enrollment
from apps.results.models import Grade


def get_low_attendance_risk_students(threshold_pct=75):
    """Students with attendance below threshold - AI risk alert."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    students = User.objects.filter(role='STUDENT')
    at_risk = []
    for s in students:
        enrollments = Enrollment.objects.filter(student=s)
        total, present = 0, 0
        for e in enrollments:
            sessions = QRSession.objects.filter(semester_course=e.semester_course)
            for sess in sessions:
                total += 1
                if AttendanceRecord.objects.filter(qr_session=sess, student=s).exists():
                    present += 1
        if total > 0:
            pct = present / total * 100
            if pct < threshold_pct:
                at_risk.append({'student': s, 'attendance_pct': round(pct, 1), 'total': total})
    return at_risk


def get_weak_performing_students(threshold_gpa=2.0):
    """Students with low GPA - academic risk."""
    from apps.results.models import SemesterResult
    from django.contrib.auth import get_user_model
    User = get_user_model()
    results = SemesterResult.objects.filter(gpa__lt=threshold_gpa).select_related('student')
    return [{'student': r.student, 'gpa': float(r.gpa), 'semester': r.semester} for r in results]
