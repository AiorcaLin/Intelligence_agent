"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, FlaskConical } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { TemplateCard } from "@/components/cocreate/template-card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { templateAPI } from "@/lib/api";

interface Template {
  id: string;
  name: string;
  domain: string;
  description: string;
  adoptionCount: number;
  qualityScore: number;
  creatorName: string;
}

export default function CocreatePage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [domainFilter, setDomainFilter] = useState("");

  useEffect(() => {
    loadTemplates();
  }, [domainFilter]);

  const loadTemplates = async () => {
    try {
      const { data } = await templateAPI.list({
        domain: domainFilter || undefined,
        sort: "adoption_count",
      });
      setTemplates(data);
    } catch {
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  const filtered = templates.filter(
    (t) =>
      !search ||
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase())
  );

  const domains = ["", "AI", "Crypto"];

  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">共创中心</h1>
          <p className="text-muted-foreground mt-1">
            发现和采用社区共创的情报分析配方
          </p>
        </div>

        {/* Search and filter */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜索配方..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <div className="flex gap-2">
            {domains.map((d) => (
              <button
                key={d}
                onClick={() => setDomainFilter(d)}
                className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                  domainFilter === d
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border text-muted-foreground hover:border-border/80"
                }`}
              >
                {d || "全部"}
              </button>
            ))}
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="border-border/50">
                <CardContent className="p-5 space-y-3">
                  <Skeleton className="h-5 w-16" />
                  <Skeleton className="h-5 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-1/2" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Empty */}
        {!loading && filtered.length === 0 && (
          <Card className="border-border/50 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted mb-4">
                <FlaskConical className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">暂无配方</h3>
              <p className="text-muted-foreground text-sm">
                {search ? "未找到匹配的配方" : "共创配方即将上线"}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Grid */}
        {!loading && filtered.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((t) => (
              <TemplateCard
                key={t.id}
                template={t}
                onClick={(id) => router.push(`/cocreate/${id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
