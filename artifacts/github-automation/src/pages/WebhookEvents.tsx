import { useListWebhookEvents } from "@workspace/api-client-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow, format } from "date-fns";

export default function WebhookEvents() {
  const { data: events, isLoading } = useListWebhookEvents();

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-mono tracking-tight">Webhook Events</h1>
        <p className="text-sm text-muted-foreground mt-1">Raw events received from GitHub.</p>
      </div>

      <div className="border border-border rounded-md bg-card/50 overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead className="font-mono text-xs uppercase w-[200px]">Event Type</TableHead>
              <TableHead className="font-mono text-xs uppercase">Repository</TableHead>
              <TableHead className="font-mono text-xs uppercase">Delivery ID</TableHead>
              <TableHead className="font-mono text-xs uppercase text-right w-[150px]">Triggered Count</TableHead>
              <TableHead className="font-mono text-xs uppercase text-right w-[200px]">Processed At</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-6 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-48" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-12 ml-auto" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-24 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : events?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-muted-foreground font-mono text-sm">
                  No webhook events received yet.
                </TableCell>
              </TableRow>
            ) : (
              events?.map((event) => (
                <TableRow key={event.id} className="hover:bg-muted/30">
                  <TableCell>
                    <Badge variant="outline" className="font-mono text-[10px] uppercase bg-card">
                      {event.eventType}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono text-sm">{event.repository}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground truncate max-w-[200px]">
                    {event.deliveryId || '—'}
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {event.automationsTriggered > 0 ? (
                      <span className="text-green-500 font-bold">{event.automationsTriggered}</span>
                    ) : (
                      <span className="text-muted-foreground">{event.automationsTriggered}</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs text-muted-foreground">
                    <div title={format(new Date(event.processedAt), "PPpp")}>
                      {formatDistanceToNow(new Date(event.processedAt), { addSuffix: true })}
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
