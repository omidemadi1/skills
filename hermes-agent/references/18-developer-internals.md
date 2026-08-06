<!-- Sections in this file (in order):
  - developer-guide/architecture.md
  - developer-guide/agent-loop.md
  - developer-guide/adding-tools.md
  - developer-guide/adding-platform-adapters.md
  - developer-guide/programmatic-integration.md
  - guides/python-library.md
-->


---

# SOURCE: website/docs/developer-guide/architecture.md

---
sidebar_position: 1
title: "Architecture"
description: "Hermes Agent internals — major subsystems, execution paths, data flow, and where to read next"
---

# Architecture

This page is the top-level map of Hermes Agent internals. Use it to orient yourself in the codebase, then dive into subsystem-specific docs for implementation details.

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        Entry Points                                  │
│                                                                      │
│  CLI (cli.py)    Gateway (gateway/run.py)    ACP (acp_adapter/)     │
│  Batch Runner    API Server                  Python Library          │
└──────────┬──────────────┬───────────────────────┬───────────────────┘
           │              │                       │
           ▼              ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AIAgent (run_agent.py)                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Prompt       │  │ Provider     │  │ Tool         │               │
│  │ Builder      │  │ Resolution   │  │ Dispatch     │               │
│  │ (prompt_     │  │ (runtime_    │  │ (model_      │               │
│  │  builder.py) │  │  provider.py)│  │  tools.py)   │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                       │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐               │
│  │ Compression  │  │ 3 API Modes  │  │ Tool Registry│               │
│  │ & Caching    │  │ chat_compl.  │  │ (registry.py)│               │
│  │              │  │ codex_resp.  │  │ 70+ tools    │               │
│  │              │  │ anthropic    │  │ 28 toolsets  │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────┴─────────────────┴─────────────────┴───────────────────────┘
           │                                    │
           ▼                                    ▼
┌───────────────────┐              ┌──────────────────────┐
│ Session Storage   │              │ Tool Backends         │
│ (SQLite + FTS5)   │              │ Terminal (6 backends) │
│ hermes_state.py   │              │ Browser (5 backends)  │
│ gateway/session.py│              │ Web (4 backends)      │
└───────────────────┘              │ MCP (dynamic)         │
                                   │ File, Vision, etc.    │
                                   └──────────────────────┘
```

## Directory Structure

```text
hermes-agent/
├── run_agent.py              # AIAgent — core conversation loop (large file)
├── cli.py                    # HermesCLI — interactive terminal UI (large file)
├── model_tools.py            # Tool discovery, schema collection, dispatch
├── toolsets.py               # Tool groupings and platform presets
├── hermes_state.py           # SQLite session/state database with FTS5
├── hermes_constants.py       # HERMES_HOME, profile-aware paths
├── batch_runner.py           # Batch trajectory generation
│
├── agent/                    # Agent internals
│   ├── prompt_builder.py     # System prompt assembly
│   ├── context_engine.py     # ContextEngine ABC (pluggable)
│   ├── context_compressor.py # Default engine — lossy summarization
│   ├── prompt_caching.py     # Anthropic prompt caching
│   ├── auxiliary_client.py   # Auxiliary LLM for side tasks (vision, summarization)
│   ├── model_metadata.py     # Model context lengths, token estimation
│   ├── models_dev.py         # models.dev registry integration
│   ├── anthropic_adapter.py  # Anthropic Messages API format conversion
│   ├── display.py            # KawaiiSpinner, tool preview formatting
│   ├── skill_commands.py     # Skill slash commands
│   ├── memory_manager.py    # Memory manager orchestration
│   ├── memory_provider.py   # Memory provider ABC
│   └── trajectory.py         # Trajectory saving helpers
│
├── hermes_cli/               # CLI subcommands and setup
│   ├── main.py               # Entry point — all `hermes` subcommands (large file)
│   ├── config.py             # DEFAULT_CONFIG, OPTIONAL_ENV_VARS, migration
│   ├── commands.py           # COMMAND_REGISTRY — central slash command definitions
│   ├── auth.py               # PROVIDER_REGISTRY, credential resolution
│   ├── runtime_provider.py   # Provider → api_mode + credentials
│   ├── models.py             # Model catalog, provider model lists
│   ├── model_switch.py       # /model command logic (CLI + gateway shared)
│   ├── setup.py              # Interactive setup wizard (large file)
│   ├── skin_engine.py        # CLI theming engine
│   ├── skills_config.py      # hermes skills — enable/disable per platform
│   ├── skills_hub.py         # /skills slash command
│   ├── tools_config.py       # hermes tools — enable/disable per platform
│   ├── plugins.py            # PluginManager — discovery, loading, hooks
│   ├── callbacks.py          # Terminal callbacks (clarify, sudo, approval)
│   └── gateway.py            # hermes gateway start/stop
│
├── tools/                    # Tool implementations (one file per tool)
│   ├── registry.py           # Central tool registry
│   ├── approval.py           # Dangerous command detection
│   ├── terminal_tool.py      # Terminal orchestration
│   ├── process_registry.py   # Background process management
│   ├── file_tools.py         # read_file, write_file, patch, search_files
│   ├── web_tools.py          # web_search, web_extract
│   ├── browser_tool.py       # 10 browser automation tools
│   ├── code_execution_tool.py # execute_code sandbox
│   ├── delegate_tool.py      # Subagent delegation
│   ├── mcp_tool.py           # MCP client (large file)
│   ├── credential_files.py   # File-based credential passthrough
│   ├── env_passthrough.py    # Env var passthrough for sandboxes
│   ├── ansi_strip.py         # ANSI escape stripping
│   └── environments/         # Terminal backends (local, docker, ssh, modal, daytona, singularity)
│
├── gateway/                  # Messaging platform gateway
│   ├── run.py                # GatewayRunner — message dispatch (large file)
│   ├── session.py            # SessionStore — conversation persistence
│   ├── delivery.py           # Outbound message delivery
│   ├── pairing.py            # DM pairing authorization
│   ├── hooks.py              # Hook discovery and lifecycle events
│   ├── mirror.py             # Cross-session message mirroring
│   ├── status.py             # Token locks, profile-scoped process tracking
│   ├── builtin_hooks/        # Extension point for always-registered hooks (none shipped)
│   └── platforms/            # 20 adapters: telegram, discord, slack, whatsapp,
│                             #   signal, matrix, mattermost, email, sms,
│                             #   dingtalk, feishu, wecom, wecom_callback, weixin,
│                             #   bluebubbles, qqbot, homeassistant, webhook, api_server,
│                             #   yuanbao
│
├── acp_adapter/              # ACP server (VS Code / Zed / JetBrains)
├── cron/                     # Scheduler (jobs.py, scheduler.py)
├── plugins/memory/           # Memory provider plugins
├── plugins/context_engine/   # Context engine plugins
├── skills/                   # Bundled skills (always available)
├── optional-skills/          # Official optional skills (install explicitly)
├── website/                  # Docusaurus documentation site
└── tests/                    # Pytest suite (~25,000 tests across ~1,250 files)
```

## Data Flow

### CLI Session

```text
User input → HermesCLI.process_input()
  → AIAgent.run_conversation()
    → prompt_builder.build_system_prompt()
    → runtime_provider.resolve_runtime_provider()
    → API call (chat_completions / codex_responses / anthropic_messages)
    → tool_calls? → model_tools.handle_function_call() → loop
    → final response → display → save to SessionDB
```

### Gateway Message

```text
Platform event → Adapter.on_message() → MessageEvent
  → GatewayRunner._handle_message()
    → authorize user
    → resolve session key
    → create AIAgent with session history
    → AIAgent.run_conversation()
    → deliver response back through adapter
```

### Cron Job

```text
Scheduler tick → load due jobs from jobs.json
  → create fresh AIAgent (no history)
  → inject attached skills as context
  → run job prompt
  → deliver response to target platform
  → update job state and next_run
