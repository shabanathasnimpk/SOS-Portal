"""
SOS - School Of Skills — Management Portal
Built with Python + Streamlit | Red / Black / White theme

Corrected / refactored version:
  - Single source of truth for page navigation (st.session_state.current_page
    bound directly to the sidebar radio's `key`), fixing the double-click bug.
  - Single source of truth for fee data (st.session_state.fees) with a proper
    validated payment-recording routine, fixing the pending/paid calculation.
  - Every mutation (add student/course/employee, enroll/drop, mark attendance,
    record payment, reset) triggers an immediate, safe st.rerun() so every
    page/tab reflects the change on the very next paint instead of needing a
    second interaction.
  - OOP models cleaned up: no attribute/method name collisions, no references
    to non-existent private attributes, clear encapsulation via properties.
"""

import streamlit as st
import pandas as pd
import datetime as dt
import re

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="SOS - School Of Skills",
    page_icon="🅢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# THEME — RED / BLACK / WHITE
# ============================================================
RED = "#E10600"
DARK_RED = "#A30000"
BLACK = "#000000"
CHARCOAL = "#151515"
CARD_BG = "#1A1A1A"
BORDER = "#2E2E2E"
WHITE = "#FFFFFF"
OFF_WHITE = "#E8E8E8"

st.markdown(f"""
<style>
    .stApp {{ background-color:{BLACK}; color:{WHITE}; }}
    #MainMenu, footer {{visibility:hidden;}}
    header[data-testid="stHeader"] {{ background-color:{BLACK}; }}

    /* Global text color */
    html, body, p, span, li, label, .stMarkdown, .stCaption, .stText,
    div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {{
        color:{WHITE} !important;
    }}
    h1, h2, h3, h4, h5, h6 {{ color:{WHITE} !important; }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {BLACK} 0%, {CHARCOAL} 100%);
        border-right: 3px solid {RED};
    }}
    section[data-testid="stSidebar"] * {{ color:{WHITE} !important; }}
    section[data-testid="stSidebar"] .stRadio label {{
        font-size:15px; padding:4px 0;
    }}
    section[data-testid="stSidebar"] hr {{ border-color:{RED}; }}

    .sos-logo-badge {{
        display:flex; align-items:center; gap:12px;
        background:{CARD_BG}; border:3px solid {RED}; border-radius:14px;
        padding:10px 16px; margin-bottom:6px;
    }}
    .sos-logo-circle {{
        width:46px; height:46px; border-radius:50%;
        background:linear-gradient(135deg,{RED},{DARK_RED});
        display:flex; align-items:center; justify-content:center;
        color:{WHITE}; font-weight:800; font-size:18px; letter-spacing:1px;
        border:2px solid {WHITE};
        flex-shrink:0;
    }}
    .sos-logo-text {{ line-height:1.1; }}
    .sos-logo-text .name {{ color:{WHITE} !important; font-weight:800; font-size:15px; }}
    .sos-logo-text .tag {{ color:{RED} !important; font-size:11px; font-weight:600; letter-spacing:1px; }}

    .page-title {{
        color:{WHITE} !important; border-left:6px solid {RED}; padding-left:14px;
        margin-bottom:4px; font-weight:800;
    }}
    .page-sub {{ color:{OFF_WHITE} !important; margin-bottom:18px; font-size:14px; }}

    .kpi-card {{
        background:{CARD_BG}; border:1px solid {BORDER}; border-top:5px solid {RED};
        border-radius:12px; padding:16px 18px; box-shadow:0 2px 10px rgba(225,6,0,0.08);
    }}
    .kpi-value {{ font-size:28px; font-weight:800; color:{WHITE} !important; }}
    .kpi-label {{ font-size:13px; color:{OFF_WHITE} !important; font-weight:600; text-transform:uppercase; letter-spacing:.5px; }}

    .sos-card {{
        background:{CARD_BG}; border:1px solid {BORDER}; border-radius:12px;
        padding:16px 18px; box-shadow:0 2px 6px rgba(0,0,0,0.4); margin-bottom:14px;
        border-left:5px solid {RED}; color:{WHITE} !important;
    }}
    .badge {{
        display:inline-block; padding:3px 10px; border-radius:20px;
        font-size:12px; font-weight:700; color:{WHITE} !important;
    }}
    .badge-green {{ background:#1e8e3e; }}
    .badge-yellow {{ background:#c98a00; }}
    .badge-red {{ background:{RED}; }}
    .badge-black {{ background:{CARD_BG}; border:1px solid {RED}; }}

    div.stButton > button {{
        background:{RED}; color:{WHITE}; border:none; border-radius:8px;
        font-weight:700; padding:8px 18px; transition:0.15s;
    }}
    div.stButton > button:hover {{ background:{DARK_RED}; color:{WHITE}; }}

    .stTabs [data-baseweb="tab-list"] {{ border-bottom:2px solid {RED}; }}
    .stTabs [data-baseweb="tab"] p {{ color:{OFF_WHITE} !important; }}
    .stTabs [aria-selected="true"] p {{ color:{RED} !important; font-weight:700; }}

    hr {{ border-color:{BORDER}; }}

    /* Inputs, selects, text areas */
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {{
        background-color:{CARD_BG} !important; color:{WHITE} !important;
        border:1px solid {BORDER} !important;
    }}
    .stSelectbox svg {{ fill:{WHITE} !important; }}
    div[data-baseweb="popover"] * {{ color:{WHITE} !important; }}
    ul[role="listbox"] {{ background-color:{CARD_BG} !important; }}

    /* Dataframes / tables */
    div[data-testid="stDataFrame"] {{ background-color:{CARD_BG}; border:1px solid {BORDER}; border-radius:8px; }}

    /* Expander */
    div[data-testid="stExpander"] {{ background-color:{CARD_BG}; border:1px solid {BORDER}; border-radius:10px; }}
    div[data-testid="stExpander"] summary {{ color:{WHITE} !important; }}

    /* Alerts */
    div[data-testid="stAlert"] {{ background-color:{CARD_BG}; border:1px solid {RED}; color:{WHITE} !important; }}

    /* Metric widgets */
    div[data-testid="stMetric"] {{ background-color:{CARD_BG}; border:1px solid {BORDER}; border-radius:10px; padding:8px; }}

    /* Radio / checkbox labels */
    .stRadio label, .stCheckbox label {{ color:{WHITE} !important; }}

    /* Form container */
    div[data-testid="stForm"] {{ background-color:{CHARCOAL}; border:1px solid {BORDER}; border-radius:12px; padding:16px; }}
</style>
""", unsafe_allow_html=True)


