/**
 * Inventory / Store Management — Admin page for items, categories, suppliers,
 * stock movements, and purchase orders.
 */
import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon, MagnifyingGlassIcon,
  CubeIcon, TagIcon, TruckIcon,
  ArrowPathIcon, ClipboardDocumentListIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Category {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  item_count: number;
}

interface Supplier {
  id: string;
  name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  status: string;
  status_display: string;
  payment_terms: string;
  notes: string;
}

interface InventoryItem {
  id: string;
  category: number | null;
  category_name: string | null;
  supplier: string | null;
  supplier_name: string | null;
  name: string;
  sku: string;
  description: string;
  unit: string;
  unit_display: string;
  unit_price: number;
  current_stock: number;
  minimum_stock: number;
  maximum_stock: number;
  location: string;
  barcode: string;
  is_active: boolean;
  is_low_stock: boolean;
  stock_value: number;
}

interface StockMovement {
  id: string;
  item: string;
  item_name: string;
  item_sku: string;
  movement_type: string;
  movement_type_display: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
  reference_number: string;
  notes: string;
  performed_by_name: string | null;
  created_at: string;
}

interface PurchaseOrder {
  id: string;
  order_number: string;
  supplier: string | null;
  supplier_name: string | null;
  order_date: string;
  expected_date: string | null;
  status: string;
  status_display: string;
  subtotal: number;
  tax_amount: number;
  shipping_cost: number;
  total_amount: number;
  notes: string;
  ordered_by_name: string | null;
  items: PurchaseOrderItem[];
}

