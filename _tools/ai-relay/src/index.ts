/**
 * Roomi Movers AI relay (Cloudflare Worker).
 *
 * The website chat posts the visitor's recent messages here. This Worker holds the Anthropic API key
 * (a secret, never in the web page), adds the business fact sheet from ./prompt.ts, asks Claude for a short
 * reply and returns { reply }. If the reply ends with [[ESTIMATE]] the website starts its estimate form.
 *
 * Protections: only roomimovers.com may call it, tiny request caps, per-visitor rate limit, optional daily cap,
 * short answers, and no conversation is stored.
 */
import Anthropic from "@anthropic-ai/sdk";
import { SYSTEM } from "./prompt";

export interface Env {
  ANTHROPIC_API_KEY: string;
  /** Claude model id. Default claude-opus-5-5; claude-haiku-5-5 is far cheaper and fine for this job. */
  MODEL?: string;
  /** Comma separated list of site origins allowed to call the relay. */
  ALLOWED_ORIGINS?: string;
  /** Optional KV namespace; when bound, enables a global daily cap across all visitors. */
  RATE_KV?: KVNamespace;
  /** Daily cap on AI replies when RATE_KV is bound. Default 1500. */
  DAILY_CAP?: string;
}

type Role = "user" | "assistant";
interface Turn { role: Role; content: string }

const DEFAULT_ORIGINS = ["https://roomimovers.com", "https://www.roomimovers.com"];
const MAX_BODY_CHARS = 12_000;
const MAX_TURNS = 12;
const MAX_TURN_CHARS = 700;
const PER_VISITOR = 20;               // replies per visitor per window
const WINDOW_MS = 10 * 60 * 1000;     // 10 minutes
const FALLBACK = "I am not able to answer that right now. Please call or text (813) 436-3216 and Kareem will help.";

// Best effort, per Worker instance. The Cloudflare rate-limiting rule described in SETUP.md is the hard limit.
const seen = new Map<string, number[]>();

function json(body: unknown, status: number, extra: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...extra },
  });
}

function tooMany(ip: string): boolean {
  const now = Date.now();
  const hits = (seen.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  if (hits.length >= PER_VISITOR) { seen.set(ip, hits); return true; }
  hits.push(now);
  seen.set(ip, hits);
  if (seen.size > 5000) for (const k of seen.keys()) { seen.delete(k); if (seen.size < 2500) break; }
  return false;
}

async function overDailyCap(env: Env): Promise<boolean> {
  if (!env.RATE_KV) return false;
  const cap = Number(env.DAILY_CAP) || 1500;
  const key = "day:" + new Date().toISOString().slice(0, 10);
  const used = Number((await env.RATE_KV.get(key)) || "0");
  if (used >= cap) return true;
  await env.RATE_KV.put(key, String(used + 1), { expirationTtl: 60 * 60 * 36 });
  return false;
}

/** Keep only well-formed turns, start with the visitor, alternate roles, cap the size. */
function clean(input: unknown): Turn[] | null {
  if (!Array.isArray(input)) return null;
  const out: Turn[] = [];
  for (const item of input.slice(-MAX_TURNS)) {
    if (!item || typeof item !== "object") return null;
    const { role, content } = item as { role?: unknown; content?: unknown };
    if ((role !== "user" && role !== "assistant") || typeof content !== "string") return null;
    const text = content.replace(/\s+/g, " ").trim().slice(0, MAX_TURN_CHARS);
    if (!text) continue;
    const prev = out[out.length - 1];
    if (prev && prev.role === role) prev.content += "\n" + text;
    else out.push({ role, content: text });
  }
  while (out.length && out[0].role !== "user") out.shift();
  if (!out.length || out[out.length - 1].role !== "user") return null;
  return out;
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const origin = req.headers.get("Origin") || "";
    const allowed = env.ALLOWED_ORIGINS ? env.ALLOWED_ORIGINS.split(",").map((s) => s.trim()).filter(Boolean) : DEFAULT_ORIGINS;
    const originOk = allowed.includes(origin);
    const cors: Record<string, string> = originOk
      ? {
          "Access-Control-Allow-Origin": origin,
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
          "Access-Control-Max-Age": "86400",
          Vary: "Origin",
        }
      : {};

    if (req.method === "OPTIONS") return new Response(null, { status: originOk ? 204 : 403, headers: cors });
    if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405, cors);
    if (!originOk) return json({ error: "forbidden" }, 403);
    if (!env.ANTHROPIC_API_KEY) return json({ error: "not_configured" }, 503, cors);

    const ip = req.headers.get("CF-Connecting-IP") || "unknown";
    if (tooMany(ip)) return json({ error: "slow_down" }, 429, { ...cors, "Retry-After": "60" });

    const raw = await req.text();
    if (raw.length > MAX_BODY_CHARS) return json({ error: "too_large" }, 413, cors);
    let body: { messages?: unknown };
    try { body = JSON.parse(raw); } catch { return json({ error: "bad_json" }, 400, cors); }
    const messages = clean(body.messages);
    if (!messages) return json({ error: "bad_messages" }, 400, cors);

    if (await overDailyCap(env)) return json({ reply: FALLBACK }, 200, cors);

    try {
      const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
      const res = await client.messages.create({
        model: env.MODEL || "claude-opus-5-5",
        // Thinking cannot be switched off on Opus 5.5, so leave room for it. Replies are a few sentences.
        max_tokens: 1024,
        system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
        messages,
        output_config: { effort: "low" },
      });
      if (res.stop_reason === "refusal") return json({ reply: FALLBACK }, 200, cors);
      const text = res.content
        .filter((b): b is Anthropic.TextBlock => b.type === "text")
        .map((b) => b.text)
        .join("")
        .trim()
        .slice(0, 900);
      return json({ reply: text || FALLBACK }, 200, cors);
    } catch (err) {
      // Never echo upstream details to the browser; the site falls back to the phone number.
      const status = err instanceof Anthropic.APIError ? err.status : 0;
      console.error("anthropic_error", status);
      return json({ error: "upstream" }, 502, cors);
    }
  },
};
