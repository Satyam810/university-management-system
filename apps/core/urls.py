from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('messages/', views.message_inbox, name='message_inbox'),
    path('messages/sent/', views.message_sent, name='message_sent'),
    path('messages/compose/', views.message_compose, name='message_compose'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('documents/bonafide/', views.document_bonafide, name='document_bonafide'),
    path('documents/grade-report/', views.document_grade_report, name='document_grade_report'),
    path('documents/admit-card/', views.document_admit_card, name='document_admit_card'),
    path('chatbot/', views.ai_chatbot, name='chatbot'),
]
