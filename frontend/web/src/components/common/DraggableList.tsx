import React from "react";
import { Reorder } from "framer-motion";
import { Bars3Icon } from "@heroicons/react/24/outline";

interface DraggableListProps<T extends { id: string }> {
  items: T[];
  onReorder: (items: T[]) => void;
  renderItem: (item: T, dragControls: any) => React.ReactNode;
  className?: string;
}

/**
 * Reusable drag-and-drop list using framer-motion Reorder.
 * Items can be dragged to reorder via a handle icon.
 */
export function DraggableList<T extends { id: string }>({
  items,
  onReorder,
  renderItem,
  className,
}: DraggableListProps<T>) {
  return (
    <Reorder.Group
      axis="y"
      values={items}
      onReorder={onReorder}
      className={className || "space-y-2"}
    >
      {items.map((item) => (
        <Reorder.Item
          key={item.id}
          value={item}
          className="cursor-grab active:cursor-grabbing"
          whileDrag={{ scale: 1.02, boxShadow: "0 8px 32px rgba(0,0,0,0.12)" }}
        >
          {renderItem(item, null)}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  );
}

/**
 * Drag handle icon component to show grab affordance.
 */
export function DragHandle({ className }: { className?: string }) {
  return (
    <Bars3Icon
      className={`h-5 w-5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 ${
        className || ""
      }`}
    />
  );
}
