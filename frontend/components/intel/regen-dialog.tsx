"use client";

import { useState } from "react";
import { RefreshCw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface RegenDialogProps {
  onConfirm: (feedback: string) => Promise<void>;
  estimatedCost?: number;
}

export function RegenDialog({ onConfirm, estimatedCost = 50 }: RegenDialogProps) {
  const [open, setOpen] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm(feedback);
      setOpen(false);
      setFeedback("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <button className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-1.5">
          <RefreshCw className="h-3.5 w-3.5" />
          对今日情报不满意？点击重新生成
        </button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>重新生成情报</DialogTitle>
          <DialogDescription>
            请告诉我们哪里需要改进，我们会重新为你生成今日情报。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <textarea
            className="w-full min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
            placeholder="例如：希望更多关注大模型落地应用的消息，减少融资新闻..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
          <div className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2">
            <span className="text-sm text-muted-foreground">预计消耗积分</span>
            <span className="text-sm font-semibold text-primary">
              {estimatedCost} 积分
            </span>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            取消
          </Button>
          <Button onClick={handleConfirm} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            确认重新生成
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