```

## Recommended Reading Order

If you are new to the codebase:

1. **This page** — orient yourself
2. **[Agent Loop Internals](./agent-loop.md)** — how AIAgent works
3. **[Prompt Assembly](./prompt-assembly.md)** — system prompt construction
4. **[Provider Runtime Resolution](./provider-runtime.md)** — how providers are selected
5. **[Adding Providers](./adding-providers.md)** — practical guide to adding a new provider
6. **[Tools Runtime](./tools-runtime.md)** — tool registry, dispatch, environments
7. **[Session Storage](./session-storage.md)** — SQLite schema, FTS5, session lineage
8. **[Gateway Internals](./gateway-internals.md)** — messaging platform gateway
9. **[Context Compression & Prompt Caching](./context-compression-and-caching.md)** — compression and caching
10. **[ACP Internals](./acp-internals.md)** — IDE integration

## Major Subsystems

### Agent Loop

The synchronous orchestration engine (`AIAgent` in `run_agent.py`). Handles provider selection, prompt construction, tool execution, retries, fallback, callbacks, compression, and persistence. Supports three API modes for different provider backends.

→ [Agent Loop Internals](./agent-loop.md)

### Prompt System

Prompt construction and maintenance across the conversation lifecycle:

- **`system_prompt.py` + `prompt_builder.py`** — assembles the ordered system-prompt tiers (`stable` → `context` → `volatile`): identity/tool guidance/skills, context files, then memory/profile/timestamp blocks
- **`prompt_caching.py`** — Applies Anthropic cache breakpoints for prefix caching
- **`context_compressor.py`** — Summarizes middle conversation turns when context exceeds thresholds

→ [Prompt Assembly](./prompt-assembly.md), [Context Compression & Prompt Caching](./context-compression-and-caching.md)

### Provider Resolution

A shared runtime resolver used by CLI, gateway, cron, ACP, and auxiliary calls. Maps `(provider, model)` tuples to `(api_mode, api_key, base_url)`. Handles 18+ providers, OAuth flows, credential pools, and alias resolution.

→ [Provider Runtime Resolution](./provider-runtime.md)

### Tool System

Central tool registry (`tools/registry.py`) with 70+ registered tools across ~28 toolsets. Each tool file self-registers at import time. The registry handles schema collection, dispatch, availability checking, and error wrapping. Terminal tools support 6 backends (local, Docker, SSH, Daytona, Modal, Singularity).

→ [Tools Runtime](./tools-runtime.md)

### Session Persistence

SQLite-based session storage with FTS5 full-text search. Sessions have lineage tracking (parent/child across compressions), per-platform isolation, and atomic writes with contention handling.

→ [Session Storage](./session-storage.md)

### Messaging Gateway

Long-running process with 20 platform adapters, unified session routing, user authorization (allowlists + DM pairing), slash command dispatch, hook system, cron ticking, and background maintenance.

→ [Gateway Internals](./gateway-internals.md)

### Plugin System

Three discovery sources: `~/.hermes/plugins/` (user), `.hermes/plugins/` (project), and pip entry points. Plugins register tools, hooks, and CLI commands through a context API. Two specialized plugin types exist: memory providers (`plugins/memory/`) and context engines (`plugins/context_engine/`). Both are single-select — only one of each can be active at a time, configured via `hermes plugins` or `config.yaml`.

→ [Plugin Guide](/guides/build-a-hermes-plugin), [Memory Provider Plugin](./memory-provider-plugin.md)

### Cron

First-class agent tasks (not shell tasks). Jobs store in JSON, support multiple schedule formats, can attach skills and scripts, and deliver to any platform.

→ [Cron Internals](./cron-internals.md)

### ACP Integration

Exposes Hermes as an editor-native agent over stdio/JSON-RPC for VS Code, Zed, and JetBrains.

→ [ACP Internals](./acp-internals.md)

### Trajectories

Generates ShareGPT-format trajectories from agent sessions for training data generation.

→ [Trajectories & Training Format](./trajectory-format.md)

## Design Principles

| Principle | What it means in practice |
|-----------|--------------------------|
| **Prompt stability** | System prompt doesn't change mid-conversation. No cache-breaking mutations except explicit user actions (`/model`). |
| **Observable execution** | Every tool call is visible to the user via callbacks. Progress updates in CLI (spinner) and gateway (chat messages). |
| **Interruptible** | API calls and tool execution can be cancelled mid-flight by user input or signals. |
| **Platform-agnostic core** | One AIAgent class serves CLI, gateway, ACP, batch, and API server. Platform differences live in the entry point, not the agent. |
| **Loose coupling** | Optional subsystems (MCP, plugins, memory providers, RL environments) use registry patterns and check_fn gating, not hard dependencies. |
| **Profile isolation** | Each profile (`hermes -p <name>`) gets its own HERMES_HOME, config, memory, sessions, and gateway PID. Multiple profiles run concurrently. |

## File Dependency Chain

```text
tools/registry.py  (no deps — imported by all tool files)
       ↑
