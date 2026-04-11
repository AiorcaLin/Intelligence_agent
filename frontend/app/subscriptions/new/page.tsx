"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { SubForm, type SubFormData } from "@/components/subscriptions/sub-form";
import { Button } from "@/components/ui/button";
import { subscriptionAPI } from "@/lib/api";

export default function NewSubscriptionPage() {
  const router = useRouter();

  const handleSubmit = async (data: SubFormData) => {
    await subscriptionAPI.create(data as unknown as Record<string, unknown>);
    router.push("/subscriptions");
  };

  return (
    <DashboardShell>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/subscriptions">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">创建新订阅</h1>
            <p className="text-muted-foreground mt-1">
              配置你的情报订阅源
            </p>
          </div>
        </div>

        <SubForm onSubmit={handleSubmit} submitLabel="创建订阅" />
      </div>
    </DashboardShell>
  );
}
