"""
Generate Entity-Relationship diagram for the School Management System.
Run: python docs/er_diagram.py
Requires: pip install graphviz
"""

import os, sys, subprocess

# Ensure we're in the project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Find Graphviz binary
dot_path = None
possible_paths = [
    r"C:\Program Files\Graphviz\bin\dot.exe",
    r"C:\Program Files (x86)\Graphviz\bin\dot.exe",
]
for p in possible_paths:
    if os.path.exists(p):
        dot_path = p
        break

if dot_path:
    os.environ["PATH"] = os.path.dirname(dot_path) + os.pathsep + os.environ.get("PATH", "")
    print(f"Using Graphviz: {dot_path}")

from graphviz import Digraph
from graphviz import ENGINES

dot = Digraph(
    "SMS_ER_Diagram",
    comment="School Management System - Entity Relationship Diagram",
    format="png",
    engine="dot",
)

dot.attr(
    rankdir="LR",
    splines="ortho",
    nodesep="0.5",
    ranksep="1.2",
    fontname="Helvetica",
    fontsize="12",
    bgcolor="#1a1a2e",
    label="School Management System — Entity Relationship Diagram",
    labelloc="t",
    labeljust="c",
    fontcolor="white",
    pad="0.5",
    dpi="150",
)

# ── Color Palette ──────────────────────────────────────────────────────────
COLORS = {
    "core": "#0f3460",        # Dark blue - auth/core
    "students": "#16213e",    # Navy - student module
    "academics": "#1a1a2e",   # Dark - academics
    "gradebook": "#0d7377",   # Teal - gradebook
    "fees": "#2d6a4f",        # Green - fees
    "attendance": "#5a189a",  # Purple - attendance
    "timetable": "#e07a5f",   # Coral - timetable
    "hr": "#3d405b",          # Slate - hr
    "communication": "#81b29a",  # Sage - communication
    "transport": "#e63946",   # Red - transport
    "inventory": "#f4a261",   # Orange - inventory
    "hostel": "#264653",      # Dark green - hostel
    "sports": "#2a9d8f",      # Teal green - sports
    "health": "#e76f51",      # Burnt orange - health
    "library": "#9c89b8",     # Purple - library
    "conferences": "#b56576", # Rose - conferences
    "behavior": "#6c584c",    # Brown - behavior
    "admissions": "#1d3557",  # Navy - admissions
    "alumni": "#457b9d",      # Steel blue - alumni
    "cafeteria": "#e0afa0",   # Peach - cafeteria
    "reporting": "#588157",   # Green - reporting
}

# Node styles
dot.attr("node", shape="record", style="filled,rounded", fontname="Helvetica", fontsize="10")

# ─── Clusters (grouped by service) ────────────────────────────────────────

# 1. CORE / AUTH
with dot.subgraph(name="cluster_auth") as sub:
    sub.attr(label="Auth & Core", style="filled", fillcolor="#0f3460:20", fontcolor="white", color="#0f3460")
    sub.node("School", 'School|{code|subdomain|name|address|is_active|subscription_tier|l<logo>}', fillcolor="#0f3460", fontcolor="white")
    sub.node("User", '{User|{role|email|first_name|last_name|is_active<is_active>|email_verified|two_factor_enabled|l<school>}}', fillcolor="#16213e", fontcolor="white")
    sub.node("AuditLog", '{AuditLog|{action|resource_type|resource_id|ip_address|l<school> l<user>}}', fillcolor="#1a1a2e", fontcolor="white")
    sub.node("UserSession", '{UserSession|{refresh_token_jti|l<user>|device_info|is_active}}', fillcolor="#1a1a2e", fontcolor="white")
    sub.node("PasswordResetToken", '{PasswordResetToken|{token|l<user>|expires_at|used}}', fillcolor="#1a1a2e", fontcolor="white")
    sub.node("EmailVerificationToken", '{EmailVerificationToken|{token|l<user>|email|expires_at|used}}', fillcolor="#1a1a2e", fontcolor="white")
    sub.node("TwoFactorBackupCode", '{TwoFactorBackupCode|{hashed_code|l<user>|used}}', fillcolor="#1a1a2e", fontcolor="white")
    sub.edge("User", "UserSession", arrowhead="crow", label="1:N")
    sub.edge("User", "PasswordResetToken", arrowhead="crow", label="1:N")
    sub.edge("User", "EmailVerificationToken", arrowhead="crow", label="1:N")
    sub.edge("User", "TwoFactorBackupCode", arrowhead="crow", label="1:N")
    sub.edge("User", "AuditLog", arrowhead="crow", label="1:N")
    sub.edge("School", "User", arrowhead="crow", label="1:N")
    sub.edge("School", "AuditLog", arrowhead="crow", label="1:N")

