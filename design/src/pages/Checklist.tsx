import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { mockReviews } from "@/lib/mock";
import { toast } from "sonner";

export default function Checklist() {
  // Demo: use latest weekly review todo as checklist source
  const r = mockReviews[0];

  return (
    <AppShell title="开仓前清单">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold">开仓前清单</div>
          <div className="text-[11px] text-muted-foreground">来自复盘行动清单（示例）</div>
        </div>
        <Badge className="rounded-full bg-primary text-primary-foreground text-[10px]">大A</Badge>
      </div>

      <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="text-sm font-semibold">本周重点（{r.range}）</div>
        <div className="mt-2 text-[11px] text-muted-foreground">勾选完成后再开仓，强化纪律。</div>

        <div className="mt-4 space-y-3">
          {r.todo.map((t) => (
            <label key={t} className="flex items-start gap-3">
              <Checkbox className="mt-0.5" />
              <div className="text-[13px] leading-relaxed text-muted-foreground">{t}</div>
            </label>
          ))}
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2">
          <Button className="rounded-xl" onClick={() => toast.success("已保存（演示占位）")}>保存状态</Button>
          <Button variant="outline" className="rounded-xl" onClick={() => toast.message("将支持按组合/策略生成")}>生成新清单</Button>
        </div>
      </Card>

      <div className="mt-3 text-[11px] text-muted-foreground">注：当前为前端演示，占位数据来自周度复盘。</div>
    </AppShell>
  );
}
