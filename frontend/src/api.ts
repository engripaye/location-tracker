export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type UserResponse = {
  id: string;
  name: string;
  email: string;
};

export type SessionResponse = {
  session_id: string;
  share_token: string;
  share_url: string;
  expires_at: string;
};

export type SessionDetail = {
  id: string;
  active: boolean;
  expires_at: string;
  created_at: string;
};

export type LocationResponse = {
  id: string;
  session_id: string;
  latitude: number;
  longitude: number;
  accuracy: number | null;
  address: string | null;
  device_fingerprint: string | null;
  created_at: string;
};

export type SosResponse = {
  id: string;
  session_id: string | null;
  latitude: number | null;
  longitude: number | null;
  message: string | null;
  status: string;
  created_at: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  accessToken?: string | null
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  headers.set("X-Device-Fingerprint", getDeviceFingerprint());
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  }).catch(() => {
    throw new Error("Backend is not reachable. Start FastAPI on http://127.0.0.1:8000 and try again.");
  });

  if (!response.ok) {
    const message = await readError(response);
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function getWebSocketUrl(path: string): string {
  const baseUrl = API_BASE || window.location.origin;
  const url = new URL(path, baseUrl);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}

export function getDeviceFingerprint(): string {
  const parts = [
    navigator.userAgent,
    navigator.language,
    `${screen.width}x${screen.height}`,
    Intl.DateTimeFormat().resolvedOptions().timeZone
  ];
  return parts.join("|");
}

async function readError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") {
      return data.detail;
    }
  } catch {
    return response.statusText || "Request failed";
  }
  return response.statusText || "Request failed";
}
