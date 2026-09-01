/**
 * Student Transport Page — View bus route, schedule, and tracking.
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { TruckIcon, MapPinIcon, ClockIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface RouteAssignment {
  id: string;
  route_name: string;
  pickup_point: string;
  dropoff_point: string;
  pickup_time: string;
  dropoff_time: string;
  bus_number: string;
  driver_name: string;
  is_active: boolean;
}

export default function StudentTransportPage() {
  useTitle("Transport");
  const { data: assignment, isLoading } = useQuery({
    queryKey: ["student-transport"],
    queryFn: async () => {
      const r = await api.get<{ results: RouteAssignment[] }>("/transportation/assignments/my/");
      return r.results?.[0] ?? null;
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Transport</h1>
        <p className="text-sm text-slate-500 mt-1">Your bus route and schedule</p>
      </div>

      {isLoading ? (
        <div className="h-48 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
      ) : !assignment ? (
        <EmptyState
          icon={TruckIcon}
          title="No transport assigned"
          description="You don't have a bus route assigned yet"
        />
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                {assignment.route_name}
              </h2>
              <p className="text-sm text-slate-500">Bus: {assignment.bus_number}</p>
            </div>
            <Badge color={assignment.is_active ? "green" : "slate"}>
              {assignment.is_active ? "Active" : "Inactive"}
            </Badge>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <MapPinIcon className="h-5 w-5 text-green-600" />
                <p className="font-semibold text-green-800 dark:text-green-300">Pickup</p>
              </div>
              <p className="text-sm text-slate-700 dark:text-slate-300">
                {assignment.pickup_point}
              </p>
              <p className="text-lg font-bold text-green-600 dark:text-green-400 mt-1">
                {assignment.pickup_time}
              </p>
            </div>
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <MapPinIcon className="h-5 w-5 text-blue-600" />
                <p className="font-semibold text-blue-800 dark:text-blue-300">Drop-off</p>
              </div>
              <p className="text-sm text-slate-700 dark:text-slate-300">
                {assignment.dropoff_point}
              </p>
              <p className="text-lg font-bold text-blue-600 dark:text-blue-400 mt-1">
                {assignment.dropoff_time}
              </p>
            </div>
          </div>
          {assignment.driver_name && (
            <div className="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-4">
              <div className="flex items-center gap-2">
                <ClockIcon className="h-4 w-4 text-slate-400" />
                <p className="text-sm text-slate-600 dark:text-slate-300">
                  Driver: <span className="font-semibold">{assignment.driver_name}</span>
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
