import React, { FormEvent, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  LocationResponse,
  SessionDetail,
  SessionResponse,
  SosResponse,
  TokenResponse,
  UserResponse,
  apiRequest,
  getWebSocketUrl
} from "./api";
import "./styles.css";

type AuthMode = "login" | "register";
type AuthPanelMode = AuthMode | "forgot";
type PrimaryView = "overview" | "share" | "monitor";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserResponse | null;
};

const storedAuth = readAuth();

function App() {
  const [auth, setAuth] = useState<AuthState>(storedAuth);
  const [view, setView] = useState<PrimaryView>("overview");
  const [sessions, setSessions] = useState<SessionDetail[]>([]);
  const [activeSession, setActiveSession] = useState<SessionResponse | null>(null);
  const [locations, setLocations] = useState<LocationResponse[]>([]);
  const [status, setStatus] = useState("Ready");

  const isAuthenticated = Boolean(auth.accessToken);

  useEffect(() => {
    persistAuth(auth);
  }, [auth]);

  useEffect(() => {
    if (!auth.accessToken) {
      return;
    }
    apiRequest<UserResponse>("/auth/me", {}, auth.accessToken)
      .then((user) => setAuth((current) => ({ ...current, user })))
      .catch(() => setAuth({ accessToken: null, refreshToken: null, user: null }));
    loadSessions(auth.accessToken, setSessions);
  }, [auth.accessToken]);

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <div className="eyebrow">Engr. Ipaye Location Tracker</div>
          <h1>ENGR. IPAYE LOCATION TRACKER FOR EMERGENCY SITUATION</h1>
          <p>
            Authenticate responders, create expiring emergency share links, stream GPS updates in real time,
            and coordinate rapid SOS response from one clean command dashboard.
          </p>
          <div className="hero-actions">
            <button className="primary-button" onClick={() => setView("overview")}>
              Open dashboard
            </button>
            <button className="ghost-button" onClick={() => setView("share")}>
              Share location
            </button>
          </div>
        </div>
        <MapPreview locations={locations} />
      </section>

      <section className="workspace-grid">
        <aside className="control-rail">
          <BrandStatus user={auth.user} isAuthenticated={isAuthenticated} />
          <nav className="nav-list" aria-label="Primary">
            <button className={view === "overview" ? "active" : ""} onClick={() => setView("overview")}>
              Dashboard
            </button>
            <button className={view === "share" ? "active" : ""} onClick={() => setView("share")}>
              Share device
            </button>
            <button className={view === "monitor" ? "active" : ""} onClick={() => setView("monitor")}>
              Live monitor
            </button>
          </nav>
          <div className="status-chip">{status}</div>
        </aside>

        <section className="content-area">
          {!isAuthenticated ? (
            <AuthPanel setAuth={setAuth} setStatus={setStatus} />
          ) : (
            <>
              {view === "overview" && (
                <Dashboard
                  auth={auth}
                  sessions={sessions}
                  activeSession={activeSession}
                  setActiveSession={setActiveSession}
                  setSessions={setSessions}
                  setStatus={setStatus}
                  setAuth={setAuth}
                />
              )}
              {view === "share" && <ShareDevice setStatus={setStatus} />}
              {view === "monitor" && (
                <LiveMonitor locations={locations} setLocations={setLocations} setStatus={setStatus} />
              )}
            </>
          )}
        </section>
      </section>
    </main>
  );
}