LOGO_URL = "https://soslearnings.com/images/logo1.png"


def sos_logo(sidebar=False):
    """Display the current SOS School Of Skills logo from the official site."""
    wrap_class = "sidebar-logo" if sidebar else ""
    st.markdown(f'<div class="{wrap_class}">', unsafe_allow_html=True)
    st.image(LOGO_URL, width=220)
    st.markdown("</div>", unsafe_allow_html=True)


def page_header(title, subtitle=""):
    st.markdown(f'<h2 class="page-title">{title}</h2>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-sub">{subtitle}</div>', unsafe_allow_html=True)


def kpi(col, label, value):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)


def status_badge(pct):
    if pct >= 85:
        return f'<span class="badge badge-green">{pct:.1f}% Good</span>'
    elif pct >= 65:
        return f'<span class="badge badge-yellow">{pct:.1f}% Low</span>'
    else:
        return f'<span class="badge badge-red">{pct:.1f}% Critical</span>'


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valid_email(email):
    return bool(EMAIL_RE.match(email or ""))


# ============================================================
# DATA MODELS (OOP)
# ------------------------------------------------------------
# Each class keeps its stored data in ordinary attributes and exposes
# read-only computed values through @property. No property/method ever
# shares a name with a plain instance attribute it would shadow or be
# shadowed by (that conflict is what breaks a class like this), and no
# code references a private/name-mangled attribute that was never set.
# ============================================================
class Institution:
    def __init__(self, name, location, established, phone, email, about, departments):
        self.name = name
        self.location = location
        self.established = established
        self.phone = phone
        self.email = email
        self.about = about
        self.departments = departments


class Course:
    def __init__(self, course_id, name, duration, credits, capacity, faculty, department):
        self.course_id = course_id
        self.name = name
        self.duration = duration
        self.credits = credits
        self.capacity = capacity
        self.faculty = faculty
        self.department = department

    def to_dict(self, enrolled):
        return {
            "Course ID": self.course_id, "Course Name": self.name,
            "Duration": self.duration, "Credits": self.credits,
            "Capacity": self.capacity, "Enrolled": enrolled,
            "Available Seats": max(self.capacity - enrolled, 0),
            "Faculty": self.faculty, "Department": self.department,
        }


class Student:
    def __init__(self, sid, name, email, phone, dob, course_id, admission_date, status="Active"):
        self.student_id = sid
        self.name = name
        self.email = email
        self.phone = phone
        self.dob = dob
        self.course_id = course_id
        self.admission_date = admission_date
        self.status = status


class Employee:
    def __init__(self, eid, name, email, phone, department, designation,
                 specialization, joining_date, emp_type, course_id):
        self.employee_id = eid
        self.name = name
        self.email = email
        self.phone = phone
        self.department = department
        self.designation = designation
        self.specialization = specialization
        self.joining_date = joining_date
        self.emp_type = emp_type
        self.course_id = course_id


# ============================================================
# SESSION STATE INITIALIZATION (sample data)
# ============================================================
def seed_state():
    """(Re)populate session state with the sample dataset. Only ever called
    once per session (guarded by `initialized`) or explicitly on reset, so a
    normal rerun never wipes out data the user has entered."""
    st.session_state.institution = Institution(
        name="SOS-School of Skills",
        location="Calicut, Kerala, India",
        established=2026,
        phone="+91 98765 43210",
        email="info@sosinstitution.edu",
        about="SOS Educational Institution is a premier center for technology, "
              "business and creative skills training, committed to producing "
              "industry-ready professionals through hands-on learning.",
        departments=["Computer Science", "Business & HR", "Design", "Data & AI"],
    )

    courses_seed = [
        ("C101", "Data Science", "6 Months", 24, 40, "Dr. Anita Rao", "Data & AI"),
        ("C102", "Artificial Intelligence", "6 Months", 24, 35, "Dr. Ravi Kumar", "Data & AI"),
        ("C103", "Software Development", "9 Months", 30, 45, "Mr. Arjun Menon", "Computer Science"),
        ("C104", "Human Resource Management", "4 Months", 16, 30, "Ms. Priya Nair", "Business & HR"),
        ("C105", "Fashion Designing", "5 Months", 18, 25, "Ms. Fathima K.", "Design"),
        ("C106", "Python Programming", "3 Months", 12, 50, "Mr. Arjun Menon", "Computer Science"),
        ("C107", "Machine Learning", "5 Months", 20, 35, "Dr. Anita Rao", "Data & AI"),
    ]
    st.session_state.courses = [Course(*c) for c in courses_seed]

    students_seed = [
        ("S001", "Aiswarya Menon", "aiswarya@example.com", "9812300001", dt.date(2001, 4, 12), "C101", dt.date(2026, 1, 10)),
        ("S002", "Rahul Varma", "rahul@example.com", "9812300002", dt.date(2000, 8, 2), "C103", dt.date(2026, 1, 12)),
        ("S003", "Sneha Pillai", "sneha@example.com", "9812300003", dt.date(2002, 1, 20), "C106", dt.date(2026, 2, 1)),
        ("S004", "Vishnu Nair", "vishnu@example.com", "9812300004", dt.date(1999, 11, 5), "C102", dt.date(2026, 2, 5)),
        ("S005", "Kavya Suresh", "kavya@example.com", "9812300005", dt.date(2001, 6, 30), "C105", dt.date(2026, 2, 15)),
    ]
    st.session_state.students = [Student(*s) for s in students_seed]

    employees_seed = [
        ("E001", "Dr. Anita Rao", "anita@sos.edu", "9911100001", "Data & AI", "Senior Faculty", "Data Science", dt.date(2018, 6, 1), "Full-Time", "C101"),
        ("E002", "Dr. Ravi Kumar", "ravi@sos.edu", "9911100002", "Data & AI", "Faculty", "Artificial Intelligence", dt.date(2020, 3, 15), "Full-Time", "C102"),
        ("E003", "Mr. Arjun Menon", "arjun@sos.edu", "9911100003", "Computer Science", "Trainer", "Software Development", dt.date(2019, 7, 20), "Full-Time", "C103"),
        ("E004", "Ms. Priya Nair", "priya@sos.edu", "9911100004", "Business & HR", "HR Manager", "HR Management", dt.date(2021, 1, 10), "Full-Time", "C104"),
        ("E005", "Ms. Fathima K.", "fathima@sos.edu", "9911100005", "Design", "Faculty", "Fashion Design", dt.date(2022, 5, 5), "Part-Time", "C105"),
        ("E006", "Mr. Suresh Babu", "suresh@sos.edu", "9911100006", "Administration", "Admin Staff", "Operations", dt.date(2017, 2, 1), "Full-Time", ""),
    ]
    st.session_state.employees = [Employee(*e) for e in employees_seed]

    st.session_state.enrollments = [
        {"Student ID": s.student_id, "Course ID": s.course_id, "Enrolled On": s.admission_date}
        for s in st.session_state.students
    ]

    st.session_state.student_attendance = []
    st.session_state.employee_attendance = []

    # Single source of truth for fee data. "Paid" is always the running total
    # actually received; "Pending" is *never* stored — it is always derived
    # as max(0, Total Fee - Paid) by pending_fee() below, so the two numbers
    # can never drift out of sync.
    st.session_state.fees = [
        {"Student ID": "S001", "Total Fee": 45000, "Paid": 45000},
        {"Student ID": "S002", "Total Fee": 60000, "Paid": 30000},
        {"Student ID": "S003", "Total Fee": 20000, "Paid": 0},
        {"Student ID": "S004", "Total Fee": 50000, "Paid": 50000},
        {"Student ID": "S005", "Total Fee": 35000, "Paid": 15000},
    ]

    st.session_state.activity_log = [
        "System initialized with sample institution data.",
    ]

    st.session_state.current_page = "🏠 Dashboard"
    st.session_state.initialized = True


