import { Navigate, Route, Routes } from "react-router-dom";
import { useApp } from "./store.jsx";
import Layout from "./components/Layout.jsx";
import Auth, { Verify } from "./pages/Auth.jsx";
import Chat from "./pages/Chat.jsx";
import Library from "./pages/Library.jsx";
import { Profile, Settings } from "./pages/Account.jsx";

function Guard() {
  const { user, ready } = useApp();
  if (!ready) return <div className="center muted">Loading…</div>;
  return user ? <Layout /> : <Navigate to="/login" replace />;
}

export default function App() {
  const { user } = useApp();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Auth mode="login" />} />
      <Route path="/register" element={user ? <Navigate to="/" replace /> : <Auth mode="register" />} />
      <Route path="/verify" element={user ? <Navigate to="/" replace /> : <Verify />} />
      <Route element={<Guard />}>
        <Route path="/" element={<Chat />} />
        <Route path="/c/:id" element={<Chat />} />
        <Route path="/library" element={<Library />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
