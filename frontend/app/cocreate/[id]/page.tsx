"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Users,
  Star,
  Sparkles,
  Download,
  Loader2,
} from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { LineageTree } from "@/components/cocreate/lineage-tree";
import { ForkDialog } from "@/components/cocreate/fork-dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/components/ui/cn";
import { templateAPI } from "@/lib/api";

interface TemplateDetail {
  id: string;
  name: string;
  domain: string;
  description: string;
  adoptionCount: number;
  qualityScore: number;
  creatorName: string;
  config: {
    collectionWeights: Record<string, number>;
    filteringRules: string[];
  };
  contributors: { name: string; score: number }[];
}

interface LineageNode {
  id: string;
  name: string;
  creatorName: string;
  children?: LineageNode[];
  isCurrent?: boolean;
}

export default function TemplateDetailPage() {
  const params = useParams();
  const templateId = params.id as string;
  const [template, setTemplate] = useState<TemplateDetail | null>(null);
  const [lineage, setLineage] = useState<LineageNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [adopting, setAdopting] = useState(false);
  const [trying, setTrying] = useState(false);

  useEffect(() => {
    if (!templateId) return;
    loadData();
  }, [templateId]);

  const loadData = async () => {
    try {
      const [tplRes, lineageRes] = await Promise.all([
        templateAPI.get(templateId),
        templateAPI.lineage(templateId),
      ]);
      setTemplate(tplRes.data);
      setLineage(lineageRes.data);
    } catch {
      setTemplate(null);
    } finally {
      setLoading(false);
    }
  };

  const handleTry = async () => {
    setTrying(true);
    try {
      await templateAPI.tryTemplate(templateId);
    } finally {
      setTrying(false);
    }
  };

  const handleAdopt = async () => {
    setAdopting(true);
    try {
      await templateAPI.adopt(templateId);
    } finally {
      setAdopting(false);
    }
  };

  const handleFork = async (name: string, description: string) => {
    await templateAPI.fork(templateId, { name, description });
  };

  return (
    <DashboardShell>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/cocreate">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold tracking-tight">配方详情</h1>
        </div>

        {loading && (
          <div className="space-y-4">
            <Skeleton className="h-8 w-1/2" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-40 w-full" />
          </div>
        )}

        {!loading && !template && (
          <Card className="border-border/50 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <h3 className="text-lg font-semibold mb-2">配方未找到</h3>
              <Link href="/cocreate">
                <Button>返回共创中心</Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {template && (
          <>
            {/* Header */}
            <Card className="border-border/50">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className="text-[11px]">
                        {template.domain}
                      </Badge>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Users className="h-3.5 w-3.5" />
                        <span>{template.adoptionCount} 人使用</span>
                      </div>
                    </div>
                    <h2 className="text-xl font-bold mb-2">{template.name}</h2>
                    <p className="text-muted-foreground">
                      {template.description}
                    </p>
                    <div className="flex items-center gap-1 mt-3">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className={cn(
                            "h-4 w-4",
                            i < Math.round(template.qualityScore)
                              ? "fill-amber-400 text-amber-400"
                              : "text-muted-foreground/30"
                          )}
                        />
                      ))}
                      <span className="text-sm text-muted-foreground ml-2">
                        {template.qualityScore.toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>

                <Separator className="my-4" />

                <div className="flex flex-wrap gap-3">
                  <Button onClick={handleTry} disabled={trying} className="gap-2">
                    {trying ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Sparkles className="h-4 w-4" />
                    )}
                    免费试用
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={handleAdopt}
                    disabled={adopting}
                    className="gap-2"
                  >
                    {adopting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Download className="h-4 w-4" />
                    )}
                    采用此配方
                  </Button>
                  <ForkDialog
                    templateName={template.name}
                    onFork={handleFork}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Config preview */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-lg">配方配置</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium mb-2">采集权重</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(template.config.collectionWeights).map(
                        ([key, value]) => (
                          <div
                            key={key}
                            className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2 text-sm"
                          >
                            <span>{key}</span>
                            <span className="font-medium text-primary">
                              {(value * 100).toFixed(0)}%
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium mb-2">过滤规则</h4>
                    <ul className="space-y-1">
                      {template.config.filteringRules.map((rule, i) => (
                        <li
                          key={i}
                          className="flex items-start gap-2 text-sm text-muted-foreground"
                        >
                          <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                          {rule}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Contributors */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-lg">贡献者</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {template.contributors.map((c, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2"
                    >
                      <span className="text-sm font-medium">{c.name}</span>
                      <span className="text-sm text-primary">
                        {c.score} 分
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Lineage tree */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-lg">配方族谱</CardTitle>
              </CardHeader>
              <CardContent>
                <LineageTree root={lineage} />
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardShell>
  );
}
