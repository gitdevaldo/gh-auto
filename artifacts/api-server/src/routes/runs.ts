import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import { automationRunsTable, automationsTable } from "@workspace/db";
import { eq, and, count, sql, desc } from "drizzle-orm";
import { ListRunsQueryParams } from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/runs", async (req, res) => {
  const params = ListRunsQueryParams.parse({
    automationId: req.query.automationId ? Number(req.query.automationId) : undefined,
    status: req.query.status,
  });

  const conditions = [];
  if (params.automationId) {
    conditions.push(eq(automationRunsTable.automationId, params.automationId));
  }
  if (params.status) {
    conditions.push(eq(automationRunsTable.status, params.status as "success" | "failure" | "skipped"));
  }

  const runs = await db
    .select()
    .from(automationRunsTable)
    .where(conditions.length > 0 ? and(...conditions) : undefined)
    .orderBy(desc(automationRunsTable.createdAt))
    .limit(100);

  res.json(runs.map(toRunResponse));
});

router.get("/runs/stats", async (req, res) => {
  const [totals] = await db
    .select({
      total: count(),
      success: sql<number>`count(*) filter (where status = 'success')`,
      failure: sql<number>`count(*) filter (where status = 'failure')`,
      skipped: sql<number>`count(*) filter (where status = 'skipped')`,
      last24hRuns: sql<number>`count(*) filter (where created_at > now() - interval '24 hours')`,
    })
    .from(automationRunsTable);

  const [automationCounts] = await db
    .select({
      totalAutomations: count(),
      activeAutomations: sql<number>`count(*) filter (where enabled = true)`,
    })
    .from(automationsTable);

  res.json({
    total: Number(totals.total),
    success: Number(totals.success),
    failure: Number(totals.failure),
    skipped: Number(totals.skipped),
    last24hRuns: Number(totals.last24hRuns),
    totalAutomations: Number(automationCounts.totalAutomations),
    activeAutomations: Number(automationCounts.activeAutomations),
  });
});

function toRunResponse(r: typeof automationRunsTable.$inferSelect) {
  return {
    id: r.id,
    automationId: r.automationId,
    automationName: r.automationName,
    triggerEvent: r.triggerEvent,
    repository: r.repository,
    status: r.status,
    errorMessage: r.errorMessage ?? null,
    payload: r.payload ?? {},
    createdAt: r.createdAt.toISOString(),
  };
}

export default router;
