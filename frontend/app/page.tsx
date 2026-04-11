"use client";

import Link from "next/link";
import {
  Globe,
  Brain,
  History,
  Lightbulb,
  MonitorPlay,
  FlaskConical,
  ArrowRight,
  Rss,
  Sparkles,
  Bell,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const features = [
  {
    icon: Globe,
    title: "多源采集",
    description: "自动从数百个信息源采集最新情报，覆盖新闻、论文、社交媒体、行业报告",
  },
  {
    icon: Brain,
    title: "智能分析",
    description: "AI深度分析每条情报的重要性、相关性和影响面，智能排序推送",
  },
  {
    icon: History,
    title: "历史脉络",
    description: "自动关联历史事件，构建事件发展时间线，洞察趋势演变",
  },
  {
    icon: Lightbulb,
    title: "行动建议",
    description: "基于情报分析生成可执行的行动建议，助力快速决策",
  },
  {
    icon: MonitorPlay,
    title: "多模态输出",
    description: "支持文字、音频、视频多种输出格式，适配不同阅读场景",
  },
  {
    icon: FlaskConical,
    title: "共创配方",
    description: "社区共创分析配方，持续优化情报质量，创作者获得积分收益",
  },
];

const steps = [
  {
    icon: Rss,
    step: "01",
    title: "创建订阅",
    description: "选择关注领域，自定义关键词、信息密度和推送频率",
  },
  {
    icon: Sparkles,
    step: "02",
    title: "自动生成",
    description: "AI自动采集、分析、筛选，生成结构化情报报告",
  },
  {
    icon: Bell,
    step: "03",
    title: "每日推送",
    description: "按时推送情报到你的收件箱，重大事件实时通知",
  },
];

const pricingTiers = [
  {
    name: "入门",
    price: "¥10",
    credits: "1,000",
    description: "适合轻度使用",
    features: ["1,000 积分", "约10次标准情报", "文字格式输出"],
  },
  {
    name: "标准",
    price: "¥30",
    credits: "3,500",
    description: "最受欢迎",
    popular: true,
    features: ["3,500 积分", "赠送500积分", "全格式输出", "优先生成"],
  },
  {
    name: "专业",
    price: "¥100",
    credits: "13,000",
    description: "适合重度用户",
    features: ["13,000 积分", "赠送3,000积分", "全格式输出", "优先生成", "专属客服"],
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <header className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Brain className="h-7 w-7 text-primary" />
            <span className="text-xl font-bold">智能情报分析师</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">
                登录
              </Button>
            </Link>
            <Link href="/register">
              <Button size="sm">免费体验</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden py-24 sm:py-32">
        <div className="absolute inset-0 -z-10">
          <div className="absolute left-1/2 top-0 -translate-x-1/2 w-[800px] h-[600px] rounded-full bg-primary/5 blur-[120px]" />
        </div>
        <div className="container mx-auto px-4 text-center">
          <Badge variant="secondary" className="mb-6 px-4 py-1.5">
            AI 驱动 · 每日更新 · 精准推送
          </Badge>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            你的
            <span className="text-gradient">AI情报分析师</span>
          </h1>
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            每天花2分钟，掌握你所在领域的一切重要动态。
            <br />
            多源采集 · 智能分析 · 行动建议 · 一键推送
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="gap-2 px-8">
                免费体验 <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="#features">
              <Button variant="outline" size="lg" className="px-8">
                了解更多
              </Button>
            </Link>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            新用户每日赠送100免费积分，无需绑定支付
          </p>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">为什么选择我们</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              六大核心能力，让你从信息洪流中解放出来
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <Card
                key={f.title}
                className="group border-border/50 bg-card/50 hover:bg-card hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
              >
                <CardHeader>
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-3 group-hover:bg-primary/20 transition-colors">
                    <f.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{f.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {f.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">三步开始</h2>
            <p className="text-muted-foreground">简单设置，即刻获取专属情报</p>
          </div>
          <div className="grid gap-8 md:grid-cols-3 max-w-4xl mx-auto">
            {steps.map((s, i) => (
              <div key={s.step} className="text-center group">
                <div className="relative mx-auto mb-6">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 mx-auto group-hover:bg-primary/20 transition-colors">
                    <s.icon className="h-8 w-8 text-primary" />
                  </div>
                  <span className="absolute -top-2 -right-2 flex h-7 w-7 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                    {s.step}
                  </span>
                </div>
                <h3 className="text-lg font-semibold mb-2">{s.title}</h3>
                <p className="text-muted-foreground text-sm">{s.description}</p>
                {i < steps.length - 1 && (
                  <ArrowRight className="hidden md:block h-5 w-5 text-muted-foreground/30 absolute right-0 top-1/2 -translate-y-1/2" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">积分套餐</h2>
            <p className="text-muted-foreground">
              按需充值，用多少买多少
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-3 max-w-4xl mx-auto">
            {pricingTiers.map((tier) => (
              <Card
                key={tier.name}
                className={`relative ${
                  tier.popular
                    ? "border-primary shadow-lg shadow-primary/10 scale-105"
                    : "border-border/50"
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="px-3">最受欢迎</Badge>
                  </div>
                )}
                <CardHeader className="text-center pb-2">
                  <CardTitle className="text-lg">{tier.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {tier.description}
                  </p>
                </CardHeader>
                <CardContent className="text-center">
                  <div className="mb-6">
                    <span className="text-4xl font-bold">{tier.price}</span>
                    <span className="text-muted-foreground ml-1">
                      / {tier.credits} 积分
                    </span>
                  </div>
                  <ul className="space-y-2 text-sm mb-6">
                    {tier.features.map((f) => (
                      <li key={f} className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-primary shrink-0" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                  <Link href="/register">
                    <Button
                      className="w-full"
                      variant={tier.popular ? "default" : "outline"}
                    >
                      开始使用
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="container mx-auto px-4">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Brain className="h-6 w-6 text-primary" />
                <span className="font-bold">智能情报分析师</span>
              </div>
              <p className="text-sm text-muted-foreground">
                AI驱动的情报分析平台，让信息为你工作。
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-3">产品</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#features" className="hover:text-foreground transition-colors">功能介绍</Link></li>
                <li><Link href="/cocreate" className="hover:text-foreground transition-colors">共创中心</Link></li>
                <li><Link href="/credits/recharge" className="hover:text-foreground transition-colors">积分套餐</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">支持</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">帮助中心</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">联系我们</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">反馈建议</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">法律</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">服务条款</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">隐私政策</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
            © 2026 智能情报分析师. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
