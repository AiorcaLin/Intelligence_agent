"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Calendar } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { ReportCard } from "@/components/intel/report-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { intelAPI } from "@/lib/api";
import type { Report } from "@/lib/store";

export default function ReportDetailPage() {
  const params = useParams();
  const reportId = params.reportId as string;
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!reportId) return;
    (async () => {
      try {
        const { data } = await intelAPI.getReport(reportId);
        setReport(data);
      } catch {
        setReport(null);
      } finally {
        setLoading(false);
      }
    })();
  }, [reportId]);

  return (
    <DashboardShell>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/intel">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">情报详情</h1>
            {report && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                <Calendar className="h-3.5 w-3.5" />
                <span>{report.date}</span>
              </div>
            )}
          </div>
        </div>

        {loading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="border-border/50">
                <CardContent className="p-5 space-y-3">
                  <Skeleton className="h-5 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && !report && (
          <Card className="border-border/50 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <h3 className="text-lg font-semibold mb-2">报告未找到</h3>
              <p className="text-muted-foreground text-sm mb-4">
                该情报报告可能已被删除或不存在
              </p>
              <Link href="/intel">
                <Button>返回情报中心</Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {report && (
          <div className="space-y-3">
            {report.items.map((item) => (
              <ReportCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
