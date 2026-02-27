import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { mockReviews } from "@/lib/mock";
import { ArrowLeft, Share2 } from "lucide-react";
import { useLocation } from "wouter";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";

function heatColor(v: number) {
  // 0-4 → background intensity (yellow in OKX style)
  if (v <= 0) return "bg-background/25";
  if (v === 1) return "bg-primary/15";
  if (v === 2) return "bg-primary/25";
  if (v === 3) return "bg-primary/35";
  return "bg-primary/45";
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: "up" | "down" }) {
  return (
    <div className="flex flex-col">
      <div className="text-[11px] text-muted-foreground">{label}</div>
      <div
        className={cn(
          "mt-1 text-mono font-semibold",
          tone === "up" && "text-[#FF4D4F]",
          tone === "down" && "text-[#27D17F]"
        )}
      >
        {value}
      </div>
    </div>
  );
}

export default function ReviewDetail({ id }: { id: string }) {
  const r = mockReviews.find((x) => x.id === id);
  const [, setLoc] = useLocation();

  if (!r) {
    return (
      <AppShell title="复盘详情">
        <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">未找到报告。</Card>
      </AppShell>
    );
  }

  const radarData = [
    { k: "Mind", v: r.scores.mind },
    { k: "Method", v: r.scores.method },
    { k: "Money", v: r.scores.money },
  ];

  return (
    <AppShell
      title="周度复盘"
      right={
        <Button variant="ghost" size="icon" className="rounded-xl" onClick={() => setLoc("/reviews")}
        >
          <Share2 className="size-5" />
        </Button>
      }
    >
      <div className="flex items-center gap-2 mb-3">
        <Button variant="ghost" size="icon" className="rounded-xl" onClick={() => setLoc("/reviews")}
        >
          <ArrowLeft className="size-5" />
        </Button>
        <div>
          <div className="text-sm font-semibold">周度复盘 {r.range}</div>
          <div className="text-[11px] text-muted-foreground">样本 {r.sampleCount} 笔 · 大A</div>
        </div>
      </div>

      <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold">摘要</div>
          <Badge className="rounded-full bg-primary text-primary-foreground text-[10px]">仅复盘不预测</Badge>
        </div>
        <div className="mt-3 grid grid-cols-3 gap-3">
          <Metric label="胜率" value={`${Math.round(r.winRate * 100)}%`} />
          <Metric label="盈亏比" value={r.rr.toFixed(1)} />
          <Metric label="期望值" value={`${r.expectancy >= 0 ? "+" : ""}${r.expectancy.toFixed(2)}`} tone={r.expectancy >= 0 ? "up" : "down"} />
        </div>
      </Card>

      <Card className="mt-4 bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold">3M 能力图</div>
            <div className="text-[11px] text-muted-foreground">Mind / Method / Money（0-5）</div>
          </div>
          <Badge variant="outline" className="rounded-full border-border/70 text-[10px]">本周</Badge>
        </div>

        <div className="mt-4 h-44">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData} outerRadius="78%">
              <PolarGrid stroke="rgba(255,255,255,0.10)" />
              <PolarAngleAxis dataKey="k" tick={{ fill: "#FFFFFF", fontSize: 12 }} />
              <Radar
                dataKey="v"
                stroke="#FFD12E"
                fill="rgba(255, 209, 46, 0.18)"
                strokeWidth={2}
                dot={{ r: 3, fill: "#FFD12E" }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-3 grid grid-cols-3 gap-2">
          <div className="rounded-xl bg-background/30 hairline p-2">
            <div className="text-[11px] text-muted-foreground">Mind</div>
            <div className="text-mono font-semibold mt-0.5">{r.scores.mind.toFixed(1)}</div>
          </div>
          <div className="rounded-xl bg-background/30 hairline p-2">
            <div className="text-[11px] text-muted-foreground">Method</div>
            <div className="text-mono font-semibold mt-0.5">{r.scores.method.toFixed(1)}</div>
          </div>
          <div className="rounded-xl bg-background/30 hairline p-2">
            <div className="text-[11px] text-muted-foreground">Money</div>
            <div className="text-mono font-semibold mt-0.5">{r.scores.money.toFixed(1)}</div>
          </div>
        </div>

        <div className="mt-3 space-y-2 text-[13px] text-muted-foreground">
          <div><span className="text-primary">•</span> Mind：FOMO 增加，盘中情绪波动更大</div>
          <div><span className="text-primary">•</span> Method：信号一致性 76%，但追涨频率上升</div>
          <div><span className="text-primary">•</span> Money：止损执行率 67%，两次违规</div>
        </div>
      </Card>

      <Card className="mt-4 bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold">情绪与纪律热力图</div>
            <div className="text-[11px] text-muted-foreground">不同交易时段的错误分布（0-4 强度）</div>
          </div>
          <Badge variant="outline" className="rounded-full border-border/70 text-[10px]">本周</Badge>
        </div>

        <div className="mt-3 overflow-x-auto">
          <div className="min-w-[520px]">
            <div className="grid" style={{ gridTemplateColumns: `120px repeat(${r.heatmap.cols.length}, minmax(72px, 1fr))` }}>
              <div className="px-2 py-2 text-[11px] text-muted-foreground">时段</div>
              {r.heatmap.cols.map((c) => (
                <div key={c} className="px-2 py-2 text-[11px] text-muted-foreground">
                  {c}
                </div>
              ))}

              {r.heatmap.rows.map((row, i) => (
                <>
                  <div key={row} className="px-2 py-2 text-[11px] text-muted-foreground">
                    {row}
                  </div>
                  {r.heatmap.cols.map((col, j) => {
                    const v = r.heatmap.values[i]?.[j] ?? 0;
                    return (
                      <div key={`${row}-${col}`} className="px-2 py-2">
                        <div
                          className={cn(
                            "h-9 rounded-lg hairline flex items-center justify-center text-mono text-[12px]",
                            heatColor(v),
                            v >= 3 ? "text-foreground" : "text-muted-foreground"
                          )}
                          title={`${row} · ${col}：${v}`}
                        >
                          {v === 0 ? "" : v}
                        </div>
                      </div>
                    );
                  })}
                </>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-3 flex items-center justify-between text-[11px] text-muted-foreground">
          <span>越亮表示该类错误更集中</span>
          <span className="text-primary">重点：收盘前纪律风险</span>
        </div>
        {r.heatmap.notes ? <div className="mt-2 text-[12px] text-muted-foreground">{r.heatmap.notes}</div> : null}
      </Card>

      <Separator className="my-5 opacity-60" />

      <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="text-sm font-semibold">重复性错误</div>
        <div className="mt-3 space-y-2">
          {r.mistakes.map((m) => (
            <div key={m} className="flex items-start gap-2 text-[13px] text-muted-foreground">
              <span className="mt-1 size-1.5 rounded-full bg-primary" />
              <span className="leading-relaxed">{m}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card className="mt-4 bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="text-sm font-semibold">下周改进清单</div>
        <div className="mt-3 space-y-2">
          {r.todo.map((t) => (
            <div key={t} className="flex items-start gap-2 text-[13px] text-muted-foreground">
              <span className="mt-1 size-1.5 rounded-full bg-primary" />
              <span className="leading-relaxed">{t}</span>
            </div>
          ))}
        </div>
        <a href="#/checklist">
          <Button className="mt-4 w-full rounded-xl">加入开仓前清单</Button>
        </a>
      </Card>

      <div className="mt-3 text-[11px] text-muted-foreground">注：此为前端演示占位，后续接入真实分析结果。</div>
    </AppShell>
  );
}
