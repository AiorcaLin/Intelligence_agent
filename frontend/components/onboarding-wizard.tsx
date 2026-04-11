"use client";

import { useState } from "react";
import {
  ArrowRight,
  ArrowLeft,
  Rss,
  Brain,
  Eye,
  BookOpen,
  Microscope,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/components/ui/cn";

interface OnboardingData {
  domain: string;
  density: string;
  frequency: string;
  name: string;
}

interface OnboardingWizardProps {
  onComplete: (data: OnboardingData) => void;
}

const steps = ["选择领域", "信息密度", "推送频率", "确认"];

export function OnboardingWizard({ onComplete }: OnboardingWizardProps) {
  const [step, setStep] = useState(0);
  const [data, setData] = useState<OnboardingData>({
    domain: "AI",
    density: "standard",
    frequency: "daily",
    name: "",
  });

  const update = <K extends keyof OnboardingData>(
    key: K,
    value: OnboardingData[K]
  ) => setData((prev) => ({ ...prev, [key]: value }));

  const next = () => {
    if (step < steps.length - 1) setStep(step + 1);
    else onComplete(data);
  };

  const prev = () => {
    if (step > 0) setStep(step - 1);
  };

  return (
    <div className="max-w-lg mx-auto">
      {/* Progress */}
      <div className="flex items-center justify-center gap-2 mb-8">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center">
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold transition-all",
                i < step
                  ? "bg-primary text-primary-foreground"
                  : i === step
                  ? "bg-primary/20 text-primary border-2 border-primary"
                  : "bg-muted text-muted-foreground"
              )}
            >
              {i < step ? <Check className="h-4 w-4" /> : i + 1}
            </div>
            {i < steps.length - 1 && (
              <div
                className={cn(
                  "h-0.5 w-8 mx-1",
                  i < step ? "bg-primary" : "bg-muted"
                )}
              />
            )}
          </div>
        ))}
      </div>

      <Card className="border-border/50">
        <CardContent className="p-6">
          {/* Step 0: Domain */}
          {step === 0 && (
            <div className="space-y-4">
              <div className="text-center mb-6">
                <Rss className="h-10 w-10 text-primary mx-auto mb-3" />
                <h2 className="text-xl font-bold">选择你关注的领域</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  我们将为你采集该领域的最新情报
                </p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { value: "AI", label: "人工智能" },
                  { value: "Crypto", label: "加密货币" },
                  { value: "Tech", label: "科技行业" },
                  { value: "Finance", label: "金融市场" },
                ].map((d) => (
                  <button
                    key={d.value}
                    type="button"
                    onClick={() => update("domain", d.value)}
                    className={cn(
                      "rounded-lg border p-4 text-center transition-all",
                      data.domain === d.value
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border hover:border-border/80"
                    )}
                  >
                    <span className="font-medium">{d.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 1: Density */}
          {step === 1 && (
            <div className="space-y-4">
              <div className="text-center mb-6">
                <Brain className="h-10 w-10 text-primary mx-auto mb-3" />
                <h2 className="text-xl font-bold">选择信息密度</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  决定每条情报的详细程度
                </p>
              </div>
              <div className="space-y-3">
                {[
                  { value: "brief", label: "速览", desc: "每条50字摘要", icon: Eye },
                  { value: "standard", label: "标准", desc: "详细摘要+行动建议", icon: BookOpen },
                  { value: "research", label: "研究级", desc: "深度分析+数据图表", icon: Microscope },
                ].map((d) => (
                  <button
                    key={d.value}
                    type="button"
                    onClick={() => update("density", d.value)}
                    className={cn(
                      "flex items-center gap-4 w-full rounded-lg border p-4 text-left transition-all",
                      data.density === d.value
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-border/80"
                    )}
                  >
                    <d.icon className="h-6 w-6 text-primary shrink-0" />
                    <div>
                      <span className="font-medium">{d.label}</span>
                      <p className="text-xs text-muted-foreground">{d.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Frequency */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="text-center mb-6">
                <h2 className="text-xl font-bold">推送频率</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  多久收到一次情报更新
                </p>
              </div>
              <div className="space-y-3">
                {[
                  { value: "daily", label: "每日", desc: "每天推送最新情报" },
                  { value: "weekly", label: "每周", desc: "每周汇总推送" },
                  { value: "breaking", label: "仅重大事件", desc: "只在重大事件时通知" },
                ].map((d) => (
                  <button
                    key={d.value}
                    type="button"
                    onClick={() => update("frequency", d.value)}
                    className={cn(
                      "flex items-center gap-4 w-full rounded-lg border p-4 text-left transition-all",
                      data.frequency === d.value
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-border/80"
                    )}
                  >
                    <div>
                      <span className="font-medium">{d.label}</span>
                      <p className="text-xs text-muted-foreground">{d.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Confirm */}
          {step === 3 && (
            <div className="space-y-4">
              <div className="text-center mb-6">
                <Check className="h-10 w-10 text-primary mx-auto mb-3" />
                <h2 className="text-xl font-bold">确认你的订阅</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  为你的订阅取个名字
                </p>
              </div>
              <div className="space-y-3">
                <div className="space-y-2">
                  <Label>订阅名称</Label>
                  <Input
                    placeholder={`${data.domain} 日报`}
                    value={data.name}
                    onChange={(e) => update("name", e.target.value)}
                  />
                </div>
                <div className="rounded-lg bg-muted/50 p-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">领域</span>
                    <span className="font-medium">{data.domain}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">密度</span>
                    <span className="font-medium">{data.density}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">频率</span>
                    <span className="font-medium">{data.frequency}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation buttons */}
          <div className="flex justify-between mt-8">
            <Button
              variant="ghost"
              onClick={prev}
              disabled={step === 0}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              上一步
            </Button>
            <Button onClick={next} className="gap-2">
              {step === steps.length - 1 ? "创建订阅" : "下一步"}
              {step < steps.length - 1 && <ArrowRight className="h-4 w-4" />}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
