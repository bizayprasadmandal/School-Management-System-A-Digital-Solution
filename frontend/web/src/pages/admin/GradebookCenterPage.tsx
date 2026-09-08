/**
 * Gradebook Center — full-surface admin page for the gradebook module.
 *
 * 32 entity tabs (config-driven via EntitySection). Exams, grades, rubrics, standards, transcripts, report cards, history and analytics.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, AcademicCapIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  // ===== gradebook =====
  assessments: {
    key: "assessments",
    icon: AcademicCapIcon,
    label: "Assessment",
    endpoint: "assessments",
    titleField: "title",
    fields: [
      { key: "assignment", label: "Assignment" },
      { key: "subject_name", label: "Subject Name" },
      { key: "classroom_name", label: "Classroom Name" },
      { key: "title", label: "Title" },
      {
        key: "assessment_type",
        label: "Assessment Type",
        type: "select",
        options: [
          ["homework", "Homework"],
          ["quiz", "Quiz"],
          ["project", "Project"],
          ["classwork", "Classwork"],
          ["lab", "Lab"],
        ],
      },
      { key: "due_date", label: "Due Date", type: "date" },
      { key: "max_marks", label: "Max Marks" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "attachment", label: "Attachment" },
    ],
  },
  "category-assignments": {
    key: "category-assignments",
    icon: AcademicCapIcon,
    label: "Category Assignment",
    endpoint: "category-assignments",
    titleField: "assessment",
    subtitleField: "category",
    fields: [
      { key: "assessment", label: "Assessment" },
      { key: "assessment_title", label: "Assessment Title" },
      { key: "category", label: "Category" },
      { key: "category_name", label: "Category Name" },
    ],
  },
  comments: {
    key: "comments",
    icon: AcademicCapIcon,
    label: "Grade Comment",
    endpoint: "comments",
    titleField: "category",
    fields: [
      {
        key: "category",
        label: "Category",
        type: "select",
        options: [
          ["academic", "Academic"],
          ["behavior", "Behavior"],
          ["attendance", "Attendance"],
          ["work_habits", "Work Habits"],
          ["social", "Social"],
          ["general", "General"],
        ],
      },
      { key: "comment_text", label: "Comment Text" },
      { key: "grade_range_min", label: "Grade Range Min" },
      { key: "grade_range_max", label: "Grade Range Max" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "usage_count", label: "Usage Count" },
    ],
  },
  "course-grades": {
    key: "course-grades",
    icon: AcademicCapIcon,
    label: "Course Grade Calculation",
    endpoint: "course-grades",
    titleField: "subject",
    fields: [
      { key: "gpa_calculation", label: "Gpa Calculation" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "subject_name", label: "Subject Name" },
      { key: "marks_obtained", label: "Marks Obtained" },
      { key: "max_marks", label: "Max Marks" },
      { key: "percentage", label: "Percentage", type: "number" },
      { key: "grade_letter", label: "Grade Letter" },
      { key: "grade_points", label: "Grade Points" },
      { key: "credits", label: "Credits" },
      { key: "is_honors", label: "Is Honors" },
      { key: "is_pass_fail", label: "Is Pass Fail" },
    ],
  },
  "exam-schedules": {
    key: "exam-schedules",
    icon: AcademicCapIcon,
    label: "Exam Schedule",
    endpoint: "exam-schedules",
    titleField: "subject",
    fields: [
      { key: "exam", label: "Exam" },
      { key: "exam_name", label: "Exam Name" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "subject_name", label: "Subject Name" },
      { key: "classroom", label: "Classroom" },
      { key: "classroom_name", label: "Classroom Name" },
      { key: "date", label: "Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "venue", label: "Venue" },
      { key: "invigilator", label: "Invigilator" },
      { key: "max_marks", label: "Max Marks" },
      { key: "passing_marks", label: "Passing Marks" },
    ],
  },
  "exam-types": {
    key: "exam-types",
    icon: AcademicCapIcon,
    label: "Exam Type",
    endpoint: "exam-types",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "weightage", label: "Weightage" },
      { key: "is_terminal", label: "Is Terminal" },
    ],
  },
  exams: {
    key: "exams",
    icon: AcademicCapIcon,
    label: "Exam",
    endpoint: "exams",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "exam_type", label: "Exam Type" },
      { key: "exam_type_name", label: "Exam Type Name" },
      { key: "academic_year", label: "Academic Year" },
      { key: "academic_year_name", label: "Academic Year Name" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["ongoing", "Ongoing"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "schedule_count", label: "Schedule Count" },
    ],
  },
  "extra-credit": {
    key: "extra-credit",
    icon: AcademicCapIcon,
    label: "Extra Credit",
    endpoint: "extra-credit",
    titleField: "title",
    fields: [
      { key: "assessment", label: "Assessment" },
      {
        key: "credit_type",
        label: "Credit Type",
        type: "select",
        options: [
          ["assignment", "Assignment"],
          ["bonus_points", "Bonus Points"],
          ["participation", "Participation"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "max_bonus_marks", label: "Max Bonus Marks" },
      { key: "due_date", label: "Due Date", type: "date" },
    ],
  },
  "extra-credit-submissions": {
    key: "extra-credit-submissions",
    icon: AcademicCapIcon,
    label: "Extra Credit Submission",
    endpoint: "extra-credit-submissions",
    titleField: "extra_credit",
    fields: [
      { key: "extra_credit", label: "Extra Credit" },
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "bonus_marks_obtained", label: "Bonus Marks Obtained" },
      { key: "submitted_at", label: "Submitted At", type: "date" },
      { key: "remarks", label: "Remarks" },
      { key: "graded_at", label: "Graded At", type: "date" },
    ],
  },
  "gpa-calculations": {
    key: "gpa-calculations",
    icon: AcademicCapIcon,
    label: "G P A Calculation",
    endpoint: "gpa-calculations",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "academic_year", label: "Academic Year" },
      { key: "semester", label: "Semester" },
      {
        key: "gpa_type",
        label: "Gpa Type",
        type: "select",
        options: [
          ["semester", "Semester"],
          ["cumulative", "Cumulative"],
          ["weighted", "Weighted"],
          ["unweighted", "Unweighted"],
        ],
      },
      { key: "gpa_value", label: "Gpa Value" },
      { key: "total_grade_points", label: "Total Grade Points" },
      { key: "total_credits", label: "Total Credits" },
      { key: "class_rank", label: "Class Rank" },
      { key: "class_size", label: "Class Size" },
      { key: "percentile_rank", label: "Percentile Rank" },
      { key: "calculated_at", label: "Calculated At", type: "date" },
      { key: "course_grades", label: "Course Grades" },
    ],
  },
  "grade-change-logs": {
    key: "grade-change-logs",
    icon: AcademicCapIcon,
    label: "Grade Change Log",
    endpoint: "grade-change-logs",
    titleField: "changed_by_name",
    fields: [
      { key: "changed_by_name", label: "Changed By Name" },
      {
        key: "action",
        label: "Action",
        type: "select",
        options: [
          ["create", "Create"],
          ["update", "Update"],
          ["delete", "Delete"],
        ],
      },
      { key: "marks_obtained_old", label: "Marks Obtained Old" },
      { key: "marks_obtained_new", label: "Marks Obtained New" },
      { key: "is_absent_old", label: "Is Absent Old" },
      { key: "is_absent_new", label: "Is Absent New" },
      { key: "remarks_old", label: "Remarks Old" },
      { key: "remarks_new", label: "Remarks New" },
      { key: "changed_at", label: "Changed At", type: "date" },
      { key: "student", label: "Student" },
      { key: "exam_schedule", label: "Exam Schedule" },
      { key: "changed_by", label: "Changed By" },
    ],
  },
  "grade-history": {
    key: "grade-history",
    icon: AcademicCapIcon,
    label: "Grade History",
    endpoint: "grade-history",
    titleField: "subject",
    fields: [
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "subject_name", label: "Subject Name" },
      { key: "academic_year", label: "Academic Year" },
      { key: "semester", label: "Semester" },
      { key: "final_marks", label: "Final Marks" },
      { key: "max_marks", label: "Max Marks" },
      { key: "percentage", label: "Percentage", type: "number" },
      { key: "grade_letter", label: "Grade Letter" },
      { key: "grade_points", label: "Grade Points" },
      { key: "is_pass", label: "Is Pass" },
      { key: "teacher_name", label: "Teacher Name" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "recorded_at", label: "Recorded At", type: "date" },
    ],
  },
  grades: {
    key: "grades",
    icon: AcademicCapIcon,
    label: "Grade",
    endpoint: "grades",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "exam_schedule", label: "Exam Schedule" },
      { key: "subject_name", label: "Subject Name" },
      { key: "exam_name", label: "Exam Name" },
      { key: "marks_obtained", label: "Marks Obtained" },
      { key: "max_marks", label: "Max Marks" },
      { key: "percentage", label: "Percentage", type: "number" },
      { key: "is_pass", label: "Is Pass" },
      { key: "is_absent", label: "Is Absent" },
      { key: "remarks", label: "Remarks" },
      { key: "graded_at", label: "Graded At", type: "date" },
    ],
  },
  "grading-categories": {
    key: "grading-categories",
    icon: AcademicCapIcon,
    label: "Grading Category",
    endpoint: "grading-categories",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "weight", label: "Weight" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "subject_name", label: "Subject Name" },
      { key: "academic_year", label: "Academic Year" },
      { key: "drop_lowest", label: "Drop Lowest" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "assignments_count", label: "Assignments Count" },
    ],
  },
  "grading-scale-entries": {
    key: "grading-scale-entries",
    icon: AcademicCapIcon,
    label: "Grading Scale Entry",
    endpoint: "grading-scale-entries",
    titleField: "scale",
    fields: [
      { key: "scale", label: "Scale" },
      { key: "grade_letter", label: "Grade Letter" },
      { key: "min_percentage", label: "Min Percentage" },
      { key: "max_percentage", label: "Max Percentage" },
      { key: "grade_point", label: "Grade Point" },
      { key: "description", label: "Description", type: "textarea" },
    ],
  },
  "grading-scales": {
    key: "grading-scales",
    icon: AcademicCapIcon,
    label: "Grading Scale",
    endpoint: "grading-scales",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "is_default", label: "Is Default", type: "bool" },
      { key: "entries", label: "Entries" },
    ],
  },
  "late-penalties": {
    key: "late-penalties",
    icon: AcademicCapIcon,
    label: "Late Penalty Rule",
    endpoint: "late-penalties",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "penalty_type",
        label: "Penalty Type",
        type: "select",
        options: [
          ["percentage", "Percentage"],
          ["fixed", "Fixed"],
          ["per_day", "Per Day"],
          ["stepwise", "Stepwise"],
        ],
      },
      { key: "penalty_value", label: "Penalty Value" },
      { key: "max_penalty", label: "Max Penalty" },
      { key: "grace_period_hours", label: "Grace Period Hours" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "academic_year", label: "Academic Year" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "mastery-scales": {
    key: "mastery-scales",
    icon: AcademicCapIcon,
    label: "Standard Mastery Scale",
    endpoint: "mastery-scales",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "levels", label: "Levels" },
      { key: "is_default", label: "Is Default", type: "bool" },
    ],
  },
  notifications: {
    key: "notifications",
    icon: AcademicCapIcon,
    label: "Grade Notification",
    endpoint: "notifications",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      {
        key: "notification_type",
        label: "Notification Type",
        type: "select",
        options: [
          ["grade_posted", "Grade Posted"],
          ["grade_changed", "Grade Changed"],
          ["missing_assignment", "Missing Assignment"],
          ["grade_warning", "Grade Warning"],
          ["report_card", "Report Card"],
          ["transcript", "Transcript"],
        ],
      },
      {
        key: "channel",
        label: "Channel",
        type: "select",
        options: [
          ["email", "Email"],
          ["sms", "Sms"],
          ["push", "Push"],
          ["in_app", "In App"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "message", label: "Message", type: "textarea" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "subject_name", label: "Subject Name" },
      { key: "grade_value", label: "Grade Value" },
      { key: "previous_grade", label: "Previous Grade" },
      { key: "status", label: "Status" },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "read_at", label: "Read At", type: "date" },
    ],
  },
  proposals: {
    key: "proposals",
    icon: AcademicCapIcon,
    label: "Grade Change Proposal",
    endpoint: "proposals",
    titleField: "subject",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "admission_number", label: "Admission Number" },
      { key: "exam_schedule", label: "Exam Schedule" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "exam", label: "Exam" },
      { key: "max_marks", label: "Max Marks" },
      {
        key: "action",
        label: "Action",
        type: "select",
        options: [
          ["create", "Create"],
          ["update", "Update"],
          ["delete", "Delete"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["proposed", "Proposed"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
        ],
      },
      { key: "marks_obtained_new", label: "Marks Obtained New" },
      { key: "marks_obtained_current", label: "Marks Obtained Current" },
      { key: "is_absent_new", label: "Is Absent New" },
      { key: "remarks_new", label: "Remarks New" },
      { key: "reason", label: "Reason" },
      { key: "proposed_by", label: "Proposed By" },
      { key: "proposed_at", label: "Proposed At", type: "date" },
      { key: "reviewed_by", label: "Reviewed By" },
      { key: "reviewed_at", label: "Reviewed At", type: "date" },
      { key: "review_notes", label: "Review Notes" },
    ],
  },
  "report-card-comments": {
    key: "report-card-comments",
    icon: AcademicCapIcon,
    label: "Report Card Comment",
    endpoint: "report-card-comments",
    titleField: "report_card",
    fields: [
      { key: "report_card", label: "Report Card" },
      { key: "comment", label: "Comment" },
      { key: "comment_text", label: "Comment Text" },
      { key: "custom_text", label: "Custom Text" },
      { key: "added_at", label: "Added At", type: "date" },
    ],
  },
  "report-cards": {
    key: "report-cards",
    icon: AcademicCapIcon,
    label: "Report Card",
    endpoint: "report-cards",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "student_admission_number", label: "Student Admission Number" },
      { key: "exam", label: "Exam" },
      { key: "exam_name", label: "Exam Name" },
      { key: "academic_year", label: "Academic Year" },
      { key: "academic_year_name", label: "Academic Year Name" },
      { key: "total_marks", label: "Total Marks" },
      { key: "obtained_marks", label: "Obtained Marks" },
      { key: "percentage", label: "Percentage", type: "number" },
      { key: "grade_letter", label: "Grade Letter" },
      { key: "gpa", label: "Gpa" },
      { key: "rank_in_class", label: "Rank In Class" },
      { key: "rank_in_grade", label: "Rank In Grade" },
      { key: "attendance_percentage", label: "Attendance Percentage" },
      { key: "teacher_remarks", label: "Teacher Remarks" },
      { key: "principal_remarks", label: "Principal Remarks" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["published", "Published"],
          ["sent", "Sent"],
        ],
      },
      { key: "pdf_url", label: "Pdf Url" },
      { key: "generated_at", label: "Generated At", type: "date" },
      { key: "published_at", label: "Published At", type: "date" },
    ],
  },
  "rubric-assessments": {
    key: "rubric-assessments",
    icon: AcademicCapIcon,
    label: "Rubric Assessment",
    endpoint: "rubric-assessments",
    titleField: "assessment",
    fields: [
      { key: "assessment", label: "Assessment" },
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "rubric_template", label: "Rubric Template" },
      { key: "total_score", label: "Total Score" },
      { key: "graded_at", label: "Graded At", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "scores", label: "Scores" },
    ],
  },
  "rubric-criteria": {
    key: "rubric-criteria",
    icon: AcademicCapIcon,
    label: "Rubric Criterion",
    endpoint: "rubric-criteria",
    titleField: "name",
    fields: [
      { key: "template", label: "Template" },
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "max_score", label: "Max Score" },
      { key: "order", label: "Order" },
      { key: "levels", label: "Levels" },
    ],
  },
  "rubric-levels": {
    key: "rubric-levels",
    icon: AcademicCapIcon,
    label: "Rubric Level",
    endpoint: "rubric-levels",
    titleField: "name",
    fields: [
      { key: "criterion", label: "Criterion" },
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "score", label: "Score", type: "number" },
      { key: "order", label: "Order" },
    ],
  },
  "rubric-scores": {
    key: "rubric-scores",
    icon: AcademicCapIcon,
    label: "Rubric Score",
    endpoint: "rubric-scores",
    titleField: "rubric_assessment",
    fields: [
      { key: "rubric_assessment", label: "Rubric Assessment" },
      { key: "criterion", label: "Criterion" },
      { key: "criterion_name", label: "Criterion Name" },
      { key: "selected_level", label: "Selected Level" },
      { key: "score", label: "Score", type: "number" },
      { key: "feedback", label: "Feedback" },
    ],
  },
  "rubric-templates": {
    key: "rubric-templates",
    icon: AcademicCapIcon,
    label: "Rubric Template",
    endpoint: "rubric-templates",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "criteria_count", label: "Criteria Count" },
    ],
  },
  "standard-grades": {
    key: "standard-grades",
    icon: AcademicCapIcon,
    label: "Student Standard Grade",
    endpoint: "standard-grades",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "standard", label: "Standard" },
      { key: "standard_code", label: "Standard Code" },
      { key: "standard_name", label: "Standard Name" },
      {
        key: "mastery_level",
        label: "Mastery Level",
        type: "select",
        options: [
          ["exceeding", "Exceeding"],
          ["meeting", "Meeting"],
          ["approaching", "Approaching"],
          ["beginning", "Beginning"],
          ["not_yet", "Not Yet"],
        ],
      },
      { key: "score", label: "Score", type: "number" },
      { key: "evidence", label: "Evidence" },
      { key: "graded_at", label: "Graded At", type: "date" },
    ],
  },
  standards: {
    key: "standards",
    icon: AcademicCapIcon,
    label: "Standard",
    endpoint: "standards",
    titleField: "name",
    fields: [
      { key: "code", label: "Code" },
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "standard_type",
        label: "Standard Type",
        type: "select",
        options: [
          ["course", "Course"],
          ["grade_level", "Grade Level"],
          ["district", "District"],
          ["state", "State"],
        ],
      },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  submissions: {
    key: "submissions",
    icon: AcademicCapIcon,
    label: "Assessment Submission",
    endpoint: "submissions",
    titleField: "assessment",
    fields: [
      { key: "assessment", label: "Assessment" },
      { key: "assessment_title", label: "Assessment Title" },
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "marks_obtained", label: "Marks Obtained" },
      { key: "submitted_at", label: "Submitted At", type: "date" },
      { key: "file", label: "File" },
      { key: "remarks", label: "Remarks" },
      { key: "is_late", label: "Is Late" },
      { key: "percentage", label: "Percentage", type: "number" },
    ],
  },
  "transcript-entries": {
    key: "transcript-entries",
    icon: AcademicCapIcon,
    label: "Transcript Entry",
    endpoint: "transcript-entries",
    titleField: "subject",
    fields: [
      { key: "transcript", label: "Transcript" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "subject_name", label: "Subject Name" },
      { key: "academic_year", label: "Academic Year" },
      { key: "semester", label: "Semester" },
      { key: "marks_obtained", label: "Marks Obtained" },
      { key: "max_marks", label: "Max Marks" },
      { key: "percentage", label: "Percentage", type: "number" },
      { key: "grade_letter", label: "Grade Letter" },
      { key: "grade_points", label: "Grade Points" },
      { key: "credits", label: "Credits" },
      { key: "is_honors", label: "Is Honors" },
      { key: "is_repeated", label: "Is Repeated" },
    ],
  },
  transcripts: {
    key: "transcripts",
    icon: AcademicCapIcon,
    label: "Transcript",
    endpoint: "transcripts",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "student_name", label: "Student Name" },
      { key: "academic_year", label: "Academic Year" },
      { key: "transcript_number", label: "Transcript Number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["final", "Final"],
          ["requested", "Requested"],
          ["sent", "Sent"],
        ],
      },
      { key: "cumulative_gpa", label: "Cumulative Gpa" },
      { key: "class_rank", label: "Class Rank" },
      { key: "class_size", label: "Class Size" },
      { key: "total_credits_earned", label: "Total Credits Earned" },
      { key: "graduation_date", label: "Graduation Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "issued_at", label: "Issued At", type: "date" },
      { key: "entries", label: "Entries" },
    ],
  },
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: AcademicCapIcon,
}));

export default function GradebookCenterPage() {
  useTitle("Gradebook Center");
  useShortcutHelp();
  const [activeTab, setActiveTab] = useState(TABS[0]?.key ?? "");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const [helpOpen, setHelpOpen] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const actionRef = useRef<{ add?: () => void; export?: () => void }>({});

  useEffect(() => {
    setPage(1);
  }, [activeTab]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
        return;
      }
      if (e.key === "/") {
        e.preventDefault();
        searchRef.current?.focus();
      } else if (e.key.toLowerCase() === "n") {
        e.preventDefault();
        actionRef.current.add?.();
      } else if (e.key.toLowerCase() === "e") {
        e.preventDefault();
        actionRef.current.export?.();
      } else if (e.key.toLowerCase() === "p") {
        e.preventDefault();
        setViewMode((v) => (v === "pagination" ? "infinite" : "pagination"));
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const activeCfg = ENTITY_CONFIGS[activeTab];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Gradebook Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Exams, grades, rubrics, standards, transcripts, report cards, history and analytics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              ref={searchRef}
              type="search"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search…  ( / )"
              className="w-56 rounded-xl border border-slate-200 bg-white px-4 py-2 pl-9 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </div>
          <div className="flex items-center gap-1 rounded-xl border border-slate-200 p-1 dark:border-slate-600">
            <button
              onClick={() => setViewMode("pagination")}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                viewMode === "pagination"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              Paginated
            </button>
            <button
              onClick={() => setViewMode("infinite")}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                viewMode === "infinite"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              Infinite
            </button>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setHelpOpen(true)}
            leftIcon={<AcademicCapIcon className="h-4 w-4" />}
          >
            Shortcuts
          </Button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-medium transition ${
              activeTab === t.key
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-white text-slate-600 hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            }`}
          >
            <t.icon className="h-4 w-4" />
            {t.label}
          </button>
        ))}
      </div>

      <EntitySection
        cfg={activeCfg}
        basePath="/gradebook"
        search={search}
        page={page}
        setPage={setPage}
        viewMode={viewMode}
        registerActions={(h) => {
          actionRef.current = h;
        }}
      />

      <KeyboardShortcutHelp
        open={helpOpen}
        onClose={() => setHelpOpen(false)}
        shortcuts={[
          { keys: ["N"], label: "New", description: "New record" },
          { keys: ["/"], label: "Search", description: "Focus search" },
          { keys: ["E"], label: "Export", description: "Export CSV" },
          {
            keys: ["P"],
            label: "Pages",
            description: "Toggle pagination / infinite scroll",
          },
        ]}
      />
    </div>
  );
}
