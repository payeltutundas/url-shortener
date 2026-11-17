import { useCallback, useEffect, useState } from "react";
import ShortenForm from "./ShortenForm.jsx";
import LinksTable from "./LinksTable.jsx";
import { fetchLinks } from "./api.js";

const REFRESH_MS = 10000; // refresh the table every 10 seconds

export default function App() {
  const [links, setLinks] = useState([]);
  const [loadError, setLoadError] = useState("");

  const loadLinks = useCallback(async () => {
    try {
      setLinks(await fetchLinks());
      setLoadError("");
    } catch (err) {
      setLoadError(err.message);
    }
  }, []);

  // Load once, then keep refreshing on a timer
  useEffect(() => {
    loadLinks();
    const timer = setInterval(loadLinks, REFRESH_MS);
    return () => clearInterval(timer);
  }, [loadLinks]);

  return (
    <main className="container">
      <header>
        <h1>URL Shortener</h1>
        <p className="subtitle">Paste a long link and get a short one.</p>
      </header>

      <ShortenForm onCreated={loadLinks} />

      <section className="card">
        <h2>Your links</h2>
        {loadError && <p className="error">{loadError}</p>}
        <LinksTable links={links} />
      </section>
    </main>
  );
}
