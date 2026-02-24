"""
Results models: Grade, SemesterResult - GPA/CGPA calculation.
"""
from django.db import models
from django.conf import settings
from django.db.models import Avg
from decimal import Decimal


class Grade(models.Model):
    """Individual course grade for a student."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grades',
        limit_choices_to={'role': 'STUDENT'}
    )
    semester_course = models.ForeignKey(
        'academics.SemesterCourse',
        on_delete=models.CASCADE,
        related_name='grades'
    )
    grade_point = models.ForeignKey(
        'academics.GradePointMapping',
        on_delete=models.PROTECT,
        related_name='grades'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='graded_results'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'semester_course']

    def __str__(self):
        return f"{self.student} - {self.semester_course.course.code}: {self.grade_point.grade}"

    @property
    def points(self):
        return self.grade_point.point


class SemesterResult(models.Model):
    """Aggregated semester result - GPA and classification."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='semester_results',
        limit_choices_to={'role': 'STUDENT'}
    )
    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.CASCADE,
        related_name='results'
    )
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    total_credits = models.PositiveIntegerField(default=0)
    earned_credits = models.PositiveIntegerField(default=0)
    classification = models.CharField(max_length=50, blank=True)  # Distinction, First Class, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'semester']

    def __str__(self):
        return f"{self.student} - {self.semester}: GPA {self.gpa}"

    def calculate_gpa(self):
        """Calculate GPA from grades in this semester."""
        from apps.academics.models import SemesterCourse
        grades = Grade.objects.filter(
            student=self.student,
            semester_course__semester=self.semester
        ).select_related('grade_point', 'semester_course__course')
        if not grades:
            return
        total_points = sum(g.points * g.semester_course.course.credits for g in grades)
        total_credits = sum(g.semester_course.course.credits for g in grades)
        if total_credits > 0:
            self.gpa = round(Decimal(total_points) / total_credits, 2)
            self.total_credits = total_credits
            self.earned_credits = sum(
                g.semester_course.course.credits for g in grades
                if g.grade_point.grade != 'F'
            )
            self.classification = self._get_classification(float(self.gpa))
            self.save()

    def _get_classification(self, gpa):
        if gpa >= 3.75:
            return 'Distinction'
        elif gpa >= 3.25:
            return 'First Class'
        elif gpa >= 2.75:
            return 'Second Class'
        elif gpa >= 2.0:
            return 'Pass'
        return 'Fail'
