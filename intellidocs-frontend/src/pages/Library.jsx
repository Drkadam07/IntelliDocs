import { useEffect, useRef, useState } from "react";
import { FileText, Trash2, Upload } from "lucide-react";
import { api } from "../api";
import { useApp } from "../store.jsx";

const size = (b) => (b > 1e6 ? (b / 1e6).toFixed(1) + " MB" : Math.max(1, Math.round(b / 1e3)) + " KB");

export default function Library() {
  const [docs, setDocs] = useState(null);
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const input = useRef(null);
  const { toast } = useApp();
  const load = () => api.listDocs().then(setDocs);
  useEffect(() => { load(); }, []);

  const upload = async (files) => {
    const f = files[0];
    if (!f) return;
    if (f.type !== "application/pdf") return setErr("Only PDF files are supported.");
    setErr(""); setBusy(true);
    try { await api.uploadDoc(f); await load(); toast(`${f.name} uploaded.`); } catch (e) { setErr(e.message); }
    setBusy(false);
  };

  return (
    <div className="page">
      <h1>Library</h1>
      <p className="muted">Documents you upload here are searchable in every chat.</p>
      <div
        className={"drop" + (drag ? " over" : "")}
        onClick={() => input.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); upload(e.dataTransfer.files); }}
      >
        <Upload size={20} />
        <b>{busy ? "Processing PDF…" : "Drop a PDF here, or click to choose"}</b>
        <input ref={input} type="file" accept="application/pdf" hidden onChange={(e) => { upload(e.target.files); e.target.value = ""; }} />
      </div>
      {err && <p className="error">{err}</p>}
      <ul className="docs">
        {docs?.length === 0 && <li className="muted pad">No documents yet. Upload your first PDF above.</li>}
        {docs?.map((d) => (
          <li key={d.id}>
            <FileText size={18} />
            <span><b>{d.name}</b><small>{size(d.size)} · {new Date(d.created).toLocaleDateString()}</small></span>
            <button className="icon" title="Delete document" onClick={async () => { try { await api.deleteDoc(d.id); load(); toast("Document deleted."); } catch (e) { toast(e.message, "error"); } }}><Trash2 size={16} /></button>
          </li>
        ))}
      </ul>
    </div>
  );
}
