import { pgTable, serial, text, boolean, integer, timestamp, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const automationsTable = pgTable("automations", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description"),
  triggerEvent: text("trigger_event").notNull(),
  triggerCondition: text("trigger_condition"),
  actionType: text("action_type").notNull(),
  actionConfig: jsonb("action_config").default({}),
  enabled: boolean("enabled").notNull().default(true),
  repository: text("repository").notNull(),
  runCount: integer("run_count").notNull().default(0),
  lastRunAt: timestamp("last_run_at"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertAutomationSchema = createInsertSchema(automationsTable).omit({
  id: true,
  runCount: true,
  lastRunAt: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertAutomation = z.infer<typeof insertAutomationSchema>;
export type Automation = typeof automationsTable.$inferSelect;
