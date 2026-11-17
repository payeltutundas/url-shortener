import { useState } from "react";
import { createLink } from "./api.js";

export default function ShortenForm({ onCreated }) {
  const [url, setUrl] = useState("");
  const [alias, setAlias] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [error, setError] = useState("");
  const [created, setCreated] = useState(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setCreated(null);
    setBusy(true);
    try {
      const link = await createLink({ url, alias: alias.trim(), expiresAt });
      setCreated(link);
      setUrl("");
      setAlias("");
      setExpiresAt("");
      onCreated(); // tell the page to reload the table
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h2>Create a short link</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Long URL
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/a/very/long/page"
            required
          />
        </label>

        <div className="row">
          <label>
            Custom alias (optional)
            <input
              type="text"
              value={alias}
              onChange={(e) => setAlias(e.target.value)}
              placeholder="my-offer"
            />
          </label>
          <label>
            Expires at (optional)
            <input
              type="datetime-local"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
            />
          </label>
        </div>

        <button type="submit" disabled={busy}>
          {busy ? "Creating..." : "Shorten"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
      {created && (
        <p className="success">
          Your short link:{" "}
          <a href={created.short_url} target="_blank" rel="noreferrer">
            {created.short_url}
          </a>
        </p>
      )}
    </section>
  );
}
