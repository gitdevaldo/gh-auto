import { Link, useLocation } from "wouter";
import { useHealthCheck } from "@workspace/api-client-react";
import { Activity, GitMerge, Settings, PlaySquare, Webhook, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const { data: health } = useHealthCheck();

  const navItems = [
    { href: "/", label: "Dashboard", icon: Activity },
    { href: "/automations", label: "Automations", icon: Zap },
    { href: "/runs", label: "Run History", icon: PlaySquare },
    { href: "/webhook-events", label: "Webhook Events", icon: Webhook },
  ];

  return (
    <div className="flex h-screen bg-background text-foreground font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card flex flex-col">
        <div className="h-14 flex items-center px-4 border-b border-border">
          <GitMerge className="w-5 h-5 text-primary mr-2" />
          <span className="font-mono font-bold tracking-tight text-sm">GH_AUTOMATION</span>
        </div>
        
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          <div className="px-3 mb-2 text-xs font-mono text-muted-foreground uppercase tracking-wider">
            Menu
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location === item.href || (location.startsWith(item.href) && item.href !== "/");
            return (
              <Link key={item.href} href={item.href} className={`flex items-center px-3 py-2 text-sm rounded-md transition-colors ${active ? 'bg-primary/10 text-primary font-medium' : 'text-muted-foreground hover:bg-accent hover:text-foreground'}`}>
                <Icon className="w-4 h-4 mr-3" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border bg-card/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center text-xs text-muted-foreground font-mono">
              <div className={`w-2 h-2 rounded-full mr-2 ${health?.status === 'ok' ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`} />
              API Status
            </div>
            <Badge variant="outline" className="text-[10px] uppercase font-mono px-1.5 py-0">v0.1</Badge>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <div className="flex-1 overflow-y-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
