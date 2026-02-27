import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { mockReviews } from "@/lib/mock";
import { Link } from "wouter";
import { Filter } from "lucide-react";

export default function Reviews() {
  return (
    <AppShell
      title="复盘"
      right={
        <Button variant="ghost" size="icon" className="rounded-xl">
          <Filter className="size-5 text-primary" />
        </Button>
      }
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="text-sm font-semibold">报告</div>
        <div className="text-[11px] text-muted-foreground">周度 / 月度 / 单笔</div>
      </div>

      <div className="space-y-3">
        {mockReviews.map((r) => (
          <Link key={r.id} href={`/reviews/${r.id}`}>
            <a>
              <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-semibold">{r.title}</div>
                      <Badge variant="outline" className="rounded-full border-border/70 text-[10px]">{r.type}</Badge>
                      <Badge className="rounded-full bg-primary text-primary-foreground text-[10px]">大A</Badge>
                    </div>
                    <div className="mt-1 text-[11px] text-muted-foreground">
                      {r.range} · 样本 {r.sampleCount} 笔
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[11px] text-muted-foreground">总览</div>
                    <div className="mt-1 text-mono font-semibold">{Math.round(r.winRate * 100)}%</div>
                    <div className="mt-1 text-[11px] text-primary">查看</div>
                  </div>
                </div>
              </Card>
            </a>
          </Link>
        ))}
      </div>

      <div className="mt-5 text-[11px] text-muted-foreground">提示：自定义复盘与对比后续接入。</div>
    </AppShell>
  );
}
