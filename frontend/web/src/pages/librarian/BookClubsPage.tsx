import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { UserGroupIcon } from "@heroicons/react/24/outline";

interface BookClub {
  id: string;
  name: string;
  book_title: string;
  description: string;
  meeting_day: string;
  members: number;
  status: "active" | "upcoming" | "completed";
}

function BookClubSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function BookClubsPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [clubs, setClubs] = useState<BookClub[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClubs = async () => {
      try {
        const res = await fetch("/api/library/book-clubs/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setClubs(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchClubs();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Book Clubs</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Create Club
        </button>
      </div>

      {loading ? (
        <BookClubSkeleton />
      ) : clubs.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <UserGroupIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No book clubs</h3>
          <p className="mt-1 text-sm text-gray-400">
            Create book clubs to encourage reading among students.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {clubs.map((club) => (
            <div key={club.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-white">{club.name}</h3>
                  <p className="text-sm text-gray-400">Reading: {club.book_title}</p>
                  <p className="text-xs text-gray-500">{club.description}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    Meets {club.meeting_day} &middot; {club.members} members
                  </p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    club.status === "active"
                      ? "bg-green-500/20 text-green-400"
                      : club.status === "upcoming"
                        ? "bg-blue-500/20 text-blue-400"
                        : "bg-gray-500/20 text-gray-400"
                  }`}
                >
                  {club.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
