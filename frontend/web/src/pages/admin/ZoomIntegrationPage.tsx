/**
 * Zoom Integration Settings Page
 * Configure Zoom Server-to-Server OAuth with Account ID, Client ID, Client Secret.
 * Zoom deprecated API Key/Secret — this uses the new OAuth flow.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  VideoCameraIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  LinkIcon,
} from "@heroicons/react/24/outline";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, Input, Badge, Modal } from "../../components/common";

interface ZoomConnectionStatus {
  status: "connected" | "disconnected" | "error";
  detail: string;
  user?: {
    id: string;
    email: string;
    display_name: string;
  } | null;
}

interface ZoomMeeting {
  id: string;
  topic: string;
  join_url: string;
  start_url: string;
  password: string;
  duration: number;
  start_time: string;
}

export default function ZoomIntegrationPage() {
  const qc = useQueryClient();
  const [showConfig, setShowConfig] = useState(false);
  const [form, setForm] = useState({ account_id: "", client_id: "", client_secret: "" });

  // Fetch Zoom connection status
  const { data: status, isLoading, refetch } = useQuery<ZoomConnectionStatus>({
    queryKey: ["zoom-connection"],
    queryFn: () => api.get<ZoomConnectionStatus>("/conferences/zoom/connection/"),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  // Fetch upcoming Zoom meetings
  const { data: meetingsData } = useQuery<{ meetings: ZoomMeeting[] }>({
    queryKey: ["zoom-meetings"],
    queryFn: () => api.get<{ meetings: ZoomMeeting[] }>("/conferences/zoom/meetings/"),
    enabled: status?.status === "connected",
    staleTime: 60_000,
  });

  // Test / save Zoom credentials
  const testMut = useMutation({
    mutationFn: (data: typeof form) =>
      api.post<{ status: string; detail: string; user?: any }>("/conferences/zoom/connection/", data),
    onSuccess: (data) => {
      if (data.status === "success") {
        toast.success("Zoom credentials verified successfully!");
        setShowConfig(false);
        qc.invalidateQueries({ queryKey: ["zoom-connection"] });
      } else {
        toast.error(data.detail || "Failed to connect");
      }
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Failed to verify Zoom credentials");
    },
  });

  const isConnected = status?.status === "connected";
  const meetings = meetingsData?.meetings ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Zoom Integration</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Configure Zoom Server-to-Server OAuth for video conferencing
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => refetch()}>
            <ArrowPathIcon className="h-4 w-4 mr-1.5" /> Refresh
          </Button>
          <Button onClick={() => setShowConfig(true)}>
            <LinkIcon className="h-4 w-4 mr-1.5" /> Configure
          </Button>
        </div>
      </div>

      {/* Connection Status Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-xl ${
            isConnected
              ? "bg-green-100 dark:bg-green-900/30"
              : "bg-slate-100 dark:bg-slate-700"
          }`}>
            <VideoCameraIcon className={`h-8 w-8 ${
              isConnected ? "text-green-600 dark:text-green-400" : "text-slate-400"
            }`} />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Zoom API</h2>
              {isLoading ? (
                <div className="h-5 w-20 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
              ) : (
                <Badge color={isConnected ? "green" : status?.status === "error" ? "red" : "slate"} dot>
                  {isConnected ? "Connected" : status?.status === "error" ? "Error" : "Disconnected"}
                </Badge>
              )}
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {status?.detail || "Checking connection..."}
            </p>
            {isConnected && status?.user && (
              <div className="mt-3 flex flex-wrap gap-4 text-sm">
                <div>
                  <span className="text-slate-400 dark:text-slate-500">Account: </span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">{status.user.display_name}</span>
                </div>
                <div>
                  <span className="text-slate-400 dark:text-slate-500">Email: </span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">{status.user.email}</span>
                </div>
              </div>
            )}
            {!isConnected && !isLoading && (
              <button
                onClick={() => setShowConfig(true)}
                className="mt-3 text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
              >
                Configure Zoom credentials →
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Configuration Modal */}
      <Modal open={showConfig} onClose={() => setShowConfig(false)} title="Zoom API Configuration">
        <div className="space-y-4">
          <div className="rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-4">
            <div className="flex gap-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-amber-800 dark:text-amber-300">Zoom's New OAuth Credentials</p>
                <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">
                  Zoom no longer provides API Key &amp; Secret. Create a <strong>Server-to-Server OAuth</strong> app in the
                  Zoom Marketplace to get your Account ID, Client ID, and Client Secret.
                </p>
                <a
                  href="https://marketplace.zoom.us/develop/create"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 mt-2"
                >
                  Create Zoom App →
                </a>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Account ID</label>
            <input
              value={form.account_id}
              onChange={(e) => setForm((p) => ({ ...p, account_id: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200 font-mono"
              placeholder="Enter your Zoom Account ID"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Client ID</label>
            <input
              value={form.client_id}
              onChange={(e) => setForm((p) => ({ ...p, client_id: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200 font-mono"
              placeholder="Enter your Zoom Client ID"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Client Secret</label>
            <input
              type="password"
              value={form.client_secret}
              onChange={(e) => setForm((p) => ({ ...p, client_secret: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200 font-mono"
              placeholder="Enter your Zoom Client Secret"
            />
          </div>
          <p className="text-xs text-slate-400 dark:text-slate-500">
            These credentials are tested but not stored server-side. Set them as environment variables
            (<code className="text-indigo-600 dark:text-indigo-400">ZOOM_ACCOUNT_ID</code>,{" "}
            <code className="text-indigo-600 dark:text-indigo-400">ZOOM_CLIENT_ID</code>,{" "}
            <code className="text-indigo-600 dark:text-indigo-400">ZOOM_CLIENT_SECRET</code>)
            in production for persistent configuration.
          </p>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setShowConfig(false)} disabled={testMut.isPending}>
              Cancel
            </Button>
            <Button
              onClick={() => testMut.mutate(form)}
              loading={testMut.isPending}
              disabled={!form.account_id || !form.client_id || !form.client_secret}
            >
  Test Connection
            </Button>
          </div>
        </div>
      </Modal>

      {/* Upcoming Zoom Meetings */}
      {isConnected && (
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-700">
            <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
              Upcoming Zoom Meetings ({meetings.length})
            </h2>
          </div>
          <div className="p-6">
            {meetings.length === 0 ? (
              <div className="text-center py-8">
                <VideoCameraIcon className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
                <p className="text-sm text-slate-500 dark:text-slate-400">No upcoming Zoom meetings found</p>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                  Create conference slots with Zoom enabled to schedule meetings
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {meetings.map((meeting) => (
                  <div
                    key={meeting.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex-shrink-0">
                        <VideoCameraIcon className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">
                          {meeting.topic}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          ID: {meeting.id} · {meeting.duration} min
                          {meeting.password && ` · Pass: ${meeting.password}`}
                        </p>
                      </div>
                    </div>
                    <a
                      href={meeting.join_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 transition-colors"
                    >
                      <VideoCameraIcon className="h-3.5 w-3.5" />
                      Join
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