# 2. STUDENTS
with dot.subgraph(name="cluster_students") as sub:
    sub.attr(label="Students", style="filled", fillcolor="#16213e:20", fontcolor="white", color="#16213e")
    sub.node("AcademicYear", '{AcademicYear|{name|start_date|end_date|is_current|l<school>}}', fillcolor="#0d1b2a", fontcolor="white")
    sub.node("Grade", '{Grade|{name|level|l<school>}}', fillcolor="#1b263b", fontcolor="white")
    sub.node("Classroom", '{Classroom|{name|capacity|room_number|l<school> l<grade> l<academic_year> l<class_teacher>}}', fillcolor="#1b263b", fontcolor="white")
    sub.node("Student", '{Student|{admission_number|roll_number|date_of_birth|gender|l<school> l<user>|is_active}}', fillcolor="#0d1b2a", fontcolor="white")
    sub.node("Guardian", '{Guardian|{first_name|last_name|email|phone|l<user>|is_primary}}', fillcolor="#1b263b", fontcolor="white")
    sub.node("StudentGuardian", '{StudentGuardian|{l<student> l<guardian>|relationship|is_primary_contact|portal_access}}', fillcolor="#0d1b2a", fontcolor="white")
    sub.node("Enrollment", '{Enrollment|{l<student> l<classroom> l<academic_year>|status|is_active}}', fillcolor="#1b263b", fontcolor="white")
    sub.node("Document", '{Document|{l<student>|document_type|title|l<uploaded_by>}}', fillcolor="#0d1b2a", fontcolor="white")
    sub.edge("School", "AcademicYear", arrowhead="crow", label="1:N")
    sub.edge("School", "Grade", arrowhead="crow", label="1:N")
    sub.edge("School", "Classroom", arrowhead="crow", label="1:N")
    sub.edge("School", "Student", arrowhead="crow", label="1:N")
    sub.edge("Grade", "Classroom", arrowhead="crow", label="1:N")
    sub.edge("AcademicYear", "Classroom", arrowhead="crow", label="1:N")
    sub.edge("AcademicYear", "Enrollment", arrowhead="crow", label="1:N")
    sub.edge("User", "Student", arrowhead="odiamond", label="1:1")
    sub.edge("User", "Guardian", arrowhead="odiamond", label="1:1")
    sub.edge("User", "Classroom", arrowhead="crow", label="1:N", headlabel="(class_teacher)")
    sub.edge("Student", "Enrollment", arrowhead="crow", label="1:N")
    sub.edge("Classroom", "Enrollment", arrowhead="crow", label="1:N")
    sub.edge("Student", "StudentGuardian", arrowhead="crow", label="1:N")
    sub.edge("Guardian", "StudentGuardian", arrowhead="crow", label="1:N")
    sub.edge("Student", "Document", arrowhead="crow", label="1:N")

# 3. ACADEMICS
with dot.subgraph(name="cluster_academics") as sub:
    sub.attr(label="Academics", style="filled", fillcolor="#1a1a2e:20", fontcolor="white", color="#1a1a2e")
    sub.node("Subject", '{Subject|{name|code|is_core|is_elective|max_marks|l<school> l<grade>}}', fillcolor="#16213e", fontcolor="white")
    sub.node("TeacherAssignment", '{TeacherAssignment|{l<teacher> l<subject> l<classroom> l<academic_year>|is_primary}}', fillcolor="#1a1a2e", fontcolor="white")
    sub.node("TeacherProfile", '{TeacherProfile|{employee_id|qualification|specialization|department|l<user> l<school>}}', fillcolor="#16213e", fontcolor="white")
    sub.node("LessonPlan", '{LessonPlan|{title|topic|date|duration|status|l<assignment>}}', fillcolor="#1a1a2e", fontcolor="white")
    sub.edge("School", "Subject", arrowhead="crow", label="1:N")
    sub.edge("School", "TeacherProfile", arrowhead="crow", label="1:N")
    sub.edge("User", "TeacherProfile", arrowhead="odiamond", label="1:1")
    sub.edge("User", "TeacherAssignment", arrowhead="crow", label="1:N")
    sub.edge("Grade", "Subject", arrowhead="crow", label="1:N")
    sub.edge("Subject", "TeacherAssignment", arrowhead="crow", label="1:N")
    sub.edge("Classroom", "TeacherAssignment", arrowhead="crow", label="1:N")
    sub.edge("AcademicYear", "TeacherAssignment", arrowhead="crow", label="1:N")
    sub.edge("TeacherAssignment", "LessonPlan", arrowhead="crow", label="1:N")

