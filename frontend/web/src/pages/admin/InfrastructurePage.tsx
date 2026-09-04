/**
 * Infrastructure — Admin page for buildings, rooms, work orders, and assets.
 * Full feature set: dark mode, search, pagination/infinite scroll, CSV export,
 * bulk actions, keyboard shortcuts, shimmer skeletons, CRUD modals.
 */
import React, { useState, useMemo, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  BuildingOffice2Icon,
  Square2StackIcon,
  WrenchScrewdriverIcon,
  ArchiveBoxIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Pagination } from "../../components/common";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";
import { useTitle } from "../../hooks";
import { toCsv, downloadCsv } from "../../utils";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Building {
  id: string;
  name: string;
  code: string;
  description: string;
  floors: number;
  year_built: number | null;
  total_area_sqft: number | null;
  address: string;
  status: string;
  status_display?: string;
  is_active: boolean;
  created_at: string;
}

interface Room {
  id: string;
  building: string;
  building_name?: string;
  name: string;
  room_number: string;
  floor: number;
  room_type: string;
  room_type_display?: string;
  status: string;
  status_display?: string;
  capacity: number;
  area_sqft: number | null;
  has_projector: boolean;
  has_smartboard: boolean;
  has_ac: boolean;
  has_wifi: boolean;
  has_computers: boolean;
  computer_count: number;
}

interface WorkOrder {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: string;
  priority_display?: string;
  status: string;
  status_display?: string;
  building: string | null;
  building_name?: string;
  room: string | null;
  room_name?: string;
  reported_by_name?: string;
  assigned_to_name?: string;
  created_at: string;
}

interface Asset {
  id: string;
  asset_tag: string;
  name: string;
  description: string;
  asset_type: string;
  asset_type_display?: string;
  condition: string;
  condition_display?: string;
  status: string;
  status_display?: string;
  building: string | null;
  building_name?: string;
  room: string | null;
  room_name?: string;
  purchase_date: string | null;
  purchase_cost: number | null;
  created_at: string;
}

// ─── Choice options (mirror backend TextChoices) ─────────────────────────────

const BUILDING_STATUSES = [
  ["active", "Active"],
  ["under_maintenance", "Under Maintenance"],
  ["closed", "Closed"],
  ["demolished", "Demolished"],
] as const;

const ROOM_TYPES = [
  ["classroom", "Classroom"],
  ["lab", "Laboratory"],
  ["library", "Library"],
  ["office", "Office"],
  ["gym", "Gymnasium"],
  ["auditorium", "Auditorium"],
] as const;

const ROOM_STATUSES = [
  ["available", "Available"],
  ["occupied", "Occupied"],
  ["under_maintenance", "Under Maintenance"],
  ["reserved", "Reserved"],
  ["unavailable", "Unavailable"],
] as const;

const WORK_ORDER_PRIORITIES = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["urgent", "Urgent"],
  ["emergency", "Emergency"],
] as const;

