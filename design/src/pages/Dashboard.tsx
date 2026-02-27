import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Bell, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

function MetricCard({ title, value, hint, tone }: { title: string; value: string; hint?: string; tone?: "yellow" }) {
  return (
    <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
      <div className="text-[11px] text-muted-foreground">{title}</div>
      <div className={cn("mt-2 text-xl font-semibold tracking-tight text-mono", tone === "yellow" && "text-primary")}>
        {value}
      </div>
      {hint ? <div className="mt-1 text-[11px] text-muted-foreground">{hint}</div> : null}
    </Card>
  );
}

export default function Dashboard() {
  return (
    <AppShell
      title="Vault"
      right={
        <Button variant="ghost" size="icon" className="rounded-xl">
          <div className="relative">
            <Bell className="size-5" />
            <span className="absolute -right-0.5 -top-0.5 size-2 rounded-full bg-primary" />
          </div>
        </Button>
      }
    >
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold">本周概览</div>
          <div className="text-[11px] text-muted-foreground">组合：大A 纪律账户 · 02/19-02/25</div>
        </div>
        <Badge variant="outline" className="rounded-full border-border/70">沪深A</Badge>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <MetricCard title="交易数" value="12" hint="样本" />
        <MetricCard title="胜率" value="58%" hint="本周" />
        <MetricCard title="执行评分" value="4.1/5" hint="不是盈亏" />
        <MetricCard title="纪律违规" value="3" hint="需关注" tone="yellow" />
      </div>

      <Card className="mt-4 bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold">权益曲线（¥）</div>
            <div className="text-[11px] text-muted-foreground">仅展示历史结果，不做预测</div>
          </div>
          <div className="text-right">
            <div className="text-[11px] text-muted-foreground">本周收益</div>
            <div className="text-sm font-semibold text-[#FF4D4F] text-mono">+2.8%</div>
          </div>
        </div>
        <div className="mt-3 h-16 rounded-xl bg-background/30 hairline" />
        <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
          <span>最大回撤</span>
          <span className="text-[#27D17F] text-mono">-3.2%</span>
        </div>
      </Card>

      <Card className="mt-4 bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-start gap-3">
          <div className="mt-1 h-10 w-1.5 rounded-full bg-primary" />
          <div className="flex-1">
            <div className="flex items-center justify-between">
            <div className="text-sm font-semibold">提醒</div>
            <a href="#/checklist" className="text-[11px] text-primary underline underline-offset-4">开仓前清单</a>
          </div>
            <div className="mt-1 text-[13px] leading-relaxed text-muted-foreground">
              本周 <span className="text-primary font-medium">2 次</span> 未按止损执行。建议查看涉及交易，生成下周改进清单。
            </div>
            <Button variant="outline" className="mt-3 rounded-xl">
              查看涉及交易
              <ChevronRight className="ml-1 size-4" />
            </Button>
          </div>
        </div>
      </Card>

    </AppShell>
  );
}
