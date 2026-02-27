import { cn } from "@/lib/utils";
import { Link, useLocation } from "wouter";
import { BarChart3, BookOpen, Home, Plus, User } from "lucide-react";

const tabs = [
  { href: "/dashboard", label: "总览", icon: Home },
  { href: "/trades", label: "交易", icon: BarChart3 },
  { href: "/record", label: "记一笔", icon: Plus },
  { href: "/reviews", label: "复盘", icon: BookOpen },
  { href: "/profile", label: "我的", icon: User },
] as const;

export default function AppShell({
  title,
  right,
  children,
}: {
  title?: string;
  right?: React.ReactNode;
  children: React.ReactNode;
}) {
  const [loc] = useLocation();

  return (
    <div className="min-h-screen bg-background text-foreground grain">
      <div className="mx-auto w-full max-w-[460px] min-h-screen">
        {/* Top Bar */}
        <header className="sticky top-0 z-30 bg-background/85 backdrop-blur border-b border-border">
          <div className="px-4 h-14 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="size-8 rounded-xl bg-card hairline grid place-items-center">
                <div className="size-2 rounded-full bg-primary" />
              </div>
              <div className="leading-tight">
                <div className="text-sm font-semibold tracking-wide">{title ?? "Vault"}</div>
                <div className="text-[11px] text-muted-foreground">大A · 纪律复盘 · 不做预测</div>
              </div>
            </div>
            <div>{right}</div>
          </div>
        </header>

        {/* Content */}
        <main className="px-4 pt-4 pb-24">{children}</main>

        {/* Bottom Tab */}
        <nav className="fixed bottom-0 left-0 right-0 z-40">
          <div className="mx-auto w-full max-w-[460px]">
            <div className="bg-background/90 backdrop-blur border-t border-border">
              <div className="px-4 h-[72px] grid grid-cols-5 items-center relative">
                {tabs.map((t) => {
                  const active = loc === t.href;
                  const Icon = t.icon;

                  // Center "Record" tab gets slightly stronger emphasis but stays aligned.
                  const isRecord = t.href === "/record";

                  return (
                    <Link key={t.href} href={t.href}>
                      <a
                        className={cn(
                          "col-span-1 flex flex-col items-center justify-center gap-1",
                          active ? "text-foreground" : "text-muted-foreground"
                        )}
                      >
                        <div
                          className={cn(
                            "size-10 rounded-2xl grid place-items-center",
                            isRecord ? "bg-background/30 hairline" : "bg-transparent",
                            active && isRecord && "bg-primary text-primary-foreground glow-yellow"
                          )}
                        >
                          <Icon className={cn("size-5", active ? (isRecord ? "text-primary-foreground" : "text-primary") : "")} />
                        </div>
                        <span
                          className={cn(
                            "text-[11px]",
                            active ? "text-foreground" : "text-muted-foreground",
                            active && isRecord && "text-primary"
                          )}
                        >
                          {t.label}
                        </span>
                        <span
                          className={cn(
                            "mt-0.5 h-[2px] w-8 rounded-full",
                            active ? "bg-primary" : "bg-transparent"
                          )}
                        />
                      </a>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        </nav>
      </div>
    </div>
  );
}
