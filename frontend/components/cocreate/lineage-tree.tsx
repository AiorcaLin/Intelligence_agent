"use client";

import { GitBranch } from "lucide-react";
import { cn } from "@/components/ui/cn";

interface LineageNode {
  id: string;
  name: string;
  creatorName: string;
  children?: LineageNode[];
  isCurrent?: boolean;
}

interface LineageTreeProps {
  root: LineageNode | null;
}

function TreeNode({ node, depth = 0 }: { node: LineageNode; depth?: number }) {
  return (
    <div className={cn("relative", depth > 0 && "ml-6")}>
      {depth > 0 && (
        <div className="absolute left-[-16px] top-0 h-full w-px bg-border" />
      )}
      {depth > 0 && (
        <div className="absolute left-[-16px] top-3.5 w-4 h-px bg-border" />
      )}
      <div
        className={cn(
          "flex items-center gap-2 rounded-md px-3 py-2 text-sm",
          node.isCurrent
            ? "bg-primary/10 border border-primary/20"
            : "bg-muted/50"
        )}
      >
        <GitBranch className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
        <div>
          <span className="font-medium">{node.name}</span>
          <span className="text-xs text-muted-foreground ml-2">
            by {node.creatorName}
          </span>
        </div>
      </div>
      {node.children && node.children.length > 0 && (
        <div className="mt-2 space-y-2">
          {node.children.map((child) => (
            <TreeNode key={child.id} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export function LineageTree({ root }: LineageTreeProps) {
  if (!root) {
    return (
      <div className="text-sm text-muted-foreground text-center py-8">
        暂无族谱数据
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <TreeNode node={root} />
    </div>
  );
}
