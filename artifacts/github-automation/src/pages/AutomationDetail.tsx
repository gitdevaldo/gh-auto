import { useParams, Link } from "wouter";
import { useGetAutomation, useListRuns, getGetAutomationQueryKey } from "@workspace/api-client-react";
import { ArrowLeft, Play, Settings2, Activity, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatDistanceToNow, format } from "date-fns";
import { RunStatusBadge } from "./Dashboard";

export default function AutomationDetail() {
  const { id } = useParams();
  const automationId = parseInt(id || "0", 10);
  
  const { data: automation, isLoading: automationLoading } = useGetAutomation(automationId, {
    query: { enabled: !!automationId, queryKey: getGetAutomationQueryKey(automationId) }
  });

  const { data: runs, isLoading: runsLoading } = useListRuns(
    { automationId },
    { query: { enabled: !!automationId } }
  );

  if (automationLoading) {
    return <div className="p-8"><Skeleton className="h-10 w-64 mb-4" /><Skeleton className="h-64 w-full" /></div>;
  }

  if (!automation) {
    return <div className="p-8 text-center text-muted-foreground">Automation not found.</div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/automations">
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold font-mono tracking-tight">{automation.name}</h1>
              {automation.enabled ? (
                <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20 text-[10px] uppercase font-mono px-1.5 py-0">Active</Badge>
              ) : (
                <Badge variant="outline" className="bg-muted text-muted-foreground text-[10px] uppercase font-mono px-1.5 py-0">Disabled</Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground mt-1">{automation.description || "No description provided."}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <Card className="bg-card/50 border-border">
            <CardHeader className="pb-3 border-b border-border/50">
              <CardTitle className="text-sm font-mono uppercase tracking-wider text-muted-foreground flex items-center">
                <Settings2 className="w-4 h-4 mr-2" /> Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="grid grid-cols-2 divide-x divide-border/50">
                <div className="p-6 space-y-4">
                  <div>
                    <div className="text-[10px] font-mono text-muted-foreground uppercase mb-1">Repository</div>
                    <div className="font-mono text-sm font-semibold">{automation.repository}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-muted-foreground uppercase mb-1">Trigger Event</div>
                    <Badge variant="outline" className="font-mono text-xs bg-blue-500/10 text-blue-400 border-blue-500/20">{automation.triggerEvent}</Badge>
                  </div>
                  {automation.triggerCondition && (
                    <div>
                      <div className="text-[10px] font-mono text-muted-foreground uppercase mb-1">Condition</div>
                      <code className="px-2 py-1 bg-black text-green-400 rounded text-xs font-mono">{automation.triggerCondition}</code>
                    </div>
                  )}
                </div>
                <div className="p-6 space-y-4 bg-muted/10">
                  <div>
                    <div className="text-[10px] font-mono text-muted-foreground uppercase mb-1">Action Type</div>
                    <Badge variant="outline" className="font-mono text-xs bg-purple-500/10 text-purple-400 border-purple-500/20">{automation.actionType}</Badge>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-muted-foreground uppercase mb-2">Action Payload Config</div>
                    <pre className="bg-black text-green-400 p-4 rounded-md text-xs font-mono overflow-x-auto border border-border/50 shadow-inner">
                      {JSON.stringify(automation.actionConfig, null, 2) || "{}"}
                    </pre>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="bg-card/50 border-border">
            <CardHeader className="pb-3 border-b border-border/50">
              <CardTitle className="text-sm font-mono uppercase tracking-wider text-muted-foreground flex items-center">
                <Activity className="w-4 h-4 mr-2" /> Stats
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="flex justify-between items-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">Total Runs</div>
                <div className="font-mono text-xl font-bold">{automation.runCount}</div>
              </div>
              <div className="flex justify-between items-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">Created</div>
                <div className="font-mono text-sm">{format(new Date(automation.createdAt), "MMM d, yyyy")}</div>
              </div>
              <div className="flex justify-between items-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">Last Run</div>
                <div className="font-mono text-sm">{automation.lastRunAt ? formatDistanceToNow(new Date(automation.lastRunAt), { addSuffix: true }) : 'Never'}</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Card className="bg-card/50 border-border">
        <CardHeader className="pb-3 border-b border-border/50">
          <CardTitle className="text-sm font-mono uppercase tracking-wider text-muted-foreground flex items-center">
            <Play className="w-4 h-4 mr-2" /> Recent Runs
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-muted/30">
              <TableRow>
                <TableHead className="font-mono text-xs uppercase">Status</TableHead>
                <TableHead className="font-mono text-xs uppercase">Repository</TableHead>
                <TableHead className="font-mono text-xs uppercase">Event</TableHead>
                <TableHead className="font-mono text-xs uppercase">Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runsLoading ? (
                <TableRow>
                  <TableCell colSpan={4}><Skeleton className="h-10 w-full" /></TableCell>
                </TableRow>
              ) : runs?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="h-32 text-center text-muted-foreground font-mono text-sm">
                    No runs recorded yet.
                  </TableCell>
                </TableRow>
              ) : (
                runs?.slice(0, 10).map((run) => (
                  <TableRow key={run.id} className="hover:bg-muted/30">
                    <TableCell><RunStatusBadge status={run.status} /></TableCell>
                    <TableCell className="font-mono text-sm">{run.repository}</TableCell>
                    <TableCell className="font-mono text-sm">{run.triggerEvent}</TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(run.createdAt), { addSuffix: true })}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
