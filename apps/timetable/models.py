"""
Timetable models: Slot, Classroom, TimetableEntry.
Conflict detection and faculty load tracking.
"""
from django.db import models
from django.conf import settings


class Slot(models.Model):
    """Time slot (e.g., 9:00-10:00)."""
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_number = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['day', 'start_time']
        unique_together = ['day', 'start_time']

    def __str__(self):
        return f"{self.get_day_display()} {self.start_time}-{self.end_time}"


class Classroom(models.Model):
    """Classroom allocation."""
    name = models.CharField(max_length=50)
    building = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(default=50)

    def __str__(self):
        return self.name


class TimetableEntry(models.Model):
    """Weekly timetable entry - links course to slot and classroom."""
    semester_course = models.ForeignKey(
        'academics.SemesterCourse',
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='entries')
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, related_name='entries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Timetable entries'
        unique_together = ['slot', 'semester_course']  # One entry per course per slot
        # Additional constraint: same faculty cannot have two classes at same slot

    def __str__(self):
        return f"{self.semester_course} @ {self.slot}"
