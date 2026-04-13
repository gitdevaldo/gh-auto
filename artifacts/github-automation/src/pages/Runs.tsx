import { useState } from "react";
import { useListRuns } from "@workspace/api-client-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow, format } from "date-fns";
import { RunStatusBadge } from "./Dashboard";
import type { ListRunsStatus } from "@workspace/api-client-react/src/generated/api.schemas";

export default function Runs() {
  const [statusFilter, setStatusFilter] = useState<ListRunsStatus | "all">("all");
  
  const params = statusFilter === "all" ? undefined : { status: statusFilter };
  const { data: runs, isLoading } = useListRuns(params);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tight">Run History</h1>
          <p className="text-sm text-muted-foreground mt-1">Log of all automation executions.</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="text-xs font-mono uppercase text-muted-foreground">Filter:</div>
          <Select value={statusFilter} onValueChange={(val) => setStatusFilter(val as ListRunsStatus | "all")}>
            <SelectTrigger className="w-[140px] font-mono text-xs h-8">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="success">Success</SelectItem>
              <SelectItem value="failure">Failure</SelectItem>
              <SelectItem value="skipped">Skipped</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="border border-border rounded-md bg-card/50 overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead className="font-mono text-xs uppercase w-[120px]">Status</TableHead>
              <TableHead className="font-mono text-xs uppercase">Automation</TableHead>
              <TableHead className="font-mono text-xs uppercase">Repository</TableHead>
              <TableHead className="font-mono text-xs uppercase">Event</TableHead>
              <TableHead className="font-mono text-xs uppercase text-right">Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-6 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-48" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-24 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : runs?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-muted-foreground font-mono text-sm">
                  No runs found matching the criteria.
                </TableCell>
              </TableRow>
            ) : (
              runs?.map((run) => (
                <TableRow key={run.id} className="hover:bg-muted/30">
                  <TableCell><RunStatusBadge status={run.status} /></TableCell>
                  <TableCell className="font-medium text-sm">{run.automationName}</TableCell>
                  <TableCell className="font-mono text-xs">{run.repository}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">{run.triggerEvent}</TableCell>
                  <TableCell className="text-right font-mono text-xs text-muted-foreground">
                    <div title={format(new Date(run.createdAt), "PPpp")}>
                      {formatDistanceToNow(new Date(run.createdAt), { addSuffix: true })}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