const WORK_ORDER_STATUSES = [
  ["open", "Open"],
  ["in_progress", "In Progress"],
  ["on_hold", "On Hold"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as const;

const WORK_ORDER_CATEGORIES = [
  ["plumbing", "Plumbing"],
  ["electrical", "Electrical"],
  ["hvac", "HVAC / Climate"],
  ["carpentry", "Carpentry"],
  ["painting", "Painting"],
  ["roofing", "Roofing"],
  ["general", "General"],
] as const;

const ASSET_TYPES = [
  ["furniture", "Furniture"],
  ["electronics", "Electronics"],
  ["it_device", "IT Device"],
  ["projector", "Projector / Display"],
  ["network", "Network Equipment"],
  ["safety", "Safety Equipment"],
  ["other", "Other"],
] as const;

const ASSET_CONDITIONS = [
  ["new", "New"],
  ["good", "Good"],
  ["fair", "Fair"],
  ["poor", "Poor"],
  ["damaged", "Damaged"],
  ["written_off", "Written Off"],
] as const;

const ASSET_STATUSES = [
  ["in_stock", "In Stock"],
  ["in_use", "In Use"],
  ["under_repair", "Under Repair"],
  ["retired", "Retired"],
  ["disposed", "Disposed"],
] as const;

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  available: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  in_use: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  in_stock: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  occupied: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  reserved: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  in_progress: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  open: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  under_maintenance: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  under_repair: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  on_hold: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  closed: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  cancelled: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  retired: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  disposed: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  demolished: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  unavailable: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  poor: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  damaged: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  written_off: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const PRIORITY_COLORS: Record<string, string> = {
  low: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  medium: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  high: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  urgent: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  emergency: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const CONDITION_COLORS: Record<string, string> = {
  new: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  good: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  fair: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  poor: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  damaged: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  written_off: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

// ─── Tabs ────────────────────────────────────────────────────────────────────

type TabType = "buildings" | "rooms" | "workorders" | "assets";

const TABS: { key: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "buildings", label: "Buildings", icon: BuildingOffice2Icon },
  { key: "rooms", label: "Rooms", icon: Square2StackIcon },
  { key: "workorders", label: "Work Orders", icon: WrenchScrewdriverIcon },
  { key: "assets", label: "Assets", icon: ArchiveBoxIcon },
];

// ─── Skeleton ────────────────────────────────────────────────────────────────

function CardSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          className="h-32 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
        >
          <div
            className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-slate-200/50 to-transparent dark:via-slate-600/30"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function InfrastructurePage() {
  useTitle("Infrastructure");
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>("buildings");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const searchRef = useRef<HTMLInputElement>(null);

  // Modals
  const [showBuildingForm, setShowBuildingForm] = useState(false);
  const [editingBuilding, setEditingBuilding] = useState<Building | null>(null);
  const [showRoomForm, setShowRoomForm] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [showWorkOrderForm, setShowWorkOrderForm] = useState(false);
  const [editingWorkOrder, setEditingWorkOrder] = useState<WorkOrder | null>(null);
  const [showAssetForm, setShowAssetForm] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);

  // ── Data fetching ───────────────────────────────────────────────────────

  const { data: buildings = [], isLoading: buildingsLoading } = useQuery({
    queryKey: ["infra-buildings"],
    queryFn: async () => {
      const res = await api.get<{ results: Building[] }>("/infrastructure/buildings/");
      return res.results ?? [];
    },
  });

  const { data: rooms = [], isLoading: roomsLoading } = useQuery({
    queryKey: ["infra-rooms"],
    queryFn: async () => {
      const res = await api.get<{ results: Room[] }>("/infrastructure/rooms/");
      return res.results ?? [];
    },
  });

  const { data: workOrders = [], isLoading: workOrdersLoading } = useQuery({
    queryKey: ["infra-workorders"],
    queryFn: async () => {
      const res = await api.get<{ results: WorkOrder[] }>("/infrastructure/work-orders/");
      return res.results ?? [];
    },
  });

  const { data: assets = [], isLoading: assetsLoading } = useQuery({
    queryKey: ["infra-assets"],
    queryFn: async () => {
      const res = await api.get<{ results: Asset[] }>("/infrastructure/assets/");
      return res.results ?? [];
    },
  });

  // ── Mutations ───────────────────────────────────────────────────────────

  const deleteBuilding = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/buildings/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-buildings"] });
      toast.success("Building deleted");
    },
  });
  const deleteRoom = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/rooms/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-rooms"] });
      toast.success("Room deleted");
    },
  });
  const deleteWorkOrder = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/work-orders/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-workorders"] });
      toast.success("Work order deleted");
    },
  });
  const deleteAsset = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/assets/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-assets"] });
      toast.success("Asset deleted");
    },
  });

  // ── Filtering ───────────────────────────────────────────────────────────

  const filteredBuildings = useMemo(() => {
    if (!search.trim()) return buildings;
    const q = search.toLowerCase();
    return buildings.filter(
      (b) =>
        b.name.toLowerCase().includes(q) ||
        b.code.toLowerCase().includes(q) ||
        b.address?.toLowerCase().includes(q),
    );
  }, [buildings, search]);

  const filteredRooms = useMemo(() => {
    if (!search.trim()) return rooms;
    const q = search.toLowerCase();
    return rooms.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.room_number.toLowerCase().includes(q) ||
        (r.building_name || "").toLowerCase().includes(q),
    );
  }, [rooms, search]);

  const filteredWorkOrders = useMemo(() => {
    if (!search.trim()) return workOrders;
    const q = search.toLowerCase();
    return workOrders.filter(
      (w) =>
        w.title.toLowerCase().includes(q) ||
        w.category.toLowerCase().includes(q) ||
        (w.building_name || "").toLowerCase().includes(q),
    );
  }, [workOrders, search]);

  const filteredAssets = useMemo(() => {
    if (!search.trim()) return assets;
    const q = search.toLowerCase();
    return assets.filter(
      (a) =>
        a.name.toLowerCase().includes(q) ||
        a.asset_tag.toLowerCase().includes(q) ||
        (a.building_name || "").toLowerCase().includes(q),
    );
  }, [assets, search]);

  const allFiltered =
    activeTab === "buildings"
      ? filteredBuildings
      : activeTab === "rooms"
        ? filteredRooms
        : activeTab === "workorders"
          ? filteredWorkOrders
          : filteredAssets;

  const PAGE_SIZE = 12;
  const totalPages = Math.max(1, Math.ceil(allFiltered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginated = allFiltered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  const [infinitePage, setInfinitePage] = useState(1);
  const infiniteItems: { id: string }[] = allFiltered.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < allFiltered.length;

  const visibleItems = viewMode === "pagination" ? paginated : infiniteItems;

  // ── Bulk selection ──────────────────────────────────────────────────────

  const bulk = useBulkSelect<{ id: string }>(allFiltered);
  const activeDelete =
    deleteBuilding.isPending ||
    deleteRoom.isPending ||
    deleteWorkOrder.isPending ||
    deleteAsset.isPending;

  const handleBulkDelete = async () => {
    if (bulk.selectedCount === 0) return;
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => {
          const base =
            activeTab === "buildings"
              ? "/infrastructure/buildings/"
              : activeTab === "rooms"
                ? "/infrastructure/rooms/"
                : activeTab === "workorders"
                  ? "/infrastructure/work-orders/"
                  : "/infrastructure/assets/";
          return api.delete(`${base}${id}/`);
        }),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries();
    } catch {
      toast.error("Failed to delete items");
    }
  };

  // ── CSV export ──────────────────────────────────────────────────────────

  const handleExport = () => {
    const rows =
      activeTab === "buildings"
        ? filteredBuildings.map((b) => ({
            name: b.name,
            code: b.code,
            floors: b.floors,
            address: b.address,
            status: b.status,
          }))
        : activeTab === "rooms"
          ? filteredRooms.map((r) => ({
              name: r.name,
              room_number: r.room_number,
              building: r.building_name ?? "",
              room_type: r.room_type,
              capacity: r.capacity,
              status: r.status,
            }))
          : activeTab === "workorders"
            ? filteredWorkOrders.map((w) => ({
                title: w.title,
                category: w.category,
                priority: w.priority,
                status: w.status,
                building: w.building_name ?? "",
              }))
            : filteredAssets.map((a) => ({
                name: a.name,
                asset_tag: a.asset_tag,
                asset_type: a.asset_type,
                condition: a.condition,
                status: a.status,
                building: a.building_name ?? "",
              }));
    const cols = Object.keys(rows[0] ?? {}).map((k) => ({ key: k, label: k }));
    downloadCsv(
      toCsv(rows, cols),
      `infrastructure-${activeTab}-${dayjs().format("YYYY-MM-DD")}.csv`,
    );
  };

  const handleBulkExport = () => {
    const cols = [{ key: "id", label: "ID" }];
    downloadCsv(
      toCsv(
        bulk.selectedItems.map((i) => ({ id: i.id })),
        cols,
      ),
      `infrastructure-bulk-${dayjs().format("YYYY-MM-DD")}.csv`,
    );
  };

  // ── Keyboard shortcuts ──────────────────────────────────────────────────

  const { open: helpOpen, setOpen: setHelpOpen } = useShortcutHelp();
  useKeyboardShortcuts({
    onCreate: () => {
      if (activeTab === "buildings") setShowBuildingForm(true);
      else if (activeTab === "rooms") setShowRoomForm(true);
      else if (activeTab === "workorders") setShowWorkOrderForm(true);
      else setShowAssetForm(true);
    },
    onSearch: () => searchRef.current?.focus(),
    onExport: handleExport,
    onEscape: () => bulk.clear(),
    onDelete: () => {
      if (bulk.selectedCount > 0) handleBulkDelete();
    },
    onSelectAll: () => bulk.toggleAll(),
  });

  const isLoading =
    activeTab === "buildings"
      ? buildingsLoading
      : activeTab === "rooms"
        ? roomsLoading
        : activeTab === "workorders"
          ? workOrdersLoading
          : assetsLoading;

  const createButton =
    activeTab === "buildings"
      ? {
          label: "Add Building",
          action: () => {
            setEditingBuilding(null);
            setShowBuildingForm(true);
          },
        }
      : activeTab === "rooms"
        ? {
            label: "Add Room",
            action: () => {
              setEditingRoom(null);
              setShowRoomForm(true);
            },
          }
        : activeTab === "workorders"
          ? {
              label: "New Work Order",
              action: () => {
                setEditingWorkOrder(null);
                setShowWorkOrderForm(true);
              },
            }
          : {
              label: "Add Asset",
              action: () => {
                setEditingAsset(null);
                setShowAssetForm(true);
              },
            };

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Infrastructure</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Buildings, rooms, work orders and assets
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={bulk.allSelected}
              ref={(el) => {
                if (el) el.indeterminate = bulk.someSelected;
              }}
              onChange={bulk.toggleAll}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
            />
            <span className="text-sm text-slate-500 dark:text-slate-400">Select all</span>
          </label>
          <div className="flex items-center gap-1 rounded-lg border border-slate-200 p-0.5 dark:border-slate-700">
            <button
              onClick={() => setViewMode("pagination")}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "pagination"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              }`}
            >
              Pages
            </button>
            <button
              onClick={() => setViewMode("infinite")}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "infinite"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              }`}
            >
              Scroll
            </button>
          </div>
          <Button
            variant="secondary"
            leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            onClick={handleExport}
          >
            Export CSV
          </Button>
          <Button onClick={createButton.action}>
            <PlusIcon className="mr-1.5 h-4 w-4" />
            {createButton.label}
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto rounded-lg bg-slate-100 p-1 w-fit dark:bg-slate-800">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key);
                setPage(1);
                setInfinitePage(1);
              }}
              className={`inline-flex items-center gap-2 whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white"
                  : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
              <span className="rounded-full bg-slate-200 px-1.5 py-0.5 text-xs dark:bg-slate-600">
                {activeTab === tab.key ? allFiltered.length : ""}
              </span>
            </button>
          );
        })}
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          ref={searchRef}
          type="search"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder={`Search ${activeTab === "workorders" ? "work orders" : activeTab}...`}
          className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:placeholder-slate-400"
        />
      </div>

      {/* Content */}
      {isLoading ? (
        <CardSkeleton />
      ) : allFiltered.length === 0 ? (
        <EmptyState
          icon={
            activeTab === "buildings"
              ? BuildingOffice2Icon
              : activeTab === "rooms"
                ? Square2StackIcon
                : activeTab === "workorders"
                  ? WrenchScrewdriverIcon
                  : ArchiveBoxIcon
          }
          title={`No ${activeTab === "workorders" ? "work orders" : activeTab}`}
          description={`Add your first ${
            activeTab === "workorders" ? "work order" : activeTab.slice(0, -1)
          } to get started`}
        />
      ) : (
        <>
          {viewMode === "pagination" ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {visibleItems.map((item) => (
                <Card
                  key={item.id}
                  tab={activeTab}
                  item={item}
                  selected={bulk.isSelected(item.id)}
                  onToggle={() => bulk.toggle(item.id)}
                  onEdit={() => {
                    if (activeTab === "buildings") {
                      setEditingBuilding(item as Building);
                      setShowBuildingForm(true);
                    } else if (activeTab === "rooms") {
                      setEditingRoom(item as Room);
                      setShowRoomForm(true);
                    } else if (activeTab === "workorders") {
                      setEditingWorkOrder(item as WorkOrder);
                      setShowWorkOrderForm(true);
                    } else {
                      setEditingAsset(item as Asset);
                      setShowAssetForm(true);
                    }
                  }}
                  onDelete={() => {
                    if (!confirm("Delete this item?")) return;
                    if (activeTab === "buildings") deleteBuilding.mutate(item.id);
                    else if (activeTab === "rooms") deleteRoom.mutate(item.id);
                    else if (activeTab === "workorders") deleteWorkOrder.mutate(item.id);
                    else deleteAsset.mutate(item.id);
                  }}
                />
              ))}
            </div>
          ) : (
            <InfiniteScroll
              items={infiniteItems}
              hasMore={infiniteHasMore}
              isLoading={false}
              isFetchingNext={false}
              onLoadMore={() => setInfinitePage((p) => p + 1)}
              renderItem={(item) => (
                <Card
                  key={item.id}
                  tab={activeTab}
                  item={item}
                  selected={bulk.isSelected(item.id)}
                  onToggle={() => bulk.toggle(item.id)}
                  onEdit={() => {
                    if (activeTab === "buildings") {
                      setEditingBuilding(item as Building);
                      setShowBuildingForm(true);
                    } else if (activeTab === "rooms") {
                      setEditingRoom(item as Room);
                      setShowRoomForm(true);
                    } else if (activeTab === "workorders") {
                      setEditingWorkOrder(item as WorkOrder);
                      setShowWorkOrderForm(true);
                    } else {
                      setEditingAsset(item as Asset);
                      setShowAssetForm(true);
                    }
                  }}
                  onDelete={() => {
                    if (!confirm("Delete this item?")) return;
                    if (activeTab === "buildings") deleteBuilding.mutate(item.id);
                    else if (activeTab === "rooms") deleteRoom.mutate(item.id);
                    else if (activeTab === "workorders") deleteWorkOrder.mutate(item.id);
                    else deleteAsset.mutate(item.id);
                  }}
                />
              )}
            />
          )}

          {viewMode === "pagination" && totalPages > 1 && (
            <Pagination
              page={safePage}
              total={allFiltered.length}
              pageSize={PAGE_SIZE}
              onChange={setPage}
            />
          )}
        </>
      )}

      {/* Bulk action bar */}
      <BulkActionBar
        selectedCount={bulk.selectedCount}
        onClear={bulk.clear}
        onDelete={handleBulkDelete}
        onExport={handleBulkExport}
        deleteLabel={`Delete ${bulk.selectedCount} selected`}
      />

      {/* Modals */}
      {activeTab === "buildings" && (
        <BuildingFormModal
          open={showBuildingForm}
          onClose={() => {
            setShowBuildingForm(false);
            setEditingBuilding(null);
          }}
          building={editingBuilding}
          onSaved={() => {
            setShowBuildingForm(false);
            setEditingBuilding(null);
            qc.invalidateQueries({ queryKey: ["infra-buildings"] });
          }}
        />
      )}
      {activeTab === "rooms" && (
        <RoomFormModal
          open={showRoomForm}
          onClose={() => {
            setShowRoomForm(false);
            setEditingRoom(null);
          }}
          room={editingRoom}
          buildings={buildings}
          onSaved={() => {
            setShowRoomForm(false);
            setEditingRoom(null);
            qc.invalidateQueries({ queryKey: ["infra-rooms"] });
          }}
        />
      )}
      {activeTab === "workorders" && (
        <WorkOrderFormModal
          open={showWorkOrderForm}
          onClose={() => {
            setShowWorkOrderForm(false);
            setEditingWorkOrder(null);
          }}
          workOrder={editingWorkOrder}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowWorkOrderForm(false);
            setEditingWorkOrder(null);
            qc.invalidateQueries({ queryKey: ["infra-workorders"] });
          }}
        />
      )}
      {activeTab === "assets" && (
        <AssetFormModal
          open={showAssetForm}
          onClose={() => {
            setShowAssetForm(false);
            setEditingAsset(null);
          }}
          asset={editingAsset}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowAssetForm(false);
            setEditingAsset(null);
            qc.invalidateQueries({ queryKey: ["infra-assets"] });
          }}
        />
      )}

      {/* Shortcut help */}
      <KeyboardShortcutHelp open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  );
}

// ─── Card ────────────────────────────────────────────────────────────────────

function Card({
  tab,
  item,
  selected,
  onToggle,
  onEdit,
  onDelete,
}: {
  tab: TabType;
  item: { id: string };
  selected: boolean;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const inputCls =
    "h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600";
  return (
    <div
      className={`group rounded-xl border bg-white p-4 transition-all hover:shadow-md dark:bg-slate-800 ${
        selected
          ? "border-indigo-400 ring-1 ring-indigo-400 dark:border-indigo-500"
          : "border-slate-200 dark:border-slate-700"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className={inputCls}
          aria-label="Select item"
        />
        <div className="flex-1 min-w-0">
          {tab === "buildings" && <BuildingCard item={item as Building} />}
          {tab === "rooms" && <RoomCard item={item as Room} />}
          {tab === "workorders" && <WorkOrderCard item={item as WorkOrder} />}
          {tab === "assets" && <AssetCard item={item as Asset} />}
        </div>
        <div className="flex gap-1">
          <button
            onClick={onEdit}
            className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
            aria-label="Edit"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={onDelete}
            className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
            aria-label="Delete"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function Badge({ value, colors }: { value: string; colors: Record<string, string> }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
        colors[value] ?? "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
      }`}
    >
      {value.replace(/_/g, " ")}
    </span>
  );
}

function BuildingCard({ item }: { item: Building }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="font-mono text-xs text-slate-400">{item.code}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.floors > 0 && <span>🏢 {item.floors} floors</span>}
        {item.total_area_sqft && (
          <span>📐 {Number(item.total_area_sqft).toLocaleString()} sqft</span>
        )}
      </div>
      {item.address && <p className="mt-1 truncate text-xs text-slate-400">📍 {item.address}</p>}
    </>
  );
}

function RoomCard({ item }: { item: Room }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="text-xs text-slate-400">
        {item.room_number}
        {item.building_name && ` · ${item.building_name}`}
        {item.floor != null && ` · Floor ${item.floor}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Badge value={item.room_type} colors={{}} />
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.capacity > 0 && <span>👥 {item.capacity}</span>}
      </div>
      <div className="mt-1 flex flex-wrap gap-1.5 text-xs text-slate-400">
        {item.has_projector && <span>🖥</span>}
        {item.has_smartboard && <span>🪄</span>}
        {item.has_ac && <span>❄️</span>}
        {item.has_wifi && <span>📶</span>}
        {item.has_computers && <span>💻 {item.computer_count}</span>}
      </div>
    </>
  );
}

