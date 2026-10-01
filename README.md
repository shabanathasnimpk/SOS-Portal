# SOS-Portal
# SOS-LMS-Portal
# SOS – School Of Skills LMS Portal

A professional **Learning Management System (LMS) and Institution Management Portal** developed for **SOS – School Of Skills** using **Python, Streamlit, Pandas, and Object-Oriented Programming (OOP)**.

The system provides a centralized platform for managing students, courses, faculty/employees, enrollments, attendance, fees, reports, and institution information through an interactive web-based dashboard.

---

## 📌 Project Overview

**SOS – School Of Skills LMS Portal** is designed to simplify and organize the day-to-day academic and administrative activities of an educational institution.

The application provides an interactive dashboard with dedicated modules for:

* Student Management
* Course Management
* Faculty/Employee Management
* Student Enrollment
* Student Attendance
* Employee/Faculty Attendance
* Fee Management
* Reports
* Institution Information
* Administrative Operations

The project uses **Streamlit** to provide the web interface and Python OOP concepts to structure the institution, course, student, and employee models.

---

## ✨ Key Features

### 🏠 Dashboard

The dashboard provides an overview of the institution, including:

* Total Students
* Total Employees
* Total Courses
* Total Enrollments
* Student Attendance
* Employee Attendance
* Course-wise Enrollment
* Recent Activities
* Quick Navigation Actions

---

### 🏛️ Institution Management

Displays important information about SOS – School Of Skills, including:

* Institution name
* Location
* Established year
* Contact information
* Departments
* Institution description

The institution model is implemented separately in `institution.py` using an OOP-based structure.

---

### 🎓 Student Management

The student module allows administrators to:

* Register new students
* View all students
* Search students
* View student profiles
* Assign students to courses
* Track admission dates
* View student status
* View fee information
* View attendance information

The application also validates student email addresses and prevents duplicate Student IDs.

---

### 📚 Course Management

The course management module provides:

* Course creation
* Course listing
* Course search
* Course details
* Faculty assignment
* Department assignment
* Course duration
* Credit information
* Maximum capacity
* Enrollment tracking
* Available seat calculation

The separate OOP course model maintains enrollment information and provides course searching and availability functionality.

---

### 👨‍🏫 Faculty / Employee Management

The portal provides employee/faculty management features such as:

* Employee ID
* Name
* Email
* Phone
* Department
* Designation
* Specialization
* Joining Date
* Employment Type
* Assigned Course

The OOP backend also provides a `Faculty` compatibility class derived from the `Employee` model.

---

### 📝 Enrollment Management

The enrollment module manages the relationship between students and courses.

It supports:

* Student enrollment
* Course assignment
* Course capacity checking
* Enrollment tracking
* Course dropping
* Available-seat validation

The `AcademicServices` service layer keeps student and course enrollment data synchronized.

---

### 📅 Student Attendance

The attendance module allows administrators to:

* Select a course
* Select an attendance date
* Mark students as:

  * Present
  * Absent
  * Leave
* Save attendance records
* View attendance history
* Generate attendance summaries
* Calculate attendance percentages

---

### 👥 Employee / Faculty Attendance

The portal also supports attendance management for employees/faculty, allowing attendance information to be recorded and used in dashboard and reporting sections.

---

### 💰 Fee Management

The fee management module tracks:

* Total Fee
* Paid Amount
* Pending Amount
* Payment Status

Supported payment statuses include:

* **Paid**
* **Partially Paid**
* **Pending**

The system calculates pending fees from:

```text
Pending Fee = Total Fee - Paid Amount
```

Payments are validated to prevent:

* Zero payments
* Negative payments
* Invalid payment values
* Payments exceeding the pending amount
* Payments for already fully paid fees

The OOP `Student` model also implements fee handling through `tuition_fee`, `paid_fee`, `pending_fee`, and `record_payment()`.

---

## 🔧 Technical Improvements

The current version includes several reliability improvements.

### Single Source of Truth for Navigation

The Streamlit application uses `st.session_state.current_page` as the central navigation state.

This helps prevent the previous double-click navigation issue and allows Quick Actions to navigate to the selected page immediately.

### Reliable Fee Calculation

Fee information is maintained through a single fee state, while pending fees are calculated dynamically from the total and paid amounts.

This prevents paid and pending values from becoming inconsistent.

### OOP-Based Architecture

The `institution.py` module separates important domain models such as:

* `SOSInstitution`
* `Course`
* `Student`
* `Employee`
* `Faculty`
* `AcademicServices`

This provides a structured foundation for managing the institution's data and operations.

### Input Validation

The project includes validation for:

* Email addresses
* Student IDs
* Course IDs
* Payment amounts
* Course capacity
* Enrollment limits

