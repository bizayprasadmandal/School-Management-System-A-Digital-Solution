import React, { useRef, useEffect, useState, useCallback } from "react";
import { Spinner } from "./index";

interface InfiniteScrollProps<T> {
  /** All items loaded so far */
  items: T[];
  /** Total count from API (for "X of Y" display) */
  totalCount?: number;
  /** Whether more data is available */
  hasMore: boolean;
  /** Whether initial data is loading */
  isLoading: boolean;
  /** Whether next page is being fetched */
  isFetchingNext: boolean;
  /** Callback to load the next page */
  onLoadMore: () => void;
  /** Number of items per page (for display) */
  pageSize?: number;
  /** Render function for each item */
  renderItem: (item: T, index: number) => React.ReactNode;
  /** Optional loading skeleton for the next page */
  loadingSkeleton?: React.ReactNode;
  /** Empty state when no items */
  emptyState?: React.ReactNode;
  /** Optional end-of-list message */
  endMessage?: string;
  /** Root element for IntersectionObserver (default: viewport) */
  root?: React.RefObject<HTMLElement>;
  /** Margin around root for提前触发 (default: "200px") */
  rootMargin?: string;
}

/**
 * Infinite scroll container using IntersectionObserver.
 * Replaces pagination with automatic loading as user scrolls down.
 *
 * Usage:
 *   <InfiniteScroll
 *     items={data}
 *     hasMore={hasMore}
 *     isLoading={isLoading}
 *     isFetchingNext={isFetchingNext}
 *     onLoadMore={fetchNextPage}
 *     renderItem={(item) => <Card item={item} />}
 *   />
 */
export function InfiniteScroll<T>({
  items,
  totalCount,
  hasMore,
  isLoading,
  isFetchingNext,
  onLoadMore,
  pageSize = 12,
  renderItem,
  loadingSkeleton,
  emptyState,
  endMessage = "No more items to load",
  root,
  rootMargin = "200px",
}: InfiniteScrollProps<T>) {
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasMore || isFetchingNext) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isFetchingNext) {
          onLoadMore();
        }
      },
      {
        root: root?.current || null,
        rootMargin,
        threshold: 0,
      },
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, isFetchingNext, onLoadMore, root, rootMargin]);

  if (isLoading) {
    return (
      loadingSkeleton || (
        <div className="flex items-center justify-center py-12">
          <Spinner size="md" />
        </div>
      )
    );
  }

  if (items.length === 0) {
    return (
      emptyState || (
        <div className="py-12 text-center text-slate-500 dark:text-slate-400">No items found</div>
      )
    );
  }

  return (
    <div className="space-y-2">
      {items.map((item, index) => (
        <React.Fragment key={(item as any).id || index}>{renderItem(item, index)}</React.Fragment>
      ))}

      {/* Sentinel element for intersection observer */}
      <div ref={sentinelRef} className="h-1" />

      {/* Loading indicator for next page */}
      {isFetchingNext && (
        <div className="flex items-center justify-center py-4">
          <Spinner size="sm" />
          <span className="ml-2 text-sm text-slate-500 dark:text-slate-400">Loading more...</span>
        </div>
      )}

      {/* End of list message */}
      {!hasMore && items.length > 0 && (
        <p className="py-4 text-center text-sm text-slate-400 dark:text-slate-500">{endMessage}</p>
      )}

      {/* Item count */}
      {totalCount !== undefined && (
        <p className="py-2 text-center text-xs text-slate-400 dark:text-slate-500">
          Showing {items.length} of {totalCount.toLocaleString()}
        </p>
      )}
    </div>
  );
}

/**
 * Hook for managing infinite scroll state with React Query.
 * Wraps useInfiniteQuery patterns.
 */
export function useInfiniteScroll({
  queryKey,
  fetchFn,
  pageSize = 12,
}: {
  queryKey: string;
  fetchFn: (page: number) => Promise<{ results: any[]; count: number }>;
  pageSize?: number;
}) {
  const [items, setItems] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isFetchingNext, setIsFetchingNext] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const loadInitial = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchFn(1);
      setItems(data.results);
      setTotalCount(data.count);
      setHasMore(data.results.length < data.count);
      setPage(1);
    } catch {
      // Error handling
    } finally {
      setIsLoading(false);
    }
  }, [fetchFn]);

  const loadMore = useCallback(async () => {
    if (isFetchingNext || !hasMore) return;
    setIsFetchingNext(true);
    try {
      const nextPage = page + 1;
      const data = await fetchFn(nextPage);
      setItems((prev) => [...prev, ...data.results]);
      setTotalCount(data.count);
      setHasMore((prev) => prev && items.length + data.results.length < data.count);
      setPage(nextPage);
    } catch {
      // Error handling
    } finally {
      setIsFetchingNext(false);
    }
  }, [page, hasMore, isFetchingNext, fetchFn, items.length]);

  const reset = useCallback(() => {
    setItems([]);
    setPage(1);
    setHasMore(true);
    setIsLoading(true);
    setTotalCount(0);
  }, []);

  return {
    items,
    page,
    hasMore,
    isLoading,
    isFetchingNext,
    totalCount,
    loadInitial,
    loadMore,
    reset,
    setItems,
  };
}