tools/*.py  (each calls registry.register() at import time)
       ↑
model_tools.py  (imports tools/registry + triggers tool discovery)
       ↑
run_agent.py, cli.py, batch_runner.py, environments/
```

This chain means tool registration happens at import time, before any agent instance is created. Any `tools/*.py` file with a top-level `registry.register()` call is auto-discovered — no manual import list needed.

---

# SOURCE: website/docs/developer-guide/agent-loop.md

---
sidebar_position: 3
title: "Agent Loop Internals"
description: "Detailed walkthrough of AIAgent execution, API modes, tools, callbacks, and fallback behavior"
---

# Agent Loop Internals

The core orchestration engine is `run_agent.py`'s `AIAgent` class — a large file that handles everything from prompt assembly to tool dispatch to provider failover.

## Core Responsibilities

`AIAgent` is responsible for:

- Assembling the effective system prompt and tool schemas via `prompt_builder.py`
- Selecting the correct provider/API mode (chat_completions, codex_responses, anthropic_messages)
- Making interruptible model calls with cancellation support
- Executing tool calls (sequentially or concurrently via thread pool)
- Maintaining conversation history in OpenAI message format
- Handling compression, retries, and fallback model switching
- Tracking iteration budgets across parent and child agents
- Flushing persistent memory before context is lost

## Two Entry Points

```python
# Simple interface — returns final response string
response = agent.chat("Fix the bug in main.py")

# Full interface — returns dict with messages, metadata, usage stats
result = agent.run_conversation(
    user_message="Fix the bug in main.py",
    system_message=None,           # auto-built if omitted
    conversation_history=None,      # auto-loaded from session if omitted
    task_id="task_abc123"
)
```

`chat()` is a thin wrapper around `run_conversation()` that extracts the `final_response` field from the result dict.

## API Modes

Hermes supports three API execution modes, resolved from provider selection, explicit args, and base URL heuristics:

| API mode | Used for | Client type |
|----------|----------|-------------|
| `chat_completions` | OpenAI-compatible endpoints (OpenRouter, custom, most providers) | `openai.OpenAI` |
| `codex_responses` | OpenAI Codex / Responses API | `openai.OpenAI` with Responses format |
| `anthropic_messages` | Native Anthropic Messages API | `anthropic.Anthropic` via adapter |

The mode determines how messages are formatted, how tool calls are structured, how responses are parsed, and how caching/streaming works. All three converge on the same internal message format (OpenAI-style `role`/`content`/`tool_calls` dicts) before and after API calls.

**Mode resolution order:**
1. Explicit `api_mode` constructor arg (highest priority)
2. Provider-specific detection (e.g., `anthropic` provider → `anthropic_messages`)
3. Base URL heuristics (e.g., `api.anthropic.com` → `anthropic_messages`)
4. Default: `chat_completions`

## Turn Lifecycle

Each iteration of the agent loop follows this sequence:

```text
run_conversation()
  1. Generate task_id if not provided
  2. Append user message to conversation history
  3. Build or reuse cached system prompt (prompt_builder.py)
  4. Check if preflight compression is needed (>50% context)
  5. Build API messages from conversation history
     - chat_completions: OpenAI format as-is
     - codex_responses: convert to Responses API input items
     - anthropic_messages: convert via anthropic_adapter.py
  6. Inject ephemeral prompt layers (budget warnings, context pressure)
  7. Apply prompt caching markers if on Anthropic
  8. Make interruptible API call (_interruptible_api_call)
  9. Parse response:
     - If tool_calls: execute them, append results, loop back to step 5
     - If text response: persist session, flush memory if needed, return
```

### Message Format

All messages use OpenAI-compatible format internally:

```python
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "...", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

Reasoning content (from models that support extended thinking) is stored in `assistant_msg["reasoning"]` and optionally displayed via the `reasoning_callback`.

### Message Alternation Rules

The agent loop enforces strict message role alternation:

- After the system message: `User → Assistant → User → Assistant → ...`
- During tool calling: `Assistant (with tool_calls) → Tool → Tool → ... → Assistant`
- **Never** two assistant messages in a row
- **Never** two user messages in a row
- **Only** `tool` role can have consecutive entries (parallel tool results)

Providers validate these sequences and will reject malformed histories.

## Interruptible API Calls

API requests are wrapped in `_interruptible_api_call()` which runs the actual HTTP call in a background thread while monitoring an interrupt event:

```text
┌────────────────────────────────────────────────────┐
│  Main thread                  API thread           │
│                                                    │
│   wait on:                     HTTP POST           │
│    - response ready     ───▶   to provider         │
│    - interrupt event                               │
│    - timeout                                       │
└────────────────────────────────────────────────────┘
```

When interrupted (user sends new message, `/stop` command, or signal):
- The API thread is abandoned (response discarded)
- The agent can process the new input or shut down cleanly
- No partial response is injected into conversation history

## Tool Execution

### Sequential vs Concurrent

When the model returns tool calls:

- **Single tool call** → executed directly in the main thread
- **Multiple tool calls** → executed concurrently via `ThreadPoolExecutor`
  - Exception: tools marked as interactive (e.g., `clarify`) force sequential execution
  - Results are reinserted in the original tool call order regardless of completion order

### Execution Flow

```text
for each tool_call in response.tool_calls:
    1. Resolve handler from tools/registry.py
    2. Fire pre_tool_call plugin hook
    3. Check if dangerous command (tools/approval.py)
       - If dangerous: invoke approval_callback, wait for user
    4. Execute handler with args + task_id
    5. Fire post_tool_call plugin hook
    6. Append {"role": "tool", "content": result} to history
```

### Agent-Level Tools

Some tools are intercepted by `run_agent.py` *before* reaching `handle_function_call()`:

| Tool | Why intercepted |
|------|--------------------|
| `todo` | Reads/writes agent-local task state |
| `memory` | Writes to persistent memory files with character limits |
| `session_search` | Queries session history via the agent's session DB |
| `delegate_task` | Spawns subagent(s) with isolated context |

These tools modify agent state directly and return synthetic tool results without going through the registry.

## Callback Surfaces

`AIAgent` supports platform-specific callbacks that enable real-time progress in the CLI, gateway, and ACP integrations:

| Callback | When fired | Used by |
|----------|-----------|---------|
| `tool_progress_callback` | Before/after each tool execution | CLI spinner, gateway progress messages |
| `thinking_callback` | When model starts/stops thinking | CLI "thinking..." indicator |
| `reasoning_callback` | When model returns reasoning content | CLI reasoning display, gateway reasoning blocks |
| `clarify_callback` | When `clarify` tool is called | CLI input prompt, gateway interactive message |
| `step_callback` | After each complete agent turn | Gateway step tracking, ACP progress |
| `stream_delta_callback` | Each streaming token (when enabled) | CLI streaming display |
| `tool_gen_callback` | When tool call is parsed from stream | CLI tool preview in spinner |
| `status_callback` | State changes (thinking, executing, etc.) | ACP status updates |

## Budget and Fallback Behavior

### Iteration Budget

The agent tracks iterations via `IterationBudget`:

- Default: 90 iterations (configurable via `agent.max_turns`)
- Each agent gets its own budget. Subagents get independent budgets capped at `delegation.max_iterations` (default 50) — total iterations across parent + subagents can exceed the parent's cap
- At 100%, the agent stops and returns a summary of work done

### Fallback Model

When the primary model fails (429 rate limit, 5xx server error, 401/403 auth error):

1. Check `fallback_providers` list in config
2. Try each fallback in order
3. On success, continue the conversation with the new provider
4. On 401/403, attempt credential refresh before failing over

The fallback system also covers auxiliary tasks independently — vision, compression, and web extraction each have their own fallback chain configurable via the `auxiliary.*` config section.

## Compression and Persistence

### When Compression Triggers

- **Preflight** (before API call): If conversation exceeds 50% of model's context window
- **Gateway auto-compression**: If conversation exceeds 85% (more aggressive, runs between turns)

### What Happens During Compression

1. Memory is flushed to disk first (preventing data loss)
2. Middle conversation turns are summarized into a compact summary
3. The last N messages are preserved intact (`compression.protect_last_n`, default: 20)
4. Tool call/result message pairs are kept together (never split)
5. A new session lineage ID is generated (compression creates a "child" session)

### Session Persistence

After each turn:
- Messages are saved to the session store (SQLite via `hermes_state.py`)
- Memory changes are flushed to `MEMORY.md` / `USER.md`
- The session can be resumed later via `/resume` or `hermes chat --resume`

## Key Source Files

| File | Purpose |
|------|---------|
| `run_agent.py` | AIAgent class — the complete agent loop |
| `agent/prompt_builder.py` | System prompt assembly from memory, skills, context files, personality |
| `agent/context_engine.py` | ContextEngine ABC — pluggable context management |
| `agent/context_compressor.py` | Default engine — lossy summarization algorithm |
| `agent/prompt_caching.py` | Anthropic prompt caching markers and cache metrics |
| `agent/auxiliary_client.py` | Auxiliary LLM client for side tasks (vision, summarization) |
| `model_tools.py` | Tool schema collection, `handle_function_call()` dispatch |

## Related Docs

- [Provider Runtime Resolution](./provider-runtime.md)
- [Prompt Assembly](./prompt-assembly.md)
- [Context Compression & Prompt Caching](./context-compression-and-caching.md)
- [Tools Runtime](./tools-runtime.md)
- [Architecture Overview](./architecture.md)

---

# SOURCE: website/docs/developer-guide/adding-tools.md

---
sidebar_position: 2
title: "Adding Tools"
description: "How to add a new tool to Hermes Agent — schemas, handlers, registration, and toolsets"
---

# Adding Tools

Before writing a tool, ask yourself: **should this be a [skill](creating-skills.md) instead?**

:::warning Built-in Core Tools Only
This page is for adding a **built-in Hermes tool** to the repository itself.
If you want a personal, project-local, or otherwise custom tool without
modifying Hermes core, use the plugin route instead:

- [Plugins](/user-guide/features/plugins)
- [Build a Hermes Plugin](/guides/build-a-hermes-plugin)

Default to plugins for most custom tool creation. Only follow this page when
you explicitly want to ship a new built-in tool in `tools/` and `toolsets.py`.
:::

Make it a **Skill** when the capability can be expressed as instructions + shell commands + existing tools (arXiv search, git workflows, Docker management, PDF processing).

Make it a **Tool** when it requires end-to-end integration with API keys, custom processing logic, binary data handling, or streaming (browser automation, TTS, vision analysis).

## Overview

Adding a tool touches **2 files**:

1. **`tools/your_tool.py`** — handler, schema, check function, `registry.register()` call
2. **`toolsets.py`** — add tool name to `_HERMES_CORE_TOOLS` (or a specific toolset)

Any `tools/*.py` file with a top-level `registry.register()` call is auto-discovered at startup — no manual import list required.

## Step 1: Create the Built-in Tool File

Every tool file follows the same structure:

```python
# tools/weather_tool.py
"""Weather Tool -- look up current weather for a location."""

import json
import os
import logging

logger = logging.getLogger(__name__)


# --- Availability check ---

def check_weather_requirements() -> bool:
    """Return True if the tool's dependencies are available."""
    return bool(os.getenv("WEATHER_API_KEY"))


# --- Handler ---

def weather_tool(location: str, units: str = "metric") -> str:
    """Fetch weather for a location. Returns JSON string."""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "WEATHER_API_KEY not configured"})
    try:
        # ... call weather API ...
        return json.dumps({"location": location, "temp": 22, "units": units})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Schema ---

WEATHER_SCHEMA = {
    "name": "weather",
    "description": "Get current weather for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or coordinates (e.g. 'London' or '51.5,-0.1')"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "Temperature units (default: metric)",
                "default": "metric"
            }
        },
        "required": ["location"]
    }
}


# --- Registration ---

from tools.registry import registry

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool(
        location=args.get("location", ""),
        units=args.get("units", "metric")),
    check_fn=check_weather_requirements,
    requires_env=["WEATHER_API_KEY"],
)
```

### Key Rules

:::danger Important
- Handlers **MUST** return a JSON string (via `json.dumps()`), never raw dicts
- Errors **MUST** be returned as `{"error": "message"}`, never raised as exceptions
- The `check_fn` is called when building tool definitions — if it returns `False`, the tool is silently excluded
- The `handler` receives `(args: dict, **kwargs)` where `args` is the LLM's tool call arguments
:::

## Step 2: Add the Built-in Tool to a Toolset

In `toolsets.py`, add the tool name:

```python
# If it should be available on all platforms (CLI + messaging):
_HERMES_CORE_TOOLS = [
    ...
    "weather",  # <-- add here
]

# Or create a new standalone toolset:
"weather": {
    "description": "Weather lookup tools",
    "tools": ["weather"],
    "includes": []
},
```

## ~~Step 3: Add Discovery Import~~ (No longer needed)

Tool modules with a top-level `registry.register()` call are auto-discovered by `discover_builtin_tools()` in `tools/registry.py`. No manual import list to maintain — just create your file in `tools/` and it's picked up at startup.

## Async Handlers

If your handler needs async code, mark it with `is_async=True`:

```python
async def weather_tool_async(location: str) -> str:
    async with aiohttp.ClientSession() as session:
        ...
    return json.dumps(result)

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool_async(args.get("location", "")),
    check_fn=check_weather_requirements,
    is_async=True,  # registry calls _run_async() automatically
)
```

The registry handles async bridging transparently — you never call `asyncio.run()` yourself.

## Handlers That Need task_id

Tools that manage per-session state receive `task_id` via `**kwargs`:

```python
def _handle_weather(args, **kw):
    task_id = kw.get("task_id")
    return weather_tool(args.get("location", ""), task_id=task_id)

registry.register(
    name="weather",
    ...
    handler=_handle_weather,
)
```

## Agent-Loop Intercepted Tools

Some tools (`todo`, `memory`, `session_search`, `delegate_task`) need access to per-session agent state. These are intercepted by `run_agent.py` before reaching the registry. The registry still holds their schemas, but `dispatch()` returns a fallback error if the intercept is bypassed.

## Optional: Setup Wizard Integration

If your tool requires an API key, add it to `hermes_cli/config.py`:

```python
OPTIONAL_ENV_VARS = {
    ...
    "WEATHER_API_KEY": {
        "description": "Weather API key for weather lookup",
        "prompt": "Weather API key",
        "url": "https://weatherapi.com/",
        "tools": ["weather"],
        "password": True,
    },
}
```

## Checklist

- [ ] Tool file created with handler, schema, check function, and registration
- [ ] Added to appropriate toolset in `toolsets.py`
- [ ] Confirmed this really should be a built-in/core tool and not a plugin
- [ ] Handler returns JSON strings, errors returned as `{"error": "..."}`
- [ ] Optional: API key added to `OPTIONAL_ENV_VARS` in `hermes_cli/config.py`
- [ ] Optional: Added to `toolset_distributions.py` for batch processing
- [ ] Tested with `hermes chat -q "Use the weather tool for London"`

---

# SOURCE: website/docs/developer-guide/adding-platform-adapters.md

---
sidebar_position: 9
---

# Adding a Platform Adapter

This guide covers adding a new messaging platform to the Hermes gateway. A platform adapter connects Hermes to an external messaging service (Telegram, Discord, WeCom, etc.) so users can interact with the agent through that service.

:::tip
There are two ways to add a platform:
- **Plugin** (recommended for community/third-party): Drop a plugin directory into `~/.hermes/plugins/` — zero core code changes needed. See [Plugin Path](#plugin-path-recommended) below.
- **Built-in**: Modify 20+ files across code, config, and docs. Use the [Built-in Checklist](#step-by-step-checklist-built-in-path) below.
:::

## Architecture Overview

```
User ↔ Messaging Platform ↔ Platform Adapter ↔ Gateway Runner ↔ AIAgent
```

Every adapter extends `BasePlatformAdapter` from `gateway/platforms/base.py` and implements:

- **`connect()`** — Establish connection (WebSocket, long-poll, HTTP server, etc.) *(abstract)*
- **`disconnect()`** — Clean shutdown *(abstract)*
- **`send()`** — Send a text message to a chat *(abstract)*
- **`send_typing()`** — Show typing indicator (optional override)
- **`get_chat_info()`** — Return chat metadata (optional override)

Inbound messages are received by the adapter and forwarded via `self.handle_message(event)`, which the base class routes to the gateway runner.

## Plugin Path (Recommended)

The plugin system lets you add a platform adapter without modifying any core Hermes code. Your plugin is a directory with two files:

```
~/.hermes/plugins/my-platform/
  plugin.yaml      # Plugin metadata
  adapter.py       # Adapter class + register() entry point
```

### plugin.yaml

Plugin metadata. The `requires_env` and `optional_env` blocks auto-populate `hermes config` UI entries (see [Surfacing Env Vars](#surfacing-env-vars-in-hermes-config) below).

```yaml
name: my-platform
label: My Platform
kind: platform
version: 1.0.0
description: My custom messaging platform adapter
author: Your Name
requires_env:
  - MY_PLATFORM_TOKEN          # bare string works
  - name: MY_PLATFORM_CHANNEL  # or rich dict for better UX
    description: "Channel to join"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery"
    password: false
```

### adapter.py

```python
import os
from gateway.platforms.base import (
    BasePlatformAdapter, SendResult, MessageEvent, MessageType,
)
from gateway.config import Platform, PlatformConfig


class MyPlatformAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform("my_platform"))
        extra = config.extra or {}
        self.token = os.getenv("MY_PLATFORM_TOKEN") or extra.get("token", "")

    async def connect(self) -> bool:
        # Connect to the platform API, start listeners
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # Send message via platform API
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}


def check_requirements() -> bool:
    return bool(os.getenv("MY_PLATFORM_TOKEN"))


def validate_config(config) -> bool:
    extra = getattr(config, "extra", {}) or {}
    return bool(os.getenv("MY_PLATFORM_TOKEN") or extra.get("token"))


def _env_enablement() -> dict | None:
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {"chat_id": home, "name": "Home"}
    return seed


def register(ctx):
    """Plugin entry point — called by the Hermes plugin system."""
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        required_env=["MY_PLATFORM_TOKEN"],
        install_hint="pip install my-platform-sdk",
        # Env-driven auto-configuration — seeds PlatformConfig.extra from
        # env vars before adapter construction. See "Env-Driven Auto-
        # Configuration" section below.
        env_enablement_fn=_env_enablement,
        # Cron home-channel delivery support. Lets deliver=my_platform cron
        # jobs route without editing cron/scheduler.py. See "Cron Delivery"
        # section below.
        cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
        # Per-platform user authorization env vars
        allowed_users_env="MY_PLATFORM_ALLOWED_USERS",
        allow_all_env="MY_PLATFORM_ALLOW_ALL_USERS",
        # Message length limit for smart chunking (0 = no limit)
        max_message_length=4000,
        # LLM guidance injected into system prompt
        platform_hint=(
            "You are chatting via My Platform. "
            "It supports markdown formatting."
        ),
        # Display
        emoji="💬",
    )

    # Optional: register platform-specific tools
    ctx.register_tool(
        name="my_platform_search",
        toolset="my_platform",
        schema={...},
        handler=my_search_handler,
    )
```

### Configuration

Users configure the platform in `config.yaml`:

```yaml
gateway:
  platforms:
    my_platform:
      enabled: true
      extra:
        token: "..."
        channel: "#general"
```

Or via environment variables (which the adapter reads in `__init__`).

### What the Plugin System Handles Automatically

When you call `ctx.register_platform()`, the following integration points are handled for you — no core code changes needed:

| Integration point | How it works |
|---|---|
| Gateway adapter creation | Registry checked before built-in if/elif chain |
| Config parsing | `Platform._missing_()` accepts any platform name |
| Connected platform validation | Registry `validate_config()` called |
| User authorization | `allowed_users_env` / `allow_all_env` checked |
| Env-only auto-enable | `env_enablement_fn` seeds `PlatformConfig.extra` + `home_channel` |
| YAML config bridge | `apply_yaml_config_fn` translates `config.yaml` keys into env vars / extras |
| Cron delivery | `cron_deliver_env_var` makes `deliver=<name>` work |
| `hermes config` UI entries | `requires_env` / `optional_env` in `plugin.yaml` auto-populate |
| send engine (`tools/send_message_tool.py`) | Routes through live gateway adapter |
| Webhook cross-platform delivery | Registry checked for known platforms |
| `/update` command access | `allow_update_command` flag |
| Channel directory | Plugin platforms included in enumeration |
| System prompt hints | `platform_hint` injected into LLM context |
| Message chunking | `max_message_length` for smart splitting |
| PII redaction | `pii_safe` flag |
| `hermes status` | Shows plugin platforms with `(plugin)` tag |
| `hermes gateway setup` | Plugin platforms appear in setup menu |
| `hermes tools` / `hermes skills` | Plugin platforms in per-platform config |
| Token lock (multi-profile) | Use `acquire_scoped_lock()` in your `connect()` |
| Orphaned config warning | Descriptive log when plugin is missing |

## Env-Driven Auto-Configuration

Most users set up a platform by dropping env vars into `~/.hermes/.env` rather than editing `config.yaml`. The `env_enablement_fn` hook lets your plugin pick those env vars up **before** the adapter is constructed, so `hermes gateway status`, `get_connected_platforms()`, and cron delivery see the correct state without instantiating the platform SDK.

```python
def _env_enablement() -> dict | None:
    """Seed PlatformConfig.extra from env vars.

    Called by the platform registry during load_gateway_config().
    Return None when the platform isn't minimally configured — the
    caller then skips auto-enabling. Return a dict to seed extras.

    The special 'home_channel' key is extracted and becomes a proper
    HomeChannel dataclass on the PlatformConfig; every other key is
    merged into PlatformConfig.extra.
    """
    token = os.getenv("MY_PLATFORM_TOKEN", "").strip()
    channel = os.getenv("MY_PLATFORM_CHANNEL", "").strip()
    if not (token and channel):
        return None
    seed = {"token": token, "channel": channel}
    home = os.getenv("MY_PLATFORM_HOME_CHANNEL")
    if home:
        seed["home_channel"] = {
            "chat_id": home,
            "name": os.getenv("MY_PLATFORM_HOME_CHANNEL_NAME", "Home"),
        }
    return seed


def register(ctx):
    ctx.register_platform(
        name="my_platform",
        label="My Platform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        validate_config=validate_config,
        env_enablement_fn=_env_enablement,
        # ... other fields
    )
```


## YAML→env Config Bridge

Some users prefer setting `config.yaml` keys (`my_platform.require_mention`, `my_platform.allowed_channels`, etc.) over env vars. The `apply_yaml_config_fn` hook lets your plugin own this translation instead of forcing core `gateway/config.py` to know your platform's YAML schema.

```python
import os

def _apply_yaml_config(yaml_cfg: dict, platform_cfg: dict) -> dict | None:
    """Translate config.yaml `my_platform:` keys into env vars / extras.

    yaml_cfg     — the full top-level parsed config.yaml dict
    platform_cfg — the platform's own sub-dict (yaml_cfg.get("my_platform", {}))

    May mutate os.environ directly (use `not os.getenv(...)` guards to
    preserve env > YAML precedence) and/or return a dict to merge into
    PlatformConfig.extra. Return None or {} for no extras.
    """
    if "require_mention" in platform_cfg and not os.getenv("MY_PLATFORM_REQUIRE_MENTION"):
        os.environ["MY_PLATFORM_REQUIRE_MENTION"] = str(platform_cfg["require_mention"]).lower()
    allowed = platform_cfg.get("allowed_channels")
    if allowed is not None and not os.getenv("MY_PLATFORM_ALLOWED_CHANNELS"):
        if isinstance(allowed, list):
            allowed = ",".join(str(v) for v in allowed)
        os.environ["MY_PLATFORM_ALLOWED_CHANNELS"] = str(allowed)
    return None  # nothing extra to merge into PlatformConfig.extra

def register(ctx):
    ctx.register_platform(
        name="my_platform",
        ...,
        apply_yaml_config_fn=_apply_yaml_config,
    )
```

The hook is invoked during `load_gateway_config()` after the generic shared-key loop (which handles common keys like `unauthorized_dm_behavior`, `notice_delivery`, `reply_prefix`, `require_mention`, etc.) and before `_apply_env_overrides()`, so your plugin only needs to bridge **platform-specific** keys.

Exceptions raised by the hook are swallowed and logged at debug level — a misbehaving plugin never aborts gateway config load.


## Cron Delivery

To let `deliver=my_platform` cron jobs route to a configured home channel, set `cron_deliver_env_var` to the env var name that holds the default chat/room/channel ID:

```python
ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
)
```

The scheduler reads this env var when resolving the home target for `deliver=my_platform` jobs, and also treats the platform as a valid cron target in `_KNOWN_DELIVERY_PLATFORMS`-style checks. If your `env_enablement_fn` seeds a `home_channel` dict (see above), that takes precedence — `cron_deliver_env_var` is the fallback for cron jobs that run before env seeding.

### Out-of-process cron delivery

`cron_deliver_env_var` makes your platform a recognized `deliver=` target. To make the actual send succeed when the cron job runs in a separate process from the gateway (i.e., `hermes cron run` separate from `hermes gateway`), register a `standalone_sender_fn`:

```python
async def _standalone_send(
    pconfig,
    chat_id,
    message,
    *,
    thread_id=None,
    media_files=None,
    force_document=False,
):
    """Open an ephemeral connection / acquire a fresh token, send, and close."""
    # ... open connection, send message, return result ...
    return {"success": True, "message_id": "..."}
    # or {"error": "..."}

ctx.register_platform(
    name="my_platform",
    ...
    cron_deliver_env_var="MY_PLATFORM_HOME_CHANNEL",
    standalone_sender_fn=_standalone_send,
)
```

Why this hook is necessary: built-in platforms (Telegram, Discord, Slack, etc.) ship direct REST helpers in `tools/send_message_tool.py` so cron can deliver without holding the gateway in the same process. Plugin platforms historically depended on `_gateway_runner_ref()`, which returns `None` outside the gateway process, so without `standalone_sender_fn` the cron-side send fails with `No live adapter for platform '<name>'`.

The function receives the same `pconfig` and `chat_id` that the live adapter would, plus optional `thread_id`, `media_files`, and `force_document` keyword arguments. Returning `{"success": True, "message_id": ...}` is treated as a successful delivery; returning `{"error": "..."}` surfaces the message in cron's `delivery_errors`. Exceptions raised inside the function are caught by the dispatcher and reported as `Plugin standalone send failed: <reason>`. Reference implementations live in `plugins/platforms/{irc,teams,google_chat}/adapter.py`.

## Surfacing Env Vars in `hermes config`

`hermes_cli/config.py` scans `plugins/platforms/*/plugin.yaml` at import time and auto-populates `OPTIONAL_ENV_VARS` from `requires_env` and (optional) `optional_env` blocks. Use the rich-dict form to contribute proper descriptions, prompts, password flags, and URLs — the CLI setup UI picks them up for free.

```yaml
# plugins/platforms/my_platform/plugin.yaml
name: my_platform-platform
label: My Platform
kind: platform
version: 1.0.0
description: >
  My Platform gateway adapter for Hermes Agent.
