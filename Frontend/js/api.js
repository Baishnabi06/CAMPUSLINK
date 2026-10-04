const API_BASE_URL = "http://127.0.0.1:8000";

const TOKEN_KEY = "campuslink_token";
const USER_KEY = "campuslink_user";

// Routes used before the user is logged in. A 401 from these means "wrong
// credentials", not "expired session", so we must not redirect/reload.
const PUBLIC_AUTH_PATHS = [
  "/api/auth/login",
  "/api/auth/register",
  "/api/auth/request-otp",
  "/api/auth/verify-otp",
];

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Central fetch wrapper. Attaches the JWT automatically, JSON-encodes
 * object bodies, and redirects to login on 401 (expired/invalid token).
 */
async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = { ...options, headers };
  if (config.body && typeof config.body !== "string") {
    config.body = JSON.stringify(config.body);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, config);

  if (response.status === 401 && !PUBLIC_AUTH_PATHS.includes(path)) {
    clearAuth();
    window.location.href = "login.html";
    return;
  }

  const data = await response.json();
  if (!response.ok || data.success === false) {
    throw new Error(data.message || data.detail || "Request failed");
  }
  return data;
}


/**
 * For file uploads. Does NOT set Content-Type — the browser sets the
 * correct multipart boundary automatically when you pass a FormData body.
 */
async function apiUpload(path, formData) {
  const token = getToken();
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (response.status === 401) {
    clearAuth();
    window.location.href = "login.html";
    return;
  }

  const data = await response.json();
  if (!response.ok || data.success === false) {
    throw new Error(data.message || data.detail || "Upload failed");
  }
  return data;
}

/** Fetches an authenticated file response without JSON parsing. */
async function apiFetchBlob(path) {
  const token = getToken();
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${path}`, { headers });

  if (response.status === 401) {
    clearAuth();
    window.location.href = "login.html";
    return;
  }

  if (!response.ok) {
    let message = "Failed to retrieve document";
    try {
      const data = await response.json();
      message = data.detail || data.message || message;
    } catch (err) {
      // Keep the default message when the server response is not JSON.
    }
    throw new Error(message);
  }

  return response.blob();
}

/**
 * Theme handling: "light" | "dark" | "system" (default).
 * Runs on every page immediately, since api.js is the first script loaded
 * everywhere — including login.html/register.html, which never call renderShell().
 */
function applyTheme() {
  const theme = localStorage.getItem("campuslink_theme") || "system";
  const root = document.documentElement;
  if (theme === "system") {
    root.removeAttribute("data-theme");
  } else {
    root.setAttribute("data-theme", theme);
  }
}

applyTheme();

if (window.matchMedia) {
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if ((localStorage.getItem("campuslink_theme") || "system") === "system") {
      applyTheme();
    }
  });
}