function AuthPanel({ setAuth, setStatus }: { setAuth: (auth: AuthState) => void; setStatus: (value: string) => void }) {
  const [mode, setMode] = useState<AuthPanelMode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (mode === "forgot") {
      setStatus(email ? `Password reset request prepared for ${email}` : "Enter your email first");
      return;
    }
    if (mode === "register" && password !== confirmPassword) {
      setStatus("Passwords do not match");
      return;
    }
    if (mode === "register" && password.length < 8) {
      setStatus("Password must be at least 8 characters");
      return;
    }
    setBusy(true);
    setStatus(mode === "login" ? "Signing in" : "Creating account");
    try {
      const payload = mode === "login" ? { email, password } : { name, email, password };
      const tokens = await apiRequest<TokenResponse>(`/auth/${mode}`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      const user = await apiRequest<UserResponse>("/auth/me", {}, tokens.access_token);
      setAuth({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token, user });
      setStatus("Authenticated");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-layout">
      <section className="panel auth-card">
        <div className="section-heading">
          <span>Secure access</span>
          <h2>
            {mode === "forgot"
              ? "Recover access"
              : mode === "login"
                ? "Welcome back"
                : "Create emergency responder account"}
          </h2>
        </div>
        <div className="segmented">
          <button className={mode === "login" ? "selected" : ""} onClick={() => setMode("login")}>
            Login
          </button>
          <button className={mode === "register" ? "selected" : ""} onClick={() => setMode("register")}>
            Register
          </button>
        </div>
        <form className="form-stack" onSubmit={submit}>
          {mode === "register" && (
            <label>
              Full name
              <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Enter full name" required />
            </label>
          )}
          <label>
            Email
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@example.com" required />
          </label>
          {mode !== "forgot" && (
            <>
              <PasswordField
                label={mode === "register" ? "Create password" : "Password"}
                value={password}
                onChange={setPassword}
                autoComplete={mode === "register" ? "new-password" : "current-password"}
              />
              {mode === "register" && (
                <PasswordField
                  label="Confirm password"
                  value={confirmPassword}
                  onChange={setConfirmPassword}
                  autoComplete="new-password"
                />
              )}
            </>
          )}
          <div className="auth-links">
            <button type="button" className="link-button" onClick={() => setMode(mode === "forgot" ? "login" : "forgot")}>
              {mode === "forgot" ? "Back to login" : "Forgot password?"}
            </button>
          </div>
          <button className="primary-button full-width" disabled={busy}>
            {busy ? "Working..." : mode === "forgot" ? "Send reset link" : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>
      </section>
      <section className="panel proof-card">
        <Metric value="JWT" label="Protected endpoints" />
        <Metric value="WS" label="Live tracking" />
        <Metric value="SOS" label="Emergency workflow" />
      </section>
    </div>
  );
}

function PasswordField({
  label,
  value,
  onChange,
  autoComplete
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete: string;
}) {
  const [visible, setVisible] = useState(false);

  return (
    <label>
      {label}
      <span className="password-wrap">
        <input
          type={visible ? "text" : "password"}
          value={value}
          autoComplete={autoComplete}
          onChange={(event) => onChange(event.target.value)}
          required
          minLength={8}
        />
        <button
          type="button"
          className="eye-button"
          onClick={() => setVisible((current) => !current)}
          aria-label={visible ? "Hide password" : "Show password"}
          title={visible ? "Hide password" : "Show password"}
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M2.4 12s3.5-6 9.6-6 9.6 6 9.6 6-3.5 6-9.6 6-9.6-6-9.6-6Z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        </button>
      </span>
    </label>
  );
}

function Dashboard({
  auth,
  sessions,
  activeSession,
  setActiveSession,
  setSessions,
  setStatus,
  setAuth
}: {
  auth: AuthState;
  sessions: SessionDetail[];
  activeSession: SessionResponse | null;
  setActiveSession: (session: SessionResponse | null) => void;
  setSessions: (sessions: SessionDetail[]) => void;
  setStatus: (value: string) => void;
  setAuth: (auth: AuthState) => void;
}) {
  const [hours, setHours] = useState(24);
  const [sosMessage, setSosMessage] = useState("Responder requested immediate assistance.");

  async function createSession() {
    if (!auth.accessToken) return;
    setStatus("Creating share link");
    try {
      const session = await apiRequest<SessionResponse>(
        "/sessions/start",
        { method: "POST", body: JSON.stringify({ expires_in_hours: hours }) },
        auth.accessToken
      );
      setActiveSession(session);
      await loadSessions(auth.accessToken, setSessions);
      setStatus("Share link created");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not create session");
    }
  }

  async function sendSos() {
    if (!auth.accessToken) return;
    setStatus("Sending SOS");
    try {
      await apiRequest<SosResponse>(
        "/sos",
        {
          method: "POST",
          body: JSON.stringify({
            session_id: activeSession?.session_id ?? null,
            message: sosMessage
          })
        },
        auth.accessToken
      );
      setStatus("SOS recorded");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "SOS failed");
    }
  }

  async function logout() {
    if (auth.refreshToken) {
      await apiRequest<void>("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: auth.refreshToken })
      }).catch(() => undefined);
    }
    setAuth({ accessToken: null, refreshToken: null, user: null });
    setStatus("Signed out");
  }

  return (
    <div className="dashboard-grid">
      <section className="panel command-panel">
        <div className="section-heading">
          <span>Command center</span>
          <h2>Operational dashboard</h2>
        </div>
        <div className="metric-grid">
          <Metric value={String(sessions.length)} label="Sessions created" />
          <Metric value={String(sessions.filter((session) => session.active).length)} label="Active links" />
          <Metric value={activeSession ? formatTime(activeSession.expires_at) : "None"} label="Current expiry" />
        </div>
        <div className="session-builder">
          <label>
            Link duration
            <input
              type="number"
              min="1"
              max="720"
              value={hours}
              onChange={(event) => setHours(Number(event.target.value))}
            />
          </label>
          <button className="primary-button" onClick={createSession}>
            Create expiring share link
          </button>
        </div>
        {activeSession && (
          <div className="share-result">
            <div>
              <span>Share URL</span>
              <strong>{activeSession.share_url}</strong>
            </div>
            <button className="ghost-button" onClick={() => copy(activeSession.share_url, setStatus)}>
              Copy
            </button>
          </div>
        )}
      </section>

      <section className="panel sos-panel">
        <div className="section-heading">
          <span>Emergency</span>
          <h2>SOS escalation</h2>
        </div>
        <textarea value={sosMessage} onChange={(event) => setSosMessage(event.target.value)} />
        <button className="danger-button full-width" onClick={sendSos}>
          Send SOS
        </button>
        <button className="ghost-button full-width" onClick={logout}>
          Sign out
        </button>
      </section>

      <section className="panel session-list">
        <div className="section-heading">
          <span>History</span>
          <h2>Recent sessions</h2>
        </div>
        {sessions.length === 0 ? (
          <p className="muted">No sessions yet. Create one to begin tracking.</p>
        ) : (
          sessions.map((session) => (
            <div className="session-row" key={session.id}>
              <div>
                <strong>{session.id.slice(0, 8)}</strong>
                <span>{formatDate(session.created_at)}</span>
              </div>
              <span className={session.active ? "pill live" : "pill"}>{session.active ? "Active" : "Closed"}</span>
            </div>
          ))
        )}
      </section>
    </div>
  );
}

