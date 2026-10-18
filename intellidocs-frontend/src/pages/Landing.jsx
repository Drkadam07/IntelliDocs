import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, FileText, History, Lock, MessageSquareText, Moon, Sigma, ShieldCheck, Upload, Sparkles } from "lucide-react";
import { useApp } from "../store.jsx";

const DEMO = [
  { q: "What is thrashing in operating systems?", a: "Thrashing happens when the system spends more time swapping pages between RAM and disk than running programs. It usually means the working set no longer fits in memory." },
  { q: "List the four conditions for deadlock.", a: "Mutual exclusion, hold and wait, no preemption, and circular wait. Break any one of them and deadlock cannot occur." },
  { q: "Summarize unit 3 in two lines.", a: "Unit 3 covers paging, segmentation and virtual memory. The key idea is keeping each process’s working set in RAM to avoid page faults." },
];
const IDEAS = ["Summarize chapter 3", "Explain this formula", "Key takeaways from the paper", "Compare the two methods", "Define every term in unit 2", "Make revision notes", "What does the syllabus cover?"];
const FEATURES = [
  [MessageSquareText, "Ask in plain language", "Type a question and get an answer grounded in the pages you uploaded."],
  [FileText, "Your own library", "Keep lecture notes, papers and manuals in one place and chat across all of them."],
  [Sigma, "Math and formatting", "Formulas, lists and code render cleanly, so technical answers stay readable."],
  [History, "Searchable history", "Every conversation is saved, grouped by date, and easy to rename or find again."],
  [Moon, "Light and dark", "Pick a theme or follow your system. The whole app adapts."],
  [ShieldCheck, "Private by default", "Email-verified accounts, and your documents are only available to you."],
];
const STEPS = [
  [Upload, "Upload a PDF", "Drop in a document. It is read and indexed in a few seconds."],
  [MessageSquareText, "Ask a question", "Chat like you would with a tutor who has read everything."],
  [Sparkles, "Get a clear answer", "Reply with the point you need, without scrolling through pages."],
];

function Demo() {
  const [i, setI] = useState(0);
  const [phase, setPhase] = useState("ask");
  const [n, setN] = useState(0);
  const d = DEMO[i];
  useEffect(() => {
    let t;
    if (phase === "ask") t = setTimeout(() => setPhase("think"), 900);
    else if (phase === "think") t = setTimeout(() => setPhase("type"), 1100);
    else if (n < d.a.length) t = setTimeout(() => setN(n + 2), 22);
    else t = setTimeout(() => { setI((i + 1) % DEMO.length); setN(0); setPhase("ask"); }, 3200);
    return () => clearTimeout(t);
  }, [phase, n, i]);
  return (
    <div className="demo" aria-hidden="true">
      <div className="demo-bar"><i /><i /><i /><span>Operating_Systems_Lecture_3.pdf</span></div>
      <div className="demo-body">
        <div className="msg user pop" key={"q" + i}>{d.q}</div>
        {phase !== "ask" && (
          <div className="msg bot pop" key={"a" + i}>
            {phase === "think" ? <span className="dots inline"><i /><i /><i /></span> : <>{d.a.slice(0, n)}<span className="caret" /></>}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Landing() {
  const { user } = useApp();
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: 0.15 });
    document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
  const cta = user ? <Link to="/" className="btn primary">Open app <ArrowRight size={16} /></Link> : <Link to="/register" className="btn primary">Get started free <ArrowRight size={16} /></Link>;

  return (
    <div className="land">
      <header className="l-nav">
        <span className="brand">IntelliDocs</span>
        <nav><a href="#features">Features</a><a href="#how">How it works</a></nav>
        <div className="row">{!user && <Link to="/login" className="btn">Sign in</Link>}{cta}</div>
      </header>

      <section className="l-hero">
        <div className="blob b1" /><div className="blob b2" />
        <div className="l-copy">
          <p className="eyebrow rise" style={{ "--d": "0s" }}><Sparkles size={14} /> Chat with your PDFs</p>
          <h1 className="rise" style={{ "--d": ".08s" }}>Your documents,<br /><em>answered.</em></h1>
          <p className="lede rise" style={{ "--d": ".16s" }}>Upload lecture notes, papers or manuals. Ask a question and get an answer from your own pages, in seconds.</p>
          <div className="row rise" style={{ "--d": ".24s" }}>{cta}<a href="#how" className="btn">See how it works</a></div>
          <p className="muted small rise" style={{ "--d": ".32s" }}><Lock size={13} /> Free to try. Your library stays private.</p>
        </div>
        <div className="l-visual rise" style={{ "--d": ".2s" }}>
          <span className="float f1"><FileText size={14} /> Syllabus_2026.pdf</span>
          <span className="float f2"><FileText size={14} /> Compiler_Notes.pdf</span>
          <Demo />
          <span className="float f3"><FileText size={14} /> DBMS_Unit_2.pdf</span>
        </div>
      </section>

      <div className="marquee" aria-hidden="true"><div className="track">{[...IDEAS, ...IDEAS].map((t, i) => <span key={i}>{t}</span>)}</div></div>

      <section id="features" className="l-sec">
        <h2 className="reveal">Everything you need to study smarter</h2>
        <div className="grid">
          {FEATURES.map(([Icon, t, d], i) => (
            <div key={t} className="card reveal" style={{ "--d": `${(i % 3) * 0.08}s` }}><span className="ico"><Icon size={20} /></span><h3>{t}</h3><p className="muted">{d}</p></div>
          ))}
        </div>
      </section>

      <section id="how" className="l-sec alt">
        <h2 className="reveal">From PDF to answer in three steps</h2>
        <ol className="steps">
          {STEPS.map(([Icon, t, d], i) => (
            <li key={t} className="reveal" style={{ "--d": `${i * 0.12}s` }}><span className="num">{i + 1}</span><Icon size={22} /><h3>{t}</h3><p className="muted">{d}</p></li>
          ))}
        </ol>
      </section>

      <section className="l-cta reveal">
        <h2>Ready to ask your first question?</h2>
        <p>Create an account, upload a PDF, and start chatting.</p>
        {cta}
      </section>
      <footer className="l-foot"><span className="brand">IntelliDocs</span><span className="muted small">Built for students and curious readers.</span></footer>
    </div>
  );
}
