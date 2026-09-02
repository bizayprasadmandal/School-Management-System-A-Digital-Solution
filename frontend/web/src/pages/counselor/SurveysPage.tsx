import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { ShieldCheckIcon } from "@heroicons/react/24/outline";

interface Survey {
  id: string;
  title: string;
  description: string;
  status: "active" | "draft" | "closed";
  responses: number;
  created_at: string;
}

function SurveySkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function SurveysPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSurveys = async () => {
      try {
        const res = await fetch("/api/counseling/surveys/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setSurveys(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchSurveys();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Wellness Surveys</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Create Survey
        </button>
      </div>

      {loading ? (
        <SurveySkeleton />
      ) : surveys.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <ShieldCheckIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No surveys yet</h3>
          <p className="mt-1 text-sm text-gray-400">
            Create wellness surveys to gather student feedback.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {surveys.map((survey) => (
            <div
              key={survey.id}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4"
            >
              <div>
                <h3 className="font-semibold text-white">{survey.title}</h3>
                <p className="text-sm text-gray-400">{survey.description}</p>
                <p className="mt-1 text-xs text-gray-500">{survey.responses} responses</p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-medium ${
                  survey.status === "active"
                    ? "bg-green-500/20 text-green-400"
                    : survey.status === "draft"
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-gray-500/20 text-gray-400"
                }`}
              >
                {survey.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
