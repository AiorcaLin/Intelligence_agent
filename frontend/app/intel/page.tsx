"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Newspaper, Layers, Rss, Plus } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { ReportCard } from "@/components/intel/report-card";
import { RegenDialog } from "@/components/intel/regen-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { intelAPI } from "@/lib/api";
import type { Report, ReportItem } from "@/lib/store";

export default function IntelPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [allItems, setAllItems] = useState<ReportItem[]>([]);

  useEffect(() => {
    loadToday();
  }, []);

  const loadToday = async () => {
    try {
      const { data } = await intelAPI.getToday();
      setReports(data.reports || []);
      const merged = (data.reports || [])
        .flatMap((r: Report) => r.items)
        .sort((a: ReportItem, b: ReportItem) => b.importanceScore - a.importanceScore);
      setAllItems(merged);
    } catch {
      setReports([]);
      setAllItems([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleImportant = (id: string) => {
    setAllItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, isImportant: !item.isImportant } : item
      )
    );
  };

  const handleRegen = async (feedback: string) => {
    if (reports.length > 0) {
      await intelAPI.regenerate(reports[0].id, feedback);
      await loadToday();
    }
  };

  const domains = [...new Set(allItems.map((item) => item.domain))];
  const todayCount = allItems.length;
  const domainCount = domains.length;

  return (
    <DashboardShell>
      <div className="space-y-6">
        {/* Page header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight">情报中心</h1>
          <p className="text-muted-foreground mt-1">
            你的专属AI情报分析，每日更新
          </p>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-2">
          <Card className="border-border/50">
            <CardContent className="flex items-center gap-3 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Newspaper className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">{loading ? "—" : todayCount}</p>
                <p className="text-xs text-muted-foreground">今日情报数量</p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-border/50">
            <CardContent className="flex items-center gap-3 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10">
                <Layers className="h-5 w-5 text-emerald-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{loading ? "—" : domainCount}</p>
                <p className="text-xs text-muted-foreground">涵盖领域数</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="border-border/50">
                <CardContent className="p-5 space-y-3">
                  <div className="flex gap-2">
                    <Skeleton className="h-5 w-16" />
                    <Skeleton className="h-5 w-24" />
                  </div>
                  <Skeleton className="h-5 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && allItems.length === 0 && (
          <Card className="border-border/50 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted mb-4">
                <Rss className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">还没有情报</h3>
              <p className="text-muted-foreground text-sm text-center max-w-sm mb-6">
                创建你的第一个订阅，AI将自动为你采集和分析情报
              </p>
              <Link href="/subscriptions/new">
                <Button className="gap-2">
                  <Plus className="h-4 w-4" />
                  创建你的第一个订阅
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {/* Intel feed grouped by domain */}
        {!loading &&
          domains.map((domain, di) => {
            const domainItems = allItems.filter((item) => item.domain === domain);
            return (
              <div key={domain}>
                {di > 0 && <Separator className="my-6" />}
                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                  {domain} · {domainItems.length} 条情报
                </h2>
                <div className="space-y-3">
                  {domainItems.map((item) => (
                    <ReportCard
                      key={item.id}
                      item={item}
                      onToggleImportant={toggleImportant}
                    />
                  ))}
                </div>
              </div>
            );
          })}

        {/* Regen dialog */}
        {!loading && allItems.length > 0 && (
          <div className="flex justify-center pt-4 pb-8">
            <RegenDialog onConfirm={handleRegen} />
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
