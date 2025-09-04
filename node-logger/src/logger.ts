import dotenv from 'dotenv';

dotenv.config();

let AffordMedLogger: any = null;
try {
  // Dynamically import/require to avoid install-time failure
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  AffordMedLogger = require('affordmed-logger');
} catch {
  AffordMedLogger = null;
}

export type LogPayload = {
  stack: string;
  level: string;
  pkg: string;
  message: string;
  meta?: Record<string, unknown>;
};

export type AffordMedCredentials = {
  email: string;
  name: string;
  rollNo: string;
  accessCode: string;
  clientID: string;
  clientSecret: string;
};

function readCredentialsFromEnv(): AffordMedCredentials {
  const {
    EMAIL,
    NAME,
    ROLLNO,
    ACCESS_CODE,
    CLIENT_ID,
    CLIENT_SECRET,
  } = process.env;

  const missing = [
    ['EMAIL', EMAIL],
    ['NAME', NAME],
    ['ROLLNO', ROLLNO],
    ['ACCESS_CODE', ACCESS_CODE],
    ['CLIENT_ID', CLIENT_ID],
    ['CLIENT_SECRET', CLIENT_SECRET],
  ].filter(([, v]) => !v);

  if (missing.length > 0) {
    console.warn(`Missing env vars: ${missing.map(([k]) => k).join(', ')}`);
  }

  return {
    email: EMAIL || '',
    name: NAME || '',
    rollNo: ROLLNO || '',
    accessCode: ACCESS_CODE || '',
    clientID: CLIENT_ID || '',
    clientSecret: CLIENT_SECRET || '',
  };
}

const credentials = readCredentialsFromEnv();

let loggerInstance: any;
try {
  if (!AffordMedLogger) {
    throw new Error('affordmed-logger not installed');
  }
  if (typeof AffordMedLogger === 'function') {
    loggerInstance = new AffordMedLogger(credentials);
  } else if (AffordMedLogger?.default && typeof AffordMedLogger.default === 'function') {
    loggerInstance = new AffordMedLogger.default(credentials);
  } else if (AffordMedLogger?.Logger && typeof AffordMedLogger.Logger === 'function') {
    loggerInstance = new AffordMedLogger.Logger(credentials);
  } else {
    throw new Error('Unknown affordmed-logger export shape');
  }
} catch (err) {
  console.error('AffordMed Logger unavailable, using console fallback:', (err as Error)?.message);
  loggerInstance = null;
}

export async function forwardLog(payload: LogPayload): Promise<any> {
  const safePayload = {
    stack: payload.stack,
    level: payload.level,
    pkg: payload.pkg,
    message: payload.message,
    meta: payload.meta || {},
  };

  if (!loggerInstance) {
    console.log('[affordmed-log-fallback]', JSON.stringify(safePayload));
    return { ok: true, fallback: true };
  }

  const fn = loggerInstance.Log || loggerInstance.log || loggerInstance.write || loggerInstance.send;
  if (typeof fn !== 'function') {
    console.error('AffordMed logger instance has no log function. Falling back.');
    console.log('[affordmed-log-fallback]', JSON.stringify(safePayload));
    return { ok: true, fallback: true };
  }

  const result = await fn.call(loggerInstance, safePayload);
  return result ?? { ok: true };
} 