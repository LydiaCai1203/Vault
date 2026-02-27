import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { mockTrades } from "@/lib/mock";
import { cn } from "@/lib/utils";
import { Link } from "wouter";
import { Filter, ShieldAlert } from "lucide-react";

function Pnl({ v }: { v: number }) {
  const isProfit = v >= 0;
  // A股语义：盈利/上涨=红；亏损/下跌=绿
  return (
    <span className={cn("text-mono font-semibold", isProfit ? "text-[#FF4D4F]" : "text-[#27D17F]")}
    >
      {isProfit ? "+" : ""}¥{Math.abs(v).toLocaleString("zh-CN")}
    </span>
  );
}

export default function Trades() {
  return (
    <AppShell
      title="交易"
      right={
        <Button variant="ghost" size="icon" className="rounded-xl">
          <Filter className="size-5 text-primary" />
        </Button>
      }
    >
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-semibold">全部</div>
        <div className="text-[11px] text-muted-foreground">红涨绿跌 · 仅回顾</div>
      </div>

      <div className="space-y-3">
        {mockTrades.map((t) => (
          <Link key={t.id} href={`/trades/${t.id}`}>
            <a>
              <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-semibold">
                        {t.name} <span className="text-muted-foreground font-medium">{t.code}</span>
                      </div>
                      <Badge variant="outline" className="rounded-full border-border/70 text-[10px]">
                        {t.market}
                      </Badge>
                      <Badge
                        variant="secondary"
                        className={cn(
                          "rounded-full text-[10px]",
                          t.direction === "做多" ? "bg-background/40" : "bg-background/20"
                        )}
                      >
                        {t.direction}
                      </Badge>
                    </div>
                    <div className="mt-1 text-[11px] text-muted-foreground">
                      {t.openDate}
                      {t.closeDate ? ` → ${t.closeDate}` : " · 持仓中"}
                      {" · "}
                      {t.status}
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {t.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="rounded-full border-border/70 text-[10px]">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="text-right">
                    <Pnl v={t.pnlCny} />
                    {t.hasStopViolation ? (
                      <div className="mt-2 inline-flex items-center gap-1 text-[11px] text-primary">
                        <ShieldAlert className="size-3.5" />
                        未按止损
                      </div>
                    ) : (
                      <div className="mt-2 text-[11px] text-muted-foreground">—</div>
                    )}
                  </div>
                </div>
              </Card>
            </a>
          </Link>
        ))}
      </div>

      <Separator className="my-5 opacity-60" />
      <div className="text-[11px] text-muted-foreground">
        提示：筛选/导入/批量记录将于后续接入。
      </div>
    </AppShell>
  );
}
