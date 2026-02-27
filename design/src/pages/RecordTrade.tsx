import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Mic, Sparkles } from "lucide-react";

export default function RecordTrade() {
  return (
    <AppShell
      title="记一笔"
      right={
        <Button variant="ghost" size="icon" className="rounded-xl" onClick={() => toast.message("语音输入后续接入")}
        >
          <Mic className="size-5 text-primary" />
        </Button>
      }
    >
      <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold">自然语言记录</div>
          <div className="inline-flex items-center gap-1 text-[11px] text-primary">
            <Sparkles className="size-3.5" />
            解析
          </div>
        </div>
        <div className="mt-2 text-[11px] text-muted-foreground">
          例如：今天下午买入宁德时代做多，入场 165.2，止损 158，仓位 20%，理由是突破回踩。
        </div>
        <Textarea
          className="mt-3 min-h-28 bg-background/30 rounded-xl"
          placeholder="用一句话描述交易…（支持语音）"
        />
      </Card>

      <Card className="mt-4 bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="text-sm font-semibold">已解析字段</div>
        <div className="mt-2 flex flex-wrap gap-2">
          {[
            "品种 宁德时代 300750",
            "方向 做多",
            "入场 165.2",
            "止损 158.0",
            "仓位 20%",
            "情绪 焦虑",
          ].map((x) => (
            <Badge key={x} variant="outline" className="rounded-full border-border/70 text-[11px]">
              {x}
            </Badge>
          ))}
          <Badge className="rounded-full bg-primary text-primary-foreground text-[11px]">未按止损</Badge>
        </div>
      </Card>

      <Card className="mt-4 bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="text-[13px] leading-relaxed text-muted-foreground">
          补一句 <span className="text-foreground font-medium">进场理由</span>，复盘会更准确。
        </div>
      </Card>

      <div className="mt-5 grid grid-cols-2 gap-2">
        <Button className="rounded-xl" onClick={() => toast.success("已保存（演示占位）")}
        >
          保存记录
        </Button>
        <Button variant="outline" className="rounded-xl" onClick={() => toast.message("补全表单后续接入")}
        >
          继续补全
        </Button>
      </div>

      <div className="mt-3 text-[11px] text-muted-foreground">注：本页为前端演示，后续接入真实解析与校验。</div>
    </AppShell>
  );
}