interface PurchaseOrderItem {
  id: number;
  item: string;
  item_name: string;
  quantity_ordered: number;
  quantity_received: number;
  unit_price: number;
  total_price: number;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  inactive: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  discontinued: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  draft: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  submitted: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  confirmed: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300",
  partially_received: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  received: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  cancelled: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const MOVEMENT_TYPE_LABELS: Record<string, string> = {
  purchase: "Purchase (Inbound)",
  issue: "Issue (Outbound)",
  adjustment: "Adjustment",
  return: "Return (Inbound)",
  transfer: "Transfer",
  damage: "Damage / Write-off",
};

// ─── Tabs ────────────────────────────────────────────────────────────────────

type TabType = "items" | "categories" | "suppliers" | "movements" | "orders";
const TABS: { key: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "items", label: "Items", icon: CubeIcon },
  { key: "categories", label: "Categories", icon: TagIcon },
  { key: "suppliers", label: "Suppliers", icon: TruckIcon },
  { key: "movements", label: "Stock Movements", icon: ArrowPathIcon },
  { key: "orders", label: "Purchase Orders", icon: ClipboardDocumentListIcon },
];

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function InventoryPage() {
  useTitle("Inventory / Store");
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>("items");
  const [search, setSearch] = useState("");

  // Modals
  const [showItemForm, setShowItemForm] = useState(false);
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [showSupplierForm, setShowSupplierForm] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [showStockModal, setShowStockModal] = useState(false);
  const [stockItem, setStockItem] = useState<InventoryItem | null>(null);
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [editingOrder, setEditingOrder] = useState<PurchaseOrder | null>(null);
  const [showReceiveModal, setShowReceiveModal] = useState(false);
  const [receiveOrder, setReceiveOrder] = useState<PurchaseOrder | null>(null);

  // ── Data fetching ───────────────────────────────────────────────────────

  const { data: items = [], isLoading: iLoading } = useQuery({
    queryKey: ["inv-items"],
    queryFn: async () => {
      const res = await api.get<{ results: InventoryItem[] }>("/inventory/items/");
      return res.results ?? [];
    },
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["inv-categories"],
    queryFn: async () => {
      const res = await api.get<{ results: Category[] }>("/inventory/categories/");
      return res.results ?? [];
    },
  });

  const { data: suppliers = [] } = useQuery({
    queryKey: ["inv-suppliers"],
    queryFn: async () => {
      const res = await api.get<{ results: Supplier[] }>("/inventory/suppliers/");
      return res.results ?? [];
    },
  });

  const { data: movements = [], isLoading: mLoading } = useQuery({
    queryKey: ["inv-movements"],
    queryFn: async () => {
      const res = await api.get<{ results: StockMovement[] }>("/inventory/stock-movements/");
      return res.results ?? [];
    },
  });

  const { data: orders = [], isLoading: oLoading } = useQuery({
    queryKey: ["inv-orders"],
    queryFn: async () => {
      const res = await api.get<{ results: PurchaseOrder[] }>("/inventory/purchase-orders/");
      return res.results ?? [];
    },
  });

  // ── Mutations ───────────────────────────────────────────────────────────

  const deleteItem = useMutation({
    mutationFn: (id: string) => api.delete(`/inventory/items/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["inv-items"] }); toast.success("Item deleted"); },
  });

  const deleteCategory = useMutation({
    mutationFn: (id: number) => api.delete(`/inventory/categories/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["inv-categories"] }); toast.success("Category deleted"); },
  });

  const deleteSupplier = useMutation({
    mutationFn: (id: string) => api.delete(`/inventory/suppliers/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["inv-suppliers"] }); toast.success("Supplier deleted"); },
  });

  const adjustStock = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => api.post(`/inventory/items/${id}/adjust-stock/`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["inv-items"] });
      qc.invalidateQueries({ queryKey: ["inv-movements"] });
      toast.success("Stock adjusted");
      setShowStockModal(false);
    },
  });

  // ── Filtering ───────────────────────────────────────────────────────────

  const filteredItems = useMemo(() => {
    if (!search.trim()) return items;
    const q = search.toLowerCase();
    return items.filter((i) =>
      i.name.toLowerCase().includes(q) ||
      i.sku.toLowerCase().includes(q) ||
      (i.category_name || "").toLowerCase().includes(q)
    );
  }, [items, search]);

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Inventory & Store</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage school store items, suppliers, and stock</p>
        </div>
        <div className="flex gap-2">
          {activeTab === "items" && (
            <Button onClick={() => { setEditingItem(null); setShowItemForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Item
            </Button>
          )}
          {activeTab === "categories" && (
            <Button onClick={() => { setEditingCategory(null); setShowCategoryForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Category
            </Button>
          )}
          {activeTab === "suppliers" && (
            <Button onClick={() => { setEditingSupplier(null); setShowSupplierForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Supplier
            </Button>
          )}
          {activeTab === "orders" && (
            <Button onClick={() => { setEditingOrder(null); setShowOrderForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> New Order
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.key
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Search */}
      {activeTab === "items" && (
        <div className="relative max-w-sm">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
            placeholder="Search items..." />
        </div>
      )}

      {/* ── Items Tab ────────────────────────────────────────────────────── */}
      {activeTab === "items" && (
        <>
          {iLoading ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i => <div key={i} className="h-28 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : filteredItems.length === 0 ? (
            <EmptyState icon={CubeIcon} title="No items" description="Add your first inventory item" />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredItems.map((item) => (
                <div key={item.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-slate-900 dark:text-white truncate">{item.name}</p>
                      <p className="text-xs text-slate-400 truncate">{item.sku} {item.unit_display && `· ${item.unit_display}`}</p>
                    </div>
                    {item.is_low_stock && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 whitespace-nowrap ml-2">
                        Low Stock
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-500 dark:text-slate-400 mb-3">
                    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-2 text-center">
                      <p className="text-lg font-bold text-slate-800 dark:text-white">{item.current_stock}</p>
                      <p>In Stock</p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-2 text-center">
                      <p className="text-lg font-bold text-slate-800 dark:text-white">${Number(item.unit_price).toLocaleString()}</p>
                      <p>Unit Price</p>
                    </div>
                  </div>
                  <div className="text-xs text-slate-400 space-y-0.5 mb-2">
                    {item.category_name && <p>📂 {item.category_name}</p>}
                    {item.location && <p>📍 {item.location}</p>}
                    {item.minimum_stock > 0 && <p>⚠️ Min: {item.minimum_stock} / Max: {item.maximum_stock}</p>}
                  </div>
                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                    <button onClick={() => { setEditingItem(item); setShowItemForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                    <button onClick={() => { setStockItem(item); setShowStockModal(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Adjust Stock</button>
                    <button onClick={() => { if (confirm("Delete this item?")) deleteItem.mutate(item.id); }}
                      className="text-xs text-red-500 hover:text-red-600 font-medium ml-auto">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Categories Tab ──────────────────────────────────────────────── */}
      {activeTab === "categories" && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {categories.length === 0 ? (
            <div className="sm:col-span-2 lg:col-span-3">
              <EmptyState icon={TagIcon} title="No categories" description="Create your first category" />
            </div>
          ) : (
            categories.map((c) => (
              <div key={c.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{c.name}</p>
                    {c.description && <p className="text-xs text-slate-400 mt-0.5">{c.description}</p>}
                  </div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded ${c.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>
                    {c.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                <p className="text-xs text-slate-400">{c.item_count} item{c.item_count !== 1 ? "s" : ""}</p>
                <div className="flex gap-2 mt-3 pt-2 border-t border-slate-100 dark:border-slate-700">
                  <button onClick={() => { setEditingCategory(c); setShowCategoryForm(true); }}
                    className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                  <button onClick={() => { if (confirm("Delete category?")) deleteCategory.mutate(c.id); }}
                    className="text-xs text-red-500 hover:text-red-600 font-medium">Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* ── Suppliers Tab ────────────────────────────────────────────────── */}
      {activeTab === "suppliers" && (
        <div className="grid gap-3 sm:grid-cols-2">
          {suppliers.length === 0 ? (
            <div className="sm:col-span-2"><EmptyState icon={TruckIcon} title="No suppliers" description="Add your first supplier" /></div>
          ) : (
            suppliers.map((s) => (
              <div key={s.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{s.name}</p>
                    <p className="text-xs text-slate-400">{s.contact_person && `${s.contact_person} · `}{s.phone}</p>
                  </div>
                  <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[s.status]}`}>{s.status_display}</span>
                </div>
                {s.email && <p className="text-xs text-slate-400">📧 {s.email}</p>}
                {s.payment_terms && <p className="text-xs text-slate-400">💳 {s.payment_terms}</p>}
                {s.address && <p className="text-xs text-slate-400 mt-1">{s.address}</p>}
                <div className="flex gap-2 mt-3 pt-2 border-t border-slate-100 dark:border-slate-700">
                  <button onClick={() => { setEditingSupplier(s); setShowSupplierForm(true); }}
                    className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                  <button onClick={() => { if (confirm("Delete supplier?")) deleteSupplier.mutate(s.id); }}
                    className="text-xs text-red-500 hover:text-red-600 font-medium">Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* ── Stock Movements Tab ──────────────────────────────────────────── */}
      {activeTab === "movements" && (
        <>
          {mLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : movements.length === 0 ? (
            <EmptyState icon={ArrowPathIcon} title="No stock movements" description="Stock adjustments will appear here" />
          ) : (
            <div className="space-y-2">
              {movements.map((m) => (
                <div key={m.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3 flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-slate-800 dark:text-white truncate">{m.item_name}</p>
                      <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                        m.quantity > 0 ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
                          : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300"
                      }`}>
                        {m.quantity > 0 ? "+" : ""}{m.quantity}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">
                      {m.movement_type_display}
                      {m.reference_number && ` · Ref: ${m.reference_number}`}
                      {m.performed_by_name && ` · by ${m.performed_by_name}`}
                      <span className="ml-2">{dayjs(m.created_at).format("MMM D, h:mm A")}</span>
                    </p>
                  </div>
                  <p className="text-sm font-medium text-slate-800 dark:text-white ml-4">${Number(m.total_amount).toLocaleString()}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Purchase Orders Tab ──────────────────────────────────────────── */}
      {activeTab === "orders" && (
        <>
          {oLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : orders.length === 0 ? (
            <EmptyState icon={ClipboardDocumentListIcon} title="No purchase orders" description="Create your first purchase order" />
          ) : (
            <div className="space-y-3">
              {orders.map((o) => (
                <div key={o.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-semibold text-slate-900 dark:text-white">{o.order_number}</p>
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[o.status]}`}>{o.status_display}</span>
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {o.supplier_name && `${o.supplier_name} · `}
                        Ordered: {dayjs(o.order_date).format("MMM D, YYYY")}
                        {o.expected_date && ` · Expected: ${dayjs(o.expected_date).format("MMM D, YYYY")}`}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-slate-800 dark:text-white">${Number(o.total_amount).toLocaleString()}</p>
                      {o.ordered_by_name && <p className="text-xs text-slate-400">{o.ordered_by_name}</p>}
                    </div>
                  </div>

                  {/* Items list */}
                  {o.items && o.items.length > 0 && (
                    <div className="mb-2 space-y-1">
                      {o.items.map((oi) => (
                        <div key={oi.id} className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 pl-2">
                          <span>{oi.item_name} × {oi.quantity_ordered}</span>
                          <span>${Number(oi.total_price).toLocaleString()}{oi.quantity_received > 0 && ` (recvd: ${oi.quantity_received})`}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                    {o.status !== "received" && o.status !== "cancelled" && (
                      <button onClick={() => { setReceiveOrder(o); setShowReceiveModal(true); }}
                        className="text-xs text-green-600 hover:text-green-700 font-medium">Receive Items</button>
                    )}
                    <button onClick={() => { if (confirm("Delete this PO?")) api.delete(`/inventory/purchase-orders/${o.id}/`).then(() => { qc.invalidateQueries({ queryKey: ["inv-orders"] }); toast.success("Order deleted"); }); }}
                      className="text-xs text-red-500 hover:text-red-600 font-medium ml-auto">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Item Form Modal ──────────────────────────────────────────────── */}
      <ItemFormModal
        open={showItemForm}
        onClose={() => { setShowItemForm(false); setEditingItem(null); }}
        item={editingItem}
        categories={categories}
        suppliers={suppliers}
        onSaved={() => { setShowItemForm(false); setEditingItem(null); qc.invalidateQueries({ queryKey: ["inv-items"] }); }}
      />

      {/* ── Category Form Modal ──────────────────────────────────────────── */}
      <CategoryFormModal
        open={showCategoryForm}
        onClose={() => { setShowCategoryForm(false); setEditingCategory(null); }}
        category={editingCategory}
        onSaved={() => { setShowCategoryForm(false); setEditingCategory(null); qc.invalidateQueries({ queryKey: ["inv-categories"] }); }}
      />

      {/* ── Supplier Form Modal ──────────────────────────────────────────── */}
      <SupplierFormModal
        open={showSupplierForm}
        onClose={() => { setShowSupplierForm(false); setEditingSupplier(null); }}
        supplier={editingSupplier}
        onSaved={() => { setShowSupplierForm(false); setEditingSupplier(null); qc.invalidateQueries({ queryKey: ["inv-suppliers"] }); }}
      />

      {/* ── Stock Adjust Modal ───────────────────────────────────────────── */}
      <StockAdjustModal
        open={showStockModal}
        onClose={() => { setShowStockModal(false); setStockItem(null); }}
        item={stockItem}
        onSaved={(id: string, data: any) => adjustStock.mutate({ id, data })}
        loading={adjustStock.isPending}
      />

      {/* ── Purchase Order Form Modal ────────────────────────────────────── */}
      <OrderFormModal
        open={showOrderForm}
        onClose={() => { setShowOrderForm(false); setEditingOrder(null); }}
        order={editingOrder}
        suppliers={suppliers}
        items={items}
        onSaved={() => { setShowOrderForm(false); setEditingOrder(null); qc.invalidateQueries({ queryKey: ["inv-orders"] }); qc.invalidateQueries({ queryKey: ["inv-items"] }); }}
      />

      {/* ── Receive Items Modal ──────────────────────────────────────────── */}
      <ReceiveItemsModal
        open={showReceiveModal}
        onClose={() => { setShowReceiveModal(false); setReceiveOrder(null); }}
        order={receiveOrder}
        onSaved={() => { setShowReceiveModal(false); setReceiveOrder(null); qc.invalidateQueries({ queryKey: ["inv-orders"] }); qc.invalidateQueries({ queryKey: ["inv-items"] }); qc.invalidateQueries({ queryKey: ["inv-movements"] }); }}
      />
    </div>
  );
}

// ─── Item Form Modal ──────────────────────────────────────────────────────

function ItemFormModal({
  open, onClose, item, categories, suppliers, onSaved,
}: {
  open: boolean; onClose: () => void; item?: InventoryItem | null;
  categories: Category[]; suppliers: Supplier[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: item?.name ?? "",
    sku: item?.sku ?? "",
    category: item?.category ?? ("" as number | ""),
    supplier: item?.supplier ?? "",
    unit: item?.unit ?? "piece",
    unit_price: item?.unit_price ?? 0,
    minimum_stock: item?.minimum_stock ?? 5,
    maximum_stock: item?.maximum_stock ?? 50,
    location: item?.location ?? "",
    barcode: item?.barcode ?? "",
    description: item?.description ?? "",
  });

  const isEdit = !!item;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/inventory/items/", data),
    onSuccess: () => { toast.success("Item created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/inventory/items/${item!.id}/`, data),
    onSuccess: () => { toast.success("Item updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Item name is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Item" : "Add Inventory Item"}>
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[60vh] overflow-y-auto">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label>
            <input value={form.name} onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">SKU</label>
            <input value={form.sku} onChange={(e) => setForm(p => ({ ...p, sku: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200 font-mono" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Category</label>
            <select value={form.category} onChange={(e) => setForm(p => ({ ...p, category: e.target.value ? Number(e.target.value) : "" }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">None</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Supplier</label>
            <select value={form.supplier} onChange={(e) => setForm(p => ({ ...p, supplier: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">None</option>
              {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Unit</label>
            <select value={form.unit} onChange={(e) => setForm(p => ({ ...p, unit: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="piece">Piece</option>
              <option value="pack">Pack</option>
              <option value="box">Box</option>
              <option value="set">Set</option>
              <option value="liter">Liter</option>
              <option value="kilogram">Kilogram</option>
              <option value="meter">Meter</option>
              <option value="roll">Roll</option>
              <option value="pair">Pair</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Unit Price</label>
            <input type="number" min={0} step={0.01} value={form.unit_price} onChange={(e) => setForm(p => ({ ...p, unit_price: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Location</label>
            <input value={form.location} onChange={(e) => setForm(p => ({ ...p, location: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Min Stock Level</label>
            <input type="number" min={0} value={form.minimum_stock} onChange={(e) => setForm(p => ({ ...p, minimum_stock: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Max Stock Level</label>
            <input type="number" min={0} value={form.maximum_stock} onChange={(e) => setForm(p => ({ ...p, maximum_stock: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea value={form.description} onChange={(e) => setForm(p => ({ ...p, description: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Item</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Category Form Modal ──────────────────────────────────────────────────

function CategoryFormModal({
  open, onClose, category, onSaved,
}: {
  open: boolean; onClose: () => void; category?: Category | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: category?.name ?? "",
    description: category?.description ?? "",
  });

  const isEdit = !!category;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/inventory/categories/", data),
    onSuccess: () => { toast.success("Category created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/inventory/categories/${category!.id}/`, data),
    onSuccess: () => { toast.success("Category updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Name is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Category" : "Add Category"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label>
          <input value={form.name} onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea value={form.description} onChange={(e) => setForm(p => ({ ...p, description: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Category</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Supplier Form Modal ──────────────────────────────────────────────────

function SupplierFormModal({
  open, onClose, supplier, onSaved,
}: {
  open: boolean; onClose: () => void; supplier?: Supplier | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: supplier?.name ?? "",
    contact_person: supplier?.contact_person ?? "",
    email: supplier?.email ?? "",
    phone: supplier?.phone ?? "",
    address: supplier?.address ?? "",
    payment_terms: supplier?.payment_terms ?? "",
    notes: supplier?.notes ?? "",
  });

  const isEdit = !!supplier;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/inventory/suppliers/", data),
    onSuccess: () => { toast.success("Supplier created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/inventory/suppliers/${supplier!.id}/`, data),
    onSuccess: () => { toast.success("Supplier updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Supplier name is required");
    if (!form.phone.trim()) return toast.error("Phone is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Supplier" : "Add Supplier"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label>
            <input value={form.name} onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Contact Person</label>
            <input value={form.contact_person} onChange={(e) => setForm(p => ({ ...p, contact_person: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Email</label>
            <input type="email" value={form.email} onChange={(e) => setForm(p => ({ ...p, email: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Phone *</label>
            <input value={form.phone} onChange={(e) => setForm(p => ({ ...p, phone: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Address</label>
          <textarea value={form.address} onChange={(e) => setForm(p => ({ ...p, address: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Payment Terms</label>
          <input value={form.payment_terms} onChange={(e) => setForm(p => ({ ...p, payment_terms: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
            placeholder="e.g. Net 30" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Supplier</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Stock Adjust Modal ────────────────────────────────────────────────────

function StockAdjustModal({
  open, onClose, item, onSaved, loading,
}: {
  open: boolean; onClose: () => void; item?: InventoryItem | null;
  onSaved: (id: string, data: any) => void; loading: boolean;
}) {
  const [form, setForm] = useState({ movement_type: "adjustment", quantity: 0, notes: "", reference_number: "" });

  React.useEffect(() => {
    if (open) setForm({ movement_type: "adjustment", quantity: 0, notes: "", reference_number: "" });
  }, [open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!item) return;
    if (form.quantity === 0) return toast.error("Quantity must be non-zero");
    onSaved(item.id, form);
  };

  if (!item) return null;

  return (
    <Modal open={open} onClose={onClose} title={`Adjust Stock — ${item.name}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="text-sm text-slate-500 dark:text-slate-400 mb-2">
          Current stock: <strong className="text-slate-800 dark:text-white">{item.current_stock}</strong> {item.unit_display}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Type</label>
            <select value={form.movement_type} onChange={(e) => setForm(p => ({ ...p, movement_type: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="adjustment">Adjustment</option>
              <option value="issue">Issue (Outbound)</option>
              <option value="return">Return (Inbound)</option>
              <option value="damage">Damage / Write-off</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Quantity <span className="text-xs text-slate-400">(+ / -)</span>
            </label>
            <input type="number" value={form.quantity} onChange={(e) => setForm(p => ({ ...p, quantity: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Reference</label>
          <input value={form.reference_number} onChange={(e) => setForm(p => ({ ...p, reference_number: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
            placeholder="Invoice #, PO #, etc." />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Notes</label>
          <textarea value={form.notes} onChange={(e) => setForm(p => ({ ...p, notes: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={loading}>Cancel</Button>
          <Button type="submit" loading={loading}>Adjust Stock</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Purchase Order Form Modal ────────────────────────────────────────────

function OrderFormModal({
  open, onClose, order, suppliers, items, onSaved,
}: {
  open: boolean; onClose: () => void; order?: PurchaseOrder | null;
  suppliers: Supplier[]; items: InventoryItem[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    order_number: order?.order_number ?? `PO-${dayjs().format("YYYYMMDD")}-${Math.floor(Math.random() * 1000).toString().padStart(3, "0")}`,
    supplier: order?.supplier ?? "",
    order_date: order?.order_date ?? dayjs().format("YYYY-MM-DD"),
    expected_date: order?.expected_date ?? "",
    notes: order?.notes ?? "",
  });
  const [lineItems, setLineItems] = useState<{ item: string; quantity_ordered: number; unit_price: number }[]>(
    order?.items?.map((oi) => ({ item: oi.item, quantity_ordered: oi.quantity_ordered, unit_price: oi.unit_price })) ?? []
  );

  const isEdit = !!order;
  const createMut = useMutation({
    mutationFn: (data: { header: typeof form; items: typeof lineItems }) => api.post("/inventory/purchase-orders/", {
      ...data.header,
      items_data: JSON.stringify(data.items),
    }),
    onSuccess: () => { toast.success("Purchase order created"); onSaved(); },
  });
  const isSaving = createMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.order_number.trim()) return toast.error("Order number is required");
    if (lineItems.length === 0) return toast.error("Add at least one item");
    createMut.mutate({ header: form, items: lineItems });
  };

  const addLine = () => {
    setLineItems(prev => [...prev, { item: "", quantity_ordered: 1, unit_price: 0 }]);
  };

  const updateLine = (i: number, field: string, value: any) => {
    setLineItems(prev => prev.map((l, idx) => idx === i ? { ...l, [field]: value } : l));
  };

  const removeLine = (i: number) => {
    setLineItems(prev => prev.filter((_, idx) => idx !== i));
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Purchase Order" : "New Purchase Order"}>
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[60vh] overflow-y-auto">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Order # *</label>
            <input value={form.order_number} onChange={(e) => setForm(p => ({ ...p, order_number: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200 font-mono" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Supplier</label>
            <select value={form.supplier} onChange={(e) => setForm(p => ({ ...p, supplier: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">Select supplier...</option>
              {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Order Date</label>
            <input type="date" value={form.order_date} onChange={(e) => setForm(p => ({ ...p, order_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Expected Date</label>
            <input type="date" value={form.expected_date} onChange={(e) => setForm(p => ({ ...p, expected_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>

        {/* Line Items */}
        <div className="border-t border-slate-100 dark:border-slate-700 pt-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Items</p>
            <Button variant="secondary" size="sm" onClick={addLine} type="button">
              <PlusIcon className="h-3.5 w-3.5 mr-1" /> Add Item
            </Button>
          </div>
          {lineItems.length === 0 && (
            <p className="text-xs text-slate-400 text-center py-4">No items added yet. Click "Add Item" to add line items.</p>
          )}
          <div className="space-y-2">
            {lineItems.map((li, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <select value={li.item} onChange={(e) => updateLine(idx, "item", e.target.value)}
                  className="flex-1 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
                  <option value="">Select item...</option>
                  {items.map((i) => <option key={i.id} value={i.id}>{i.name} (${Number(i.unit_price).toLocaleString()})</option>)}
                </select>
                <input type="number" min={1} value={li.quantity_ordered} onChange={(e) => updateLine(idx, "quantity_ordered", Number(e.target.value))}
                  className="w-20 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
                  placeholder="Qty" />
                <input type="number" min={0} step={0.01} value={li.unit_price} onChange={(e) => updateLine(idx, "unit_price", Number(e.target.value))}
                  className="w-24 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
                  placeholder="Price" />
                <button type="button" onClick={() => removeLine(idx)}
                  className="text-red-400 hover:text-red-600 text-xs">✕</button>
              </div>
            ))}
          </div>
          {lineItems.length > 0 && (
            <p className="text-xs text-slate-400 mt-2">
              Total: <strong>${lineItems.reduce((sum, li) => sum + li.quantity_ordered * li.unit_price, 0).toLocaleString()}</strong>
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Notes</label>
          <textarea value={form.notes} onChange={(e) => setForm(p => ({ ...p, notes: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>Create Order</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Receive Items Modal ──────────────────────────────────────────────────

function ReceiveItemsModal({
  open, onClose, order, onSaved,
}: {
  open: boolean; onClose: () => void; order?: PurchaseOrder | null; onSaved: () => void;
}) {
  const [qtyInputs, setQtyInputs] = useState<Record<string, number>>({});

  const receiveMut = useMutation({
    mutationFn: (data: any) => api.post(`/inventory/purchase-orders/${order!.id}/receive/`, data),
    onSuccess: () => { toast.success("Items received"); onSaved(); },
  });

  React.useEffect(() => {
    if (open && order?.items) {
      const init: Record<string, number> = {};
      order.items.forEach((oi) => {
        init[oi.item] = oi.quantity_ordered - oi.quantity_received;
      });
      setQtyInputs(init);
    }
  }, [open, order]);

  if (!order) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const items = Object.entries(qtyInputs)
      .filter(([_, qty]) => qty > 0)
      .map(([item_id, quantity_received]) => ({ item_id, quantity_received }));
    if (items.length === 0) return toast.error("Enter at least one item quantity");
    receiveMut.mutate({ items });
  };

  return (
    <Modal open={open} onClose={onClose} title={`Receive Items — ${order.order_number}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Enter quantities received for each item. Only items not fully received are shown.
        </p>
        {order.items?.map((oi) => {
          const remaining = oi.quantity_ordered - oi.quantity_received;
          if (remaining <= 0) return null;
          return (
            <div key={oi.id} className="flex items-center justify-between rounded-lg border border-slate-100 dark:border-slate-700 p-3">
              <div>
                <p className="text-sm font-medium text-slate-800 dark:text-white">{oi.item_name}</p>
                <p className="text-xs text-slate-400">
                  Ordered: {oi.quantity_ordered} · Received: {oi.quantity_received} · Remaining: {remaining}
                </p>
              </div>
              <input type="number" min={0} max={remaining} value={qtyInputs[oi.item] || 0}
                onChange={(e) => setQtyInputs(p => ({ ...p, [oi.item]: Number(e.target.value) }))}
                className="w-24 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200 text-center" />
            </div>
          );
        })}
        {(!order.items || order.items.every((oi) => oi.quantity_received >= oi.quantity_ordered)) && (
          <p className="text-sm text-green-600 text-center py-4">All items have been fully received ✓</p>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={receiveMut.isPending}>Cancel</Button>
          <Button type="submit" loading={receiveMut.isPending}>Receive Items</Button>
        </div>
      </form>
    </Modal>
  );
}
