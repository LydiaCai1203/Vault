import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronRight, Download, Shield, UserCircle2 } from "lucide-react";
import { toast } from "sonner";

function MenuItem({
  icon,
  title,
  desc,
  onClick,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
  onClick: () => void;
}) {
  return (
    <button onClick={onClick} className="w-full text-left">
      <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-center gap-3">
          <div className="size-10 rounded-xl bg-background/30 hairline grid place-items-center text-primary">{icon}</div>
          <div className="flex-1">
            <div className="text-sm font-semibold">{title}</div>
            <div className="mt-0.5 text-[11px] text-muted-foreground">{desc}</div>
          </div>
          <ChevronRight className="size-4 text-muted-foreground" />
        </div>
      </Card>
    </button>
  );
}

export default function Profile() {
  return (
    <AppShell title="我的">
      <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
        <div className="flex items-center gap-3">
          <div className="size-12 rounded-2xl bg-background/30 hairline grid place-items-center">
            <UserCircle2 className="size-7 text-primary" />
          </div>
          <div className="flex-1">
            <div className="text-sm font-semibold">cai cai</div>
            <div className="mt-1 flex flex-wrap gap-2">
              <Badge className="rounded-full bg-primary text-primary-foreground text-[10px]">大A 纪律账户</Badge>
              <Badge variant="outline" className="rounded-full border-border/70 text-[10px]">红涨绿跌</Badge>
              <Badge variant="outline" className="rounded-full border-border/70 text-[10px]">仅复盘不预测</Badge>
            </div>
          </div>
        </div>
      </Card>

      <div className="mt-4 space-y-3">
        <MenuItem
          icon={<Shield className="size-5" />}
          title="风险规则"
          desc="单笔最大风险、最大日亏、最大仓位、最大持仓数"
          onClick={() => toast.message("风险规则配置后续接入")}
        />
        <MenuItem
          icon={<Download className="size-5" />}
          title="数据导入 / 导出"
          desc="CSV/Excel 导入、备份、导出复盘报告"
          onClick={() => toast.message("导入导出后续接入")}
        />
        <MenuItem
          icon={<Shield className="size-5" />}
          title="隐私与声明"
          desc="只做记录与复盘，不触碰真实交易"
          onClick={() => toast.message("声明页后续接入")}
        />
      </div>

      <div className="mt-5">
        <Button variant="outline" className="w-full rounded-xl" onClick={() => toast.message("登出后续接入")}
        >
          退出登录
        </Button>
      </div>

      <div className="mt-3 text-[11px] text-muted-foreground">
        说明：当前为前端可交互原型（占位数据）。后续将对接 FastAPI。
      </div>
    </AppShell>
  );
}
