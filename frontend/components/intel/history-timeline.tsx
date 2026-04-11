"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Clock } from "lucide-react";
import { cn } from "@/components/ui/cn";

interface HistoryItem {
  date: string;
  title: string;
  summary: string;
}

interface HistoryTimelineProps {
  items: HistoryItem[];
}

export function HistoryTimeline({ items }: HistoryTimelineProps) {
  const [expanded, setExpanded] = useState(false);

  if (!items || items.length === 0) return null;

  return (
    <div className="mt-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <Clock className="h-3.5 w-3.5" />
        <span>查看历史脉络 ({items.length})</span>
        {expanded ? (
          <ChevronUp className="h-3.5 w-3.5" />
        ) : (
          <ChevronDown className="h-3.5 w-3.5" />
        )}
      </button>

      {expanded && (
        <div className="mt-3 ml-2 border-l-2 border-border pl-4 space-y-3 animate-fade-in">
          {items.map((item, i) => (
            <div key={i} className="relative">
              <div className="absolute -left-[21px] top-1.5 h-2 w-2 rounded-full bg-primary" />
              <p className="text-xs text-muted-foreground">{item.date}</p>
              <p className="text-sm font-medium mt-0.5">{item.title}</p>
              <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                {item.summary}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