def init_state():
    if "initialized" not in st.session_state:
        seed_state()


def log_activity(msg):
    st.session_state.activity_log.insert(0, f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M')} — {msg}")
    st.session_state.activity_log = st.session_state.activity_log[:15]


init_state()

# ============================================================
# HELPERS
# ============================================================
def course_map():
    return {c.course_id: c for c in st.session_state.courses}


def enrolled_count(course_id):
    return sum(1 for s in st.session_state.students if s.course_id == course_id and s.status == "Active")


def student_map():
    return {s.student_id: s for s in st.session_state.students}


def employee_map():
    return {e.employee_id: e for e in st.session_state.employees}


def fee_status(total, paid):
    if paid >= total:
        return "Paid"
    elif paid > 0:
        return "Partially Paid"
    return "Pending"


def pending_fee(record):
    """Single, reliable source of truth for the pending amount:
    Pending = Total Fee - Paid, floored at zero. Never stored separately."""
    return max(0, record["Total Fee"] - record["Paid"])


def record_payment(record, amount):
    """Validate and apply a payment to a fee record in place.

    Raises ValueError with a user-facing message on any invalid input and
    leaves the record completely untouched in that case. On success, updates
    `record["Paid"]` — the one place paid/pending data lives — so every page
    that reads st.session_state.fees sees the change immediately.
    """
    if amount is None:
        raise ValueError("Enter a payment amount.")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Payment amount must be a number.")
    if amount != amount:  # NaN guard
        raise ValueError("Payment amount must be a number.")
    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    pending = pending_fee(record)
    if pending <= 0:
        raise ValueError("This student's fee is already fully paid.")
    if amount > pending:
        raise ValueError(
            f"Payment of ₹{amount:,.0f} exceeds the pending amount of ₹{pending:,.0f}."
        )

    record["Paid"] += amount
    return record


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
PAGES = [
    "🏠 Dashboard", "🏛️ Institution", "🎓 Students", "📚 Courses",
    "👨‍🏫 Employees", "📝 Enrollment", "📅 Student Attendance",
    "👥 Employee Attendance", "💰 Fees", "📊 Reports", "⚙️ Administration",
]

# `current_page` in session_state is the ONE reliable navigation variable.
# It is guaranteed to exist by init_state()/seed_state(). Quick Action
# buttons write to it directly and call st.rerun(); the sidebar radio below
# is bound to it via `key=`, which is what actually fixes the double-click
# bug: because the radio's key IS "current_page", Streamlit renders the
# radio using session_state["current_page"] on every run (rather than
# silently keeping its own separate widget state and ignoring `index`), so
# a Quick Action's change is reflected the very next rerun — one click.
if st.session_state.current_page not in PAGES:
    st.session_state.current_page = PAGES[0]


def _navigate_to(page_name: str) -> None:
    """Callback used by every navigation control (sidebar radio is bound via
    its own `key`; Quick Action buttons call this via `on_click`). Callbacks
    run BEFORE the script body executes on the next rerun, so `current_page`
    is already correct by the time the sidebar radio (key="current_page") is
    instantiated — no ordering ambiguity, no extra click needed."""
    st.session_state.current_page = page_name

with st.sidebar:
    sos_logo(sidebar=True)
    st.markdown("---")
    st.sidebar.radio("Navigation", PAGES, key="current_page")

page = st.session_state.current_page

# ============================================================
# 1. DASHBOARD
# ============================================================
if page == "🏠 Dashboard":
    sos_logo()
    page_header(" Institution Dashboard ", "Overview of SOS Educational Institution")

    students = st.session_state.students
    employees = st.session_state.employees
    courses = st.session_state.courses
    enrollments = st.session_state.enrollments

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total Students", len(students))
    kpi(c2, "Total Employees", len(employees))
    kpi(c3, "Total Courses", len(courses))
    kpi(c4, "Total Enrollments", len(enrollments))

    st.write("")
    sa = st.session_state.student_attendance
    ea = st.session_state.employee_attendance
    s_pct = (sum(1 for a in sa if a["Status"] == "Present") / len(sa) * 100) if sa else 0
    e_pct = (sum(1 for a in ea if a["Status"] == "Present") / len(ea) * 100) if ea else 0

    c5, c6 = st.columns(2)
    kpi(c5, "Overall Student Attendance", f"{s_pct:.1f}%")
    kpi(c6, "Overall Employee Attendance", f"{e_pct:.1f}%")

    st.write("")
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("#### 📈 Course-wise Enrollment")
        if courses:
            chart_df = pd.DataFrame({
                "Course": [c.name for c in courses],
                "Enrolled": [enrolled_count(c.course_id) for c in courses],
            }).set_index("Course")
            st.bar_chart(chart_df, color=RED)
        else:
            st.info("No courses to chart yet.")

        st.markdown("#### 🕘 Recent Activities")
        if st.session_state.activity_log:
            for a in st.session_state.activity_log[:6]:
                st.markdown(f"<div class='sos-card'>{a}</div>", unsafe_allow_html=True)
        else:
            st.info("No recent activity.")

    with right:
        st.markdown("### Quick Actions")

        q1, q2, q3, q4 = st.columns(4)

        q1.button("🎓 Students", use_container_width=True,
                  on_click=_navigate_to, args=("🎓 Students",))
        q2.button("📚 Courses", use_container_width=True,
                  on_click=_navigate_to, args=("📚 Courses",))
        q3.button("📝 Enrollment", use_container_width=True,
                  on_click=_navigate_to, args=("📝 Enrollment",))
        q4.button("👨‍🏫 Employees", use_container_width=True,
                  on_click=_navigate_to, args=("👨‍🏫 Employees",))

# ============================================================
# 2. INSTITUTION
# ============================================================
elif page == "🏛️ Institution":
    sos_logo()
    inst = st.session_state.institution
    page_header("Institution", "Information about SOS - School Of Skills")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        <div class="sos-card">
            <h3>🏫 {inst.name}</h3>
            <p><b>📍 Location:</b> {inst.location}</p>
            <p><b>📅 Established:</b> {inst.established}</p>
            <p><b>📞 Phone:</b> {inst.phone}</p>
            <p><b>✉️ Email:</b> {inst.email}</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("#### 🏢 Departments")
        for department in inst.departments:
            st.markdown(f"<div class='sos-card'>🏢 {department}</div>", unsafe_allow_html=True)

    st.markdown("#### ℹ️ About SOS")
    st.markdown(f"<div class='sos-card'>{inst.about}</div>", unsafe_allow_html=True)

# ============================================================
# 3. COURSES
# ============================================================
elif page == "📚 Courses":
    sos_logo()
    page_header("Course Management")

    tab1, tab2, tab3 = st.tabs(["📋 All Courses", "➕ Add Course", "🔍 Search / Details"])

    with tab1:
        rows = [c.to_dict(enrolled_count(c.course_id)) for c in st.session_state.courses]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No courses yet. Add one from the 'Add Course' tab.")

    with tab2:
        with st.form("add_course", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cid = c1.text_input("Course ID (e.g. C108)")
            cname = c2.text_input("Course Name")
            duration = c1.text_input("Duration (e.g. 6 Months)")
            credits = c2.number_input("Credits", 1, 60, 12)
            capacity = c1.number_input("Maximum Capacity", 1, 500, 30)
            faculty = c2.selectbox(
                "Assigned Faculty",
                [e.name for e in st.session_state.employees] or ["— No employees yet —"],
            )
            dept = c1.selectbox("Department", st.session_state.institution.departments)
            add = st.form_submit_button("➕ Add Course")
            if add:
                ids = {c.course_id for c in st.session_state.courses}
                cid = cid.strip()
                cname = cname.strip()
                if not cid or not cname:
                    st.error("Course ID and Name are required.")
                elif cid in ids:
                    st.error(f"Course ID '{cid}' already exists.")
                else:
                    st.session_state.courses.append(Course(cid, cname, duration, credits, capacity, faculty, dept))
                    log_activity(f"Course '{cname}' ({cid}) added.")
                    st.success(f"Course '{cname}' added successfully.")
                    st.rerun()

    with tab3:
        query = st.text_input("🔍 Search by Course ID or Name", key="course_search").strip()

        if query:
            q = query.casefold()
            results = [
                c for c in st.session_state.courses
                if q in c.course_id.casefold() or q in c.name.casefold()
            ]
            if not results:
                st.error(f"❌ No such courses are available for '{query}'.")
        else:
            results = st.session_state.courses

        for c in results:
            en = enrolled_count(c.course_id)
            with st.expander(f"{c.course_id} — {c.name}"):
                st.write(
                    f"**Department:** {c.department}  |  "
                    f"**Duration:** {c.duration}  |  "
                    f"**Credits:** {c.credits}"
                )
                st.write(f"**Faculty:** {c.faculty}")
                st.write(
                    f"**Capacity:** {c.capacity}  |  "
                    f"**Enrolled:** {en}  |  "
                    f"**Available Seats:** {max(c.capacity - en, 0)}"
                )
                enrolled_students = [s for s in st.session_state.students if s.course_id == c.course_id]
                if enrolled_students:
                    st.write("**Enrolled Students:**")
                    st.dataframe(
                        pd.DataFrame([{"ID": s.student_id, "Name": s.name} for s in enrolled_students]),
                        hide_index=True, use_container_width=True,
                    )

# ============================================================
# 4. STUDENTS
# ============================================================
elif page == "🎓 Students":
    sos_logo()
    page_header("Student Management")

    tab1, tab2, tab3 = st.tabs(["📋 All Students", "➕ Register Student", "🔍 Search / Profile"])

    with tab1:
        cmap = course_map()
        rows = [{
            "Student ID": s.student_id, "Name": s.name, "Email": s.email, "Phone": s.phone,
            "Course": cmap[s.course_id].name if s.course_id in cmap else "—",
            "Admission Date": s.admission_date, "Status": s.status,
        } for s in st.session_state.students]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No students yet. Register one from the 'Register Student' tab.")

    with tab2:
        with st.form("add_student", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sid = c1.text_input("Student ID (e.g. S006)")
            name = c2.text_input("Full Name")
            email = c1.text_input("Email")
            phone = c2.text_input("Phone Number")
            dob = c1.date_input("Date of Birth", min_value=dt.date(1970, 1, 1), max_value=dt.date.today())
            course_options = [f"{c.course_id} — {c.name}" for c in st.session_state.courses]
            course_choice = c2.selectbox("Course", course_options or ["— No courses yet —"])
            admission_date = c1.date_input("Admission Date", dt.date.today())
            add = st.form_submit_button("➕ Register Student")
            if add:
                ids = {s.student_id for s in st.session_state.students}
                sid = sid.strip()
                name = name.strip()
                cid = course_choice.split(" — ")[0] if course_options else ""
                course = course_map().get(cid)
                if not sid or not name:
                    st.error("Student ID and Name are required.")
                elif sid in ids:
                    st.error(f"Student ID '{sid}' already exists.")
                elif not valid_email(email):
                    st.error("Please enter a valid email address.")
                elif course is None:
                    st.error("Please add a course before registering students.")
                elif enrolled_count(cid) >= course.capacity:
                    st.error(f"Course '{course.name}' is full. Cannot register student.")
                else:
                    st.session_state.students.append(Student(sid, name, email, phone, dob, cid, admission_date))
                    st.session_state.enrollments.append({"Student ID": sid, "Course ID": cid, "Enrolled On": admission_date})
                    st.session_state.fees.append({"Student ID": sid, "Total Fee": 30000, "Paid": 0})
                    log_activity(f"Student '{name}' ({sid}) registered into {course.name}.")
                    st.success(f"Student '{name}' registered successfully.")
                    st.rerun()

    with tab3:
        query = st.text_input("Search by Student ID or Name", key="student_search").strip()
        cmap = course_map()

        if query:
            q = query.casefold()
            results = [
                s for s in st.session_state.students
                if q in s.student_id.casefold() or q in s.name.casefold()
            ]
            if not results:
                st.warning(f"❌ No student found with ID or Name: '{query}'")
        else:
            results = st.session_state.students

        for s in results:
            with st.expander(f"{s.student_id} — {s.name}"):
                st.write(f"**Email:** {s.email}  |  **Phone:** {s.phone}")
                st.write(f"**DOB:** {s.dob}  |  **Status:** {s.status}")
                course_name = cmap[s.course_id].name if s.course_id in cmap else "—"
                st.write(f"**Course:** {course_name}  |  **Admission Date:** {s.admission_date}")

                fee = next((f for f in st.session_state.fees if f["Student ID"] == s.student_id), None)
                if fee:
                    st.write(
                        f"**Fee Status:** {fee_status(fee['Total Fee'], fee['Paid'])} "
                        f"(Paid ₹{fee['Paid']:,} / ₹{fee['Total Fee']:,}, "
                        f"Pending ₹{pending_fee(fee):,})"
                    )

                recs = [a for a in st.session_state.student_attendance if a["Student ID"] == s.student_id]
                if recs:
                    present = sum(1 for r in recs if r["Status"] == "Present")
                    pct = present / len(recs) * 100
                    st.markdown(f"**Attendance:** {status_badge(pct)}", unsafe_allow_html=True)

# ============================================================
# 5. STUDENT ATTENDANCE
# ============================================================
elif page == "📅 Student Attendance":
    sos_logo()
    page_header("Student Attendance")

    tab1, tab2, tab3 = st.tabs(["✅ Mark Attendance", "📜 History / Edit", "📊 Summary & Reports"])

    with tab1:
        if not st.session_state.courses:
            st.info("No courses available yet.")
        else:
            c1, c2 = st.columns(2)
            course_choice = c1.selectbox("Select Course", [f"{c.course_id} — {c.name}" for c in st.session_state.courses])
            att_date = c2.date_input("Select Date", dt.date.today(), key="s_att_date")
            cid = course_choice.split(" — ")[0]
            roster = [s for s in st.session_state.students if s.course_id == cid]

            if not roster:
                st.warning("No students enrolled in this course.")
            else:
                st.write(f"**{len(roster)} student(s) enrolled** — mark status for {att_date}")
                with st.form("mark_student_att"):
                    statuses = {}
                    for s in roster:
                        existing = next((a for a in st.session_state.student_attendance
                                          if a["Student ID"] == s.student_id and a["Date"] == att_date), None)
                        default = existing["Status"] if existing else "Present"
                        statuses[s.student_id] = st.radio(
                            f"{s.name} ({s.student_id})", ["Present", "Absent", "Leave"],
                            index=["Present", "Absent", "Leave"].index(default),
                            horizontal=True, key=f"satt_{s.student_id}_{att_date}",
                        )
                    save = st.form_submit_button("💾 Save Attendance")
                    if save:
                        for sid_, status in statuses.items():
                            existing = next((a for a in st.session_state.student_attendance
                                              if a["Student ID"] == sid_ and a["Date"] == att_date and a["Course ID"] == cid), None)
                            if existing:
                                existing["Status"] = status
                            else:
                                st.session_state.student_attendance.append({
                                    "Student ID": sid_, "Course ID": cid, "Date": att_date, "Status": status,
                                })
                        log_activity(f"Attendance saved for {len(roster)} students in {course_map()[cid].name} on {att_date}.")
                        st.success("Attendance saved successfully.")
                        st.rerun()

    with tab2:
        if not st.session_state.student_attendance:
            st.info("No attendance records yet.")
        else:
            smap, cmap = student_map(), course_map()
            df = pd.DataFrame(st.session_state.student_attendance)
            df["Student Name"] = df["Student ID"].map(lambda x: smap[x].name if x in smap else x)
            df["Course"] = df["Course ID"].map(lambda x: cmap[x].name if x in cmap else x)
            st.dataframe(df[["Date", "Student ID", "Student Name", "Course", "Status"]]
                         .sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

    with tab3:
        smap = student_map()
        if not st.session_state.student_attendance:
            st.info("No attendance data to summarize.")
        else:
            df = pd.DataFrame(st.session_state.student_attendance)
            summary = df.groupby("Student ID")["Status"].value_counts().unstack(fill_value=0)
            for col in ["Present", "Absent", "Leave"]:
                if col not in summary.columns:
                    summary[col] = 0
            summary["Total Classes"] = summary[["Present", "Absent", "Leave"]].sum(axis=1)
            summary["Attendance %"] = (summary["Present"] / summary["Total Classes"] * 100).round(1)
            summary["Student Name"] = summary.index.map(lambda x: smap[x].name if x in smap else x)
            summary = summary.reset_index()[["Student ID", "Student Name", "Total Classes", "Present", "Absent", "Leave", "Attendance %"]]
            st.dataframe(summary, use_container_width=True, hide_index=True)
            st.markdown("#### 📈 Attendance % by Student")
            st.bar_chart(summary.set_index("Student Name")["Attendance %"])

# ============================================================
# 6. EMPLOYEES
# ============================================================
elif page == "👨‍🏫 Employees":
    sos_logo()
    page_header("Employee Management")

    tab1, tab2, tab3 = st.tabs(["📋 All Employees", "➕ Add Employee", "🔍 Search / Profile"])

    with tab1:
        rows = [{
            "Employee ID": e.employee_id, "Name": e.name, "Email": e.email, "Phone": e.phone,
            "Department": e.department, "Designation": e.designation,
            "Type": e.emp_type, "Joining Date": e.joining_date,
        } for e in st.session_state.employees]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No employees yet. Add one from the 'Add Employee' tab.")

    with tab2:
        with st.form("add_employee", clear_on_submit=True):
            c1, c2 = st.columns(2)
            eid = c1.text_input("Employee ID (e.g. E007)")
            name = c2.text_input("Full Name")
            email = c1.text_input("Email")
            phone = c2.text_input("Phone Number")
            department = c1.selectbox("Department", st.session_state.institution.departments + ["Administration"])
            designation = c2.selectbox("Designation", ["Faculty", "Trainer", "HR Staff", "Administrative Staff", "Technical Staff"])
            specialization = c1.text_input("Specialization")
            joining_date = c2.date_input("Joining Date", dt.date.today())
            emp_type = c1.selectbox("Employment Type", ["Full-Time", "Part-Time", "Contract"])
            course_choice = c2.selectbox("Assigned Course (optional)", ["None"] + [f"{c.course_id} — {c.name}" for c in st.session_state.courses])
            add = st.form_submit_button("➕ Add Employee")
            if add:
                ids = {e.employee_id for e in st.session_state.employees}
                eid = eid.strip()
                name = name.strip()
                cid = "" if course_choice == "None" else course_choice.split(" — ")[0]
                if not eid or not name:
                    st.error("Employee ID and Name are required.")
                elif eid in ids:
                    st.error(f"Employee ID '{eid}' already exists.")
                elif not valid_email(email):
                    st.error("Please enter a valid email address.")
                else:
                    st.session_state.employees.append(Employee(eid, name, email, phone, department, designation,
                                                                 specialization, joining_date, emp_type, cid))
                    log_activity(f"Employee '{name}' ({eid}) added to {department}.")
                    st.success(f"Employee '{name}' added successfully.")
                    st.rerun()

    with tab3:
        query = st.text_input("Search by Employee ID or Name", key="emp_search").strip()
        cmap = course_map()

        if query:
            q = query.casefold()
            results = [
                e for e in st.session_state.employees
                if q in e.employee_id.casefold() or q in e.name.casefold()
            ]
            if not results:
                st.error(f"❌ No such employee exists with ID or Name: '{query}'.")
        else:
            results = st.session_state.employees

        for e in results:
            with st.expander(f"{e.employee_id} — {e.name}"):
                st.write(f"**Email:** {e.email}  |  **Phone:** {e.phone}")
                st.write(f"**Department:** {e.department}  |  **Designation:** {e.designation}")
                st.write(f"**Specialization:** {e.specialization}  |  **Type:** {e.emp_type}")
                st.write(f"**Joining Date:** {e.joining_date}")

                course = cmap.get(e.course_id)
                course_name = course.name if course else "—"
                st.write(f"**Assigned Course:** {course_name}")

                recs = [a for a in st.session_state.employee_attendance if a["Employee ID"] == e.employee_id]
                if recs:
                    present = sum(1 for r in recs if r["Status"] == "Present")
                    pct = present / len(recs) * 100
                    st.markdown(f"**Attendance:** {status_badge(pct)}", unsafe_allow_html=True)

# ============================================================
# 7. EMPLOYEE ATTENDANCE
# ============================================================
elif page == "👥 Employee Attendance":
    sos_logo()
    page_header("Employee Attendance")

    tab1, tab2, tab3 = st.tabs(["✅ Mark Attendance", "📜 History / Edit", "📊 Summary & Reports"])

    with tab1:
        if not st.session_state.employees:
            st.info("No employees available yet.")
        else:
            c1, c2 = st.columns(2)
            emp_choice = c1.selectbox("Select Employee", [f"{e.employee_id} — {e.name}" for e in st.session_state.employees])
            att_date = c2.date_input("Select Date", dt.date.today(), key="e_att_date")
            eid = emp_choice.split(" — ")[0]
            existing = next((a for a in st.session_state.employee_attendance
                              if a["Employee ID"] == eid and a["Date"] == att_date), None)
            default = existing["Status"] if existing else "Present"
            status = st.radio("Status", ["Present", "Absent", "Leave", "Half Day"],
                               index=["Present", "Absent", "Leave", "Half Day"].index(default),
                               horizontal=True, key=f"eatt_{eid}_{att_date}")
            if st.button("💾 Save Attendance", key="save_emp_att"):
                if existing:
                    existing["Status"] = status
                else:
                    st.session_state.employee_attendance.append({"Employee ID": eid, "Date": att_date, "Status": status})
                log_activity(f"Attendance marked '{status}' for employee {eid} on {att_date}.")
                st.success("Employee attendance saved.")
                st.rerun()

    with tab2:
        if not st.session_state.employee_attendance:
            st.info("No attendance records yet.")
        else:
            emap = employee_map()
            df = pd.DataFrame(st.session_state.employee_attendance)
            df["Employee Name"] = df["Employee ID"].map(lambda x: emap[x].name if x in emap else x)
            df["Department"] = df["Employee ID"].map(lambda x: emap[x].department if x in emap else "—")
            st.dataframe(df[["Date", "Employee ID", "Employee Name", "Department", "Status"]]
                         .sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

    with tab3:
        emap = employee_map()
        if not st.session_state.employee_attendance:
            st.info("No attendance data to summarize.")
        else:
            df = pd.DataFrame(st.session_state.employee_attendance)
            summary = df.groupby("Employee ID")["Status"].value_counts().unstack(fill_value=0)
            for col in ["Present", "Absent", "Leave", "Half Day"]:
                if col not in summary.columns:
                    summary[col] = 0
            summary["Total Working Days"] = summary[["Present", "Absent", "Leave", "Half Day"]].sum(axis=1)
            summary["Attendance %"] = (summary["Present"] / summary["Total Working Days"] * 100).round(1)
            summary["Employee Name"] = summary.index.map(lambda x: emap[x].name if x in emap else x)
            summary["Department"] = summary.index.map(lambda x: emap[x].department if x in emap else "—")
            summary = summary.reset_index()[["Employee ID", "Employee Name", "Department", "Total Working Days",
                                              "Present", "Absent", "Leave", "Half Day", "Attendance %"]]
            st.dataframe(summary, use_container_width=True, hide_index=True)
            st.markdown("#### 📈 Attendance % by Employee")
            st.bar_chart(summary.set_index("Employee Name")["Attendance %"])
            st.markdown("#### 🏢 Department-wise Average Attendance")
            dept_summary = summary.groupby("Department")["Attendance %"].mean()
            st.bar_chart(dept_summary)

# ============================================================
# 8. ENROLLMENT
# ============================================================
elif page == "📝 Enrollment":
    sos_logo()
    page_header("Enrollment Management")

    cmap = course_map()
    smap = student_map()

    tab1, tab2 = st.tabs(["📋 Enroll / Drop", "📜 Enrollment Records"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### ➕ Enroll Student")
            if not st.session_state.students or not st.session_state.courses:
                st.info("Add students and courses first.")
            else:
                sid = st.selectbox("Student", [s.student_id + " — " + s.name for s in st.session_state.students], key="enroll_sid")
                cid_choice = st.selectbox("Course", [f"{c.course_id} — {c.name}" for c in st.session_state.courses], key="enroll_cid")
                if st.button("Enroll"):
                    sid_ = sid.split(" — ")[0]
                    cid_ = cid_choice.split(" — ")[0]
                    already = any(en["Student ID"] == sid_ and en["Course ID"] == cid_ for en in st.session_state.enrollments)
                    course = cmap[cid_]
                    if already:
                        st.error("Student is already enrolled in this course.")
                    elif enrolled_count(cid_) >= course.capacity:
                        st.error(f"Course '{course.name}' is full. Cannot enroll.")
                    else:
                        st.session_state.enrollments.append({"Student ID": sid_, "Course ID": cid_, "Enrolled On": dt.date.today()})
                        smap[sid_].course_id = cid_
                        log_activity(f"Student {sid_} enrolled into {course.name}.")
                        st.success("Student enrolled successfully.")
                        st.rerun()
        with c2:
            st.markdown("##### ➖ Drop Student")
            if st.session_state.enrollments:
                options = [f"{en['Student ID']} — {cmap[en['Course ID']].name if en['Course ID'] in cmap else en['Course ID']}"
                           for en in st.session_state.enrollments]
                drop_idx = st.selectbox(
                    "Select Enrollment", range(len(options)),
                    format_func=lambda i: options[i], key="drop_choice",
                )
                if st.button("Drop"):
                    removed = st.session_state.enrollments.pop(drop_idx)
                    log_activity(f"Student {removed['Student ID']} dropped from course {removed['Course ID']}.")
                    st.success("Enrollment removed.")
                    st.rerun()
            else:
                st.info("No enrollments to drop.")

    with tab2:
        rows = [{
            "Student ID": en["Student ID"],
            "Student Name": smap[en["Student ID"]].name if en["Student ID"] in smap else "—",
            "Course": cmap[en["Course ID"]].name if en["Course ID"] in cmap else en["Course ID"],
            "Enrolled On": en["Enrolled On"],
        } for en in st.session_state.enrollments]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown("#### 📊 Seats Overview")
            seat_df = pd.DataFrame([{
                "Course": c.name, "Enrolled": enrolled_count(c.course_id),
                "Available": max(c.capacity - enrolled_count(c.course_id), 0),
            } for c in st.session_state.courses]).set_index("Course")
            st.bar_chart(seat_df)
        else:
            st.info("No enrollments yet.")

# ============================================================
# 9. FEES
# ============================================================
elif page == "💰 Fees":
    sos_logo()
    page_header("Fees Management")

    smap = student_map()
    tab1, tab2 = st.tabs(["📋 Fee Records", "💳 Record Payment"])

    with tab1:
        rows = []
        for f in st.session_state.fees:
            rows.append({
                "Student ID": f["Student ID"],
                "Student Name": smap[f["Student ID"]].name if f["Student ID"] in smap else "—",
                "Total Fee (₹)": f["Total Fee"], "Paid (₹)": f["Paid"], "Pending (₹)": pending_fee(f),
                "Status": fee_status(f["Total Fee"], f["Paid"]),
            })
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            c1, c2, c3 = st.columns(3)
            kpi(c1, "Total Collected", f"₹{df['Paid (₹)'].sum():,}")
            kpi(c2, "Total Pending", f"₹{df['Pending (₹)'].sum():,}")
            kpi(c3, "Fully Paid Students", int((df["Status"] == "Paid").sum()))
        else:
            st.info("No fee records yet.")

    with tab2:
        options = [f["Student ID"] for f in st.session_state.fees]
        if not options:
            st.info("No fee records to update yet.")
        else:
            sid = st.selectbox(
                "Select Student", options, key="fee_payment_student",
                format_func=lambda x: f"{x} — {smap[x].name if x in smap else x}",
            )
            record = next(f for f in st.session_state.fees if f["Student ID"] == sid)
            pending = pending_fee(record)
            st.write(
                f"**Total Fee:** ₹{record['Total Fee']:,}  |  **Paid so far:** ₹{record['Paid']:,}  |  "
                f"**Pending:** ₹{pending:,}"
            )

            if pending <= 0:
                st.success("This student's fee is fully paid. No further payment needed.")
            else:
                with st.form("record_payment_form", clear_on_submit=True):
                    amount = st.number_input(
                        "Payment Amount (₹)", min_value=0, max_value=pending, step=500,
                    )
                    submitted = st.form_submit_button("💳 Record Payment")
                    if submitted:
                        try:
                            record_payment(record, amount)
                        except ValueError as exc:
                            st.error(str(exc))
                        else:
                            log_activity(f"Payment of ₹{amount:,.0f} recorded for student {sid}.")
                            st.success(
                                f"Payment of ₹{amount:,.0f} recorded. "
                                f"New status: {fee_status(record['Total Fee'], record['Paid'])}"
                            )
                            st.rerun()

# ============================================================
# 10. REPORTS
# ============================================================
elif page == "📊 Reports":
    sos_logo()
    page_header("Reports & Analytics")

    cmap, smap, emap = course_map(), student_map(), employee_map()

    report_type = st.selectbox("Select Report", [
        "Student Report", "Employee Report", "Course Report",
        "Student Attendance Report", "Employee Attendance Report",
        "Enrollment Report", "Fee Report",
    ])

    if report_type == "Student Report":
        if not st.session_state.students:
            st.info("No student data available.")
        else:
            course_filter = st.selectbox("Filter by Course", ["All"] + [c.name for c in st.session_state.courses])
            rows = [{"ID": s.student_id, "Name": s.name, "Course": cmap[s.course_id].name if s.course_id in cmap else "—",
                     "Status": s.status, "Admission Date": s.admission_date} for s in st.session_state.students]
            df = pd.DataFrame(rows)
            if course_filter != "All":
                df = df[df["Course"] == course_filter]
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif report_type == "Employee Report":
        if not st.session_state.employees:
            st.info("No employee data available.")
        else:
            dept_filter = st.selectbox("Filter by Department", ["All"] + st.session_state.institution.departments + ["Administration"])
            rows = [{"ID": e.employee_id, "Name": e.name, "Department": e.department,
                     "Designation": e.designation, "Type": e.emp_type} for e in st.session_state.employees]
            df = pd.DataFrame(rows)
            if dept_filter != "All":
                df = df[df["Department"] == dept_filter]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown("#### 🏢 Department-wise Employee Count")
            st.bar_chart(df["Department"].value_counts() if dept_filter == "All" else pd.Series({dept_filter: len(df)}))

    elif report_type == "Course Report":
        if not st.session_state.courses:
            st.info("No course data available.")
        else:
            rows = [c.to_dict(enrolled_count(c.course_id)) for c in st.session_state.courses]
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown("#### 🎓 Course-wise Students")
            st.bar_chart(df.set_index("Course Name")["Enrolled"])

    elif report_type == "Student Attendance Report":
        if not st.session_state.student_attendance:
            st.info("No attendance data available.")
        else:
            df = pd.DataFrame(st.session_state.student_attendance)
            course_filter = st.selectbox("Filter by Course", ["All"] + [c.name for c in st.session_state.courses], key="sar_course")
            df["Course"] = df["Course ID"].map(lambda x: cmap[x].name if x in cmap else x)
            df["Student Name"] = df["Student ID"].map(lambda x: smap[x].name if x in smap else x)
            if course_filter != "All":
                df = df[df["Course"] == course_filter]
            st.dataframe(df[["Date", "Student ID", "Student Name", "Course", "Status"]], use_container_width=True, hide_index=True)
            st.markdown("#### 📈 Status Distribution")
            st.bar_chart(df["Status"].value_counts())

    elif report_type == "Employee Attendance Report":
        if not st.session_state.employee_attendance:
            st.info("No attendance data available.")
        else:
            df = pd.DataFrame(st.session_state.employee_attendance)
            df["Employee Name"] = df["Employee ID"].map(lambda x: emap[x].name if x in emap else x)
            df["Department"] = df["Employee ID"].map(lambda x: emap[x].department if x in emap else "—")
            dept_filter = st.selectbox("Filter by Department", ["All"] + st.session_state.institution.departments + ["Administration"], key="ear_dept")
            if dept_filter != "All":
                df = df[df["Department"] == dept_filter]
            st.dataframe(df[["Date", "Employee ID", "Employee Name", "Department", "Status"]], use_container_width=True, hide_index=True)
            st.markdown("#### 📈 Status Distribution")
            st.bar_chart(df["Status"].value_counts())

    elif report_type == "Enrollment Report":
        if not st.session_state.enrollments:
            st.info("No enrollment data available.")
        else:
            rows = [{"Student ID": en["Student ID"], "Student Name": smap[en["Student ID"]].name if en["Student ID"] in smap else "—",
                     "Course": cmap[en["Course ID"]].name if en["Course ID"] in cmap else en["Course ID"],
                     "Enrolled On": en["Enrolled On"]} for en in st.session_state.enrollments]
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown("#### 📊 Enrollment by Course")
            st.bar_chart(df["Course"].value_counts())

    elif report_type == "Fee Report":
        if not st.session_state.fees:
            st.info("No fee data available.")
        else:
            rows = []
            for f in st.session_state.fees:
                rows.append({"Student ID": f["Student ID"], "Student Name": smap[f["Student ID"]].name if f["Student ID"] in smap else "—",
                             "Total Fee": f["Total Fee"], "Paid": f["Paid"], "Pending": pending_fee(f),
                             "Status": fee_status(f["Total Fee"], f["Paid"])})
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown("#### 💰 Payment Status Distribution")
            st.bar_chart(df["Status"].value_counts())

# ============================================================
# 11. ADMINISTRATION
# ============================================================
elif page == "⚙️ Administration":
    sos_logo()
    page_header("Administration", "System settings and data management")

    st.markdown("#### 🎨 Branding")
    st.write(f"Institution: **{st.session_state.institution.name}**")
    st.color_picker("Primary Brand Color", RED, disabled=True)

    st.markdown("---")
    st.markdown("#### 🗂️ Data Overview")
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Students", len(st.session_state.students))
    kpi(c2, "Employees", len(st.session_state.employees))
    kpi(c3, "Courses", len(st.session_state.courses))
    kpi(c4, "Attendance Records", len(st.session_state.student_attendance) + len(st.session_state.employee_attendance))

    st.markdown("---")
    st.markdown("#### 🔄 Reset Portal Data")
    st.warning("This will erase all changes made in this session and restore sample data.")
    if st.button("♻️ Reset to Sample Data"):
        for key in ["initialized", "institution", "courses", "students", "employees",
                    "enrollments", "student_attendance", "employee_attendance", "fees",
                    "activity_log", "current_page"]:
            st.session_state.pop(key, None)
        init_state()
        st.success("Portal data has been reset.")
        st.rerun()
