# Bulk Certificate Generator API

## 1. Project Overview

Bulk Certificate Generator is a Django REST API that accepts a list of recipients in a single request and generates a PDF certificate for each valid recipient.

The system:

- Accepts bulk certificate generation requests
- Validates recipient information
- Generates certificates using one predefined template
- Handles individual recipient failures
- Tracks job status and progress
- Provides failure reasons
- Allows generated certificates to be downloaded

No frontend is required for this project.

---

## 2. Technologies Used

- Python
- Django
- Django REST Framework
- SQLite
- ReportLab

---

## 3. Project Structure

```text
myproject/
│
├── certificates/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── utils.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── media/
│   └── certificates/
│
├── myproject/
│   ├── settings.py
│   └── urls.py
│
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md