function WorkOrderCard({ item }: { item: WorkOrder }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name || "—"}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.priority} colors={PRIORITY_COLORS} />
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.category && <span className="text-slate-400">{item.category}</span>}
      </div>
      {item.assigned_to_name && (
        <p className="mt-1 truncate text-xs text-slate-400">👷 {item.assigned_to_name}</p>
      )}
    </>
  );
}

function AssetCard({ item }: { item: Asset }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="font-mono text-xs text-slate-400">{item.asset_tag}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.asset_type} colors={{}} />
        <Badge value={item.condition} colors={CONDITION_COLORS} />
        <Badge value={item.status} colors={STATUS_COLORS} />
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.building_name && <span>📍 {item.building_name}</span>}
        {item.purchase_cost != null && <span>💲{Number(item.purchase_cost).toLocaleString()}</span>}
      </div>
    </>
  );
}

// ─── Form helpers ────────────────────────────────────────────────────────────

const inputCls =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200";
const labelCls = "mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300";

function SelectField({
  label,
  value,
  options,
  onChange,
  required,
}: {
  label: string;
  value: string;
  options: readonly (readonly [string, string])[];
  onChange: (v: string) => void;
  required?: boolean;
}) {
  return (
    <div>
      <label className={labelCls}>
        {label}
        {required && " *"}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={inputCls}
        required={required}
      >
        {options.map(([v, l]) => (
          <option key={v} value={v}>
            {l}
          </option>
        ))}
      </select>
    </div>
  );
}

