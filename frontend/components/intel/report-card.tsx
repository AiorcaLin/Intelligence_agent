"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/components/ui/cn";
import { ImportanceBtn } from "@/components/intel/importance-btn";
import { HistoryTimeline } from "@/components/intel/history-timeline";
import type { ReportItem } from "@/lib/store";

const domainColors: Record<string, string> = {
  AI: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  Crypto: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  Finance: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  Tech: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  default: "bg-gray-500/10 text-gray-400 border-gray-500/20",
};

function getImportanceColor(score: number) {
  if (score > 8) return "bg-red-500/10 text-red-400 border-red-500/20";
  if (score >= 6) return "bg-amber-500/10 text-amber-400 border-amber-500/20";
  return "bg-green-500/10 text-green-400 border-green-500/20";
}

interface ReportCardProps {
  item: ReportItem;
  onToggleImportant?: (id: string) => void;
}

export function ReportCard({ item, onToggleImportant }: ReportCardProps) {
  const [expanded, setExpanded] = useState(false);
  const domainColor = domainColors[item.domain] || domainColors.default;
  const importanceColor = getImportanceColor(item.importanceScore);

  return (
    <Card className="group border-border/50 hover:border-border transition-all duration-200">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {/* Tags row */}
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className={cn("text-[11px]", domainColor)}>
                {item.domain}
              </Badge>
              <Badge variant="outline" className={cn("text-[11px]", importanceColor)}>
                重要性 {item.importanceScore}/10
              </Badge>
            </div>

            {/* Title */}
            <h3 className="font-semibold text-base mb-2 leading-snug">
              {item.title}
            </h3>

            {/* Summary */}
            <p className="text-sm text-muted-foreground leading-relaxed mb-3">
              {item.summary}
            </p>

            {/* Sources */}
            {item.sources && item.sources.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {item.sources.map((source, i) => (
                  <a
                    key={i}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-primary/80 hover:text-primary transition-colors"
                  >
                    <ExternalLink className="h-3 w-3" />
                    {source.name}
                  </a>
                ))}
              </div>
            )}

            {/* Action items expandable */}
            {item.actionItems && item.actionItems.length > 0 && (
              <div>
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  行动建议 ({item.actionItems.length})
                  {expanded ? (
                    <ChevronUp className="h-3.5 w-3.5" />
                  ) : (
                    <ChevronDown className="h-3.5 w-3.5" />
                  )}
                </button>
                {expanded && (
                  <ul className="mt-2 space-y-1.5 animate-fade-in">
                    {item.actionItems.map((action, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm text-muted-foreground"
                      >
                        <span className="mt-1 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                        {action}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* History timeline */}
            <HistoryTimeline items={item.historyItems || []} />
          </div>

          {/* Star button */}
          <div className="shrink-0 pt-1">
            <ImportanceBtn
              isImportant={item.isImportant}
              onToggle={() => onToggleImportant?.(item.id)}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
