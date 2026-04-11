"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, TrendingUp } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { creditAPI } from "@/lib/api";

interface Earning {
  id: string;
  date: string;
  templateName: string;
  usedBy: string;
  credits: number;
}

export default function EarningsPage() {
  const [earnings, setEarnings] = useState<Earning[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    loadEarnings();
  }, [page]);

  const loadEarnings = async () => {
    setLoading(true);
    try {
      const { data } = await creditAPI.earnings({ page, limit: 20 });
      setEarnings(data?.earnings || []);
    } catch {
      setEarnings([]);
    } finally {
      setLoading(false);
    }
  };

  const totalEarned = earnings.reduce((sum, e) => sum + e.credits, 0);

  return (
    <DashboardShell>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/credits">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">创作者收益</h1>
            <p className="text-muted-foreground mt-1">
              查看配方被使用获得的积分收益
            </p>
          </div>
        </div>

        {/* Earnings summary */}
        <Card className="border-border/50 bg-gradient-to-br from-emerald-500/5 to-emerald-500/10">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/20">
                <TrendingUp className="h-5 w-5 text-emerald-400" />
              </div>
              <span className="text-sm text-muted-foreground">
                本页累计收益
              </span>
            </div>
            <p className="text-3xl font-bold text-emerald-400">
              +{totalEarned}
              <span className="text-base font-normal text-muted-foreground ml-1">
                积分
              </span>
            </p>
          </CardContent>
        </Card>

        {/* Earnings table */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-lg">收益明细</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="grid grid-cols-12 gap-4 px-6 py-3 border-b text-xs font-medium text-muted-foreground uppercase tracking-wider">
              <div className="col-span-3">日期</div>
              <div className="col-span-4">配方名称</div>
              <div className="col-span-3">使用者</div>
              <div className="col-span-2 text-right">积分</div>
            </div>

            {loading ? (
              <div className="p-6 space-y-3">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : earnings.length === 0 ? (
              <div className="p-12 text-center text-muted-foreground text-sm">
                暂无收益记录。发布共创配方后，每次被使用都将获得积分奖励。
              </div>
            ) : (
              <div className="divide-y divide-border">
                {earnings.map((e) => (
                  <div
                    key={e.id}
                    className="grid grid-cols-12 gap-4 px-6 py-3 items-center text-sm hover:bg-muted/30 transition-colors"
                  >
                    <div className="col-span-3 text-muted-foreground">
                      {e.date}
                    </div>
                    <div className="col-span-4 font-medium">
                      {e.templateName}
                    </div>
                    <div className="col-span-3 text-muted-foreground">
                      {e.usedBy}
                    </div>
                    <div className="col-span-2 text-right font-semibold text-emerald-400">
                      +{e.credits}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pagination */}
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            上一页
          </Button>
          <span className="flex items-center px-3 text-sm text-muted-foreground">
            第 {page} 页
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={earnings.length < 20}
          >
            下一页
          </Button>
        </div>
      </div>
    </DashboardShell>
  );
}