author: Your Name
requires_env:
  - name: MY_PLATFORM_TOKEN
    description: "Bot API token from the My Platform console"
    prompt: "My Platform bot token"
    url: "https://my-platform.example.com/bots"
    password: true
  - name: MY_PLATFORM_CHANNEL
    description: "Channel to join (e.g. #hermes)"
    prompt: "Channel"
    password: false
optional_env:
  - name: MY_PLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery (defaults to MY_PLATFORM_CHANNEL)"
    prompt: "Home channel (or empty)"
    password: false
  - name: MY_PLATFORM_ALLOWED_USERS
    description: "Comma-separated user IDs allowed to talk to the bot"
    prompt: "Allowed users (comma-separated)"
    password: false
```

**Supported dict keys:** `name` (required), `description`, `prompt`, `url`, `password` (bool; auto-detected from `*_TOKEN` / `*_SECRET` / `*_KEY` / `*_PASSWORD` / `*_JSON` suffix when omitted), `category` (defaults to `"messaging"`).

Bare-string entries (`- MY_PLATFORM_TOKEN`) still work — they get a generic description auto-derived from the plugin's `label`. If a hardcoded entry for the same var already exists in `OPTIONAL_ENV_VARS`, it wins (back-compat); the plugin.yaml form acts as the fallback.

## Platform-Specific Slow-LLM UX

Some platforms have constraints that change how a slow LLM response should be presented:

- **LINE** issues a single-use *reply token* that expires roughly 60 seconds after the inbound event. Replying with that token is free; falling back to the metered Push API is not. If the LLM hasn't finished by the deadline, the choice is "burn paid Push quota" or "do something cleverer with the reply token before it expires."
- **WhatsApp** marks a session inactive after 24h, after which only template messages are accepted.
- **SMS** has no concept of typing indicators or progressive updates — long responses just look like the bot is offline.

These are real constraints the base `BasePlatformAdapter` can't anticipate. The plugin surface intentionally leaves the room for an adapter to layer platform-specific UX on top of the base typing loop without expanding the kwarg list.

### Pattern: subclass `_keep_typing` to layer mid-flight UX

`BasePlatformAdapter._keep_typing` is the typing-indicator heartbeat — it runs as a background task while the LLM is generating, and is cancelled when the response is delivered. To layer a platform-specific behavior at a threshold (e.g. send a "still thinking" bubble at 45s), override `_keep_typing` in your adapter, schedule your own task alongside `super()._keep_typing()`, and tear it down in `finally`:

```python
class LineAdapter(BasePlatformAdapter):
    async def _keep_typing(self, chat_id: str, *args, **kwargs) -> None:
        if self.slow_response_threshold <= 0:
            await super()._keep_typing(chat_id, *args, **kwargs)
            return

        async def _fire_at_threshold() -> None:
            try:
                await asyncio.sleep(self.slow_response_threshold)
            except asyncio.CancelledError:
                raise
            # Platform-specific work here — for LINE, send a Template
            # Buttons "Get answer" bubble using the cached reply token
            # so the user can fetch the cached response later via a
            # fresh (free) reply token from the postback callback.
            await self._send_slow_response_button(chat_id)

        side_task = asyncio.create_task(_fire_at_threshold())
        try:
            await super()._keep_typing(chat_id, *args, **kwargs)
        finally:
            if not side_task.done():
                side_task.cancel()
                try:
                    await side_task
                except (asyncio.CancelledError, Exception):
                    pass
