import { useGetRunStats, useListWebhookEvents, useListRuns } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Zap, CheckCircle2, XCircle, SkipForward, Activity } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useGetRunStats();
  const { data: webhooks, isLoading: webhooksLoading } = useListWebhookEvents();
  const { data: runs, isLoading: runsLoading } = useListRuns();

  const recentWebhooks = webhooks?.slice(0, 5) || [];
  const recentRuns = runs?.slice(0, 5) || [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Overview of your GitHub automation activity.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Active Automations" value={stats?.activeAutomations} icon={<Zap className="w-4 h-4 text-primary" />} isLoading={statsLoading} />
        <StatCard title="24h Runs" value={stats?.last24hRuns} icon={<Activity className="w-4 h-4 text-blue-500" />} isLoading={statsLoading} />
        <StatCard title="Total Success" value={stats?.success} icon={<CheckCircle2 className="w-4 h-4 text-green-500" />} isLoading={statsLoading} />
        <StatCard title="Total Failures" value={stats?.failure} icon={<XCircle className="w-4 h-4 text-red-500" />} isLoading={statsLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-card/50 border-border">
          <CardHeader className="pb-3 border-b border-border/50">
            <CardTitle className="text-sm font-mono">Recent Automation Runs</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {runsLoading ? (
              <div className="p-4 space-y-3">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : recentRuns.length === 0 ? (
              <div className="p-8 text-center text-sm text-muted-foreground">No recent runs.</div>
            ) : (
              <div className="divide-y divide-border/50">
                {recentRuns.map(run => (
                  <div key={run.id} className="p-4 flex items-center justify-between hover:bg-muted/30 transition-colors">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-sm">{run.automationName}</span>
                        <RunStatusBadge status={run.status} />
                      </div>
                      <div className="text-xs text-muted-foreground font-mono">
                        {run.repository} • {run.triggerEvent}
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground whitespace-nowrap">
                      {formatDistanceToNow(new Date(run.createdAt), { addSuffix: true })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-border">
          <CardHeader className="pb-3 border-b border-border/50">
            <CardTitle className="text-sm font-mono">Recent Webhooks Received</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {webhooksLoading ? (
              <div className="p-4 space-y-3">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : recentWebhooks.length === 0 ? (
              <div className="p-8 text-center text-sm text-muted-foreground">No recent webhooks.</div>
            ) : (
              <div className="divide-y divide-border/50">
                {recentWebhooks.map(event => (
                  <div key={event.id} className="p-4 flex items-center justify-between hover:bg-muted/30 transition-colors">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="font-mono text-[10px] uppercase">{event.eventType}</Badge>
                        <span className="text-sm font-medium">{event.repository}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Triggered {event.automationsTriggered} automations
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground whitespace-nowrap">
                      {formatDistanceToNow(new Date(event.processedAt), { addSuffix: true })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, isLoading }: { title: string; value?: number; icon: React.ReactNode; isLoading: boolean }) {
  return (
    <Card className="bg-card/50 border-border">
      <CardContent className="p-6 flex flex-col justify-center h-full">
        <div className="flex items-center justify-between space-x-2 mb-2">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider font-mono">{title}</p>
          {icon}
        </div>
        {isLoading ? (
          <Skeleton className="h-8 w-16" />
        ) : (
          <div className="text-3xl font-bold font-mono">{value ?? 0}</div>
        )}
      </CardContent>
    </Card>
  );
}

export function RunStatusBadge({ status }: { status: string }) {
  if (status === 'success') {
    return <Badge variant="secondary" className="bg-green-500/10 text-green-500 hover:bg-green-500/20 border-green-500/20 text-[10px] uppercase font-mono px-1.5 py-0">Success</Badge>;
  }
  if (status === 'failure') {
    return <Badge variant="destructive" className="bg-red-500/10 text-red-500 hover:bg-red-500/20 border-red-500/20 text-[10px] uppercase font-mono px-1.5 py-0">Failure</Badge>;
  }
  return <Badge variant="outline" className="text-muted-foreground text-[10px] uppercase font-mono px-1.5 py-0">Skipped</Badge>;
}
