# University Management System (UMS)

Enterprise-grade Django application for university management with QR attendance, GPA/CGPA, analytics, and AI features.

## Tech Stack

- Django 5.x
- SQLite3 (PostgreSQL-ready)
- Bootstrap 5
- Chart.js
- qrcode, reportlab, Pillow

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or: source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts for username, email, password. Set role to ADMIN in Django admin after creation.

### 5. Load Sample Data (Optional)

```bash
python manage.py setup_sample_data
```

This creates:
- Admin: `admin` / `admin123`
- Faculty: `faculty1` / `faculty123`
- Students: `student1` / `student123`, `student2` / `student123`
- Departments, courses, semesters, enrollments, grades, timetable

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000

## Superuser Instructions

1. Run `python manage.py createsuperuser`
2. Login to /admin/
3. Edit your user and set **Role** to **Admin**
4. Save

Or use sample data: `admin` / `admin123`

## Features

- **Smart QR Attendance**: Faculty generates time-limited QR, students scan to mark attendance
- **GPA/CGPA**: Auto-calculated from grades, classification (Distinction, First Class, etc.)
- **AI Chatbot**: Rule-based assistant for attendance, GPA, assignments
- **Analytics**: Admin/Faculty/Student dashboards with Chart.js
- **Assignments**: Upload, submit, grade, late marking
- **Timetable**: Weekly schedule, conflict detection
- **Documents**: Bonafide, Admit Card, Grade Report (PDF)
- **Messaging**: Faculty-Student communication, announcements
- **Events & Notices**: University events and announcements

## Folder Structure

```
ums/
├── config/          # Django settings
├── apps/
│   ├── accounts/    # Custom User, roles
│   ├── academics/  # Department, Course, Semester
│   ├── attendance/ # QR attendance
│   ├── assignments/
│   ├── results/    # GPA/CGPA
│   ├── timetable/
│   ├── notifications/
│   ├── analytics/
│   └── core/       # Announcements, messages, documents
├── templates/
├── static/
├── media/
└── utils/
```

## Switching to PostgreSQL

Uncomment the PostgreSQL block in `config/settings.py` and set environment variables:

```
DB_NAME=ums_db
DB_USER=ums_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```
