import { useState } from "wouter";
import { useLocation } from "wouter";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useCreateAutomation, getListAutomationsQueryKey } from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ArrowLeft, Save } from "lucide-react";
import { Link } from "wouter";

const formSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  repository: z.string().min(1, "Repository is required (e.g., owner/repo or *)"),
  triggerEvent: z.string().min(1, "Trigger event is required"),
  triggerCondition: z.string().optional(),
  actionType: z.string().min(1, "Action type is required"),
  actionConfig: z.string().refine(val => {
    if (!val) return true;
    try {
      JSON.parse(val);
      return true;
    } catch {
      return false;
    }
  }, "Must be valid JSON").optional(),
  enabled: z.boolean().default(true)
});

type FormValues = z.infer<typeof formSchema>;

export default function NewAutomation() {
  const [, setLocation] = useLocation();
  const createAutomation = useCreateAutomation();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      description: "",
      repository: "*",
      triggerEvent: "push",
      triggerCondition: "",
      actionType: "comment",
      actionConfig: "{\n  \"message\": \"Hello!\"\n}",
      enabled: true
    }
  });

  const onSubmit = (data: FormValues) => {
    let parsedConfig = {};
    if (data.actionConfig) {
      try {
        parsedConfig = JSON.parse(data.actionConfig);
      } catch (e) {
        toast({ title: "Invalid JSON", description: "Action config must be valid JSON.", variant: "destructive" });
        return;
      }
    }

    createAutomation.mutate(
      {
        data: {
          name: data.name,
          description: data.description,
          repository: data.repository,
          triggerEvent: data.triggerEvent,
          triggerCondition: data.triggerCondition,
          actionType: data.actionType,
          actionConfig: parsedConfig,
          enabled: data.enabled
        }
      },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: getListAutomationsQueryKey() });
          toast({ title: "Success", description: "Automation created." });
          setLocation("/automations");
        },
        onError: (error) => {
          toast({ title: "Error", description: "Failed to create automation.", variant: "destructive" });
        }
      }
    );
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/automations">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <ArrowLeft className="w-4 h-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tight">New Rule</h1>
          <p className="text-sm text-muted-foreground mt-1">Configure a new automated workflow.</p>
        </div>
      </div>

      <Card className="bg-card/50 border-border">
        <CardContent className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField control={form.control} name="name" render={({ field }) => (
                  <FormItem>
                    <FormLabel className="font-mono text-xs uppercase">Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Auto-label PRs" className="font-mono text-sm" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )} />

                <FormField control={form.control} name="repository" render={({ field }) => (
                  <FormItem>
                    <FormLabel className="font-mono text-xs uppercase">Repository</FormLabel>
                    <FormControl>
                      <Input placeholder="owner/repo or *" className="font-mono text-sm" {...field} />
                    </FormControl>
                    <FormDescription className="text-[10px]">Use * for all repos</FormDescription>
                    <FormMessage />
                  </FormItem>
                )} />
              </div>

              <FormField control={form.control} name="description" render={({ field }) => (
                <FormItem>
                  <FormLabel className="font-mono text-xs uppercase">Description</FormLabel>
                  <FormControl>
                    <Input placeholder="Labels new PRs with 'triage'" className="font-mono text-sm" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )} />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 border border-border bg-background rounded-md">
                <div className="space-y-4">
                  <h3 className="font-mono text-xs uppercase font-semibold text-blue-400">Trigger</h3>
                  
                  <FormField control={form.control} name="triggerEvent" render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-[10px] uppercase text-muted-foreground">Event Type</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger className="font-mono text-sm">
                            <SelectValue placeholder="Select event" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="push">push</SelectItem>
                          <SelectItem value="pull_request">pull_request</SelectItem>
                          <SelectItem value="issues">issues</SelectItem>
                          <SelectItem value="issue_comment">issue_comment</SelectItem>
                          <SelectItem value="release">release</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />

                  <FormField control={form.control} name="triggerCondition" render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-[10px] uppercase text-muted-foreground">Condition (Optional)</FormLabel>
                      <FormControl>
                        <Input placeholder="payload.action === 'opened'" className="font-mono text-sm" {...field} />
                      </FormControl>
                      <FormDescription className="text-[10px]">JS expression evaluated against payload</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>

                <div className="space-y-4">
                  <h3 className="font-mono text-xs uppercase font-semibold text-purple-400">Action</h3>
                  
                  <FormField control={form.control} name="actionType" render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-[10px] uppercase text-muted-foreground">Action Type</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger className="font-mono text-sm">
                            <SelectValue placeholder="Select action" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="label">label</SelectItem>
                          <SelectItem value="comment">comment</SelectItem>
                          <SelectItem value="close">close</SelectItem>
                          <SelectItem value="assign">assign</SelectItem>
                          <SelectItem value="request_review">request_review</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>
              </div>

              <FormField control={form.control} name="actionConfig" render={({ field }) => (
                <FormItem>
                  <FormLabel className="font-mono text-xs uppercase">Action Config (JSON)</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="{}" 
                      className="font-mono text-sm h-32 resize-y bg-black text-green-400" 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )} />

              <FormField control={form.control} name="enabled" render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border border-border p-4 bg-background">
                  <div className="space-y-0.5">
                    <FormLabel className="font-mono text-xs uppercase">Enable Rule</FormLabel>
                    <FormDescription className="text-xs">Rule will process incoming webhooks.</FormDescription>
                  </div>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )} />

              <div className="flex justify-end pt-4 border-t border-border">
                <Button type="submit" disabled={createAutomation.isPending} className="font-mono uppercase tracking-wider text-xs">
                  <Save className="w-4 h-4 mr-2" />
                  {createAutomation.isPending ? "Saving..." : "Create Rule"}
                </Button>
              </div>

            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
