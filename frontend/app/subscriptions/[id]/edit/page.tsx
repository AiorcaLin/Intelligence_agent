"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Trash2, Loader2 } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { SubForm, type SubFormData } from "@/components/subscriptions/sub-form";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { subscriptionAPI } from "@/lib/api";
import type { Subscription } from "@/lib/store";

export default function EditSubscriptionPage() {
  const params = useParams();
  const router = useRouter();
  const subId = params.id as string;
  const [sub, setSub] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!subId) return;
    (async () => {
      try {
        const { data } = await subscriptionAPI.get(subId);
        setSub(data);
      } catch {
        setSub(null);
      } finally {
        setLoading(false);
      }
    })();
  }, [subId]);

  const handleSubmit = async (data: SubFormData) => {
    await subscriptionAPI.update(subId, data as unknown as Record<string, unknown>);
    router.push("/subscriptions");
  };

  const handleDelete = async () => {
    if (!confirm("确定要删除此订阅吗？")) return;
    setDeleting(true);
    try {
      await subscriptionAPI.delete(subId);
      router.push("/subscriptions");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <DashboardShell>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/subscriptions">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">编辑订阅</h1>
              <p className="text-muted-foreground mt-1">
                修改订阅配置
              </p>
            </div>
          </div>
          <Button
            variant="destructive"
            size="sm"
            onClick={handleDelete}
            disabled={deleting}
            className="gap-2"
          >
            {deleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
            删除
          </Button>
        </div>

        {loading && (
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        )}

        {!loading && sub && (
          <SubForm
            initialData={{
              name: sub.name,
              domain: sub.domain,
              customKeywords: sub.customKeywords,
              density: sub.density,
              formats: sub.formats,
              frequency: sub.frequency,
              pushTime: sub.pushTime,
              templateId: sub.templateId,
            }}
            onSubmit={handleSubmit}
            submitLabel="保存修改"
          />
        )}
      </div>
    </DashboardShell>
  );
}
