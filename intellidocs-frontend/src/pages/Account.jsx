import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../store.jsx";

export function Profile() {
  const { user, updateUser } = useApp();
  const [f, setF] = useState({ name: user.name, username: user.username, email: user.email });
  const [msg, setMsg] = useState({ ok: true, t: "" });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const save = async (e) => {
    e.preventDefault();
    try { await updateUser(f); setMsg({ ok: true, t: "Profile saved." }); }
    catch (x) { setMsg({ ok: false, t: x.message }); }
  };
  return (
    <div className="page narrow">
      <h1>Profile</h1>
      <div className="profile-head"><span className="avatar lg">{user.name[0].toUpperCase()}</span><div><b>{user.name}</b><p className="muted small">@{user.username}</p></div></div>
      <form className="form" onSubmit={save}>
        <label>Full name<input required value={f.name} onChange={set("name")} /></label>
        <label>Username<input required value={f.username} onChange={set("username")} /></label>
        <label>Email<input required type="email" value={f.email} onChange={set("email")} /></label>
        <div className="row"><button className="btn primary">Save changes</button>{msg.t && <span className={msg.ok ? "ok small" : "error"}>{msg.t}</span>}</div>
      </form>
    </div>
  );
}

function Toggle({ label, hint, value, onChange }) {
  return (
    <div className="setting">
      <span><b>{label}</b><small>{hint}</small></span>
      <button role="switch" aria-checked={value} className={"switch" + (value ? " on" : "")} onClick={() => onChange(!value)}><i /></button>
    </div>
  );
}

export function Settings() {
  const { settings, setSetting, logout } = useApp();
  const nav = useNavigate();
  const clearAll = async () => {
    if (!confirm("Delete all chats and documents? This can't be undone.")) return;
    await api.clearAll();
    nav("/");
    location.reload();
  };
  return (
    <div className="page narrow">
      <h1>Settings</h1>
      <section>
        <h3>Appearance</h3>
        <div className="seg">
          {["light", "dark", "system"].map((t) => (
            <button key={t} className={settings.theme === t ? "on" : ""} onClick={() => setSetting("theme", t)}>{t[0].toUpperCase() + t.slice(1)}</button>
          ))}
        </div>
      </section>
      <section>
        <h3>Notifications</h3>
        <Toggle label="In-app notifications" hint="Tell me when a document finishes processing." value={settings.notifications} onChange={(v) => setSetting("notifications", v)} />
        <Toggle label="Email digest" hint="A weekly summary of your activity." value={settings.emailDigest} onChange={(v) => setSetting("emailDigest", v)} />
      </section>
      <section>
        <h3>Chat</h3>
        <Toggle label="Press Enter to send" hint="Use Shift+Enter for a new line." value={settings.enterToSend} onChange={(v) => setSetting("enterToSend", v)} />
      </section>
      <section>
        <h3>Account</h3>
        <div className="row"><button className="btn" onClick={logout}>Sign out</button><button className="btn danger" onClick={clearAll}>Delete all chats and documents</button></div>
      </section>
    </div>
  );
}
