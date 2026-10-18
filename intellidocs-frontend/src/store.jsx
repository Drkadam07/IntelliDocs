import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";

const Ctx = createContext(null);
export const useApp = () => useContext(Ctx);
const DEFAULTS = { theme: "system", notifications: true, emailDigest: false, enterToSend: true };

export function Providers({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [settings, setSettings] = useState(() => ({ ...DEFAULTS, ...JSON.parse(localStorage.getItem("settings") || "{}") }));

  useEffect(() => {
    localStorage.setItem("settings", JSON.stringify(settings));
    const mq = matchMedia("(prefers-color-scheme: dark)");
    const apply = () => { document.documentElement.dataset.theme = settings.theme === "dark" || (settings.theme === "system" && mq.matches) ? "dark" : "light"; };
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, [settings]);

  useEffect(() => {
    const expired = () => { setUser(null); toast("Your session expired. Sign in again.", "error"); };
    window.addEventListener("auth:expired", expired);
    api.me().then(setUser).catch(() => localStorage.removeItem("token")).finally(() => setReady(true));
    return () => window.removeEventListener("auth:expired", expired);
  }, []);

  // success toasts respect the "In-app notifications" setting; errors always show
  const toast = (text, type = "ok") => {
    if (type === "ok" && !settings.notifications) return;
    const id = Math.random();
    setToasts((t) => [...t, { id, text, type }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3800);
  };

  const value = {
    user, ready, settings, toast,
    setSetting: (k, v) => setSettings((s) => ({ ...s, [k]: v })),
    login: async (b) => setUser(await api.login(b)),
    verify: async (b) => { await api.verifyOtp(b); setUser(await api.me()); },
    updateUser: async (b) => setUser(await api.updateMe(b)),
    logout: () => { api.logout(); setUser(null); },
  };
  return (
    <Ctx.Provider value={value}>
      {children}
      <div className="toasts" aria-live="polite">{toasts.map((t) => <div key={t.id} className={"toast " + t.type}>{t.text}</div>)}</div>
    </Ctx.Provider>
  );
}
