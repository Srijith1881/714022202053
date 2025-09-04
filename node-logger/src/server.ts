import express, { Request, Response, NextFunction } from 'express';
import dotenv from 'dotenv';
import { forwardLog, LogPayload } from './logger';

dotenv.config();

const app = express();
app.use(express.json({ limit: '1mb' }));

const PORT = Number(process.env.LOGGER_PORT || 4000);

app.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok' });
});

app.post('/log', async (req: Request, res: Response) => {
  const body = req.body as Partial<LogPayload>;

  if (!body || !body.stack || !body.level || !body.pkg || !body.message) {
    return res.status(400).json({
      error: 'Invalid body. Expected { stack, level, pkg, message, meta? }',
    });
  }

  try {
    const result = await forwardLog({
      stack: String(body.stack),
      level: String(body.level),
      pkg: String(body.pkg),
      message: String(body.message),
      meta: body.meta || {},
    });
    return res.json({ ok: true, result });
  } catch (err: any) {
    return res.status(500).json({ ok: false, error: err?.message || 'Unknown error' });
  }
});

// Global error handler
app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
  // eslint-disable-next-line no-console
  console.error('Node logger error:', err);
  res.status(500).json({ ok: false, error: 'Internal Server Error' });
});

app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`Node logger service listening on port ${PORT}`);
}); 