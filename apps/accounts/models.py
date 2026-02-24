"""
Custom User model with role-based system.
Supports ADMIN, FACULTY, STUDENT roles.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    FACULTY = 'FACULTY', 'Faculty'
    STUDENT = 'STUDENT', 'Student'


class User(AbstractUser):
    """Custom user model with role choices."""
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def get_role_display(self):
        return dict(Role.choices).get(self.role, self.role)

    @property
    def is_admin_user(self):
        return self.role == Role.ADMIN

    @property
    def is_faculty_user(self):
        return self.role == Role.FACULTY

    @property
    def is_student_user(self):
        return self.role == Role.STUDENT
