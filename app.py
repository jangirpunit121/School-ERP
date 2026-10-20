"""
🏫 Scholaris Pro — School ERP (Professional UI + Editable + Class Teacher)
Run: streamlit run app.py
Login: admin / Admin@123
"""
import os
import uuid
import sqlite3
import hashlib
import secrets
import shutil
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

# ═══════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════
APP_NAME = "Scholaris Pro"
APP_TAGLINE = "School Management ERP"
APP_VERSION = "3.2.0"
SCHOOL_NAME = "Sunrise Public School"
SCHOOL_ADDRESS = "123 Education Lane, Knowledge City - 400001"
SCHOOL_PHONE = "+91 98765 43210"
SCHOOL_EMAIL = "office@sunriseschool.edu"

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "school.db"
BACKUP_DIR = BASE_DIR / "backups"
UPLOAD_DIR = BASE_DIR / "uploads"
PAPERS_DIR = UPLOAD_DIR / "papers"
for d in (BACKUP_DIR, PAPERS_DIR):
    d.mkdir(parents=True, exist_ok=True)

ROLE_MENUS = {
    "admin": [
        ("Dashboard", "📊"), ("Teachers", "👩‍🏫"), ("Students", "👨‍🎓"),
        ("Classes", "🏫"), ("Subjects", "📚"), ("Attendance", "📅"),
        ("Examinations", "📝"), ("Fee Collection", "💰"),
        ("Papers & Material", "📄"), ("Announcements", "📢"),
        ("Audit Log", "🧾"), ("Settings", "⚙️"),
    ],
    "teacher": [
        ("Dashboard", "📊"), ("My Students", "👨‍🎓"),
        ("Attendance", "📅"), ("Examinations", "📝"),
        ("Papers & Material", "📄"), ("Timetable", "🗓️"),
        ("Announcements", "📢"),
    ],
    "student": [
        ("Dashboard", "📊"), ("My Marks", "📝"),
        ("Fees & Receipts", "💰"), ("Study Material", "📄"),
        ("Announcements", "📢"),
    ],
}

GRADES = [(90, "A+", "#16a34a"), (80, "A", "#22c55e"), (70, "B", "#84cc16"),
          (60, "C", "#eab308"), (50, "D", "#f97316"), (0, "F", "#ef4444")]
EXAMS = ("Unit Test 1", "Mid Term", "Unit Test 2", "Final")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
PERIODS = tuple(range(1, 9))
FEE_MONTHS = ["April", "May", "June", "July", "August", "September",
              "October", "November", "December", "January", "February", "March"]

