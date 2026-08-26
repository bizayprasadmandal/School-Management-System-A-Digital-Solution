"""
Generate Combined HLD + LLD Diagram for EduSphere School Management System.

This diagram combines:
  - High-Level Design: System architecture, layers, components, external services
  - Low-Level Design: All 105 database tables, 166 relationships, 127 dependencies

Run: python docs/combined_hld_lld.py
Requires: pip install graphviz
"""

import os

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

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DIAGRAM — Combined HLD + LLD
# ═══════════════════════════════════════════════════════════════════════════════

dot = Digraph(
    "EduSphere_HLD_LLD",
    comment="EduSphere SMS — Combined High-Level & Low-Level Design",
    format="png",
    engine="dot",
)

dot.attr(
    rankdir="TB",
    splines="spline",
    nodesep="0.3",
    ranksep="0.8",
    fontname="Sans",
    fontsize="14",
    bgcolor="#0d1117",
    label=(
        "<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='4'>"
        "<TR><TD><FONT COLOR='white' POINT-SIZE='24'><B>EduSphere SMS — Combined HLD + LLD</B></FONT></TD></TR>"
        "<TR><TD><FONT COLOR='#8b949e' POINT-SIZE='12'>105 Tables · 166 Relationships · 127 Dependencies · 22 Service Modules</FONT></TD></TR>"
        "</TABLE>>"
    ),
    labelloc="t",
    labeljust="c",
    pad="0.5",
    dpi="150",
    margin="0.3",
)

# ── Global Node Styles ──────────────────────────────────────────────────────
dot.attr("node", fontname="Helvetica", fontsize="9")
dot.attr("edge", fontname="Helvetica", fontsize="8")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: CLIENT LAYER (HLD)
# ═══════════════════════════════════════════════════════════════════════════════

