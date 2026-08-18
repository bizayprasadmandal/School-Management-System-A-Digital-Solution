/**
 * Public Application Form — parents can apply without an account.
 * Route: /apply
 */
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { apiClient } from "../../api/client";

// ─── Schema ──────────────────────────────────────────────────────────────────

const applicationSchema = z.object({
  intake: z.string().min(1, "Please select an intake period"),
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  middle_name: z.string().optional(),
  date_of_birth: z.string().min(1, "Date of birth is required"),
  gender: z.enum(["male", "female", "other"], { required_error: "Gender is required" }),
  nationality: z.string().optional(),
  email: z.string().email("Valid email is required"),
  phone: z.string().min(1, "Phone number is required"),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  postal_code: z.string().optional(),
  previous_school: z.string().optional(),
  previous_grade: z.string().optional(),
  applying_for_grade: z.string().min(1, "Grade applying for is required"),
  gpa: z.coerce.number().min(0).max(100).optional(),
  guardian_name: z.string().min(1, "Guardian name is required"),
  guardian_phone: z.string().min(1, "Guardian phone is required"),
  guardian_email: z.string().email("Valid guardian email is required"),
  guardian_relation: z.string().min(1, "Relationship is required"),
  source: z.string().optional(),
});

type ApplicationForm = z.infer<typeof applicationSchema>;

// ─── Grade options ───────────────────────────────────────────────────────────

const GRADES = [
  "Nursery",
  "LKG",
  "UKG",
  "Grade 1",
  "Grade 2",
  "Grade 3",
  "Grade 4",
  "Grade 5",
  "Grade 6",
  "Grade 7",
  "Grade 8",
  "Grade 9",
  "Grade 10",
  "Grade 11",
  "Grade 12",
];

// ─── Component ───────────────────────────────────────────────────────────────

