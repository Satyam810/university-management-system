"""
Assignment models: Assignment, Submission.
Faculty uploads, student submits, late submission marking.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Assignment(models.Model):
    """Faculty-uploaded assignment."""
    semester_course = models.ForeignKey(
        'academics.SemesterCourse',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    deadline = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_assignments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.semester_course}"

    @property
    def is_past_deadline(self):
        return timezone.now() > self.deadline


class Submission(models.Model):
    """Student submission with late marking."""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        limit_choices_to={'role': 'STUDENT'}
    )
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student} - {self.assignment.title}"

    def save(self, *args, **kwargs):
        if self.assignment and self.assignment.deadline:
            submitted = self.submitted_at or timezone.now()
            self.is_late = submitted > self.assignment.deadline
        super().save(*args, **kwargs)
