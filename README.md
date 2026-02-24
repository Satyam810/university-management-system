# 🎓 University Management System (UMS)

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.x-green?style=for-the-badge&logo=django)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?style=for-the-badge&logo=sqlite)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap%205-purple?style=for-the-badge&logo=bootstrap)
![License](https://img.shields.io/badge/License-Educational-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

Enterprise-grade **University Management System** built with **Django**, featuring Smart QR Attendance, GPA/CGPA automation, Analytics Dashboard, and AI-powered academic assistant.

---

## 🚀 Overview

A scalable and modular University Management System inspired by modern university ERP systems.  
Designed with clean architecture, role-based dashboards, secure QR attendance, and AI-driven academic insights.

---

## 🛠 Tech Stack

- **Backend:** Django (Latest)
- **Database:** SQLite3 (PostgreSQL-ready)
- **Frontend:** Bootstrap 5
- **Charts:** Chart.js
- **QR Code:** qrcode (Python)
- **PDF Generation:** ReportLab
- **Architecture:** Modular App-Based Structure
- **Security:** Role-based decorators, CSRF protection, session expiry

---

# 🔐 Role-Based System

### 👑 Admin
- Full system management
- User & department control
- Attendance analytics
- Academic performance monitoring
- Event & announcement control

### 👨‍🏫 Faculty
- Generate dynamic QR attendance
- Monitor class performance
- Upload & grade assignments
- Export attendance reports

### 🎓 Student
- Scan QR for attendance
- View GPA & CGPA
- Submit assignments
- Download academic documents
- Use AI chatbot assistant

---

# 📌 Core Features

## 1️⃣ Smart QR Attendance System

- Time-limited QR generation (2–5 minutes)
- UUID-based secure session IDs
- Duplicate prevention (DB-level constraint)
- Enrollment validation
- Late attendance detection
- Attendance CSV export

---

## 2️⃣ GPA & CGPA Automation

- Grade-to-point mapping
- Weighted CGPA calculation
- Academic classification (Distinction, First Class, etc.)
- Semester-wise performance tracking

---

## 3️⃣ AI-Powered Academic Insights

### 🤖 Rule-Based Chatbot
- Attendance queries
- GPA queries
- Assignment status queries
- Dynamic ORM-driven responses

### 📉 Risk Detection
- Low attendance prediction
- Weak academic performance detection

---

## 4️⃣ Analytics Dashboard

- Admin KPIs
- Faculty course performance
- Student GPA trends
- Attendance charts
- Enrollment growth visualization

---

## 5️⃣ Assignment Module

- Assignment upload & submission
- Deadline tracking
- Late submission detection
- Grading system

---

## 6️⃣ Timetable Management

- Weekly timetable scheduling
- Conflict prevention
- Unique slot enforcement
- Classroom allocation

---

## 7️⃣ Internal Messaging System

- Faculty ↔ Student communication
- Admin broadcast announcements
- Unread notification counter

---

## 8️⃣ Dynamic PDF Generation

Using ReportLab:

- Bonafide Certificate
- Admit Card
- Grade Report

Generated dynamically in memory and streamed securely.

---

# 🧱 Project Structure

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


# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/university-management-system-django.git
cd university-management-system-django
```

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate   # Mac/Linux
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Apply Migrations

```bash
python manage.py migrate
```

## 5️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

## 6️⃣ Load Sample Data (Optional)

```bash
python manage.py setup_sample_data
```

## 7️⃣ Run Development Server

```bash
python manage.py runserver
```

Visit:

```
http://127.0.0.1:8000
```

---

# 🔒 Security Features

- Role-based decorators & mixins
- CSRF protection
- UUID-based QR sessions
- Session expiry enforcement
- Unique attendance constraints
- Secure file streaming via FileResponse

---

# 📈 Scalability & Design

- PostgreSQL-ready
- Modular Django apps
- Clean ORM usage
- Separation of business logic
- Easily extendable AI module

---

# 🧠 Future Improvements

- NLP-based chatbot integration
- Email/SMS notification system
- Redis caching
- REST API integration
- Cloud deployment

---

# 👨‍💻 Author

Developed by Satyam Kumar (Ai & Ml)
---



## Switching to PostgreSQL

Uncomment the PostgreSQL block in `config/settings.py` and set environment variables:

```
DB_NAME=ums_db
DB_USER=ums_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

# 📄 License

This project is for educational and demonstration purposes.