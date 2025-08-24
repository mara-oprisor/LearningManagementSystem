# Learning Management System

A full-stack web application built with Python Flask, HTML, CSS, and Bootstrap that provides a complete learning management solution for administrators, instructors, and students.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)

---

## Overview

The Learning Management System (LMS) is designed to streamline the management of educational courses, assignments, and user accounts. It supports three user roles:

- **Admin:** Manage users, courses, and view system statistics.
- **Instructor:** Create courses, upload course materials, assign and grade assignments.
- **Student:** Enroll in courses, access materials, submit assignments, and view grades.

---

## Features

- **User Authentication & Authorization:**  
  Secure registration and login with role-based access control.

- **Admin Dashboard:**  
  View system statistics (total students, instructors, courses) and manage users (view profiles, change passwords, delete accounts).

- **Instructor Portal:**  
  Create and manage courses, upload materials, add assignments with deadlines, and grade student submissions.

- **Student Portal:**  
  Access enrolled courses, download materials, submit assignments (text or file upload), and view grades with feedback.

- **File Management:**  
  Secure file upload and download using Werkzeug's `secure_filename`, with organized storage for course materials and submissions.

- **Database Integration:**  
  Utilizes SQLAlchemy Object Relational Mapping with SQLite for managing users, courses, enrollments, assignments, submissions, and grades.

---

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Login, Flask-CKEditor, Flask-Bootstrap
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite
- **Utilities:** Werkzeug (for secure file uploads)

---

## Screenshots of the UI

![image](https://github.com/user-attachments/assets/d51f455b-7dc5-4778-8bf9-06a78c2f5876)

![image](https://github.com/user-attachments/assets/c3814a9b-c4d9-4ff8-971d-e0a58d2542c3)

