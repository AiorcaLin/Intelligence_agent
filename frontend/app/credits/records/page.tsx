"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { creditAPI } from "@/lib/api";

interface Record {
  id: string;
  date: string;
  type: string;
  amount: number;
  description: string;
  reportId?: string;
}

export default function RecordsPage() {
  const [records, setRecords] = useState<Record[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    loadRecords();
  }, [page]);

  const loadRecords = async () => {
    setLoading(true);
    try {
      const { data } = await creditAPI.records({ page, limit: 20 });
      setRecords(data?.records || []);
    } catch {
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

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
            <h1 className="text-2xl font-bold tracking-tight">消费记录</h1>
            <p className="text-muted-foreground mt-1">查看所有积分消费明细</p>
          </div>
        </div>

        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-lg">全部记录</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {/* Table header */}
            <div className="grid grid-cols-12 gap-4 px-6 py-3 border-b text-xs font-medium text-muted-foreground uppercase tracking-wider">
              <div className="col-span-3">日期</div>
              <div className="col-span-2">类型</div>
              <div className="col-span-4">描述</div>
              <div className="col-span-2 text-right">积分</div>
              <div className="col-span-1"></div>
            </div>

            {loading ? (
              <div className="p-6 space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : records.length === 0 ? (
              <div className="p-12 text-center text-muted-foreground text-sm">
                暂无消费记录
              </div>
            ) : (
              <div className="divide-y divide-border">
                {records.map((r) => (
                  <div
                    key={r.id}
                    className="grid grid-cols-12 gap-4 px-6 py-3 items-center text-sm hover:bg-muted/30 transition-colors"
                  >
                    <div className="col-span-3 text-muted-foreground">
                      {r.date}
                    </div>
                    <div className="col-span-2">
                      <span className="inline-flex items-center gap-1">
                        {r.amount < 0 ? (
                          <ArrowUpRight className="h-3.5 w-3.5 text-red-400" />
                        ) : (
                          <ArrowDownRight className="h-3.5 w-3.5 text-emerald-400" />
                        )}
                        {r.type}
                      </span>
                    </div>
                    <div className="col-span-4 truncate text-muted-foreground">
                      {r.description}
                    </div>
                    <div
                      className={`col-span-2 text-right font-medium ${
                        r.amount < 0 ? "text-red-400" : "text-emerald-400"
                      }`}
                    >
                      {r.amount > 0 ? "+" : ""}
                      {r.amount}
                    </div>
                    <div className="col-span-1 text-right">
                      {r.reportId && (
                        <Link
                          href={`/intel/${r.reportId}`}
                          className="text-xs text-primary hover:underline"
                        >
                          查看
                        </Link>
                      )}
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
            disabled={records.length < 20}
          >
            下一页
          </Button>
        </div>
      </div>
    </DashboardShell>
  );
}