with dot.subgraph(name="cluster_client_layer") as sub:
    sub.attr(
        label="CLIENT LAYER",
        style="filled,rounded",
        fillcolor="#161b22",
        fontcolor="#58a6ff",
        color="#30363d",
        fontsize="14",
        fontname="Sans",
        penwidth="2",
    )

    # React Web
    with sub.subgraph(name="cluster_web") as web:
        web.attr(
            label="React Web (Vite + TS)",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="11",
            penwidth="1.5",
        )
        web.node(
            "web_react",
            "React 18\nreact-dom",
            shape="component",
            style="filled,rounded",
            fillcolor="#1f6feb",
            fontcolor="white",
        )
        web.node(
            "web_router",
            "react-router-dom\nv6",
            shape="box",
            style="filled,rounded",
            fillcolor="#238636",
            fontcolor="white",
        )
        web.node(
            "web_query",
            "@tanstack/react-query\nServer State",
            shape="box",
            style="filled,rounded",
            fillcolor="#8957e5",
            fontcolor="white",
        )
        web.node(
            "web_state",
            "zustand\nUI State",
            shape="box",
            style="filled,rounded",
            fillcolor="#da3633",
            fontcolor="white",
        )
        web.node(
            "web_forms",
            "react-hook-form + zod\nForm Validation",
            shape="box",
            style="filled,rounded",
            fillcolor="#f78166",
            fontcolor="white",
        )
        web.node(
            "web_http",
            "axios\nHTTP Client",
            shape="box",
            style="filled,rounded",
            fillcolor="#3fb950",
            fontcolor="white",
        )
        web.node(
            "web_i18n", "i18next\nEN / NE", shape="box", style="filled,rounded", fillcolor="#d2a8ff", fontcolor="white"
        )
        web.node(
            "web_ui",
            "tailwindcss + framer-motion\n@heroicons/react + clsx",
            shape="box",
            style="filled,rounded",
            fillcolor="#56d364",
            fontcolor="black",
        )
        web.node(
            "web_charts",
            "recharts\nDashboard Charts",
            shape="box",
            style="filled,rounded",
            fillcolor="#f0883e",
            fontcolor="white",
        )
        web.node(
            "web_stripe",
            "@stripe/react-stripe-js\nPayment UI",
            shape="box",
            style="filled,rounded",
            fillcolor="#6e40c9",
            fontcolor="white",
        )
        web.node(
            "web_sentry",
            "@sentry/react\nError Tracking",
            shape="box",
            style="filled,rounded",
            fillcolor="#8b949e",
            fontcolor="white",
        )
        web.node(
            "web_qr",
            "qrcode.react\nQR Codes",
            shape="box",
            style="filled,rounded",
            fillcolor="#79c0ff",
            fontcolor="white",
        )
        web.node(
            "web_toast",
            "react-hot-toast\nNotifications",
            shape="box",
            style="filled,rounded",
            fillcolor="#f778ba",
            fontcolor="white",
        )
        web.node(
            "web_dayjs",
            "dayjs\nDate Utils",
            shape="box",
            style="filled,rounded",
            fillcolor="#8b949e",
            fontcolor="white",
        )

    # React Native Mobile
    with sub.subgraph(name="cluster_mobile") as mobile:
        mobile.attr(
            label="React Native (Expo SDK 51)",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="11",
            penwidth="1.5",
        )
        mobile.node(
            "mob_rn",
            "React Native 0.74\nreact",
            shape="box",
            style="filled,rounded",
            fillcolor="#238636",
            fontcolor="white",
        )
        mobile.node(
            "mob_expo",
            "Expo 51\nCamera · Device · Notifications\nSecureStore · LocalAuth",
            shape="box",
            style="filled,rounded",
            fillcolor="#1f6feb",
            fontcolor="white",
        )
        mobile.node(
            "mob_nav",
            "@react-navigation\nnative-stack + bottom-tabs",
            shape="box",
            style="filled,rounded",
            fillcolor="#8957e5",
            fontcolor="white",
        )
        mobile.node(
            "mob_query",
            "@tanstack/react-query\n+ axios + zustand",
            shape="box",
            style="filled,rounded",
            fillcolor="#da3633",
            fontcolor="white",
        )
        mobile.node(
            "mob_charts",
            "react-native-chart-kit",
            shape="box",
            style="filled,rounded",
            fillcolor="#f0883e",
            fontcolor="white",
        )
        mobile.node(
            "mob_sentry",
            "@sentry/react-native",
            shape="box",
            style="filled,rounded",
            fillcolor="#8b949e",
            fontcolor="white",
        )

    # Public Portal
    with sub.subgraph(name="cluster_portal") as portal:
        portal.attr(
            label="Public Portal (Unauthenticated)",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#ffa657",
            color="#d29922",
            fontsize="11",
            penwidth="1.5",
        )
        portal.node(
            "portal_apply",
            "Application Form\nAdmission Apply",
            shape="box",
            style="filled,rounded",
            fillcolor="#d29922",
            fontcolor="black",
        )
        portal.node(
            "portal_status",
            "Status Tracker\nTracking ID Lookup",
            shape="box",
            style="filled,rounded",
            fillcolor="#e3b341",
            fontcolor="black",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: INFRASTRUCTURE LAYER (HLD)
# ═══════════════════════════════════════════════════════════════════════════════

with dot.subgraph(name="cluster_infra_layer") as sub:
    sub.attr(
        label="INFRASTRUCTURE LAYER",
        style="filled,rounded",
        fillcolor="#161b22",
        fontcolor="#f0883e",
        color="#30363d",
        fontsize="14",
        fontname="Sans",
        penwidth="2",
    )

    # CDN
    sub.node(
        "cdn",
        "<<B>CDN</B><BR/>CloudFront<BR/><FONT POINT-SIZE='8'>Static Assets · Media<BR/>Cache TTL: 1 year</FONT>>",
        shape="cylinder",
        style="filled,rounded",
        fillcolor="#f0883e",
        fontcolor="white",
    )

    # Nginx
    with sub.subgraph(name="cluster_nginx") as nginx:
        nginx.attr(
            label="Nginx — Reverse Proxy + Load Balancer + API Gateway",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#ff7b72",
            color="#da3633",
            fontsize="11",
            penwidth="1.5",
        )
        nginx.node(
            "nginx_rp",
            "Reverse Proxy\nTLS Termination",
            shape="box",
            style="filled,rounded",
            fillcolor="#da3633",
            fontcolor="white",
        )
        nginx.node(
            "nginx_lb",
            "Load Balancer\nleast_conn",
            shape="box",
            style="filled,rounded",
            fillcolor="#f85149",
            fontcolor="white",
        )
        nginx.node(
            "nginx_gw",
            "API Gateway\nRate Limiting\nSecurity Headers\nCORS · CSP",
            shape="box",
            style="filled,rounded",
            fillcolor="#b62324",
            fontcolor="white",
        )

    # Security
    with sub.subgraph(name="cluster_security") as sec:
        sec.attr(
            label="Security",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="11",
            penwidth="1.5",
        )
        sec.node(
            "sec_jwt",
            "JWT Auth\nSimpleJWT\nAccess: 60min\nRefresh: 7d",
            shape="box",
            style="filled,rounded",
            fillcolor="#238636",
            fontcolor="white",
        )
        sec.node(
            "sec_2fa",
            "2FA (TOTP)\npyotp\nBackup Codes",
            shape="box",
            style="filled,rounded",
            fillcolor="#1a7f37",
            fontcolor="white",
        )
        sec.node(
            "sec_rbac",
            "RBAC (7 Roles)\nIsSchoolAdmin\nIsTeacher\nIsStudent...",
            shape="box",
            style="filled,rounded",
            fillcolor="#2ea043",
            fontcolor="white",
        )
        sec.node(
            "sec_axes",
            "django-axes\nBrute-Force\n(5 attempts/30m)",
            shape="box",
            style="filled,rounded",
            fillcolor="#56d364",
            fontcolor="black",
        )
        sec.node(
            "sec_tenant",
            "TenantMiddleware\nschool_id isolation\nX-School-ID header",
            shape="box",
            style="filled,rounded",
            fillcolor="#3fb950",
            fontcolor="black",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: APPLICATION LAYER — Django Backend (HLD + LLD)
# ═══════════════════════════════════════════════════════════════════════════════

with dot.subgraph(name="cluster_app_layer") as sub:
    sub.attr(
        label="APPLICATION LAYER — Django 5.2 + DRF 3.15",
        style="filled,rounded",
        fillcolor="#161b22",
        fontcolor="#d2a8ff",
        color="#8957e5",
        fontsize="14",
        fontname="Sans",
        penwidth="2",
    )

    # Backend Dependencies
    with sub.subgraph(name="cluster_backend_deps") as bdep:
        bdep.attr(
            label="Backend Dependencies (52 packages)",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="10",
            penwidth="1",
        )
        bdep.node(
            "dep_django",
            "Django 5.2\n+ DRF 3.15",
            shape="box",
            style="filled,rounded",
            fillcolor="#0c2d6b",
            fontcolor="white",
        )
        bdep.node(
            "dep_channels",
            "channels 4.3\nchannels-redis 4.3",
            shape="box",
            style="filled,rounded",
            fillcolor="#1f6feb",
            fontcolor="white",
        )
        bdep.node(
            "dep_celery",
            "celery 5.3\ndjango-celery-beat\nflower",
            shape="box",
            style="filled,rounded",
            fillcolor="#8957e5",
            fontcolor="white",
        )
        bdep.node(
            "dep_security",
            "pyotp · cryptography\ndjango-axes\ndjango-ratelimit",
            shape="box",
            style="filled,rounded",
            fillcolor="#238636",
            fontcolor="white",
        )
        bdep.node(
            "dep_comm",
            "sendgrid · twilio\nvonage · firebase-admin",
            shape="box",
            style="filled,rounded",
            fillcolor="#da3633",
            fontcolor="white",
        )
        bdep.node(
            "dep_storage",
            "boto3 · django-storages\nwhitenoise · Pillow",
            shape="box",
            style="filled,rounded",
            fillcolor="#f0883e",
            fontcolor="white",
        )
        bdep.node(
            "dep_reports",
            "reportlab · openpyxl\npandas · matplotlib",
            shape="box",
            style="filled,rounded",
            fillcolor="#3fb950",
            fontcolor="white",
        )
        bdep.node(
            "dep_monitor",
            "sentry-sdk\ndjango-prometheus",
            shape="box",
            style="filled,rounded",
            fillcolor="#8b949e",
            fontcolor="white",
        )
        bdep.node(
            "dep_docs",
            "drf-spectacular\nOpenAPI docs",
            shape="box",
            style="filled,rounded",
            fillcolor="#79c0ff",
            fontcolor="white",
        )
        bdep.node(
            "dep_servers",
            "daphne (ASGI)\ngunicorn (WSGI)\nuvicorn",
            shape="box",
            style="filled,rounded",
            fillcolor="#d2a8ff",
            fontcolor="white",
        )

    # Middleware Stack
    sub.node(
        "middleware",
        "<<B>Middleware Stack</B><BR/>CORS → Tenant → JWT → Axes → Audit → Security",
        shape="folder",
        style="filled,rounded",
        fillcolor="#30363d",
        fontcolor="#c9d1d9",
    )

    # ── SERVICE MODULES (22 modules with tables) ──────────────────────────────

    # 1. AUTH SERVICE
    with sub.subgraph(name="cluster_auth") as auth:
        auth.attr(
            label="Auth & Core (7 tables)",
            style="filled,rounded",
            fillcolor="#0f3460",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="10",
            penwidth="1.5",
        )
        auth.node(
            "t_school",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD BGCOLOR="#0f3460"><FONT COLOR="white"><B>School</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="8">code · subdomain · name<BR/>logo · timezone · subscription_tier</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        auth.node(
            "t_user",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD BGCOLOR="#16213e"><FONT COLOR="white"><B>User</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="8">email · role (8 roles)<BR/>2FA · email_verified</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        auth.node(
            "t_audit",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD BGCOLOR="#1a1a2e"><FONT COLOR="white"><B>AuditLog</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="8">action · resource_type<BR/>ip_address</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        auth.node(
            "t_session",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD BGCOLOR="#1a1a2e"><FONT COLOR="white"><B>UserSession</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="8">refresh_token_jti<BR/>device_info</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        auth.node(
            "t_preset",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD BGCOLOR="#1a1a2e"><FONT COLOR="white"><B>PasswordResetToken</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="8">token (SHA-256)<BR/>expires_at · used</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        auth.node(
            "t_evtok",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD BGCOLOR="#1a1a2e"><FONT COLOR="white"><B>EmailVerificationToken</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="8">token (SHA-256)<BR/>email · expires_at</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        auth.node(
            "t_2fabk",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4"><TR><TD BGCOLOR="#1a1a2e"><FONT COLOR="white"><B>TwoFactorBackupCode</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="8">hashed_code · used</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 2. STUDENTS SERVICE
    with sub.subgraph(name="cluster_students") as st:
        st.attr(
            label="Students (9 tables)",
            style="filled,rounded",
            fillcolor="#16213e",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="10",
            penwidth="1.5",
        )
        st.node(
            "t_ay",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d1b2a"><FONT COLOR="white" POINT-SIZE="8"><B>AcademicYear</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · start/end_date</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        st.node(
            "t_grade",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1b263b"><FONT COLOR="white" POINT-SIZE="8"><B>Grade</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · level</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        st.node(
            "t_class",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1b263b"><FONT COLOR="white" POINT-SIZE="8"><B>Classroom</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · capacity · room_number</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        st.node(
            "t_student",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d1b2a"><FONT COLOR="white" POINT-SIZE="8"><B>Student</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">admission_number · DOB · gender</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        st.node(
            "t_guardian",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1b263b"><FONT COLOR="white" POINT-SIZE="8"><B>Guardian</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · email · phone</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        st.node(
            "t_stuguard",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d1b2a"><FONT COLOR="white" POINT-SIZE="8"><B>StudentGuardian</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">relationship · portal_access</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        st.node(
            "t_enroll",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1b263b"><FONT COLOR="white" POINT-SIZE="8"><B>Enrollment</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">status · is_active</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        st.node(
            "t_parent",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1b263b"><FONT COLOR="white" POINT-SIZE="8"><B>ParentProfile</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">relationship · occupation</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        st.node(
            "t_doc",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d1b2a"><FONT COLOR="white" POINT-SIZE="8"><B>Document</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">document_type · title</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 3. ACADEMICS
    with sub.subgraph(name="cluster_academics") as acad:
        acad.attr(
            label="Academics (4 tables)",
            style="filled,rounded",
            fillcolor="#1a1a2e",
            fontcolor="#d2a8ff",
            color="#8957e5",
            fontsize="10",
            penwidth="1.5",
        )
        acad.node(
            "t_subject",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#16213e"><FONT COLOR="white" POINT-SIZE="8"><B>Subject</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · code · max_marks</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        acad.node(
            "t_ta",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1a1a2e"><FONT COLOR="white" POINT-SIZE="8"><B>TeacherAssignment</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">teacher × subject × class</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        acad.node(
            "t_tp",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#16213e"><FONT COLOR="white" POINT-SIZE="8"><B>TeacherProfile</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">qualification · specialization</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        acad.node(
            "t_lp",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1a1a2e"><FONT COLOR="white" POINT-SIZE="8"><B>LessonPlan</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">title · topic · date · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 4. ATTENDANCE
    with sub.subgraph(name="cluster_attendance") as att:
        att.attr(
            label="Attendance (3 tables)",
            style="filled,rounded",
            fillcolor="#5a189a",
            fontcolor="#d2a8ff",
            color="#8957e5",
            fontsize="10",
            penwidth="1.5",
        )
        att.node(
            "t_attrec",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#3c096c"><FONT COLOR="white" POINT-SIZE="8"><B>AttendanceRecord</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">date · status · recorded_by</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        att.node(
            "t_peratt",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#5a189a"><FONT COLOR="white" POINT-SIZE="8"><B>PeriodAttendance</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">period_number · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        att.node(
            "t_attleave",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#7b2cbf"><FONT COLOR="white" POINT-SIZE="8"><B>AttendanceLeave</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">leave_type · from/to_date</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 5. GRADEBOOK
    with sub.subgraph(name="cluster_gradebook") as gb:
        gb.attr(
            label="Gradebook (11 tables)",
            style="filled,rounded",
            fillcolor="#0d7377",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="10",
            penwidth="1.5",
        )
        gb.node(
            "t_gscale",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d7377"><FONT COLOR="white" POINT-SIZE="8"><B>GradingScale</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · is_default</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_gse",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#14919b"><FONT COLOR="white" POINT-SIZE="8"><B>GradingScaleEntry</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">letter · min/max% · grade_point</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_etype",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d7377"><FONT COLOR="white" POINT-SIZE="8"><B>ExamType</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · weightage</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_exam",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#14919b"><FONT COLOR="white" POINT-SIZE="8"><B>Exam</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · start/end · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_esch",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d7377"><FONT COLOR="white" POINT-SIZE="8"><B>ExamSchedule</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">date · time · venue · max_marks</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_gbook_grade",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#14919b"><FONT COLOR="white" POINT-SIZE="8"><B>Grade</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">marks_obtained · is_pass</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_assess",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d7377"><FONT COLOR="white" POINT-SIZE="8"><B>Assessment</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">title · type · due_date</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_assub",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#14919b"><FONT COLOR="white" POINT-SIZE="8"><B>AssessmentSubmission</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">marks · submitted_at · is_late</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_rcard",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d7377"><FONT COLOR="white" POINT-SIZE="8"><B>ReportCard</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">percentage · GPA · rank · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_gclog",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#14919b"><FONT COLOR="white" POINT-SIZE="8"><B>GradeChangeLog</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">old/new_marks · reason</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        gb.node(
            "t_gcprop",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#0d7377"><FONT COLOR="white" POINT-SIZE="8"><B>GradeChangeProposal</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">proposed_marks · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 6. FEES
    with sub.subgraph(name="cluster_fees") as fees:
        fees.attr(
            label="Fees (6 tables)",
            style="filled,rounded",
            fillcolor="#2d6a4f",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="10",
            penwidth="1.5",
        )
        fees.node(
            "t_fcat",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1b4332"><FONT COLOR="white" POINT-SIZE="8"><B>FeeCategory</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · recurrence</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        fees.node(
            "t_fstruct",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#2d6a4f"><FONT COLOR="white" POINT-SIZE="8"><B>FeeStructure</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">amount · late_fee_per_day</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        fees.node(
            "t_finv",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#40916c"><FONT COLOR="white" POINT-SIZE="8"><B>FeeInvoice</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">invoice# · amount · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        fees.node(
            "t_pay",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#52b788"><FONT COLOR="white" POINT-SIZE="8"><B>Payment</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">amount · method · txn_id</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        fees.node(
            "t_schol",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#2d6a4f"><FONT COLOR="white" POINT-SIZE="8"><B>Scholarship</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">discount_type · value</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        fees.node(
            "t_pgway",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#40916c"><FONT COLOR="white" POINT-SIZE="8"><B>PaymentGatewayConfig</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">stripe · khalti · esewa</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 7. TIMETABLE
    with sub.subgraph(name="cluster_timetable") as tt:
        tt.attr(
            label="Timetable (3 tables)",
            style="filled,rounded",
            fillcolor="#e07a5f",
            fontcolor="#ffa657",
            color="#d29922",
            fontsize="10",
            penwidth="1.5",
        )
        tt.node(
            "t_period",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e07a5f"><FONT COLOR="white" POINT-SIZE="8"><B>Period</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">number · start/end_time</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        tt.node(
            "t_slot",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="white" POINT-SIZE="8"><B>TimetableSlot</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">day · class × subject × teacher</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        tt.node(
            "t_event",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e07a5f"><FONT COLOR="white" POINT-SIZE="8"><B>SchoolEvent</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">title · type · datetime</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 8. COMMUNICATION
    with sub.subgraph(name="cluster_comm") as comm:
        comm.attr(
            label="Communication (6 tables)",
            style="filled,rounded",
            fillcolor="#81b29a",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="10",
            penwidth="1.5",
        )
        comm.node(
            "t_announce",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#6a994e"><FONT COLOR="white" POINT-SIZE="8"><B>Announcement</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">title · priority · audience</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        comm.node(
            "t_annread",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#81b29a"><FONT COLOR="white" POINT-SIZE="8"><B>AnnouncementRead</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">read_at</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        comm.node(
            "t_msg",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#a7c957"><FONT COLOR="black" POINT-SIZE="8"><B>DirectMessage</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">subject · body · read_at</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        comm.node(
            "t_ntpl",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#6a994e"><FONT COLOR="white" POINT-SIZE="8"><B>NotificationTemplate</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">event_type · email/SMS</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        comm.node(
            "t_notif",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#81b29a"><FONT COLOR="white" POINT-SIZE="8"><B>Notification</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">title · type · is_read</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        comm.node(
            "t_dtoken",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#a7c957"><FONT COLOR="black" POINT-SIZE="8"><B>DeviceToken</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">token · device_type</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 9. HR
    with sub.subgraph(name="cluster_hr") as hr:
        hr.attr(
            label="HR & Payroll (7 tables)",
            style="filled,rounded",
            fillcolor="#3d405b",
            fontcolor="#c9d1d9",
            color="#8b949e",
            fontsize="10",
            penwidth="1.5",
        )
        hr.node(
            "t_dept",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#3d405b"><FONT COLOR="white" POINT-SIZE="8"><B>Department</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · code</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hr.node(
            "t_emp",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#5c5f7e"><FONT COLOR="white" POINT-SIZE="8"><B>Employee</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">employee_id · designation</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hr.node(
            "t_sstruct",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#3d405b"><FONT COLOR="white" POINT-SIZE="8"><B>SalaryStructure</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">basic_pay · allowances</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hr.node(
            "t_esal",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#5c5f7e"><FONT COLOR="white" POINT-SIZE="8"><B>EmployeeSalary</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">effective_from · is_active</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hr.node(
            "t_payslip",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#3d405b"><FONT COLOR="white" POINT-SIZE="8"><B>Payslip</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">month · gross/net_pay</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hr.node(
            "t_lreq",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#5c5f7e"><FONT COLOR="white" POINT-SIZE="8"><B>LeaveRequest</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">type · dates · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hr.node(
            "t_acctpro",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#3d405b"><FONT COLOR="white" POINT-SIZE="8"><B>AccountantProfile</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">certification · specialization</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 10. TRANSPORT
    with sub.subgraph(name="cluster_transport") as tr:
        tr.attr(
            label="Transportation (6 tables)",
            style="filled,rounded",
            fillcolor="#e63946",
            fontcolor="#ff7b72",
            color="#da3633",
            fontsize="10",
            penwidth="1.5",
        )
        tr.node(
            "t_vehicle",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e63946"><FONT COLOR="white" POINT-SIZE="8"><B>Vehicle</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">reg# · type · capacity</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        tr.node(
            "t_driver",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="black" POINT-SIZE="8"><B>Driver</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">license · phone</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        tr.node(
            "t_route",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e63946"><FONT COLOR="white" POINT-SIZE="8"><B>Route</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · start/end · fare</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        tr.node(
            "t_rstop",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="black" POINT-SIZE="8"><B>RouteStop</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · order · lat/lng</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        tr.node(
            "t_sturoot",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e63946"><FONT COLOR="white" POINT-SIZE="8"><B>StudentRoute</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">pickup/dropoff · fare</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        tr.node(
            "t_vmaint",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="black" POINT-SIZE="8"><B>VehicleMaintenance</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">type · cost · next_service</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 11. INVENTORY
    with sub.subgraph(name="cluster_inventory") as inv:
        inv.attr(
            label="Inventory (6 tables)",
            style="filled,rounded",
            fillcolor="#f4a261",
            fontcolor="#ffa657",
            color="#d29922",
            fontsize="10",
            penwidth="1.5",
        )
        inv.node(
            "t_cat",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e76f51"><FONT COLOR="white" POINT-SIZE="8"><B>Category</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · description</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        inv.node(
            "t_supplier",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="black" POINT-SIZE="8"><B>Supplier</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · contact · email</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        inv.node(
            "t_invitem",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e76f51"><FONT COLOR="white" POINT-SIZE="8"><B>InventoryItem</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · sku · qty · price</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        inv.node(
            "t_stock",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="black" POINT-SIZE="8"><B>StockMovement</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">qty · type · reference</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        inv.node(
            "t_po",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e76f51"><FONT COLOR="white" POINT-SIZE="8"><B>PurchaseOrder</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">order# · status · total</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        inv.node(
            "t_poi",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="black" POINT-SIZE="8"><B>PurchaseOrderItem</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">qty · unit_price · total</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 12. HOSTEL
    with sub.subgraph(name="cluster_hostel") as host:
        host.attr(
            label="Hostel (5 tables)",
            style="filled,rounded",
            fillcolor="#264653",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="10",
            penwidth="1.5",
        )
        host.node(
            "t_hostel",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#264653"><FONT COLOR="white" POINT-SIZE="8"><B>Hostel</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · type · warden</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        host.node(
            "t_hroom",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#2a9d8f"><FONT COLOR="white" POINT-SIZE="8"><B>HostelRoom</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">room# · capacity · fee</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        host.node(
            "t_halloc",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#264653"><FONT COLOR="white" POINT-SIZE="8"><B>HostelAllocation</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">check_in/out · is_active</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        host.node(
            "t_hfee",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#2a9d8f"><FONT COLOR="white" POINT-SIZE="8"><B>HostelFee</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">type · amount · paid</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        host.node(
            "t_hvisit",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#264653"><FONT COLOR="white" POINT-SIZE="8"><B>HostelVisitor</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · date · in/out_time</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 13. SPORTS
    with sub.subgraph(name="cluster_sports") as sp:
        sp.attr(
            label="Sports (5 tables)",
            style="filled,rounded",
            fillcolor="#2a9d8f",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="10",
            penwidth="1.5",
        )
        sp.node(
            "t_sport",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#2a9d8f"><FONT COLOR="white" POINT-SIZE="8"><B>Sport</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · equipment</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        sp.node(
            "t_team",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#3dbca8"><FONT COLOR="white" POINT-SIZE="8"><B>Team</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · age_group · gender</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        sp.node(
            "t_tmember",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#2a9d8f"><FONT COLOR="white" POINT-SIZE="8"><B>TeamMember</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">role · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        sp.node(
            "t_sevent",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#3dbca8"><FONT COLOR="white" POINT-SIZE="8"><B>SportEvent</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · type · dates</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        sp.node(
            "t_sach",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#2a9d8f"><FONT COLOR="white" POINT-SIZE="8"><B>SportAchievement</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">type · title · rank</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 14. HEALTH
    with sub.subgraph(name="cluster_health") as hlth:
        hlth.attr(
            label="Health Clinic (4 tables)",
            style="filled,rounded",
            fillcolor="#e76f51",
            fontcolor="#ffa657",
            color="#d29922",
            fontsize="10",
            penwidth="1.5",
        )
        hlth.node(
            "t_hrec",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e76f51"><FONT COLOR="white" POINT-SIZE="8"><B>HealthRecord</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">blood_group · allergies</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hlth.node(
            "t_nurse",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="black" POINT-SIZE="8"><B>NurseVisit</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">symptoms · diagnosis</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hlth.node(
            "t_immun",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e76f51"><FONT COLOR="white" POINT-SIZE="8"><B>Immunization</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">vaccine · date · dose</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        hlth.node(
            "t_medlog",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#f4a261"><FONT COLOR="black" POINT-SIZE="8"><B>MedicationLog</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">medication · dosage</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 15. LIBRARY
    with sub.subgraph(name="cluster_library") as lib:
        lib.attr(
            label="Library (3 tables)",
            style="filled,rounded",
            fillcolor="#9c89b8",
            fontcolor="#d2a8ff",
            color="#8957e5",
            fontsize="10",
            penwidth="1.5",
        )
        lib.node(
            "t_book",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#9c89b8"><FONT COLOR="white" POINT-SIZE="8"><B>Book</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">title · isbn · copies</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        lib.node(
            "t_checkout",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#b8a9c9"><FONT COLOR="white" POINT-SIZE="8"><B>Checkout</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">due · returned · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        lib.node(
            "t_libpro",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#9c89b8"><FONT COLOR="white" POINT-SIZE="8"><B>LibrarianProfile</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">certification · experience</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 16. CONFERENCES
    with sub.subgraph(name="cluster_conferences") as conf:
        conf.attr(
            label="Conferences (1 table)",
            style="filled,rounded",
            fillcolor="#b56576",
            fontcolor="#f778ba",
            color="#da3633",
            fontsize="10",
            penwidth="1.5",
        )
        conf.node(
            "t_confslot",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#b56576"><FONT COLOR="white" POINT-SIZE="8"><B>ConferenceSlot</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">date · time · status · mode</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 17. BEHAVIOR
    with sub.subgraph(name="cluster_behavior") as beh:
        beh.attr(
            label="Behavior (2 tables)",
            style="filled,rounded",
            fillcolor="#6c584c",
            fontcolor="#ffa657",
            color="#d29922",
            fontsize="10",
            penwidth="1.5",
        )
        beh.node(
            "t_incident",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#6c584c"><FONT COLOR="white" POINT-SIZE="8"><B>Incident</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">type · severity · action</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        beh.node(
            "t_bref",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#8c7a6b"><FONT COLOR="white" POINT-SIZE="8"><B>Referral</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">reason · type · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 18. ADMISSIONS
    with sub.subgraph(name="cluster_admissions") as adm:
        adm.attr(
            label="Admissions (6 tables)",
            style="filled,rounded",
            fillcolor="#1d3557",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="10",
            penwidth="1.5",
        )
        adm.node(
            "t_intake",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1d3557"><FONT COLOR="white" POINT-SIZE="8"><B>EnrollmentIntake</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · dates · capacity</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        adm.node(
            "t_app",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#457b9d"><FONT COLOR="white" POINT-SIZE="8"><B>Application</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">tracking_id · status (state machine)</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        adm.node(
            "t_appdoc",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1d3557"><FONT COLOR="white" POINT-SIZE="8"><B>ApplicationDocument</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">doc_type · file</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        adm.node(
            "t_apprev",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#457b9d"><FONT COLOR="white" POINT-SIZE="8"><B>ApplicationReview</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">rating · decision</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        adm.node(
            "t_apptl",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#1d3557"><FONT COLOR="white" POINT-SIZE="8"><B>ApplicationTimelineEvent</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">event_type · description</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        adm.node(
            "t_entrance",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#457b9d"><FONT COLOR="white" POINT-SIZE="8"><B>EntranceAssessment</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">test_date · score · notes</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 19. ALUMNI
    with sub.subgraph(name="cluster_alumni") as alum:
        alum.attr(
            label="Alumni (4 tables)",
            style="filled,rounded",
            fillcolor="#457b9d",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="10",
            penwidth="1.5",
        )
        alum.node(
            "t_alumpro",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#457b9d"><FONT COLOR="white" POINT-SIZE="8"><B>AlumniProfile</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">grad_year · occupation</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        alum.node(
            "t_alevent",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#5c9cc9"><FONT COLOR="white" POINT-SIZE="8"><B>AlumniEvent</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · type · date</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        alum.node(
            "t_aldon",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#457b9d"><FONT COLOR="white" POINT-SIZE="8"><B>AlumniDonation</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">amount · type · method</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        alum.node(
            "t_alchap",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#5c9cc9"><FONT COLOR="white" POINT-SIZE="8"><B>AlumniChapter</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · city · country</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # 20. CAFETERIA
    with sub.subgraph(name="cluster_cafeteria") as caf:
        caf.attr(
            label="Cafeteria (4 tables)",
            style="filled,rounded",
            fillcolor="#e0afa0",
            fontcolor="#ffa657",
            color="#d29922",
            fontsize="10",
            penwidth="1.5",
        )
        caf.node(
            "t_meal",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#d68c79"><FONT COLOR="white" POINT-SIZE="8"><B>MealMenu</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">day · type · items · price</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        caf.node(
            "t_mplan",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e0afa0"><FONT COLOR="white" POINT-SIZE="8"><B>MealPlan</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">name · price_per_period</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        caf.node(
            "t_mbook",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#d68c79"><FONT COLOR="white" POINT-SIZE="8"><B>MealBooking</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">date · type · status</FONT></TD></TR></TABLE>>',
            shape="none",
        )
        caf.node(
            "t_diet",
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="#e0afa0"><FONT COLOR="white" POINT-SIZE="8"><B>DietaryRestriction</B></FONT></TD></TR><TR><TD BGCOLOR="#161b22"><FONT COLOR="#c9d1d9" POINT-SIZE="7">type · allergen · notes</FONT></TD></TR></TABLE>>',
            shape="none",
        )

    # Celery Task Queue
    sub.node(
        "celery",
        "<<B>Celery Task Queue</B><BR/><FONT POINT-SIZE='8'>default · notifications · reports<BR/>Beat: backup · expiry · reminders<BR/>Workers: 2-8 pods (HPA)</FONT>>",
        shape="cylinder",
        style="filled,rounded",
        fillcolor="#8957e5",
        fontcolor="white",
    )

    # WebSocket
    sub.node(
        "websocket",
        "<<B>Django Channels (WebSocket)</B><BR/><FONT POINT-SIZE='8'>/ws/notifications/ · /ws/chat/{id}/<BR/>channels 4.3 + channels-redis 4.3</FONT>>",
        shape="cylinder",
        style="filled,rounded",
        fillcolor="#1f6feb",
        fontcolor="white",
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: DATA TIER (HLD + LLD)
# ═══════════════════════════════════════════════════════════════════════════════

with dot.subgraph(name="cluster_data_layer") as sub:
    sub.attr(
        label="DATA TIER",
        style="filled,rounded",
        fillcolor="#161b22",
        fontcolor="#58a6ff",
        color="#30363d",
        fontsize="14",
        fontname="Sans",
        penwidth="2",
    )

    sub.node(
        "postgres",
        "<<B>PostgreSQL 16</B><BR/><FONT POINT-SIZE='8'>Primary DB + Read Replica<BR/>105 tables · PgBouncer<BR/>psycopg2-binary · django-extensions</FONT>>",
        shape="cylinder",
        style="filled,rounded",
        fillcolor="#336791",
        fontcolor="white",
    )
    sub.node(
        "redis",
        "<<B>Redis 7</B><BR/><FONT POINT-SIZE='8'>Cache · Session · Channel Layer<BR/>Celery Broker · JWT Blacklist<BR/>redis 5.0 · django-redis 5.4</FONT>>",
        shape="cylinder",
        style="filled,rounded",
        fillcolor="#dc382d",
        fontcolor="white",
    )
    sub.node(
        "s3",
        "<<B>AWS S3 / MinIO</B><BR/><FONT POINT-SIZE='8'>Documents · Media · Reports<BR/>boto3 · django-storages<BR/>whitenoise (static files)</FONT>>",
        shape="cylinder",
        style="filled,rounded",
        fillcolor="#ff9900",
        fontcolor="black",
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: EXTERNAL SERVICES (HLD)
# ═══════════════════════════════════════════════════════════════════════════════

with dot.subgraph(name="cluster_external") as sub:
    sub.attr(
        label="EXTERNAL SERVICES",
        style="filled,rounded",
        fillcolor="#161b22",
        fontcolor="#f0883e",
        color="#30363d",
        fontsize="14",
        fontname="Sans",
        penwidth="2",
    )

    with sub.subgraph(name="cluster_payments") as pay:
        pay.attr(
            label="Payment Gateways",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="11",
            penwidth="1.5",
        )
        pay.node(
            "stripe",
            "Stripe\nstripe 10.0\nCard Payments",
            shape="box",
            style="filled,rounded",
            fillcolor="#635bff",
            fontcolor="white",
        )
        pay.node(
            "khalti",
            "Khalti\nNepal Mobile Wallet",
            shape="box",
            style="filled,rounded",
            fillcolor="#5c2d91",
            fontcolor="white",
        )
        pay.node(
            "esewa",
            "eSewa\nNepal e-Wallet",
            shape="box",
            style="filled,rounded",
            fillcolor="#60b842",
            fontcolor="white",
        )

    with sub.subgraph(name="cluster_notif") as notif:
        notif.attr(
            label="Communication Services",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="11",
            penwidth="1.5",
        )
        notif.node(
            "sendgrid",
            "SendGrid\nTransactional Email\nsendgrid 6.11",
            shape="box",
            style="filled,rounded",
            fillcolor="#1a82e2",
            fontcolor="white",
        )
        notif.node(
            "twilio",
            "Twilio\nSMS Notifications\ntwilio 9.0",
            shape="box",
            style="filled,rounded",
            fillcolor="#f22f46",
            fontcolor="white",
        )
        notif.node(
            "vonage",
            "Vonage\nSMS Fallback\nvonage 4.0",
            shape="box",
            style="filled,rounded",
            fillcolor="#000000",
            fontcolor="white",
        )
        notif.node(
            "firebase",
            "Firebase FCM\nMobile Push\nfirebase-admin 6.4",
            shape="box",
            style="filled,rounded",
            fillcolor="#ffca28",
            fontcolor="black",
        )

    with sub.subgraph(name="cluster_monitoring") as mon:
        mon.attr(
            label="Monitoring & Observability",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#c9d1d9",
            color="#8b949e",
            fontsize="11",
            penwidth="1.5",
        )
        mon.node(
            "sentry",
            "Sentry\nError Tracking\nsentry-sdk 1.44",
            shape="box",
            style="filled,rounded",
            fillcolor="#362d59",
            fontcolor="white",
        )
        mon.node(
            "prometheus",
            "Prometheus + Grafana\ndjango-prometheus\nMetrics + Dashboards",
            shape="box",
            style="filled,rounded",
            fillcolor="#e6522c",
            fontcolor="white",
        )

    with sub.subgraph(name="cluster_zoom") as zoom:
        zoom.attr(
            label="Video Conferencing",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#2d8cff",
            color="#1f6feb",
            fontsize="11",
            penwidth="1.5",
        )
        zoom.node(
            "zoom",
            "Zoom S2S OAuth\nConference Integration\n(Server-to-Server)",
            shape="box",
            style="filled,rounded",
            fillcolor="#2d8cff",
            fontcolor="white",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: DEPLOYMENT (HLD)
# ═══════════════════════════════════════════════════════════════════════════════

with dot.subgraph(name="cluster_deploy") as sub:
    sub.attr(
        label="DEPLOYMENT",
        style="filled,rounded",
        fillcolor="#161b22",
        fontcolor="#58a6ff",
        color="#30363d",
        fontsize="14",
        fontname="Sans",
        penwidth="2",
    )

    with sub.subgraph(name="cluster_dev") as dev:
        dev.attr(
            label="Development (Docker Compose)",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="10",
            penwidth="1.5",
        )
        dev.node(
            "dev_compose",
            "Docker Compose\n9 services\npostgres · redis · minio\nbackend · celery · beat\nfrontend · nginx · flower",
            shape="box",
            style="filled,rounded",
            fillcolor="#238636",
            fontcolor="white",
        )

    with sub.subgraph(name="cluster_prod") as prod:
        prod.attr(
            label="Production (Kubernetes)",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="10",
            penwidth="1.5",
        )
        prod.node(
            "prod_k8s",
            "Kubernetes (EKS/AKS)\nIngress → Backend (2-10 pods)\nCelery Workers (2-8 pods)\nHPA: CPU 70%, Memory 80%",
            shape="box",
            style="filled,rounded",
            fillcolor="#1f6feb",
            fontcolor="white",
        )
        prod.node(
            "prod_ci",
            "GitHub Actions CI/CD\npytest · coverage · lint\ndocker build · deploy",
            shape="box",
            style="filled,rounded",
            fillcolor="#8957e5",
            fontcolor="white",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: STATE MACHINES (LLD)
# ═══════════════════════════════════════════════════════════════════════════════

with dot.subgraph(name="cluster_states") as sub:
    sub.attr(
        label="STATE MACHINES (LLD)",
        style="filled,rounded",
        fillcolor="#161b22",
        fontcolor="#f778ba",
        color="#da3633",
        fontsize="14",
        fontname="Sans",
        penwidth="2",
    )

    # Admissions State Machine
    with sub.subgraph(name="cluster_adm_sm") as asm:
        asm.attr(
            label="Admissions Application",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#79c0ff",
            color="#1f6feb",
            fontsize="10",
            penwidth="1.5",
        )
        asm.node(
            "sm_applied", "applied", shape="circle", style="filled", fillcolor="#1f6feb", fontcolor="white", width="0.8"
        )
        asm.node(
            "sm_screening",
            "screening",
            shape="circle",
            style="filled",
            fillcolor="#238636",
            fontcolor="white",
            width="0.8",
        )
        asm.node(
            "sm_interview",
            "interview",
            shape="circle",
            style="filled",
            fillcolor="#8957e5",
            fontcolor="white",
            width="0.8",
        )
        asm.node(
            "sm_offer", "offer", shape="circle", style="filled", fillcolor="#d29922", fontcolor="white", width="0.8"
        )
        asm.node(
            "sm_enrolled",
            "enrolled",
            shape="doublecircle",
            style="filled",
            fillcolor="#56d364",
            fontcolor="black",
            width="0.8",
        )
        asm.node(
            "sm_rejected",
            "rejected",
            shape="circle",
            style="filled",
            fillcolor="#da3633",
            fontcolor="white",
            width="0.8",
        )
        asm.node(
            "sm_waitlisted",
            "waitlisted",
            shape="circle",
            style="filled",
            fillcolor="#f0883e",
            fontcolor="white",
            width="0.8",
        )
        asm.node(
            "sm_withdrawn",
            "withdrawn",
            shape="circle",
            style="filled",
            fillcolor="#8b949e",
            fontcolor="white",
            width="0.8",
        )

    # Fee Payment State Machine
    with sub.subgraph(name="cluster_fee_sm") as fsm:
        fsm.attr(
            label="Fee Invoice Status",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#7ee787",
            color="#238636",
            fontsize="10",
            penwidth="1.5",
        )
        fsm.node(
            "sm_draft", "draft", shape="circle", style="filled", fillcolor="#8b949e", fontcolor="white", width="0.6"
        )
        fsm.node(
            "sm_unpaid", "unpaid", shape="circle", style="filled", fillcolor="#da3633", fontcolor="white", width="0.6"
        )
        fsm.node(
            "sm_partial", "partial", shape="circle", style="filled", fillcolor="#d29922", fontcolor="white", width="0.6"
        )
        fsm.node(
            "sm_paid", "paid", shape="doublecircle", style="filled", fillcolor="#56d364", fontcolor="black", width="0.6"
        )
        fsm.node(
            "sm_overdue", "overdue", shape="circle", style="filled", fillcolor="#f85149", fontcolor="white", width="0.6"
        )
        fsm.node(
            "sm_waived", "waived", shape="circle", style="filled", fillcolor="#238636", fontcolor="white", width="0.6"
        )

    # Grade Change State Machine
    with sub.subgraph(name="cluster_grade_sm") as gsm:
        gsm.attr(
            label="Grade Change Workflow",
            style="filled,rounded",
            fillcolor="#1a2332",
            fontcolor="#d2a8ff",
            color="#8957e5",
            fontsize="10",
            penwidth="1.5",
        )
        gsm.node(
            "sm_proposed",
            "proposed",
            shape="circle",
            style="filled",
            fillcolor="#d29922",
            fontcolor="white",
            width="0.6",
        )
        gsm.node(
            "sm_approved",
            "approved",
            shape="circle",
            style="filled",
            fillcolor="#238636",
            fontcolor="white",
            width="0.6",
        )
        gsm.node(
            "sm_published",
            "published",
            shape="doublecircle",
            style="filled",
            fillcolor="#56d364",
            fontcolor="black",
            width="0.6",
        )
        gsm.node(
            "sm_grej", "rejected", shape="circle", style="filled", fillcolor="#da3633", fontcolor="white", width="0.6"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════════════════════════

with dot.subgraph(name="cluster_legend") as leg:
    leg.attr(
        label="LEGEND",
        style="filled,rounded",
        fillcolor="#161b22",
        fontcolor="#c9d1d9",
        color="#30363d",
        fontsize="12",
        fontname="Sans",
        penwidth="1",
    )
    leg.node("leg_1n", "1:N", shape="plaintext", fontcolor="#58a6ff", fontsize="10")
    leg.node("leg_11", "1:1", shape="plaintext", fontcolor="#7ee787", fontsize="10")
    leg.node("leg_mn", "M:N", shape="plaintext", fontcolor="#f0883e", fontsize="10")
    leg.node(
        "leg_stats",
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2"><TR><TD ALIGN="LEFT"><FONT COLOR="#c9d1d9" POINT-SIZE="9">105 Tables · 166 Relationships · 127 Dependencies</FONT></TD></TR><TR><TD ALIGN="LEFT"><FONT COLOR="#8b949e" POINT-SIZE="9">1:1 = 12 (7.3%) · 1:N = 153 (92.7%) · M:N = 1 (0.6%)</FONT></TD></TR></TABLE>>',
        shape="none",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EDGES — Architecture Flow (HLD)
# ═══════════════════════════════════════════════════════════════════════════════

# Client → CDN
dot.edge("web_react", "cdn", color="#58a6ff", arrowsize="0.8")
dot.edge("mob_rn", "cdn", color="#58a6ff", arrowsize="0.8")
dot.edge("portal_apply", "cdn", color="#58a6ff", arrowsize="0.8")

# CDN → Nginx (dynamic requests)
dot.edge(
    "cdn",
    "nginx_rp",
    color="#f0883e",
    style="dashed",
    label="dynamic",
    fontcolor="#8b949e",
    fontsize="7",
    arrowsize="0.8",
)

# Nginx internal
dot.edge("nginx_rp", "nginx_lb", color="#da3633", arrowsize="0.7")
dot.edge("nginx_lb", "nginx_gw", color="#da3633", arrowsize="0.7")

# Nginx → Application
dot.edge(
    "nginx_gw", "middleware", color="#8957e5", label="HTTPS/WSS", fontcolor="#d2a8ff", fontsize="7", arrowsize="0.8"
)

# Middleware → Security
dot.edge("middleware", "sec_jwt", color="#238636", style="dashed", arrowsize="0.6")

# Middleware → Backend
dot.edge(
    "middleware", "dep_django", color="#8957e5", label="requests", fontcolor="#d2a8ff", fontsize="7", arrowsize="0.8"
)

# WebSocket
dot.edge(
    "nginx_gw",
    "websocket",
    color="#1f6feb",
    label="WS Upgrade",
    fontcolor="#79c0ff",
    fontsize="7",
    arrowsize="0.8",
    style="dashed",
)

# Backend → Celery
dot.edge(
    "dep_django",
    "celery",
    color="#8957e5",
    style="dashed",
    label="tasks",
    fontcolor="#d2a8ff",
    fontsize="7",
    arrowsize="0.7",
)

# Celery → External
dot.edge("celery", "sendgrid", color="#1a82e2", style="dashed", arrowsize="0.6")
dot.edge("celery", "twilio", color="#f22f46", style="dashed", arrowsize="0.6")
dot.edge("celery", "firebase", color="#ffca28", style="dashed", arrowsize="0.6")

# Backend → Data Tier
dot.edge("dep_django", "postgres", color="#336791", label="SQL", fontcolor="#79c0ff", fontsize="7", arrowsize="0.8")
dot.edge("dep_django", "redis", color="#dc382d", label="cache", fontcolor="#ff7b72", fontsize="7", arrowsize="0.8")
dot.edge("dep_django", "s3", color="#ff9900", label="files", fontcolor="#ffa657", fontsize="7", arrowsize="0.8")
dot.edge("celery", "redis", color="#dc382d", style="dashed", arrowsize="0.6")
dot.edge("websocket", "redis", color="#dc382d", style="dashed", arrowsize="0.6")

# External → Backend (webhooks)
dot.edge(
    "stripe",
    "nginx_gw",
    color="#635bff",
    style="dashed",
    label="webhook",
    fontcolor="#8b949e",
    fontsize="7",
    arrowsize="0.6",
    dir="back",
)
dot.edge(
    "khalti",
    "nginx_gw",
    color="#5c2d91",
    style="dashed",
    label="callback",
    fontcolor="#8b949e",
    fontsize="7",
    arrowsize="0.6",
    dir="back",
)
dot.edge(
    "esewa",
    "nginx_gw",
    color="#60b842",
    style="dashed",
    label="status",
    fontcolor="#8b949e",
    fontsize="7",
    arrowsize="0.6",
    dir="back",
)

# Monitoring
dot.edge("dep_django", "sentry", color="#362d59", style="dotted", arrowsize="0.5")
dot.edge("dep_django", "prometheus", color="#e6522c", style="dotted", arrowsize="0.5")

# Zoom
dot.edge(
    "dep_django",
    "zoom",
    color="#2d8cff",
    style="dashed",
    label="S2S OAuth",
    fontcolor="#79c0ff",
    fontsize="7",
    arrowsize="0.6",
)

# Deployment
dot.edge("prod_k8s", "postgres", color="#336791", style="dotted", arrowsize="0.5")
dot.edge("prod_k8s", "redis", color="#dc382d", style="dotted", arrowsize="0.5")


# ═══════════════════════════════════════════════════════════════════════════════
# EDGES — Database Relationships (LLD)
# ═══════════════════════════════════════════════════════════════════════════════

edge_style = {"arrowsize": "0.6", "color": "#484f58", "fontcolor": "#8b949e", "fontsize": "7"}

# School → Everything (tenant)
for target in [
    "t_user",
    "t_audit",
    "t_ay",
    "t_grade",
    "t_class",
    "t_student",
    "t_subject",
    "t_dept",
    "t_emp",
    "t_sstruct",
    "t_vehicle",
    "t_route",
    "t_invitem",
    "t_hostel",
    "t_sport",
    "t_book",
    "t_intake",
    "t_alumpro",
    "t_meal",
    "t_fcat",
    "t_fstruct",
    "t_announce",
    "t_ntpl",
]:
    dot.edge("t_school", target, arrowhead="crow", label="1:N", **edge_style)

# User → Profiles (1:1)
for target in ["t_student", "t_guardian", "t_parent", "t_tp", "t_emp", "t_acctpro", "t_libpro", "t_alumpro"]:
    dot.edge(
        "t_user",
        target,
        arrowhead="odiamond",
        label="1:1",
        color="#238636",
        fontcolor="#238636",
        fontsize="7",
        arrowsize="0.6",
    )

# User → 1:N
for target in [
    "t_audit",
    "t_session",
    "t_preset",
    "t_evtok",
    "t_2fabk",
    "t_ta",
    "t_attrec",
    "t_attleave",
    "t_msg",
    "t_notif",
    "t_dtoken",
    "t_lreq",
    "t_confslot",
    "t_incident",
    "t_bref",
    "t_stock",
    "t_apptl",
]:
    dot.edge("t_user", target, arrowhead="crow", label="1:N", **edge_style)

# Student → Various
for target in [
    "t_enroll",
    "t_stuguard",
    "t_doc",
    "t_attrec",
    "t_peratt",
    "t_attleave",
    "t_gbook_grade",
    "t_assub",
    "t_rcard",
    "t_finv",
    "t_schol",
    "t_sturoot",
    "t_halloc",
    "t_tmember",
    "t_sach",
    "t_nurse",
    "t_checkout",
    "t_incident",
    "t_bref",
    "t_mbook",
    "t_diet",
    "t_confslot",
]:
    dot.edge("t_student", target, arrowhead="crow", label="1:N", **edge_style)

# Grade → Classroom → Enrollment
dot.edge("t_grade", "t_class", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_ay", "t_class", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_ay", "t_enroll", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_class", "t_enroll", arrowhead="crow", label="1:N", **edge_style)

# Guardian ↔ Student (M:N via junction)
dot.edge("t_guardian", "t_stuguard", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_student", "t_stuguard", arrowhead="crow", label="1:N", **edge_style)

# Academics
dot.edge("t_grade", "t_subject", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_subject", "t_ta", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_class", "t_ta", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_ay", "t_ta", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_ta", "t_lp", arrowhead="crow", label="1:N", **edge_style)

# Gradebook
dot.edge("t_gscale", "t_gse", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_etype", "t_exam", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_ay", "t_exam", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_exam", "t_esch", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_subject", "t_esch", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_class", "t_esch", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_esch", "t_gbook_grade", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_ta", "t_assess", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_assess", "t_assub", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_exam", "t_rcard", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_gbook_grade", "t_gclog", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_gbook_grade", "t_gcprop", arrowhead="crow", label="1:N", **edge_style)

# Fees
dot.edge("t_fcat", "t_fstruct", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_ay", "t_fstruct", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_grade", "t_fstruct", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_fstruct", "t_finv", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_ay", "t_finv", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_finv", "t_pay", arrowhead="crow", label="1:N", **edge_style)
dot.edge(
    "t_fcat",
    "t_schol",
    arrowhead="crow",
    label="M:N",
    color="#f0883e",
    fontcolor="#f0883e",
    fontsize="7",
    arrowsize="0.6",
)
dot.edge(
    "t_school",
    "t_pgway",
    arrowhead="odiamond",
    label="1:1",
    color="#238636",
    fontcolor="#238636",
    fontsize="7",
    arrowsize="0.6",
)

# Timetable
dot.edge("t_class", "t_slot", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_period", "t_slot", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_subject", "t_slot", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_user", "t_slot", arrowhead="crow", label="1:N", **edge_style)

# Communication
dot.edge("t_announce", "t_annread", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_user", "t_annread", arrowhead="crow", label="1:N", **edge_style)

# HR
dot.edge("t_dept", "t_sstruct", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_emp", "t_esal", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_sstruct", "t_esal", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_esal", "t_payslip", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_dept", "t_acctpro", arrowhead="crow", label="1:N", **edge_style)

# Transport
dot.edge("t_route", "t_rstop", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_route", "t_sturoot", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_vehicle", "t_vmaint", arrowhead="crow", label="1:N", **edge_style)

# Inventory
dot.edge("t_cat", "t_invitem", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_invitem", "t_stock", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_supplier", "t_po", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_po", "t_poi", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_invitem", "t_poi", arrowhead="crow", label="1:N", **edge_style)

# Hostel
dot.edge("t_hostel", "t_hroom", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_hroom", "t_halloc", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_halloc", "t_hfee", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_halloc", "t_hvisit", arrowhead="crow", label="1:N", **edge_style)

# Sports
dot.edge("t_sport", "t_team", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_team", "t_tmember", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_team", "t_sevent", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_team", "t_sach", arrowhead="crow", label="1:N", **edge_style)

# Health
dot.edge(
    "t_student",
    "t_hrec",
    arrowhead="odiamond",
    label="1:1",
    color="#238636",
    fontcolor="#238636",
    fontsize="7",
    arrowsize="0.6",
)
dot.edge("t_hrec", "t_nurse", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_hrec", "t_immun", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_hrec", "t_medlog", arrowhead="crow", label="1:N", **edge_style)

# Library
dot.edge("t_book", "t_checkout", arrowhead="crow", label="1:N", **edge_style)
dot.edge(
    "t_user",
    "t_libpro",
    arrowhead="odiamond",
    label="1:1",
    color="#238636",
    fontcolor="#238636",
    fontsize="7",
    arrowsize="0.6",
)

# Admissions
dot.edge("t_intake", "t_app", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_app", "t_appdoc", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_app", "t_apprev", arrowhead="crow", label="1:N", **edge_style)
dot.edge("t_app", "t_apptl", arrowhead="crow", label="1:N", **edge_style)
dot.edge(
    "t_app",
    "t_entrance",
    arrowhead="odiamond",
    label="1:1",
    color="#238636",
    fontcolor="#238636",
    fontsize="7",
    arrowsize="0.6",
)

# Alumni
dot.edge("t_alumpro", "t_aldon", arrowhead="crow", label="1:N", **edge_style)

# Cafeteria
dot.edge("t_mplan", "t_mbook", arrowhead="crow", label="1:N", **edge_style)


# ═══════════════════════════════════════════════════════════════════════════════
# EDGES — State Machine Transitions
# ═══════════════════════════════════════════════════════════════════════════════

sm_edge = {"color": "#f778ba", "fontcolor": "#f778ba", "fontsize": "7", "arrowsize": "0.6"}

# Admissions state machine
dot.edge("sm_applied", "sm_screening", **sm_edge)
dot.edge("sm_screening", "sm_interview", **sm_edge)
dot.edge("sm_screening", "sm_rejected", **sm_edge)
dot.edge("sm_interview", "sm_offer", **sm_edge)
dot.edge("sm_interview", "sm_rejected", **sm_edge)
dot.edge("sm_interview", "sm_waitlisted", **sm_edge)
dot.edge("sm_offer", "sm_enrolled", **sm_edge)
dot.edge("sm_offer", "sm_withdrawn", **sm_edge)
dot.edge("sm_waitlisted", "sm_offer", **sm_edge)
dot.edge("sm_enrolled", "sm_withdrawn", **sm_edge)

# Fee state machine
dot.edge("sm_draft", "sm_unpaid", **sm_edge)
dot.edge("sm_unpaid", "sm_partial", **sm_edge)
dot.edge("sm_unpaid", "sm_paid", **sm_edge)
dot.edge("sm_partial", "sm_paid", **sm_edge)
dot.edge("sm_unpaid", "sm_overdue", **sm_edge)
dot.edge("sm_overdue", "sm_waived", **sm_edge)

# Grade change state machine
dot.edge("sm_proposed", "sm_approved", **sm_edge)
dot.edge("sm_approved", "sm_published", **sm_edge)
dot.edge("sm_proposed", "sm_grej", **sm_edge)


# ═══════════════════════════════════════════════════════════════════════════════
# EDGES — Cross-Service Dependencies
# ═══════════════════════════════════════════════════════════════════════════════

cross_edge = {
    "style": "dotted",
    "color": "#484f58",
    "fontcolor": "#6e7681",
    "fontsize": "6",
    "arrowsize": "0.5",
    "constraint": "false",
}

# Attendance → Communication (absence notifications)
dot.edge("t_attrec", "t_notif", **cross_edge)

# Fees → Communication (payment notifications)
dot.edge("t_pay", "t_notif", **cross_edge)

# Admissions → Communication (status emails)
dot.edge("t_app", "t_notif", **cross_edge)

# Gradebook → Communication (report cards)
dot.edge("t_rcard", "t_notif", **cross_edge)

# HR → Communication (payroll)
dot.edge("t_payslip", "t_notif", **cross_edge)


# ═══════════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════════

output_dir = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "edusphere_combined_hld_lld")

print("Generating Combined HLD + LLD diagram...")
print(f"  Tables: 105 | Relationships: 166 | Dependencies: 127 | Services: 22")

try:
    dot.render(output_path, cleanup=True)
    print(f"Diagram generated: {output_path}.png")
except Exception as e:
    print(f"Could not render to PNG (Graphviz binary may not be in PATH): {e}")
    dot.save(os.path.join(output_dir, "edusphere_combined_hld_lld.dot"))
    print(f"DOT source saved: {output_dir}/edusphere_combined_hld_lld.dot")
    print("   Install Graphviz system binary and run again:")
    print("   - macOS: brew install graphviz")
    print("   - Linux: apt-get install graphviz")
    print("   - Windows: winget install graphviz (then restart terminal)")
