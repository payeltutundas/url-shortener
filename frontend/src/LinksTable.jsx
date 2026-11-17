import { useState } from "react";

function formatDate(value) {
  return new Date(value).toLocaleString();
}

// A button that copies the short link and briefly says "Copied!"
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      window.prompt("Copy this link:", text);
    }
  }

  return (
    <button type="button" className="small" onClick={copy}>
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}

export default function LinksTable({ links }) {
  if (links.length === 0) {
    return <p className="muted">No links yet. Create your first one above.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Short link</th>
            <th>Original URL</th>
            <th>Clicks</th>
            <th>Expiry / status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {links.map((link) => (
            <tr key={link.code}>
              <td className="short">
                <a href={link.short_url} target="_blank" rel="noreferrer">
                  {link.short_url}
                </a>{" "}
                <CopyButton text={link.short_url} />
              </td>
              <td className="original" title={link.original_url}>
                {link.original_url}
              </td>
              <td>{link.clicks}</td>
              <td>
                <span className={`badge ${link.status}`}>{link.status}</span>
                {link.expires_at && (
                  <div className="muted small-text">
                    {link.status === "expired" ? "Expired " : "Expires "}
                    {formatDate(link.expires_at)}
                  </div>
                )}
              </td>
              <td>{formatDate(link.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
