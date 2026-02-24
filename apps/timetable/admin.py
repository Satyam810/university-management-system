from django.contrib import admin
from .models import Slot, Classroom, TimetableEntry


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ['day', 'start_time', 'end_time', 'slot_number']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'capacity']


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['semester_course', 'slot', 'classroom']
