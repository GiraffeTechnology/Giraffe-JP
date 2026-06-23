/**
 * openclaw-aivan — OpenClaw channel-event-handler plugin
 *
 * Intercepts every inbound channel event (WeChat, Email, WhatsApp, etc.)
 * BEFORE the built-in LLM layer and forwards it directly to the AIVAN
 * procurement AI over HTTP.  The response is returned to OpenClaw verbatim
 * so OpenClaw can deliver outbound messages through the originating channel.
 *
 * Required env var:  AIVAN_BASE_URL  (e.g. http://localhost:8000)
 * Optional env var:  GIRAFFE_API_BASE  (alias for AIVAN_BASE_URL)
 */

const AIVAN_BASE_URL =
  process.env.AIVAN_BASE_URL ||
  process.env.GIRAFFE_API_BASE ||
  "http://localhost:8000";

const SKILL_INVOKE_URL = `${AIVAN_BASE_URL}/api/skill/invoke`;

const TIMEOUT_MS = 30_000;

// ─── Types ─────────────────────────────────────────────────────────────────────

interface ChannelEvent {
  source: string;
  channel: string;
  channel_account_id: string;
  conversation_id: string;
  sender_id: string;
  sender_display_name?: string;
  message_text: string;
  message_type?: string;
  attachments?: unknown[];
  timestamp?: string;
  project_id?: string | null;
  procurement_edge_id?: string | null;
  actor_id?: string | null;
  role_context?: string | null;
  mode?: string | null;
}

interface AivanResponse {
  ok: boolean;
  reply_text?: string;
  outbound_messages?: Array<{ channel: string; recipient_id: string; text: string }>;
  status?: string;
  [key: string]: unknown;
}

// ─── AIVAN call ──────────────────────────────────────────────────────────────────

async function callAivan(event: ChannelEvent): Promise<AivanResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(SKILL_INVOKE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(event),
      signal: controller.signal,
    });

    if (!res.ok) {
      const body = await res.text().catch(() => "(no body)");
      return {
        ok: false,
        error: `AIVAN returned HTTP ${res.status}: ${body}`,
        status: "aivan_error",
      };
    }

    return (await res.json()) as AivanResponse;
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return {
      ok: false,
      error: `AIVAN unreachable: ${msg}`,
      status: "aivan_unreachable",
    };
  } finally {
    clearTimeout(timer);
  }
}

// ─── Plugin export ──────────────────────────────────────────────────────────────

/**
 * OpenClaw plugin manifest.
 *
 * OpenClaw loads this object when it finds `openclaw.plugin = true` in
 * package.json and requires the `main` entry point.
 *
 * The `channel-event-handler` function is called for every inbound event
 * before the built-in agent/LLM pipeline runs.  Returning a non-null value
 * short-circuits the LLM and delivers the return value to the channel.
 */
const plugin = {
  name: "openclaw-aivan",
  version: "1.0.0",
  description:
    "Routes channel events directly to AIVAN procurement AI — no LLM pass-through",

  /**
   * channel-event-handler
   *
   * Called by the OpenClaw Gateway for every inbound channel message.
   * Returning a truthy object prevents the built-in LLM from handling
   * the message.
   *
   * @param event   - normalized OpenClaw channel event
   * @param context - OpenClaw runtime context (gateway config, logger, etc.)
   */
  "channel-event-handler": async (
    event: ChannelEvent,
    _context?: unknown
  ): Promise<AivanResponse> => {
    return callAivan(event);
  },
};

export = plugin;
