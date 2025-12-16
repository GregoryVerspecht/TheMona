export async function apiPost<T = unknown>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`POST ${path} -> ${r.status} ${text}`);
  }

  // als je soms empty responses hebt:
  const ct = r.headers.get("content-type") ?? "";
  if (!ct.includes("application/json")) return undefined as T;

  return (await r.json()) as T;
}

export async function apiGet<T = unknown>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`GET ${path} -> ${r.status}`);
  return (await r.json()) as T;
}
