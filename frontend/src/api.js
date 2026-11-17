// Small helpers that talk to the back end. All calls start with /api.

// Turn an error response from the API into one readable sentence.
async function readError(response) {
  try {
    const body = await response.json();
    const detail = body.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      // FastAPI validation errors: take the first message
      const msg = detail[0].msg || "Invalid input";
      return msg.replace(/^Value error, /, "");
    }
  } catch {
    // The body was not JSON: fall through
  }
  return `Something went wrong (error ${response.status})`;
}

export async function createLink({ url, alias, expiresAt }) {
  const body = { url };
  if (alias) body.alias = alias;
  // The date-time input gives local time; toISOString converts it to UTC.
  if (expiresAt) body.expires_at = new Date(expiresAt).toISOString();

  let response;
  try {
    response = await fetch("/api/links", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error("Cannot reach the server. Is the back end running?");
  }
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function fetchLinks() {
  let response;
  try {
    response = await fetch("/api/links");
  } catch {
    throw new Error("Cannot reach the server. Is the back end running?");
  }
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}