# 4. ATTENDANCE
with dot.subgraph(name="cluster_attendance") as sub:
    sub.attr(label="Attendance", style="filled", fillcolor="#5a189a:20", fontcolor="white", color="#5a189a")
    sub.node("AttendanceRecord", '{AttendanceRecord|{l<student> l<classroom> l<academic_year>|date|status|l<recorded_by>}}', fillcolor="#3c096c", fontcolor="white")
    sub.node("PeriodAttendance", '{PeriodAttendance|{l<student> l<assignment>|date|period_number|status|l<recorded_by>}}', fillcolor="#5a189a", fontcolor="white")
    sub.node("AttendanceLeave", '{AttendanceLeave|{l<student>|leave_type|from_date|to_date|reason|status|l<reviewed_by>}}', fillcolor="#7b2cbf", fontcolor="white")
    sub.edge("Student", "AttendanceRecord", arrowhead="crow", label="1:N")
    sub.edge("Classroom", "AttendanceRecord", arrowhead="crow", label="1:N")
    sub.edge("AcademicYear", "AttendanceRecord", arrowhead="crow", label="1:N")
    sub.edge("Student", "PeriodAttendance", arrowhead="crow", label="1:N")
    sub.edge("TeacherAssignment", "PeriodAttendance", arrowhead="crow", label="1:N")
    sub.edge("Student", "AttendanceLeave", arrowhead="crow", label="1:N")

# 5. GRADEBOOK
with dot.subgraph(name="cluster_gradebook") as sub:
    sub.attr(label="Gradebook", style="filled", fillcolor="#0d7377:20", fontcolor="white", color="#0d7377")
    sub.node("GradingScale", '{GradingScale|{name|l<school>|is_default}}', fillcolor="#0d7377", fontcolor="white")
    sub.node("GradingScaleEntry", '{GradingScaleEntry|{grade_letter|min_percentage|max_percentage|grade_point|l<scale>}}', fillcolor="#14919b", fontcolor="white")
    sub.node("ExamType", '{ExamType|{name|weightage|is_terminal|l<school>}}', fillcolor="#0d7377", fontcolor="white")
    sub.node("Exam", '{Exam|{name|start_date|end_date|status|l<school> l<academic_year> l<exam_type> l<created_by>}}', fillcolor="#14919b", fontcolor="white")
    sub.node("ExamSchedule", '{ExamSchedule|{date|start_time|end_time|venue|max_marks|l<exam> l<subject> l<classroom> l<invigilator>}}', fillcolor="#0d7377", fontcolor="white")
    sub.node("Grade", '{Grade|{l<student> l<exam_schedule>|marks_obtained|is_absent|is_pass|l<graded_by>}}', fillcolor="#14919b", fontcolor="white")
    sub.node("Assessment", '{Assessment|{title|assessment_type|due_date|max_marks|l<assignment>}}', fillcolor="#0d7377", fontcolor="white")
    sub.node("AssessmentSubmission", '{AssessmentSubmission|{l<assessment> l<student>|marks_obtained|submitted_at|file|is_late}}', fillcolor="#14919b", fontcolor="white")
    sub.node("ReportCard", '{ReportCard|{l<student> l<exam> l<academic_year>|percentage|gpa|rank_in_class|status}}', fillcolor="#0d7377", fontcolor="white")
    sub.edge("School", "GradingScale", arrowhead="crow", label="1:N")
    sub.edge("School", "ExamType", arrowhead="crow", label="1:N")
    sub.edge("School", "Exam", arrowhead="crow", label="1:N")
    sub.edge("GradingScale", "GradingScaleEntry", arrowhead="crow", label="1:N")
    sub.edge("AcademicYear", "Exam", arrowhead="crow", label="1:N")
    sub.edge("ExamType", "Exam", arrowhead="crow", label="1:N")
    sub.edge("Exam", "ExamSchedule", arrowhead="crow", label="1:N")
    sub.edge("Subject", "ExamSchedule", arrowhead="crow", label="1:N")
    sub.edge("Classroom", "ExamSchedule", arrowhead="crow", label="1:N")
    sub.edge("ExamSchedule", "Grade", arrowhead="crow", label="1:N")
    sub.edge("Student", "Grade", arrowhead="crow", label="1:N")
    sub.edge("TeacherAssignment", "Assessment", arrowhead="crow", label="1:N")
    sub.edge("Assessment", "AssessmentSubmission", arrowhead="crow", label="1:N")
    sub.edge("Student", "AssessmentSubmission", arrowhead="crow", label="1:N")
    sub.edge("Student", "ReportCard", arrowhead="crow", label="1:N")
    sub.edge("Exam", "ReportCard", arrowhead="crow", label="1:N")

