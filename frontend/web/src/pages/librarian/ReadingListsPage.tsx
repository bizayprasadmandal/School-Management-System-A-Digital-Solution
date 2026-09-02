import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { ListBulletIcon } from "@heroicons/react/24/outline";

interface ReadingList {
  id: string;
  title: string;
  description: string;
  grade_level: string;
  books_count: number;
  assigned_to: number;
  created_at: string;
}

function ReadingListSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function ReadingListsPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [lists, setLists] = useState<ReadingList[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLists = async () => {
      try {
        const res = await fetch("/api/library/reading-lists/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setLists(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchLists();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Reading Lists</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Create List
        </button>
      </div>

      {loading ? (
        <ReadingListSkeleton />
      ) : lists.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <ListBulletIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No reading lists</h3>
          <p className="mt-1 text-sm text-gray-400">
            Create curated reading lists for different grade levels.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {lists.map((list) => (
            <div
              key={list.id}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4"
            >
              <div>
                <h3 className="font-semibold text-white">{list.title}</h3>
                <p className="text-sm text-gray-400">{list.description}</p>
                <p className="mt-1 text-xs text-gray-500">
                  Grade: {list.grade_level} &middot; {list.books_count} books &middot; Assigned to{" "}
                  {list.assigned_to} students
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
