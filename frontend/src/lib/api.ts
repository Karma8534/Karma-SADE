// Centralized API base + fetch helper.
//
// In `next dev` (CSR over http://localhost:3000) the relative `/v1/...` paths
// 404 because nothing serves them. In the Tauri build (`output: 'export'`,
// loaded via tauri:// or http://tauri.localhost) relative URLs resolve to the
// webview origin, which also has no backend. Both cases need an absolute URL
// pointing at the local cc_server_p1 bridge on 127.0.0.1:7891.

const FALLBACK_BRIDGE = 'http://127.0.0.1:7891';

let cachedBase: string | null = null;

export function apiBase(): string {
  if (cachedBase !== null) return cachedBase;

  // 1. Build-time override (next.config / tauri build env).
  const envBase = process.env.NEXT_PUBLIC_API_BASE;
  if (envBase && envBase.trim()) {
    cachedBase = envBase.trim().replace(/\/+$/, '');
    return cachedBase;
  }

  // 2. Runtime override (set by the Tauri shell or in the browser console
  //    via `localStorage.setItem('karma-api-base', 'http://127.0.0.1:7891')`).
  if (typeof window !== 'undefined') {
    try {
      const stored = window.localStorage.getItem('karma-api-base');
      if (stored && stored.trim()) {
        cachedBase = stored.trim().replace(/\/+$/, '');
        return cachedBase;
      }
    } catch {}
  }

  // 3. Tauri webview detection. Tauri 2 on Windows serves the app from
  //    `http://tauri.localhost`; older bundles use `tauri://localhost`. Either
  //    way, absolute URLs to 127.0.0.1 are required.
  if (typeof window !== 'undefined') {
    const proto = window.location.protocol;
    const host = window.location.hostname;
    if (proto === 'tauri:' || host === 'tauri.localhost') {
      cachedBase = FALLBACK_BRIDGE;
      return cachedBase;
    }
    // 4. `next dev` (http://localhost:3000) — same-origin won't reach the
    //    bridge either, so route through the bridge directly.
    if (host === 'localhost' || host === '127.0.0.1') {
      // If the page itself is served from the bridge port, keep relative URLs.
      if (window.location.port === '7891') {
        cachedBase = '';
        return cachedBase;
      }
      cachedBase = FALLBACK_BRIDGE;
      return cachedBase;
    }
  }

  cachedBase = FALLBACK_BRIDGE;
  return cachedBase;
}

export function apiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  const base = apiBase();
  if (!base) return path;
  return `${base}${path.startsWith('/') ? path : `/${path}`}`;
}

export interface ApiFetchInit extends RequestInit {
  token?: string;
  json?: unknown;
}

export async function apiFetch(path: string, init: ApiFetchInit = {}): Promise<Response> {
  const { token, json, headers, body, ...rest } = init;
  const merged: Record<string, string> = {};
  if (headers) {
    if (headers instanceof Headers) {
      headers.forEach((v, k) => { merged[k] = v; });
    } else if (Array.isArray(headers)) {
      for (const [k, v] of headers) merged[k] = v;
    } else {
      Object.assign(merged, headers as Record<string, string>);
    }
  }
  let actualBody = body;
  if (json !== undefined) {
    actualBody = JSON.stringify(json);
    if (!Object.keys(merged).some((k) => k.toLowerCase() === 'content-type')) {
      merged['Content-Type'] = 'application/json';
    }
  }
  const resolvedToken = token ?? readStoredToken();
  if (resolvedToken && !Object.keys(merged).some((k) => k.toLowerCase() === 'authorization')) {
    merged['Authorization'] = `Bearer ${resolvedToken}`;
  }
  const primaryUrl = apiUrl(path);
  const res = await fetch(primaryUrl, { ...rest, headers: merged, body: actualBody });
  // P-FU7 (S183 Nexus V3.0 merge fragment): on hub 5xx, retry once against direct P1 bridge if accessible.
  // Only applies when primary URL is remote (not already 127.0.0.1) and response is 5xx.
  if (res.status >= 500 && res.status < 600 && !/127\.0\.0\.1|localhost/.test(primaryUrl)) {
    try {
      const fallbackUrl = `${FALLBACK_BRIDGE}${path.startsWith('/') ? path : `/${path}`}`;
      const fbRes = await fetch(fallbackUrl, { ...rest, headers: merged, body: actualBody });
      if (fbRes.ok) return fbRes;
    } catch { /* fall through to original 5xx response */ }
  }
  return res;
}

function readStoredToken(): string {
  if (typeof window === 'undefined') return '';
  try {
    return window.localStorage.getItem('karma-token') || '';
  } catch {
    return '';
  }
}
