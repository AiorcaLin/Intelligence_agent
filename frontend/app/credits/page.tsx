"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Coins, Sparkles, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { creditAPI } from "@/lib/api";

interface CreditBalance {
  balance: number;
  freeRemaining: number;
}

interface Transaction {
  id: string;
  date: string;
  type: string;
  amount: number;
  description: string;
}

export default function CreditsPage() {
  const [balance, setBalance] = useState<CreditBalance | null>(null);
  const [records, setRecords] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [balRes, recRes] = await Promise.all([
        creditAPI.balance(),
        creditAPI.records({ limit: 10 }),
      ]);
      setBalance(balRes.data);
      setRecords(recRes.data?.records || []);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">积分管理</h1>
          <p className="text-muted-foreground mt-1">查看余额和消费记录</p>
        </div>

        {/* Balance display */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="border-border/50 bg-gradient-to-br from-primary/5 to-primary/10">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/20">
                  <Coins className="h-5 w-5 text-primary" />
                </div>
                <span className="text-sm text-muted-foreground">总积分余额</span>
              </div>
              {loading ? (
                <Skeleton className="h-10 w-32" />
              ) : (
                <p className="text-4xl font-bold">{balance?.balance?.toLocaleString() ?? 0}</p>
              )}
            </CardContent>
          </Card>
          <Card className="border-border/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10">
                  <Sparkles className="h-5 w-5 text-emerald-400" />
                </div>
                <span className="text-sm text-muted-foreground">今日免费额度</span>
              </div>
              {loading ? (
                <Skeleton className="h-10 w-32" />
              ) : (
                <p className="text-4xl font-bold">{balance?.freeRemaining ?? 0}</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick recharge */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-lg">快速充值</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {[
                { price: "¥10", credits: "1,000" },
                { price: "¥30", credits: "3,500" },
                { price: "¥100", credits: "13,000" },
              ].map((tier) => (
                <Link key={tier.price} href="/credits/recharge">
                  <Button variant="outline" className="h-auto py-3 px-5">
                    <div className="text-center">
                      <p className="font-bold">{tier.price}</p>
                      <p className="text-xs text-muted-foreground">
                        {tier.credits} 积分
                      </p>
                    </div>
                  </Button>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Tabs for records / earnings */}
        <Tabs defaultValue="records">
          <TabsList>
            <TabsTrigger value="records">消费记录</TabsTrigger>
            <TabsTrigger value="earnings">创作者收益</TabsTrigger>
          </TabsList>

          <TabsContent value="records" className="mt-4">
            <Card className="border-border/50">
              <CardContent className="p-0">
                {loading ? (
                  <div className="p-6 space-y-3">
                    {[1, 2, 3].map((i) => (
                      <Skeleton key={i} className="h-12 w-full" />
                    ))}
                  </div>
                ) : records.length === 0 ? (
                  <div className="p-6 text-center text-muted-foreground text-sm">
                    暂无消费记录
                  </div>
                ) : (
                  <div className="divide-y divide-border">
                    {records.map((r) => (
                      <div
                        key={r.id}
                        className="flex items-center justify-between px-6 py-3"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`flex h-8 w-8 items-center justify-center rounded-full ${
                              r.amount < 0
                                ? "bg-red-500/10"
                                : "bg-emerald-500/10"
                            }`}
                          >
                            {r.amount < 0 ? (
                              <ArrowUpRight className="h-4 w-4 text-red-400" />
                            ) : (
                              <ArrowDownRight className="h-4 w-4 text-emerald-400" />
                            )}
                          </div>
                          <div>
                            <p className="text-sm font-medium">
                              {r.description}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {r.date}
                            </p>
                          </div>
                        </div>
                        <span
                          className={`text-sm font-semibold ${
                            r.amount < 0 ? "text-red-400" : "text-emerald-400"
                          }`}
                        >
                          {r.amount > 0 ? "+" : ""}
                          {r.amount}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
            <div className="mt-4 text-center">
              <Link href="/credits/records">
                <Button variant="ghost" size="sm">
                  查看全部消费记录
                </Button>
              </Link>
            </div>
          </TabsContent>

          <TabsContent value="earnings" className="mt-4">
            <Card className="border-border/50">
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground text-sm">
                  当你的共创配方被其他用户使用时，你将获得积分收益
                </p>
                <Link href="/credits/earnings" className="mt-4 inline-block">
                  <Button variant="ghost" size="sm">
                    查看创作者收益
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardShell>
  );
}
