"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Check, Loader2, Wallet } from "lucide-react";
import { DashboardShell } from "@/components/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/components/ui/cn";
import { creditAPI } from "@/lib/api";

const tiers = [
  {
    id: "basic",
    name: "入门",
    price: 10,
    credits: 1000,
    bonus: 0,
    features: ["1,000 积分", "约10次标准情报", "文字格式输出"],
  },
  {
    id: "standard",
    name: "标准",
    price: 30,
    credits: 3500,
    bonus: 500,
    popular: true,
    features: ["3,500 积分", "赠送500积分", "全格式输出", "优先生成"],
  },
  {
    id: "pro",
    name: "专业",
    price: 100,
    credits: 13000,
    bonus: 3000,
    features: ["13,000 积分", "赠送3,000积分", "全格式输出", "优先生成", "专属客服"],
  },
];

const paymentMethods = [
  { id: "alipay", name: "支付宝", color: "text-blue-400" },
  { id: "wechat", name: "微信支付", color: "text-green-400" },
];

export default function RechargePage() {
  const [selectedTier, setSelectedTier] = useState("standard");
  const [paymentMethod, setPaymentMethod] = useState("alipay");
  const [loading, setLoading] = useState(false);

  const handleRecharge = async () => {
    setLoading(true);
    try {
      await creditAPI.recharge({ tier: selectedTier, paymentMethod });
    } finally {
      setLoading(false);
    }
  };

  const selected = tiers.find((t) => t.id === selectedTier);

  return (
    <DashboardShell>
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/credits">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">积分充值</h1>
            <p className="text-muted-foreground mt-1">选择套餐和支付方式</p>
          </div>
        </div>

        {/* Tier selection */}
        <div className="grid gap-4 sm:grid-cols-3">
          {tiers.map((tier) => (
            <Card
              key={tier.id}
              className={cn(
                "cursor-pointer transition-all duration-200 relative",
                selectedTier === tier.id
                  ? "border-primary shadow-lg shadow-primary/10"
                  : "border-border/50 hover:border-border"
              )}
              onClick={() => setSelectedTier(tier.id)}
            >
              {tier.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="px-3">最受欢迎</Badge>
                </div>
              )}
              <CardContent className="p-5 text-center">
                <h3 className="font-semibold mb-1">{tier.name}</h3>
                <div className="mb-3">
                  <span className="text-3xl font-bold">¥{tier.price}</span>
                </div>
                <p className="text-sm text-primary font-medium mb-3">
                  {tier.credits.toLocaleString()} 积分
                  {tier.bonus > 0 && (
                    <span className="text-emerald-400">
                      {" "}
                      +{tier.bonus.toLocaleString()}
                    </span>
                  )}
                </p>
                <ul className="space-y-1.5 text-sm text-left">
                  {tier.features.map((f) => (
                    <li key={f} className="flex items-center gap-2">
                      <Check className="h-3.5 w-3.5 text-primary shrink-0" />
                      <span className="text-muted-foreground">{f}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Payment method */}
        <Card className="border-border/50">
          <CardContent className="p-5">
            <h3 className="font-semibold mb-4">支付方式</h3>
            <div className="flex gap-3">
              {paymentMethods.map((pm) => (
                <button
                  key={pm.id}
                  onClick={() => setPaymentMethod(pm.id)}
                  className={cn(
                    "flex items-center gap-2 rounded-lg border px-5 py-3 text-sm font-medium transition-all",
                    paymentMethod === pm.id
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-border/80"
                  )}
                >
                  <Wallet className={cn("h-4 w-4", pm.color)} />
                  {pm.name}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Confirm */}
        <Card className="border-border/50">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-4">
              <span className="text-muted-foreground">套餐</span>
              <span className="font-medium">{selected?.name}</span>
            </div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-muted-foreground">积分</span>
              <span className="font-medium">
                {selected?.credits.toLocaleString()}
                {selected?.bonus ? ` + ${selected.bonus.toLocaleString()}` : ""}
              </span>
            </div>
            <div className="flex items-center justify-between mb-6">
              <span className="text-muted-foreground">支付金额</span>
              <span className="text-2xl font-bold text-primary">
                ¥{selected?.price}
              </span>
            </div>
            <Button
              size="lg"
              className="w-full"
              onClick={handleRecharge}
              disabled={loading}
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              确认支付
            </Button>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
