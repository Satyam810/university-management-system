"""Assignment views."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm
from apps.academics.models import Enrollment, SemesterCourse
from apps.accounts.models import Role
from apps.core.decorators import faculty_required, student_required


@login_required
def assignment_list(request):
    if request.user.role == Role.FACULTY:
        courses = SemesterCourse.objects.filter(faculty=request.user)
        assignments = Assignment.objects.filter(semester_course__in=courses).select_related('semester_course__course')
    elif request.user.role == Role.STUDENT:
        enrollments = Enrollment.objects.filter(student=request.user)
        assignments = Assignment.objects.filter(semester_course__in=[e.semester_course for e in enrollments]).select_related('semester_course__course')
    else:
        assignments = []
    return render(request, 'assignments/list.html', {'assignments': assignments})


@faculty_required
def assignment_create(request, semester_course_id):
    from apps.academics.models import SemesterCourse
    semester_course = get_object_or_404(SemesterCourse, id=semester_course_id, faculty=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.semester_course = semester_course
            obj.created_by = request.user
            obj.save()
            return redirect('assignments:list')
    else:
        form = AssignmentForm()
    return render(request, 'assignments/form.html', {'form': form, 'semester_course': semester_course})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submission = None
    if request.user.role == Role.STUDENT:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        # Check enrollment
        if not Enrollment.objects.filter(student=request.user, semester_course=assignment.semester_course).exists():
            return HttpResponseForbidden()
    elif request.user.role == Role.FACULTY:
        if assignment.created_by != request.user:
            return HttpResponseForbidden()
    return render(request, 'assignments/detail.html', {'assignment': assignment, 'submission': submission})


@student_required
def submission_create(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not Enrollment.objects.filter(student=request.user, semester_course=assignment.semester_course).exists():
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.assignment = assignment
            obj.student = request.user
            obj.save()
            return redirect('assignments:detail', pk=assignment.pk)
    else:
        form = SubmissionForm()
    return render(request, 'assignments/submit.html', {'form': form, 'assignment': assignment})


@faculty_required
def submission_grade(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if submission.assignment.created_by != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        marks = request.POST.get('marks')
        feedback = request.POST.get('feedback', '')
        if marks is not None:
            submission.marks = int(marks) if marks else None
            submission.feedback = feedback
            submission.save()
            return redirect('assignments:detail', pk=submission.assignment.pk)
    return render(request, 'assignments/grade.html', {'submission': submission})
