"use client";

import { Users, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/components/ui/cn";

const domainColors: Record<string, string> = {
  AI: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  Crypto: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  general: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
};

interface TemplateCardProps {
  template: {
    id: string;
    name: string;
    domain: string;
    description: string;
    adoptionCount: number;
    qualityScore: number;
    creatorName: string;
  };
  onClick: (id: string) => void;
}

export function TemplateCard({ template, onClick }: TemplateCardProps) {
  const colorClass = domainColors[template.domain] || domainColors.general;

  return (
    <Card
      className="border-border/50 cursor-pointer hover:border-border hover:shadow-md transition-all duration-200 group"
      onClick={() => onClick(template.id)}
    >
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <Badge variant="outline" className={cn("text-[11px]", colorClass)}>
            {template.domain}
          </Badge>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Users className="h-3.5 w-3.5" />
            <span>{template.adoptionCount}</span>
          </div>
        </div>

        <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">
          {template.name}
        </h3>

        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
          {template.description}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            by {template.creatorName}
          </span>
          <div className="flex items-center gap-0.5">
            {Array.from({ length: 5 }).map((_, i) => (
              <Star
                key={i}
                className={cn(
                  "h-3.5 w-3.5",
                  i < Math.round(template.qualityScore)
                    ? "fill-amber-400 text-amber-400"
                    : "text-muted-foreground/30"
                )}
              />
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
