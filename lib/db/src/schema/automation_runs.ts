import { pgTable, serial, integer, text, timestamp, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";
import { automationsTable } from "./automations";

export const automationRunsTable = pgTable("automation_runs", {
  id: serial("id").primaryKey(),
  automationId: integer("automation_id").notNull().references(() => automationsTable.id, { onDelete: "cascade" }),
  automationName: text("automation_name").notNull(),
  triggerEvent: text("trigger_event").notNull(),
  repository: text("repository").notNull(),
  status: text("status", { enum: ["success", "failure", "skipped"] }).notNull(),
  errorMessage: text("error_message"),
  payload: jsonb("payload").default({}),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertAutomationRunSchema = createInsertSchema(automationRunsTable).omit({
  id: true,
  createdAt: true,
});

export type InsertAutomationRun = z.infer<typeof insertAutomationRunSchema>;
export type AutomationRun = typeof automationRunsTable.$inferSelect;
