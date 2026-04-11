"use client";

import { FileText, Headphones, Video, ToggleLeft, ToggleRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/components/ui/cn";
import type { Subscription } from "@/lib/store";

const domainColors: Record<string, string> = {
  AI: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  Crypto: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  custom: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
};

const densityLabels: Record<string, string> = {
  brief: "速览",
  standard: "标准",
  research: "研究级",
};

const frequencyLabels: Record<string, string> = {
  daily: "每日",
  weekly: "每周",
  breaking: "仅重大事件",
};

const formatIcons: Record<string, React.ElementType> = {
  text: FileText,
  audio: Headphones,
  video: Video,
};

interface SubCardProps {
  subscription: Subscription;
  onToggle: (id: string) => void;
  onClick: (id: string) => void;
}

export function SubCard({ subscription, onToggle, onClick }: SubCardProps) {
  const colorClass = domainColors[subscription.domain] || domainColors.custom;

  return (
    <Card
      className={cn(
        "border-border/50 cursor-pointer hover:border-border hover:shadow-md transition-all duration-200",
        !subscription.isActive && "opacity-60"
      )}
      onClick={() => onClick(subscription.id)}
    >
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold truncate">{subscription.name}</h3>
            <div className="flex items-center gap-2 mt-1.5">
              <Badge variant="outline" className={cn("text-[11px]", colorClass)}>
                {subscription.domain}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {densityLabels[subscription.density] || subscription.density}
              </span>
            </div>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggle(subscription.id);
            }}
            className="shrink-0"
          >
            {subscription.isActive ? (
              <ToggleRight className="h-7 w-7 text-primary" />
            ) : (
              <ToggleLeft className="h-7 w-7 text-muted-foreground" />
            )}
          </button>
        </div>

        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>{frequencyLabels[subscription.frequency] || subscription.frequency}</span>
          <span>·</span>
          <span>{subscription.pushTime}</span>
          <span>·</span>
          <div className="flex items-center gap-1">
            {subscription.formats.map((fmt) => {
              const Icon = formatIcons[fmt];
              return Icon ? <Icon key={fmt} className="h-3.5 w-3.5" /> : null;
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