# 6. FEES
with dot.subgraph(name="cluster_fees") as sub:
    sub.attr(label="Fees", style="filled", fillcolor="#2d6a4f:20", fontcolor="white", color="#2d6a4f")
    sub.node("FeeCategory", '{FeeCategory|{name|is_mandatory|recurrence|l<school>}}', fillcolor="#1b4332", fontcolor="white")
    sub.node("FeeStructure", '{FeeStructure|{amount|due_day|late_fee_per_day|l<school> l<academic_year> l<grade> l<fee_category>}}', fillcolor="#2d6a4f", fontcolor="white")
    sub.node("FeeInvoice", '{FeeInvoice|{invoice_number|l<student> l<academic_year> l<fee_structure>|due_date|base_amount|total_amount|paid_amount|status|l<created_by>}}', fillcolor="#40916c", fontcolor="white")
    sub.node("Payment", '{Payment|{amount|payment_method|status|transaction_id|receipt_number|l<invoice> l<collected_by>}}', fillcolor="#52b788", fontcolor="white")
    sub.node("Scholarship", '{Scholarship|{name|discount_type|discount_value|l<school> l<student> l<academic_year>|reason|l<approved_by>}}', fillcolor="#2d6a4f", fontcolor="white")
    sub.node("PaymentGatewayConfig", '{PaymentGatewayConfig|{l<school>|stripe_enabled|khalti_enabled|esewa_enabled}}', fillcolor="#40916c", fontcolor="white")
    sub.edge("School", "FeeCategory", arrowhead="crow", label="1:N")
    sub.edge("School", "FeeStructure", arrowhead="crow", label="1:N")
    sub.edge("School", "Scholarship", arrowhead="crow", label="1:N")
    sub.edge("School", "PaymentGatewayConfig", arrowhead="odiamond", label="1:1")
    sub.edge("AcademicYear", "FeeStructure", arrowhead="crow", label="1:N")
    sub.edge("AcademicYear", "FeeInvoice", arrowhead="crow", label="1:N")
    sub.edge("AcademicYear", "Scholarship", arrowhead="crow", label="1:N")
    sub.edge("Grade", "FeeStructure", arrowhead="crow", label="1:N")
    sub.edge("FeeCategory", "FeeStructure", arrowhead="crow", label="1:N")
    sub.edge("FeeCategory", "Scholarship", arrowhead="crow", label="M:N")
    sub.edge("FeeStructure", "FeeInvoice", arrowhead="crow", label="1:N")
    sub.edge("Student", "FeeInvoice", arrowhead="crow", label="1:N")
    sub.edge("Student", "Scholarship", arrowhead="crow", label="1:N")
    sub.edge("FeeInvoice", "Payment", arrowhead="crow", label="1:N")

# 7. TIMETABLE
with dot.subgraph(name="cluster_timetable") as sub:
    sub.attr(label="Timetable", style="filled", fillcolor="#e07a5f:20", fontcolor="white", color="#e07a5f")
    sub.node("Period", '{Period|{name|period_number|start_time|end_time|is_break|l<school>}}', fillcolor="#e07a5f", fontcolor="white")
    sub.node("TimetableSlot", '{TimetableSlot|{day_of_week|l<classroom> l<period> l<subject> l<teacher> l<academic_year>}}', fillcolor="#f4a261", fontcolor="white")
    sub.node("SchoolEvent", '{SchoolEvent|{title|description|start_datetime|end_datetime|event_type|l<school>}}', fillcolor="#e07a5f", fontcolor="white")
    sub.edge("School", "Period", arrowhead="crow", label="1:N")
    sub.edge("School", "SchoolEvent", arrowhead="crow", label="1:N")
    sub.edge("Classroom", "TimetableSlot", arrowhead="crow", label="1:N")
    sub.edge("Period", "TimetableSlot", arrowhead="crow", label="1:N")
    sub.edge("Subject", "TimetableSlot", arrowhead="crow", label="1:N")
    sub.edge("User", "TimetableSlot", arrowhead="crow", label="1:N")

# 8. COMMUNICATION
with dot.subgraph(name="cluster_communication") as sub:
    sub.attr(label="Communication", style="filled", fillcolor="#81b29a:20", fontcolor="white", color="#81b29a")
    sub.node("Announcement", '{Announcement|{title|content|priority|audience|is_draft|l<school> l<created_by>}}', fillcolor="#6a994e", fontcolor="white")
    sub.node("AnnouncementRead", '{AnnouncementRead|{l<announcement> l<user>|read_at}}', fillcolor="#81b29a", fontcolor="white")
    sub.node("DirectMessage", '{DirectMessage|{subject|body|l<sender> l<recipient>|read_at}}', fillcolor="#a7c957", fontcolor="white")
    sub.node("NotificationTemplate", '{NotificationTemplate|{event_type|email_subject|email_body|l<school>|is_active}}', fillcolor="#6a994e", fontcolor="white")
    sub.node("Notification", '{Notification|{title|body|notification_type|l<user>|is_read}}', fillcolor="#81b29a", fontcolor="white")
    sub.node("DeviceToken", '{DeviceToken|{token|device_type|l<user>|is_active}}', fillcolor="#a7c957", fontcolor="white")
    sub.edge("School", "Announcement", arrowhead="crow", label="1:N")
    sub.edge("School", "NotificationTemplate", arrowhead="crow", label="1:N")
    sub.edge("User", "Announcement", arrowhead="crow", label="1:N")
    sub.edge("User", "DirectMessage", arrowhead="crow", label="1:N")
    sub.edge("User", "DirectMessage", arrowhead="crow", label="1:N", headlabel="(recipient)")
    sub.edge("User", "Notification", arrowhead="crow", label="1:N")
    sub.edge("User", "DeviceToken", arrowhead="crow", label="1:N")
    sub.edge("Announcement", "AnnouncementRead", arrowhead="crow", label="1:N")
    sub.edge("User", "AnnouncementRead", arrowhead="crow", label="1:N")