```

Key points:

- **Always `await super()._keep_typing(...)`.** The typing heartbeat is independently useful — don't replace it, layer on top of it.
- **Tear down the side task in `finally`.** When the LLM finishes (or `/stop` cancels the run), the gateway cancels the typing task. Your side task must observe that cancellation too, otherwise it lingers and may fire after the response was already delivered.
- **Pair with `interrupt_session_activity`** to resolve any orphan UX state when the user issues `/stop`. For LINE, this means transitioning the postback cache entry from `PENDING` to `ERROR` so the persistent "Get answer" button delivers a "Run was interrupted" message instead of looping.

### Pattern: subclass `send` to route through a cache instead of sending immediately

If your slow-response UX caches the response for later retrieval (LINE's postback flow), your `send` override needs to recognize three modes:

1. **Pending postback active for this chat** → cache the response under the request_id, don't send anything visible.
2. **System busy-ack** (`⚡ Interrupting`, `⏳ Queued`, `⏩ Steered`) → bypass the cache and send visibly so the user sees the gateway's response to their input.
3. **Normal response** → send via reply-token-or-push as usual.

```python
async def send(self, chat_id: str, content: str, **kw) -> SendResult:
    if _is_system_bypass(content):
        return await self._send_text_chunks(chat_id, content, force_push=False)
    pending_rid = self._pending_buttons.get(chat_id)
    if pending_rid:
        self._cache.set_ready(pending_rid, content)
        return SendResult(success=True, message_id=pending_rid)
    return await self._send_text_chunks(chat_id, content, force_push=False)
