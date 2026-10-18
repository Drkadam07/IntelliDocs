import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import { FileText, LogOut, Menu, MessageSquarePlus, PanelLeft, Pencil, Search, Settings as Cog, Trash2 } from "lucide-react";
import { api } from "../api";
import { useApp } from "../store.jsx";

const ORDER = ["Today", "Yesterday", "Previous 7 days", "Older"];
const bucket = (t) => {
  if (new Date(t).toDateString() === new Date().toDateString()) return "Today";
  const d = (Date.now() - t) / 864e5;
  return d < 2 ? "Yesterday" : d < 7 ? "Previous 7 days" : "Older";
};

export default function Layout() {
  const { user, logout, toast } = useApp();
  const { id } = useParams();
  const nav = useNavigate();
  const loc = useLocation();
  const [chats, setChats] = useState([]);
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("collapsed") === "1");
  const [edit, setEdit] = useState(null); // {id, title}

  const refresh = () => api.listChats().then(setChats).catch((e) => toast(e.message, "error"));
  useEffect(() => { refresh(); }, []);
  useEffect(() => { setOpen(false); }, [loc.pathname]);
  useEffect(() => { localStorage.setItem("collapsed", collapsed ? "1" : "0"); }, [collapsed]);

  const remove = async (e, cid) => {
    e.preventDefault();
    if (!confirm("Delete this chat?")) return;
    try { await api.deleteChat(cid); toast("Chat deleted."); refresh(); if (String(cid) === id) nav("/"); }
    catch (x) { toast(x.message, "error"); }
  };
  const rename = async () => {
    const t = edit.title.trim();
    if (t) { try { await api.renameChat(edit.id, t); refresh(); } catch (x) { toast(x.message, "error"); } }
    setEdit(null);
  };

  const shown = chats.filter((c) => c.title.toLowerCase().includes(q.toLowerCase()));
  const groups = ORDER.map((g) => [g, shown.filter((c) => bucket(c.updated) === g)]).filter(([, l]) => l.length);

  return (
    <div className={"shell" + (collapsed ? " collapsed" : "")}>
      <aside className={"side" + (open ? " open" : "")}>
        <div className="side-top">
          <div className="brand">IntelliDocs</div>
          <button className="icon hide-mobile" title="Collapse sidebar" onClick={() => setCollapsed(true)}><PanelLeft size={18} /></button>
        </div>
        <NavLink to="/" end className="btn primary wide"><MessageSquarePlus size={16} /> New chat</NavLink>
        <nav className="nav"><NavLink to="/library"><FileText size={16} /> Library</NavLink></nav>
        <label className="search"><Search size={14} /><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search chats" /></label>
        <div className="history">
          {shown.length === 0 && <p className="muted small pad">{q ? "No chats match your search." : "Your chats will appear here."}</p>}
          {groups.map(([g, list]) => (
            <div key={g}>
              <p className="group">{g}</p>
              {list.map((c) => edit?.id === c.id ? (
                <div key={c.id} className="chat-item active">
                  <input autoFocus className="rename" value={edit.title} onChange={(e) => setEdit({ ...edit, title: e.target.value })}
                    onBlur={rename} onKeyDown={(e) => { if (e.key === "Enter") rename(); if (e.key === "Escape") setEdit(null); }} />
                </div>
              ) : (
                <NavLink key={c.id} to={`/c/${c.id}`} className="chat-item">
                  <span>{c.title}</span>
                  <button className="icon" title="Rename chat" onClick={(e) => { e.preventDefault(); setEdit({ id: c.id, title: c.title }); }}><Pencil size={13} /></button>
                  <button className="icon" title="Delete chat" onClick={(e) => remove(e, c.id)}><Trash2 size={13} /></button>
                </NavLink>
              ))}
            </div>
          ))}
        </div>
        <div className="side-foot">
          <NavLink to="/profile" className="me">
            <span className="avatar">{user.name?.[0]?.toUpperCase() || "U"}</span>
            <span><b>{user.name}</b><small>@{user.username}</small></span>
          </NavLink>
          <NavLink to="/settings" className="icon" title="Settings"><Cog size={16} /></NavLink>
          <button className="icon" title="Sign out" onClick={logout}><LogOut size={16} /></button>
        </div>
      </aside>
      {open && <div className="scrim" onClick={() => setOpen(false)} />}
      <main className="main">
        <button className="icon menu-btn" onClick={() => (window.innerWidth <= 800 ? setOpen(true) : setCollapsed(false))} aria-label="Open sidebar"><Menu size={20} /></button>
        <Outlet context={{ refresh }} />
      </main>
    </div>
  );
}