---

## 🛠️ Technologies Used

| Technology          | Purpose                         |
| ------------------- | ------------------------------- |
| Python              | Core programming language       |
| Streamlit           | Interactive web application     |
| Pandas              | Data processing and tables      |
| OOP                 | Application and domain modeling |
| Dataclasses         | Structured data representation  |
| Regular Expressions | Email validation                |
| Python DateTime     | Date and attendance handling    |
| Session State       | Application state management    |
| HTML/CSS            | UI styling inside Streamlit     |

---

## 📁 Project Structure

```text
SOS-LMS-Portal/
│
├── app.py
│   └── Main Streamlit LMS and Management Portal
│
├── institution.py
│   └── OOP institution, course, student,
│       employee/faculty and academic service models
│
└── README.md
    └── Project documentation
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/FaheemaSadhikPV/SOS-LMS-Portal.git
```

### 2. Navigate to the Project

```bash
cd SOS-LMS-Portal
```

### 3. Install Required Libraries

```bash
pip install streamlit pandas
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🖥️ Application Interface

The portal uses a professional **Red / Black / White** visual theme with a sidebar-based navigation system.

## The application includes a responsive dashboard and dedicated pages for each major institutional operation.

## 🧩 OOP Concepts Demonstrated

This project demonstrates practical Python Object-Oriented Programming concepts including:

* Classes and Objects
* Encapsulation
* Properties
* Inheritance
* Class Methods
* Static Methods
* Private Attributes
* Data Validation
* Service Layer Design
* Object Relationships
* Class-level Registries

For example:

```python
class Faculty(Employee):
    pass
```

The project also uses properties for calculated values such as:

```python
@property
def pending_fee(self):
    return max(0.0, self.tuition_fee - self._paid_fee)
```

This keeps important calculated values consistent instead of storing duplicate values.

---

## 🔄 Application Workflow

```text
                 ┌─────────────────────┐
                 │   SOS LMS Portal    │
                 └──────────┬──────────┘
                            │
             ┌──────────────┴──────────────┐
             │                             │
      ┌──────▼──────┐               ┌──────▼──────┐
      │  Dashboard  │               │ Institution │
      └──────┬──────┘               └─────────────┘
             │
   ┌─────────┼─────────┬───────────┐
   │         │         │           │
   ▼         ▼         ▼           ▼
Students  Courses  Faculty    Enrollment
   │         │         │           │
   └─────────┴─────────┴───────────┘
             │
      ┌──────┴─────────┐
      │                │
      ▼                ▼
 Attendance           Fees
      │                │
      └────────┬───────┘
               ▼
            Reports
```

---

## 📊 Sample Modules

The application is initialized with sample institutional data covering courses, students, employees, enrollments, attendance, and fees. The Streamlit application stores its working data in session state so normal reruns do not reset user-entered data.

---

## 🔐 Data Handling

The current project is primarily an **in-memory educational/demo management system**.

Application data is maintained during the Streamlit session using `st.session_state`.

This makes the project suitable for:

* Academic projects
* Portfolio demonstrations
* LMS prototypes
* Python/Streamlit learning
* OOP demonstrations
* Institution management prototypes

For production deployment, a persistent database and authentication system can be added.

---

## 🧪 Testing

The `institution.py` module includes built-in self-tests that can be executed directly:

```bash
python institution.py
```

The self-tests verify:

* Fee calculations
* Payment validation
* Enrollment
* Course dropping
* Enrollment consistency

The file reports successful completion when these checks pass.

---

## 🔮 Future Enhancements

Potential future improvements include:

* User authentication and role-based access
* Admin / Faculty / Student accounts
* Database integration
* PostgreSQL or MySQL support
* Persistent attendance records
* Student result management
* Assignment management
* Online learning materials
* Exam and assessment management
* Automated reports
* PDF report generation
* Email notifications
* Payment gateway integration
* Student dashboard
* Faculty dashboard
* Course material management
* Deployment using Streamlit Cloud or another hosting platform

---

## 🎯 Project Objective

The primary objective of the SOS LMS Portal is to create a centralized and easy-to-use platform for managing the academic and administrative operations of an educational institution.

The project combines **Python programming, Object-Oriented Programming, data management, validation, and Streamlit application development** into a practical LMS-oriented system.

---

## Team Members

This project was collaboratively developed by:

| Team Members |
|-------------|
| Shabana Thasnim PK |
| Faheema Sadhik PV |
| Ahamed Zayan |
| Adul Ahamed |

Python | Data Science | Streamlit | OOP | LMS Development

---

## 📄 License

This project is intended for educational, learning, and portfolio purposes.

If a specific open-source license is required, an appropriate license such as MIT can be added to the repository.
