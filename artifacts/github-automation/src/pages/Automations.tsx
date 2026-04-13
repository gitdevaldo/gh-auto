import { Link } from "wouter";
import { useListAutomations, useDeleteAutomation, useToggleAutomation, getListAutomationsQueryKey } from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Play, Trash2, Plus, ArrowRight, Settings } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { formatDistanceToNow } from "date-fns";

export default function Automations() {
  const { data: automations, isLoading } = useListAutomations();
  const deleteAutomation = useDeleteAutomation();
  const toggleAutomation = useToggleAutomation();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const handleToggle = (id: number) => {
    toggleAutomation.mutate({ id }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListAutomationsQueryKey() });
        toast({ title: "Automation toggled", description: "Status updated successfully." });
      },
      onError: (err) => {
        toast({ title: "Error", description: "Failed to toggle automation.", variant: "destructive" });
      }
    });
  };

  const handleDelete = (id: number) => {
    if (!confirm("Are you sure you want to delete this automation?")) return;
    deleteAutomation.mutate({ id }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListAutomationsQueryKey() });
        toast({ title: "Automation deleted", description: "The rule has been removed." });
      },
      onError: (err) => {
        toast({ title: "Error", description: "Failed to delete automation.", variant: "destructive" });
      }
    });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tight">Automations</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage rules that react to GitHub events.</p>
        </div>
        <Link href="/automations/new">
          <Button className="font-mono uppercase tracking-wider text-xs">
            <Plus className="w-4 h-4 mr-2" /> New Rule
          </Button>
        </Link>
      </div>

      <div className="border border-border rounded-md bg-card/50 overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead className="w-[400px] font-mono text-xs uppercase">Name & Repo</TableHead>
              <TableHead className="font-mono text-xs uppercase">Trigger → Action</TableHead>
              <TableHead className="font-mono text-xs uppercase text-right">Runs</TableHead>
              <TableHead className="font-mono text-xs uppercase text-right">Last Run</TableHead>
              <TableHead className="w-[100px] font-mono text-xs uppercase text-center">Status</TableHead>
              <TableHead className="w-[100px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-6 w-48" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-12 ml-auto" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-24 ml-auto" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-10 mx-auto" /></TableCell>
                  <TableCell><Skeleton className="h-8 w-16 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : automations?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-32 text-center text-muted-foreground font-mono text-sm">
                  No automations configured.
                </TableCell>
              </TableRow>
            ) : (
              automations?.map((automation) => (
                <TableRow key={automation.id} className="hover:bg-muted/30 group">
                  <TableCell>
                    <div className="flex flex-col">
                      <Link href={`/automations/${automation.id}`} className="font-medium text-sm hover:text-primary transition-colors w-fit">
                        {automation.name}
                      </Link>
                      <span className="text-xs text-muted-foreground font-mono mt-1">{automation.repository}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center text-xs font-mono space-x-2">
                      <Badge variant="outline" className="px-1.5 py-0 text-[10px] bg-blue-500/10 text-blue-400 border-blue-500/20">{automation.triggerEvent}</Badge>
                      <ArrowRight className="w-3 h-3 text-muted-foreground" />
                      <Badge variant="outline" className="px-1.5 py-0 text-[10px] bg-purple-500/10 text-purple-400 border-purple-500/20">{automation.actionType}</Badge>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {automation.runCount}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs text-muted-foreground">
                    {automation.lastRunAt ? formatDistanceToNow(new Date(automation.lastRunAt), { addSuffix: true }) : 'Never'}
                  </TableCell>
                  <TableCell className="text-center">
                    <Switch
                      checked={automation.enabled}
                      onCheckedChange={() => handleToggle(automation.id)}
                      disabled={toggleAutomation.isPending}
                    />
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Link href={`/automations/${automation.id}`}>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <Settings className="w-4 h-4 text-muted-foreground hover:text-foreground" />
                        </Button>
                      </Link>
                      <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive" onClick={() => handleDelete(automation.id)} disabled={deleteAutomation.isPending}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
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