# 9. HR
with dot.subgraph(name="cluster_hr") as sub:
    sub.attr(label="HR & Payroll", style="filled", fillcolor="#3d405b:20", fontcolor="white", color="#3d405b")
    sub.node("Department", '{Department|{name|code|description|head_of_dept|l<school>}}', fillcolor="#3d405b", fontcolor="white")
    sub.node("Employee", '{Employee|{employee_id|designation|department|joining_date|l<user> l<school>}}', fillcolor="#5c5f7e", fontcolor="white")
    sub.node("SalaryStructure", '{SalaryStructure|{title|basic_pay|allowances|deductions|l<school> l<department>}}', fillcolor="#3d405b", fontcolor="white")
    sub.node("EmployeeSalary", '{EmployeeSalary|{l<employee> l<salary_structure>|effective_from|is_active}}', fillcolor="#5c5f7e", fontcolor="white")
    sub.node("Payslip", '{Payslip|{month|year|gross_pay|net_pay|deductions|l<employee_salary>}}', fillcolor="#3d405b", fontcolor="white")
    sub.node("LeaveRequest", '{LeaveRequest|{leave_type|from_date|to_date|reason|status|l<employee> l<approved_by>}}', fillcolor="#5c5f7e", fontcolor="white")
    sub.edge("School", "Department", arrowhead="crow", label="1:N")
    sub.edge("School", "Employee", arrowhead="crow", label="1:N")
    sub.edge("School", "SalaryStructure", arrowhead="crow", label="1:N")
    sub.edge("User", "Employee", arrowhead="odiamond", label="1:1")
    sub.edge("Department", "SalaryStructure", arrowhead="crow", label="1:N")
    sub.edge("Employee", "EmployeeSalary", arrowhead="crow", label="1:N")
    sub.edge("SalaryStructure", "EmployeeSalary", arrowhead="crow", label="1:N")
    sub.edge("EmployeeSalary", "Payslip", arrowhead="crow", label="1:N")
    sub.edge("Employee", "LeaveRequest", arrowhead="crow", label="1:N")

# 10. TRANSPORT
with dot.subgraph(name="cluster_transport") as sub:
    sub.attr(label="Transportation", style="filled", fillcolor="#e63946:20", fontcolor="white", color="#e63946")
    sub.node("Vehicle", '{Vehicle|{registration_number|type|capacity|make|model|year|l<school>}}', fillcolor="#e63946", fontcolor="white")
    sub.node("Driver", '{Driver|{license_number|phone|emergency_contact|l<user> l<school>}}', fillcolor="#f4a261", fontcolor="white")
    sub.node("Route", '{Route|{name|start_point|end_point|distance|fare_amount|l<school>}}', fillcolor="#e63946", fontcolor="white")
    sub.node("RouteStop", '{RouteStop|{name|stop_order|latitude|longitude|l<route>}}', fillcolor="#f4a261", fontcolor="white")
    sub.node("StudentRoute", '{StudentRoute|{pickup_stop|dropoff_stop|fare|is_active|l<student> l<route> l<academic_year>}}', fillcolor="#e63946", fontcolor="white")
    sub.node("VehicleMaintenance", '{VehicleMaintenance|{maintenance_type|description|cost|service_date|next_service_date|l<vehicle>}}', fillcolor="#f4a261", fontcolor="white")
    sub.edge("School", "Vehicle", arrowhead="crow", label="1:N")
    sub.edge("School", "Driver", arrowhead="crow", label="1:N")
    sub.edge("School", "Route", arrowhead="crow", label="1:N")
    sub.edge("Route", "RouteStop", arrowhead="crow", label="1:N")
    sub.edge("Route", "StudentRoute", arrowhead="crow", label="1:N")
    sub.edge("Student", "StudentRoute", arrowhead="crow", label="1:N")
    sub.edge("Vehicle", "VehicleMaintenance", arrowhead="crow", label="1:N")

