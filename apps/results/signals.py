"""Signals for auto-updating GPA/CGPA."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grade, SemesterResult


@receiver(post_save, sender=Grade)
def update_semester_gpa(sender, instance, **kwargs):
    """Recalculate semester GPA when grade is added/updated."""
    semester = instance.semester_course.semester
    result, _ = SemesterResult.objects.get_or_create(
        student=instance.student,
        semester=semester,
        defaults={'gpa': 0}
    )
    result.calculate_gpa()