// ─── Building Form Modal ─────────────────────────────────────────────────────

function BuildingFormModal({
  open,
  onClose,
  building,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  building?: Building | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: building?.name ?? "",
    code: building?.code ?? "",
    description: building?.description ?? "",
    floors: building?.floors ?? 1,
    year_built: building?.year_built ?? "",
    total_area_sqft: building?.total_area_sqft ?? "",
    address: building?.address ?? "",
    status: building?.status ?? "active",
  });
  const isEdit = !!building;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/buildings/", data),
    onSuccess: () => {
      toast.success("Building created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/buildings/${building!.id}/`, data),
    onSuccess: () => {
      toast.success("Building updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Building name is required");
    const data = {
      ...f,
      year_built: f.year_built ? Number(f.year_built) : null,
      total_area_sqft: f.total_area_sqft ? Number(f.total_area_sqft) : null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Building" : "Add Building"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Code</label>
            <input
              value={f.code}
              onChange={(e) => setF((p) => ({ ...p, code: e.target.value }))}
              className={inputCls}
              placeholder="e.g. BLDG-A"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Floors</label>
            <input
              type="number"
              min={1}
              value={f.floors}
              onChange={(e) => setF((p) => ({ ...p, floors: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Year Built</label>
            <input
              type="number"
              min={1800}
              max={2100}
              value={f.year_built}
              onChange={(e) => setF((p) => ({ ...p, year_built: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Area (sqft)</label>
            <input
              type="number"
              min={0}
              value={f.total_area_sqft}
              onChange={(e) => setF((p) => ({ ...p, total_area_sqft: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <SelectField
          label="Status"
          value={f.status}
          options={BUILDING_STATUSES}
          onChange={(v) => setF((p) => ({ ...p, status: v }))}
        />
        <div>
          <label className={labelCls}>Address</label>
          <input
            value={f.address}
            onChange={(e) => setF((p) => ({ ...p, address: e.target.value }))}
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Room Form Modal ─────────────────────────────────────────────────────────

function RoomFormModal({
  open,
  onClose,
  room,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  room?: Room | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: room?.building ?? "",
    name: room?.name ?? "",
    room_number: room?.room_number ?? "",
    floor: room?.floor ?? 1,
    room_type: room?.room_type ?? "classroom",
    status: room?.status ?? "available",
    capacity: room?.capacity ?? 30,
    area_sqft: room?.area_sqft ?? "",
    has_projector: room?.has_projector ?? false,
    has_smartboard: room?.has_smartboard ?? false,
    has_ac: room?.has_ac ?? false,
    has_wifi: room?.has_wifi ?? false,
    has_computers: room?.has_computers ?? false,
    computer_count: room?.computer_count ?? 0,
  });
  const isEdit = !!room;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/rooms/", data),
    onSuccess: () => {
      toast.success("Room created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/rooms/${room!.id}/`, data),
    onSuccess: () => {
      toast.success("Room updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Room name is required");
    if (!f.building) return toast.error("Select a building");
    const data = { ...f, area_sqft: f.area_sqft ? Number(f.area_sqft) : null } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Room" : "Add Room"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building *</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select building...</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room Number</label>
            <input
              value={f.room_number}
              onChange={(e) => setF((p) => ({ ...p, room_number: e.target.value }))}
              className={inputCls}
              placeholder="e.g. A-101"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Floor</label>
            <input
              type="number"
              min={0}
              value={f.floor}
              onChange={(e) => setF((p) => ({ ...p, floor: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Capacity</label>
            <input
              type="number"
              min={0}
              value={f.capacity}
              onChange={(e) => setF((p) => ({ ...p, capacity: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Room Type"
            value={f.room_type}
            options={ROOM_TYPES}
            onChange={(v) => setF((p) => ({ ...p, room_type: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={ROOM_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div>
          <label className={labelCls}>Area (sqft)</label>
          <input
            type="number"
            min={0}
            value={f.area_sqft}
            onChange={(e) => setF((p) => ({ ...p, area_sqft: e.target.value }))}
            className={inputCls}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          {(
            [
              ["has_projector", "Projector"],
              ["has_smartboard", "Smartboard"],
              ["has_ac", "Air Conditioning"],
              ["has_wifi", "Wi-Fi"],
              ["has_computers", "Computers"],
            ] as const
          ).map(([key, label]) => (
            <label
              key={key}
              className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300"
            >
              <input
                type="checkbox"
                checked={f[key]}
                onChange={(e) => setF((p) => ({ ...p, [key]: e.target.checked }))}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
              />
              {label}
            </label>
          ))}
        </div>
        {f.has_computers && (
          <div>
            <label className={labelCls}>Computer Count</label>
            <input
              type="number"
              min={0}
              value={f.computer_count}
              onChange={(e) => setF((p) => ({ ...p, computer_count: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Work Order Form Modal ───────────────────────────────────────────────────

function WorkOrderFormModal({
  open,
  onClose,
  workOrder,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  workOrder?: WorkOrder | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    title: workOrder?.title ?? "",
    description: workOrder?.description ?? "",
    category: workOrder?.category ?? "general",
    priority: workOrder?.priority ?? "medium",
    status: workOrder?.status ?? "open",
    building: workOrder?.building ?? "",
    room: workOrder?.room ?? "",
  });
  const isEdit = !!workOrder;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/work-orders/", data),
    onSuccess: () => {
      toast.success("Work order created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/work-orders/${workOrder!.id}/`, data),
    onSuccess: () => {
      toast.success("Work order updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    const data = { ...f, building: f.building || null, room: f.room || null } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Work Order" : "New Work Order"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Title *</label>
          <input
            value={f.title}
            onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
            className={inputCls}
            required
          />
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={3}
            className={inputCls}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Category"
            value={f.category}
            options={WORK_ORDER_CATEGORIES}
            onChange={(v) => setF((p) => ({ ...p, category: v }))}
          />
          <SelectField
            label="Priority"
            value={f.priority}
            options={WORK_ORDER_PRIORITIES}
            onChange={(v) => setF((p) => ({ ...p, priority: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={WORK_ORDER_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
            >
              <option value="">None</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Asset Form Modal ────────────────────────────────────────────────────────

function AssetFormModal({
  open,
  onClose,
  asset,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  asset?: Asset | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: asset?.name ?? "",
    asset_tag: asset?.asset_tag ?? "",
    description: asset?.description ?? "",
    asset_type: asset?.asset_type ?? "furniture",
    condition: asset?.condition ?? "good",
    status: asset?.status ?? "in_stock",
    building: asset?.building ?? "",
    room: asset?.room ?? "",
    purchase_date: asset?.purchase_date ?? "",
    purchase_cost: asset?.purchase_cost ?? "",
  });
  const isEdit = !!asset;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/assets/", data),
    onSuccess: () => {
      toast.success("Asset created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/assets/${asset!.id}/`, data),
    onSuccess: () => {
      toast.success("Asset updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Asset name is required");
    const data = {
      ...f,
      building: f.building || null,
      room: f.room || null,
      purchase_date: f.purchase_date || null,
      purchase_cost: f.purchase_cost ? Number(f.purchase_cost) : null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Asset" : "Add Asset"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Asset Tag</label>
            <input
              value={f.asset_tag}
              onChange={(e) => setF((p) => ({ ...p, asset_tag: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. AST-0001"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Type"
            value={f.asset_type}
            options={ASSET_TYPES}
            onChange={(v) => setF((p) => ({ ...p, asset_type: v }))}
          />
          <SelectField
            label="Condition"
            value={f.condition}
            options={ASSET_CONDITIONS}
            onChange={(v) => setF((p) => ({ ...p, condition: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={ASSET_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
            >
              <option value="">None</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Purchase Date</label>
            <input
              type="date"
              value={f.purchase_date}
              onChange={(e) => setF((p) => ({ ...p, purchase_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Purchase Cost</label>
            <input
              type="number"
              min={0}
              step={0.01}
              value={f.purchase_cost}
              onChange={(e) => setF((p) => ({ ...p, purchase_cost: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
