"""
Management command to create sample data for UMS.
Run: python manage.py setup_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.academics.models import (
    Department, Semester, Course, SemesterCourse, GradePointMapping,
    StudentProfile, FacultyProfile, Enrollment
)
from apps.attendance.models import QRSession, AttendanceRecord
from apps.results.models import Grade, SemesterResult
from apps.timetable.models import Slot, Classroom, TimetableEntry
from apps.core.models import Announcement, Event
from datetime import date, timedelta, time
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for UMS'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Grade mappings
        grades_data = [
            ('A+', Decimal('4.00'), 'Distinction'),
            ('A', Decimal('3.75'), 'First Class'),
            ('B+', Decimal('3.25'), 'First Class'),
            ('B', Decimal('3.00'), 'Second Class'),
            ('C+', Decimal('2.75'), 'Second Class'),
            ('C', Decimal('2.50'), 'Pass'),
            ('D', Decimal('2.00'), 'Pass'),
            ('F', Decimal('0.00'), 'Fail'),
        ]
        for g, p, d in grades_data:
            GradePointMapping.objects.get_or_create(grade=g, defaults={'point': p, 'description': d})

        # Departments
        dept_cs, _ = Department.objects.get_or_create(code='CS', defaults={'name': 'Computer Science'})
        dept_ee, _ = Department.objects.get_or_create(code='EE', defaults={'name': 'Electrical Engineering'})

        # Semesters
        today = date.today()
        sem1, _ = Semester.objects.get_or_create(code='F24', defaults={
            'name': 'Fall 2024', 'start_date': today - timedelta(days=90),
            'end_date': today + timedelta(days=30), 'is_active': True
        })
        sem2, _ = Semester.objects.get_or_create(code='S24', defaults={
            'name': 'Spring 2024', 'start_date': today - timedelta(days=180),
            'end_date': today - timedelta(days=60), 'is_active': False
        })

        # Courses
        course_ds, _ = Course.objects.get_or_create(department=dept_cs, code='CS101', defaults={'name': 'Data Structures', 'credits': 3})
        course_db, _ = Course.objects.get_or_create(department=dept_cs, code='CS102', defaults={'name': 'Database Systems', 'credits': 3})
        course_ml, _ = Course.objects.get_or_create(department=dept_cs, code='CS201', defaults={'name': 'Machine Learning', 'credits': 4})

        # Users
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@ums.edu', 'first_name': 'Admin', 'last_name': 'User',
            'role': 'ADMIN', 'is_staff': True, 'is_superuser': True
        })
        if not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.save()

        faculty_user, _ = User.objects.get_or_create(username='faculty1', defaults={
            'email': 'faculty@ums.edu', 'first_name': 'John', 'last_name': 'Professor',
            'role': 'FACULTY'
        })
        if not faculty_user.check_password('faculty123'):
            faculty_user.set_password('faculty123')
            faculty_user.save()

        FacultyProfile.objects.get_or_create(user=faculty_user, defaults={'employee_id': 'EMP001', 'department': dept_cs})

        student1, _ = User.objects.get_or_create(username='student1', defaults={
            'email': 'student1@ums.edu', 'first_name': 'Alice', 'last_name': 'Smith',
            'role': 'STUDENT'
        })
        if not student1.check_password('student123'):
            student1.set_password('student123')
            student1.save()

        student2, _ = User.objects.get_or_create(username='student2', defaults={
            'email': 'student2@ums.edu', 'first_name': 'Bob', 'last_name': 'Jones',
            'role': 'STUDENT'
        })
        if not student2.check_password('student123'):
            student2.set_password('student123')
            student2.save()

        StudentProfile.objects.get_or_create(user=student1, defaults={'enrollment_number': 'ENR001', 'department': dept_cs, 'current_semester': sem1})
        StudentProfile.objects.get_or_create(user=student2, defaults={'enrollment_number': 'ENR002', 'department': dept_cs, 'current_semester': sem1})

        # Semester courses
        sc1, _ = SemesterCourse.objects.get_or_create(semester=sem1, course=course_ds, defaults={'faculty': faculty_user})
        sc2, _ = SemesterCourse.objects.get_or_create(semester=sem1, course=course_db, defaults={'faculty': faculty_user})

        # Enrollments
        Enrollment.objects.get_or_create(student=student1, semester_course=sc1)
        Enrollment.objects.get_or_create(student=student1, semester_course=sc2)
        Enrollment.objects.get_or_create(student=student2, semester_course=sc1)

        # Grades
        gpa_a = GradePointMapping.objects.get(grade='A')
        gpa_b = GradePointMapping.objects.get(grade='B+')
        Grade.objects.get_or_create(student=student1, semester_course=sc1, defaults={'grade_point': gpa_a})
        Grade.objects.get_or_create(student=student1, semester_course=sc2, defaults={'grade_point': gpa_b})
        Grade.objects.get_or_create(student=student2, semester_course=sc1, defaults={'grade_point': gpa_b})

        # Slots and classrooms
        slot1, _ = Slot.objects.get_or_create(day='MON', start_time=time(9, 0), defaults={'end_time': time(10, 0), 'slot_number': 1})
        room1, _ = Classroom.objects.get_or_create(name='R101', defaults={'building': 'Main', 'capacity': 50})
        TimetableEntry.objects.get_or_create(semester_course=sc1, slot=slot1, defaults={'classroom': room1})

        # Announcements
        Announcement.objects.get_or_create(title='Welcome to UMS', defaults={
            'content': 'Welcome to the University Management System. Check announcements regularly.',
            'created_by': admin_user, 'is_featured': True
        })
        Event.objects.get_or_create(title='Annual Day', defaults={
            'event_date': today + timedelta(days=30), 'venue': 'Main Hall'
        })

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('Login: admin / admin123 (Admin), faculty1 / faculty123 (Faculty), student1 / student123 (Student)')
