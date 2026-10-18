// Talks to FastAPI. Dev: Vite proxies /api -> http://localhost:8000. Prod: set VITE_API_URL.
const BASE = import.meta.env.VITE_API_URL || "/api";

async function req(method, path, body) {
  const token = localStorage.getItem("token");
  const isForm = body instanceof FormData;
  const res = await fetch(BASE + path, {
    method,
    headers: {
      ...(body && !isForm ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && token && !path.startsWith("/auth")) {
      localStorage.removeItem("token");
      window.dispatchEvent(new Event("auth:expired"));
    }
    const d = data.detail;
    const err = new Error(
      Array.isArray(d)
        ? d.map((e) => e.msg).join(". ")
        : d || "Something went wrong. Try again.",
    );
    err.status = res.status;
    throw err;
  }
  return data;
}

export const needsVerify = (e) => e.status === 403 || /verify/i.test(e.message);

export const api = {
  register: (b) => req("POST", "/auth/register", b), // account stays unverified: token is ignored until OTP is confirmed
  verifyOtp: async (b) => {
    const r = await req("POST", "/auth/verify-otp", b);
    localStorage.setItem("token", r.token);
    return r;
  },
  resendOtp: (email) => req("POST", "/auth/resend-otp", { email }),
  login: async (b) => {
    const r = await req("POST", "/auth/login", b);
    localStorage.setItem("token", r.token);
    return r.user;
  },
  logout: () => localStorage.removeItem("token"),
  me: () => req("GET", "/me"),
  updateMe: (b) => req("PATCH", "/me", b),

  listChats: () => req("GET", "/chats"),
  createChat: () => req("POST", "/chats", {}),
  getChat: (id) => req("GET", `/chats/${id}`),
  renameChat: (id, title) => req("PATCH", `/chats/${id}`, { title }),
  deleteChat: (id) => req("DELETE", `/chats/${id}`),
  send: (id, message) => req("POST", `/chats/${id}/messages`, { message }),

  listDocs: () => req("GET", "/documents"),
  uploadDoc: (file) => {
    const fd = new FormData();
    fd.append("file", file);
    return req("POST", "/documents", fd);
  },
  deleteDoc: (id) => req("DELETE", `/documents/${id}`),
  clearAll: () => req("POST", "/clear", {}),
};
