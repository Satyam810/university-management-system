"""
Academic models: Department, Semester, Course, GradePointMapping, Enrollment.
"""
from django.db import models
from django.conf import settings


class Department(models.Model):
    """Academic department."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Semester(models.Model):
    """Academic semester."""
    name = models.CharField(max_length=50) 
    code = models.CharField(max_length=20, unique=True)  
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Course(models.Model):
    """Course with credit system and syllabus."""
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    credits = models.PositiveIntegerField(default=3)
    syllabus = models.FileField(upload_to='syllabus/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']
        unique_together = ['department', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class SemesterCourse(models.Model):
    """Semester-wise course mapping."""
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='semester_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='semester_courses')
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='teaching_courses',
        limit_choices_to={'role': 'FACULTY'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['semester', 'course']
        verbose_name = 'Semester Course'
        verbose_name_plural = 'Semester Courses'

    def __str__(self):
        return f"{self.course} - {self.semester}"


class GradePointMapping(models.Model):
    """Grade to point mapping for GPA calculation."""
    grade = models.CharField(max_length=5)  # A+, A, B+, B, C+, C, D, F
    point = models.DecimalField(max_digits=3, decimal_places=2)
    description = models.CharField(max_length=50, blank=True)  # Distinction, First Class, etc.

    class Meta:
        ordering = ['-point']

    def __str__(self):
        return f"{self.grade} = {self.point}"


class StudentProfile(models.Model):
    """Student profile linked to User."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students', null=True)
    enrollment_number = models.CharField(max_length=50, unique=True)
    current_semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['enrollment_number']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.enrollment_number})"


class FacultyProfile(models.Model):
    """Faculty profile linked to User."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_profile'
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='faculty', null=True)
    employee_id = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


class Enrollment(models.Model):
    """Student enrollment in semester courses."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'}
    )
    semester_course = models.ForeignKey(SemesterCourse, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'semester_course']

    def __str__(self):
        return f"{self.student} in {self.semester_course}"
