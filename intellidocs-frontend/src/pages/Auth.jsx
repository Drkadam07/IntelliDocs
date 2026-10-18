import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Eye, EyeOff, FileText, MessageSquareText, ShieldCheck } from "lucide-react";
import { api, needsVerify } from "../api";
import { useApp } from "../store.jsx";

const pending = { get: () => sessionStorage.getItem("pendingEmail") || "", set: (e) => sessionStorage.setItem("pendingEmail", e) };

function Shell({ children }) {
  return (
    <div className="auth">
      <div className="auth-art">
        <div className="brand">IntelliDocs</div>
        <div>
          <h1>Ask your documents anything.</h1>
          <ul className="points">
            <li><FileText size={18} /> Upload lecture notes, papers or manuals as PDFs.</li>
            <li><MessageSquareText size={18} /> Chat with them and get answers from your own pages.</li>
            <li><ShieldCheck size={18} /> Your library stays private to your account.</li>
          </ul>
        </div>
      </div>
      {children}
    </div>
  );
}

export default function Auth({ mode }) {
  const { login } = useApp();
  const nav = useNavigate();
  const isReg = mode === "register";
  const [f, setF] = useState({ name: "", username: "", email: "", password: "" });
  const [show, setShow] = useState(false);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    if (isReg && f.password.length < 8) return setErr("Use at least 8 characters for your password.");
    setBusy(true);
    try {
      if (isReg) { await api.register(f); pending.set(f.email); nav("/verify"); }
      else await login({ email: f.email, password: f.password });
    } catch (x) {
      if (!isReg && needsVerify(x)) { pending.set(f.email); api.resendOtp(f.email).catch(() => {}); nav("/verify"); }
      else setErr(x.message);
    }
    setBusy(false);
  };

  return (
    <Shell>
      <form className="auth-card" onSubmit={submit}>
        <h2>{isReg ? "Create your account" : "Welcome back"}</h2>
        {isReg && <>
          <label>Full name<input required value={f.name} onChange={set("name")} autoComplete="name" /></label>
          <label>Username<input required value={f.username} onChange={set("username")} autoComplete="username" /></label>
        </>}
        <label>Email<input required type="email" value={f.email} onChange={set("email")} autoComplete="email" /></label>
        <label>Password
          <span className="pw">
            <input required type={show ? "text" : "password"} value={f.password} onChange={set("password")} autoComplete={isReg ? "new-password" : "current-password"} />
            <button type="button" className="icon" aria-label={show ? "Hide password" : "Show password"} onClick={() => setShow(!show)}>{show ? <EyeOff size={16} /> : <Eye size={16} />}</button>
          </span>
        </label>
        {err && <p className="error" role="alert">{err}</p>}
        <button className="btn primary wide" disabled={busy}>{busy ? "Please wait…" : isReg ? "Create account" : "Sign in"}</button>
        <p className="muted small center-t">
          {isReg ? "Already have an account? " : "New to IntelliDocs? "}
          <Link to={isReg ? "/login" : "/register"}>{isReg ? "Sign in" : "Create an account"}</Link>
        </p>
      </form>
    </Shell>
  );
}

export function Verify() {
  const { verify, toast } = useApp();
  const email = pending.get();
  const [otp, setOtp] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [cool, setCool] = useState(30);
  useEffect(() => { if (cool > 0) { const t = setTimeout(() => setCool(cool - 1), 1000); return () => clearTimeout(t); } }, [cool]);
  if (!email) return <Navigate to="/login" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try { await verify({ email, otp }); sessionStorage.removeItem("pendingEmail"); }
    catch (x) { setErr(x.message); }
    setBusy(false);
  };
  const resend = async () => {
    try { await api.resendOtp(email); setCool(30); toast("A new code is on its way."); }
    catch (x) { toast(x.message, "error"); }
  };

  return (
    <Shell>
      <form className="auth-card" onSubmit={submit}>
        <h2>Check your email</h2>
        <p className="muted">Enter the 6-digit code sent to <b>{email}</b>.</p>
        <input className="otp" inputMode="numeric" autoComplete="one-time-code" maxLength={6} required autoFocus
          value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))} placeholder="000000" aria-label="Verification code" />
        {err && <p className="error" role="alert">{err}</p>}
        <button className="btn primary wide" disabled={busy || otp.length !== 6}>{busy ? "Verifying…" : "Verify and continue"}</button>
        <p className="muted small center-t">
          Didn’t get it? <button type="button" className="linklike" disabled={cool > 0} onClick={resend}>{cool > 0 ? `Resend in ${cool}s` : "Resend code"}</button>
          {" · "}<Link to="/login">Back to sign in</Link>
        </p>
      </form>
    </Shell>
  );
}
