/**
 * Public Application Status — parents check status by application number.
 * Route: /apply/status
 */
import React, { useState } from "react";
import { apiClient } from "../../api/client";
import toast from "react-hot-toast";

interface TimelineEvent {
  stage: string;
  stage_display: string;
  note: string;
  created_at: string;
}

interface ApplicationStatus {
  application_number: string;
  status: string;
  status_display: string;
  first_name: string;
  last_name: string;
  intake_name: string;
  applying_for_grade: string;
  submitted_at: string;
  offer_deadline: string | null;
  timeline: TimelineEvent[];
}

const STATUS_COLORS: Record<string, string> = {
  submitted: "bg-blue-100 text-blue-700",
  under_review: "bg-yellow-100 text-yellow-700",
  shortlisted: "bg-purple-100 text-purple-700",
  accepted: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  waitlisted: "bg-orange-100 text-orange-700",
  enrolled: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-500",
  draft: "bg-slate-100 text-slate-500",
};

export default function PublicStatusPage() {
  const [appNumber, setAppNumber] = useState("");
  const [result, setResult] = useState<ApplicationStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!appNumber.trim()) return;

    setLoading(true);
    setResult(null);
    setSearched(true);
    try {
      const res = await apiClient.get(`/admissions/public/status/${appNumber.trim()}/`);
      setResult(res.data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        toast.error("Application not found. Please check your application number.");
      } else {
        toast.error("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-7 h-7 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-slate-800">Check Application Status</h1>
          <p className="text-slate-500 mt-2">
            Enter your application number to view the current status
          </p>
        </div>

        {/* Search form */}
        <form onSubmit={handleSearch} className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={appNumber}
              onChange={(e) => setAppNumber(e.target.value)}
              placeholder="e.g. APP-202608-A1B2C3"
              className="input-field flex-1"
              autoFocus
            />
            <button
              type="submit"
              disabled={loading || !appNumber.trim()}
              className="px-6 py-2 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
        </form>

        {/* Result */}
        {result && (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            {/* Status banner */}
            <div className="p-6 border-b border-slate-100">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm text-slate-500">Application Number</p>
                  <p className="text-xl font-mono font-bold text-slate-800">
                    {result.application_number}
                  </p>
                </div>
                <span
                  className={`px-4 py-1.5 rounded-full text-sm font-semibold ${
                    STATUS_COLORS[result.status] || "bg-slate-100 text-slate-600"
                  }`}
                >
                  {result.status_display}
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-slate-500">Student</p>
                  <p className="font-medium text-slate-800">
                    {result.first_name} {result.last_name}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500">Intake</p>
                  <p className="font-medium text-slate-800">{result.intake_name}</p>
                </div>
                <div>
                  <p className="text-slate-500">Grade</p>
                  <p className="font-medium text-slate-800">{result.applying_for_grade}</p>
                </div>
                <div>
                  <p className="text-slate-500">Submitted</p>
                  <p className="font-medium text-slate-800">
                    {result.submitted_at ? new Date(result.submitted_at).toLocaleDateString() : "—"}
                  </p>
                </div>
              </div>
              {result.offer_deadline && (
                <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm">
                  <span className="font-semibold text-amber-700">Offer Deadline: </span>
                  <span className="text-amber-800">
                    {new Date(result.offer_deadline).toLocaleDateString()} — Please respond before
                    this date.
                  </span>
                </div>
              )}
            </div>

            {/* Timeline */}
            {result.timeline.length > 0 && (
              <div className="p-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Timeline</h3>
                <div className="space-y-4">
                  {result.timeline.map((event, idx) => (
                    <div key={idx} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div
                          className={`w-3 h-3 rounded-full mt-1.5 ${
                            idx === 0 ? "bg-indigo-600" : "bg-slate-300"
                          }`}
                        />
                        {idx < result.timeline.length - 1 && (
                          <div className="w-px flex-1 bg-slate-200 mt-1" />
                        )}
                      </div>
                      <div className="pb-4">
                        <p className="font-medium text-slate-800">{event.stage_display}</p>
                        <p className="text-sm text-slate-500">
                          {new Date(event.created_at).toLocaleString()}
                        </p>
                        {event.note && <p className="text-sm text-slate-600 mt-1">{event.note}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* No results yet */}
        {searched && !result && !loading && (
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <p className="text-slate-500">No application found with that number.</p>
            <a href="/apply" className="text-indigo-600 hover:underline mt-2 inline-block">
              Submit a new application →
            </a>
          </div>
        )}

        {/* Footer link */}
        <div className="text-center mt-6">
          <a href="/apply" className="text-sm text-indigo-600 hover:underline">
            ← Back to Application Form
          </a>
        </div>
      </div>
    </div>
  );
}
