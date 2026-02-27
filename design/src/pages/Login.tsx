import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Link } from "wouter";

export default function Login() {
  return (
    <div className="min-h-screen bg-background text-foreground grain">
      <div className="mx-auto w-full max-w-[460px] min-h-screen px-6 py-10 flex flex-col">
        <div className="flex-1 flex flex-col justify-center">
          <div className="mb-8">
            <div className="text-3xl font-semibold tracking-wide">Vault</div>
            <div className="mt-2 text-sm text-muted-foreground">交易日志与复盘（不做预测）</div>
          </div>

          <Card className="bg-card text-card-foreground border-border/70 p-4 hairline">
            <div className="space-y-3">
              <div>
                <div className="text-xs text-muted-foreground mb-1">手机号 / 邮箱</div>
                <Input placeholder="例如：acaicai1203@gmail.com" className="bg-background/40" />
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">密码</div>
                <Input type="password" placeholder="••••••••" className="bg-background/40" />
              </div>
              <Button
                className="w-full rounded-xl"
                onClick={() => toast.success("已进入演示模式（前端占位）")}
              >
                登录
              </Button>
              <Button
                variant="outline"
                className="w-full rounded-xl"
                onClick={() => toast.message("注册流程后续接入")}
              >
                注册
              </Button>
            </div>
          </Card>

          <div className="mt-4 text-[11px] text-muted-foreground leading-relaxed">
            仅用于记录与复盘，不提供买卖建议。所有内容为你的行为改进服务。
          </div>

          <div className="mt-6">
            <Link href="/dashboard">
              <a className="text-sm text-primary underline underline-offset-4">跳过，进入演示</a>
            </Link>
          </div>
        </div>

        <div className="pb-6 text-[11px] text-muted-foreground">© Vault · A股专用语义：红涨绿跌</div>
      </div>
    </div>
  );
}