# ═══════════════════════════════════════════════════════════════════
#  PAGE SETUP + CSS
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
    color: #1e293b !important;
}
.stApp { background: #f8fafc !important; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1500px !important; }

h1, h2, h3, h4, h5 { color: #0f172a !important; font-weight: 700 !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }

[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: 0.55rem 0.85rem !important;
    border-radius: 8px !important;
    margin: 1px 0 !important;
    border-left: 3px solid transparent;
    transition: all 0.15s ease;
    cursor: pointer;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(56, 189, 248, 0.15) !important;
    border-left-color: #38bdf8 !important;
    color: #f1f5f9 !important;
}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
    background: rgba(56, 189, 248, 0.22) !important;
    border-left-color: #38bdf8 !important;
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}

.pg-head {
    background: #ffffff !important;
    border-left: 5px solid #0ea5e9;
    padding: 1.2rem 1.5rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.pg-head h1 { margin: 0; font-size: 1.55rem !important; color: #0f172a !important; }
.pg-head p { margin: 0.35rem 0 0; color: #64748b !important; font-size: 0.9rem; }
.crumb { font-size: 0.8rem; color: #94a3b8 !important; margin-bottom: 0.7rem; }

.kpi-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    display: flex; align-items: center; gap: 1rem;
    transition: all 0.2s;
    min-height: 88px;
}
.kpi-card:hover {
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
    transform: translateY(-2px);
    border-color: #cbd5e1;
}
.kpi-icon {
    width: 50px; height: 50px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; flex-shrink: 0;
}
.kpi-label {
    font-size: 0.78rem; color: #64748b !important;
    font-weight: 500; text-transform: uppercase; letter-spacing: 0.03em;
}
.kpi-value {
    font-size: 1.6rem; font-weight: 800;
    color: #0f172a !important; line-height: 1.1; margin-top: 0.1rem;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div > div {
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #0f172a !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 0.75rem !important;
    transition: all 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus,
.stSelectbox > div > div > div:focus-within {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15) !important;
    outline: none !important;
}

.stTextInput label, .stNumberInput label, .stDateInput label,
.stTextArea label, .stSelectbox label, .stFileUploader label,
.stRadio label, .stCheckbox label {
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    margin-bottom: 0.25rem !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

[data-baseweb="select"] > div {
    background: #ffffff !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
}
[data-baseweb="popover"] { background: #ffffff !important; }
[data-baseweb="popover"] li { color: #0f172a !important; font-size: 0.9rem !important; }
[data-baseweb="popover"] li:hover { background: #f1f5f9 !important; }

.stNumberInput button {
    background: #f1f5f9 !important;
    color: #475569 !important;
    border: 1px solid #cbd5e1 !important;
}

.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: 1.5px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #0f172a !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s !important;
    font-size: 0.9rem !important;
}
.stButton > button:hover {
    background: #f1f5f9 !important;
    border-color: #0ea5e9 !important;
    color: #0ea5e9 !important;
}
.stButton > button[kind="primary"] {
    background: #0ea5e9 !important;
    color: #ffffff !important;
    border: 1.5px solid #0ea5e9 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #0284c7 !important;
    border-color: #0284c7 !important;
    color: #ffffff !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: transparent;
    border-bottom: 2px solid #e2e8f0; padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    color: #64748b !important;
    border-radius: 8px 8px 0 0 !important;
    border: none !important;
    font-size: 0.92rem !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0ea5e9 !important;
    background: #f1f5f9 !important;
}
.stTabs [aria-selected="true"] {
    background: #0ea5e9 !important;
    color: #ffffff !important;
    border-bottom: 3px solid #0284c7 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    background: #ffffff !important;
}

details {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 0.3rem 0.8rem !important;
    margin-bottom: 0.8rem !important;
}
details summary {
    font-weight: 600 !important;
    color: #0f172a !important;
    padding: 0.4rem 0 !important;
}
details[open] { padding-bottom: 0.8rem !important; }

[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}

.pill {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 0.1rem;
}
.pill-green  { background: #dcfce7; color: #166534; }
.pill-red    { background: #fee2e2; color: #991b1b; }
.pill-yellow { background: #fef3c7; color: #92400e; }
.pill-blue   { background: #dbeafe; color: #1e40af; }
.pill-gray   { background: #f1f5f9; color: #475569; }

.empty {
    background: #ffffff;
    border: 2px dashed #cbd5e1;
    border-radius: 12px;
    padding: 2.5rem 1.5rem;
    text-align: center;
    color: #64748b;
    margin: 1rem 0;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.empty h3 { margin: 0.3rem 0; color: #0f172a !important; font-size: 1.1rem !important; }
.empty p { margin: 0.5rem 0 0; font-size: 0.9rem; }

.stForm {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 1.3rem !important;
}

.stFileUploader {
    background: #f8fafc !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

.receipt {
    background: #ffffff !important;
    border: 1.5px solid #0f172a;
    border-radius: 10px;
    padding: 1.8rem;
    color: #0f172a !important;
    max-width: 720px;
    margin: 1rem 0;
}
.receipt h2 { color: #0f172a !important; margin: 0 0 0.2rem !important; }
.receipt hr { border: none; border-top: 2px solid #0f172a; margin: 0.8rem 0; }
.receipt table { width: 100%; border-collapse: collapse; }
.receipt td { padding: 0.55rem 0.4rem; border-bottom: 1px dashed #cbd5e1; }
.receipt .total { font-size: 1.35rem; font-weight: 800; color: #0f172a; }
.sign-line {
    margin-top: 2rem;
    border-top: 1px solid #64748b;
    padding-top: 0.4rem;
    display: inline-block;
    color: #64748b;
    font-size: 0.8rem;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════════════════
def get_conn():
    c = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def _df(sql, params=()):
    with get_conn() as c:
        return pd.read_sql_query(sql, c, params=params)


def _exec(sql, params=()):
    with get_conn() as c:
        return c.execute(sql, params).lastrowid


def init_schema():
    with get_conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            linked_id INTEGER,
            full_name TEXT NOT NULL,
            email TEXT, phone TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT
        );
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            section TEXT NOT NULL DEFAULT '',
            capacity INTEGER DEFAULT 40,
            teacher_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, section)
        );
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            qualification TEXT,
            join_date TEXT,
            status TEXT DEFAULT 'Active'
        );
        CREATE TABLE IF NOT EXISTS teacher_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_no TEXT UNIQUE,
            name TEXT NOT NULL,
            roll_no TEXT,
            class_id INTEGER,
            gender TEXT,
            dob TEXT,
            blood_group TEXT,
            guardian_name TEXT,
            guardian_phone TEXT,
            guardian_email TEXT,
            address TEXT,
            admission_date TEXT,
            status TEXT DEFAULT 'Active',
            UNIQUE(roll_no, class_id),
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT UNIQUE,
            max_marks INTEGER DEFAULT 100
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            class_id INTEGER,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            marked_by INTEGER,
            UNIQUE(student_id, date),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            exam TEXT NOT NULL,
            max_marks REAL DEFAULT 100,
            obtained REAL NOT NULL,
            exam_date TEXT,
            entered_by INTEGER,
            UNIQUE(student_id, subject_id, exam),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS fee_structure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            UNIQUE(class_id, month),
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS fee_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_no TEXT UNIQUE NOT NULL,
            student_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            month TEXT,
            method TEXT,
            paid_date TEXT,
            note TEXT,
            collected_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            class_id INTEGER,
            subject_id INTEGER,
            paper_type TEXT DEFAULT 'Question Paper',
            file_path TEXT NOT NULL,
            original_name TEXT,
            file_size INTEGER,
            uploaded_by INTEGER,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            priority TEXT DEFAULT 'Normal',
            audience TEXT DEFAULT 'All',
            posted_by TEXT,
            posted_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            day TEXT,
            period INTEGER,
            subject_id INTEGER,
            teacher_id INTEGER,
            UNIQUE(class_id, day, period)
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            username TEXT,
            action TEXT,
            entity TEXT,
            entity_id INTEGER,
            detail TEXT
        );
        """)


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${h}"


def verify_pw(pw, stored):
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return hash_pw(pw, salt) == stored


def create_user(username, password, role, full_name, linked_id=None,
                email=None, phone=None):
    try:
        return _exec(
            """INSERT INTO users (username, password_hash, role, linked_id,
               full_name, email, phone) VALUES (?,?,?,?,?,?,?)""",
            (username.strip(), hash_pw(password), role, linked_id,
             full_name.strip(), email, phone))
    except Exception:
        return None


def authenticate(username, password):
    with get_conn() as c:
        r = c.execute("SELECT * FROM users WHERE username=? AND is_active=1",
                      (username.strip(),)).fetchone()
    if not r or not verify_pw(password, r["password_hash"]):
        return None
    with get_conn() as c:
        c.execute("UPDATE users SET last_login=? WHERE id=?",
                  (datetime.now().isoformat(), r["id"]))
    return dict(r)


def log_action(user, action, entity, eid=None, detail=""):
    if not user:
        return
    _exec("INSERT INTO audit_log (user_id, username, action, entity, entity_id, detail) "
          "VALUES (?,?,?,?,?,?)",
          (user["id"], user["username"], action, entity, eid, detail))


def _column_exists(table, column):
    with get_conn() as c:
        rows = c.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == column for r in rows)


def migrate_db():
    try:
        upgrades = {
            "users": [("is_active", "INTEGER DEFAULT 1"),
                      ("linked_id", "INTEGER"),
                      ("email", "TEXT"), ("phone", "TEXT"),
                      ("last_login", "TEXT")],
            "students": [("admission_no", "TEXT"),
                         ("blood_group", "TEXT"),
                         ("guardian_email", "TEXT"),
                         ("status", "TEXT DEFAULT 'Active'")],
            "teachers": [("employee_id", "TEXT"),
                         ("qualification", "TEXT"),
                         ("status", "TEXT DEFAULT 'Active'")],
            "classes": [("capacity", "INTEGER DEFAULT 40"),
                        ("teacher_id", "INTEGER")],
            "attendance": [("class_id", "INTEGER")],
            "marks": [("entered_by", "INTEGER")],
            "papers": [("file_size", "INTEGER")],
        }
        for table, cols in upgrades.items():
            with get_conn() as c:
                exists = c.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table,)).fetchone()
            if not exists:
                continue
            for col, dtype in cols:
                if not _column_exists(table, col):
                    with get_conn() as c:
                        c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
    except Exception as e:
        print(f"Migration warning: {e}")


init_schema()
migrate_db()

with get_conn() as _c:
    if not _c.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        create_user("admin", "Admin@123", "admin", "System Administrator")


# ═══════════════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════════════
def page_header(title, subtitle="", icon="", crumbs=None):
    if crumbs:
        st.markdown(f'<div class="crumb">{" › ".join(crumbs)}</div>',
                    unsafe_allow_html=True)
    st.markdown(
        f'<div class="pg-head"><h1>{icon} {title}</h1>'
        f'<p>{subtitle}</p></div>', unsafe_allow_html=True)


def kpi(label, value, icon="", bg="#dbeafe"):
    st.markdown(
        f'''<div class="kpi-card">
            <div class="kpi-icon" style="background:{bg}">{icon}</div>
            <div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
        </div>''', unsafe_allow_html=True)


def pill(text, kind="blue"):
    return f'<span class="pill pill-{kind}">{text}</span>'


def status_pill(s):
    m = {"Present": "green", "Paid": "green", "Active": "green",
         "Absent": "red", "Inactive": "red",
         "Late": "yellow", "Pending": "yellow", "Partial": "yellow",
         "Leave": "blue",
         "Urgent": "red", "Important": "yellow", "Normal": "blue"}
    return pill(s, m.get(s, "gray"))


def empty_state(icon, title, hint=""):
    st.markdown(
        f'<div class="empty"><div class="empty-icon">{icon}</div>'
        f'<h3>{title}</h3><p>{hint}</p></div>',
        unsafe_allow_html=True)


def download_csv(df, filename):
    st.download_button("⬇️  Export CSV",
                       df.to_csv(index=False).encode(),
                       f"{filename}.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════
#  SERVICES
# ═══════════════════════════════════════════════════════════════════
def list_teachers(search=""):
    sql = "SELECT * FROM teachers WHERE 1=1"
    p = []
    if search:
        sql += " AND (name LIKE ? OR email LIKE ? OR employee_id LIKE ?)"
        p += [f"%{search}%"] * 3
    sql += " ORDER BY id DESC"
    return _df(sql, tuple(p))


def get_teacher(tid):
    with get_conn() as c:
        r = c.execute("SELECT * FROM teachers WHERE id=?", (tid,)).fetchone()
    return dict(r) if r else None


def add_teacher(data):
    return _exec(
        """INSERT INTO teachers (employee_id, name, email, phone,
           qualification, join_date, status) VALUES (?,?,?,?,?,?,?)""",
        (data.get("employee_id") or None, data["name"],
         data.get("email") or None, data.get("phone"),
         data.get("qualification"), data.get("join_date"), "Active"))


def update_teacher(tid, data):
    _exec("""UPDATE teachers SET employee_id=?, name=?, email=?, phone=?,
             qualification=?, status=? WHERE id=?""",
          (data.get("employee_id") or None, data["name"],
           data.get("email") or None, data.get("phone"),
           data.get("qualification"), data.get("status", "Active"), tid))


def delete_teacher(tid):
    _exec("DELETE FROM teachers WHERE id=?", (tid,))


def assign_teacher_subject(teacher_id, subject_id, class_id):
    try:
        _exec("INSERT INTO teacher_subjects (teacher_id, subject_id, class_id) "
              "VALUES (?,?,?)", (teacher_id, subject_id, class_id))
        return True
    except Exception:
        return False


def teacher_assignments(teacher_id):
    return _df("""
        SELECT ts.id, sub.name AS subject, c.name || COALESCE(' - ' || c.section,'') AS class,
               ts.subject_id, ts.class_id
        FROM teacher_subjects ts
        JOIN subjects sub ON ts.subject_id = sub.id
        JOIN classes c ON ts.class_id = c.id
        WHERE ts.teacher_id=?
        ORDER BY c.name, sub.name
    """, (teacher_id,))


def remove_assignment(aid):
    _exec("DELETE FROM teacher_subjects WHERE id=?", (aid,))


def list_students(search="", class_id=None, status="All"):
    sql = """
        SELECT s.id, s.admission_no, s.name, s.roll_no,
               c.name || CASE WHEN c.section!='' THEN ' - '||c.section ELSE '' END AS class,
               s.class_id, s.gender, s.status, s.guardian_name, s.guardian_phone
        FROM students s LEFT JOIN classes c ON s.class_id=c.id WHERE 1=1
    """
    p = []
    if search:
        sql += " AND (s.name LIKE ? OR s.roll_no LIKE ? OR s.admission_no LIKE ?)"
        p += [f"%{search}%"] * 3
    if class_id:
        sql += " AND s.class_id=?"; p.append(class_id)
    if status != "All":
        sql += " AND s.status=?"; p.append(status)
    sql += " ORDER BY s.id DESC"
    return _df(sql, tuple(p))


def get_student(sid):
    with get_conn() as c:
        r = c.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    return dict(r) if r else None


def add_student(data):
    return _exec(
        """INSERT INTO students (admission_no, name, roll_no, class_id, gender,
           dob, blood_group, guardian_name, guardian_phone, guardian_email,
           address, admission_date, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data.get("admission_no") or None, data["name"],
         data.get("roll_no"), data.get("class_id"), data.get("gender"),
         data.get("dob"), data.get("blood_group"), data.get("guardian_name"),
         data.get("guardian_phone"), data.get("guardian_email"),
         data.get("address"), data.get("admission_date", date.today().isoformat()),
         "Active"))


def update_student(sid, data):
    _exec("""UPDATE students SET admission_no=?, name=?, roll_no=?, class_id=?,
             gender=?, dob=?, blood_group=?, guardian_name=?, guardian_phone=?,
             guardian_email=?, address=?, status=? WHERE id=?""",
          (data.get("admission_no") or None, data["name"],
           data.get("roll_no"), data.get("class_id"), data.get("gender"),
           data.get("dob"), data.get("blood_group"), data.get("guardian_name"),
           data.get("guardian_phone"), data.get("guardian_email"),
           data.get("address"), data.get("status", "Active"), sid))


def delete_student(sid):
    _exec("DELETE FROM students WHERE id=?", (sid,))


def list_classes():
    return _df("""SELECT c.id, c.name, c.section, c.capacity,
        c.teacher_id, t.name AS class_teacher,
        (SELECT COUNT(*) FROM students s WHERE s.class_id=c.id AND s.status='Active') AS students
        FROM classes c
        LEFT JOIN teachers t ON c.teacher_id = t.id
        ORDER BY c.name, c.section""")


def add_class(name, section, capacity=40, teacher_id=None):
    return _exec(
        "INSERT INTO classes (name, section, capacity, teacher_id) VALUES (?,?,?,?)",
        (name, section or "", capacity, teacher_id))


def update_class(cid, name, section, capacity, teacher_id=None):
    _exec("UPDATE classes SET name=?, section=?, capacity=?, teacher_id=? WHERE id=?",
          (name, section or "", capacity, teacher_id, cid))


def delete_class(cid):
    _exec("DELETE FROM classes WHERE id=?", (cid,))


def list_subjects():
    return _df("SELECT * FROM subjects ORDER BY name")


def add_subject(name, code, max_marks=100):
    return _exec("INSERT INTO subjects (name, code, max_marks) VALUES (?,?,?)",
                 (name, code or None, max_marks))


def update_subject(sid, name, code, max_marks):
    _exec("UPDATE subjects SET name=?, code=?, max_marks=? WHERE id=?",
          (name, code or None, max_marks, sid))


def delete_subject(sid):
    _exec("DELETE FROM subjects WHERE id=?", (sid,))


def students_in_class(class_id):
    return _df("SELECT id, name, roll_no FROM students WHERE class_id=? AND status='Active' "
               "ORDER BY roll_no", (class_id,))


def get_attendance(class_id, day):
    return _df("""SELECT s.id, s.name, s.roll_no, a.status
        FROM students s LEFT JOIN attendance a ON a.student_id=s.id AND a.date=?
        WHERE s.class_id=? AND s.status='Active' ORDER BY s.roll_no""",
               (day, class_id))


def save_attendance(sid, class_id, day, status, marked_by):
    _exec("""INSERT INTO attendance (student_id, class_id, date, status, marked_by)
             VALUES (?,?,?,?,?)
             ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status,
                marked_by=excluded.marked_by""",
          (sid, class_id, day, status, marked_by))


def attendance_summary(class_id):
    return _df("""SELECT s.name, s.roll_no,
        SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) present,
        SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) absent,
        SUM(CASE WHEN a.status='Late' THEN 1 ELSE 0 END) late,
        SUM(CASE WHEN a.status='Leave' THEN 1 ELSE 0 END) leave,
        COUNT(a.id) total
        FROM students s LEFT JOIN attendance a ON a.student_id=s.id
        WHERE s.class_id=? GROUP BY s.id ORDER BY s.roll_no""", (class_id,))


def save_marks(sid, sub_id, exam, max_m, obt, exam_date, entered_by):
    _exec("""INSERT INTO marks (student_id, subject_id, exam, max_marks, obtained,
             exam_date, entered_by) VALUES (?,?,?,?,?,?,?)
             ON CONFLICT(student_id, subject_id, exam) DO UPDATE SET
                obtained=excluded.obtained, max_marks=excluded.max_marks,
                exam_date=excluded.exam_date, entered_by=excluded.entered_by""",
          (sid, sub_id, exam, max_m, obt, exam_date, entered_by))


def student_marks(sid):
    return _df("""SELECT m.id, m.exam, sub.name AS subject, sub.code,
        m.max_marks, m.obtained, ROUND(m.obtained*100.0/m.max_marks, 1) AS pct
        FROM marks m JOIN subjects sub ON m.subject_id=sub.id
        WHERE m.student_id=? ORDER BY m.exam, sub.name""", (sid,))


def update_mark(mid, obtained, max_marks):
    _exec("UPDATE marks SET obtained=?, max_marks=? WHERE id=?",
          (obtained, max_marks, mid))


def delete_mark(mid):
    _exec("DELETE FROM marks WHERE id=?", (mid,))


def grade_for(pct):
    for t, l, c in GRADES:
        if pct >= t:
            return l, c
    return "F", "#ef4444"


def set_fee_structure(class_id, month, amount):
    _exec("""INSERT INTO fee_structure (class_id, month, amount) VALUES (?,?,?)
             ON CONFLICT(class_id, month) DO UPDATE SET amount=excluded.amount""",
          (class_id, month, amount))


def get_fee_structure(class_id):
    return _df("SELECT * FROM fee_structure WHERE class_id=? ORDER BY id", (class_id,))


def update_fee_structure(fid, amount):
    _exec("UPDATE fee_structure SET amount=? WHERE id=?", (amount, fid))


def delete_fee_structure(fid):
    _exec("DELETE FROM fee_structure WHERE id=?", (fid,))


def _next_receipt_no():
    with get_conn() as c:
        n = c.execute("SELECT COUNT(*) c FROM fee_payments").fetchone()["c"]
    return f"RCPT{date.today().strftime('%Y%m')}{n + 1:04d}"


def collect_fee(student_id, amount, month, method, paid_date, note, collected_by):
    receipt = _next_receipt_no()
    rid = _exec("""INSERT INTO fee_payments (receipt_no, student_id, amount, month,
                   method, paid_date, note, collected_by) VALUES (?,?,?,?,?,?,?,?)""",
                (receipt, student_id, amount, month, method, paid_date, note, collected_by))
    return rid, receipt


def list_fee_payments(student_id=None, search=""):
    sql = """
        SELECT f.id, f.receipt_no, f.student_id, s.name AS student,
               s.roll_no, c.name || COALESCE(' - ' || c.section,'') AS class,
               f.amount, f.month, f.method, f.paid_date, f.note, f.created_at
        FROM fee_payments f JOIN students s ON f.student_id = s.id
        LEFT JOIN classes c ON s.class_id = c.id WHERE 1=1
    """
    p = []
    if student_id:
        sql += " AND f.student_id=?"; p.append(student_id)
    if search:
        sql += " AND (s.name LIKE ? OR f.receipt_no LIKE ? OR s.roll_no LIKE ?)"
        p += [f"%{search}%"] * 3
    sql += " ORDER BY f.id DESC"
    return _df(sql, tuple(p))


def get_payment(rid):
    with get_conn() as c:
        r = c.execute("SELECT * FROM fee_payments WHERE id=?", (rid,)).fetchone()
    return dict(r) if r else None


def update_payment(pid, amount, month, method, paid_date, note):
    _exec("""UPDATE fee_payments SET amount=?, month=?, method=?, paid_date=?,
             note=? WHERE id=?""",
          (amount, month, method, paid_date, note, pid))


def delete_payment(pid):
    _exec("DELETE FROM fee_payments WHERE id=?", (pid,))


def student_fee_summary(student_id):
    student = get_student(student_id)
    if not student or not student["class_id"]:
        return dict(total_due=0, total_paid=0, balance=0, months=[])
    structure = get_fee_structure(student["class_id"])
    if structure.empty:
        return dict(total_due=0, total_paid=0, balance=0, months=[])
    paid_df = list_fee_payments(student_id=student_id)
    total_due = structure["amount"].sum()
    total_paid = paid_df["amount"].sum() if not paid_df.empty else 0
    months = []
    for _, row in structure.iterrows():
        paid = 0
        if not paid_df.empty:
            sub = paid_df[paid_df["month"] == row["month"]]
            paid = sub["amount"].sum()
        months.append({
            "month": row["month"], "amount": row["amount"],
            "paid": paid, "balance": row["amount"] - paid,
        })
    return dict(total_due=total_due, total_paid=total_paid,
                balance=total_due - total_paid, months=months)


def save_paper(title, description, class_id, subject_id, paper_type,
               uploaded_file, uploaded_by):
    ext = os.path.splitext(uploaded_file.name)[1]
    fname = f"{uuid.uuid4().hex}{ext}"
    path = PAPERS_DIR / fname
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return _exec("""INSERT INTO papers (title, description, class_id, subject_id,
                    paper_type, file_path, original_name, file_size, uploaded_by)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                 (title, description, class_id, subject_id, paper_type,
                  str(path), uploaded_file.name, uploaded_file.size, uploaded_by))


def list_papers(class_id=None, subject_id=None, search=""):
    sql = """SELECT p.id, p.title, p.description, p.paper_type,
               c.name || COALESCE(' - ' || c.section,'') AS class,
               sub.name AS subject, p.file_path, p.original_name,
               p.file_size, u.full_name AS uploaded_by_name,
               p.uploaded_at, p.class_id, p.subject_id
        FROM papers p LEFT JOIN classes c ON p.class_id=c.id
        LEFT JOIN subjects sub ON p.subject_id=sub.id
        LEFT JOIN users u ON p.uploaded_by=u.id WHERE 1=1"""
    p = []
    if class_id:
        sql += " AND p.class_id=?"; p.append(class_id)
    if subject_id:
        sql += " AND p.subject_id=?"; p.append(subject_id)
    if search:
        sql += " AND (p.title LIKE ? OR p.description LIKE ?)"
        p += [f"%{search}%"] * 2
    sql += " ORDER BY p.id DESC"
    return _df(sql, tuple(p))


def delete_paper(pid):
    with get_conn() as c:
        r = c.execute("SELECT file_path FROM papers WHERE id=?", (pid,)).fetchone()
    if r and os.path.exists(r["file_path"]):
        try:
            os.remove(r["file_path"])
        except Exception:
            pass
    _exec("DELETE FROM papers WHERE id=?", (pid,))


def post_announcement(title, body, priority, audience, posted_by):
    return _exec("""INSERT INTO announcements (title, body, priority, audience,
                    posted_by) VALUES (?,?,?,?,?)""",
                 (title, body, priority, audience, posted_by))


def list_announcements(limit=50):
    return _df("SELECT * FROM announcements ORDER BY id DESC LIMIT ?", (limit,))


def delete_announcement(aid):
    _exec("DELETE FROM announcements WHERE id=?", (aid,))


def save_period(class_id, day, period, subject_id, teacher_id):
    _exec("""INSERT INTO timetable (class_id, day, period, subject_id, teacher_id)
             VALUES (?,?,?,?,?)
             ON CONFLICT(class_id, day, period) DO UPDATE SET
                subject_id=excluded.subject_id, teacher_id=excluded.teacher_id""",
          (class_id, day, period, subject_id, teacher_id))


def class_timetable(class_id):
    return _df("""SELECT t.id, t.day, t.period, sub.name AS subject, tea.name AS teacher
        FROM timetable t LEFT JOIN subjects sub ON t.subject_id=sub.id
        LEFT JOIN teachers tea ON t.teacher_id=tea.id WHERE t.class_id=?""",
               (class_id,))


def teacher_timetable(teacher_id):
    return _df("""SELECT t.day, t.period, sub.name AS subject,
        c.name || COALESCE(' - ' || c.section,'') AS class
        FROM timetable t LEFT JOIN subjects sub ON t.subject_id=sub.id
        LEFT JOIN classes c ON t.class_id=c.id
        WHERE t.teacher_id=? ORDER BY t.period""", (teacher_id,))


def delete_period(pid):
    _exec("DELETE FROM timetable WHERE id=?", (pid,))


def dashboard_kpis():
    with get_conn() as c:
        return dict(
            students=c.execute("SELECT COUNT(*) c FROM students WHERE status='Active'").fetchone()["c"],
            teachers=c.execute("SELECT COUNT(*) c FROM teachers").fetchone()["c"],
            classes=c.execute("SELECT COUNT(*) c FROM classes").fetchone()["c"],
            collected=c.execute("SELECT COALESCE(SUM(amount),0) s FROM fee_payments").fetchone()["s"])


def attendance_trend():
    return _df("""SELECT date, status, COUNT(*) c FROM attendance
        WHERE date >= date('now','-14 days') GROUP BY date, status ORDER BY date""")


def top_performers(limit=5):
    return _df(f"""SELECT s.name, s.roll_no,
        ROUND(AVG(m.obtained*100.0/m.max_marks),1) avg_pct
        FROM students s JOIN marks m ON m.student_id=s.id
        GROUP BY s.id ORDER BY avg_pct DESC LIMIT {limit}""")


# ═══════════════════════════════════════════════════════════════════
#  LOGIN
# ═══════════════════════════════════════════════════════════════════
if "user" not in st.session_state:
    st.session_state.user = None


def login_screen():
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'''<div style="text-align:center;margin-bottom:1.5rem">
            <div style="font-size:3.5rem">🏫</div>
            <h1 style="margin:0.5rem 0 0.2rem;color:#0f172a;font-size:2rem">
            {APP_NAME}</h1>
            <p style="color:#64748b;margin:0;font-size:0.95rem">
            {APP_TAGLINE}</p>
            <p style="color:#94a3b8;margin:0.3rem 0 0;font-size:0.82rem">
            {SCHOOL_NAME}</p>
            </div>''', unsafe_allow_html=True)

        with st.form("login"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password",
                                     placeholder="••••••••")
            ok = st.form_submit_button("🔓  Sign In", use_container_width=True,
                                       type="primary")
            if ok:
                user = authenticate(username, password)
                if user:
                    st.session_state.user = user
                    log_action(user, "LOGIN", "user", user["id"])
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown("---")
        st.caption(f"**Default login** · `admin` / `Admin@123`  \n"
                   f"Change password from Settings after first login.")


# ═══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════
def page_dashboard(user):
    page_header("Dashboard", f"Welcome back, {user['full_name']}", "📊",
                crumbs=["Home", "Dashboard"])

    if user["role"] == "teacher":
        tid = user["linked_id"]
        assigns = teacher_assignments(tid) if tid else pd.DataFrame()
        classes = assigns["class"].unique().tolist() if not assigns.empty else []

        # Class teacher info
        my_class_teacher_of = _df(
            "SELECT id, name, section FROM classes WHERE teacher_id=?",
            (tid,) if tid else (0,))

        c1, c2, c3 = st.columns(3)
        with c1: kpi("My Classes", len(classes), "🏫", "#dbeafe")
        with c2: kpi("Subjects", len(assigns), "📚", "#dcfce7")
        with c3: kpi("Class Teacher Of", len(my_class_teacher_of), "🎓", "#fef3c7")

        if not my_class_teacher_of.empty:
            st.markdown("### 🎓 Classes where I am Class Teacher")
            for _, cr in my_class_teacher_of.iterrows():
                st.info(f"**{cr['name']} {cr['section'] or ''}** — you are the "
                        f"class teacher of this class.")

        st.markdown("---")
        st.markdown("### 📚 My Subject Assignments")
        if assigns.empty:
            empty_state("📚", "No assignments yet",
                        "Contact admin to assign you subjects & classes.")
        else:
            st.dataframe(assigns[["class", "subject"]],
                         use_container_width=True, hide_index=True)
        return

    if user["role"] == "student":
        sid = user["linked_id"]
        if not sid:
            empty_state("👤", "Student record not linked",
                        "Contact admin to link your account.")
            return
        student = get_student(sid)
        marks = student_marks(sid)
        summary = student_fee_summary(sid)
        c1, c2, c3 = st.columns(3)
        with c1: kpi("Class", student.get("class_id") or "—", "🏫", "#dbeafe")
        with c2: kpi("Average %",
                     f"{marks['pct'].mean():.1f}%" if not marks.empty else "—",
                     "📊", "#dcfce7")
        with c3: kpi("Fee Balance", f"₹{summary['balance']:,.0f}", "💰", "#fef3c7")
        st.markdown("---")
        st.markdown("### 📈 Recent Marks")
        if marks.empty:
            empty_state("📝", "No marks published yet")
        else:
            st.dataframe(marks, use_container_width=True, hide_index=True)
        return

    k = dashboard_kpis()
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Active Students", k["students"], "👨‍🎓", "#dbeafe")
    with c2: kpi("Teachers", k["teachers"], "👩‍🏫", "#dcfce7")
    with c3: kpi("Classes", k["classes"], "🏫", "#fef3c7")
    with c4: kpi("Fees Collected", f"₹{k['collected']:,.0f}", "💰", "#fce7f3")

    st.markdown("---")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown("### 📈 Attendance (last 14 days)")
        df = attendance_trend()
        if df.empty:
            empty_state("📅", "No attendance yet")
        else:
            fig = px.bar(df, x="date", y="c", color="status",
                         color_discrete_map={"Present": "#22c55e",
                                             "Absent": "#ef4444",
                                             "Late": "#eab308",
                                             "Leave": "#3b82f6"},
                         labels={"c": "Count", "date": "Date"})
            fig.update_layout(template="plotly_white", height=340,
                              margin=dict(l=10, r=10, t=10, b=10),
                              legend=dict(orientation="h", y=-0.2),
                              plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("### 🏆 Top Performers")
        df = top_performers()
        if df.empty:
            empty_state("🏆", "No marks yet")
        else:
            st.dataframe(df.rename(columns={"name": "Student",
                                            "roll_no": "Roll",
                                            "avg_pct": "Avg %"}),
                         use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
#  TEACHERS
# ═══════════════════════════════════════════════════════════════════
def page_teachers(user):
    page_header("Teachers", "Manage teaching staff & their logins", "👩‍🏫",
                crumbs=["Home", "Teachers"])

    tab1, tab2, tab3 = st.tabs(["📋 All Teachers", "➕ Add Teacher", "🔗 Assignments"])

    with tab2:
        with st.form("add_teacher", clear_on_submit=True):
            st.markdown("**Personal Info**")
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *", placeholder="e.g., Rajesh Kumar")
                email = st.text_input("Email", placeholder="teacher@school.com")
                phone = st.text_input("Phone", placeholder="+91 98765 43210")
            with c2:
                emp = st.text_input("Employee ID", placeholder="EMP001")
                qual = st.text_input("Qualification", placeholder="M.Sc, B.Ed")
                jd = st.date_input("Joining Date", value=date.today())

            st.markdown("**Login Credentials**")
            c3, c4 = st.columns(2)
            with c3:
                username = st.text_input("Username *",
                                         placeholder="Auto-generated if blank")
            with c4:
                password = st.text_input("Password *", type="password",
                                         value="Teacher@123")

            if st.form_submit_button("✅  Create Teacher + Login",
                                     type="primary", use_container_width=True):
                try:
                    if not name.strip():
                        raise ValueError("Name is required.")
                    uname = username.strip() or (
                        name.lower().replace(" ", ".") +
                        str(int(datetime.now().timestamp()))[-3:])
                    tid = add_teacher({
                        "employee_id": emp or None, "name": name.strip(),
                        "email": email or None, "phone": phone,
                        "qualification": qual, "join_date": jd.isoformat(),
                    })
                    uid = create_user(uname, password, "teacher", name,
                                      linked_id=tid, email=email or None,
                                      phone=phone or None)
                    if not uid:
                        raise ValueError(f"Username '{uname}' already exists.")
                    log_action(user, "CREATE", "teacher", tid, f"{name}")
                    st.success(
                        f"✅ **Teacher created!**  \n"
                        f"Login → `{uname}`  \n"
                        f"Password → `{password}`")
                except Exception as e:
                    st.error(f"⚠️ {e}")

    with tab1:
        search = st.text_input("🔍  Search", placeholder="Name, email, employee ID")
        df = list_teachers(search)
        if df.empty:
            empty_state("👩‍🏫", "No teachers yet")
            return

        with get_conn() as c:
            logins = pd.read_sql_query(
                "SELECT linked_id, username, last_login, is_active "
                "FROM users WHERE role='teacher'", c)
        if not logins.empty:
            df = df.merge(logins, left_on="id", right_on="linked_id", how="left")

        st.markdown(f"**{len(df)} teachers**")
        st.dataframe(
            df.rename(columns={
                "id": "ID", "employee_id": "Emp#", "name": "Name",
                "email": "Email", "phone": "Phone",
                "qualification": "Qualification", "join_date": "Joined",
                "status": "Status", "username": "Login Username",
                "last_login": "Last Login", "is_active": "Active",
            }).drop(columns=["linked_id"], errors="ignore"),
            use_container_width=True, hide_index=True)
        download_csv(df, "teachers")

        st.markdown("---")
        st.markdown("### ✏️  Edit / Delete Teacher")
        pick = st.selectbox("Select teacher", df["id"].tolist(),
                            format_func=lambda x: f"#{x} — {df[df['id']==x]['name'].values[0]}",
                            key="edit_teacher_pick")

        t = get_teacher(pick)
        with st.form("edit_teacher_form"):
            c1, c2 = st.columns(2)
            with c1:
                ename = st.text_input("Name", value=t["name"], key="et_name")
                eemp = st.text_input("Employee ID", value=t["employee_id"] or "",
                                     key="et_emp")
                eemail = st.text_input("Email", value=t["email"] or "", key="et_email")
            with c2:
                ephone = st.text_input("Phone", value=t["phone"] or "", key="et_phone")
                equal = st.text_input("Qualification", value=t["qualification"] or "",
                                      key="et_qual")
                estatus = st.selectbox("Status", ["Active", "Inactive"],
                                       index=0 if t["status"] == "Active" else 1,
                                       key="et_status")

            c3, c4 = st.columns(2)
            if c3.form_submit_button("💾  Save Changes", type="primary",
                                     use_container_width=True):
                update_teacher(pick, {
                    "name": ename, "employee_id": eemp, "email": eemail,
                    "phone": ephone, "qualification": equal, "status": estatus,
                })
                log_action(user, "UPDATE", "teacher", pick, ename)
                st.success("✅ Updated.")
                st.rerun()

            if c4.form_submit_button("🗑️  Delete Teacher", use_container_width=True):
                if st.session_state.get(f"confirm_del_teacher_{pick}"):
                    delete_teacher(pick)
                    log_action(user, "DELETE", "teacher", pick, t["name"])
                    st.success("✅ Deleted.")
                    st.rerun()
                else:
                    st.session_state[f"confirm_del_teacher_{pick}"] = True
                    st.warning("Click again to confirm delete.")

    with tab3:
        teachers_list = list_teachers()
        subjects = list_subjects()
        classes = list_classes()

        if subjects.empty or classes.empty or teachers_list.empty:
            empty_state("🔗", "Setup required",
                        "Create at least one teacher, subject, and class first.")
            return

        t_opts = {f"{r['name']} (#{r['id']})": r["id"]
                  for _, r in teachers_list.iterrows()}
        s_opts = {r["name"]: r["id"] for _, r in subjects.iterrows()}
        c_opts = {f"{r['name']}" + (f" - {r['section']}" if r["section"] else ""): r["id"]
                  for _, r in classes.iterrows()}

        with st.form("assign_form"):
            c1, c2, c3 = st.columns(3)
            with c1: tsel = st.selectbox("Teacher", list(t_opts.keys()))
            with c2: ssel = st.selectbox("Subject", list(s_opts.keys()))
            with c3: csel = st.selectbox("Class", list(c_opts.keys()))
            if st.form_submit_button("🔗  Assign", type="primary",
                                     use_container_width=True):
                ok = assign_teacher_subject(t_opts[tsel], s_opts[ssel],
                                            c_opts[csel])
                if ok:
                    st.success("✅ Assigned.")
                    st.rerun()
                else:
                    st.warning("⚠️ Already assigned.")

        st.markdown("#### Current Assignments")
        tsel2 = st.selectbox("View for", list(t_opts.keys()), key="view_assign")
        assigns = teacher_assignments(t_opts[tsel2])
        if assigns.empty:
            st.info("No assignments yet.")
        else:
            st.dataframe(assigns[["id", "class", "subject"]],
                         use_container_width=True, hide_index=True)
            rid = st.selectbox("Remove assignment (ID)", assigns["id"].tolist())
            if st.button("🗑️  Remove"):
                remove_assignment(rid)
                st.success("Removed.")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  STUDENTS
# ═══════════════════════════════════════════════════════════════════
def page_students(user):
    page_header("Students", "Manage student records", "👨‍🎓",
                crumbs=["Home", "Students"])

    classes = list_classes()
    if classes.empty:
        empty_state("🏫", "Create a class first",
                    "Go to Classes page and add your first class.")
        return

    class_opts = {"— All —": None}
    for _, r in classes.iterrows():
        lbl = r["name"] + (f" - {r['section']}" if r["section"] else "")
        class_opts[lbl] = r["id"]

    tab1, tab2 = st.tabs(["📋 All Students", "➕ Add Student"])

    with tab2:
        with st.form("add_student", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *", placeholder="e.g., Aarav Sharma")
                roll = st.text_input("Roll Number *", placeholder="01")
                adm = st.text_input("Admission No", placeholder="ADM2024001")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                dob = st.date_input("Date of Birth", value=date(2010, 1, 1))
            with c2:
                cls = st.selectbox("Class *", list(class_opts.keys())[1:])
                guardian = st.text_input("Guardian Name", placeholder="Parent name")
                phone = st.text_input("Guardian Phone", placeholder="+91 98765 43210")
                email = st.text_input("Guardian Email", placeholder="parent@email.com")
                address = st.text_area("Address", height=90,
                                       placeholder="House, Street, City")
            if st.form_submit_button("✅  Add Student", type="primary",
                                     use_container_width=True):
                try:
                    if not name.strip():
                        raise ValueError("Name required.")
                    sid = add_student({
                        "admission_no": adm or None, "name": name.strip(),
                        "roll_no": roll, "class_id": class_opts[cls],
                        "gender": gender, "dob": dob.isoformat(),
                        "guardian_name": guardian, "guardian_phone": phone,
                        "guardian_email": email, "address": address,
                    })
                    log_action(user, "CREATE", "student", sid, name)
                    st.success(f"✅ Student '{name}' added successfully.")
                except Exception as e:
                    st.error(f"⚠️ {e}")

    with tab1:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            search = st.text_input("🔍  Search", placeholder="Name, roll, admission no")
        with c2:
            filt_cls = st.selectbox("Class", list(class_opts.keys()))
        with c3:
            filt_status = st.selectbox("Status", ["All", "Active", "Inactive"])

        df = list_students(search, class_opts[filt_cls], filt_status)
        if df.empty:
            empty_state("👨‍🎓", "No students found")
            return

        st.markdown(f"**{len(df)} students**")
        st.dataframe(df.rename(columns={
            "id": "ID", "admission_no": "Adm#", "name": "Name",
            "roll_no": "Roll", "class": "Class", "gender": "Gender",
            "status": "Status", "guardian_name": "Guardian",
            "guardian_phone": "Phone"}).drop(columns=["class_id"]),
            use_container_width=True, hide_index=True)
        download_csv(df, "students")

        st.markdown("---")
        st.markdown("### ✏️  Edit / Delete Student")
        pick = st.selectbox("Select student", df["id"].tolist(),
                            format_func=lambda x: f"#{x} — {df[df['id']==x]['name'].values[0]}",
                            key="edit_student_pick")

        s = get_student(pick)
        class_id_list = list(class_opts.values())[1:]
        cur_class_idx = (class_id_list.index(s["class_id"])
                         if s["class_id"] in class_id_list else 0)

        with st.form("edit_student_form"):
            c1, c2 = st.columns(2)
            with c1:
                nm = st.text_input("Name", value=s["name"], key="es_name")
                rl = st.text_input("Roll", value=s["roll_no"] or "", key="es_roll")
                adm2 = st.text_input("Admission No", value=s["admission_no"] or "",
                                     key="es_adm")
                gd = st.selectbox("Gender", ["Male", "Female", "Other"],
                                  index=["Male", "Female", "Other"].index(s["gender"])
                                  if s["gender"] in ["Male", "Female", "Other"] else 0,
                                  key="es_gender")
            with c2:
                cls2 = st.selectbox("Class", list(class_opts.keys())[1:],
                                    index=cur_class_idx, key="es_class")
                guardian2 = st.text_input("Guardian",
                                          value=s["guardian_name"] or "", key="es_guard")
                phone2 = st.text_input("Phone",
                                       value=s["guardian_phone"] or "", key="es_phone")
                status2 = st.selectbox("Status", ["Active", "Inactive"],
                                       index=0 if s["status"] == "Active" else 1,
                                       key="es_status")

            c3, c4 = st.columns(2)
            if c3.form_submit_button("💾  Save Changes", type="primary",
                                     use_container_width=True):
                s.update({
                    "name": nm, "roll_no": rl, "admission_no": adm2,
                    "gender": gd, "class_id": class_opts[cls2],
                    "guardian_name": guardian2, "guardian_phone": phone2,
                    "status": status2,
                })
                update_student(pick, s)
                log_action(user, "UPDATE", "student", pick, nm)
                st.success("✅ Updated.")
                st.rerun()

            if c4.form_submit_button("🗑️  Delete Student", use_container_width=True):
                if st.session_state.get(f"confirm_del_student_{pick}"):
                    delete_student(pick)
                    log_action(user, "DELETE", "student", pick, s["name"])
                    st.success("✅ Deleted.")
                    st.rerun()
                else:
                    st.session_state[f"confirm_del_student_{pick}"] = True
                    st.warning("Click again to confirm delete.")


# ═══════════════════════════════════════════════════════════════════
#  CLASSES (with Class Teacher)
# ═══════════════════════════════════════════════════════════════════
def page_classes(user):
    page_header("Classes & Sections", "Organize classes & assign class teachers", "🏫",
                crumbs=["Home", "Classes"])

    teachers = list_teachers()
    t_opts = {"— Not assigned —": None}
    if not teachers.empty:
        t_opts.update({f"{r['name']} (#{r['id']})": r["id"]
                       for _, r in teachers.iterrows()})

    tab1, tab2 = st.tabs(["📋 All Classes", "➕ Add Class"])

    with tab2:
        with st.form("add_class", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: name = st.text_input("Class Name *", placeholder="Grade 10")
            with c2: section = st.text_input("Section", placeholder="A")
            with c3: cap = st.number_input("Capacity", 1, 200, 40)

            st.markdown("**Class Teacher**")
            teacher_sel = st.selectbox(
                "Assign class teacher", list(t_opts.keys()),
                help="Class teacher will be responsible for this class. "
                     "Can be changed anytime.")

            if st.form_submit_button("✅  Add Class", type="primary",
                                     use_container_width=True):
                try:
                    if not name.strip():
                        raise ValueError("Class name required.")
                    cid = add_class(name.strip(), section.strip(),
                                    int(cap), t_opts[teacher_sel])
                    log_action(user, "CREATE", "class", cid,
                               f"{name} - {section} | teacher: {teacher_sel}")
                    st.success(f"✅ Class '{name} {section}' added.")
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ {e}")

    with tab1:
        df = list_classes()
        if df.empty:
            empty_state("🏫", "No classes yet",
                        "Add your first class from the other tab.")
            return

        st.dataframe(df.rename(columns={
            "id": "ID", "name": "Class", "section": "Section",
            "capacity": "Capacity", "students": "Students",
            "class_teacher": "Class Teacher"}).drop(
            columns=["teacher_id"], errors="ignore"),
            use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ✏️  Edit / Delete Class")
        pick = st.selectbox(
            "Select class", df["id"].tolist(),
            format_func=lambda x: f"#{x} — {df[df['id']==x]['name'].values[0]} "
                                  f"{df[df['id']==x]['section'].values[0] or ''}",
            key="edit_class_pick")
        row = df[df["id"] == pick].iloc[0]

        current_teacher_label = "— Not assigned —"
        if row["teacher_id"]:
            for lbl, tid in t_opts.items():
                if tid == row["teacher_id"]:
                    current_teacher_label = lbl
                    break

        with st.form("edit_class_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                nm = st.text_input("Class Name", value=row["name"])
            with c2:
                sec = st.text_input("Section", value=row["section"] or "")
            with c3:
                cap2 = st.number_input("Capacity", 1, 200,
                                       int(row["capacity"] or 40))

            st.markdown("**Class Teacher**")
            teacher_opts_list = list(t_opts.keys())
            new_teacher = st.selectbox(
                "Assign class teacher", teacher_opts_list,
                index=teacher_opts_list.index(current_teacher_label),
                help="Change the class teacher here",
                key="edit_class_teacher")

            c4, c5 = st.columns(2)
            if c4.form_submit_button("💾  Save Changes", type="primary",
                                     use_container_width=True):
                update_class(pick, nm, sec, int(cap2), t_opts[new_teacher])
                log_action(user, "UPDATE", "class", pick,
                           f"{nm} - {sec} | teacher: {new_teacher}")
                st.success("✅ Updated successfully.")
                st.rerun()

            if c5.form_submit_button("🗑️  Delete Class", use_container_width=True):
                if st.session_state.get(f"confirm_del_class_{pick}"):
                    delete_class(pick)
                    log_action(user, "DELETE", "class", pick, nm)
                    st.success("✅ Deleted.")
                    st.rerun()
                else:
                    st.session_state[f"confirm_del_class_{pick}"] = True
                    st.warning("Click again to confirm delete.")


# ═══════════════════════════════════════════════════════════════════
#  SUBJECTS
# ═══════════════════════════════════════════════════════════════════
def page_subjects(user):
    page_header("Subjects", "Manage subjects", "📚",
                crumbs=["Home", "Subjects"])

    tab1, tab2 = st.tabs(["📋 All Subjects", "➕ Add Subject"])

    with tab2:
        with st.form("add_subject", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: nm = st.text_input("Subject Name *", placeholder="Mathematics")
            with c2: code = st.text_input("Code", placeholder="MATH101")
            with c3: mm = st.number_input("Max Marks", 1, 500, 100)
            if st.form_submit_button("✅  Add Subject", type="primary",
                                     use_container_width=True):
                try:
                    if not nm.strip():
                        raise ValueError("Name required.")
                    sid = add_subject(nm.strip(), code, int(mm))
                    st.success(f"✅ '{nm}' added.")
                except Exception as e:
                    st.error(f"⚠️ {e}")

    with tab1:
        df = list_subjects()
        if df.empty:
            empty_state("📚", "No subjects yet")
            return

        st.dataframe(df.rename(columns={
            "id": "ID", "name": "Subject", "code": "Code",
            "max_marks": "Max Marks"}),
            use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ✏️  Edit / Delete Subject")
        pick = st.selectbox("Select subject", df["id"].tolist(),
                            format_func=lambda x: f"#{x} — {df[df['id']==x]['name'].values[0]}",
                            key="edit_subject_pick")
        row = df[df["id"] == pick].iloc[0]

        with st.form("edit_subject_form"):
            c1, c2, c3 = st.columns(3)
            with c1: nm2 = st.text_input("Name", value=row["name"])
            with c2: code2 = st.text_input("Code", value=row["code"] or "")
            with c3: mm2 = st.number_input("Max Marks", 1, 500,
                                           int(row["max_marks"] or 100))
            c4, c5 = st.columns(2)
            if c4.form_submit_button("💾  Save", type="primary",
                                     use_container_width=True):
                update_subject(pick, nm2, code2, int(mm2))
                st.success("✅ Updated.")
                st.rerun()
            if c5.form_submit_button("🗑️  Delete Subject", use_container_width=True):
                if st.session_state.get(f"confirm_del_subject_{pick}"):
                    delete_subject(pick)
                    st.success("✅ Deleted.")
                    st.rerun()
                else:
                    st.session_state[f"confirm_del_subject_{pick}"] = True
                    st.warning("Click again to confirm.")


# ═══════════════════════════════════════════════════════════════════
#  ATTENDANCE
# ═══════════════════════════════════════════════════════════════════
def page_attendance(user):
    page_header("Attendance", "Mark daily attendance", "📅",
                crumbs=["Home", "Attendance"])

    classes = list_classes()
    if classes.empty:
        empty_state("🏫", "No classes yet")
        return

    if user["role"] == "teacher" and user["linked_id"]:
        tid = user["linked_id"]
        # Allowed = subjects assigned OR class teacher of
        assigns = teacher_assignments(tid)
        allowed = set(assigns["class"].tolist()) if not assigns.empty else set()
        ct_classes = _df("SELECT name, section FROM classes WHERE teacher_id=?", (tid,))
        if not ct_classes.empty:
            for _, r in ct_classes.iterrows():
                allowed.add(r["name"] + (f" - {r['section']}" if r["section"] else ""))
        classes = classes[classes.apply(
            lambda r: (r["name"] + (f" - {r['section']}" if r["section"] else ""))
            in allowed, axis=1)]
        if classes.empty:
            empty_state("📅", "No classes assigned to you",
                        "Contact admin.")
            return

    c_opts = {f"{r['name']}" + (f" - {r['section']}" if r["section"] else ""): r["id"]
              for _, r in classes.iterrows()}

    c1, c2 = st.columns([1, 1])
    with c1: cls = st.selectbox("Class", list(c_opts.keys()))
    with c2: day = st.date_input("Date", value=date.today())

    rows = get_attendance(c_opts[cls], day.isoformat())
    if rows.empty:
        empty_state("👨‍🎓", "No students in this class")
        return

    with st.form("att_form"):
        statuses = {}
        for _, r in rows.iterrows():
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**{r['name']}**  \n"
                            f"<small style='color:#64748b'>Roll: {r['roll_no']}</small>",
                            unsafe_allow_html=True)
            with cols[1]:
                cur = r["status"] or "Present"
                statuses[r["id"]] = st.selectbox(
                    "Status", ["Present", "Absent", "Late", "Leave"],
                    index=["Present", "Absent", "Late", "Leave"].index(cur),
                    key=f"a_{r['id']}", label_visibility="collapsed")
        if st.form_submit_button("💾  Save Attendance", type="primary",
                                 use_container_width=True):
            for sid, stv in statuses.items():
                save_attendance(sid, c_opts[cls], day.isoformat(), stv, user["id"])
            log_action(user, "UPDATE", "attendance", None, f"{cls} on {day}")
            st.success("✅ Attendance saved.")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Cumulative Summary")
    summ = attendance_summary(c_opts[cls])
    if not summ.empty:
        st.dataframe(summ.rename(columns={
            "name": "Student", "roll_no": "Roll", "present": "Present",
            "absent": "Absent", "late": "Late", "leave": "Leave",
            "total": "Total"}),
            use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
#  EXAMINATIONS
# ═══════════════════════════════════════════════════════════════════
def page_examinations(user):
    page_header("Examinations", "Enter marks & view report cards", "📝",
                crumbs=["Home", "Examinations"])

    classes = list_classes()
    subjects = list_subjects()
    if classes.empty or subjects.empty:
        empty_state("📚", "Setup required",
                    "Create at least one class and one subject first.")
        return

    c_opts = {f"{r['name']}" + (f" - {r['section']}" if r["section"] else ""): r["id"]
              for _, r in classes.iterrows()}
    s_opts = {r["name"]: r["id"] for _, r in subjects.iterrows()}

    tab1, tab2 = st.tabs(["📝 Enter Marks", "🏅 Report Card"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        with c1: cls = st.selectbox("Class", list(c_opts.keys()), key="mk_cls")
        with c2: subj = st.selectbox("Subject", list(s_opts.keys()), key="mk_sub")
        with c3: exam = st.selectbox("Exam", EXAMS)
        with c4: max_m = st.number_input("Max Marks", 1, 500, 100, key="mk_max")

        students = students_in_class(c_opts[cls])
        if students.empty:
            empty_state("👨‍🎓", "No students in this class")
            return

        with st.form("marks_form"):
            scores = {}
            for _, r in students.iterrows():
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**{r['name']}**  \n"
                                f"<small style='color:#64748b'>Roll: {r['roll_no']}</small>",
                                unsafe_allow_html=True)
                with cols[1]:
                    scores[r["id"]] = st.number_input(
                        "Marks", 0.0, float(max_m), 0.0,
                        key=f"m_{r['id']}", label_visibility="collapsed")
            if st.form_submit_button("💾  Save Marks", type="primary",
                                     use_container_width=True):
                for sid, obt in scores.items():
                    save_marks(sid, s_opts[subj], exam, max_m, obt,
                               date.today().isoformat(), user["id"])
                log_action(user, "UPDATE", "marks", None, f"{cls}/{subj}/{exam}")
                st.success("✅ Marks saved.")
                st.rerun()

    with tab2:
        c1, c2 = st.columns(2)
        with c1: cls2 = st.selectbox("Class", list(c_opts.keys()), key="rp_cls")
        with c2:
            st_df = students_in_class(c_opts[cls2])
            if st_df.empty:
                empty_state("👨‍🎓", "No students")
                return
            sid = st.selectbox(
                "Student", st_df["id"].tolist(),
                format_func=lambda x: st_df[st_df["id"] == x]["name"].values[0],
                key="rp_student")

        marks = student_marks(sid)
        student = get_student(sid)
        if marks.empty:
            empty_state("📝", "No marks entered yet")
            return

        avg = marks["pct"].mean()
        grade, color = grade_for(avg)

        st.markdown(
            f'''<div class="receipt" style="max-width:100%">
            <div style="display:flex;justify-content:space-between;align-items:start;
                        border-bottom:2px solid #0f172a;padding-bottom:0.8rem">
              <div>
                <h2>🏫 {SCHOOL_NAME}</h2>
                <div style="color:#64748b;font-size:0.82rem">Academic Report Card</div>
              </div>
              <div style="text-align:right">
                <div style="font-size:0.75rem;color:#64748b">Grade</div>
                <div style="font-size:2rem;font-weight:800;color:{color}">{grade}</div>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;
                        margin:1rem 0">
              <div><div style="font-size:0.75rem;color:#64748b">Student</div>
                   <div style="font-weight:600">{student["name"]}</div></div>
              <div><div style="font-size:0.75rem;color:#64748b">Roll No</div>
                   <div style="font-weight:600">{student["roll_no"] or "—"}</div></div>
              <div><div style="font-size:0.75rem;color:#64748b">Average</div>
                   <div style="font-weight:600">{avg:.1f}%</div></div>
            </div>
            </div>''', unsafe_allow_html=True)

        st.dataframe(marks.rename(columns={
            "id": "ID", "exam": "Exam", "subject": "Subject", "code": "Code",
            "max_marks": "Max", "obtained": "Obtained", "pct": "%"}),
            use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ✏️  Edit / Delete Mark")
        mid = st.selectbox(
            "Select mark record", marks["id"].tolist(),
            format_func=lambda x: f"#{x} — {marks[marks['id']==x]['subject'].values[0]} ({marks[marks['id']==x]['exam'].values[0]})",
            key="edit_mark_pick")
        mrow = marks[marks["id"] == mid].iloc[0]

        with st.form("edit_mark_form"):
            c1, c2 = st.columns(2)
            with c1: new_obt = st.number_input("Obtained", 0.0, 500.0,
                                                float(mrow["obtained"]))
            with c2: new_max = st.number_input("Max", 1.0, 500.0,
                                                float(mrow["max_marks"]))
            c3, c4 = st.columns(2)
            if c3.form_submit_button("💾  Save", type="primary",
                                     use_container_width=True):
                update_mark(mid, new_obt, new_max)
                st.success("✅ Updated.")
                st.rerun()
            if c4.form_submit_button("🗑️  Delete Mark", use_container_width=True):
                if st.session_state.get(f"confirm_del_mark_{mid}"):
                    delete_mark(mid)
                    st.success("✅ Deleted.")
                    st.rerun()
                else:
                    st.session_state[f"confirm_del_mark_{mid}"] = True
                    st.warning("Click again to confirm.")


# ═══════════════════════════════════════════════════════════════════
#  FEE COLLECTION
# ═══════════════════════════════════════════════════════════════════
def page_fee_collection(user):
    page_header("Fee Collection", "Collect fees & generate receipts", "💰",
                crumbs=["Home", "Fee Collection"])

    tab1, tab2, tab3 = st.tabs(["💵 Collect Fee", "🧾 All Payments", "🏷️ Fee Structure"])

    with tab3:
        classes = list_classes()
        if classes.empty:
            empty_state("🏫", "Create a class first")
            return
        c_opts = {f"{r['name']}" + (f" - {r['section']}" if r["section"] else ""): r["id"]
                  for _, r in classes.iterrows()}

        with st.form("fee_struct_form"):
            c1, c2, c3 = st.columns(3)
            with c1: cls_s = st.selectbox("Class", list(c_opts.keys()), key="fs_cls")
            with c2: month = st.selectbox("Month", FEE_MONTHS, key="fs_month")
            with c3: amt = st.number_input("Amount (₹)", 0.0, 1_000_000.0,
                                           5000.0, 100.0, key="fs_amt")
            if st.form_submit_button("💾  Set Fee", type="primary",
                                     use_container_width=True):
                set_fee_structure(c_opts[cls_s], month, amt)
                st.success("✅ Fee structure saved.")
                st.rerun()

        st.markdown("### 📋 Current Fee Structures")
        all_structs = []
        for lbl, cid in c_opts.items():
            fs = get_fee_structure(cid)
            if not fs.empty:
                fs.insert(0, "class", lbl)
                all_structs.append(fs)

        if not all_structs:
            st.info("No fee structure defined yet.")
        else:
            combined = pd.concat(all_structs, ignore_index=True)
            st.dataframe(
                combined[["id", "class", "month", "amount"]].rename(
                    columns={"id": "ID", "class": "Class",
                             "month": "Month", "amount": "Amount"}),
                use_container_width=True, hide_index=True)

            st.markdown("### ✏️  Edit / Delete Fee Structure")
            pick = st.selectbox(
                "Select record", combined["id"].tolist(),
                format_func=lambda x: f"#{x} — {combined[combined['id']==x]['class'].values[0]} / {combined[combined['id']==x]['month'].values[0]}",
                key="edit_fs_pick")
            row = combined[combined["id"] == pick].iloc[0]

            with st.form("edit_fs_form"):
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Class", value=row["class"], disabled=True)
                with c2:
                    new_amt = st.number_input("Amount (₹)", 0.0, 1_000_000.0,
                                              float(row["amount"]))
                c3, c4 = st.columns(2)
                if c3.form_submit_button("💾  Update", type="primary",
                                         use_container_width=True):
                    update_fee_structure(pick, new_amt)
                    st.success("✅ Updated.")
                    st.rerun()
                if c4.form_submit_button("🗑️  Delete", use_container_width=True):
                    if st.session_state.get(f"confirm_del_fs_{pick}"):
                        delete_fee_structure(pick)
                        st.success("✅ Deleted.")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_fs_{pick}"] = True
                        st.warning("Click again to confirm.")

    with tab1:
        students = list_students(status="Active")
        if students.empty:
            empty_state("👨‍🎓", "No active students")
            return

        search = st.text_input("🔍  Search student",
                               placeholder="Name or roll number")
        filtered = students
        if search:
            mask = (students["name"].str.contains(search, case=False, na=False) |
                    students["roll_no"].astype(str).str.contains(search, case=False, na=False))
            filtered = students[mask]

        if filtered.empty:
            st.info("No matching students.")
            return

        s_opts = {f"{r['name']} ({r['roll_no']}) — {r['class']}": r["id"]
                  for _, r in filtered.iterrows()}
        sel = st.selectbox("Select student", list(s_opts.keys()))
        sid = s_opts[sel]
        student = get_student(sid)

        st.markdown("---")
        st.markdown(f"### 👤 {student['name']}")
        c1, c2, c3 = st.columns(3)
        summary = student_fee_summary(sid)
        with c1: kpi("Total Due", f"₹{summary['total_due']:,.0f}", "📋", "#dbeafe")
        with c2: kpi("Paid", f"₹{summary['total_paid']:,.0f}", "✅", "#dcfce7")
        with c3: kpi("Balance", f"₹{summary['balance']:,.0f}", "⚠️", "#fee2e2")

        st.markdown("### 📅 Month-wise Breakdown")
        if summary["months"]:
            month_df = pd.DataFrame(summary["months"])
            month_df["status"] = month_df.apply(
                lambda r: "Paid" if r["balance"] <= 0 else
                          ("Partial" if r["paid"] > 0 else "Pending"), axis=1)
            st.dataframe(month_df.rename(columns={
                "month": "Month", "amount": "Fee", "paid": "Paid",
                "balance": "Balance", "status": "Status"}),
                use_container_width=True, hide_index=True)
        else:
            st.info("No fee structure set for this class.")

        st.markdown("---")
        st.markdown("### 💵 Record Payment")
        with st.form("pay_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                pay_amt = st.number_input("Amount (₹)", 0.0, 1_000_000.0,
                                          float(max(summary["balance"], 100.0)),
                                          100.0)
                pay_month = st.selectbox("Month", FEE_MONTHS, key="pay_month")
            with c2:
                method = st.selectbox("Method",
                                      ["Cash", "UPI", "Bank Transfer",
                                       "Cheque", "Card"])
                pay_date = st.date_input("Payment Date", value=date.today())
            with c3:
                note = st.text_input("Note")

            if st.form_submit_button("💰  Collect & Generate Receipt",
                                     type="primary", use_container_width=True):
                if pay_amt <= 0:
                    st.error("Amount must be greater than zero.")
                else:
                    rid, receipt_no = collect_fee(
                        sid, pay_amt, pay_month, method,
                        pay_date.isoformat(), note, user["id"])
                    log_action(user, "CREATE", "fee_payment", rid,
                               f"{student['name']} ₹{pay_amt:,.0f}")
                    st.session_state["last_receipt_id"] = rid
                    st.success(f"✅ Payment collected. Receipt: **{receipt_no}**")
                    st.rerun()

        if st.session_state.get("last_receipt_id"):
            rid = st.session_state["last_receipt_id"]
            payment = get_payment(rid)
            if payment:
                pstudent = get_student(payment["student_id"])
                st.markdown("---")
                st.markdown("### 🧾 Receipt Preview")
                st.markdown(f'''
                <div class="receipt">
                  <div style="display:flex;justify-content:space-between;align-items:start">
                    <div>
                      <h2>🏫 {SCHOOL_NAME}</h2>
                      <div style="color:#64748b;font-size:0.8rem">{SCHOOL_ADDRESS}</div>
                      <div style="color:#64748b;font-size:0.8rem">
                        📞 {SCHOOL_PHONE} · ✉️ {SCHOOL_EMAIL}</div>
                    </div>
                    <div style="text-align:right">
                      <div style="font-size:0.75rem;color:#64748b">FEE RECEIPT</div>
                      <div style="font-weight:800;font-size:1.1rem">{payment["receipt_no"]}</div>
                      <div style="font-size:0.75rem;color:#64748b">{payment["created_at"][:10]}</div>
                    </div>
                  </div>
                  <hr>
                  <table>
                    <tr><td><b>Student</b></td><td>{pstudent["name"]}</td>
                        <td><b>Roll No</b></td><td>{pstudent["roll_no"] or "—"}</td></tr>
                    <tr><td><b>Month</b></td><td>{payment["month"]}</td>
                        <td><b>Method</b></td><td>{payment["method"]}</td></tr>
                    <tr><td><b>Paid On</b></td><td>{payment["paid_date"]}</td>
                        <td><b>Note</b></td><td>{payment["note"] or "—"}</td></tr>
                  </table>
                  <div style="text-align:center;margin:1rem 0">
                    <div style="color:#64748b;font-size:0.85rem">Amount Paid</div>
                    <div class="total">₹{payment["amount"]:,.2f}</div>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-top:1.5rem">
                    <div style="text-align:center">
                      <div class="sign-line" style="width:150px"></div>
                      <div style="font-size:0.75rem;color:#64748b">Payer Signature</div>
                    </div>
                    <div style="text-align:center">
                      <div class="sign-line" style="width:150px"></div>
                      <div style="font-size:0.75rem;color:#64748b">
                        Authorized Signatory</div>
                    </div>
                  </div>
                  <div style="text-align:center;margin-top:1.2rem;
                              color:#94a3b8;font-size:0.72rem">
                    This is a computer-generated receipt. Thank you for your payment.
                  </div>
                </div>''', unsafe_allow_html=True)

                if st.button("✅  Done / Next Student"):
                    del st.session_state["last_receipt_id"]
                    st.rerun()

    with tab2:
        search = st.text_input("🔍  Search by name, roll, or receipt")
        df = list_fee_payments(search=search)
        if df.empty:
            empty_state("💰", "No fee payments recorded")
            return

        c1, c2, c3 = st.columns(3)
        with c1: kpi("Total Records", len(df), "🧾", "#dbeafe")
        with c2: kpi("Total Collected", f"₹{df['amount'].sum():,.0f}", "💰", "#dcfce7")
        with c3: kpi("This Month",
                     f"₹{df[df['paid_date'].astype(str).str.startswith(date.today().strftime('%Y-%m'))]['amount'].sum():,.0f}",
                     "📅", "#fef3c7")

        st.dataframe(df.rename(columns={
            "id": "ID", "receipt_no": "Receipt#", "student": "Student",
            "roll_no": "Roll", "class": "Class", "amount": "Amount",
            "month": "Month", "method": "Method", "paid_date": "Paid On",
            "note": "Note", "created_at": "Created"}).drop(
            columns=["student_id"]),
            use_container_width=True, hide_index=True)
        download_csv(df, "fee_payments")

        st.markdown("---")
        st.markdown("### ✏️  Edit / Delete Payment")
        pick = st.selectbox(
            "Select payment", df["id"].tolist(),
            format_func=lambda x: f"#{x} — {df[df['id']==x]['receipt_no'].values[0]} / ₹{df[df['id']==x]['amount'].values[0]:,.0f}",
            key="edit_pay_pick")
        prow = df[df["id"] == pick].iloc[0]

        with st.form("edit_pay_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_amt2 = st.number_input("Amount (₹)", 0.0, 1_000_000.0,
                                           float(prow["amount"]))
                new_month = st.selectbox("Month", FEE_MONTHS,
                                         index=FEE_MONTHS.index(prow["month"])
                                         if prow["month"] in FEE_MONTHS else 0)
            with c2:
                new_method = st.selectbox("Method",
                                          ["Cash", "UPI", "Bank Transfer",
                                           "Cheque", "Card"],
                                          index=["Cash", "UPI", "Bank Transfer",
                                                 "Cheque", "Card"].index(prow["method"])
                                          if prow["method"] in
                                          ["Cash", "UPI", "Bank Transfer",
                                           "Cheque", "Card"] else 0)
                new_date = st.date_input("Paid Date",
                                         value=datetime.strptime(prow["paid_date"],
                                                                "%Y-%m-%d").date()
                                         if prow["paid_date"] else date.today())
            with c3:
                new_note = st.text_input("Note", value=prow["note"] or "")

            c4, c5 = st.columns(2)
            if c4.form_submit_button("💾  Update", type="primary",
                                     use_container_width=True):
                update_payment(pick, new_amt2, new_month, new_method,
                               new_date.isoformat(), new_note)
                st.success("✅ Updated.")
                st.rerun()
            if c5.form_submit_button("🗑️  Delete Payment", use_container_width=True):
                if st.session_state.get(f"confirm_del_pay_{pick}"):
                    delete_payment(pick)
                    st.success("✅ Deleted.")
                    st.rerun()
                else:
                    st.session_state[f"confirm_del_pay_{pick}"] = True
                    st.warning("Click again to confirm.")


# ═══════════════════════════════════════════════════════════════════
#  PAPERS
# ═══════════════════════════════════════════════════════════════════
def page_papers(user):
    page_header("Papers & Study Material",
                "Upload question papers, notes, study material", "📄",
                crumbs=["Home", "Papers & Material"])

    classes = list_classes()
    subjects = list_subjects()
    c_opts = {"—": None}
    if not classes.empty:
        for _, r in classes.iterrows():
            lbl = r["name"] + (f" - {r['section']}" if r["section"] else "")
            c_opts[lbl] = r["id"]
    s_opts = {"—": None}
    if not subjects.empty:
        s_opts.update({r["name"]: r["id"] for _, r in subjects.iterrows()})

    if user["role"] in ("admin", "teacher"):
        with st.expander("⬆️  Upload New Paper / Material", expanded=False):
            with st.form("upload_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    title = st.text_input("Title *", placeholder="Chapter 5 Notes")
                    ptype = st.selectbox("Type",
                                         ["Question Paper", "Study Material",
                                          "Notes", "Syllabus", "Worksheet", "Other"])
                    cls_s = st.selectbox("Class", list(c_opts.keys()))
                with c2:
                    desc = st.text_area("Description", height=68)
                    subj_s = st.selectbox("Subject", list(s_opts.keys()))
                    file = st.file_uploader("File *", type=[
                        "pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx",
                        "png", "jpg", "jpeg", "txt"])

                if st.form_submit_button("📤  Upload", type="primary",
                                         use_container_width=True):
                    try:
                        if not title.strip():
                            raise ValueError("Title required.")
                        if not file:
                            raise ValueError("Please choose a file.")
                        if file.size > 20 * 1024 * 1024:
                            raise ValueError("File must be under 20 MB.")
                        pid = save_paper(title, desc, c_opts[cls_s],
                                         s_opts[subj_s], ptype, file, user["id"])
                        log_action(user, "CREATE", "paper", pid, title)
                        st.success(f"✅ Uploaded '{file.name}'.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ {e}")

    st.markdown("---")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: search = st.text_input("🔍  Search papers",
                                     placeholder="Title or description")
    with c2: f_cls = st.selectbox("Class", list(c_opts.keys()))
    with c3: f_sub = st.selectbox("Subject", list(s_opts.keys()))

    df = list_papers(c_opts[f_cls], s_opts[f_sub], search)
    if df.empty:
        empty_state("📄", "No papers or material yet")
        return

    st.markdown(f"**{len(df)} files**")
    for _, row in df.iterrows():
        size_kb = (row["file_size"] or 0) / 1024
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 1, 1])
            with c1:
                st.markdown(
                    f"**{row['title']}** {pill(row['paper_type'], 'blue')}  \n"
                    f"<span style='color:#64748b;font-size:0.85rem'>"
                    f"{row['class'] or '—'} · {row['subject'] or '—'} · "
                    f"{size_kb:.0f} KB · {row['uploaded_at'][:10]}</span>",
                    unsafe_allow_html=True)
                if row["description"]:
                    st.caption(row["description"])
            with c2:
                if os.path.exists(row["file_path"]):
                    with open(row["file_path"], "rb") as f:
                        st.download_button(
                            "⬇️  Download", f.read(),
                            file_name=row["original_name"] or row["title"],
                            key=f"dl_{row['id']}", use_container_width=True)
            with c3:
                if user["role"] == "admin":
                    if st.button("🗑️  Delete", key=f"dp_{row['id']}",
                                 use_container_width=True):
                        delete_paper(row["id"])
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  TIMETABLE
# ═══════════════════════════════════════════════════════════════════
def page_timetable(user):
    page_header("Timetable", "Weekly schedule", "🗓️",
                crumbs=["Home", "Timetable"])

    if user["role"] == "teacher" and user["linked_id"]:
        df = teacher_timetable(user["linked_id"])
        if df.empty:
            empty_state("🗓️", "No periods scheduled for you")
        else:
            pivot = df.pivot_table(index="period", columns="day",
                                   values="class", aggfunc="first",
                                   fill_value="—")
            ordered_cols = [d for d in DAYS if d in pivot.columns]
            st.dataframe(pivot[ordered_cols], use_container_width=True)
        return

    classes = list_classes()
    subjects = list_subjects()
    teachers = list_teachers()
    if classes.empty or subjects.empty:
        empty_state("📅", "Setup required", "Add a class and subject first.")
        return

    c_opts = {f"{r['name']}" + (f" - {r['section']}" if r["section"] else ""): r["id"]
              for _, r in classes.iterrows()}
    s_opts = {r["name"]: r["id"] for _, r in subjects.iterrows()}
    t_opts = {"—": None}
    if not teachers.empty:
        t_opts.update({r["name"]: r["id"] for _, r in teachers.iterrows()})

    cls = st.selectbox("Class", list(c_opts.keys()))

    with st.expander("➕  Add / Update Period", expanded=False):
        with st.form("tt_form"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: day = st.selectbox("Day", DAYS)
            with c2: period = st.selectbox("Period", PERIODS)
            with c3: subj = st.selectbox("Subject", list(s_opts.keys()))
            with c4: teacher = st.selectbox("Teacher", list(t_opts.keys()))
            if st.form_submit_button("💾  Save", type="primary",
                                     use_container_width=True):
                save_period(c_opts[cls], day, period, s_opts[subj],
                            t_opts[teacher])
                st.success("✅ Saved.")
                st.rerun()

    df = class_timetable(c_opts[cls])
    if df.empty:
        empty_state("🗓️", "No periods scheduled")
    else:
        pivot = df.pivot_table(index="period", columns="day", values="subject",
                               aggfunc="first", fill_value="—")
        ordered_cols = [d for d in DAYS if d in pivot.columns]
        st.dataframe(pivot[ordered_cols], use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
#  ANNOUNCEMENTS
# ═══════════════════════════════════════════════════════════════════
def page_announcements(user):
    page_header("Announcements", "School-wide notices", "📢",
                crumbs=["Home", "Announcements"])

    if user["role"] in ("admin", "teacher"):
        with st.expander("➕  Post Announcement", expanded=False):
            with st.form("ann_form", clear_on_submit=True):
                title = st.text_input("Title *", placeholder="Annual Day on 15th Dec")
                body = st.text_area("Message *", height=100,
                                    placeholder="Details...")
                c1, c2 = st.columns(2)
                with c1:
                    prio = st.selectbox("Priority",
                                        ["Normal", "Important", "Urgent"])
                with c2:
                    aud = st.selectbox("Audience",
                                       ["All", "Students", "Teachers", "Parents"])
                if st.form_submit_button("📢  Post", type="primary",
                                         use_container_width=True):
                    if title and body:
                        post_announcement(title, body, prio, aud,
                                          user["full_name"])
                        st.success("✅ Posted.")
                        st.rerun()
                    else:
                        st.error("Title and message required.")

    df = list_announcements(50)
    if df.empty:
        empty_state("📢", "No announcements yet")
        return

    for _, row in df.iterrows():
        st.markdown(
            f'''<div style="background:#ffffff;border:1px solid #e2e8f0;
                border-left:4px solid #0ea5e9;border-radius:10px;
                padding:1rem 1.2rem;margin-bottom:0.8rem">
            <div style="display:flex;justify-content:space-between;
                        align-items:start;gap:1rem">
              <div style="font-weight:700;font-size:1.05rem;color:#0f172a">
                {row["title"]}</div>
              {status_pill(row["priority"])}
            </div>
            <div style="color:#475569;margin-top:0.5rem;font-size:0.92rem">
              {row["body"]}</div>
            <div style="color:#94a3b8;font-size:0.75rem;margin-top:0.6rem">
              📌 {row["audience"]} · {row["posted_by"] or "—"} · {row["posted_at"]}
            </div></div>''', unsafe_allow_html=True)
        if user["role"] == "admin":
            if st.button(f"🗑️ Delete #{row['id']}", key=f"dann_{row['id']}"):
                delete_announcement(row["id"])
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  AUDIT LOG
# ═══════════════════════════════════════════════════════════════════
def page_audit(user):
    page_header("Audit Log", "All system activity", "🧾",
                crumbs=["Home", "Audit Log"])
    df = _df("SELECT * FROM audit_log ORDER BY id DESC LIMIT 300")
    if df.empty:
        empty_state("🧾", "No activity yet")
        return
    st.dataframe(df[["ts", "username", "action", "entity", "entity_id", "detail"]],
                 use_container_width=True, hide_index=True)
    download_csv(df, "audit_log")


# ═══════════════════════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════════════════════
def page_settings(user):
    page_header("Settings", "System administration", "⚙️",
                crumbs=["Home", "Settings"])

    tab1, tab2, tab3 = st.tabs(["🔑 Password", "💾 Backup", "👥 Users"])

    with tab1:
        with st.form("chg_pw"):
            old = st.text_input("Current password", type="password")
            new = st.text_input("New password", type="password")
            conf = st.text_input("Confirm new password", type="password")
            if st.form_submit_button("🔑  Update Password", type="primary"):
                with get_conn() as c:
                    r = c.execute("SELECT password_hash FROM users WHERE id=?",
                                  (user["id"],)).fetchone()
                if not verify_pw(old, r["password_hash"]):
                    st.error("Current password incorrect.")
                elif new != conf:
                    st.error("Passwords don't match.")
                elif len(new) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    with get_conn() as c:
                        c.execute("UPDATE users SET password_hash=? WHERE id=?",
                                  (hash_pw(new), user["id"]))
                    log_action(user, "UPDATE", "user", user["id"], "Password changed")
                    st.success("✅ Updated. Please sign in again.")
                    st.session_state.user = None
                    st.rerun()

    with tab2:
        st.markdown("### 💾 Backup Database")
        if st.button("📦  Create Backup", type="primary"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = BACKUP_DIR / f"school_{ts}.db"
            shutil.copy(DB_PATH, dst)
            log_action(user, "BACKUP", "db", None, dst.name)
            st.success(f"✅ Backup created: `{dst.name}`")

        st.markdown("### Recent Backups")
        backups = sorted(BACKUP_DIR.glob("school_*.db"), reverse=True)
        if backups:
            for b in backups[:10]:
                st.markdown(f"- `{b.name}` — {b.stat().st_size / 1024:.1f} KB")
        else:
            st.info("No backups yet.")

    with tab3:
        st.markdown("### 👥 All Users")
        with get_conn() as c:
            udf = pd.read_sql_query(
                "SELECT id, username, role, full_name, email, phone, "
                "is_active, last_login FROM users ORDER BY id", c)
        st.dataframe(udf, use_container_width=True, hide_index=True)
        download_csv(udf, "users")

        st.markdown("### ➕ Create User")
        with st.form("new_user", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                u = st.text_input("Username *")
                p = st.text_input("Password *", type="password")
            with c2:
                fn = st.text_input("Full Name *")
                r = st.selectbox("Role", ["admin", "student"])
            if st.form_submit_button("➕  Create", type="primary",
                                     use_container_width=True):
                try:
                    if not u or not p or not fn:
                        raise ValueError("All fields required.")
                    uid = create_user(u, p, r, fn)
                    if uid:
                        st.success(f"✅ User '{u}' created.")
                        st.rerun()
                    else:
                        st.error("Username exists.")
                except Exception as e:
                    st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════════════
def render_sidebar(user):
    with st.sidebar:
        st.markdown(
            f'''<div style="padding:0.4rem 0 1rem;
                border-bottom:1px solid rgba(255,255,255,0.1);
                margin-bottom:1rem">
            <div style="font-size:1.4rem;font-weight:800;color:#38bdf8 !important">
              🏫 {APP_NAME}</div>
            <div style="font-size:0.72rem;color:#94a3b8 !important">
              {APP_TAGLINE}</div>
            </div>''', unsafe_allow_html=True)

        st.markdown(
            f'''<div style="display:flex;align-items:center;gap:0.75rem;
                padding:0.6rem;background:rgba(56,189,248,0.12);
                border-radius:8px;margin-bottom:1rem">
            <div style="width:38px;height:38px;border-radius:50%;
                background:linear-gradient(135deg,#0ea5e9,#8b5cf6);
                display:flex;align-items:center;justify-content:center;
                font-weight:700;color:white !important">
              {user["full_name"][0].upper()}</div>
            <div>
              <div style="font-weight:600;font-size:0.9rem;
                          color:#f1f5f9 !important">{user["full_name"]}</div>
              <div style="font-size:0.72rem;color:#94a3b8 !important;
                          text-transform:capitalize">{user["role"]}</div>
            </div></div>''', unsafe_allow_html=True)

        menu = ROLE_MENUS.get(user["role"], [])
        labels = [f"{icon}  {lbl}" for lbl, icon in menu]

        if "menu" not in st.session_state or st.session_state.menu not in labels:
            st.session_state.menu = labels[0]

        st.session_state.menu = st.radio("Navigation", labels,
                                         index=labels.index(st.session_state.menu),
                                         label_visibility="collapsed")

        st.markdown("---")
        if st.button("🚪  Sign Out", use_container_width=True):
            log_action(user, "LOGOUT", "user", user["id"])
            st.session_state.clear()
            st.rerun()
        st.caption(f"v{APP_VERSION} · {SCHOOL_NAME}")


PAGES = {
    "Dashboard": page_dashboard,
    "Teachers": page_teachers,
    "Students": page_students,
    "Classes": page_classes,
    "Subjects": page_subjects,
    "Attendance": page_attendance,
    "Examinations": page_examinations,
    "Fee Collection": page_fee_collection,
    "Papers & Material": page_papers,
    "Timetable": page_timetable,
    "Announcements": page_announcements,
    "Audit Log": page_audit,
    "Settings": page_settings,
    "My Students": page_students,
    "My Marks": page_examinations,
    "Fees & Receipts": page_fee_collection,
    "Study Material": page_papers,
}


def main():
    if not st.session_state.user:
        login_screen()
        return

    user = st.session_state.user
    render_sidebar(user)

    choice = st.session_state.menu.split("  ", 1)[1]
    fn = PAGES.get(choice)
    if fn:
        fn(user)
    else:
        st.error(f"Page '{choice}' not found.")


if __name__ == "__main__":
    main()