# 11. INVENTORY
with dot.subgraph(name="cluster_inventory") as sub:
    sub.attr(label="Inventory", style="filled", fillcolor="#f4a261:20", fontcolor="white", color="#f4a261")
    sub.node("Category", '{Category|{name|description|l<school>}}', fillcolor="#e76f51", fontcolor="white")
    sub.node("Supplier", '{Supplier|{name|contact_person|email|phone|address|l<school>}}', fillcolor="#f4a261", fontcolor="white")
    sub.node("InventoryItem", '{InventoryItem|{name|sku|quantity|unit_price|reorder_level|l<school> l<category>}}', fillcolor="#e76f51", fontcolor="white")
    sub.node("StockMovement", '{StockMovement|{quantity|movement_type|reference|notes|l<item> l<created_by>}}', fillcolor="#f4a261", fontcolor="white")
    sub.node("PurchaseOrder", '{PurchaseOrder|{order_number|status|total_amount|l<supplier> l<created_by>}}', fillcolor="#e76f51", fontcolor="white")
    sub.node("PurchaseOrderItem", '{PurchaseOrderItem|{quantity|unit_price|total_price|l<purchase_order> l<item>}}', fillcolor="#f4a261", fontcolor="white")
    sub.edge("School", "Category", arrowhead="crow", label="1:N")
    sub.edge("School", "Supplier", arrowhead="crow", label="1:N")
    sub.edge("School", "InventoryItem", arrowhead="crow", label="1:N")
    sub.edge("Category", "InventoryItem", arrowhead="crow", label="1:N")
    sub.edge("InventoryItem", "StockMovement", arrowhead="crow", label="1:N")
    sub.edge("Supplier", "PurchaseOrder", arrowhead="crow", label="1:N")
    sub.edge("PurchaseOrder", "PurchaseOrderItem", arrowhead="crow", label="1:N")
    sub.edge("InventoryItem", "PurchaseOrderItem", arrowhead="crow", label="1:N")

# 12. HOSTEL
with dot.subgraph(name="cluster_hostel") as sub:
    sub.attr(label="Hostel", style="filled", fillcolor="#264653:20", fontcolor="white", color="#264653")
    sub.node("Hostel", '{Hostel|{name|type|warden_name|phone|l<school>}}', fillcolor="#264653", fontcolor="white")
    sub.node("HostelRoom", '{HostelRoom|{room_number|capacity|occupied|fee_per_bed|l<hostel>}}', fillcolor="#2a9d8f", fontcolor="white")
    sub.node("HostelAllocation", '{HostelAllocation|{l<room> l<student> l<academic_year>|check_in|check_out|is_active}}', fillcolor="#264653", fontcolor="white")
    sub.node("HostelFee", '{HostelFee|{fee_type|amount|due_date|l<allocation>|paid}}', fillcolor="#2a9d8f", fontcolor="white")
    sub.node("HostelVisitor", '{HostelVisitor|{visitor_name|relationship|visit_date|in_time|out_time|l<allocation>}}', fillcolor="#264653", fontcolor="white")
    sub.edge("School", "Hostel", arrowhead="crow", label="1:N")
    sub.edge("Hostel", "HostelRoom", arrowhead="crow", label="1:N")
    sub.edge("HostelRoom", "HostelAllocation", arrowhead="crow", label="1:N")
    sub.edge("Student", "HostelAllocation", arrowhead="crow", label="1:N")
    sub.edge("AcademicYear", "HostelAllocation", arrowhead="crow", label="1:N")
    sub.edge("HostelAllocation", "HostelFee", arrowhead="crow", label="1:N")
    sub.edge("HostelAllocation", "HostelVisitor", arrowhead="crow", label="1:N")

# 13. SPORTS
with dot.subgraph(name="cluster_sports") as sub:
    sub.attr(label="Sports", style="filled", fillcolor="#2a9d8f:20", fontcolor="white", color="#2a9d8f")
    sub.node("Sport", '{Sport|{name|equipment_required|l<school>}}', fillcolor="#2a9d8f", fontcolor="white")
    sub.node("Team", '{Team|{name|age_group|gender|l<sport> l<coach> l<school>}}', fillcolor="#3dbca8", fontcolor="white")
    sub.node("TeamMember", '{TeamMember|{role|status|l<team> l<student>}}', fillcolor="#2a9d8f", fontcolor="white")
    sub.node("SportEvent", '{SportEvent|{name|event_type|location|start_date|end_date|l<team> l<school>}}', fillcolor="#3dbca8", fontcolor="white")
    sub.node("SportAchievement", '{SportAchievement|{achievement_type|title|rank|date|description|l<team> l<student> l<school>}}', fillcolor="#2a9d8f", fontcolor="white")
    sub.edge("School", "Sport", arrowhead="crow", label="1:N")
    sub.edge("School", "Team", arrowhead="crow", label="1:N")
    sub.edge("Sport", "Team", arrowhead="crow", label="1:N")
    sub.edge("Team", "TeamMember", arrowhead="crow", label="1:N")
    sub.edge("Student", "TeamMember", arrowhead="crow", label="1:N")
    sub.edge("Team", "SportEvent", arrowhead="crow", label="1:N")
    sub.edge("Team", "SportAchievement", arrowhead="crow", label="1:N")
    sub.edge("Student", "SportAchievement", arrowhead="crow", label="1:N")