function ShareDevice({ setStatus }: { setStatus: (value: string) => void }) {
  const [token, setToken] = useState("");
  const [location, setLocation] = useState<LocationResponse | null>(null);

  async function shareLocation() {
    if (!token.trim()) {
      setStatus("Paste a share token first");
      return;
    }
    if (!navigator.geolocation) {
      setStatus("Geolocation is unavailable");
      return;
    }

    setStatus("Requesting GPS permission");
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const update = await apiRequest<LocationResponse>(`/track/${token.trim()}/location`, {
            method: "POST",
            body: JSON.stringify({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
              accuracy: position.coords.accuracy
            })
          });
          setLocation(update);
          setStatus("Location shared");
        } catch (error) {
          setStatus(error instanceof Error ? error.message : "Could not share location");
        }
      },
      () => setStatus("Location permission denied"),
      { enableHighAccuracy: true, timeout: 15000 }
    );
  }

  return (
    <section className="panel share-device">
      <div className="section-heading">
        <span>Share device</span>
        <h2>Send current GPS position</h2>
      </div>
      <label>
        Share token
        <input value={token} onChange={(event) => setToken(event.target.value)} placeholder="Paste secure token" />
      </label>
      <button className="primary-button full-width" onClick={shareLocation}>
        Share current location
      </button>
      {location && <LocationCard location={location} />}
    </section>
  );
}

