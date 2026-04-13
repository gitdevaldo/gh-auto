import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import { webhookEventsTable, automationsTable, automationRunsTable } from "@workspace/db";
import { eq, desc } from "drizzle-orm";

const router: IRouter = Router();

router.post("/webhooks/github", async (req, res) => {
  const eventType = (req.headers["x-github-event"] as string) ?? "unknown";
  const deliveryId = (req.headers["x-github-delivery"] as string) ?? null;
  const payload = req.body as Record<string, unknown>;
  const repository = (payload.repository as { full_name?: string })?.full_name ?? "unknown/unknown";

  const matchingAutomations = await db
    .select()
    .from(automationsTable)
    .where(eq(automationsTable.enabled, true));

  const triggered = matchingAutomations.filter(
    (a) =>
      a.triggerEvent === eventType &&
      (a.repository === "*" || a.repository === repository),
  );

  const [webhookEvent] = await db
    .insert(webhookEventsTable)
    .values({
      eventType,
      repository,
      deliveryId,
      payload: payload as Record<string, unknown>,
      automationsTriggered: triggered.length,
    })
    .returning();

  for (const automation of triggered) {
    const status = "success" as const;
    await db.insert(automationRunsTable).values({
      automationId: automation.id,
      automationName: automation.name,
      triggerEvent: eventType,
      repository,
      status,
      payload: payload as Record<string, unknown>,
    });

    await db
      .update(automationsTable)
      .set({
        runCount: automation.runCount + 1,
        lastRunAt: new Date(),
        updatedAt: new Date(),
      })
      .where(eq(automationsTable.id, automation.id));
  }

  res.json({
    received: true,
    automationsTriggered: triggered.length,
  });
});

router.get("/webhook-events", async (req, res) => {
  const events = await db
    .select()
    .from(webhookEventsTable)
    .orderBy(desc(webhookEventsTable.processedAt))
    .limit(100);

  res.json(
    events.map((e) => ({
      id: e.id,
      eventType: e.eventType,
      repository: e.repository,
      deliveryId: e.deliveryId ?? null,
      payload: e.payload ?? {},
      processedAt: e.processedAt.toISOString(),
      automationsTriggered: e.automationsTriggered,
    })),
  );
});

export default router;