# 14. HEALTH
with dot.subgraph(name="cluster_health") as sub:
    sub.attr(label="Health Clinic", style="filled", fillcolor="#e76f51:20", fontcolor="white", color="#e76f51")
    sub.node("HealthRecord", '{HealthRecord|{blood_group|allergies|chronic_conditions|emergency_contact|l<student> l<school>}}', fillcolor="#e76f51", fontcolor="white")
    sub.node("NurseVisit", '{NurseVisit|{symptoms|diagnosis|treatment|medication|follow_up_date|l<student> l<record> l<attended_by>}}', fillcolor="#f4a261", fontcolor="white")
    sub.node("Immunization", '{Immunization|{vaccine_name|date_given|dose_number|next_due_date|l<student> l<record>}}', fillcolor="#e76f51", fontcolor="white")
    sub.node("MedicationLog", '{MedicationLog|{medication_name|dosage|frequency|start_date|end_date|l<student> l<record>}}', fillcolor="#f4a261", fontcolor="white")
    sub.edge("Student", "HealthRecord", arrowhead="odiamond", label="1:1")
    sub.edge("School", "HealthRecord", arrowhead="crow", label="1:N")
    sub.edge("HealthRecord", "NurseVisit", arrowhead="crow", label="1:N")
    sub.edge("HealthRecord", "Immunization", arrowhead="crow", label="1:N")
    sub.edge("HealthRecord", "MedicationLog", arrowhead="crow", label="1:N")
    sub.edge("Student", "NurseVisit", arrowhead="crow", label="1:N")

# 15. LIBRARY
with dot.subgraph(name="cluster_library") as sub:
    sub.attr(label="Library", style="filled", fillcolor="#9c89b8:20", fontcolor="white", color="#9c89b8")
    sub.node("Book", '{Book|{title|author|isbn|publisher|publish_year|total_copies|available_copies|l<school>}}', fillcolor="#9c89b8", fontcolor="white")
    sub.node("Checkout", '{Checkout|{l<book> l<student>|checked_out|due_date|returned_date|status|l<issued_by>}}', fillcolor="#b8a9c9", fontcolor="white")
    sub.edge("School", "Book", arrowhead="crow", label="1:N")
    sub.edge("Book", "Checkout", arrowhead="crow", label="1:N")
    sub.edge("Student", "Checkout", arrowhead="crow", label="1:N")

# 16. CONFERENCES
with dot.subgraph(name="cluster_conferences") as sub:
    sub.attr(label="Conferences", style="filled", fillcolor="#b56576:20", fontcolor="white", color="#b56576")
    sub.node("ConferenceSlot", '{ConferenceSlot|{l<teacher> l<student>|date|start_time|end_time|status|mode|l<booked_by>}}', fillcolor="#b56576", fontcolor="white")
    sub.edge("User", "ConferenceSlot", arrowhead="crow", label="1:N", headlabel="(teacher)")
    sub.edge("Student", "ConferenceSlot", arrowhead="crow", label="1:N")

# 17. BEHAVIOR
with dot.subgraph(name="cluster_behavior") as sub:
    sub.attr(label="Behavior", style="filled", fillcolor="#6c584c:20", fontcolor="white", color="#6c584c")
    sub.node("Incident", '{Incident|{incident_type|description|date|location|severity|action_taken|l<student> l<reported_by> l<school>}}', fillcolor="#6c584c", fontcolor="white")
    sub.node("Referral", '{Referral|{reason|referral_type|notes|status|l<student> l<referred_by> l<school>}}', fillcolor="#8c7a6b", fontcolor="white")
    sub.edge("Student", "Incident", arrowhead="crow", label="1:N")
    sub.edge("School", "Incident", arrowhead="crow", label="1:N")
    sub.edge("Student", "Referral", arrowhead="crow", label="1:N")
    sub.edge("School", "Referral", arrowhead="crow", label="1:N")

# 18. ADMISSIONS
with dot.subgraph(name="cluster_admissions") as sub:
    sub.attr(label="Admissions", style="filled", fillcolor="#1d3557:20", fontcolor="white", color="#1d3557")
    sub.node("EnrollmentIntake", '{EnrollmentIntake|{name|start_date|end_date|capacity|is_open|l<school> l<grade> l<academic_year>}}', fillcolor="#1d3557", fontcolor="white")
    sub.node("Application", '{Application|{applicant_name|applicant_email|status|submitted_at|decision_date|l<intake> l<reviewed_by>}}', fillcolor="#457b9d", fontcolor="white")
    sub.node("ApplicationDocument", '{ApplicationDocument|{document_type|file|uploaded_at|l<application>}}', fillcolor="#1d3557", fontcolor="white")
    sub.node("ApplicationReview", '{ApplicationReview|{rating|comments|decision|l<application> l<reviewer>}}', fillcolor="#457b9d", fontcolor="white")
    sub.edge("School", "EnrollmentIntake", arrowhead="crow", label="1:N")
    sub.edge("EnrollmentIntake", "Application", arrowhead="crow", label="1:N")
    sub.edge("Application", "ApplicationDocument", arrowhead="crow", label="1:N")
    sub.edge("Application", "ApplicationReview", arrowhead="crow", label="1:N")

