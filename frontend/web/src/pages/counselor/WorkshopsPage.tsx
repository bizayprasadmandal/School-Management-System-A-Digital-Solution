import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { AcademicCapIcon } from "@heroicons/react/24/outline";

interface Workshop {
  id: string;
  title: string;
  description: string;
  date: string;
  facilitator: string;
  attendees: number;
  max_attendees: number;
}

function WorkshopSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function WorkshopsPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [workshops, setWorkshops] = useState<Workshop[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWorkshops = async () => {
      try {
        const res = await fetch("/api/counseling/workshops/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setWorkshops(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchWorkshops();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Workshops</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Schedule Workshop
        </button>
      </div>

      {loading ? (
        <WorkshopSkeleton />
      ) : workshops.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <AcademicCapIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No workshops</h3>
          <p className="mt-1 text-sm text-gray-400">Schedule workshops for student development.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {workshops.map((ws) => (
            <div key={ws.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-white">{ws.title}</h3>
                  <p className="text-sm text-gray-400">{ws.description}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    {ws.facilitator} &middot; {new Date(ws.date).toLocaleDateString()}
                  </p>
                </div>
                <span className="text-sm text-gray-400">
                  {ws.attendees}/{ws.max_attendees}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