export default function PublicApplyPage() {
  const [submitted, setSubmitted] = useState<{
    application_number: string;
    intake_name: string;
  } | null>(null);
  const [intakes, setIntakes] = useState<any[]>([]);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<ApplicationForm>({
    resolver: zodResolver(applicationSchema),
  });

  // Load intakes on mount
  React.useEffect(() => {
    apiClient
      .get("/admissions/public/intakes/")
      .then((res) => setIntakes(res.data))
      .catch(() => {});
  }, []);

  const onSubmit = async (data: ApplicationForm) => {
    try {
      const res = await apiClient.post("/admissions/public/apply/", data);
      setSubmitted({
        application_number: res.data.application_number,
        intake_name: res.data.intake_name,
      });
      toast.success("Application submitted!");
      reset();
    } catch (err: any) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.intake?.[0] ||
        "Submission failed. Please try again.";
      toast.error(msg);
    }
  };

  // ── Success screen ──────────────────────────────────────────────────────
  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center p-6">
        <div className="max-w-lg w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Application Submitted!</h2>
          <p className="text-slate-600 mb-6">
            Your application to <strong>{submitted.intake_name}</strong> has been received.
          </p>
          <div className="bg-indigo-50 rounded-xl p-4 mb-6">
            <p className="text-sm text-slate-500 mb-1">Your Application Number</p>
            <p className="text-2xl font-mono font-bold text-indigo-600">
              {submitted.application_number}
            </p>
          </div>
          <p className="text-sm text-slate-500 mb-6">
            Please save this number. You can check your application status at any time.
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => setSubmitted(null)}
              className="px-4 py-2 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors"
            >
              Submit Another Application
            </button>
            <a
              href="/apply/status"
              className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 font-semibold hover:bg-slate-50 transition-colors"
            >
              Check Status
            </a>
          </div>
        </div>
      </div>
    );
  }

  // ── Application form ────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">🎓</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-800">Apply for Admission</h1>
          <p className="text-slate-500 mt-2">Complete the form below to submit your application</p>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="bg-white rounded-2xl shadow-xl p-8 space-y-8"
        >
          {/* Intake Selection */}
          <Section title="Select Intake">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Intake Period *
              </label>
              <select {...register("intake")} className="input-field">
                <option value="">Select an intake period</option>
                {intakes.map((intake: any) => (
                  <option key={intake.id} value={intake.id}>
                    {intake.name} ({intake.academic_year}) — Applications {intake.application_start}{" "}
                    to {intake.application_end}
                  </option>
                ))}
              </select>
              {errors.intake && (
                <p className="text-red-500 text-sm mt-1">{errors.intake.message}</p>
              )}
            </div>
          </Section>

          {/* Student Information */}
          <Section title="Student Information">
            <Field label="First Name *" error={errors.first_name?.message}>
              <input {...register("first_name")} className="input-field" placeholder="First name" />
            </Field>
            <Field label="Last Name *" error={errors.last_name?.message}>
              <input {...register("last_name")} className="input-field" placeholder="Last name" />
            </Field>
            <Field label="Middle Name" error={errors.middle_name?.message}>
              <input
                {...register("middle_name")}
                className="input-field"
                placeholder="Middle name (optional)"
              />
            </Field>
            <Field label="Date of Birth *" error={errors.date_of_birth?.message}>
              <input type="date" {...register("date_of_birth")} className="input-field" />
            </Field>
            <Field label="Gender *" error={errors.gender?.message}>
              <select {...register("gender")} className="input-field">
                <option value="">Select</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </Field>
            <Field label="Nationality" error={errors.nationality?.message}>
              <input
                {...register("nationality")}
                className="input-field"
                placeholder="e.g. Nepali"
              />
            </Field>
          </Section>

          {/* Contact */}
          <Section title="Contact Information">
            <Field label="Email *" error={errors.email?.message}>
              <input
                type="email"
                {...register("email")}
                className="input-field"
                placeholder="student@example.com"
              />
            </Field>
            <Field label="Phone *" error={errors.phone?.message}>
              <input {...register("phone")} className="input-field" placeholder="+977-XXXXXXXXX" />
            </Field>
            <div className="col-span-2">
              <Field label="Address" error={errors.address?.message}>
                <input
                  {...register("address")}
                  className="input-field"
                  placeholder="Street address"
                />
              </Field>
            </div>
            <Field label="City" error={errors.city?.message}>
              <input {...register("city")} className="input-field" placeholder="City" />
            </Field>
            <Field label="State" error={errors.state?.message}>
              <input {...register("state")} className="input-field" placeholder="State/Province" />
            </Field>
            <Field label="Postal Code" error={errors.postal_code?.message}>
              <input
                {...register("postal_code")}
                className="input-field"
                placeholder="Postal code"
              />
            </Field>
          </Section>

          {/* Academic */}
          <Section title="Academic Information">
            <Field label="Applying for Grade *" error={errors.applying_for_grade?.message}>
              <select {...register("applying_for_grade")} className="input-field">
                <option value="">Select grade</option>
                {GRADES.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Previous School" error={errors.previous_school?.message}>
              <input
                {...register("previous_school")}
                className="input-field"
                placeholder="Previous school name"
              />
            </Field>
            <Field label="Previous Grade" error={errors.previous_grade?.message}>
              <input
                {...register("previous_grade")}
                className="input-field"
                placeholder="e.g. Grade 5"
              />
            </Field>
            <Field label="GPA / Percentage" error={errors.gpa?.message}>
              <input
                type="number"
                step="0.01"
                {...register("gpa")}
                className="input-field"
                placeholder="0.00"
              />
            </Field>
          </Section>

          {/* Guardian */}
          <Section title="Guardian / Parent Information">
            <Field label="Guardian Name *" error={errors.guardian_name?.message}>
              <input
                {...register("guardian_name")}
                className="input-field"
                placeholder="Full name"
              />
            </Field>
            <Field label="Relationship *" error={errors.guardian_relation?.message}>
              <input
                {...register("guardian_relation")}
                className="input-field"
                placeholder="e.g. Father, Mother, Guardian"
              />
            </Field>
            <Field label="Guardian Phone *" error={errors.guardian_phone?.message}>
              <input
                {...register("guardian_phone")}
                className="input-field"
                placeholder="+977-XXXXXXXXX"
              />
            </Field>
            <Field label="Guardian Email *" error={errors.guardian_email?.message}>
              <input
                type="email"
                {...register("guardian_email")}
                className="input-field"
                placeholder="guardian@example.com"
              />
            </Field>
          </Section>

          {/* How did you hear about us */}
          <Section title="Additional Information">
            <div className="col-span-2">
              <Field label="How did you hear about us?" error={errors.source?.message}>
                <input
                  {...register("source")}
                  className="input-field"
                  placeholder="e.g. Referral, Online Search, Social Media"
                />
              </Field>
            </div>
          </Section>

          {/* Submit */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-100">
            <a href="/apply/status" className="text-sm text-indigo-600 hover:underline">
              Already applied? Check your status →
            </a>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-8 py-3 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isSubmitting ? "Submitting..." : "Submit Application"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Helper components ───────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-slate-800 mb-4">{title}</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">{children}</div>
    </div>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
      {children}
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
}
