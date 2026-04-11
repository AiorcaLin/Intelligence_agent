"use client";

import { useState } from "react";
import { GitFork, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface ForkDialogProps {
  templateName: string;
  onFork: (name: string, description: string) => Promise<void>;
}

export function ForkDialog({ templateName, onFork }: ForkDialogProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState(`${templateName} (分支)`);
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFork = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      await onFork(name, description);
      setOpen(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <GitFork className="h-4 w-4" />
          分支创建
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>分支创建配方</DialogTitle>
          <DialogDescription>
            基于「{templateName}」创建新的分支版本，你可以自由修改和优化。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="fork-name">配方名称</Label>
            <Input
              id="fork-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="为你的分支命名"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="fork-desc">修改说明（可选）</Label>
            <textarea
              id="fork-desc"
              className="w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
              placeholder="描述你计划做的改进..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            取消
          </Button>
          <Button onClick={handleFork} disabled={loading || !name.trim()}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            创建分支
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
