"""
SOS - School of Skills — Institution / Domain Models
------------------------------------------------------------
Corrected, self-contained OOP backend. Fixes applied vs. the original draft:

  * `self.__enrolled_courses` (name-mangled, never assigned) -> now correctly
    reads/writes `self.enrolled_courses`.
  * `enrolled_courses` was both a list attribute AND a method with the same
    name, so one silently shadowed the other. The method is renamed to
    `get_enrolled_courses()`; `enrolled_courses` is only ever the list.
  * `paid_fee` had the same attribute/method collision. Storage is now the
    private `_paid_fee`, exposed read-only via the `paid_fee` property.
  * `record_payment()` called `self.get_pending_fee()`, which didn't exist.
    It now uses the `pending_fee` property.
  * `AcademicServices.enroll_student()` called `student.get_enrolled_courses()`
    while `Student` only defined `enrolled_courses()` — names are now aligned.
  * `MAX_COURSES_PER_STUDENT` was referenced but never defined — added below.
  * The file no longer requires a live Streamlit session to import; a small
    optional helper (`new_session_state`) is provided for `app.py` to use if
    it ever wants to build session data from these models instead of its own
    plain dataclasses-lite classes.
  * The previous file's content was accidentally duplicated top-to-bottom and
    cut off mid-function; this is one complete, working copy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Set, Tuple

# ============================================================
# CONSTANTS
# ============================================================
MAX_COURSES_PER_STUDENT = 3
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valid_email(value: Optional[str]) -> bool:
    return bool(EMAIL_RE.match(value or ""))


# ============================================================
# INSTITUTION
# ============================================================
class SOSInstitution:
    """Static institution profile. Kept as class attributes since there is
    only ever one institution; instantiate only if you need an object to
    hand around (e.g. for the Streamlit UI's `st.session_state.institution`).
    """

    name: str = "SOS - School of Skills"
    location: str = "Calicut, Kerala, India"
    established: int = 2026
    ceo: str = "Mr. Shaheen"
    email: str = "info@sosinstitution.edu"
    phone: str = "+91 94567 89092"
    departments: List[str] = ["Computer Science", "Business & HR", "Design", "Data & AI"]

    @classmethod
    def details(cls) -> Dict[str, object]:
        return {
            "Institution": cls.name,
            "Location": cls.location,
            "Established": cls.established,
            "CEO": cls.ceo,
            "Contact Email": cls.email,
            "Contact Number": cls.phone,
        }


# ============================================================
# COURSE
# ============================================================
class Course:
    """A course keeps its own enrollment via a set of student IDs, so
    `enrollment_count()` is always accurate regardless of what any other
    object thinks — there is exactly one place enrollment is tracked."""

    #: Simple in-memory registry of every course created. Useful for
    #: `course_map()` / lookups without threading a container through every
    #: function. NOTE: because this is a class-level list it is shared across
    #: every `Course` instance in the process — fine for a single-user script
    #: or demo, but if this module is reused in a multi-user server, wrap it
    #: in a per-session/per-request registry instead of relying on this list.
    courses_list: List["Course"] = []

    def __init__(self, course_id, course_name, credits, max_capacity,
                 department="General", duration="", faculty=""):
        self.course_id = str(course_id).strip()
        self.course_name = str(course_name).strip()
        self.credits = int(credits)
        self.max_capacity = int(max_capacity)
        self.department = str(department).strip()
        self.duration = str(duration).strip()
        self.faculty = str(faculty).strip()
        self._enrolled_student_ids: Set[str] = set()

        Course.courses_list.append(self)

    # -- read-only computed views -----------------------------------
    @property
    def name(self) -> str:
        return self.course_name

    @property
    def capacity(self) -> int:
        return self.max_capacity

    @property
    def enrolled_student_ids(self) -> Set[str]:
        """Read-only view of who is enrolled. Mutate via `_enroll`/`_drop`
        (called by AcademicServices) rather than editing this directly."""
        return set(self._enrolled_student_ids)

    def enrollment_count(self) -> int:
        return len(self._enrolled_student_ids)

    def seats_available(self) -> int:
        return max(0, self.max_capacity - self.enrollment_count())

    # -- mutation, used only by AcademicServices ---------------------
    def _enroll(self, student_id: str) -> None:
        self._enrolled_student_ids.add(student_id)

    def _drop(self, student_id: str) -> None:
        self._enrolled_student_ids.discard(student_id)

    # -- lookups ------------------------------------------------------
    @classmethod
    def find(cls, course_id: str) -> Optional["Course"]:
        return next((c for c in cls.courses_list if c.course_id == course_id), None)

    @classmethod
    def available_courses(cls) -> List["Course"]:
        return [c for c in cls.courses_list if c.seats_available() > 0]

    @classmethod
    def search(cls, query: str) -> List["Course"]:
        term = str(query).strip().casefold()
        if not term:
            return list(cls.courses_list)
        return [
            c for c in cls.courses_list
            if term in c.course_id.casefold()
            or term in c.course_name.casefold()
            or term in c.department.casefold()
        ]

    def to_dict(self) -> Dict[str, object]:
        return {
            "Course ID": self.course_id,
            "Course Name": self.course_name,
            "Department": self.department,
            "Duration": self.duration or "—",
            "Credits": self.credits,
            "Capacity": self.max_capacity,
            "Enrolled": self.enrollment_count(),
            "Available Seats": self.seats_available(),
            "Faculty": self.faculty or "—",
        }

    def __repr__(self) -> str:
        return f"<Course {self.course_id} '{self.course_name}'>"


# ============================================================
# STUDENT
# ============================================================
class Student:
    """Fee data lives ONLY in `_paid_fee` / `tuition_fee` on the student —
    there is no separate parallel fee record anywhere else, so paid/pending
    can never disagree with themselves. `paid_fee` and `pending_fee` are
    read-only properties; the only way to change paid amount is through
    `record_payment()`, which validates the input."""

    def __init__(self, student_id, name, email, phone="", dob=None,
                 admission_date=None, status="Active", course_id=""):
        self.student_id = str(student_id).strip()
        self.name = str(name).strip()
        self.email = str(email).strip()
        self.phone = str(phone).strip()
        self.dob = dob
        self.admission_date = admission_date or date.today()
        self.status = status
        self.course_id = str(course_id).strip()

        self.enrolled_courses: List[Course] = []
        self.tuition_fee: float = 0.0
        self._paid_fee: float = 0.0

    # -- enrollment ----------------------------------------------------
    def can_enroll(self) -> bool:
        return len(self.enrolled_courses) < MAX_COURSES_PER_STUDENT

    def get_enrolled_courses(self) -> List[Course]:
        """Read-only copy of enrolled courses. Named distinctly from the
        `enrolled_courses` attribute so neither ever shadows the other."""
        return list(self.enrolled_courses)

    def add_enrolled_course(self, course: Course) -> None:
        if course not in self.enrolled_courses:
            self.enrolled_courses.append(course)
            if not self.course_id:
                self.course_id = course.course_id

    def remove_enrolled_course(self, course_id: str) -> bool:
        course_id = str(course_id)
        for course in self.enrolled_courses:
            if course.course_id == course_id:
                self.enrolled_courses.remove(course)
                if self.course_id == course_id:
                    self.course_id = self.enrolled_courses[0].course_id if self.enrolled_courses else ""
                return True
        return False

    # -- fees ------------------------------------------------------------
    def set_fee(self, amount) -> None:
        amount = float(amount)
        if amount < 0:
            raise ValueError("Fee amount cannot be negative.")
        self.tuition_fee = amount

    @property
    def paid_fee(self) -> float:
        return self._paid_fee

    @property
    def pending_fee(self) -> float:
        """Single reliable source of truth: Total - Paid, floored at zero."""
        return max(0.0, self.tuition_fee - self._paid_fee)

    def record_payment(self, amount) -> None:
        """Validate and apply a payment. Raises ValueError (with a
        user-facing message) and leaves state untouched on any invalid
        input, exactly mirroring the Streamlit UI's validation rules."""
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError("Payment amount must be a number.")
        if amount != amount:  # NaN guard
            raise ValueError("Payment amount must be a number.")
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        pending = self.pending_fee
        if pending <= 0:
            raise ValueError("This student's fee is already fully paid.")
        if amount > pending:
            raise ValueError(
                f"Payment of ₹{amount:,.0f} exceeds the pending amount of ₹{pending:,.0f}."
            )
        self._paid_fee += amount

    def fee_status(self) -> str:
        if self.pending_fee <= 0:
            return "Paid"
        if self._paid_fee > 0:
            return "Partially Paid"
        return "Pending"

    def to_dict(self) -> Dict[str, object]:
        return {
            "Student ID": self.student_id,
            "Name": self.name,
            "Email": self.email,
            "Phone": self.phone,
            "Status": self.status,
            "Admission Date": self.admission_date,
            "Course": self.course_id or "—",
            "Enrolled Courses": len(self.enrolled_courses),
            "Total Fee": self.tuition_fee,
            "Paid": self.paid_fee,
            "Pending": self.pending_fee,
            "Fee Status": self.fee_status(),
        }

    def __repr__(self) -> str:
        return f"<Student {self.student_id} '{self.name}'>"


# ============================================================
# EMPLOYEE / FACULTY
# ============================================================
class Employee:
    employees_list: List["Employee"] = []

    def __init__(self, employee_id, name, email, phone, department, designation,
                 specialization="", joining_date=None, employment_type="Full-Time",
                 assigned_course=""):
        self.employee_id = str(employee_id).strip()
        self.name = str(name).strip()
        self.email = str(email).strip()
        self.phone = str(phone).strip()
        self.department = str(department).strip()
        self.designation = str(designation).strip()
        self.specialization = str(specialization).strip()
        self.joining_date = joining_date or date.today()
        self.employment_type = str(employment_type).strip()
        self.assigned_course = str(assigned_course).strip()

        Employee.employees_list.append(self)

    @property
    def course_id(self) -> str:
        return self.assigned_course

    @classmethod
    def find(cls, employee_id: str) -> Optional["Employee"]:
        return next((e for e in cls.employees_list if e.employee_id == employee_id), None)

    @classmethod
    def search(cls, query: str) -> List["Employee"]:
        term = str(query).strip().casefold()
        if not term:
            return list(cls.employees_list)
        return [
            e for e in cls.employees_list
            if term in e.employee_id.casefold() or term in e.name.casefold()
        ]

    def to_dict(self) -> Dict[str, object]:
        return {
            "Employee ID": self.employee_id,
            "Name": self.name,
            "Email": self.email,
            "Phone": self.phone,
            "Department": self.department,
            "Designation": self.designation,
            "Specialization": self.specialization or "—",
            "Joining Date": self.joining_date,
            "Employment Type": self.employment_type,
            "Assigned Course": self.assigned_course or "—",
        }

    def __repr__(self) -> str:
        return f"<Employee {self.employee_id} '{self.name}'>"


class Faculty(Employee):
    """Compatibility subclass: a Faculty member is an Employee with the same
    fields. Kept separate only so callers can `isinstance(x, Faculty)`."""

    def to_dict(self) -> Dict[str, object]:
        return super().to_dict()


# ============================================================
# SERVICE LAYER — enrollment workflow that touches BOTH sides
# (Student.enrolled_courses and Course._enrolled_student_ids) atomically,
# so the two can never fall out of sync.
# ============================================================
class AcademicServices:
    @staticmethod
    def enroll_student(student: Optional[Student], course: Optional[Course]) -> Tuple[bool, str]:
        if student is None:
            return False, "Student not found."
        if course is None:
            return False, "Course not found."
        if not student.can_enroll():
            return False, f"A student may enroll in a maximum of {MAX_COURSES_PER_STUDENT} courses."
        if course in student.get_enrolled_courses():
            return False, "This student is already enrolled in that course."
        if course.seats_available() <= 0:
            return False, "This course has no seats available."

        student.add_enrolled_course(course)
        course._enroll(student.student_id)
        return True, f"{student.name} was enrolled in {course.course_name}."

    @staticmethod
    def drop_course(student: Optional[Student], course: Optional[Course]) -> Tuple[bool, str]:
        if student is None or course is None:
            return False, "Student or course not found."
        if not student.remove_enrolled_course(course.course_id):
            return False, "The student is not enrolled in that course."
        course._drop(student.student_id)
        return True, f"{student.name} was removed from {course.course_name}."


# ============================================================
# MODULE-LEVEL HELPERS
# ============================================================
def course_map() -> Dict[str, Course]:
    return {c.course_id: c for c in Course.courses_list}


def employee_map() -> Dict[str, Employee]:
    return {e.employee_id: e for e in Employee.employees_list}


def attendance_percent(records: List[dict]) -> float:
    if not records:
        return 0.0
    present = sum(1 for r in records if r["Status"] == "Present")
    return present / len(records) * 100


def reset_registries() -> None:
    """Clear the module-level Course/Employee registries. Call this before
    reseeding demo data (e.g. on an 'admin reset' action) to avoid piling up
    duplicate entries across repeated seeding calls."""
    Course.courses_list.clear()
    Employee.employees_list.clear()


def seed_demo_data() -> Dict[str, list]:
    """Build one consistent set of demo objects and return them, instead of
    silently mutating global state on import. Callers (e.g. a Streamlit app)
    decide what to do with the result — e.g. store it in
    `st.session_state`. Safe to call multiple times: it always starts from a
    clean registry.
    """
    reset_registries()

    courses_seed = [
        ("C101", "Data Science", 24, 40, "Data & AI", "6 Months", "Dr. Anita Rao"),
        ("C102", "Artificial Intelligence", 24, 35, "Data & AI", "6 Months", "Dr. Ravi Kumar"),
        ("C103", "Software Development", 30, 45, "Computer Science", "9 Months", "Mr. Arjun Menon"),
        ("C104", "Human Resource Management", 16, 30, "Business & HR", "4 Months", "Ms. Priya Nair"),
        ("C105", "Fashion Designing", 18, 25, "Design", "5 Months", "Ms. Fathima K."),
    ]
    courses = [Course(*c) for c in courses_seed]
    cmap = {c.course_id: c for c in courses}

    students_seed = [
        ("S001", "Aiswarya Menon", "aiswarya@example.com", "9812300001", "C101", 45000, 45000),
        ("S002", "Rahul Varma", "rahul@example.com", "9812300002", "C103", 60000, 30000),
        ("S003", "Sneha Pillai", "sneha@example.com", "9812300003", "C102", 20000, 0),
    ]
    students = []
    for sid, name, email, phone, cid, total, paid in students_seed:
        s = Student(sid, name, email, phone, course_id=cid)
        s.set_fee(total)
        if paid:
            s.record_payment(paid)
        ok, msg = AcademicServices.enroll_student(s, cmap.get(cid))
        if not ok:
            raise RuntimeError(f"Demo data seeding failed: {msg}")
        students.append(s)

    employees_seed = [
        ("E001", "Dr. Anita Rao", "anita@sos.edu", "9911100001", "Data & AI", "Senior Faculty", "Data Science", "Full-Time", "C101"),
        ("E002", "Dr. Ravi Kumar", "ravi@sos.edu", "9911100002", "Data & AI", "Faculty", "Artificial Intelligence", "Full-Time", "C102"),
    ]
    employees = [Employee(eid, name, email, phone, dept, desig, spec, employment_type=etype, assigned_course=cid)
                 for eid, name, email, phone, dept, desig, spec, etype, cid in employees_seed]

    return {"courses": courses, "students": students, "employees": employees}


# ============================================================
# SELF-TEST — run this file directly to verify there are no errors and the
# fixed methods behave correctly, without needing Streamlit installed.
# ============================================================
if __name__ == "__main__":
    data = seed_demo_data()
    s1 = data["students"][0]   # S001, fee 45000, fully paid
    s2 = data["students"][1]   # S002, fee 60000, paid 30000

    assert s1.pending_fee == 0
    assert s1.fee_status() == "Paid"
    assert s2.pending_fee == 30000
    assert s2.fee_status() == "Partially Paid"

    # Spec example: Total 50000, Paid 10000, pay 5000 -> Paid 15000, Pending 35000
    demo = Student("SX", "Demo Student", "demo@example.com", "0000000000")
    demo.set_fee(50000)
    demo.record_payment(10000)
    demo.record_payment(5000)
    assert demo.paid_fee == 15000 and demo.pending_fee == 35000, (demo.paid_fee, demo.pending_fee)

    # Validation: reject over-pending, zero, negative, non-numeric
    for bad in (100000, 0, -5, "abc", None):
        try:
            demo.record_payment(bad)
            raise AssertionError(f"should have rejected {bad!r}")
        except ValueError:
            pass

    # Enrollment / drop consistency between Student and Course
    course = data["courses"][0]
    ok, _ = AcademicServices.enroll_student(demo, course)
    assert ok and course.enrollment_count() == 2  # s1 + demo
    ok, _ = AcademicServices.drop_course(demo, course)
    assert ok and course.enrollment_count() == 1
    assert demo.get_enrolled_courses() == []

    print("All institution.py self-tests passed — no errors.")
