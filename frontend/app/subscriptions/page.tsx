"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Plus, Rss } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { SubCard } from "@/components/subscriptions/sub-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { subscriptionAPI } from "@/lib/api";
import type { Subscription } from "@/lib/store";

export default function SubscriptionsPage() {
  const router = useRouter();
  const [subs, setSubs] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubs();
  }, []);

  const loadSubs = async () => {
    try {
      const { data } = await subscriptionAPI.list();
      setSubs(data);
    } catch {
      setSubs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (id: string) => {
    try {
      await subscriptionAPI.toggle(id);
      setSubs((prev) =>
        prev.map((s) =>
          s.id === id ? { ...s, isActive: !s.isActive } : s
        )
      );
    } catch {
      // ignore
    }
  };

  return (
    <DashboardShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">订阅管理</h1>
            <p className="text-muted-foreground mt-1">管理你的情报订阅源</p>
          </div>
          <Link href="/subscriptions/new">
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              创建新订阅
            </Button>
          </Link>
        </div>

        {loading && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="border-border/50">
                <CardContent className="p-5 space-y-3">
                  <Skeleton className="h-5 w-2/3" />
                  <Skeleton className="h-4 w-1/2" />
                  <Skeleton className="h-4 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && subs.length === 0 && (
          <Card className="border-border/50 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted mb-4">
                <Rss className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">还没有订阅</h3>
              <p className="text-muted-foreground text-sm text-center max-w-sm mb-6">
                创建你的第一个订阅，开始接收AI情报分析
              </p>
              <Link href="/subscriptions/new">
                <Button className="gap-2">
                  <Plus className="h-4 w-4" />
                  创建新订阅
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {!loading && subs.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {subs.map((sub) => (
              <SubCard
                key={sub.id}
                subscription={sub}
                onToggle={handleToggle}
                onClick={(id) => router.push(`/subscriptions/${id}/edit`)}
              />
            ))}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