# 19. ALUMNI
with dot.subgraph(name="cluster_alumni") as sub:
    sub.attr(label="Alumni", style="filled", fillcolor="#457b9d:20", fontcolor="white", color="#457b9d")
    sub.node("AlumniProfile", '{AlumniProfile|{graduation_year|current_occupation|organization|l<user> l<school>}}', fillcolor="#457b9d", fontcolor="white")
    sub.node("AlumniEvent", '{AlumniEvent|{name|event_type|location|date|description|l<school>}}', fillcolor="#5c9cc9", fontcolor="white")
    sub.node("AlumniDonation", '{AlumniDonation|{amount|donation_type|date|payment_method|l<alumni> l<school>}}', fillcolor="#457b9d", fontcolor="white")
    sub.node("AlumniChapter", '{AlumniChapter|{name|city|country|description|l<school>}}', fillcolor="#5c9cc9", fontcolor="white")
    sub.edge("User", "AlumniProfile", arrowhead="odiamond", label="1:1")
    sub.edge("School", "AlumniProfile", arrowhead="crow", label="1:N")
    sub.edge("School", "AlumniEvent", arrowhead="crow", label="1:N")
    sub.edge("School", "AlumniDonation", arrowhead="crow", label="1:N")
    sub.edge("School", "AlumniChapter", arrowhead="crow", label="1:N")
    sub.edge("AlumniProfile", "AlumniDonation", arrowhead="crow", label="1:N")

# 20. CAFETERIA
with dot.subgraph(name="cluster_cafeteria") as sub:
    sub.attr(label="Cafeteria", style="filled", fillcolor="#e0afa0:20", fontcolor="white", color="#e0afa0")
    sub.node("MealMenu", '{MealMenu|{day_of_week|meal_type|main_item|side_item|price|l<school>}}', fillcolor="#d68c79", fontcolor="white")
    sub.node("MealPlan", '{MealPlan|{name|description|price_per_period|is_active|l<school>}}', fillcolor="#e0afa0", fontcolor="white")
    sub.node("MealBooking", '{MealBooking|{booking_date|meal_type|status|l<student> l<plan>}}', fillcolor="#d68c79", fontcolor="white")
    sub.node("DietaryRestriction", '{DietaryRestriction|{restriction_type|allergen|notes|l<student>}}', fillcolor="#e0afa0", fontcolor="white")
    sub.edge("School", "MealMenu", arrowhead="crow", label="1:N")
    sub.edge("School", "MealPlan", arrowhead="crow", label="1:N")
    sub.edge("Student", "MealBooking", arrowhead="crow", label="1:N")
    sub.edge("MealPlan", "MealBooking", arrowhead="crow", label="1:N")
    sub.edge("Student", "DietaryRestriction", arrowhead="crow", label="1:N")

# ── Cross-cluster relationships ──────────────────────────────────────────

# School → Everything (tenant isolation)
dot.edge("School", "Grade", arrowhead="crow", label="1:N", style="dashed")
dot.edge("School", "Subject", arrowhead="crow", label="1:N", style="dashed")
dot.edge("School", "AttendanceRecord", arrowhead="crow", label="1:N", style="dashed")

# User is the central hub across all services
dot.edge("User", "DirectMessage", arrowhead="crow", label="1:N", style="dashed")
dot.edge("User", "Notification", arrowhead="crow", label="1:N", style="dashed")
dot.edge("User", "ConferenceSlot", arrowhead="crow", label="1:N", style="dashed")
dot.edge("User", "Employee", arrowhead="odiamond", label="1:1", style="dashed")
dot.edge("User", "AlumniProfile", arrowhead="odiamond", label="1:1", style="dashed")

# Student is the second central hub
dot.edge("Student", "Checkout", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "Incident", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "Referral", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "MealBooking", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "DietaryRestriction", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "ConferenceSlot", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "StudentRoute", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "HostelAllocation", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "SportAchievement", arrowhead="crow", label="1:N", style="dashed")
dot.edge("Student", "TeamMember", arrowhead="crow", label="1:N", style="dashed")

# ── Render ────────────────────────────────────────────────────────────────
output_dir = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "sms_er_diagram")

print("Generating ER diagram...")
try:
    dot.render(output_path, cleanup=True)
    print(f"ER diagram generated: {output_path}.png")
except Exception as e:
    print(f"Could not render to PNG (Graphviz binary may not be in PATH): {e}")
    # Save the DOT source file at least
    dot.save(os.path.join(output_dir, "sms_er_diagram.dot"))
    print(f"DOT source saved: {output_dir}/sms_er_diagram.dot")
    print("   Install Graphviz system binary and run again:")
    print("   - macOS: brew install graphviz")
    print("   - Linux: apt-get install graphviz")
    print("   - Windows: winget install graphviz (then restart terminal)")