```

`_SYSTEM_BYPASS_PREFIXES` are the gateway's own busy-acknowledgment prefixes (`⚡`, `⏳`, `⏩`, `💾`). Always let those through visibly, regardless of cached UX state.

### When this pattern is appropriate

Use the typing-loop override approach when:

- The platform's outbound API has a hard time-window constraint (single-use reply token, expiring sticky session, etc.) AND
- A *visible mid-flight bubble* is acceptable UX on that platform.

Use the simpler `slow_response_threshold = 0` always-Push path when:

- The platform doesn't have a meaningful free vs. paid distinction, OR
- The user community prefers "loading… loading… DONE" silence-then-response over an interactive intermediate bubble.

LINE supports both: the threshold defaults to 45s for free postback fetch, and `LINE_SLOW_RESPONSE_THRESHOLD=0` reverts to "always Push fallback."

### Reference Implementation

See `plugins/platforms/line/adapter.py` for the full LINE postback implementation — a `RequestCache` state machine (`PENDING → READY → DELIVERED`, plus `ERROR` for `/stop`), a `_keep_typing` override that fires the Template Buttons bubble at threshold, a `send` override that routes through the cache, and an `interrupt_session_activity` override that resolves orphan PENDING entries.

### Reference Implementations (Plugin Path)

See `plugins/platforms/irc/` in the repo for a complete working example — a full async IRC adapter with zero external dependencies. `plugins/platforms/teams/` covers Bot Framework / Adaptive Cards, `plugins/platforms/google_chat/` covers OAuth-based REST APIs, and `plugins/platforms/line/` covers webhook-driven Messaging APIs with platform-specific slow-LLM UX.

---

## Step-by-Step Checklist (Built-in Path)

:::note
This checklist is for adding a platform directly to the Hermes core codebase — typically done by core contributors for officially supported platforms. Community/third-party platforms should use the [Plugin Path](#plugin-path-recommended) above.
:::

### 1. Platform Enum

Add your platform to the `Platform` enum in `gateway/config.py`:

```python
class Platform(str, Enum):
    # ... existing platforms ...
    NEWPLAT = "newplat"
```

### 2. Adapter File

Create `plugins/platforms/newplat/adapter.py`:

```python
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter, MessageEvent, MessageType, SendResult,
)

def check_newplat_requirements() -> bool:
    """Return True if dependencies are available."""
    return SOME_SDK_AVAILABLE

class NewPlatAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.NEWPLAT)
        # Read config from config.extra dict
        extra = config.extra or {}
        self._api_key = extra.get("api_key") or os.getenv("NEWPLAT_API_KEY", "")

    async def connect(self) -> bool:
        # Set up connection, start polling/webhook
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._running = False
        self._mark_disconnected()

    async def send(self, chat_id, content, reply_to=None, metadata=None):
        # Send message via platform API
        return SendResult(success=True, message_id="...")

    async def get_chat_info(self, chat_id):
        return {"name": chat_id, "type": "dm"}
```

For inbound messages, build a `MessageEvent` and call `self.handle_message(event)`:

```python
source = self.build_source(
    chat_id=chat_id,
    chat_name=name,
    chat_type="dm",  # or "group"
    user_id=user_id,
    user_name=user_name,
)
event = MessageEvent(
    text=content,
    message_type=MessageType.TEXT,
    source=source,
    message_id=msg_id,
)
await self.handle_message(event)
```

### 3. Gateway Config (`gateway/config.py`)

Three touchpoints:

1. **`get_connected_platforms()`** — Add a check for your platform's required credentials
2. **`load_gateway_config()`** — Add token env map entry: `Platform.NEWPLAT: "NEWPLAT_TOKEN"`
3. **`_apply_env_overrides()`** — Map all `NEWPLAT_*` env vars to config

### 4. Gateway Runner (`gateway/run.py`)

Five touchpoints:

1. **`_create_adapter()`** — Add an `elif platform == Platform.NEWPLAT:` branch
2. **`_is_user_authorized()` allowed_users map** — `Platform.NEWPLAT: "NEWPLAT_ALLOWED_USERS"`
3. **`_is_user_authorized()` allow_all map** — `Platform.NEWPLAT: "NEWPLAT_ALLOW_ALL_USERS"`
4. **Early env check `_any_allowlist` tuple** — Add `"NEWPLAT_ALLOWED_USERS"`
5. **Early env check `_allow_all` tuple** — Add `"NEWPLAT_ALLOW_ALL_USERS"`
6. **`_UPDATE_ALLOWED_PLATFORMS` frozenset** — Add `Platform.NEWPLAT`

### 5. Cross-Platform Delivery

1. **`gateway/platforms/webhook.py`** — Add `"newplat"` to the delivery type tuple
2. **`cron/scheduler.py`** — Add to `_KNOWN_DELIVERY_PLATFORMS` frozenset and `_deliver_result()` platform map

### 6. CLI Integration

1. **`hermes_cli/config.py`** — Add all `NEWPLAT_*` vars to `_EXTRA_ENV_KEYS`
2. **`hermes_cli/gateway.py`** — Add entry to `_PLATFORMS` list with key, label, emoji, token_var, setup_instructions, and vars
3. **`hermes_cli/platforms.py`** — Add `PlatformInfo` entry with label and default_toolset (used by `skills_config` and `tools_config` TUIs)
4. **`hermes_cli/setup.py`** — Add `_setup_newplat()` function (can delegate to `gateway.py`) and add tuple to the messaging platforms list
5. **`hermes_cli/status.py`** — Add platform detection entry: `"NewPlat": ("NEWPLAT_TOKEN", "NEWPLAT_HOME_CHANNEL")`
6. **`hermes_cli/dump.py`** — Add `"newplat": "NEWPLAT_TOKEN"` to platform detection dict

### 7. Tools

1. **`tools/send_message_tool.py`** — Add `"newplat": Platform.NEWPLAT` to platform map
2. **`tools/cronjob_tools.py`** — Add `newplat` to the delivery target description string

### 8. Toolsets

1. **`toolsets.py`** — Add `"hermes-newplat"` toolset definition with `_HERMES_CORE_TOOLS`
2. **`toolsets.py`** — Add `"hermes-newplat"` to the `"hermes-gateway"` includes list

### 9. Optional: Platform Hints

**`agent/prompt_builder.py`** — If your platform has specific rendering limitations (no markdown, message length limits, etc.), add an entry to the `_PLATFORM_HINTS` dict. This injects platform-specific guidance into the system prompt:

```python
_PLATFORM_HINTS = {
    # ...
    "newplat": (
        "You are chatting via NewPlat. It supports markdown formatting "
        "but has a 4000-character message limit."
    ),
}
```

Not all platforms need hints — only add one if the agent's behavior should differ.

### 10. Tests

Create `tests/gateway/test_newplat.py` covering:

- Adapter construction from config
- Message event building
- Send method (mock the external API)
- Platform-specific features (encryption, routing, etc.)

### 11. Documentation

| File | What to add |
|------|-------------|
| `website/docs/user-guide/messaging/newplat.md` | Full platform setup page |
| `website/docs/user-guide/messaging/index.md` | Platform comparison table, architecture diagram, toolsets table, security section, next-steps link |
| `website/docs/reference/environment-variables.md` | All NEWPLAT_* env vars |
| `website/docs/reference/toolsets-reference.md` | hermes-newplat toolset |
| `website/docs/integrations/index.md` | Platform link |
| `website/sidebars.ts` | Sidebar entry for the docs page |
| `website/docs/developer-guide/architecture.md` | Adapter count + listing |
| `website/docs/developer-guide/gateway-internals.md` | Adapter file listing |

## Parity Audit

Before marking a new platform PR as complete, run a parity audit against an established platform:

```bash
# Find every .py file mentioning the reference platform
search_files "bluebubbles" output_mode="files_only" file_glob="*.py"

