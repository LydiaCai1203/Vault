import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { mockTrades } from "@/lib/mock";
import { cn } from "@/lib/utils";
import { ArrowLeft, Share2 } from "lucide-react";
import { Link, useLocation } from "wouter";

export default function TradeDetail({ id }: { id: string }) {
  const t = mockTrades.find((x) => x.id === id);
  const [, setLoc] = useLocation();

  if (!t) {
    return (
      <AppShell title="交易详情">
        <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">未找到交易。</Card>
      </AppShell>
    );
  }

  const isProfit = t.pnlCny >= 0;

  return (
    <AppShell
      title="交易详情"
      right={
        <Button variant="ghost" size="icon" className="rounded-xl" onClick={() => setLoc("/trades")}
        >
          <Share2 className="size-5" />
        </Button>
      }
    >
      <div className="flex items-center gap-2 mb-3">
        <Button variant="ghost" size="icon" className="rounded-xl" onClick={() => setLoc("/trades")}
        >
          <ArrowLeft className="size-5" />
        </Button>
        <div>
          <div className="text-sm font-semibold">
            {t.name} <span className="text-muted-foreground font-medium">{t.code}</span>
          </div>
          <div className="text-[11px] text-muted-foreground">{t.market} · {t.status}</div>
        </div>
      </div>

      <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-[11px] text-muted-foreground">盈亏（¥）</div>
            <div className={cn("mt-1 text-2xl font-semibold text-mono", isProfit ? "text-[#FF4D4F]" : "text-[#27D17F]")}
            >
              {isProfit ? "+" : "-"}¥{Math.abs(t.pnlCny).toLocaleString("zh-CN")}
            </div>
            <div className="mt-2 flex flex-wrap gap-1">
              <Badge variant="outline" className="rounded-full border-border/70 text-[10px]">{t.direction}</Badge>
              {t.tags.map((tag) => (
                <Badge key={tag} variant="outline" className="rounded-full border-border/70 text-[10px]">{tag}</Badge>
              ))}
              {t.hasStopViolation ? (
                <Badge className="rounded-full bg-primary text-primary-foreground text-[10px]">未按止损</Badge>
              ) : null}
            </div>
          </div>
          <div className="text-right text-[11px] text-muted-foreground">
            <div>开仓 {t.openDate}</div>
            <div>平仓 {t.closeDate ?? "—"}</div>
          </div>
        </div>
      </Card>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
          <div className="text-[11px] text-muted-foreground">入场价</div>
          <div className="mt-1 text-mono font-semibold">165.20</div>
        </Card>
        <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
          <div className="text-[11px] text-muted-foreground">出场价</div>
          <div className="mt-1 text-mono font-semibold">171.00</div>
        </Card>
        <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
          <div className="text-[11px] text-muted-foreground">仓位</div>
          <div className="mt-1 text-mono font-semibold">20%</div>
        </Card>
        <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
          <div className="text-[11px] text-muted-foreground">止损</div>
          <div className="mt-1 text-mono font-semibold">158.00</div>
        </Card>
      </div>

      <Separator className="my-5 opacity-60" />

      <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="text-sm font-semibold">计划 vs 执行</div>
        <div className="mt-2 text-[13px] leading-relaxed text-muted-foreground">
          计划：突破回踩确认后入场，止损固定。
          <br />
          执行：盘中波动加大，止损执行犹豫，出现一次违规。
        </div>
      </Card>

      <div className="mt-4">
        <Button className="w-full rounded-xl">补充记录</Button>
      </div>

      <div className="mt-3 text-[11px] text-muted-foreground">
        注：价格/计划文本为前端演示占位，后续接入真实记录。
      </div>
    </AppShell>
  );
}
