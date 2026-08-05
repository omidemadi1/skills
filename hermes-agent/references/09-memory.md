<!-- Sections in this file (in order):
  - user-guide/features/memory.md
  - user-guide/features/memory-providers.md
  - user-guide/features/honcho.md
-->


---

# SOURCE: website/docs/user-guide/features/memory.md

---
sidebar_position: 3
title: "Persistent Memory"
description: "How Hermes Agent remembers across sessions — MEMORY.md, USER.md, and session search"
---

# Persistent Memory

Hermes Agent has bounded, curated memory that persists across sessions. This lets it remember your preferences, your projects, your environment, and things it has learned.

## How It Works

Two files make up the agent's memory:

| File | Purpose | Char Limit |
|------|---------|------------|
| **MEMORY.md** | Agent's personal notes — environment facts, conventions, things learned | 2,200 chars (~800 tokens) |
| **USER.md** | User profile — your preferences, communication style, expectations | 1,375 chars (~500 tokens) |

Both are stored in `~/.hermes/memories/` and are injected into the system prompt as a frozen snapshot at session start. The agent manages its own memory via the `memory` tool — it can add, replace, or remove entries.

:::info
Character limits keep memory focused. Memory does **not** auto-compact: when a
write would exceed the limit, the `memory` tool returns an error instead of
silently dropping entries. The agent then makes room itself — consolidating or
removing entries in the same turn before retrying (see [What Happens When Memory
is Full](#what-happens-when-memory-is-full)). Note that `replace` is also bound
by the limit: swapping an entry for a longer one can still overflow, so the new
content must be shortened (or another entry removed) to fit.
:::

## How Memory Appears in the System Prompt

At the start of every session, memory entries are loaded from disk and rendered into the system prompt as a frozen block:

```
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

The format includes:
- A header showing which store (MEMORY or USER PROFILE)
- Usage percentage and character counts so the agent knows capacity
- Individual entries separated by `§` (section sign) delimiters
- Entries can be multiline

**Frozen snapshot pattern:** The system prompt injection is captured once at session start and never changes mid-session. This is intentional — it preserves the LLM's prefix cache for performance. When the agent adds/removes memory entries during a session, the changes are persisted to disk immediately but won't appear in the system prompt until the next session starts. Tool responses always show the live state.

## Memory Tool Actions

The agent uses the `memory` tool with these actions:

- **add** — Add a new memory entry
- **replace** — Replace an existing entry with updated content (uses substring matching via `old_text`)
- **remove** — Remove an entry that's no longer relevant (uses substring matching via `old_text`)

There is no `read` action — memory content is automatically injected into the system prompt at session start. The agent sees its memories as part of its conversation context.

### Substring Matching

The `replace` and `remove` actions use short unique substring matching — you don't need the full entry text. The `old_text` parameter just needs to be a unique substring that identifies exactly one entry:

```python
# If memory contains "User prefers dark mode in all editors"
memory(action="replace", target="memory",
       old_text="dark mode",
       content="User prefers light mode in VS Code, dark mode in terminal")
```

If the substring matches multiple entries, an error is returned asking for a more specific match.

## Two Targets Explained

### `memory` — Agent's Personal Notes

For information the agent needs to remember about the environment, workflows, and lessons learned:

- Environment facts (OS, tools, project structure)
- Project conventions and configuration
- Tool quirks and workarounds discovered
- Completed task diary entries
- Skills and techniques that worked

### `user` — User Profile

For information about the user's identity, preferences, and communication style:

- Name, role, timezone
- Communication preferences (concise vs detailed, format preferences)
- Pet peeves and things to avoid
- Workflow habits
- Technical skill level

## What to Save vs Skip

### Save These (Proactively)

The agent saves automatically — you don't need to ask. It saves when it learns:

- **User preferences:** "I prefer TypeScript over JavaScript" → save to `user`
- **Environment facts:** "This server runs Debian 12 with PostgreSQL 16" → save to `memory`
- **Corrections:** "Don't use `sudo` for Docker commands, user is in docker group" → save to `memory`
- **Conventions:** "Project uses tabs, 120-char line width, Google-style docstrings" → save to `memory`
- **Completed work:** "Migrated database from MySQL to PostgreSQL on 2026-01-15" → save to `memory`
- **Explicit requests:** "Remember that my API key rotation happens monthly" → save to `memory`

### Skip These

- **Trivial/obvious info:** "User asked about Python" — too vague to be useful
- **Easily re-discovered facts:** "Python 3.12 supports f-string nesting" — can web search this
- **Raw data dumps:** Large code blocks, log files, data tables — too big for memory
- **Session-specific ephemera:** Temporary file paths, one-off debugging context
- **Information already in context files:** SOUL.md and AGENTS.md content

## Capacity Management

Memory has strict character limits to keep system prompts bounded:

| Store | Limit | Typical entries |
|-------|-------|----------------|
| memory | 2,200 chars | 8-15 entries |
| user | 1,375 chars | 5-10 entries |

### What Happens When Memory is Full

When you try to add an entry that would exceed the limit, the tool returns an error:

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Consolidate now: use 'replace' to merge overlapping entries into shorter ones or 'remove' stale or less important entries (see current_entries below), then retry this add — all in this turn.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

The agent should then:
1. Read the current entries (shown in the error response)
2. Identify entries that can be removed or consolidated
3. Use `replace` to merge related entries into shorter versions
4. Then `add` the new entry

**Best practice:** When memory is above 80% capacity (visible in the system prompt header), consolidate entries before adding new ones. For example, merge three separate "project uses X" entries into one comprehensive project description entry.

### Practical Examples of Good Memory Entries

**Compact, information-dense entries work best:**

```
# Good: Packs multiple related facts
User runs macOS 14 Sonoma, uses Homebrew, has Docker Desktop and Podman. Shell: zsh with oh-my-zsh. Editor: VS Code with Vim keybindings.

# Good: Specific, actionable convention
Project ~/code/api uses Go 1.22, sqlc for DB queries, chi router. Run tests with 'make test'. CI via GitHub Actions.

# Good: Lesson learned with context
The staging server (10.0.1.50) needs SSH port 2222, not 22. Key is at ~/.ssh/staging_ed25519.

# Bad: Too vague
User has a project.

# Bad: Too verbose
On January 5th, 2026, the user asked me to look at their project which is
located at ~/code/api. I discovered it uses Go version 1.22 and...
```

## Duplicate Prevention

The memory system automatically rejects exact duplicate entries. If you try to add content that already exists, it returns success with a "no duplicate added" message.

## Security Scanning

Memory entries are scanned for injection and exfiltration patterns before being accepted, since they're injected into the system prompt. Content matching threat patterns (prompt injection, credential exfiltration, SSH backdoors) or containing invisible Unicode characters is blocked.

## Session Search

Beyond MEMORY.md and USER.md, the agent can search its past conversations using the `session_search` tool:

- All CLI and messaging sessions are stored in SQLite (`~/.hermes/state.db`) with FTS5 full-text search
- Search queries return actual messages from the DB — no LLM summarization, no truncation
- The agent can find things it discussed weeks ago, even if they're not in its active memory
- The agent can also scroll forward/backward inside any session it finds

```bash
hermes sessions list    # Browse past sessions
```

See [Session Search Tool](/user-guide/sessions#session-search-tool) for the three calling shapes (discovery / scroll / browse) and the response format.

### session_search vs memory

| Feature | Persistent Memory | Session Search |
|---------|------------------|----------------|
| **Capacity** | ~1,300 tokens total | Unlimited (all sessions) |
| **Speed** | Instant (in system prompt) | ~20ms FTS5 query, ~1ms scroll |
| **Cost** | Token cost in every prompt | Free — no LLM calls |
| **Use case** | Key facts always available | Finding specific past conversations |
| **Management** | Manually curated by agent | Automatic — all sessions stored |
| **Token cost** | Fixed per session (~1,300 tokens) | On-demand (searched when needed) |

**Memory** is for critical facts that should always be in context. **Session search** is for "did we discuss X last week?" queries where the agent needs to recall specifics from past conversations.

## Configuration

```yaml
# In ~/.hermes/config.yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
  write_approval: false     # false = write freely (default) | true = require approval
```

## Controlling memory writes (`write_approval`)

By default the agent saves memory freely — including from the background
self-improvement review that runs after a turn. If you'd rather approve saves
first, set `memory.write_approval: true`. It's a simple on/off gate applied to
**both** foreground turns and the background review:

| `write_approval` | Behaviour |
|------------------|-----------|
| `false` (default) | Write freely — the gate is off (the pre-gate behaviour). |
| `true` | Require approval before anything is saved. In the interactive CLI, foreground writes prompt you inline (entries are small enough to read in full). Everywhere else — messaging platforms, scripts, and the background self-improvement review — writes are **staged** for review with `/memory pending`. |

> To turn memory off entirely (not just gate it), set `memory_enabled: false`.

Review staged writes from the CLI or any messaging platform:

```
/memory pending             # list staged memory writes (auto ones tagged [auto])
/memory approve <id>        # apply one (or 'all')
/memory reject <id>         # drop one (or 'all')
/memory approval on         # turn the gate on (or 'off') and persist it
```

This is the answer to "the agent saved a wrong assumption about me": set
`write_approval: true`, and every save — especially the unprompted background
ones — waits for your yes/no before it ever enters your profile.

## Background review notifications (`display.memory_notifications`)

After a turn, the background self-improvement review may quietly save a memory
or update a skill. This is Hermes' consent-aware learning loop: repeated
corrections and durable workflow lessons become compact memory entries or
procedural skills, while `write_approval` can stage those writes for review
before they affect future sessions. By default it surfaces a short
`💾 Memory updated` line in chat so you know it happened. Control how chatty
that is:

```yaml
display:
  memory_notifications: on    # off | on (default) | verbose
```

| Value | Behaviour |
|-------|-----------|
| `off` | No chat notification. The review still runs and still writes — you just don't see a line for it. |
| `on` (default) | Generic line, e.g. `💾 Memory updated`, `💾 Skill 'foo' patched`. |
| `verbose` | Includes a compact preview of what changed, e.g. `💾 Memory ➕ User prefers terse replies` or a `"old" → "new"` skill diff snippet. |

> This only governs the **gateway** chat notification. The review itself, and
> writes to your memory/skill stores, are unaffected by this setting. Set it
> per-platform via `display.platforms.<platform>.memory_notifications`.

## Running the review on a cheaper model (`auxiliary.background_review`)

The review runs on your **main chat model** by default, replaying the
conversation — which is already warm in the prompt cache, so it's cheap cache
reads. On an expensive main model you can run the review on a cheaper model
instead:

```yaml
auxiliary:
  background_review:
    provider: openrouter
    model: google/gemini-3-flash-preview   # auto (default) = main chat model
```

When you point it at a model **different** from your main one, the review runs
there for substantially lower cost (~3–5× in benchmarks). Because a different
model can't reuse your main model's prompt cache anyway, the fork automatically
replays a compact **digest** of the conversation (recent turns verbatim + a
summary of older ones) rather than the full transcript — minimizing what it
writes to the new cache. Capture holds: in testing, memory capture was
identical and skill capture near-identical to the main-model review.

Leave it at `auto` (or set it to your main model) and nothing changes — the
review keeps running on the main model with the full warm-cache replay.

## Controlling skill writes (`skills.write_approval`)

Skills use the same on/off gate, but the review UX differs because a
`SKILL.md` is far too large to read in a chat bubble:

```yaml
skills:
  write_approval: false     # false = write freely (default) | true = require approval
```

When `write_approval: true`, skill writes (create / edit / patch / write_file /
delete) always **stage** regardless of origin. You review the one-line gist
inline, but the full diff stays out-of-band:

```
/skills pending             # list staged skill writes + a one-line gist each
/skills diff <id>           # full unified diff (best viewed in CLI or dashboard)
/skills approve <id>        # apply it (or 'all')
/skills reject <id>         # drop it (or 'all')
/skills approval on         # turn the gate on (or 'off') and persist it
```

On a messaging platform, approve a skill from its gist + metadata, or open
`/skills diff` on the CLI / dashboard / the staged file under
`~/.hermes/pending/skills/<id>.json` when you want to read the whole change.
Full details in [Gating agent skill writes](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval).


## External Memory Providers

For deeper, persistent memory that goes beyond MEMORY.md and USER.md, Hermes ships with 8 external memory provider plugins — including Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, and Supermemory.

External providers run **alongside** built-in memory (never replacing it) and add capabilities like knowledge graphs, semantic search, automatic fact extraction, and cross-session user modeling.

```bash
hermes memory setup      # pick a provider and configure it
hermes memory status     # check what's active
```

See the [Memory Providers](./memory-providers.md) guide for full details on each provider, setup instructions, and comparison.

---

# SOURCE: website/docs/user-guide/features/memory-providers.md

---
sidebar_position: 4
title: "Memory Providers"
description: "External memory provider plugins — Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory"
---

# Memory Providers

Hermes Agent ships with 8 external memory provider plugins that give the agent persistent, cross-session knowledge beyond the built-in MEMORY.md and USER.md. Only **one** external provider can be active at a time — the built-in memory is always active alongside it.

## Quick Start

```bash
hermes memory setup      # interactive picker + configuration
hermes memory status     # check what's active
hermes memory off        # disable external provider
```

You can also select the active memory provider via `hermes plugins` → Provider Plugins → Memory Provider.

Or set manually in `~/.hermes/config.yaml`:

```yaml
memory:
  provider: openviking   # or honcho, mem0, hindsight, holographic, retaindb, byterover, supermemory
```

## How It Works

When a memory provider is active, Hermes automatically:

1. **Injects provider context** into the system prompt (what the provider knows)
2. **Prefetches relevant memories** before each turn (background, non-blocking)
3. **Syncs conversation turns** to the provider after each response
4. **Extracts memories on session end** (for providers that support it)
5. **Mirrors built-in memory writes** to the external provider
6. **Adds provider-specific tools** so the agent can search, store, and manage memories

The built-in memory (MEMORY.md / USER.md) continues to work exactly as before. The external provider is additive.

## Available Providers

### Honcho

AI-native cross-session user modeling with dialectic reasoning, session-scoped context injection, semantic search, and persistent conclusions. Base context now includes the session summary alongside user representation and peer cards, giving the agent awareness of what has already been discussed.

| | |
|---|---|
| **Best for** | Multi-agent systems with cross-session context, user-agent alignment |
| **Requires** | `pip install honcho-ai` + [API key](https://app.honcho.dev) or self-hosted instance |
| **Data storage** | Honcho Cloud or self-hosted |
| **Cost** | Honcho pricing (cloud) / free (self-hosted) |

**Tools (5):** `honcho_profile` (read/update peer card), `honcho_search` (semantic search), `honcho_context` (session context — summary, representation, card, messages), `honcho_reasoning` (LLM-synthesized), `honcho_conclude` (create/delete conclusions)

**Architecture:** Two-layer context injection — a base layer (session summary + representation + peer card, refreshed on `contextCadence`) plus a dialectic supplement (LLM reasoning, refreshed on `dialecticCadence`). The dialectic automatically selects cold-start prompts (general user facts) vs. warm prompts (session-scoped context) based on whether base context exists.

**Three orthogonal config knobs** control cost and depth independently:

- `contextCadence` — how often the base layer refreshes (API call frequency)
- `dialecticCadence` — how often the dialectic LLM fires (LLM call frequency)
- `dialecticDepth` — how many `.chat()` passes per dialectic invocation (1–3, depth of reasoning)

The auto-injected dialectic also scales its reasoning level by query length (longer query → deeper reasoning, capped at `reasoningLevelCap`); see [Query-Adaptive Reasoning Level](./honcho.md#query-adaptive-reasoning-level).

**Setup Wizard:**
```bash
hermes memory setup        # select "honcho" — runs the Honcho-specific post-setup
```

The legacy `hermes honcho setup` command still works (it now redirects to `hermes memory setup`), but is only registered after Honcho is selected as the active memory provider.

**Config:** `$HERMES_HOME/honcho.json` (profile-local) or `~/.honcho/config.json` (global). Resolution order: `$HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`. See the [config reference](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/honcho/README.md) and the [Honcho integration guide](https://docs.honcho.dev/v3/guides/integrations/hermes).

<details>
<summary>Full config reference</summary>

| Key | Default | Description |
|-----|---------|-------------|
| `apiKey` | -- | API key from [app.honcho.dev](https://app.honcho.dev) |
| `baseUrl` | -- | Base URL for self-hosted Honcho |
| `peerName` | -- | User peer identity |
| `aiPeer` | host key | AI peer identity (one per profile) |
| `workspace` | host key | Shared workspace ID |
| `contextTokens` | `null` (uncapped) | Token budget for auto-injected context per turn. Truncates at word boundaries |
| `contextCadence` | `1` | Minimum turns between `context()` API calls (base layer refresh) |
| `dialecticCadence` | `2` | Minimum turns between `peer.chat()` LLM calls. Recommended 1–5. Only applies to `hybrid`/`context` modes |
| `dialecticDepth` | `1` | Number of `.chat()` passes per dialectic invocation. Clamped 1–3. Pass 0: cold/warm prompt, pass 1: self-audit, pass 2: reconciliation |
| `dialecticDepthLevels` | `null` | Optional array of reasoning levels per pass, e.g. `["minimal", "low", "medium"]`. Overrides proportional defaults |
| `dialecticReasoningLevel` | `'low'` | Base reasoning level: `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | When `true`, model can override reasoning level per-call via tool param |
| `dialecticMaxChars` | `600` | Max chars of dialectic result injected into system prompt |
| `recallMode` | `'hybrid'` | `hybrid` (auto-inject + tools), `context` (inject only), `tools` (tools only) |
| `writeFrequency` | `'async'` | When to flush messages: `async` (background thread), `turn` (sync), `session` (batch on end), or integer N |
| `saveMessages` | `true` | Whether to persist messages to Honcho API |
| `observationMode` | `'directional'` | `directional` (all on) or `unified` (shared pool). Override with `observation` object |
| `messageMaxChars` | `25000` | Max chars per message (chunked if exceeded) |
| `dialecticMaxInputChars` | `10000` | Max chars for dialectic query input to `peer.chat()` |
| `sessionStrategy` | `'per-directory'` | `per-directory`, `per-repo`, `per-session`, `global` |
| `pinUserPeer` | `false` | Gateway only. When `true`, every non-agent gateway user collapses to `peerName`; the pin overrides all aliases |
| `userPeerAliases` | `{}` | Gateway only. Maps runtime IDs to peers (`{"7654321": "alice"}`). Many-to-one |
| `runtimePeerPrefix` | `""` | Gateway only. Namespaces unknown runtime IDs (`telegram_7654321`) when no alias matches |

</details>

<details>
<summary>Minimal honcho.json (cloud)</summary>

```json
{
  "apiKey": "your-key-from-app.honcho.dev",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "peerName": "your-name",
      "workspace": "hermes"
    }
  }
}
```

</details>

<details>
<summary>Minimal honcho.json (self-hosted)</summary>

```json
{
  "baseUrl": "http://localhost:8000",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "peerName": "your-name",
      "workspace": "hermes"
    }
  }
}
```

</details>

:::tip Migrating from `hermes honcho`
If you previously used `hermes honcho setup`, your config and all server-side data are intact. Just re-enable through the setup wizard again or manually set `memory.provider: honcho` to reactivate via the new system.
:::

**Multi-peer setup:**

Honcho models conversations as peers exchanging messages — one user peer plus one AI peer per Hermes profile, all sharing a workspace. The workspace is the shared environment: the user peer is global across profiles, each AI peer is its own identity. Every AI peer builds an independent representation / card from its own observations, so a `coder` profile stays code-oriented while a `writer` profile stays editorial against the same user.

The mapping:

| Concept | What it is |
|---------|-----------|
| **Workspace** | Shared environment. All Hermes profiles under one workspace see the same user identity. |
| **User peer** (`peerName`) | The human. Shared across profiles in the workspace. |
| **AI peer** (`aiPeer`) | One per Hermes profile. Host key `hermes` → default; `hermes.<profile>` for others. |
| **Observation** | Per-peer toggles controlling what Honcho models from whose messages. `directional` (default, all four on) or `unified` (single-observer pool). |

### New profile, fresh Honcho peer

```bash
hermes profile create coder --clone
```

`--clone` creates a `hermes.coder` host block in `honcho.json` with `aiPeer: "coder"`, shared `workspace`, inherited `peerName`, `recallMode`, `writeFrequency`, `observation`, etc. The AI peer is eagerly created in Honcho so it exists before the first message.

### Existing profiles, backfill Honcho peers

```bash
hermes honcho sync
```

Scans every Hermes profile, creates host blocks for any profile without one, inherits settings from the default `hermes` block, and creates the new AI peers eagerly. Idempotent — skips profiles that already have a host block.

### Per-profile observation

Each host block can override the observation config independently. Example: a code-focused profile where the AI peer observes the user but doesn't self-model:

```json
"hermes.coder": {
  "aiPeer": "coder",
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": false, "observeOthers": true }
  }
}
```

**Observation toggles (one set per peer):**

| Toggle | Effect |
|--------|--------|
| `observeMe` | Honcho builds a representation of this peer from its own messages |
| `observeOthers` | This peer observes the other peer's messages (feeds cross-peer reasoning) |

Presets via `observationMode`:

- **`"directional"`** (default) — all four flags on. Full mutual observation; enables cross-peer dialectic.
- **`"unified"`** — user `observeMe: true`, AI `observeOthers: true`, rest false. Single-observer pool; AI models the user but not itself, user peer only self-models.

Server-side toggles set via the [Honcho dashboard](https://app.honcho.dev) win over local defaults — synced back at session init.

See the [Honcho page](./honcho.md#observation-directional-vs-unified) for the full observation reference.

### Gateway identity mapping

The peer model above covers CLI, TUI, and desktop sessions, where every conversation resolves to `peerName`. The [gateway](../../developer-guide/gateway-internals.md) adds a second axis: users arrive with platform-native runtime IDs (Telegram UID, Discord snowflake, Slack user), and three keys decide which peer each ID resolves to.

| Key | Effect |
|-----|--------|
| `pinUserPeer: true` | Every non-agent gateway user collapses to `peerName`. The pin is checked first, so it overrides all aliases — pick it only when no user-side identity needs its own peer |
| `userPeerAliases` | Maps specific runtime IDs to peers (`{"7654321": "alice"}`). The home for routing distinct identities — including agents that each carry their own peer |
| `runtimePeerPrefix` | Namespaces any unmapped runtime ID (`telegram_7654321`) so platforms with same-shaped IDs don't collide |

Off-gateway these keys do nothing. `hermes memory setup` only prompts for them when it detects a connected gateway platform. See the [Honcho page](./honcho.md#gateway-identity-mapping) for the resolver ladder and the setup flow.

<details>
<summary>Full honcho.json example (multi-profile)</summary>

```json
{
  "apiKey": "your-key",
  "workspace": "hermes",
  "peerName": "eri",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "workspace": "hermes",
      "peerName": "eri",
      "recallMode": "hybrid",
      "writeFrequency": "async",
      "sessionStrategy": "per-directory",
      "observation": {
        "user": { "observeMe": true, "observeOthers": true },
        "ai": { "observeMe": true, "observeOthers": true }
      },
      "dialecticReasoningLevel": "low",
      "dialecticDynamic": true,
      "dialecticCadence": 2,
      "dialecticDepth": 1,
      "dialecticMaxChars": 600,
      "contextCadence": 1,
      "messageMaxChars": 25000,
      "saveMessages": true
    },
    "hermes.coder": {
      "enabled": true,
      "aiPeer": "coder",
      "workspace": "hermes",
      "peerName": "eri",
      "recallMode": "tools",
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    },
    "hermes.writer": {
      "enabled": true,
      "aiPeer": "writer",
      "workspace": "hermes",
      "peerName": "eri"
    }
  },
  "sessions": {
    "/home/user/myproject": "myproject-main"
  }
}
```

</details>

See the [config reference](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/honcho/README.md) and [Honcho integration guide](https://docs.honcho.dev/v3/guides/integrations/hermes).


---

### OpenViking

Context database by Volcengine (ByteDance) with filesystem-style knowledge hierarchy, tiered retrieval, and automatic memory extraction into 6 categories.

| | |
|---|---|
| **Best for** | Self-hosted knowledge management with structured browsing |
| **Requires** | `pip install openviking` + running server |
| **Data storage** | Self-hosted (local or cloud) |
| **Cost** | Free (open-source, AGPL-3.0) |

**Tools:** `viking_search` (semantic search), `viking_read` (tiered: abstract/overview/full), `viking_browse` (filesystem navigation), `viking_remember` (store facts), `viking_add_resource` (ingest URLs/docs)

**Setup:**
```bash
# Start the OpenViking server first
pip install openviking
openviking-server

# Then configure Hermes
hermes memory setup    # select "openviking"
# Or manually:
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
# Authenticated servers should use a user/admin API key:
echo "OPENVIKING_API_KEY=..." >> ~/.hermes/.env
```

**Key features:**
- Tiered context loading: L0 (~100 tokens) → L1 (~2k) → L2 (full)
- Automatic memory extraction on session commit (profile, preferences, entities, events, cases, patterns)
- `viking://` URI scheme for hierarchical knowledge browsing

`OPENVIKING_ACCOUNT` and `OPENVIKING_USER` are used for local/trusted mode.
`OPENVIKING_AGENT` is Hermes' peer ID in OpenViking for peer-scoped memories.

---

### Mem0

Server-side LLM fact extraction with semantic search, reranking, and automatic deduplication. Supports both Mem0 Platform (cloud) and OSS (self-hosted) modes.

| | |
|---|---|
| **Best for** | Hands-off memory management — Mem0 handles extraction automatically |
| **Requires** | `pip install mem0ai` + API key (platform) or LLM/vector store (OSS) |
| **Data storage** | Mem0 Cloud (platform) or self-hosted (OSS) |
| **Cost** | Mem0 pricing (platform) / free (OSS) |

**Tools (5):** `mem0_list` (list all memories, paginated), `mem0_search` (semantic search with reranking in platform mode), `mem0_add` (store verbatim facts), `mem0_update` (update by ID), `mem0_delete` (delete by ID)

**Setup (Platform):**
```bash
hermes memory setup    # select "mem0" → "Platform"
# Or manually:
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

**Setup (OSS):**
```bash
hermes memory setup    # select "mem0" → "Open Source (self-hosted)"
# Or via flags:
hermes memory setup mem0 --mode oss --oss-llm openai --oss-llm-key sk-... --oss-vector qdrant
```

Preview without writing files:
```bash
hermes memory setup mem0 --mode oss --oss-llm-key sk-... --dry-run
```

**Config:** `$HERMES_HOME/mem0.json` (behavioral settings). Only the secret `MEM0_API_KEY` belongs in `~/.hermes/.env`.

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `platform` | `platform` (Mem0 Cloud) or `oss` (self-hosted) |
| `user_id` | `hermes-user` | User identifier |
| `agent_id` | `hermes` | Agent identifier |
| `rerank` | `true` | Rerank search results for relevance (platform mode only) |

**OSS supported providers:**

| Component | Providers |
|-----------|-----------|
| LLM | openai, ollama |
| Embedder | openai, ollama |
| Vector Store | qdrant (local/server), pgvector |

**Switching modes:** Re-run `hermes memory setup mem0 --mode <platform|oss>` or edit `mem0.json` directly.

---

### Hindsight

Long-term memory with knowledge graph, entity resolution, and multi-strategy retrieval. The `hindsight_reflect` tool provides cross-memory synthesis that no other provider offers. Automatically retains full conversation turns (including tool calls) with session-level document tracking.

| | |
|---|---|
| **Best for** | Knowledge graph-based recall with entity relationships |
| **Requires** | Cloud: API key from [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io). Local: LLM API key (OpenAI, Groq, OpenRouter, etc.) |
| **Data storage** | Hindsight Cloud or local embedded PostgreSQL |
| **Cost** | Hindsight pricing (cloud) or free (local) |

**Tools:** `hindsight_retain` (store with entity extraction), `hindsight_recall` (multi-strategy search), `hindsight_reflect` (cross-memory synthesis)

**Setup:**
```bash
hermes memory setup    # select "hindsight"
# Or manually:
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

The setup wizard installs dependencies automatically and only installs what's needed for the selected mode (`hindsight-client` for cloud, `hindsight-all` for local). Requires `hindsight-client >= 0.4.22` (auto-upgraded on session start if outdated).

**Local mode UI:** `hindsight-embed -p hermes ui start`

**Config:** `$HERMES_HOME/hindsight/config.json`

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud` or `local` |
| `bank_id` | `hermes` | Memory bank identifier |
| `recall_budget` | `mid` | Recall thoroughness: `low` / `mid` / `high` |
| `memory_mode` | `hybrid` | `hybrid` (context + tools), `context` (auto-inject only), `tools` (tools only) |
| `auto_retain` | `true` | Automatically retain conversation turns |
| `auto_recall` | `true` | Automatically recall memories before each turn |
| `retain_async` | `true` | Process retain asynchronously on the server |
| `retain_context` | `conversation between Hermes Agent and the User` | Context label for retained memories |
| `retain_tags` | — | Default tags applied to retained memories; merged with per-call tool tags |
| `retain_source` | — | Optional `metadata.source` attached to retained memories |
| `retain_user_prefix` | `User` | Label used before user turns in auto-retained transcripts |
| `retain_assistant_prefix` | `Assistant` | Label used before assistant turns in auto-retained transcripts |
| `recall_tags` | — | Tags to filter on recall |

See [plugin README](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md) for the full configuration reference.

---

### Holographic

Local SQLite fact store with FTS5 full-text search, trust scoring, and HRR (Holographic Reduced Representations) for compositional algebraic queries.

| | |
|---|---|
| **Best for** | Local-only memory with advanced retrieval, no external dependencies |
| **Requires** | Nothing (SQLite is always available). NumPy optional for HRR algebra. |
| **Data storage** | Local SQLite |
| **Cost** | Free |

**Tools:** `fact_store` (9 actions: add, search, probe, related, reason, contradict, update, remove, list), `fact_feedback` (helpful/unhelpful rating that trains trust scores)

**Setup:**
```bash
hermes memory setup    # select "holographic"
# Or manually:
hermes config set memory.provider holographic
```

**Config:** `config.yaml` under `plugins.hermes-memory-store`

| Key | Default | Description |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite database path |
| `auto_extract` | `false` | Auto-extract facts at session end |
| `default_trust` | `0.5` | Default trust score (0.0–1.0) |

**Unique capabilities:**
- `probe` — entity-specific algebraic recall (all facts about a person/thing)
- `reason` — compositional AND queries across multiple entities
- `contradict` — automated detection of conflicting facts
- Trust scoring with asymmetric feedback (+0.05 helpful / -0.10 unhelpful)

---

### RetainDB

Cloud memory API with hybrid search (Vector + BM25 + Reranking), 7 memory types, and delta compression.

| | |
|---|---|
| **Best for** | Teams already using RetainDB's infrastructure |
| **Requires** | RetainDB account + API key |
| **Data storage** | RetainDB Cloud |
| **Cost** | $20/month |

**Tools:** `retaindb_profile` (user profile), `retaindb_search` (semantic search), `retaindb_context` (task-relevant context), `retaindb_remember` (store with type + importance), `retaindb_forget` (delete memories)

**Setup:**
```bash
hermes memory setup    # select "retaindb"
# Or manually:
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

---

### ByteRover

Persistent memory via the `brv` CLI — hierarchical knowledge tree with tiered retrieval (fuzzy text → LLM-driven search). Local-first with optional cloud sync.

| | |
|---|---|
| **Best for** | Developers who want portable, local-first memory with a CLI |
| **Requires** | ByteRover CLI (`npm install -g byterover-cli` or [install script](https://byterover.dev)) |
| **Data storage** | Local (default) or ByteRover Cloud (optional sync) |
| **Cost** | Free (local) or ByteRover pricing (cloud) |

**Tools:** `brv_query` (search knowledge tree), `brv_curate` (store facts/decisions/patterns), `brv_status` (CLI version + tree stats)

**Setup:**
```bash
# Install the CLI first
curl -fsSL https://byterover.dev/install.sh | sh

# Then configure Hermes
hermes memory setup    # select "byterover"
# Or manually:
hermes config set memory.provider byterover
```

**Key features:**
- Automatic pre-compression extraction (saves insights before context compression discards them)
- Knowledge tree stored at `$HERMES_HOME/byterover/` (profile-scoped)
- SOC2 Type II certified cloud sync (optional)

---

### Supermemory

Semantic long-term memory with profile recall, semantic search, explicit memory tools, and session-end conversation ingest via the Supermemory graph API.

| | |
|---|---|
| **Best for** | Semantic recall with user profiling and session-level graph building |
| **Requires** | `pip install supermemory` + [API key](http://app.supermemory.ai/integrations?connect=hermes) |
| **Data storage** | Supermemory Cloud |
| **Cost** | Supermemory pricing |

**Tools:** `supermemory_store` (save explicit memories), `supermemory_search` (semantic similarity search), `supermemory_forget` (forget by ID or best-match query), `supermemory_profile` (persistent profile + recent context)

**Setup:**
```bash
hermes memory setup    # select "supermemory"
# Or manually:
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

**Config:** `$HERMES_HOME/supermemory.json`

| Key | Default | Description |
|-----|---------|-------------|
| `container_tag` | `hermes` | Container tag used for search and writes. Supports `{identity}` template for profile-scoped tags. |
| `auto_recall` | `true` | Inject relevant memory context before turns |
| `auto_capture` | `true` | Store cleaned user-assistant turns after each response |
| `max_recall_results` | `10` | Max recalled items to format into context |
| `profile_frequency` | `50` | Include profile facts on first turn and every N turns |
| `capture_mode` | `all` | Skip tiny or trivial turns by default |
| `search_mode` | `hybrid` | Search mode: `hybrid`, `memories`, or `documents` |
| `api_timeout` | `5.0` | Timeout for SDK and ingest requests |

**Environment variables:** `SUPERMEMORY_API_KEY` (required), `SUPERMEMORY_CONTAINER_TAG` (overrides config).

**Key features:**
- Automatic context fencing — strips recalled memories from captured turns to prevent recursive memory pollution
- Full-session ingest — the entire conversation is sent once at session boundaries
- Session-end conversation ingest (to `/v4/conversations`) for richer profile + graph building in Supermemory
- Profile facts injected on first turn and at configurable intervals
- **Profile-scoped containers** — use `{identity}` in `container_tag` (e.g. `hermes-{identity}` → `hermes-coder`) to isolate memories per Hermes profile
- **Multi-container mode** — enable `enable_custom_container_tags` with a `custom_containers` list to let the agent read/write across named containers. Automatic operations stay on the primary container.

<details>
<summary>Multi-container example</summary>

```json
{
  "container_tag": "hermes",
  "enable_custom_container_tags": true,
  "custom_containers": ["project-alpha", "shared-knowledge"],
  "custom_container_instructions": "Use project-alpha for coding context."
}
```

</details>

**Support:** [Discord](https://supermemory.link/discord) · [support@supermemory.com](mailto:support@supermemory.com)

### Memori

Structured long-term memory using Memori Cloud, with background completed-turn capture, tool-aware turn context, and explicit recall tools for facts, summaries, quota, signup, and feedback.

| | |
|---|---|
| **Best for** | Agent-controlled recall with structured project and session attribution |
| **Requires** | `pip install hermes-memori` + `hermes-memori install` + [Memori API key](https://app.memorilabs.ai/signup) |
| **Data storage** | Memori Cloud |
| **Cost** | Memori pricing |

**Tools:** `memori_recall` (search long-term memory), `memori_recall_summary` (summarized context), `memori_quota` (usage/quota), `memori_signup` (request signup email), `memori_feedback` (send integration feedback)

**Setup:**
```bash
pip install hermes-memori
hermes-memori install
hermes config set memory.provider memori
hermes memory setup
```

---

## Provider Comparison

| Provider | Storage | Cost | Tools | Dependencies | Unique Feature |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | Cloud | Paid | 5 | `honcho-ai` | Dialectic user modeling + session-scoped context |
| **OpenViking** | Self-hosted | Free | 5 | `openviking` + server | Filesystem hierarchy + tiered loading |
| **Mem0** | Cloud/Self-hosted | Free/Paid | 5 | `mem0ai` | Server-side LLM extraction + OSS mode |
| **Hindsight** | Cloud/Local | Free/Paid | 3 | `hindsight-client` | Knowledge graph + reflect synthesis |
| **Holographic** | Local | Free | 2 | None | HRR algebra + trust scoring |
| **RetainDB** | Cloud | $20/mo | 5 | `requests` | Delta compression |
| **ByteRover** | Local/Cloud | Free/Paid | 3 | `brv` CLI | Pre-compression extraction |
| **Supermemory** | Cloud | Paid | 4 | `supermemory` | Context fencing + session graph ingest + multi-container |
| **Memori** | Cloud | Free/Paid | 5 | `hermes-memori` | Tool-aware memory + structured recall |

## Profile Isolation

Each provider's data is isolated per [profile](/user-guide/profiles):

- **Local storage providers** (Holographic, ByteRover) use `$HERMES_HOME/` paths which differ per profile
- **Config file providers** (Honcho, Mem0, Hindsight, Supermemory) store config in `$HERMES_HOME/` so each profile has its own credentials
- **Cloud providers** (RetainDB) auto-derive profile-scoped project names
- **Env var providers** (OpenViking) are configured via each profile's `.env` file

## Building a Memory Provider

See the [Developer Guide: Memory Provider Plugins](/developer-guide/memory-provider-plugin) for how to create your own.

---

# SOURCE: website/docs/user-guide/features/honcho.md

---
sidebar_position: 99
title: "Honcho Memory"
description: "AI-native persistent memory via Honcho — dialectic reasoning, multi-agent user modeling, and deep personalization"
---

# Honcho Memory

[Honcho](https://github.com/plastic-labs/honcho) is an AI-native memory backend that adds dialectic reasoning and deep user modeling on top of Hermes's built-in memory system. Instead of simple key-value storage, Honcho maintains a running model of who the user is — their preferences, communication style, goals, and patterns — by reasoning about conversations after they happen.

:::info Honcho is a Memory Provider Plugin
Honcho is integrated into the [Memory Providers](./memory-providers.md) system. All features below are available through the unified memory provider interface.
:::

## What Honcho Adds

| Capability | Built-in Memory | Honcho |
|-----------|----------------|--------|
| Cross-session persistence | ✔ File-based MEMORY.md/USER.md | ✔ Server-side with API |
| User profile | ✔ Manual agent curation | ✔ Automatic dialectic reasoning |
| Session summary | — | ✔ Session-scoped context injection |
| Multi-agent isolation | — | ✔ Per-peer profile separation |
| Observation modes | — | ✔ Unified or directional observation |
| Conclusions (derived insights) | — | ✔ Server-side reasoning about patterns |
| Search across history | ✔ FTS5 session search | ✔ Semantic search over conclusions |

**Dialectic reasoning**: After each conversation turn (gated by `dialecticCadence`), Honcho analyzes the exchange and derives insights about the user's preferences, habits, and goals. These accumulate over time, giving the agent a deepening understanding that goes beyond what the user explicitly stated. The dialectic supports multi-pass depth (1–3 passes) with automatic cold/warm prompt selection — cold start queries focus on general user facts while warm queries prioritize session-scoped context.

**Session-scoped context**: Base context now includes the session summary alongside the user representation and peer card. This gives the agent awareness of what has already been discussed in the current session, reducing repetition and enabling continuity.

**Multi-agent profiles**: When multiple Hermes instances talk to the same user (e.g., a coding assistant and a personal assistant), Honcho maintains separate "peer" profiles. Each peer sees only its own observations and conclusions, preventing cross-contamination of context.

## Setup

```bash
hermes memory setup    # select "honcho" from the provider list
```

Or configure manually:

```yaml
# ~/.hermes/config.yaml
memory:
  provider: honcho
```

```bash
echo 'HONCHO_API_KEY=***' >> ~/.hermes/.env
```

Get an API key at [honcho.dev](https://honcho.dev).

## Architecture

### Two-Layer Context Injection

Every turn (in `hybrid` or `context` mode), Honcho assembles two layers of context injected into the system prompt:

1. **Base context** — session summary, user representation, user peer card, AI self-representation, and AI identity card. Refreshed on `contextCadence`. This is the "who is this user" layer.
2. **Dialectic supplement** — LLM-synthesized reasoning about the user's current state and needs. Refreshed on `dialecticCadence`. This is the "what matters right now" layer.

Both layers are concatenated and truncated to the `contextTokens` budget (if set).

### Cold/Warm Prompt Selection

The dialectic automatically selects between two prompt strategies:

- **Cold start** (no base context yet): General query — "Who is this person? What are their preferences, goals, and working style?"
- **Warm session** (base context exists): Session-scoped query — "Given what's been discussed in this session so far, what context about this user is most relevant?"

This happens automatically based on whether base context has been populated.

### Three Orthogonal Config Knobs

Cost and depth are controlled by three independent knobs:

| Knob | Controls | Default |
|------|----------|---------|
| `contextCadence` | Turns between `context()` API calls (base layer refresh) | `1` |
| `dialecticCadence` | Turns between `peer.chat()` LLM calls (dialectic layer refresh) | `2` (recommended 1–5) |
| `dialecticDepth` | Number of `.chat()` passes per dialectic invocation (1–3) | `1` |

These are orthogonal — you can have frequent context refreshes with infrequent dialectic, or deep multi-pass dialectic at low frequency. Example: `contextCadence: 1, dialecticCadence: 5, dialecticDepth: 2` refreshes base context every turn, runs dialectic every 5 turns, and each dialectic run makes 2 passes.

### Dialectic Depth (Multi-Pass)

When `dialecticDepth` > 1, each dialectic invocation runs multiple `.chat()` passes:

- **Pass 0**: Cold or warm prompt (see above)
- **Pass 1**: Self-audit — identifies gaps in the initial assessment and synthesizes evidence from recent sessions
- **Pass 2**: Reconciliation — checks for contradictions between prior passes and produces a final synthesis

Each pass uses a proportional reasoning level (lighter early passes, base level for the main pass). Override per-pass levels with `dialecticDepthLevels` — e.g., `["minimal", "medium", "high"]` for a depth-3 run.

Passes bail out early if the prior pass returned strong signal (long, structured output), so depth 3 doesn't always mean 3 LLM calls.

### Session-Start Prewarm

On session init, Honcho fires a dialectic call in the background at the full configured `dialecticDepth` and hands the result directly to turn 1's context assembly. A single-pass prewarm on a cold peer often returns thin output — multi-pass depth runs the audit/reconcile cycle before the user ever speaks. If prewarm hasn't landed by turn 1, turn 1 falls back to a synchronous call with a bounded timeout.

### Query-Adaptive Reasoning Level

The auto-injected dialectic scales `dialecticReasoningLevel` by query length: +1 level at ≥120 chars, +2 at ≥400, clamped at `reasoningLevelCap` (default `"high"`). Disable with `reasoningHeuristic: false` to pin every auto call to `dialecticReasoningLevel`. Available levels: `minimal`, `low`, `medium`, `high`, `max`.

## Configuration Options

Honcho is configured in `~/.honcho/config.json` (global) or `$HERMES_HOME/honcho.json` (profile-local). The setup wizard handles this for you.

### Self-Hosted Honcho with Authentication

When pointing Hermes at a self-hosted Honcho server, `hermes honcho setup` (and `hermes memory setup`) ask for a **local JWT / bearer token** after the base URL. Paste a JWT signed with the server's `AUTH_JWT_SECRET` (the Honcho compose env var) to enable authenticated access; leave it blank for servers running with `AUTH_USE_AUTH=false`. The local token is stored under the host block (`hosts.<host>.apiKey` in `honcho.json`), separate from any cloud `apiKey`, so you can flip the `Cloud or local?` prompt back to `cloud` later without losing either credential.

### Full Config Reference

| Key | Default | Description |
|-----|---------|-------------|
| `contextTokens` | `null` (uncapped) | Token budget for auto-injected context per turn. Set to an integer (e.g. 1200) to cap. Truncates at word boundaries |
| `contextCadence` | `1` | Minimum turns between `context()` API calls (base layer refresh) |
| `dialecticCadence` | `2` | Minimum turns between `peer.chat()` LLM calls (dialectic layer). Recommended 1–5. In `tools` mode, irrelevant — model calls explicitly |
| `dialecticDepth` | `1` | Number of `.chat()` passes per dialectic invocation. Clamped to 1–3 |
| `dialecticDepthLevels` | `null` | Optional array of reasoning levels per pass, e.g. `["minimal", "low", "medium"]`. Overrides proportional defaults |
| `dialecticReasoningLevel` | `'low'` | Base reasoning level: `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | When `true`, model can override reasoning level per-call via tool param |
| `dialecticMaxChars` | `600` | Max chars of dialectic result injected into system prompt |
| `recallMode` | `'hybrid'` | `hybrid` (auto-inject + tools), `context` (inject only), `tools` (tools only) |
| `writeFrequency` | `'async'` | When to flush messages: `async` (background thread), `turn` (sync), `session` (batch on end), or integer N |
| `saveMessages` | `true` | Whether to persist messages to Honcho API |
| `observationMode` | `'directional'` | `directional` (all on) or `unified` (shared pool). Override with `observation` object for granular control |
| `messageMaxChars` | `25000` | Max chars per message sent via `add_messages()`. Chunked if exceeded |
| `dialecticMaxInputChars` | `10000` | Max chars for dialectic query input to `peer.chat()` |
| `sessionStrategy` | `'per-directory'` | `per-directory`, `per-repo`, `per-session`, or `global` |
| `pinUserPeer` | `false` | Gateway only. When `true`, every platform user collapses to `peerName` |
| `userPeerAliases` | `{}` | Gateway only. Map of runtime IDs to peers (`{"7654321": "alice"}`). Many-to-one |
| `runtimePeerPrefix` | `""` | Gateway only. Namespaces unknown runtime IDs (`telegram_7654321`) when no alias matches |

**Session strategy** controls how Honcho sessions map to your work:
- `per-session` — each `hermes` run gets a fresh session. Clean starts, memory via tools. Recommended for new users.
- `per-directory` — one Honcho session per working directory. Context accumulates across runs.
- `per-repo` — one session per git repository.
- `global` — single session across all directories.

**Recall mode** controls how memory flows into conversations:
- `hybrid` — context auto-injected into system prompt AND tools available (model decides when to query).
- `context` — auto-injection only, tools hidden.
- `tools` — tools only, no auto-injection. Agent must explicitly call `honcho_reasoning`, `honcho_search`, etc.

**Settings per recall mode:**

| Setting | `hybrid` | `context` | `tools` |
|---------|----------|-----------|---------|
| `writeFrequency` | flushes messages | flushes messages | flushes messages |
| `contextCadence` | gates base context refresh | gates base context refresh | irrelevant — no injection |
| `dialecticCadence` | gates auto LLM calls | gates auto LLM calls | irrelevant — model calls explicitly |
| `dialecticDepth` | multi-pass per invocation | multi-pass per invocation | irrelevant — model calls explicitly |
| `contextTokens` | caps injection | caps injection | irrelevant — no injection |
| `dialecticDynamic` | gates model override | N/A (no tools) | gates model override |

In `tools` mode, the model is fully in control — it calls `honcho_reasoning` when it wants, at whatever `reasoning_level` it picks. Cadence and budget settings only apply to modes with auto-injection (`hybrid` and `context`).

## Gateway Identity Mapping

These settings only matter when you run the [Hermes gateway](../../developer-guide/gateway-internals.md) — the one entrypoint where users arrive with platform-native runtime IDs (Telegram UID, Discord snowflake, Slack user). CLI, TUI, and desktop sessions have no runtime ID and always resolve to `peerName`, so off-gateway these keys do nothing.

The setup wizard detects whether a gateway platform is connected and skips this step entirely if not. When it runs, it asks one question — *who talks to this gateway?* — and derives the keys:

| Answer | Result |
|--------|--------|
| **just me** | `pinUserPeer: true` — every non-agent gateway user collapses to your peer. Pin overrides all aliases, so pick this only when no user-side identity needs its own peer. If separate agents reach the gateway and each needs a distinct peer, do **not** pin — leave `pinUserPeer: false` and map them via `userPeerAliases` (the `[e]` editor) instead |
| **me + other people** (pooled) | `pinUserPeer: false` + `userPeerAliases` mapping your runtime IDs to `peerName` — you stay on your shared history, others get their own peers |
| **only other people** | `pinUserPeer: false`, optional `runtimePeerPrefix` — each user gets their own peer |

Pick `[e]` at the prompt to set the three keys directly instead.

The resolver tries the keys top-down, first match wins: `pinUserPeer` → `userPeerAliases[id]` → `runtimePeerPrefix + id` → raw runtime ID → `peerName` → session-key fallback.

:::warning Un-pinning orphans pooled memory
Flipping `pinUserPeer` from `true` to `false` does not migrate data — memory accumulated under `peerName` stays there, and platform users resolve to fresh, empty peers. To keep your own continuity, choose the **pooled** path so your runtime IDs alias back to `peerName`. The wizard offers this steer automatically when it detects the transition.
:::

:::note Deprecated key
`pinPeerName` is a legacy alias for `pinUserPeer` — still read for back-compat (`pinUserPeer` wins where both are set), never written. Re-running setup migrates it onto the canonical key.
:::

## Observation (Directional vs. Unified)

Honcho models a conversation as peers exchanging messages. Each peer has two observation toggles that map 1:1 to Honcho's `SessionPeerConfig`:

| Toggle | Effect |
|--------|--------|
| `observeMe` | Honcho builds a representation of this peer from its own messages |
| `observeOthers` | This peer observes the other peer's messages (feeds cross-peer reasoning) |

Two peers × two toggles = four flags. `observationMode` is a shorthand preset:

| Preset | User flags | AI flags | Semantics |
|--------|-----------|----------|-----------|
| `"directional"` (default) | me: on, others: on | me: on, others: on | Full mutual observation. Enables cross-peer dialectic — "what does the AI know about the user, based on what the user said and the AI replied." |
| `"unified"` | me: on, others: off | me: off, others: on | Shared-pool semantics — the AI observes the user's messages only, the user peer only self-models. Single-observer pool. |

Override the preset with an explicit `observation` block for per-peer control:

```json
"observation": {
  "user": { "observeMe": true,  "observeOthers": true },
  "ai":   { "observeMe": true,  "observeOthers": false }
}
```

Common patterns:

| Intent | Config |
|--------|--------|
| Full observation (most users) | `"observationMode": "directional"` |
| AI shouldn't re-model the user from its own replies | `"ai": {"observeMe": true, "observeOthers": false}` |
| Strong persona the AI peer shouldn't update from self-observation | `"ai": {"observeMe": false, "observeOthers": true}` |

Server-side toggles set via the [Honcho dashboard](https://app.honcho.dev) win over local defaults — Hermes syncs them back at session init.

## Tools

When Honcho is active as the memory provider, five tools become available:

| Tool | Purpose |
|------|---------|
| `honcho_profile` | Read or update peer card — pass `card` (list of facts) to update, omit to read |
| `honcho_search` | Semantic search over context — raw excerpts, no LLM synthesis |
| `honcho_context` | Full session context — summary, representation, card, recent messages |
| `honcho_reasoning` | Synthesized answer from Honcho's LLM — pass `reasoning_level` (minimal/low/medium/high/max) to control depth |
| `honcho_conclude` | Create or delete conclusions — pass `conclusion` to create, `delete_id` to remove (PII only) |

## CLI Commands

The `hermes honcho` subcommand is **only registered when Honcho is the active memory provider** (`memory.provider: honcho` in `config.yaml`). On a fresh install, configure Honcho directly with `hermes memory setup honcho` (or run `hermes memory setup` and pick it from the list); the `hermes honcho` subcommand then appears on the next invocation.

```bash
hermes memory setup honcho    # Configure Honcho directly (works before activation)
hermes honcho status          # Connection status, config, and key settings
hermes honcho setup           # Redirects to `hermes memory setup` (post-activation alias)
hermes honcho strategy        # Show or set session strategy (per-session/per-directory/per-repo/global)
hermes honcho peer            # Show or update peer names + dialectic reasoning level
hermes honcho mode            # Show or set recall mode (hybrid/context/tools)
hermes honcho tokens          # Show or set token budget for context and dialectic
hermes honcho identity        # Seed or show the AI peer's Honcho identity
hermes honcho sync            # Sync Honcho config to all existing profiles
hermes honcho peers           # Show peer identities across all profiles
hermes honcho sessions        # List known Honcho session mappings
hermes honcho map             # Map current directory to a Honcho session name
hermes honcho enable          # Enable Honcho for the active profile
hermes honcho disable         # Disable Honcho for the active profile
hermes honcho migrate         # Step-by-step migration guide from openclaw-honcho
```

## Migrating from `hermes honcho`

If you previously used the standalone `hermes honcho setup`:

1. Your existing configuration (`honcho.json` or `~/.honcho/config.json`) is preserved
2. Your server-side data (memories, conclusions, user profiles) is intact
3. Set `memory.provider: honcho` in config.yaml to reactivate

No re-login or re-setup needed. Run `hermes memory setup` and select "honcho" — the wizard detects your existing config.

## Full Documentation

See [Memory Providers — Honcho](./memory-providers.md#honcho) for the complete reference.
