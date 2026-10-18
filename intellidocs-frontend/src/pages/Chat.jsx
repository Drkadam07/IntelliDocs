import { useEffect, useRef, useState } from "react";
import { useNavigate, useOutletContext, useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { ArrowUp, Check, Copy, Paperclip } from "lucide-react";
import { api } from "../api";
import { useApp } from "../store.jsx";

const SUGGESTIONS = ["Summarize my latest document", "List the key takeaways", "Explain the main formulas"];

function Bubble({ m }) {
  const [copied, setCopied] = useState(false);
  if (m.role === "user") return <div className="msg user">{m.content}</div>;
  return (
    <div className="msg bot">
      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>{String(m.content ?? "")}</ReactMarkdown>
      <button className="icon copy" title="Copy" onClick={() => { navigator.clipboard.writeText(m.content); setCopied(true); setTimeout(() => setCopied(false), 1200); }}>
        {copied ? <Check size={14} /> : <Copy size={14} />}
      </button>
    </div>
  );
}

export default function Chat() {
  const { id } = useParams();
  const nav = useNavigate();
  const { refresh } = useOutletContext();
  const { user, settings, toast } = useApp();
  const [docs, setDocs] = useState([]);
  const [msgs, setMsgs] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");
  const skip = useRef(null);
  const end = useRef(null);
  const file = useRef(null);
  const ta = useRef(null);
  const draft = useRef(null);
  useEffect(() => { api.listDocs().then(setDocs).catch(() => {}); }, []);

  useEffect(() => {
    draft.current = null;
    if (skip.current === id) { skip.current = null; return; }
    setMsgs([]);
    if (!id) return;
    let live = true;
    api.getChat(id).then((c) => { if (live) setMsgs(c.messages || []); }).catch(() => { if (live) nav("/"); });
    return () => { live = false; };
  }, [id]);

  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, busy]);

  // auto refresh: when the tab becomes visible again, re-sync the sidebar and the open chat
  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState !== "visible" || busy) return;
      refresh();
      if (id) api.getChat(id).then((c) => setMsgs(c.messages || [])).catch(() => {});
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [id, busy]);

  const send = async (override) => {
    const message = (override ?? text).trim();
    if (!message || busy) return;
    setText("");
    if (ta.current) ta.current.style.height = "auto";
    setBusy(true);
    setMsgs((m) => [...m, { role: "user", content: message }]);
    try {
      let cid = id || draft.current;
      if (!cid) { cid = String((await api.createChat()).id); draft.current = cid; }
      const r = await api.send(cid, message);
      const reply = r?.reply ?? r?.response ?? r?.message ?? "";
      setMsgs((m) => [...m, { role: "bot", content: String(reply) }]);
      if (!id) { skip.current = cid; nav(`/c/${cid}`, { replace: true }); }
      refresh();
    } catch (e) {
      setMsgs((m) => [...m, { role: "bot", content: `**Couldn't get a reply.** ${e.message}` }]);
    }
    setBusy(false);
  };

  const upload = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setNote(`Processing ${f.name}… this can take 10–20 seconds.`);
    try { const d = await api.uploadDoc(f); setDocs((x) => [d, ...x]); setNote(""); toast(`${f.name} is ready to chat with.`); }
    catch (x) { setNote(""); toast(x.message, "error"); }
    e.target.value = "";
  };

  return (
    <div className="chat">
      <div className="scroll">
        {msgs.length === 0 ? (
          <div className="hero">
            <h1>Hello, {user.name.split(" ")[0]}.</h1>
            <p className="muted">What would you like to know from your documents?</p>
            {docs.length === 0 && <p className="nudge">You haven’t uploaded a document yet. <button className="linklike" onClick={() => file.current.click()}>Upload a PDF</button> to get started.</p>}
            <div className="chips">{(docs.length ? [`Summarize ${docs[0].name}`, ...SUGGESTIONS.slice(1)] : SUGGESTIONS).map((s) => <button key={s} className="chip" onClick={() => send(s)}>{s}</button>)}</div>
          </div>
        ) : (
          <div className="thread">
            {msgs.map((m, i) => <Bubble key={i} m={m} />)}
            {busy && <div className="msg bot dots"><i /><i /><i /></div>}
            <div ref={end} />
          </div>
        )}
      </div>
      <div className="composer-wrap">
        {note && <p className="muted small note">{note}</p>}
        <div className="composer">
          <button className="icon" title="Upload a PDF" onClick={() => file.current.click()}><Paperclip size={18} /></button>
          <input ref={file} type="file" accept="application/pdf" hidden onChange={upload} />
          <textarea
            ref={ta} rows={1} value={text} placeholder="Ask about your documents"
            onChange={(e) => { setText(e.target.value); e.target.style.height = "auto"; e.target.style.height = Math.min(e.target.scrollHeight, 180) + "px"; }}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey && settings.enterToSend) { e.preventDefault(); send(); } }}
          />
          <button className="btn primary round" title="Send" disabled={!text.trim() || busy} onClick={() => send()}><ArrowUp size={18} /></button>
        </div>
      </div>
    </div>
  );
}
