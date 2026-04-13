import { Router, type IRouter } from "express";
import healthRouter from "./health";
import automationsRouter from "./automations";
import runsRouter from "./runs";
import webhooksRouter from "./webhooks";

const router: IRouter = Router();

router.use(healthRouter);
router.use(automationsRouter);
router.use(runsRouter);
router.use(webhooksRouter);

export default router;
