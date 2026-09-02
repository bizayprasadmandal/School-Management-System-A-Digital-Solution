import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { UserGroupIcon } from "@heroicons/react/24/outline";

interface MentoringPair {
  id: string;
  mentor_name: string;
  mentee_name: string;
  status: "active" | "completed" | "pending";
  sessions_completed: number;
  goals: string;
}

function MentoringSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function PeerMentoringPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [pairs, setPairs] = useState<MentoringPair[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPairs = async () => {
      try {
        const res = await fetch("/api/counseling/peer-mentoring/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setPairs(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchPairs();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Peer Mentoring</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Create Pair
        </button>
      </div>

      {loading ? (
        <MentoringSkeleton />
      ) : pairs.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <UserGroupIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No mentoring pairs</h3>
          <p className="mt-1 text-sm text-gray-400">Pair students for peer mentoring support.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {pairs.map((pair) => (
            <div
              key={pair.id}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4"
            >
              <div>
                <h3 className="font-semibold text-white">
                  {pair.mentor_name} &rarr; {pair.mentee_name}
                </h3>
                <p className="text-sm text-gray-400">{pair.goals}</p>
                <p className="mt-1 text-xs text-gray-500">
                  {pair.sessions_completed} sessions completed
                </p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-medium ${
                  pair.status === "active"
                    ? "bg-green-500/20 text-green-400"
                    : pair.status === "pending"
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-gray-500/20 text-gray-400"
                }`}
              >
                {pair.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
