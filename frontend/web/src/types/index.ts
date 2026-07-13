// ─── Auth & Users ────────────────────────────────────────────────────────────

export type UserRole =
  | "super_admin"
  | "school_admin"
  | "teacher"
  | "student"
  | "parent"
  | "accountant"
  | "librarian"
  | "counselor";

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  avatar?: string;
  role: UserRole;
  school?: School;
  is_active: boolean;
  email_verified: boolean;
  two_factor_enabled: boolean;
  backup_codes_remaining: number | null;
  notify_email: boolean;
  notify_sms: boolean;
  notify_push: boolean;
  date_joined: string;
}

export interface School {
  id: string;
  name: string;
  code: string;
  subdomain: string;
  logo?: string;
  address: string;
  phone: string;
  email: string;
  website?: string;
  timezone: string;
  subscription_tier: "basic" | "standard" | "premium";
  is_active: boolean;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

// ─── Academic Structure ────────────────────────────────────────────────────────

export interface AcademicYear {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
}

export interface GradeLevel {
  id: number;
  name: string;
  level: number;
  description?: string;
  classroom_count: number;
  student_count: number;
}

export interface Classroom {
  id: number;
  name: string;
  grade: number;
  grade_name: string;
  capacity: number;
  room_number?: string;
  class_teacher?: number;
  teacher_name?: string;
  student_count: number;
  academic_year: number;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  description?: string;
  grade: number;
  is_core: boolean;
  is_elective: boolean;
  max_marks: number;
  pass_marks: number;
  credit_hours: number;
}

// ─── Students ────────────────────────────────────────────────────────────────

export type Gender = "M" | "F" | "O";
export type BloodGroup = "A+" | "A-" | "B+" | "B-" | "AB+" | "AB-" | "O+" | "O-";

export interface StudentListItem {
  id: string;
  admission_number: string;
  full_name: string;
  email: string;
  avatar?: string;
  gender: Gender;
  current_class?: string;
  is_active: boolean;
}

export interface StudentDetail {
  id: string;
  admission_number: string;
  roll_number?: string;
  full_name: string;
  email: string;
  phone?: string;
  avatar?: string;
  date_of_birth: string;
  gender: Gender;
  blood_group?: BloodGroup;
  nationality: string;
  religion?: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code?: string;
  admission_date: string;
  age: number;
  medical_conditions?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  previous_school?: string;
  is_active: boolean;
  guardians: StudentGuardian[];
  enrollments: Enrollment[];
  created_at: string;
  updated_at: string;
}

export interface Guardian {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  alternate_phone?: string;
  occupation?: string;
  address?: string;
  is_primary: boolean;
}

export interface StudentGuardian {
  guardian: Guardian;
  relationship: string;
  is_primary_contact: boolean;
  has_pickup_permission: boolean;
  portal_access: boolean;
}

export interface Enrollment {
  id: number;
  classroom: number;
  classroom_name: string;
  academic_year: number;
  academic_year_name: string;
  status: "active" | "transferred" | "graduated" | "withdrawn" | "suspended";
  enrollment_date: string;
}

// ─── Attendance ────────────────────────────────────────────────────────────────

export type AttendanceStatus = "P" | "A" | "L" | "E" | "H";

export interface AttendanceRecord {
  id: number;
  student: string;
  classroom: number;
  date: string;
  status: AttendanceStatus;
  recorded_by?: number;
  recorded_at: string;
  remarks?: string;
  notified_guardian: boolean;
}

export interface BulkAttendanceEntry {
  student_id: string;
  status: AttendanceStatus;
  remarks?: string;
}

export interface AttendanceSummary {
  total_days: number;
  present: number;
  absent: number;
  late: number;
  excused: number;
  attendance_percentage: number;
}

export interface ClassroomAttendanceSummary {
  date: string;
  total_students: number;
  recorded: number;
  not_recorded: number;
  breakdown: {
    present: number;
    absent: number;
    late: number;
    excused: number;
  };
}

// ─── Gradebook ────────────────────────────────────────────────────────────────

export interface Exam {
  id: string;
  name: string;
  exam_type: number;
  exam_type_name: string;
  start_date: string;
  end_date: string;
  schedule_count: number;
  status: "scheduled" | "ongoing" | "completed" | "cancelled";
}

export interface GradeRecord {
  id: number;
  student: string;
  exam_schedule: number;
  marks_obtained?: number;
  is_absent: boolean;
  remarks?: string;
  graded_at: string;
  percentage?: number;
  is_pass: boolean;
}

export interface ReportCard {
  id: string;
  student: string;
  exam: string;
  exam_name: string;
  academic_year_name: string;
  total_marks: number;
  obtained_marks: number;
  percentage: number;
  grade_letter: string;
  gpa?: number;
  rank_in_class?: number;
  attendance_percentage?: number;
  teacher_remarks?: string;
  status: "draft" | "published" | "sent";
  pdf_url?: string;
  pdf_file?: string;
  published_at?: string;
}

// ─── Timetable ────────────────────────────────────────────────────────────────

export interface TimetableSlot {
  id: number;
  classroom: number;
  assignment: number;
  period: number;
  day_of_week: 0 | 1 | 2 | 3 | 4 | 5;
  subject_name: string;
  teacher_name: string;
  start_time: string;
  end_time: string;
  room?: string;
}

export interface SchoolEvent {
  id: number;
  title: string;
  description?: string;
  event_type: string;
  start_date: string;
  end_date: string;
  start_time?: string;
  end_time?: string;
  venue?: string;
  is_school_wide: boolean;
}

// ─── Communication ────────────────────────────────────────────────────────────

export interface Announcement {
  id: string;
  title: string;
  content: string;
  priority: "low" | "normal" | "high" | "urgent";
  audience: "all" | "teachers" | "students" | "parents" | "staff";
  created_at: string;
  published_at?: string;
  view_count: number;
}

export interface DirectMessage {
  id: string;
  sender: {
    id: string;
    full_name: string;
    avatar?: string;
    role: UserRole;
  };
  recipient: {
    id: string;
    full_name: string;
    avatar?: string;
    role: UserRole;
  };
  content: string;
  status: "sent" | "delivered" | "read";
  sent_at: string;
  read_at?: string;
}

export interface Notification {
  id: string;
  title: string;
  body: string;
  channel: "email" | "sms" | "push" | "in_app";
  status: "pending" | "sent" | "delivered" | "failed" | "read";
  reference_type?: string;
  reference_id?: string;
  created_at: string;
  read_at?: string;
}

// ─── Fees ────────────────────────────────────────────────────────────────────

export interface FeeInvoice {
  id: string;
  invoice_number: string;
  student: string;
  due_date: string;
  base_amount: number;
  discount_amount: number;
  late_fee: number;
  total_amount: number;
  paid_amount: number;
  outstanding_amount: number;
  status: "draft" | "unpaid" | "partial" | "paid" | "overdue" | "waived" | "cancelled";
}

export interface Payment {
  id: string;
  invoice: string;
  amount: number;
  payment_method: string;
  status: "pending" | "successful" | "failed" | "refunded";
  receipt_number: string;
  paid_at?: string;
}

// ─── Notification reference types ─────────────────────────────────────────────

/** Reference type for email-verification notifications */
export const VERIFICATION_REF = "email_verification";

// ─── Common ────────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ApiError {
  detail?: string;
  [field: string]: string | string[] | undefined;
}

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface DateRange {
  from: Date;
  to: Date;
}
