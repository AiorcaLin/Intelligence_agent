"use client";

import { Star } from "lucide-react";
import { cn } from "@/components/ui/cn";

interface ImportanceBtnProps {
  isImportant: boolean;
  onToggle: () => void;
}

export function ImportanceBtn({ isImportant, onToggle }: ImportanceBtnProps) {
  return (
    <button
      onClick={onToggle}
      className={cn(
        "inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-all duration-200 hover:scale-110",
        isImportant
          ? "text-amber-400 bg-amber-400/10"
          : "text-muted-foreground hover:text-amber-400 hover:bg-amber-400/10"
      )}
    >
      <Star
        className={cn(
          "h-4 w-4 transition-all duration-200",
          isImportant && "fill-amber-400"
        )}
      />
      <span>{isImportant ? "已标记" : "标记为重要"}</span>
    </button>
  );
}
