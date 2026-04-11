"use client";

import { useState } from "react";
import {
  FileText,
  Headphones,
  Video,
  Loader2,
  X,
  Eye,
  BookOpen,
  Microscope,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/components/ui/cn";

export interface SubFormData {
  name: string;
  domain: string;
  customKeywords: string[];
  density: string;
  formats: string[];
  frequency: string;
  pushTime: string;
  templateId: string;
}

interface SubFormProps {
  initialData?: Partial<SubFormData>;
  onSubmit: (data: SubFormData) => Promise<void>;
  submitLabel?: string;
}

const densityOptions = [
  {
    value: "brief",
    label: "速览",
    description: "每条50字摘要，快速浏览",
    icon: Eye,
    cost: 30,
  },
  {
    value: "standard",
    label: "标准",
    description: "详细摘要+行动建议",
    icon: BookOpen,
    cost: 80,
  },
  {
    value: "research",
    label: "研究级",
    description: "深度分析+数据图表+完整溯源",
    icon: Microscope,
    cost: 200,
  },
];

const formatOptions = [
  { value: "text", label: "文字", icon: FileText },
  { value: "audio", label: "音频", icon: Headphones },
  { value: "video", label: "视频", icon: Video },
];

const timeSlots = Array.from({ length: 8 }, (_, i) => {
  const hour = i * 3;
  return `${hour.toString().padStart(2, "0")}:00`;
});

export function SubForm({
  initialData,
  onSubmit,
  submitLabel = "创建订阅",
}: SubFormProps) {
  const [form, setForm] = useState<SubFormData>({
    name: initialData?.name || "",
    domain: initialData?.domain || "AI",
    customKeywords: initialData?.customKeywords || [],
    density: initialData?.density || "standard",
    formats: initialData?.formats || ["text"],
    frequency: initialData?.frequency || "daily",
    pushTime: initialData?.pushTime || "09:00",
    templateId: initialData?.templateId || "",
  });
  const [keywordInput, setKeywordInput] = useState("");
  const [loading, setLoading] = useState(false);

  const update = <K extends keyof SubFormData>(key: K, value: SubFormData[K]) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const addKeyword = () => {
    const kw = keywordInput.trim();
    if (kw && !form.customKeywords.includes(kw)) {
      update("customKeywords", [...form.customKeywords, kw]);
      setKeywordInput("");
    }
  };

  const removeKeyword = (kw: string) => {
    update(
      "customKeywords",
      form.customKeywords.filter((k) => k !== kw)
    );
  };

  const toggleFormat = (fmt: string) => {
    if (form.formats.includes(fmt)) {
      if (form.formats.length > 1) {
        update("formats", form.formats.filter((f) => f !== fmt));
      }
    } else {
      update("formats", [...form.formats, fmt]);
    }
  };

  const estimatedCost =
    densityOptions.find((d) => d.value === form.density)?.cost || 80;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(form);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Name */}
      <div className="space-y-2">
        <Label htmlFor="name">订阅名称</Label>
        <Input
          id="name"
          placeholder="例如：AI行业日报"
          value={form.name}
          onChange={(e) => update("name", e.target.value)}
          required
        />
      </div>

      {/* Domain */}
      <div className="space-y-2">
        <Label>领域选择</Label>
        <div className="grid grid-cols-3 gap-3">
          {["AI", "Crypto", "custom"].map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => update("domain", d)}
              className={cn(
                "rounded-lg border p-3 text-sm font-medium text-center transition-all",
                form.domain === d
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border hover:border-border/80"
              )}
            >
              {d === "custom" ? "自定义" : d}
            </button>
          ))}
        </div>
      </div>

      {/* Custom keywords */}
      {form.domain === "custom" && (
        <div className="space-y-2">
          <Label>自定义关键词</Label>
          <div className="flex gap-2">
            <Input
              placeholder="输入关键词后回车"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addKeyword();
                }
              }}
            />
            <Button type="button" variant="outline" onClick={addKeyword}>
              添加
            </Button>
          </div>
          <div className="flex flex-wrap gap-2 mt-2">
            {form.customKeywords.map((kw) => (
              <Badge key={kw} variant="secondary" className="gap-1">
                {kw}
                <button type="button" onClick={() => removeKeyword(kw)}>
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Density */}
      <div className="space-y-2">
        <Label>信息密度</Label>
        <div className="grid gap-3 sm:grid-cols-3">
          {densityOptions.map((opt) => (
            <Card
              key={opt.value}
              className={cn(
                "cursor-pointer transition-all",
                form.density === opt.value
                  ? "border-primary bg-primary/5"
                  : "border-border/50 hover:border-border"
              )}
              onClick={() => update("density", opt.value)}
            >
              <CardContent className="p-4 text-center">
                <opt.icon className="h-6 w-6 mx-auto mb-2 text-primary" />
                <p className="font-medium text-sm">{opt.label}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {opt.description}
                </p>
                <p className="text-xs text-primary mt-2">~{opt.cost} 积分/次</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Output format */}
      <div className="space-y-2">
        <Label>输出格式（可多选）</Label>
        <div className="flex gap-3">
          {formatOptions.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => toggleFormat(opt.value)}
              className={cn(
                "flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-all",
                form.formats.includes(opt.value)
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:border-border/80"
              )}
            >
              <opt.icon className="h-4 w-4" />
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Frequency */}
      <div className="space-y-2">
        <Label>推送频率</Label>
        <div className="grid grid-cols-3 gap-3">
          {[
            { value: "daily", label: "每日" },
            { value: "weekly", label: "每周" },
            { value: "breaking", label: "仅重大事件" },
          ].map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => update("frequency", opt.value)}
              className={cn(
                "rounded-lg border p-3 text-sm font-medium text-center transition-all",
                form.frequency === opt.value
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border hover:border-border/80"
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Push time */}
      <div className="space-y-2">
        <Label>推送时间桶</Label>
        <Select value={form.pushTime} onValueChange={(v) => update("pushTime", v)}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {timeSlots.map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Estimated cost + submit */}
      <div className="flex items-center justify-between rounded-lg bg-muted/50 p-4">
        <div>
          <p className="text-sm font-medium">预计每次消耗</p>
          <p className="text-xs text-muted-foreground">实际消耗可能因内容量有所浮动</p>
        </div>
        <p className="text-lg font-bold text-primary">~{estimatedCost} 积分</p>
      </div>

      <Button type="submit" size="lg" className="w-full" disabled={loading}>
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {submitLabel}
      </Button>
    </form>
  );
}