function LiveMonitor({
  locations,
  setLocations,
  setStatus
}: {
  locations: LocationResponse[];
  setLocations: (locations: LocationResponse[]) => void;
  setStatus: (value: string) => void;
}) {
  const [token, setToken] = useState("");
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!connected || !token.trim()) {
      return;
    }
    const socket = new WebSocket(getWebSocketUrl(`/ws/track/${token.trim()}`));
    socket.onopen = () => setStatus("Live monitor connected");
    socket.onmessage = (event) => {
      const update = JSON.parse(event.data) as LocationResponse;
      setLocations([update, ...locations].slice(0, 12));
    };
    socket.onclose = () => setStatus("Live monitor disconnected");
    return () => socket.close();
  }, [connected, token]);

  async function loadLatest() {
    if (!token.trim()) return;
    try {
      const latest = await apiRequest<LocationResponse>(`/track/${token.trim()}`);
      setLocations([latest, ...locations].slice(0, 12));
      setStatus("Latest location loaded");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No location yet");
    }
  }

  return (
    <div className="monitor-grid">
      <section className="panel monitor-control">
        <div className="section-heading">
          <span>Live monitor</span>
          <h2>Watch shared movement</h2>
        </div>
        <label>
          Share token
          <input value={token} onChange={(event) => setToken(event.target.value)} placeholder="Paste secure token" />
        </label>
        <div className="button-row">
          <button className="primary-button" onClick={loadLatest}>
            Load latest
          </button>
          <button className={connected ? "danger-button" : "ghost-button"} onClick={() => setConnected(!connected)}>
            {connected ? "Disconnect" : "Connect live"}
          </button>
        </div>
      </section>
      <section className="panel feed-panel">
        {locations.length === 0 ? (
          <p className="muted">Location updates will appear here.</p>
        ) : (
          locations.map((location) => <LocationCard key={location.id} location={location} />)
        )}
      </section>
    </div>
  );
}

function LocationCard({ location }: { location: LocationResponse }) {
  const mapsUrl = `https://www.google.com/maps?q=${location.latitude},${location.longitude}`;
  return (
    <article className="location-card">
      <div>
        <strong>
          {location.latitude.toFixed(5)}, {location.longitude.toFixed(5)}
        </strong>
        <span>{location.address ?? "Address enrichment pending"}</span>
        <small>{formatDate(location.created_at)}</small>
      </div>
      <a href={mapsUrl} target="_blank" rel="noreferrer">
        Map
      </a>
    </article>
  );
}

function MapPreview({ locations }: { locations: LocationResponse[] }) {
  const latest = locations[0];
  return (
    <div className="map-preview" aria-label="Map preview">
      <div className="map-route" />
      <div className="pin pin-one" />
      <div className="pin pin-two" />
      <div className="pin pin-three" />
      <div className="map-readout">
        <span>Live coordinate</span>
        <strong>{latest ? `${latest.latitude.toFixed(4)}, ${latest.longitude.toFixed(4)}` : "Waiting for signal"}</strong>
      </div>
    </div>
  );
}

function BrandStatus({ user, isAuthenticated }: { user: UserResponse | null; isAuthenticated: boolean }) {
  return (
    <div className="brand-status">
      <div className="brand-mark">LT</div>
      <div>
        <strong>{isAuthenticated ? user?.name ?? "Responder" : "Guest mode"}</strong>
        <span>{isAuthenticated ? user?.email : "Authentication required"}</span>
      </div>
    </div>
  );
}

function Metric({ value, label }: { value: string; label: string }) {
  return (
    <div className="metric">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

async function loadSessions(accessToken: string, setSessions: (sessions: SessionDetail[]) => void) {
  const sessions = await apiRequest<SessionDetail[]>("/sessions", {}, accessToken).catch(() => []);
  setSessions(sessions);
}

function copy(value: string, setStatus: (value: string) => void) {
  navigator.clipboard
    .writeText(value)
    .then(() => setStatus("Copied to clipboard"))
    .catch(() => setStatus("Copy failed"));
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function readAuth(): AuthState {
  const rawValue = localStorage.getItem("location-tracker-auth");
  if (!rawValue) {
    return { accessToken: null, refreshToken: null, user: null };
  }
  try {
    return JSON.parse(rawValue) as AuthState;
  } catch {
    return { accessToken: null, refreshToken: null, user: null };
  }
}

function persistAuth(auth: AuthState) {
  localStorage.setItem("location-tracker-auth", JSON.stringify(auth));
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
