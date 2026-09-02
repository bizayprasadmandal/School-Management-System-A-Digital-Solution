import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { HeartIcon } from "@heroicons/react/24/outline";

interface SELProgram {
  id: string;
  title: string;
  category: string;
  participants: number;
  status: "active" | "upcoming" | "completed";
  progress: number;
}

function SELSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function SELPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [programs, setPrograms] = useState<SELProgram[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        const res = await fetch("/api/counseling/sel-programs/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setPrograms(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchPrograms();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Social-Emotional Learning</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Create Program
        </button>
      </div>

      {loading ? (
        <SELSkeleton />
      ) : programs.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <HeartIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No SEL programs</h3>
          <p className="mt-1 text-sm text-gray-400">
            Create social-emotional learning programs for students.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {programs.map((program) => (
            <div key={program.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-white">{program.title}</h3>
                  <p className="text-sm text-gray-400">{program.category}</p>
                  <p className="mt-1 text-xs text-gray-500">{program.participants} participants</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${
                      program.status === "active"
                        ? "bg-green-500/20 text-green-400"
                        : program.status === "upcoming"
                          ? "bg-blue-500/20 text-blue-400"
                          : "bg-gray-500/20 text-gray-400"
                    }`}
                  >
                    {program.status}
                  </span>
                  <div className="h-2 w-24 overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-blue-500"
                      style={{ width: `${program.progress}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
