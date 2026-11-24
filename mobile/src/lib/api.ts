/**
 * Talking to our FastAPI backend.
 *
 * The server address is found automatically: in development the app is loaded
 * from the Mac (Expo's dev server, port 8081), so the backend is on the same
 * computer, port 8000. To use another address, put
 * EXPO_PUBLIC_API_URL=http://192.168.0.29:8000 into mobile/.env.local.
 */
import Constants from 'expo-constants';
import { Platform } from 'react-native';

const API_PREFIX = '/api/v1';
const TIMEOUT_MS = 10_000;
const UPLOAD_TIMEOUT_MS = 120_000;

function detectServer(): string {
  if (process.env.EXPO_PUBLIC_API_URL) return process.env.EXPO_PUBLIC_API_URL;
  if (Platform.OS === 'web') return `http://${globalThis.location?.hostname ?? 'localhost'}:8000`;
  // e.g. "192.168.0.29:8081" — the Mac that serves the app.
  const host = Constants.expoConfig?.hostUri?.split(':')[0] ?? 'localhost';
  return `http://${host}:8000`;
}

export const SERVER_URL = detectServer();

let authToken: string | null = null;
let onUnauthorized: (() => void) | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

/** Headers for loading protected files (photos) directly, e.g. in <Image>. */
export function authHeaders(): Record<string, string> {
  return authToken ? { Authorization: `Bearer ${authToken}` } : {};
}

/** A server path like "/api/v1/..." -> a full address. */
export function serverUrl(path: string): string {
  return `${SERVER_URL}${path}`;
}

/** Called when the server says the token is no longer valid (e.g. expired). */
export function setOnUnauthorized(handler: (() => void) | null) {
  onUnauthorized = handler;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
  ) {
    super(typeof detail === 'string' ? detail : `Request failed with status ${status}`);
  }
}

export class NetworkError extends Error {
  constructor() {
    super(
      'Нет связи с сервером. Проверьте, что сервер запущен (uv run fastapi dev --host 0.0.0.0) ' +
        'и телефон в той же Wi-Fi сети, что и Mac.',
    );
  }
}

type Query = Record<string, string | number | boolean | (string | number)[] | null | undefined>;

type Options = {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  json?: unknown;
  form?: Record<string, string>;
  multipart?: FormData; // file uploads
  query?: Query;
};

function buildQuery(query?: Query): string {
  if (!query) return '';
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === null || value === undefined) continue;
    // Lists become repeated keys: exclude_ideas=1&exclude_ideas=2
    for (const item of Array.isArray(value) ? value : [value]) params.append(key, String(item));
  }
  const text = params.toString();
  return text ? `?${text}` : '';
}

export async function api<T>(path: string, options: Options = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  let body: string | undefined;
  if (options.json !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(options.json);
  } else if (options.form) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams(options.form).toString();
  }
  // For FormData the Content-Type (with its "boundary") is set by fetch itself.
  const payload: BodyInit | undefined = options.multipart ?? body;

  const controller = new AbortController();
  const timer = setTimeout(
    () => controller.abort(),
    options.multipart ? UPLOAD_TIMEOUT_MS : TIMEOUT_MS,
  );
  let response: Response;
  try {
    response = await fetch(`${SERVER_URL}${API_PREFIX}${path}${buildQuery(options.query)}`, {
      method: options.method ?? 'GET',
      headers,
      body: payload,
      signal: controller.signal,
    });
  } catch {
    throw new NetworkError();
  } finally {
    clearTimeout(timer);
  }

  if (response.status === 204) return undefined as T;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && authToken) onUnauthorized?.();
    throw new ApiError(response.status, data?.detail ?? null);
  }
  return data as T;
}

/** A short message for the user from any error. */
export function errorMessage(error: unknown, fallback = 'Что-то пошло не так'): string {
  if (error instanceof NetworkError) return error.message;
  if (error instanceof ApiError) {
    if (typeof error.detail === 'string') return error.detail;
    // FastAPI validation errors: [{loc, msg}, ...]
    if (Array.isArray(error.detail) && error.detail[0]?.msg) return String(error.detail[0].msg);
  }
  return fallback;
}