# Find every .py file mentioning the new platform
search_files "newplat" output_mode="files_only" file_glob="*.py"

# Any file in the first set but not the second is a potential gap
```

Repeat for `.md` and `.ts` files. Investigate each gap — is it a platform enumeration (needs updating) or a platform-specific reference (skip)?

## Common Patterns

### Long-Poll Adapters

If your adapter uses long-polling (like Telegram or Weixin), use a polling loop task:

```python
async def connect(self):
    self._poll_task = asyncio.create_task(self._poll_loop())
    self._mark_connected()

async def _poll_loop(self):
    while self._running:
        messages = await self._fetch_updates()
        for msg in messages:
            await self.handle_message(self._build_event(msg))
```

### Callback/Webhook Adapters

If the platform pushes messages to your endpoint (like WeCom Callback), run an HTTP server:

```python
async def connect(self):
    self._app = web.Application()
    self._app.router.add_post("/callback", self._handle_callback)
    # ... start aiohttp server
    self._mark_connected()

async def _handle_callback(self, request):
    event = self._build_event(await request.text())
    await self._message_queue.put(event)
    return web.Response(text="success")  # Acknowledge immediately
```

For platforms with tight response deadlines (e.g., WeCom's 5-second limit), always acknowledge immediately and deliver the agent's reply proactively via API later. Agent sessions run 3–30 minutes — inline replies within a callback response window are not feasible.

### Token Locks

If the adapter holds a persistent connection with a unique credential, add a scoped lock to prevent two profiles from using the same credential:

```python
from gateway.status import acquire_scoped_lock, release_scoped_lock

async def connect(self):
    if not acquire_scoped_lock("newplat", self._token):
        logger.error("Token already in use by another profile")
        return False
    # ... connect

async def disconnect(self):
    release_scoped_lock("newplat", self._token)
```

## Reference Implementations

| Adapter | Pattern | Complexity | Good reference for |
|---------|---------|------------|-------------------|
| `bluebubbles.py` | REST + webhook | Medium | Simple REST API integration |
| `weixin.py` | Long-poll + CDN | High | Media handling, encryption |
| `wecom_callback.py` | Callback/webhook | Medium | HTTP server, AES crypto, multi-app |
| `plugins/platforms/irc/adapter.py` | Long-poll + IRC protocol | High | Full-featured plugin adapter with scoped token lock |

---

# SOURCE: website/docs/developer-guide/programmatic-integration.md

---
sidebar_position: 8
title: "Programmatic Integration"
description: "Three protocols for driving hermes-agent from external programs: ACP, the TUI gateway JSON-RPC, and the OpenAI-compatible HTTP API"
---

# Programmatic Integration

Hermes ships three protocols for driving the agent from external programs — IDE plugins, custom UIs, CI pipelines, embedded sub-agents. Pick the one that matches your transport and consumer.

| Protocol | Transport | Best for | Defined by |
|----------|-----------|----------|------------|
| **ACP** | JSON-RPC over stdio | IDE clients (VS Code, Zed, JetBrains) that already speak the [Agent Client Protocol](https://github.com/zed-industries/agent-client-protocol) | `acp_adapter/` |
| **TUI gateway** | JSON-RPC over stdio (or WebSocket) | Custom hosts that want fine-grained control of sessions, slash commands, approvals, and streaming events | `tui_gateway/server.py` |
| **API server** | HTTP + Server-Sent Events | OpenAI-compatible frontends (Open WebUI, LobeChat, LibreChat…) and language-agnostic web clients | `gateway/platforms/api_server.py` |

All three drive the same `AIAgent` core. They differ only in wire format and which set of features they expose.

---

## ACP (Agent Client Protocol)

`hermes acp` starts a stdio JSON-RPC server speaking ACP. Used in production by VS Code (Zed Industries' ACP extension), Zed, and any JetBrains IDE with an ACP plugin.

Capabilities exposed: session creation, prompt submission, streaming agent message chunks, tool-call events, permission requests, session fork, cancel, and authentication. Tool output is rendered into ACP `Diff`/`ToolCall` content blocks the IDE understands.

Full lifecycle, event bridge, and approval flow: [ACP Internals](./acp-internals).

```bash
hermes acp                  # serve ACP on stdio
hermes acp --bootstrap      # print install snippet for an ACP-capable IDE
```

---

## TUI Gateway JSON-RPC

`tui_gateway/server.py` is the protocol the Ink TUI (`hermes --tui`) and the embedded dashboard PTY bridge talk to. Any external host can speak the same protocol over stdio (or WebSocket via `tui_gateway/ws.py`).

### Method catalog (selected)

```
prompt.submit           prompt.background       session.steer
session.create          session.list            session.active_list
session.activate        session.close           session.interrupt
session.history         session.compress        session.branch
session.title           session.usage           session.status
clarify.respond         sudo.respond            secret.respond
approval.respond        config.set / config.get commands.catalog
command.resolve         command.dispatch        cli.exec
reload.mcp              reload.env              process.stop
delegation.status       subagent.interrupt      spawn_tree.save / list / load
terminal.resize         clipboard.paste         image.attach
```

`session.active_list`, `session.activate`, and `session.close` are the process-local live-session controls used by the TUI session switcher. Use `session.list` / `/resume` for saved transcript discovery; use the active-session methods only for sessions that are currently open in the TUI gateway process.

### Events streamed back

`message.delta`, `message.complete`, `tool.start`, `tool.progress`, `tool.complete`, `approval.request`, `clarify.request`, `sudo.request`, `secret.request`, `gateway.ready`, plus session lifecycle and error events.

### Pi-style RPC mapping

Every command in the Pi-mono RPC spec ([issue #360](https://github.com/NousResearch/hermes-agent/issues/360)) has a TUI-gateway equivalent:

| Pi command | Hermes equivalent |
|------------|-------------------|
| `prompt` | `prompt.submit` (or ACP `session/prompt`) |
| `steer` | `session.steer` |
| `follow_up` | `prompt.submit` queued after current turn |
| `abort` | `session.interrupt` |
| `set_model` | `command.dispatch` for `/model <provider:model>` (mid-session, persistent) |
| `compact` | `session.compress` |
| `get_state` | `session.status` |
| `get_messages` | `session.history` |
| `switch_session` | `session.resume` |
| `fork` | `session.branch` |
| `ui_request` / `ui_response` | `clarify.respond` / `sudo.respond` / `secret.respond` / `approval.respond` |

---

## OpenAI-Compatible API Server

`gateway/platforms/api_server.py` exposes hermes over HTTP for any client that already speaks the OpenAI format. Useful when you want a web frontend, a curl-driven CI runner, or a non-Python consumer.

Endpoints:

```
POST /v1/chat/completions        OpenAI Chat Completions (streaming via SSE)
POST /v1/responses               OpenAI Responses API (stateful)
POST /v1/runs                    Start a run, returns run_id (202)
GET  /v1/runs/{id}               Run status
GET  /v1/runs/{id}/events        SSE stream of lifecycle events
POST /v1/runs/{id}/approval      Resolve a pending approval
POST /v1/runs/{id}/stop          Interrupt the run
GET  /v1/capabilities            Machine-readable feature flags
GET  /v1/models                  Lists hermes-agent
GET  /health, /health/detailed
```

Setup, headers (`X-Hermes-Session-Id`, `X-Hermes-Session-Key`), and frontend wiring: [API Server](../user-guide/features/api-server).

---

## Which one should I use?

- **You're writing an IDE plugin and the IDE already speaks ACP** → ACP. Zero protocol work on the IDE side.
- **You're writing a custom desktop / web / TUI host and want every Hermes feature** (slash commands, approvals, clarify, multi-agent, session branching) → TUI gateway JSON-RPC.
- **You want any OpenAI-compatible frontend, a language-agnostic HTTP client, or curl-driven automation** → API server.
- **You want a Python in-process embed without a subprocess** → import `run_agent.AIAgent` directly. See [Agent Loop](./agent-loop).

---

## Model hot-swapping

Mid-session model switching works on every surface — it's the `/model` slash command under the hood.

- **CLI / TUI:** `/model claude-sonnet-4` or `/model openrouter:anthropic/claude-sonnet-4.6`
- **TUI gateway RPC:** `command.dispatch` with `{"command": "/model claude-sonnet-4"}`
- **ACP:** the IDE sends the slash command as a prompt; the agent dispatches it
- **API server:** include a `model` field in the request body or set `X-Hermes-Model`

Provider-aware resolution (the same model name picks the right format for whatever provider you're on) is built in. See `hermes_cli/model_switch.py`.

---

## A note on `--mode rpc`

Hermes does not have a `--mode rpc` flag. The three protocols above already cover the use cases — ACP for IDE-protocol clients, the TUI gateway for stdio JSON-RPC hosts, and the API server for HTTP. If you find a real gap that none of them fill, open an issue with the concrete consumer you're building.

---

# SOURCE: website/docs/guides/python-library.md

---
sidebar_position: 5
title: "Using Hermes as a Python Library"
description: "Embed AIAgent in your own Python scripts, web apps, or automation pipelines — no CLI required"
---

# Using Hermes as a Python Library

Hermes isn't just a CLI tool. You can import `AIAgent` directly and use it programmatically in your own Python scripts, web applications, or automation pipelines. This guide shows you how.

---

## Installation

Install Hermes directly from the repository:

```bash
pip install git+https://github.com/NousResearch/hermes-agent.git
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install git+https://github.com/NousResearch/hermes-agent.git
```

You can also pin it in your `requirements.txt`:

```text
hermes-agent @ git+https://github.com/NousResearch/hermes-agent.git
```

:::tip
The same environment variables used by the CLI are required when using Hermes as a library. At minimum, set `OPENROUTER_API_KEY` (or `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` if using direct provider access).
:::

---

## Basic Usage

The simplest way to use Hermes is the `chat()` method — pass a message, get a string back:

```python
from run_agent import AIAgent

agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    quiet_mode=True,
)
response = agent.chat("What is the capital of France?")
print(response)
```

`chat()` handles the full conversation loop internally — tool calls, retries, everything — and returns just the final text response.

:::warning
Always set `quiet_mode=True` when embedding Hermes in your own code. Without it, the agent prints CLI spinners, progress indicators, and other terminal output that will clutter your application's output.
:::

---

## Full Conversation Control

For more control over the conversation, use `run_conversation()` directly. It returns a dictionary with the full response, message history, and metadata:

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    quiet_mode=True,
)

result = agent.run_conversation(
    user_message="Search for recent Python 3.13 features",
    task_id="my-task-1",
)

print(result["final_response"])
print(f"Messages exchanged: {len(result['messages'])}")
```

The returned dictionary contains:
- **`final_response`** — The agent's final text reply
- **`messages`** — The complete message history (system, user, assistant, tool calls)

(The `task_id` you pass in is stored on the agent instance for VM isolation but isn't echoed back in the return dict.)

You can also pass a custom system message that overrides the ephemeral system prompt for that call:

```python
result = agent.run_conversation(
    user_message="Explain quicksort",
    system_message="You are a computer science tutor. Use simple analogies.",
)
```

---

## Configuring Tools

Control which toolsets the agent has access to using `enabled_toolsets` or `disabled_toolsets`:

```python
# Only enable web tools (browsing, search)
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    enabled_toolsets=["web"],
    quiet_mode=True,
)

# Enable everything except terminal access
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    disabled_toolsets=["terminal"],
    quiet_mode=True,
)
```

:::tip
Use `enabled_toolsets` when you want a minimal, locked-down agent (e.g., only web search for a research bot). Use `disabled_toolsets` when you want most capabilities but need to restrict specific ones (e.g., no terminal access in a shared environment).
:::

---

## Multi-turn Conversations

Maintain conversation state across multiple turns by passing the message history back in:

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    quiet_mode=True,
)

# First turn
result1 = agent.run_conversation("My name is Alice")
history = result1["messages"]

# Second turn — agent remembers the context
result2 = agent.run_conversation(
    "What's my name?",
    conversation_history=history,
)
print(result2["final_response"])  # "Your name is Alice."
```

The `conversation_history` parameter accepts the `messages` list from a previous result. The agent copies it internally, so your original list is never mutated.

---

## Saving Trajectories

Enable trajectory saving to capture conversations in ShareGPT format — useful for generating training data or debugging:

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4.6",
    save_trajectories=True,
    quiet_mode=True,
)

agent.chat("Write a Python function to sort a list")
# Saves to trajectory_samples.jsonl in ShareGPT format
```

Each conversation is appended as a single JSONL line, making it easy to collect datasets from automated runs.

---

## Custom System Prompts

Use `ephemeral_system_prompt` to set a custom system prompt that guides the agent's behavior but is **not** saved to trajectory files (keeping your training data clean):

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    ephemeral_system_prompt="You are a SQL expert. Only answer database questions.",
    quiet_mode=True,
)

response = agent.chat("How do I write a JOIN query?")
print(response)
```

This is ideal for building specialized agents — a code reviewer, a documentation writer, a SQL assistant — all using the same underlying tooling.

---

## Batch Processing

For running many prompts in parallel, Hermes includes `batch_runner.py`. It manages concurrent `AIAgent` instances with proper resource isolation:

```bash
python batch_runner.py --input prompts.jsonl --output results.jsonl
```

Each prompt gets its own `task_id` and isolated environment. If you need custom batch logic, you can build your own using `AIAgent` directly:

```python
import concurrent.futures
from run_agent import AIAgent

prompts = [
    "Explain recursion",
    "What is a hash table?",
    "How does garbage collection work?",
]

def process_prompt(prompt):
    # Create a fresh agent per task for thread safety
    agent = AIAgent(
        model="anthropic/claude-sonnet-4",
        quiet_mode=True,
        skip_memory=True,
    )
    return agent.chat(prompt)

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_prompt, prompts))

for prompt, result in zip(prompts, results):
    print(f"Q: {prompt}\nA: {result}\n")
```

:::warning
Always create a **new `AIAgent` instance per thread or task**. The agent maintains internal state (conversation history, tool sessions, iteration counters) that is not thread-safe to share.
:::

---

## Integration Examples

### FastAPI Endpoint

```python
from fastapi import FastAPI
from pydantic import BaseModel
from run_agent import AIAgent

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    model: str = "anthropic/claude-sonnet-4"

@app.post("/chat")
async def chat(request: ChatRequest):
    agent = AIAgent(
        model=request.model,
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
    )
    response = agent.chat(request.message)
    return {"response": response}
```

### Discord Bot

```python
import discord
from run_agent import AIAgent

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!hermes "):
        query = message.content[8:]
        agent = AIAgent(
            model="anthropic/claude-sonnet-4",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            platform="discord",
        )
        response = agent.chat(query)
        await message.channel.send(response[:2000])

client.run("YOUR_DISCORD_TOKEN")
```

### CI/CD Pipeline Step

```python
#!/usr/bin/env python3
"""CI step: auto-review a PR diff."""
import subprocess
from run_agent import AIAgent

diff = subprocess.check_output(["git", "diff", "main...HEAD"]).decode()

agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
    skip_context_files=True,
    skip_memory=True,
    disabled_toolsets=["terminal", "browser"],
)

review = agent.chat(
    f"Review this PR diff for bugs, security issues, and style problems:\n\n{diff}"
)
print(review)
```

---

## Key Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | `""` | Model in OpenRouter format (defaults to empty; resolved from your hermes config at runtime) |
| `quiet_mode` | `bool` | `False` | Suppress CLI output |
| `enabled_toolsets` | `List[str]` | `None` | Whitelist specific toolsets |
| `disabled_toolsets` | `List[str]` | `None` | Blacklist specific toolsets |
| `save_trajectories` | `bool` | `False` | Save conversations to JSONL |
| `ephemeral_system_prompt` | `str` | `None` | Custom system prompt (not saved to trajectories) |
| `max_iterations` | `int` | `90` | Max tool-calling iterations per conversation |
| `skip_context_files` | `bool` | `False` | Skip loading AGENTS.md files |
| `skip_memory` | `bool` | `False` | Disable persistent memory read/write |
| `api_key` | `str` | `None` | API key (falls back to env vars) |
| `base_url` | `str` | `None` | Custom API endpoint URL |
| `platform` | `str` | `None` | Platform hint (`"discord"`, `"telegram"`, etc.) |

---

## Important Notes

:::tip
- Set **`skip_context_files=True`** if you don't want `AGENTS.md` files from the working directory loaded into the system prompt.
- Set **`skip_memory=True`** to prevent the agent from reading or writing persistent memory — recommended for stateless API endpoints.
- The `platform` parameter (e.g., `"discord"`, `"telegram"`) injects platform-specific formatting hints so the agent adapts its output style.
:::

:::warning
- **Thread safety**: Create one `AIAgent` per thread or task. Never share an instance across concurrent calls.
- **Resource cleanup**: The agent automatically cleans up resources (terminal sessions, browser instances) when a conversation ends. If you're running in a long-lived process, ensure each conversation completes normally.
- **Iteration limits**: The default `max_iterations=90` is generous. For simple Q&A use cases, consider lowering it (e.g., `max_iterations=10`) to prevent runaway tool-calling loops and control costs.
:::
