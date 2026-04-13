import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import { automationsTable, insertAutomationSchema } from "@workspace/db";
import { eq, sql } from "drizzle-orm";
import {
  CreateAutomationBody,
  UpdateAutomationBody,
  GetAutomationParams,
  UpdateAutomationParams,
  DeleteAutomationParams,
  ToggleAutomationParams,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/automations", async (req, res) => {
  const automations = await db.select().from(automationsTable).orderBy(automationsTable.createdAt);
  res.json(automations.map(toAutomationResponse));
});

router.post("/automations", async (req, res) => {
  const body = CreateAutomationBody.parse(req.body);
  const [created] = await db
    .insert(automationsTable)
    .values({
      name: body.name,
      description: body.description,
      triggerEvent: body.triggerEvent,
      triggerCondition: body.triggerCondition,
      actionType: body.actionType,
      actionConfig: body.actionConfig ?? {},
      enabled: body.enabled ?? true,
      repository: body.repository,
    })
    .returning();
  res.status(201).json(toAutomationResponse(created));
});

router.get("/automations/:id", async (req, res) => {
  const params = GetAutomationParams.parse({ id: Number(req.params.id) });
  const [automation] = await db
    .select()
    .from(automationsTable)
    .where(eq(automationsTable.id, params.id));
  if (!automation) {
    res.status(404).json({ error: "Automation not found" });
    return;
  }
  res.json(toAutomationResponse(automation));
});

router.put("/automations/:id", async (req, res) => {
  const params = UpdateAutomationParams.parse({ id: Number(req.params.id) });
  const body = UpdateAutomationBody.parse(req.body);
  const [updated] = await db
    .update(automationsTable)
    .set({
      ...(body.name !== undefined && { name: body.name }),
      ...(body.description !== undefined && { description: body.description }),
      ...(body.triggerEvent !== undefined && { triggerEvent: body.triggerEvent }),
      ...(body.triggerCondition !== undefined && { triggerCondition: body.triggerCondition }),
      ...(body.actionType !== undefined && { actionType: body.actionType }),
      ...(body.actionConfig !== undefined && { actionConfig: body.actionConfig }),
      ...(body.enabled !== undefined && { enabled: body.enabled }),
      ...(body.repository !== undefined && { repository: body.repository }),
      updatedAt: new Date(),
    })
    .where(eq(automationsTable.id, params.id))
    .returning();
  if (!updated) {
    res.status(404).json({ error: "Automation not found" });
    return;
  }
  res.json(toAutomationResponse(updated));
});

router.delete("/automations/:id", async (req, res) => {
  const params = DeleteAutomationParams.parse({ id: Number(req.params.id) });
  await db.delete(automationsTable).where(eq(automationsTable.id, params.id));
  res.status(204).send();
});

router.post("/automations/:id/toggle", async (req, res) => {
  const params = ToggleAutomationParams.parse({ id: Number(req.params.id) });
  const [current] = await db
    .select()
    .from(automationsTable)
    .where(eq(automationsTable.id, params.id));
  if (!current) {
    res.status(404).json({ error: "Automation not found" });
    return;
  }
  const [updated] = await db
    .update(automationsTable)
    .set({ enabled: !current.enabled, updatedAt: new Date() })
    .where(eq(automationsTable.id, params.id))
    .returning();
  res.json(toAutomationResponse(updated));
});

function toAutomationResponse(a: typeof automationsTable.$inferSelect) {
  return {
    id: a.id,
    name: a.name,
    description: a.description ?? undefined,
    triggerEvent: a.triggerEvent,
    triggerCondition: a.triggerCondition ?? undefined,
    actionType: a.actionType,
    actionConfig: a.actionConfig ?? {},
    enabled: a.enabled,
    repository: a.repository,
    createdAt: a.createdAt.toISOString(),
    updatedAt: a.updatedAt.toISOString(),
    lastRunAt: a.lastRunAt ? a.lastRunAt.toISOString() : null,
    runCount: a.runCount,
  };
}

export default router;
