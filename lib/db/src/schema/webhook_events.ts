import { pgTable, serial, text, timestamp, jsonb, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const webhookEventsTable = pgTable("webhook_events", {
  id: serial("id").primaryKey(),
  eventType: text("event_type").notNull(),
  repository: text("repository").notNull(),
  deliveryId: text("delivery_id"),
  payload: jsonb("payload").notNull().default({}),
  automationsTriggered: integer("automations_triggered").notNull().default(0),
  processedAt: timestamp("processed_at").notNull().defaultNow(),
});

export const insertWebhookEventSchema = createInsertSchema(webhookEventsTable).omit({
  id: true,
  processedAt: true,
});

export type InsertWebhookEvent = z.infer<typeof insertWebhookEventSchema>;
export type WebhookEvent = typeof webhookEventsTable.$inferSelect;
