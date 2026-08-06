<!-- Sections in this file (in order):
  - user-guide/features/plugins.md
  - user-guide/features/built-in-plugins.md
  - guides/build-a-hermes-plugin.md
  - user-guide/features/mcp.md
  - reference/mcp-config-reference.md
  - guides/use-mcp-with-hermes.md
  - user-guide/features/tool-search.md
-->


---

# SOURCE: website/docs/user-guide/features/plugins.md

---
sidebar_position: 11
sidebar_label: "Plugins"
title: "Plugins"
description: "Extend Hermes with custom tools, hooks, and integrations via the plugin system"
---

# Plugins

Hermes has a plugin system for adding custom tools, hooks, and integrations without modifying core code.

If you want to create a custom tool for yourself, your team, or one project,
this is usually the right path. The developer guide's
[Adding Tools](/developer-guide/adding-tools) page is for built-in Hermes
core tools that live in `tools/` and `toolsets.py`.

**→ [Build a Hermes Plugin](/guides/build-a-hermes-plugin)** — step-by-step guide with a complete working example.

## Quick overview

Drop a directory into `~/.hermes/plugins/` with a `plugin.yaml` and Python code:

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # manifest
├── __init__.py      # register() — wires schemas to handlers
├── schemas.py       # tool schemas (what the LLM sees)
└── tools.py         # tool handlers (what runs when called)
```

Start Hermes — your tools appear alongside built-in tools. The model can call them immediately.

### Minimal working example

Here is a complete plugin that adds a `hello_world` tool and logs every tool call via a hook.

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: A minimal example plugin
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""Minimal Hermes plugin — registers a tool and a hook."""

import json


def register(ctx):
    # --- Tool: hello_world ---
    schema = {
        "name": "hello_world",
        "description": "Returns a friendly greeting for the given name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
                }
            },
            "required": ["name"],
        },
    }

    def handle_hello(params, **kwargs):
        del kwargs
        name = params.get("name", "World")
        return json.dumps({"success": True, "greeting": f"Hello, {name}!"})

    ctx.register_tool(
        name="hello_world",
        toolset="hello_world",
        schema=schema,
        handler=handle_hello,
        description="Return a friendly greeting for the given name.",
    )

    # --- Hook: log every tool call ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] tool called: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

Drop both files into `~/.hermes/plugins/hello-world/`, restart Hermes, and the model can immediately call `hello_world`. The hook prints a log line after every tool invocation.

Project-local plugins under `./.hermes/plugins/` are disabled by default. Enable them only for trusted repositories by setting `HERMES_ENABLE_PROJECT_PLUGINS=true` before starting Hermes.

## What plugins can do

Every `ctx.*` API below is available inside a plugin's `register(ctx)` function.

| Capability | How |
|-----------|-----|
| Add tools | `ctx.register_tool(name=..., toolset=..., schema=..., handler=...)` |
| Add hooks | `ctx.register_hook("post_tool_call", callback)` |
| Add slash commands | `ctx.register_command(name, handler, description)` — adds `/name` in CLI and gateway sessions |
| Dispatch tools from commands | `ctx.dispatch_tool(name, args)` — invokes a registered tool with parent-agent context auto-wired |
| Add CLI commands | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — adds `hermes <plugin> <subcommand>` |
| Inject messages | `ctx.inject_message(content, role="user")` — see [Injecting Messages](#injecting-messages) |
| Ship data files | `Path(__file__).parent / "data" / "file.yaml"` |
| Bundle skills | `ctx.register_skill(name, path)` — namespaced as `plugin:skill`, loaded via `skill_view("plugin:skill")` |
| Gate on env vars | `requires_env: [API_KEY]` in plugin.yaml — prompted during `hermes plugins install` |
| Distribute via pip | `[project.entry-points."hermes_agent.plugins"]` |
| Register a gateway platform (Discord, Telegram, IRC, …) | `ctx.register_platform(name, label, adapter_factory, check_fn, ...)` — see [Adding Platform Adapters](/developer-guide/adding-platform-adapters) |
| Register an image-generation backend | `ctx.register_image_gen_provider(provider)` — see [Image Generation Provider Plugins](/developer-guide/image-gen-provider-plugin) |
| Register a video-generation backend | `ctx.register_video_gen_provider(provider)` — see [Video Generation Provider Plugins](/developer-guide/video-gen-provider-plugin) |
| Register a context-compression engine | `ctx.register_context_engine(engine)` — see [Context Engine Plugins](/developer-guide/context-engine-plugin) |
| Register a memory backend | Subclass `MemoryProvider` in `plugins/memory/<name>/__init__.py` — see [Memory Provider Plugins](/developer-guide/memory-provider-plugin) (uses a separate discovery system) |
| Run a host-owned LLM call | `ctx.llm.complete(...)` / `ctx.llm.complete_structured(...)` — borrow the user's active model + auth for a one-shot completion with optional JSON schema validation. See [Plugin LLM Access](/developer-guide/plugin-llm-access) |
| Register an inference backend (LLM provider) | `register_provider(ProviderProfile(...))` in `plugins/model-providers/<name>/__init__.py` — see [Model Provider Plugins](/developer-guide/model-provider-plugin) (uses a separate discovery system) |

## Plugin discovery

| Source | Path | Use case |
|--------|------|----------|
| Bundled | `<repo>/plugins/` | Ships with Hermes — see [Built-in Plugins](/user-guide/features/built-in-plugins) |
| User | `~/.hermes/plugins/` | Personal plugins |
| Project | `.hermes/plugins/` | Project-specific plugins (requires `HERMES_ENABLE_PROJECT_PLUGINS=true`) |
| pip | `hermes_agent.plugins` entry_points | Distributed packages |
| Nix | `services.hermes-agent.extraPlugins` / `extraPythonPackages` | NixOS declarative installs — see [Nix Setup](/getting-started/nix-setup#plugins) |

Later sources override earlier ones on name collision, so a user plugin with the same name as a bundled plugin replaces it.

### Plugin sub-categories

Within each source, Hermes also recognizes sub-category directories that route plugins to specialized discovery systems:

| Sub-directory | What it holds | Discovery system |
|---|---|---|
| `plugins/` (root) | General plugins — tools, hooks, slash commands, CLI commands, bundled skills | `PluginManager` (kind: `standalone` or `backend`) |
| `plugins/platforms/<name>/` | Gateway channel adapters (`ctx.register_platform()`) | `PluginManager` (kind: `platform`, one level deeper) |
| `plugins/image_gen/<name>/` | Image-generation backends (`ctx.register_image_gen_provider()`) | `PluginManager` (kind: `backend`, one level deeper) |
| `plugins/memory/<name>/` | Memory providers (subclass `MemoryProvider`) | **Own loader** in `plugins/memory/__init__.py` (kind: `exclusive` — one active at a time) |
| `plugins/context_engine/<name>/` | Context-compression engines (`ctx.register_context_engine()`) | **Own loader** in `plugins/context_engine/__init__.py` (one active at a time) |
| `plugins/model-providers/<name>/` | LLM provider profiles (`register_provider(ProviderProfile(...))`) | **Own loader** in `providers/__init__.py` (lazily scanned on first `get_provider_profile()` call) |

User plugins at `~/.hermes/plugins/model-providers/<name>/` and `~/.hermes/plugins/memory/<name>/` override bundled plugins of the same name — last-writer-wins in `register_provider()` / `register_memory_provider()`. Drop a directory in, and it replaces the built-in without any repo edits.

## Plugins are opt-in (with a few exceptions)

**General plugins and user-installed backends are disabled by default** — discovery finds them (so they show up in `hermes plugins` and `/plugins`), but nothing with hooks or tools loads until you add the plugin's name to `plugins.enabled` in `~/.hermes/config.yaml`. This stops third-party code from running without your explicit consent.

```yaml
plugins:
  enabled:
    - my-tool-plugin
    - disk-cleanup
  disabled:       # optional deny-list — always wins if a name appears in both
    - noisy-plugin
```

Three ways to flip state:

```bash
hermes plugins                    # interactive toggle (space to check/uncheck)
hermes plugins enable <name>      # add to allow-list
hermes plugins disable <name>     # remove from allow-list + add to disabled
```

After `hermes plugins install owner/repo`, you're asked `Enable 'name' now? [y/N]` — defaults to no. Skip the prompt for scripted installs with `--enable` or `--no-enable`.

### What the allow-list does NOT gate

Several categories of plugin bypass `plugins.enabled` — they're part of Hermes' built-in surface and would break basic functionality if gated off by default:

| Plugin kind | How it's activated instead |
|---|---|
| **Bundled platform plugins** (IRC, Teams, etc. under `plugins/platforms/`) | Auto-loaded so every shipped gateway channel is available. The actual channel turns on via `gateway.platforms.<name>.enabled` in `config.yaml`. |
| **Bundled backends** (image-gen providers under `plugins/image_gen/`, etc.) | Auto-loaded so the default backend "just works". Selection happens via `<category>.provider` in `config.yaml` (e.g. `image_gen.provider: openai`). |
| **Memory providers** (`plugins/memory/`) | All discovered; exactly one is active, chosen by `memory.provider` in `config.yaml`. |
| **Context engines** (`plugins/context_engine/`) | All discovered; one is active, chosen by `context.engine` in `config.yaml`. |
| **Model providers** (`plugins/model-providers/`) | All bundled providers under `plugins/model-providers/` discover and register at the first `get_provider_profile()` call. The user picks one at a time via `--provider` or `config.yaml`. |
| **Pip-installed `backend` plugins** | Opt-in via `plugins.enabled` (same as general plugins). |
| **User-installed platforms** (under `~/.hermes/plugins/platforms/`) | Opt-in via `plugins.enabled` — third-party gateway adapters need explicit consent. |

In short: **bundled "always-works" infrastructure loads automatically; third-party general plugins are opt-in.** The `plugins.enabled` allow-list is the gate specifically for arbitrary code a user drops into `~/.hermes/plugins/`.

### Migration for existing users

When you upgrade to a version of Hermes that has opt-in plugins (config schema v21+), any user plugins already installed under `~/.hermes/plugins/` that weren't already in `plugins.disabled` are **automatically grandfathered** into `plugins.enabled`. Your existing setup keeps working. Bundled standalone plugins are NOT grandfathered — even existing users have to opt in explicitly. (Bundled platform/backend plugins never needed grandfathering because they were never gated.)

## Available hooks

Plugins can register callbacks for these lifecycle events. See the **[Event Hooks page](/user-guide/features/hooks#plugin-hooks)** for full details, callback signatures, and examples.

| Hook | Fires when |
|------|-----------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | Before any tool executes |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | After any tool returns |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | Once per turn, before the LLM loop — can return `{"context": "..."}` to [inject context into the user message](/user-guide/features/hooks#pre_llm_call) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | Once per turn, after the LLM loop (successful turns only) |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | New session created (first turn only) |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | End of every `run_conversation` call + CLI exit handler |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/gateway tears down an active session (`/new`, GC, CLI quit) |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | Gateway swaps in a new session key (`/new`, `/reset`, `/clear`, idle rotation) |
| [`subagent_stop`](/user-guide/features/hooks#subagent_stop) | Once per child after `delegate_task` finishes |
| [`pre_gateway_dispatch`](/user-guide/features/hooks#pre_gateway_dispatch) | Gateway received a user message, before auth + dispatch. Return `{"action": "skip" \| "rewrite" \| "allow", ...}` to influence flow. |

## Plugin types

Hermes has four kinds of plugins:

| Type | What it does | Selection | Location |
|------|-------------|-----------|----------|
| **General plugins** | Add tools, hooks, slash commands, CLI commands | Multi-select (enable/disable) | `~/.hermes/plugins/` |
| **Memory providers** | Replace or augment built-in memory | Single-select (one active) | `plugins/memory/` |
| **Context engines** | Replace the built-in context compressor | Single-select (one active) | `plugins/context_engine/` |
| **Model providers** | Declare an inference backend (OpenRouter, Anthropic, …) | Multi-register, picked by `--provider` / `config.yaml` | `plugins/model-providers/` |

Memory providers and context engines are **provider plugins** — only one of each type can be active at a time. Model providers are also plugins, but many load simultaneously; the user picks one at a time via `--provider` or `config.yaml`. General plugins can be enabled in any combination.

## Pluggable interfaces — where to go for each

The table above shows the four plugin categories, but within "General plugins" the `PluginContext` exposes several distinct extension points — and Hermes also accepts extensions outside the Python plugin system (config-driven backends, shell-hooked commands, external servers, etc.). Use this table to find the right doc for what you want to build:

| Want to add… | How | Authoring guide |
|---|---|---|
| A **tool** the LLM can call | Python plugin — `ctx.register_tool()` | [Build a Hermes Plugin](/guides/build-a-hermes-plugin) · [Adding Tools](/developer-guide/adding-tools) |
| A **lifecycle hook** (pre/post LLM, session start/end, tool filter) | Python plugin — `ctx.register_hook()` | [Hooks reference](/user-guide/features/hooks) · [Build a Hermes Plugin](/guides/build-a-hermes-plugin) |
| A **slash command** for the CLI / gateway | Python plugin — `ctx.register_command()` | [Build a Hermes Plugin](/guides/build-a-hermes-plugin) · [Extending the CLI](/developer-guide/extending-the-cli) |
| A **subcommand** for `hermes <thing>` | Python plugin — `ctx.register_cli_command()` | [Extending the CLI](/developer-guide/extending-the-cli) |
| A bundled **skill** that your plugin ships | Python plugin — `ctx.register_skill()` | [Creating Skills](/developer-guide/creating-skills) |
| An **inference backend** (LLM provider: OpenAI-compat, Codex, Anthropic-Messages, Bedrock) | Provider plugin — `register_provider(ProviderProfile(...))` in `plugins/model-providers/<name>/` | **[Model Provider Plugins](/developer-guide/model-provider-plugin)** · [Adding Providers](/developer-guide/adding-providers) |
| A **gateway channel** (Discord / Telegram / IRC / Teams / etc.) | Platform plugin — `ctx.register_platform()` in `plugins/platforms/<name>/` | [Adding Platform Adapters](/developer-guide/adding-platform-adapters) |
| A **memory backend** (Honcho, Mem0, Supermemory, …) | Memory plugin — subclass `MemoryProvider` in `plugins/memory/<name>/` | [Memory Provider Plugins](/developer-guide/memory-provider-plugin) |
| A **context-compression strategy** | Context-engine plugin — `ctx.register_context_engine()` | [Context Engine Plugins](/developer-guide/context-engine-plugin) |
| An **image-generation backend** (DALL·E, SDXL, …) | Backend plugin — `ctx.register_image_gen_provider()` | [Image Generation Provider Plugins](/developer-guide/image-gen-provider-plugin) |
| A **video-generation backend** (Veo, Kling, Pixverse, Grok-Imagine, Runway, …) | Backend plugin — `ctx.register_video_gen_provider()` | [Video Generation Provider Plugins](/developer-guide/video-gen-provider-plugin) |
| A **TTS backend** (any CLI — Piper, VoxCPM, Kokoro, xtts, voice-cloning scripts, …) | Config-driven (recommended) — declare under `tts.providers.<name>` with `type: command` in `config.yaml`. OR Python backend plugin — `ctx.register_tts_provider()` for Python-SDK / streaming engines that need more than a shell template. | [TTS Setup](/user-guide/features/tts#custom-command-providers) · [Python plugin guide](/user-guide/features/tts#python-plugin-providers) |
| An **STT backend** (any CLI — whisper.cpp, custom whisper binary, local ASR CLI) | Config-driven (recommended) — declare under `stt.providers.<name>` with `type: command` in `config.yaml`, or set `HERMES_LOCAL_STT_COMMAND` for the legacy single-command escape hatch. OR Python backend plugin — `ctx.register_transcription_provider()` for Python-SDK engines (OpenRouter, SenseAudio, Gemini-STT, etc.). | [STT Setup](/user-guide/features/tts#stt-custom-command-providers) · [Python plugin guide](/user-guide/features/tts#python-plugin-providers-stt) |
| **External tools via MCP** (filesystem, GitHub, Linear, Notion, any MCP server) | Config-driven — declare `mcp_servers.<name>` with `command:` / `url:` in `config.yaml`. Hermes auto-discovers the server's tools and registers them alongside built-ins. | [MCP](/user-guide/features/mcp) |
| **Additional skill sources** (custom GitHub repos, private skill indexes) | CLI — `hermes skills tap add <repo>` | [Skills Hub](/user-guide/features/skills#skills-hub) · [Publishing a custom tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| **Gateway event hooks** (fire on `gateway:startup`, `session:start`, `agent:end`, `command:*`) | Drop `HOOK.yaml` + `handler.py` into `~/.hermes/hooks/<name>/` | [Event Hooks](/user-guide/features/hooks#gateway-event-hooks) |
| **Shell hooks** (run a shell command on events — notifications, audit logs, desktop alerts) | Config-driven — declare under `hooks:` in `config.yaml` | [Shell Hooks](/user-guide/features/hooks#shell-hooks) |

:::note
Not everything is a Python plugin. Some extension surfaces intentionally use **config-driven shell commands** (TTS, STT, shell hooks) so any CLI you already have becomes a plugin without writing Python. Others are **external servers** (MCP) the agent connects to and auto-registers tools from. And some are **drop-in directories** (gateway hooks) with their own manifest format. Pick the right surface for the integration style that fits your use case; the authoring guides in the table above each cover placeholders, discovery, and examples.
:::

## NixOS declarative plugins

On NixOS, plugins can be installed declaratively via the module options — no `hermes plugins install` needed. See the **[Nix Setup guide](/getting-started/nix-setup#plugins)** for full details.

```nix
services.hermes-agent = {
  # Directory plugin (source tree with plugin.yaml)
  extraPlugins = [ (pkgs.fetchFromGitHub { ... }) ];
  # Entry-point plugin (pip package)
  extraPythonPackages = [ (pkgs.python312Packages.buildPythonPackage { ... }) ];
  # Enable in config
  settings.plugins.enabled = [ "my-plugin" ];
};
```

Declarative plugins are symlinked with a `nix-managed-` prefix — they coexist with manually installed plugins and are cleaned up automatically when removed from the Nix config.

## Managing plugins

```bash
hermes plugins                               # unified interactive UI
hermes plugins list                          # table: enabled / disabled / not enabled
hermes plugins install user/repo             # install from Git, then prompt Enable? [y/N]
hermes plugins install user/repo --enable    # install AND enable (no prompt)
hermes plugins install user/repo --no-enable # install but leave disabled (no prompt)
hermes plugins update my-plugin              # pull latest
hermes plugins remove my-plugin              # uninstall
hermes plugins enable my-plugin              # add to allow-list
hermes plugins disable my-plugin             # remove from allow-list + add to disabled
```

### Interactive UI

Running `hermes plugins` with no arguments opens a composite interactive screen:

```
Plugins
  ↑↓ navigate  SPACE toggle  ENTER configure/confirm  ESC done

  General Plugins
 → [✓] my-tool-plugin — Custom search tool
   [ ] webhook-notifier — Event hooks
   [ ] disk-cleanup — Auto-cleanup of ephemeral files [bundled]

  Provider Plugins
     Memory Provider          ▸ honcho
     Context Engine           ▸ compressor
```

- **General Plugins section** — checkboxes, toggle with SPACE. Checked = in `plugins.enabled`, unchecked = in `plugins.disabled` (explicit off).
- **Provider Plugins section** — shows current selection. Press ENTER to drill into a radio picker where you choose one active provider.
- Bundled plugins appear in the same list with a `[bundled]` tag.

Provider plugin selections are saved to `config.yaml`:

```yaml
memory:
  provider: "honcho"      # empty string = built-in only

context:
  engine: "compressor"    # default built-in compressor
```

### Enabled vs. disabled vs. neither

Plugins occupy one of three states:

| State | Meaning | In `plugins.enabled`? | In `plugins.disabled`? |
|---|---|---|---|
| `enabled` | Loaded on next session | Yes | No |
| `disabled` | Explicitly off — won't load even if also in `enabled` | (irrelevant) | Yes |
| `not enabled` | Discovered but never opted in | No | No |

The default for a newly-installed or bundled plugin is `not enabled`. `hermes plugins list` shows all three distinct states so you can tell what's been explicitly turned off vs. what's just waiting to be enabled.

In a running session, `/plugins` shows which plugins are currently loaded.

## Injecting Messages

Plugins can inject messages into the active conversation using `ctx.inject_message()`:

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**Signature:** `ctx.inject_message(content: str, role: str = "user") -> bool`

How it works:

- If the agent is **idle** (waiting for user input), the message is queued as the next input and starts a new turn.
- If the agent is **mid-turn** (actively running), the message interrupts the current operation — the same as a user typing a new message and pressing Enter.
- For non-`"user"` roles, the content is prefixed with `[role]` (e.g. `[system] ...`).
- Returns `True` if the message was queued successfully, `False` if no CLI reference is available (e.g. in gateway mode).

This enables plugins like remote control viewers, messaging bridges, or webhook receivers to feed messages into the conversation from external sources.

:::note
`inject_message` is only available in CLI mode. In gateway mode, there is no CLI reference and the method returns `False`.
:::

See the **[full guide](/guides/build-a-hermes-plugin)** for handler contracts, schema format, hook behavior, error handling, and common mistakes.

---

# SOURCE: website/docs/user-guide/features/built-in-plugins.md

---
sidebar_position: 12
sidebar_label: "Built-in Plugins"
title: "Built-in Plugins"
description: "Plugins shipped with Hermes Agent that run automatically via lifecycle hooks — disk-cleanup and friends"
---

# Built-in Plugins

Hermes ships a small set of plugins bundled with the repository. They live under `<repo>/plugins/<name>/` and load automatically alongside user-installed plugins in `~/.hermes/plugins/`. They use the same plugin surface as third-party plugins — hooks, tools, slash commands — just maintained in-tree.

See the [Plugins](/user-guide/features/plugins) page for the general plugin system, and [Build a Hermes Plugin](/guides/build-a-hermes-plugin) to write your own.

## How discovery works

The `PluginManager` scans four sources, in order:

1. **Bundled** — `<repo>/plugins/<name>/` (what this page documents)
2. **User** — `~/.hermes/plugins/<name>/`
3. **Project** — `./.hermes/plugins/<name>/` (requires `HERMES_ENABLE_PROJECT_PLUGINS=1`)
4. **Pip entry points** — `hermes_agent.plugins`

On name collision, later sources win — a user plugin named `disk-cleanup` would replace the bundled one.

`plugins/memory/` and `plugins/context_engine/` are deliberately excluded from bundled scanning. Those directories use their own discovery paths because memory providers and context engines are single-select providers configured through `hermes memory setup` / `context.engine` in config.

## Bundled plugins are opt-in

Bundled plugins ship disabled. Discovery finds them (they appear in `hermes plugins list` and the interactive `hermes plugins` UI), but none load until you explicitly enable them:

```bash
hermes plugins enable disk-cleanup
```

Or via `~/.hermes/config.yaml`:

```yaml
plugins:
  enabled:
    - disk-cleanup
```

This is the same mechanism user-installed plugins use. Bundled plugins are never auto-enabled — not on fresh install, not for existing users upgrading to a newer Hermes. You always opt in explicitly.

To turn a bundled plugin off again:

```bash
hermes plugins disable disk-cleanup
# or: remove it from plugins.enabled in config.yaml
```

## Currently shipped

The repo ships these bundled plugins under `plugins/`. All are opt-in — enable them via `hermes plugins enable <name>`.

| Plugin | Kind | Purpose |
|---|---|---|
| `disk-cleanup` | hooks + slash command | Auto-track ephemeral files and clean them on session end |
| `security-guidance` | hooks | Pattern-match dangerous code on `write_file`/`patch` and append a security warning (or block) — 25 rules (Apache-2.0 fork of Anthropic's `claude-plugins-official` patterns) |
| `observability/langfuse` | hooks | Trace turns / LLM calls / tools to [Langfuse](https://langfuse.com) |
| `observability/nemo_relay` | hooks | Relay observability events (turns / LLM calls / tools) to an NVIDIA NeMo endpoint |
| `teams_pipeline` | standalone | Microsoft Teams meeting pipeline — Graph-backed, transcript-first meeting summaries |
| `spotify` | backend (7 tools) | Native Spotify playback, queue, search, playlists, albums, library |
| `google_meet` | standalone | Join Meet calls, live-caption transcription, optional realtime duplex audio |
| `image_gen/openai` | image backend | OpenAI `gpt-image-2` image generation backend (alternative to FAL) |
| `image_gen/openai-codex` | image backend | OpenAI image generation via Codex OAuth |
| `image_gen/xai` | image backend | xAI `grok-2-image` backend |
| `hermes-achievements` | dashboard tab | Steam-style collectible badges generated from your real Hermes session history |
| `kanban/dashboard` | dashboard tab | Kanban board UI for the multi-agent dispatcher — tasks, comments, fan-out, board switching. See [Kanban Multi-Agent](./kanban.md). |

Memory providers (`plugins/memory/*`) and context engines (`plugins/context_engine/*`) are listed separately on [Memory Providers](./memory-providers.md) — they're managed through `hermes memory` and `hermes plugins` respectively. The full per-plugin detail for the two long-running hooks-based plugins follows.

### disk-cleanup

Auto-tracks and removes ephemeral files created during sessions — test scripts, temp outputs, cron logs, stale chrome profiles — without requiring the agent to remember to call a tool.

**How it works:**

| Hook | Behaviour |
|---|---|
| `post_tool_call` | When `write_file` / `terminal` / `patch` creates a file matching `test_*`, `tmp_*`, or `*.test.*` inside `HERMES_HOME` or `/tmp/hermes-*`, track it silently as `test` / `temp` / `cron-output`. |
| `on_session_end` | If any test files were auto-tracked during the turn, run the safe `quick` cleanup and log a one-line summary. Stays silent otherwise. |

**Deletion rules:**

| Category | Threshold | Confirmation |
|---|---|---|
| `test` | every session end | Never |
| `temp` | >7 days since tracked | Never |
| `cron-output` | >14 days since tracked | Never |
| empty dirs under HERMES_HOME | always | Never |
| `research` | >30 days, beyond 10 newest | Always (deep only) |
| `chrome-profile` | >14 days since tracked | Always (deep only) |
| files >500 MB | never auto | Always (deep only) |

**Slash command** — `/disk-cleanup` available in both CLI and gateway sessions:

```
/disk-cleanup status                     # breakdown + top-10 largest
/disk-cleanup dry-run                    # preview without deleting
/disk-cleanup quick                      # run safe cleanup now
/disk-cleanup deep                       # quick + list items needing confirmation
/disk-cleanup track <path> <category>    # manual tracking
/disk-cleanup forget <path>              # stop tracking (does not delete)
```

**State** — everything lives at `$HERMES_HOME/disk-cleanup/`:

| File | Contents |
|---|---|
| `tracked.json` | Tracked paths with category, size, and timestamp |
| `tracked.json.bak` | Atomic-write backup of the above |
| `cleanup.log` | Append-only audit trail of every track / skip / reject / delete |

**Safety** — cleanup only ever touches paths under `HERMES_HOME` or `/tmp/hermes-*`. Windows mounts (`/mnt/c/...`) are rejected. Well-known top-level state dirs (`logs/`, `memories/`, `sessions/`, `cron/`, `cache/`, `skills/`, `plugins/`, `disk-cleanup/` itself) are never removed even when empty — a fresh install does not get gutted on first session end.

**Enabling:** `hermes plugins enable disk-cleanup` (or check the box in `hermes plugins`).

**Disabling again:** `hermes plugins disable disk-cleanup`.

### security-guidance

Fast pattern-matched security warnings on file writes. When the agent's `write_file` / `patch` / `skill_manage` calls carry content matching a known-dangerous code pattern — `pickle.load`, `yaml.load` without `SafeLoader`, `eval(`, `os.system`, `subprocess(...,  shell=True)`, JS `child_process.exec`, React `dangerouslySetInnerHTML`, raw `.innerHTML =` / `.outerHTML =` / `document.write`, Node `crypto.createCipher`, AES ECB mode, TLS verification disabled, XXE-prone `xml.etree` / `minidom` parsers, `<script src="//..." >` without SRI, `torch.load` without `weights_only=True`, GitHub Actions `${{ github.event.* }}` injection — the plugin appends a `⚠️ Security guidance` block to the tool's result.

The file is still written. The model reads the warning in the next turn's tool message and can either fix the code or document why the construct is safe in this context. Pattern matching has a non-trivial false-positive rate, which is why warn (not block) is the default.

**Coverage:** 25 rules total, covering unsafe deserialization, command injection, XSS sinks, crypto footguns, XXE, supply-chain (SRI), and CI/CD workflow injection. The pattern data is a verbatim Apache-2.0 fork of [Anthropic's `claude-plugins-official`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance/hooks) — see the plugin's `LICENSE` and `NOTICE` files for attribution.

**Modes:**

| Env var | Effect |
|---|---|
| (unset) | **warn mode** (default) — file is written, warning appended to result |
| `SECURITY_GUIDANCE_BLOCK=1` | **block mode** — write refused, warning returned as the block reason |
| `SECURITY_GUIDANCE_DISABLE=1` | kill switch — plugin loads but does nothing |

**Enabling:** `hermes plugins enable security-guidance` (or check the box in `hermes plugins`).

**Disabling again:** `hermes plugins disable security-guidance`.

**What it does not do (yet):** the upstream Anthropic plugin has two more layers — an LLM diff review on each agent turn that touched files, and an agentic commit-time review that traces data flow across files. Neither is ported. The agent can already run those reviews on demand via `delegate_task`.

### observability/langfuse

Traces Hermes turns, LLM calls, and tool invocations to [Langfuse](https://langfuse.com) — an open-source LLM observability platform. One span per turn, one generation per API call, one tool observation per tool call. Usage totals, per-type token counts, and cost estimates come out of Hermes' canonical `agent.usage_pricing` numbers, so the Langfuse dashboard sees the same breakdown (input / output / `cache_read_input_tokens` / `cache_creation_input_tokens` / `reasoning_tokens`) that appears in `hermes logs`.

The plugin is fail-open: no SDK installed, no credentials, or a transient Langfuse error — all turn into a silent no-op in the hook. The agent loop is never impacted.

**Setup (interactive — recommended):**

```bash
hermes tools          # → Langfuse Observability → Cloud or Self-Hosted
```

The wizard collects your keys, `pip install`s the `langfuse` SDK, and adds `observability/langfuse` to `plugins.enabled` for you. Restart Hermes and the next turn ships a trace.

**Setup (manual):**

```bash
pip install langfuse
hermes plugins enable observability/langfuse
```

Then put the credentials in `~/.hermes/.env`:

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

**How it works:**

| Hook | Behaviour |
|---|---|
| `pre_api_request` / `pre_llm_call` | Open (or reuse) a per-turn root span "Hermes turn". Start a `generation` child observation for this API call with serialized recent messages as input. |
| `post_api_request` / `post_llm_call` | Close the generation, attach `usage_details`, `cost_details`, `finish_reason`, assistant output + tool calls. If no tool calls and non-empty content, close the turn. |
| `pre_tool_call` | Start a `tool` child observation with sanitized `args`. |
| `post_tool_call` | Close the tool observation with sanitized `result`. `read_file` payloads get summarized (head + tail + omitted-line count) so a huge file read stays under `HERMES_LANGFUSE_MAX_CHARS`. |

Session grouping keys off the Hermes session ID (or task ID for sub-agents) via `langfuse.propagate_attributes`, so everything in a single `hermes chat` session lives under one Langfuse session.

**Verify:**

```bash
hermes plugins list                 # observability/langfuse should show "enabled"
hermes chat -q "hello"              # check the Langfuse UI for a "Hermes turn" trace
```

**Optional tuning** (in `.env`):

| Variable | Default | Purpose |
|---|---|---|
| `HERMES_LANGFUSE_ENV` | — | Environment tag on traces (`production`, `staging`, …) |
| `HERMES_LANGFUSE_RELEASE` | — | Release/version tag |
| `HERMES_LANGFUSE_SAMPLE_RATE` | `1.0` | Sampling rate passed to the SDK (0.0–1.0) |
| `HERMES_LANGFUSE_MAX_CHARS` | `12000` | Per-field truncation for message content / tool args / tool results |
| `HERMES_LANGFUSE_DEBUG` | `false` | Verbose plugin logging to `agent.log` |

Hermes-prefixed and standard SDK env vars (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`) are both accepted — Hermes-prefixed wins when both are set.

**Performance:** the Langfuse client is cached after the first hook call. If credentials or SDK are missing, that decision is also cached — subsequent hooks fast-return without re-checking env vars or reloading config.

**Disabling:** `hermes plugins disable observability/langfuse`. The plugin module is still discovered, but no module code runs until you re-enable.

### google_meet

Lets the agent **join, transcribe, and participate in Google Meet calls** — take notes on a meeting, summarize the back-and-forth after, follow up on specific points, and (optionally) speak replies back into the call via TTS.

**What it adds:**

- A headless virtual participant that joins a Meet URL using browser automation
- Live transcription of the meeting audio via the configured STT provider
- A `meet_summarize` / `meet_speak` / `meet_followup` toolset the agent invokes to act on what it heard
- Post-meeting artifacts (transcript, speaker-attributed notes, action items) saved under `~/.hermes/cache/google_meet/<meeting_id>/`

**Setup:**

```bash
hermes plugins enable google_meet
# Prompts you to sign in via the plugin's OAuth flow on first use —
# needs a Google account with Meet access. Host approval may be required
# if the meeting enforces "only invited participants can join".
```

Usage from chat:

> "Join meet.google.com/abc-defg-hij and take notes. After the call, send me a summary with action items."

The agent kicks off the meeting join, streams the transcription back into its context as the call proceeds, and produces a structured summary when the meeting ends (or when you tell it to stop).

**When to use it:** recurring standups where you want a bot to transcribe + summarize for async attendees; deposition-style interviews where you want structured notes; any case where you'd otherwise need Fireflies / Otter / Grain. When you'd rather not have an AI listening in — don't enable it.

**Disabling:** `hermes plugins disable google_meet`. Any cached transcripts and recordings stay in `~/.hermes/cache/google_meet/` until you remove them.

### hermes-achievements

Adds a **Steam-style achievements tab to the dashboard** — 60+ collectible, tiered badges generated from your real Hermes session history. Tool-chain feats, debugging patterns, vibe-coding streaks, skill/memory usage, model/provider variety, lifestyle quirks (weekend and night sessions). Originally authored by [@PCinkusz](https://github.com/PCinkusz) as an external plugin; brought in-tree so it stays in lockstep with Hermes feature changes.

**How it works:**

- Scans your entire `~/.hermes/state.db` session history on the dashboard backend
- Per-session stats are cached by `(started_at, last_active)` fingerprint, so only new or changed sessions re-analyze on subsequent scans
- First-ever scan runs in a background thread — the dashboard never blocks waiting for it, even on databases with thousands of sessions
- Unlock state is persisted to `$HERMES_HOME/plugins/hermes-achievements/state.json`

**Tier progression:** Copper → Silver → Gold → Diamond → Olympian. Each card exposes a "What counts" section listing the exact metric being tracked.

**Achievement states:**

| State | Meaning |
|---|---|
| Unlocked | At least one tier achieved |
| Discovered | Known achievement, progress visible, not yet earned |
| Secret | Hidden until Hermes detects the first related signal in your history |

**API** — routes mount under `/api/plugins/hermes-achievements/`:

| Endpoint | Purpose |
|---|---|
| `GET /achievements` | Full catalog with per-badge unlock state (returns a pending placeholder while the first cold scan is running) |
| `GET /scan-status` | State of the background scanner: `idle` / `running` / `failed`, last duration, run count |
| `GET /recent-unlocks` | Twenty most recently unlocked badges, newest first |
| `GET /sessions/{id}/badges` | Badges earned primarily in one specific session |
| `POST /rescan` | Manual synchronous rescan (blocks; use when the user clicks the rescan button) |
| `POST /reset-state` | Clear unlock history and cached snapshot |

**State files** — live under `$HERMES_HOME/plugins/hermes-achievements/`:

| File | Contents |
|---|---|
| `state.json` | Unlock history: which badges you've earned and when. Stable across Hermes updates. |
| `scan_snapshot.json` | Last completed scan payload (served immediately on dashboard load) |
| `scan_checkpoint.json` | Per-session stats cache keyed by fingerprint (makes warm rescans fast) |

**Performance notes:**

- Cold scan on ~8,000 sessions takes a few minutes. It runs in a background thread on first dashboard request; the UI sees a pending placeholder and polls `/scan-status`.
- **Incremental results during a cold scan** — the scanner publishes a partial snapshot every ~250 sessions so each dashboard refresh shows more badges unlocked as the scan progresses. No minute-long stare at zeros.
- Warm rescan reuses per-session stats for every session whose `started_at` + `last_active` fingerprint matches the checkpoint — completes in seconds even on large histories.
- The in-memory snapshot TTL is 120s; stale requests serve the old snapshot immediately and kick a background refresh. You never wait on a spinner just because TTL expired.

**Enabling:** Nothing to enable — `hermes-achievements` is a dashboard-only plugin (no lifecycle hooks, no model-visible tools). It auto-registers as a tab in `hermes dashboard` on first launch. The `plugins.enabled` config only gates lifecycle/tool plugins; dashboard plugins are discovered purely via their `dashboard/manifest.json`.

**Opting out:** Delete or rename `plugins/hermes-achievements/dashboard/manifest.json`, or override it with a user plugin of the same name in `~/.hermes/plugins/hermes-achievements/` that ships no dashboard. The plugin's state files under `$HERMES_HOME/plugins/hermes-achievements/` survive — reinstalling preserves your unlock history.

## Adding a bundled plugin

Bundled plugins are written exactly like any other Hermes plugin — see [Build a Hermes Plugin](/guides/build-a-hermes-plugin). The only differences are:

- Directory lives at `<repo>/plugins/<name>/` instead of `~/.hermes/plugins/<name>/`
- Manifest source is reported as `bundled` in `hermes plugins list`
- User plugins with the same name override the bundled version

A plugin is a good candidate for bundling when:

- It has no optional dependencies (or they're already `pip install .[all]` deps)
- The behaviour benefits most users and is opt-out rather than opt-in
- The logic ties into lifecycle hooks that the agent would otherwise have to remember to invoke
- It complements a core capability without expanding the model-visible tool surface

Counter-examples — things that should stay as user-installable plugins, not bundled: third-party integrations with API keys, niche workflows, large dependency trees, anything that would meaningfully change agent behaviour by default.

---

# SOURCE: website/docs/guides/build-a-hermes-plugin.md

---
sidebar_position: 9
sidebar_label: "Build a Plugin"
title: "Build a Hermes Plugin"
description: "Step-by-step guide to building a complete Hermes plugin with tools, hooks, data files, and skills"
---

# Build a Hermes Plugin

This guide walks through building a complete Hermes plugin from scratch. By the end you'll have a working plugin with multiple tools, lifecycle hooks, shipped data files, and a bundled skill — everything the plugin system supports.

:::info Not sure which guide you need?
Hermes has several distinct pluggable interfaces — some use Python `register_*` APIs, others are config-driven or drop-in directories. Use this map first:

| If you want to add… | Read |
|---|---|
| Custom tools, hooks, slash commands, skills, or CLI subcommands | **This guide** (the general plugin surface) |
| An **LLM / inference backend** (new provider) | [Model Provider Plugins](/developer-guide/model-provider-plugin) |
| A **gateway channel** (Discord/Telegram/IRC/Teams/etc.) | [Adding Platform Adapters](/developer-guide/adding-platform-adapters) |
| A **memory backend** (Honcho/Mem0/Supermemory/etc.) | [Memory Provider Plugins](/developer-guide/memory-provider-plugin) |
| A **context-compression engine** | [Context Engine Plugins](/developer-guide/context-engine-plugin) |
| An **image-generation backend** | [Image Generation Provider Plugins](/developer-guide/image-gen-provider-plugin) |
| A **video-generation backend** | [Video Generation Provider Plugins](/developer-guide/video-gen-provider-plugin) |
| A **TTS backend** (any CLI — Piper, VoxCPM, Kokoro, voice cloning, …) | [TTS custom command providers](/user-guide/features/tts#custom-command-providers) — config-driven, no Python needed |
| An **STT backend** (custom whisper / ASR CLI) | [Voice Message Transcription](/user-guide/features/tts#voice-message-transcription-stt) — set `HERMES_LOCAL_STT_COMMAND` to a shell template |
| **External tools via MCP** (filesystem, GitHub, Linear, any MCP server) | [MCP](/user-guide/features/mcp) — declare `mcp_servers.<name>` in `config.yaml` |
| **Gateway event hooks** (fire on startup, session events, commands) | [Event Hooks](/user-guide/features/hooks#gateway-event-hooks) — drop `HOOK.yaml` + `handler.py` into `~/.hermes/hooks/<name>/` |
| **Shell hooks** (run a shell command on events) | [Shell Hooks](/user-guide/features/hooks#shell-hooks) — declare under `hooks:` in `config.yaml` |
| **Additional skill sources** (custom GitHub repos, private skill indexes) | [Skills](/user-guide/features/skills) — `hermes skills tap add <repo>` · [Publishing a tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| A first-class **core** inference provider (not a plugin) | [Adding Providers](/developer-guide/adding-providers) |

See the full [Pluggable interfaces table](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each) for a consolidated view of every extension surface including config-driven (TTS, STT, MCP, shell hooks) and drop-in directory (gateway hooks) styles.
:::

:::caution Third-party-product plugins ship standalone — not into the core tree
Plugins that integrate **someone else's product or project** — observability/metrics backends, vendor SaaS connectors, analytics dashboards, paid-service tie-ins — are built and distributed as **standalone plugin repos**, not merged into `NousResearch/hermes-agent`. Users install them into `~/.hermes/plugins/` or via a pip entry point; everything in this guide works the same way from a standalone repo. This is a coupling-and-maintenance decision (the core moves fast and we don't own your backend), not a quality bar — a plugin can be excellent and still belong in its own repo. Promote it in the Nous Research Discord `#plugins-skills-and-skins` channel. See [CONTRIBUTING.md](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md) for the policy.
:::

## What you're building

A **calculator** plugin with two tools:
- `calculate` — evaluate math expressions (`2**16`, `sqrt(144)`, `pi * 5**2`)
- `unit_convert` — convert between units (`100 F → 37.78 C`, `5 km → 3.11 mi`)

Plus a hook that logs every tool call, and a bundled skill file.

## Step 1: Create the plugin directory

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## Step 2: Write the manifest

Create `plugin.yaml`:

```yaml
name: calculator
version: 1.0.0
description: Math calculator — evaluate expressions and convert units
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

This tells Hermes: "I'm a plugin called calculator, I provide tools and hooks." The `provides_tools` and `provides_hooks` fields are lists of what the plugin registers.

Optional fields you could add:
```yaml
author: Your Name
requires_env:          # gate loading on env vars; prompted during install
  - SOME_API_KEY       # simple format — plugin disabled if missing
  - name: OTHER_KEY    # rich format — shows description/url during install
    description: "Key for the Other service"
    url: "https://other.com/keys"
    secret: true
```

## Step 3: Write the tool schemas

Create `schemas.py` — this is what the LLM reads to decide when to call your tools:

```python
"""Tool schemas — what the LLM sees."""

CALCULATE = {
    "name": "calculate",
    "description": (
        "Evaluate a mathematical expression and return the result. "
        "Supports arithmetic (+, -, *, /, **), functions (sqrt, sin, cos, "
        "log, abs, round, floor, ceil), and constants (pi, e). "
        "Use this for any math the user asks about."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate (e.g., '2**10', 'sqrt(144)')",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "Convert a value between units. Supports length (m, km, mi, ft, in), "
        "weight (kg, lb, oz, g), temperature (C, F, K), data (B, KB, MB, GB, TB), "
        "and time (s, min, hr, day)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "The numeric value to convert",
            },
            "from_unit": {
                "type": "string",
                "description": "Source unit (e.g., 'km', 'lb', 'F', 'GB')",
            },
            "to_unit": {
                "type": "string",
                "description": "Target unit (e.g., 'mi', 'kg', 'C', 'MB')",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**Why schemas matter:** The `description` field is how the LLM decides when to use your tool. Be specific about what it does and when to use it. The `parameters` define what arguments the LLM passes.

## Step 4: Write the tool handlers

Create `tools.py` — this is the code that actually executes when the LLM calls your tools:

```python
"""Tool handlers — the code that runs when the LLM calls each tool."""

import json
import math

# Safe globals for expression evaluation — no file/network access
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log2": math.log2, "log10": math.log10,
    "floor": math.floor, "ceil": math.ceil,
    "pi": math.pi, "e": math.e,
    "factorial": math.factorial,
}


def calculate(args: dict, **kwargs) -> str:
    """Evaluate a math expression safely.

    Rules for handlers:
    1. Receive args (dict) — the parameters the LLM passed
    2. Do the work
    3. Return a JSON string — ALWAYS, even on error
    4. Accept **kwargs for forward compatibility
    """
    expression = args.get("expression", "").strip()
    if not expression:
        return json.dumps({"error": "No expression provided"})

    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return json.dumps({"expression": expression, "result": result})
    except ZeroDivisionError:
        return json.dumps({"expression": expression, "error": "Division by zero"})
    except Exception as e:
        return json.dumps({"expression": expression, "error": f"Invalid: {e}"})


# Conversion tables — values are in base units
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # Normalize to Celsius
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # Convert to target
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """Convert between units."""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "Need value, from_unit, and to_unit"})

    try:
        # Temperature
        if from_unit.upper() in {"C","F","K"} and to_unit.upper() in {"C","F","K"}:
            result = _convert_temp(float(value), from_unit.upper(), to_unit.upper())
            return json.dumps({"input": f"{value} {from_unit}", "result": round(result, 4),
                             "output": f"{round(result, 4)} {to_unit}"})

        # Ratio-based conversions
        for table in (_LENGTH, _WEIGHT, _DATA, _TIME):
            lc = {k.lower(): v for k, v in table.items()}
            if from_unit.lower() in lc and to_unit.lower() in lc:
                result = float(value) * lc[from_unit.lower()] / lc[to_unit.lower()]
                return json.dumps({"input": f"{value} {from_unit}",
                                 "result": round(result, 6),
                                 "output": f"{round(result, 6)} {to_unit}"})

        return json.dumps({"error": f"Cannot convert {from_unit} → {to_unit}"})
    except Exception as e:
        return json.dumps({"error": f"Conversion failed: {e}"})
```

**Key rules for handlers:**
1. **Signature:** `def my_handler(args: dict, **kwargs) -> str`
2. **Return:** Always a JSON string. Success and errors alike.
3. **Never raise:** Catch all exceptions, return error JSON instead.
4. **Accept `**kwargs`:** Hermes may pass additional context in the future.

## Step 5: Write the registration

Create `__init__.py` — this wires schemas to handlers:

```python
"""Calculator plugin — registration."""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# Track tool usage via hooks
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """Hook: runs after every tool call (not just ours)."""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("Tool called: %s (session %s)", tool_name, task_id)


def register(ctx):
    """Wire schemas to handlers and register hooks."""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # This hook fires for ALL tool calls, not just ours
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**What `register()` does:**
- Called exactly once at startup
- `ctx.register_tool()` puts your tool in the registry — the model sees it immediately
- `ctx.register_hook()` subscribes to lifecycle events
- `ctx.register_cli_command()` registers a CLI subcommand (e.g. `hermes my-plugin <subcommand>`)
- `ctx.register_command()` registers an in-session slash command (e.g. `/myplugin <args>` inside CLI / gateway chat) — see [Register slash commands](#register-slash-commands) below
- `ctx.dispatch_tool(name, arguments)` — call any other tool (built-in or from another plugin) with the parent agent's context (approvals, credentials, task_id) wired up automatically. Useful from slash-command handlers that need to invoke `terminal`, `read_file`, or any other tool as if the model had called it directly.
- If this function crashes, the plugin is disabled but Hermes continues fine

**`dispatch_tool` example — a slash command that runs a tool:**

```python
def handle_scan(ctx, raw_args: str):
    """Implement /scan by invoking the terminal tool through the registry."""
    result = ctx.dispatch_tool("terminal", {"command": f"find . -name '{raw_args}'"})
    return result  # returned to the caller's chat UI

def register(ctx):
    # Handlers receive a single raw_args string; close over ctx via a lambda.
    ctx.register_command(
        "scan",
        lambda raw: handle_scan(ctx, raw),
        description="Find files matching a glob",
    )
```

The dispatched tool goes through the normal approval, redaction, and budget pipelines — it's a real tool invocation, not a shortcut around them.

## Step 6: Test it

Start Hermes:

```bash
hermes
```

You should see `calculator: calculate, unit_convert` in the banner's tool list.

Try these prompts:
```
What's 2 to the power of 16?
Convert 100 fahrenheit to celsius
What's the square root of 2 times pi?
How many gigabytes is 1.5 terabytes?
```

Check plugin status:
```
/plugins
```

Output:
```
Plugins (1):
  ✓ calculator v1.0.0 (2 tools, 1 hooks)
```

### Debugging plugin discovery

If your plugin doesn't show up — or shows up but isn't loading — set `HERMES_PLUGINS_DEBUG=1` to get verbose discovery logs on stderr:

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

You'll see, for every plugin source (bundled, user, project, entry-points):

- which directories were scanned and how many manifests each yielded
- per manifest: resolved key, name, kind, source, on-disk path
- skip reasons: `disabled via config`, `not enabled in config`, `exclusive plugin`, `no plugin.yaml, depth cap reached`
- on load: the plugin being imported, plus a one-line summary of what `register(ctx)` registered (tools, hooks, slash commands, CLI commands)
- on parse failure: a full traceback for the exception (YAML scanner errors, etc.)
- on `register()` failure: a full traceback pointing at the line in your `__init__.py` that raised

The same logs are always written to `~/.hermes/logs/agent.log` at WARNING level (failures only) and DEBUG level (everything) when the env var is set. So if you can't run with the env var (e.g. from inside the gateway), tail the log file instead:

```bash
hermes logs --level WARNING | grep -i plugin
```

Common reasons a plugin doesn't appear:

- **Not enabled in config** — plugins are opt-in. Run `hermes plugins enable <name>` (the name comes from the `plugins list` output, which can be `<category>/<plugin>` for nested layouts).
- **Wrong directory layout** — must be `~/.hermes/plugins/<plugin-name>/plugin.yaml` (flat) or `~/.hermes/plugins/<category>/<plugin-name>/plugin.yaml` (one level of category nesting, max). Anything deeper is ignored.
- **Missing `__init__.py`** — the plugin directory needs both `plugin.yaml` and `__init__.py` with a `register(ctx)` function.
- **Wrong `kind`** — gateway adapters need `kind: platform` in their manifest. Memory providers are auto-detected as `kind: exclusive` and routed through the `memory.provider` config instead of `plugins.enabled`.

## Your plugin's final structure

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # "I'm calculator, I provide tools and hooks"
├── __init__.py      # Wiring: schemas → handlers, register hooks
├── schemas.py       # What the LLM reads (descriptions + parameter specs)
└── tools.py         # What runs (calculate, unit_convert functions)
```

Four files, clear separation:
- **Manifest** declares what the plugin is
- **Schemas** describe tools for the LLM
- **Handlers** implement the actual logic
- **Registration** connects everything

## What else can plugins do?

### Ship data files

Put any files in your plugin directory and read them at import time:

```python
# In tools.py or __init__.py
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### Bundle skills

Plugins can ship skill files that the agent loads via `skill_view("plugin:skill")`. Register them in your `__init__.py`:

```
~/.hermes/plugins/my-plugin/
├── __init__.py
├── plugin.yaml
└── skills/
    ├── my-workflow/
    │   └── SKILL.md
    └── my-checklist/
        └── SKILL.md
```

```python
from pathlib import Path

def register(ctx):
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)
```

The agent can now load your skills with their namespaced name:

```python
skill_view("my-plugin:my-workflow")   # → plugin's version
skill_view("my-workflow")              # → built-in version (unchanged)
```

**Key properties:**
- Plugin skills are **read-only** — they don't enter `~/.hermes/skills/` and can't be edited via `skill_manage`.
- Plugin skills are **not** listed in the system prompt's `<available_skills>` index — they're opt-in explicit loads.
- Bare skill names are unaffected — the namespace prevents collisions with built-in skills.
- When the agent loads a plugin skill, a bundle context banner is prepended listing sibling skills from the same plugin.

:::tip Legacy pattern
The old `shutil.copy2` pattern (copying a skill into `~/.hermes/skills/`) still works but creates name collision risk with built-in skills. Prefer `ctx.register_skill()` for new plugins.
:::

### Gate on environment variables

If your plugin needs an API key:

```yaml
# plugin.yaml — simple format (backwards-compatible)
requires_env:
  - WEATHER_API_KEY
```

If `WEATHER_API_KEY` isn't set, the plugin is disabled with a clear message. No crash, no error in the agent — just "Plugin weather disabled (missing: WEATHER_API_KEY)".

When users run `hermes plugins install`, they're **prompted interactively** for any missing `requires_env` variables. Values are saved to `.env` automatically.

For a better install experience, use the rich format with descriptions and signup URLs:

```yaml
# plugin.yaml — rich format
requires_env:
  - name: WEATHER_API_KEY
    description: "API key for OpenWeather"
    url: "https://openweathermap.org/api"
    secret: true
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Environment variable name |
| `description` | No | Shown to user during install prompt |
| `url` | No | Where to get the credential |
| `secret` | No | If `true`, input is hidden (like a password field) |

Both formats can be mixed in the same list. Already-set variables are skipped silently.

### Lazy-install optional Python dependencies

If your plugin wraps an SDK that not every user will have installed (a vendor SDK, a heavy ML lib, a platform-specific package), don't `import` it at the top of the module. Use the `tools.lazy_deps.ensure(...)` helper inside the tool handler — Hermes will install the package on first use, gated by the user's `security.allow_lazy_installs` config.

```python
# tools.py
from tools.lazy_deps import ensure, FeatureUnavailable

def my_tool_handler(args, **kwargs):
    try:
        ensure("my-plugin.my-backend")   # key must be in LAZY_DEPS
    except FeatureUnavailable as exc:
        return {"error": str(exc)}

    import my_backend_sdk   # safe now
    ...
```

Two rules from the security model in `tools/lazy_deps.py`:

| Rule | Why |
|---|---|
| Your feature key must appear in the in-tree `LAZY_DEPS` allowlist | Prevents a malicious config from coaxing Hermes into installing arbitrary packages — only specs Hermes itself ships are eligible |
| Specs are PyPI-by-name only | No `--index-url`, `git+https://`, or file: paths. Pin versions with PEP 440 (`"my-sdk>=1.2,<2"`) inside the allowlist entry |

For third-party plugins distributed via pip, declare the optional deps as `[project.optional-dependencies]` extras in your own `pyproject.toml` and tell users to `pip install your-plugin[backend]` — that path doesn't go through `lazy_deps`. The lazy-install dance is most useful for **bundled** plugins where shipping a hard dependency on every install would bloat the base Hermes footprint.

When `security.allow_lazy_installs: false` is set globally, `ensure()` raises `FeatureUnavailable` immediately with a remediation hint — your plugin should catch it and degrade gracefully (return an error result, not crash the tool loop).



### Thread-safe lazy singletons

Plugins often cache an expensive object — an SDK client, an HTTP session, a connection pool — in a module-level variable built on first use:

```python
_client = None

def get_client():
    global _client
    if _client is not None:
        return _client
    _client = ExpensiveClient(...)   # ← TOCTOU race
    return _client
```

This is a footgun. Hermes runs multiple threads in one process (delegated tool calls, background workers, the self-improvement fork), so two threads can hit `get_client()` before `_client` is set, **both** pass the `is not None` check, **both** run the expensive build, and the second write clobbers the first — leaking whatever resource the loser opened (connection, file handle, background thread).

Don't hand-roll the lock. Use the helpers in `plugins/plugin_utils.py`:

```python
from plugins.plugin_utils import lazy_singleton, SingletonSlot

# Zero-arg accessor → decorate it:
@lazy_singleton
def get_client():
    return ExpensiveClient(load_config())   # runs exactly once

client = get_client()    # safe across threads
get_client.reset()       # drop the instance (tests / teardown)


# Accessor that takes a build argument → use a slot:
_slot: SingletonSlot = SingletonSlot()

def get_client(config=None):
    return _slot.get(lambda: ExpensiveClient(resolve(config)))

def reset_client():
    _slot.reset()
```

Both serialize concurrent first calls with double-checked locking and run the factory at most once. If the factory raises, nothing is cached and the next call retries. The honcho memory plugin (`plugins/memory/honcho/client.py`) is the reference consumer.

> Rule of thumb: any time you write `global _something` followed by a `is None` check and a build, reach for one of these instead.



### Conditional tool availability

For tools that depend on optional libraries:

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # False = tool hidden from model
)
```

### Overriding a built-in tool

To replace a built-in tool with your own implementation (e.g. swap the
default browser tool for a headed-Chrome CDP backend, or replace
`web_search` with a custom corporate index), pass `override=True`:

```python
def register(ctx):
    ctx.register_tool(
        name="browser_navigate",             # same name as the built-in
        toolset="plugin_my_browser",         # your own toolset namespace
        schema={...},
        handler=my_custom_navigate,
        override=True,                       # explicit opt-in
    )
```

Without `override=True`, the registry rejects any registration that would
shadow an existing tool from a different toolset — this prevents
accidental overwrites. The override is logged at INFO level so it's
auditable in `~/.hermes/logs/agent.log`. Plugins load after built-in
tools, so the registration order is correct: your handler replaces the
built-in one.

### Register multiple hooks

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

### Hook reference

Each hook is documented in full on the **[Event Hooks reference](/user-guide/features/hooks#plugin-hooks)** — callback signatures, parameter tables, exactly when each fires, and examples. Here's the summary:

| Hook | Fires when | Callback signature | Returns |
|------|-----------|-------------------|---------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | Before any tool executes | `tool_name: str, args: dict, task_id: str` | ignored |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | After any tool returns | `tool_name: str, args: dict, result: str, task_id: str, duration_ms: int` | ignored |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | Once per turn, before the tool-calling loop | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [context injection](#pre_llm_call-context-injection) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | Once per turn, after the tool-calling loop (successful turns only) | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | ignored |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | New session created (first turn only) | `session_id: str, model: str, platform: str` | ignored |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | End of every `run_conversation` call + CLI exit | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | ignored |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/gateway tears down an active session | `session_id: str \| None, platform: str` | ignored |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | Gateway swaps in a new session key (`/new`, `/reset`) | `session_id: str, platform: str` | ignored |
| `kanban_task_claimed` | A kanban task is claimed (dispatcher process, before the worker spawns) | `task_id: str, board: str \| None, assignee: str \| None, run_id: int \| None, profile_name: str` | ignored |
| `kanban_task_completed` | A kanban task completes (worker process) | `task_id, board, assignee, run_id, profile_name, summary: str \| None` | ignored |
| `kanban_task_blocked` | A kanban task is blocked (worker process) | `task_id, board, assignee, run_id, profile_name, reason: str \| None` | ignored |

Most hooks are fire-and-forget observers — their return values are ignored. The exception is `pre_llm_call`, which can inject context into the conversation.

All callbacks should accept `**kwargs` for forward compatibility. If a hook callback crashes, it's logged and skipped. Other hooks and the agent continue normally.

The kanban lifecycle hooks fire **after** the board DB change commits, so a callback always sees durable state and can never hold the SQLite write lock. Because kanban workers run as separate `hermes -p <profile> chat -q` subprocesses, `kanban_task_claimed` fires in the **dispatcher** process while `kanban_task_completed` / `kanban_task_blocked` fire in the **worker** process — hook in the dispatcher to observe every transition centrally, or in the worker for per-task in-session context.

### `pre_llm_call` context injection

This is the only hook whose return value matters. When a `pre_llm_call` callback returns a dict with a `"context"` key (or a plain string), Hermes injects that text into the **current turn's user message**. This is the mechanism for memory plugins, RAG integrations, guardrails, and any plugin that needs to provide the model with additional context.

#### Return format

```python
# Dict with context key
return {"context": "Recalled memories:\n- User prefers dark mode\n- Last project: hermes-agent"}

# Plain string (equivalent to the dict form above)
return "Recalled memories:\n- User prefers dark mode"

# Return None or don't return → no injection (observer-only)
return None
```

Any non-None, non-empty return with a `"context"` key (or a plain non-empty string) is collected and appended to the user message for the current turn.

#### How injection works

Injected context is appended to the **user message**, not the system prompt. This is a deliberate design choice:

- **Prompt cache preservation** — the system prompt stays identical across turns. Anthropic and OpenRouter cache the system prompt prefix, so keeping it stable saves 75%+ on input tokens in multi-turn conversations. If plugins modified the system prompt, every turn would be a cache miss.
- **Ephemeral** — the injection happens at API call time only. The original user message in the conversation history is never mutated, and nothing is persisted to the session database.
- **The system prompt is Hermes's territory** — it contains model-specific guidance, tool enforcement rules, personality instructions, and cached skill content. Plugins contribute context alongside the user's input, not by altering the agent's core instructions.

#### Example: Memory recall plugin

```python
"""Memory plugin — recalls relevant context from a vector store."""

import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall_context(session_id, user_message, is_first_turn, **kwargs):
    """Called before each LLM turn. Returns recalled memories."""
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None  # nothing to inject

        text = "Recalled context from previous sessions:\n"
        text += "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None  # fail silently, don't break the agent

def register(ctx):
    ctx.register_hook("pre_llm_call", recall_context)
```

#### Example: Guardrails plugin

```python
"""Guardrails plugin — enforces content policies."""

POLICY = """You MUST follow these content policies for this session:
- Never generate code that accesses the filesystem outside the working directory
- Always warn before executing destructive operations
- Refuse requests involving personal data extraction"""

def inject_guardrails(**kwargs):
    """Injects policy text into every turn."""
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", inject_guardrails)
```

#### Example: Observer-only hook (no injection)

```python
"""Analytics plugin — tracks turn metadata without injecting context."""

import logging
logger = logging.getLogger(__name__)

def log_turn(session_id, user_message, model, is_first_turn, **kwargs):
    """Fires before each LLM call. Returns None — no context injected."""
    logger.info("Turn: session=%s model=%s first=%s msg_len=%d",
                session_id, model, is_first_turn, len(user_message or ""))
    # No return → no injection

def register(ctx):
    ctx.register_hook("pre_llm_call", log_turn)
```

#### Multiple plugins returning context

When multiple plugins return context from `pre_llm_call`, their outputs are joined with double newlines and appended to the user message together. The order follows plugin discovery order (alphabetical by plugin directory name).

### Register CLI commands

Plugins can add their own `hermes <plugin>` subcommand tree:

```python
def _my_command(args):
    """Handler for hermes my-plugin <subcommand>."""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("All good!")
    elif sub == "config":
        print("Current config: ...")
    else:
        print("Usage: hermes my-plugin <status|config>")

def _setup_argparse(subparser):
    """Build the argparse tree for hermes my-plugin."""
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="Show plugin status")
    subs.add_parser("config", help="Show plugin config")
    subparser.set_defaults(func=_my_command)

def register(ctx):
    ctx.register_tool(...)
    ctx.register_cli_command(
        name="my-plugin",
        help="Manage my plugin",
        setup_fn=_setup_argparse,
        handler_fn=_my_command,
    )
```

After registration, users can run `hermes my-plugin status`, `hermes my-plugin config`, etc.

**Memory provider plugins** use a convention-based approach instead: add a `register_cli(subparser)` function to your plugin's `cli.py` file. The memory plugin discovery system finds it automatically — no `ctx.register_cli_command()` call needed. See the [Memory Provider Plugin guide](/developer-guide/memory-provider-plugin#adding-cli-commands) for details.

**Active-provider gating:** Memory plugin CLI commands only appear when their provider is the active `memory.provider` in config. If a user hasn't set up your provider, your CLI commands won't clutter the help output.

### Register slash commands

Plugins can register in-session slash commands — commands users type during a conversation (like `/lcm status` or `/ping`). These work in both CLI and gateway (Telegram, Discord, etc.).

```python
def _handle_status(raw_args: str) -> str:
    """Handler for /mystatus — called with everything after the command name."""
    if raw_args.strip() == "help":
        return "Usage: /mystatus [help|check]"
    return "Plugin status: all systems nominal"

def register(ctx):
    ctx.register_command(
        "mystatus",
        handler=_handle_status,
        description="Show plugin status",
    )
```

After registration, users can type `/mystatus` in any session. The command appears in autocomplete, `/help` output, and the Telegram bot menu.

**Signature:** `ctx.register_command(name: str, handler: Callable, description: str = "", args_hint: str = "")`

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Command name without the leading slash (e.g. `"lcm"`, `"mystatus"`) |
| `handler` | `Callable[[str], str \| None]` | Called with the raw argument string. May also be `async`. |
| `description` | `str` | Shown in `/help`, autocomplete, and Telegram bot menu |

**Key differences from `register_cli_command()`:**

| | `register_command()` | `register_cli_command()` |
|---|---|---|
| Invoked as | `/name` in a session | `hermes name` in a terminal |
| Where it works | CLI sessions, Telegram, Discord, etc. | Terminal only |
| Handler receives | Raw args string | argparse `Namespace` |
| Use case | Diagnostics, status, quick actions | Complex subcommand trees, setup wizards |

**Conflict protection:** If a plugin tries to register a name that conflicts with a built-in command (`help`, `model`, `new`, etc.), the registration is silently rejected with a log warning. Built-in commands always take precedence.

**Async handlers:** The gateway dispatch automatically detects and awaits async handlers, so you can use either sync or async functions:

```python
async def _handle_check(raw_args: str) -> str:
    result = await some_async_operation()
    return f"Check result: {result}"

def register(ctx):
    ctx.register_command("check", handler=_handle_check, description="Run async check")
```

### Dispatch tools from slash commands

Slash command handlers that need to orchestrate tools (spawn a subagent via `delegate_task`, call `file_edit`, etc.) should use `ctx.dispatch_tool()` instead of reaching into framework internals. The parent-agent context (workspace hints, spinner, model inheritance) is wired up automatically.

```python
def register(ctx):
    def _handle_deliver(raw_args: str):
        result = ctx.dispatch_tool(
            "delegate_task",
            {
                "goal": raw_args,
                "toolsets": ["terminal", "file", "web"],
            },
        )
        return result

    ctx.register_command(
        "deliver",
        handler=_handle_deliver,
        description="Delegate a goal to a subagent",
    )
```

**Signature:** `ctx.dispatch_tool(name: str, args: dict, *, parent_agent=None) -> str`

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Tool name as registered in the tool registry (e.g. `"delegate_task"`, `"file_edit"`) |
| `args` | `dict` | Tool arguments, same shape the model would send |
| `parent_agent` | `Agent \| None` | Optional override. When omitted, resolves from the current CLI agent (or degrades gracefully in gateway mode) |

**Runtime behavior:**

- **CLI mode:** `parent_agent` is resolved from the active CLI agent so workspace hints, spinner, and model selection inherit as expected.
- **Gateway mode:** There is no CLI agent, so tools degrade gracefully — workspace is read from the configured terminal working directory and no spinner is shown.
- **Explicit override:** If the caller passes `parent_agent=` explicitly, it is respected and not overwritten.

This is the public, stable interface for tool dispatch from plugin commands. Plugins should not reach into `ctx._cli_ref.agent` or similar private state.

### Act from inside a hook (profile + tools)

`ctx._cli_ref` is only populated in an **interactive CLI** session. It is `None` in the gateway, in non-interactive `hermes chat -q` runs, and in **kanban-spawned worker sessions** — so any plugin logic that reaches through `_cli_ref` silently no-ops in exactly those contexts. Two stable, session-agnostic APIs cover what hooks actually need:

- **`ctx.profile_name`** — the active profile name (e.g. `"default"`, or the assignee profile in a kanban worker). Derived from `HERMES_HOME`, so it works everywhere with no `_cli_ref` dependency.
- **`ctx.dispatch_tool(name, args)`** — invoke any registered tool (built-in or plugin), including the `kanban_*` tools, `delegate_task`, `terminal`, `read_file`, etc. Works from hook callbacks regardless of which process the hook fires in.

Together these let a kanban lifecycle hook observe a transition and act on the board without touching framework internals:

```python
def register(ctx):
    def on_blocked(*, task_id, reason=None, **kw):
        # Runs in the worker process; ctx._cli_ref is None here.
        ctx.dispatch_tool("kanban_comment", {
            "task_id": task_id,
            "comment": f"[{ctx.profile_name}] auto-noted block: {reason}",
        })
    ctx.register_hook("kanban_task_blocked", on_blocked)
```

For running a full `hermes <subcommand>` (e.g. `hermes kanban show`), shell out with the `terminal` tool via `ctx.dispatch_tool("terminal", {"command": "hermes kanban show ..."})` — there is no in-process slash-command bridge for headless worker sessions, and tools are the supported way to drive Hermes from a hook.

### Handle Slack Block Kit button clicks

Plugins that post Block Kit messages with interactive elements (buttons, overflow menus, datepickers, etc.) can register the click handlers directly with the Slack adapter — no monkey-patching of `slack_bolt.AsyncApp` required.

```python
def register(ctx):
    async def _on_approve(ack, body, action):
        # ack within 3 seconds — slack_bolt requirement.
        await ack()
        # body["channel"]["id"], body["user"]["id"], body["message"]["ts"]
        # action["action_id"], action["value"]
        sweep_id = (action.get("value") or "").split("|", 1)[-1]
        # ...do the deterministic work, then post a follow-up.

    ctx.register_slack_action_handler("inbox_sweep_approve", _on_approve)
```

**Signature:** `ctx.register_slack_action_handler(action_id, callback) -> None`

| Parameter | Type | Description |
|-----------|------|-------------|
| `action_id` | `str \| re.Pattern \| dict` | Whatever `slack_bolt.App.action()` accepts: a literal `action_id`, a compiled regex matching multiple ids, or a constraint dict like `{"action_id": "...", "block_id": "..."}` |
| `callback` | async callable | Receives `(ack, body, action)` per the slack_bolt convention |

**Runtime behavior:**

- The handler is queued at plugin-load time and wired into the adapter's `slack_bolt.AsyncApp` when the Slack platform connects.
- Each callback is wrapped defensively: if your handler raises, the gateway logs the error and best-effort-acks the click so Slack stops retrying.
- Standard slack_bolt rules apply — `await ack()` within 3 seconds, then do longer work.
- For multi-workspace deployments the handler fires for clicks from any connected workspace; use `body["team"]["id"]` if you need to scope behaviour.

This is the public way for plugins to participate in Slack interactivity. Older plugins may patch `SlackAdapter.connect`; prefer this API instead.

:::tip
This guide covers **general plugins** (tools, hooks, slash commands, CLI commands). The sections below sketch the authoring pattern for each specialized plugin type; each links to its full guide for field reference and examples.
:::

## Specialized plugin types

Hermes has five specialized plugin types beyond the general surface. Each ships as a directory under `plugins/<category>/<name>/` (bundled) or `~/.hermes/plugins/<category>/<name>/` (user). The contract differs by category — pick the one you need, then read its full guide.

### Model provider plugins — add an LLM backend

Drop a profile into `plugins/model-providers/<name>/`:

```python
# plugins/model-providers/acme/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="acme",
    aliases=("acme-inference",),
    display_name="Acme Inference",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=("acme-large-v3", "acme-medium-v3"),
))
```

```yaml
# plugins/model-providers/acme/plugin.yaml
name: acme-provider
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI-compatible direct API
```

Lazy-discovered the first time anything calls `get_provider_profile()` or `list_providers()` — `auth.py`, `config.py`, `doctor.py`, `models.py`, `runtime_provider.py`, and the chat_completions transport auto-wire to it. User plugins override bundled ones by name.

**Full guide:** [Model Provider Plugins](/developer-guide/model-provider-plugin) — field reference, overridable hooks (`prepare_messages`, `build_extra_body`, `build_api_kwargs_extras`, `fetch_models`), api_mode selection, auth types, testing.

### Platform plugins — add a gateway channel

Drop an adapter into `plugins/platforms/<name>/`:

```python
# plugins/platforms/myplatform/adapter.py
from gateway.platforms.base import BasePlatformAdapter

class MyPlatformAdapter(BasePlatformAdapter):
    async def connect(self): ...
    async def send(self, chat_id, text): ...
    async def disconnect(self): ...

def check_requirements():
    import os
    return bool(os.environ.get("MYPLATFORM_TOKEN"))

def _env_enablement():
    import os
    tok = os.getenv("MYPLATFORM_TOKEN", "").strip()
    if not tok:
        return None
    return {"token": tok}

def register(ctx):
    ctx.register_platform(
        name="myplatform",
        label="MyPlatform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        required_env=["MYPLATFORM_TOKEN"],
        # Auto-populate PlatformConfig.extra from env so env-only setups
        # show up in `hermes gateway status` without SDK instantiation.
        env_enablement_fn=_env_enablement,
        # Opt in to cron delivery: `deliver=myplatform` routes to this var.
        cron_deliver_env_var="MYPLATFORM_HOME_CHANNEL",
        emoji="💬",
        platform_hint="You are chatting via MyPlatform. Keep responses concise.",
    )
```

```yaml
# plugins/platforms/myplatform/plugin.yaml
name: myplatform-platform
label: MyPlatform
kind: platform
version: 1.0.0
description: MyPlatform gateway adapter
requires_env:
  - name: MYPLATFORM_TOKEN
    description: "Bot token from the MyPlatform console"
    password: true
optional_env:
  - name: MYPLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery"
    password: false
```

**Full guide:** [Adding Platform Adapters](/developer-guide/adding-platform-adapters) — complete `BasePlatformAdapter` contract, message routing, auth gating, setup wizard integration. Look at `plugins/platforms/irc/` for a stdlib-only working example.

### Memory provider plugins — add a cross-session knowledge backend

Drop an implementation of `MemoryProvider` into `plugins/memory/<name>/`:

```python
# plugins/memory/my-memory/__init__.py
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-memory"

    def is_available(self) -> bool:
        import os
        return bool(os.environ.get("MY_MEMORY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        self._session_id = session_id

    def sync_turn(self, user_content, assistant_content, *,
                  session_id="", messages=None) -> None:
        ...

    def prefetch(self, query, *, session_id="") -> str:
        ...

    def get_tool_schemas(self) -> list[dict]:
        return []   # required @abstractmethod — see full guide

def register(ctx):
    ctx.register_memory_provider(MyMemoryProvider())
```

Memory providers are single-select — only one is active at a time, chosen via `memory.provider` in `config.yaml`.

**Full guide:** [Memory Provider Plugins](/developer-guide/memory-provider-plugin) — full `MemoryProvider` ABC, threading contract, profile isolation, CLI command registration via `cli.py`.

### Context engine plugins — replace the context compressor

```python
# plugins/context_engine/my-engine/__init__.py
from agent.context_engine import ContextEngine

class MyContextEngine(ContextEngine):
    @property
    def name(self) -> str:
        return "my-engine"

    def update_from_response(self, usage) -> None: ...
    def should_compress(self, prompt_tokens: int = None) -> bool: ...
    def compress(self, messages, current_tokens=None, focus_topic=None) -> list: ...

def register(ctx):
    ctx.register_context_engine(MyContextEngine())
```

Context engines are single-select — chosen via `context.engine` in `config.yaml`.

**Full guide:** [Context Engine Plugins](/developer-guide/context-engine-plugin).

### Image-generation backends

Drop a provider into `plugins/image_gen/<name>/`:

```python
# plugins/image_gen/my-imggen/__init__.py
from agent.image_gen_provider import ImageGenProvider

class MyImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "my-imggen"

    def is_available(self) -> bool: ...
    def generate(self, prompt: str, aspect_ratio="landscape", **kwargs) -> dict:
        # returns success_response(...) / error_response(...)
        ...

def register(ctx):
    ctx.register_image_gen_provider(MyImageGenProvider())
```

```yaml
# plugins/image_gen/my-imggen/plugin.yaml
name: my-imggen
kind: backend
version: 1.0.0
description: Custom image generation backend
```

**Full guide:** [Image Generation Provider Plugins](/developer-guide/image-gen-provider-plugin) — full `ImageGenProvider` ABC, `list_models()` / `get_setup_schema()` metadata, `success_response()`/`error_response()` helpers, base64 vs URL output, user overrides, pip distribution.

**Reference examples:** `plugins/image_gen/openai/` (DALL-E / GPT-Image via OpenAI SDK), `plugins/image_gen/openai-codex/`, `plugins/image_gen/xai/` (Grok image gen).

## Non-Python extension surfaces

Hermes also accepts extensions that aren't Python plugins at all. These are shown in the [Pluggable interfaces table](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each); the sections below sketch each authoring style briefly.

### MCP servers — register external tools

Model Context Protocol (MCP) servers register their own tools into Hermes without any Python plugin. Declare them in `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    timeout: 120

  linear:
    url: "https://mcp.linear.app/sse"
    auth:
      type: "oauth"
```

Hermes connects to each server at startup, lists its tools, and registers them alongside built-ins. The LLM sees them exactly like any other tool. **Full guide:** [MCP](/user-guide/features/mcp).

### Gateway event hooks — fire on lifecycle events

Drop a manifest + handler into `~/.hermes/hooks/<name>/`:

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: Send a push notification when a long task finishes
events:
  - agent:end
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
async def handle(event_type: str, context: dict) -> None:
    if context.get("duration_seconds", 0) > 120:
        # send notification …
        pass
```

Events include `gateway:startup`, `session:start`, `session:end`, `session:reset`, `agent:start`, `agent:step`, `agent:end`, and wildcard `command:*`. Errors in hooks are caught and logged — they never block the main pipeline.

**Full guide:** [Gateway Event Hooks](/user-guide/features/hooks#gateway-event-hooks).

### Shell hooks — run a shell command on tool calls

If you just want to run a script when a tool fires (notifications, audit logs, desktop alerts, auto-formatters), use shell hooks in `config.yaml` — no Python required:

```yaml
hooks:
  - event: post_tool_call
    command: "notify-send 'Tool ran: {tool_name}'"
    when:
      tools: [terminal, patch, write_file]
```

Supports all the same events as Python plugin hooks (`pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_end`, `pre_gateway_dispatch`) plus structured JSON output for `pre_tool_call` blocking decisions.

**Full guide:** [Shell Hooks](/user-guide/features/hooks#shell-hooks).

### Skill sources — add a custom skill registry

If you maintain a GitHub repo of skills (or want to pull from a community index beyond the built-in sources), add it as a **tap**:

```bash
hermes skills tap add myorg/skills-repo
hermes skills search my-workflow --source myorg/skills-repo
hermes skills install myorg/skills-repo/my-workflow
```

Publishing your own tap is just a GitHub repo with `skills/<skill-name>/SKILL.md` directories — no server or registry signup needed.

**Full guides:** [Skills Hub](/user-guide/features/skills#skills-hub) · [Publishing a custom tap](/user-guide/features/skills#publishing-a-custom-skill-tap) (repo layout, minimal example, non-default paths, trust levels).

### TTS / STT via command templates

Any CLI that reads/writes audio or text can be plugged in through `config.yaml` — no Python code:

```yaml
tts:
  provider: voxcpm
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      voice_compatible: true
```

For STT, point `HERMES_LOCAL_STT_COMMAND` at a shell template. Supported placeholders: `{input_path}`, `{output_path}`, `{format}`, `{voice}`, `{model}`, `{speed}` (TTS); `{input_path}`, `{output_dir}`, `{language}`, `{model}` (STT). Any path-interacting CLI is automatically a plugin.

**Full guides:** [TTS custom command providers](/user-guide/features/tts#custom-command-providers) · [STT](/user-guide/features/tts#voice-message-transcription-stt).

## Distribute via pip

For sharing plugins publicly, add an entry point to your Python package:

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# Plugin auto-discovered on next hermes startup
```

## Distribute for NixOS

:::warning Nix is no longer explicitly supported
Nix/NixOS is no longer an explicitly supported install path (best-effort only) — see [Nix Setup](/getting-started/nix-setup). This section is kept for users already deploying on NixOS.
:::

NixOS users can install your plugin declaratively if you provide a `pyproject.toml` with entry points:

**Entry-point plugins** (recommended for distribution):
```nix
# User's configuration.nix
services.hermes-agent.extraPythonPackages = [
  (pkgs.python312Packages.buildPythonPackage {
    pname = "my-plugin";
    version = "1.0.0";
    src = pkgs.fetchFromGitHub {
      owner = "you";
      repo = "hermes-my-plugin";
      rev = "v1.0.0";
      hash = "sha256-...";  # nix-prefetch-url --unpack
    };
    format = "pyproject";
    build-system = [ pkgs.python312Packages.setuptools ];
  })
];
```

**Directory plugins** (no `pyproject.toml` needed):
```nix
services.hermes-agent.extraPlugins = [
  (pkgs.fetchFromGitHub {
    owner = "you";
    repo = "hermes-my-plugin";
    rev = "v1.0.0";
    hash = "sha256-...";
  })
];
```

See the [Nix Setup guide](/getting-started/nix-setup#plugins) for complete documentation including overlay usage and collision checking.

## Common mistakes

**Handler doesn't return JSON string:**
```python
# Wrong — returns a dict
def handler(args, **kwargs):
    return {"result": 42}

# Right — returns a JSON string
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**Missing `**kwargs` in handler signature:**
```python
# Wrong — will break if Hermes passes extra context
def handler(args):
    ...

# Right
def handler(args, **kwargs):
    ...
```

**Handler raises exceptions:**
```python
# Wrong — exception propagates, tool call fails
def handler(args, **kwargs):
    result = 1 / int(args["value"])  # ZeroDivisionError!
    return json.dumps({"result": result})

# Right — catch and return error JSON
def handler(args, **kwargs):
    try:
        result = 1 / int(args.get("value", 0))
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**Schema description too vague:**
```python
# Bad — model doesn't know when to use it
"description": "Does stuff"

# Good — model knows exactly when and how
"description": "Evaluate a mathematical expression. Use for arithmetic, trig, logarithms. Supports: +, -, *, /, **, sqrt, sin, cos, log, pi, e."
```

---

# SOURCE: website/docs/user-guide/features/mcp.md

---
sidebar_position: 4
title: "MCP (Model Context Protocol)"
description: "Connect Hermes Agent to external tool servers via MCP — and control exactly which MCP tools Hermes loads"
---

# MCP (Model Context Protocol)

MCP lets Hermes Agent connect to external tool servers so the agent can use tools that live outside Hermes itself — GitHub, databases, file systems, browser stacks, internal APIs, and more.

If you have ever wanted Hermes to use a tool that already exists somewhere else, MCP is usually the cleanest way to do it.

## What MCP gives you

- Access to external tool ecosystems without writing a native Hermes tool first
- Local stdio servers and remote HTTP MCP servers in the same config
- Automatic tool discovery and registration at startup
- Utility wrappers for MCP resources and prompts when supported by the server
- Per-server filtering so you can expose only the MCP tools you actually want Hermes to see

## Quick start

1. MCP support ships with the standard install — no extra step needed.

2. Add an MCP server to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

3. Start Hermes:

```bash
hermes chat
```

4. Ask Hermes to use the MCP-backed capability.

For example:

```text
List the files in /home/user/projects and summarize the repo structure.
```

Hermes will discover the MCP server's tools and use them like any other tool.

## Catalog: one-click install for Nous-approved MCPs

Hermes ships a curated catalog of MCP servers that Nous staff has reviewed
and merged. They're disabled by default — install only what you actually
want.

```bash
hermes mcp                # interactive picker (default)
hermes mcp catalog        # plain-text list, scriptable
hermes mcp install n8n    # install a catalog entry by name
```

The picker shows each entry with its current status:

```
n8n          available              Manage and inspect n8n workflows from Hermes
linear       enabled                Linear issue/project management (remote OAuth)
github       installed (disabled)   GitHub repo + PR tools
```

Hit `Enter` on a row to install (and walk through any required credentials),
enable, disable, or uninstall. Catalog entries are stored under
`optional-mcps/` in the hermes-agent repo — presence in that directory means
Nous approval. There is no community submission tier; entries are added by
merging a PR.

Catalog entries can require:

- **API key** — Hermes prompts at install time and writes the value to
  `~/.hermes/.env`. Non-secret values (base URLs) go to the same file.
- **OAuth** (remote MCP) — written as `auth: oauth` in your config; the MCP
  client opens a browser on first connection.
- **OAuth** (third-party provider like Google/GitHub) — Hermes points you at
  `hermes auth <provider>` if you haven't authenticated already.

### Tool selection at install time

After credentials are configured, Hermes probes the MCP server to list every
tool it exposes and presents a checklist:

```
Select tools for 'linear' (SPACE toggle, ENTER confirm)
  [x] find_issues       Find issues matching a query
  [x] get_issue         Get a single issue
  [x] create_issue      Create a new issue
  [ ] delete_workspace  Delete a Linear workspace
  ...
```

The pre-checked rows come from:

1. **Your prior selection** if you've installed this entry before (reinstalls
   preserve what you had — the manifest's defaults don't override it)
2. **The manifest's `tools.default_enabled`** if the entry declares one (some
   catalog entries pre-prune mutating or rarely-useful tools)
3. **Everything** if neither applies

Submit the checklist with ENTER. Only the checked tools end up in
`mcp_servers.<name>.tools.include`. If you select everything, no filter is
written (cleanest config shape, identical behavior).

**If the probe fails** (server unreachable, OAuth not yet completed,
backing service not running), the install still succeeds: the manifest's
`tools.default_enabled` is applied directly (if declared), or no filter is
written (if not). Re-run `hermes mcp configure <name>` once the server is
reachable to refine.

### Trust model

Installing a catalog entry runs whatever the manifest specifies — `git clone`,
the entry's `bootstrap` commands (`pip install`, `npm install`, etc.), and
ultimately the MCP server's own code. Manifests are gated by PR review into
the hermes-agent repo, so Nous has reviewed each entry before it shipped —
**but you should still read the manifest before installing**, especially the
`source:` field's repository, the `install.bootstrap:` commands, and any
`transport.command:` invocation.

Manifests live at
[`optional-mcps/<name>/manifest.yaml`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps)
on GitHub. The picker also prints the manifest's `source:` URL at install
time so you can quickly verify the upstream repo. The web dashboard's MCP
page surfaces the same detail per catalog entry — transport, auth type, the
endpoint URL (HTTP) or command + args (stdio), the git install source/ref and
bootstrap commands, and setup notes — with the `source:` rendered as a
clickable link, so you can inspect exactly what an entry connects to or runs
before clicking Install.

### Manifest version compatibility

Manifests pin a `manifest_version`. The catalog is forward-compatible: if a
PR adds an entry with a newer `manifest_version` than your installed Hermes
understands, the picker will surface a warning (`⚠ '<name>' requires a newer
Hermes`) for that entry instead of silently hiding it. Run `hermes update`
to install the latest Hermes when you see that.

### Runtime `${ENV_VAR}` substitution

Inside an entry's `transport.command`, `transport.args`, `transport.url`,
and `headers`, `${VAR}` placeholders are resolved at server-connect time
from environment variables (which include everything in `~/.hermes/.env`).
This is useful when a catalog entry wants to reference a value the user
configured elsewhere — e.g. `${HOME}/foo` or `${MY_PROVIDER_TOKEN}`.

Note this is distinct from `${INSTALL_DIR}` in catalog manifests, which is
substituted at install-time with the path the catalog cloned the entry's
repo into.

### Updating tool selection later

```bash
hermes mcp configure linear
```

Reopens the same checklist with your current selection pre-checked. Use this
when you want more tools enabled, or when the server has added new tools that
you want to opt into.

### Updating the catalog manifest

MCPs are never auto-updated. Re-run `hermes mcp install <name>` to refresh
after a Hermes update if a manifest version changed.

To add an MCP to the catalog, open a PR against
[`optional-mcps/`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps).

## Two kinds of MCP servers

### Stdio servers

Stdio servers run as local subprocesses and talk over stdin/stdout.

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
```

Use stdio servers when:
- the server is installed locally
- you want low-latency access to local resources
- you are following MCP server docs that show `command`, `args`, and `env`

### HTTP servers

HTTP MCP servers are remote endpoints Hermes connects to directly.

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

Use HTTP servers when:
- the MCP server is hosted elsewhere
- your organization exposes internal MCP endpoints
- you do not want Hermes spawning a local subprocess for that integration

### OAuth-authenticated HTTP servers

Most hosted MCP servers (Linear, Sentry, Atlassian, Asana, Figma, Stripe, …) require OAuth 2.1 instead of a static bearer token. Set `auth: oauth` and Hermes handles discovery, dynamic client registration, PKCE, token exchange, refresh, and step-up auth via the MCP Python SDK.

```yaml
mcp_servers:
  linear:
    url: "https://mcp.linear.app/mcp"
    auth: oauth
```

On first connect, Hermes prints an authorize URL, opens your browser when possible, and waits for the OAuth callback on a local loopback port. Tokens are cached at `~/.hermes/mcp-tokens/<server>.json` with 0o600 perms; subsequent runs reuse them silently until refresh fails.

**Remote / headless hosts.** When Hermes runs on a different machine than your browser, the loopback callback can't reach your laptop. Two ways to complete the flow:

- **Paste-back (no setup):** on an interactive terminal Hermes prints "Or paste the redirect URL here…" alongside the authorize URL. Open the URL in your browser, approve, copy the full URL the browser ends up on (the redirect will show a connection error — that's expected), paste it at the prompt. Bare `?code=…&state=…` query strings work too.
- **SSH port forward:** `ssh -N -L <port>:127.0.0.1:<port> user@host` in a separate terminal, then let the redirect flow normally.

See [OAuth over SSH / Remote Hosts](../../guides/oauth-over-ssh.md#mcp-servers) for the full walkthrough, including DCR-less servers (e.g. Slack), pre-registered `client_id`/`client_secret`, scope customization, and re-auth via `hermes mcp login <server>`.

**Pitfall — providers that don't support automatic registration (Google Drive, Atlassian).** Some servers reject the dynamic client registration step (RFC 7591) that bare `auth: oauth` relies on — Google's official Drive server (`https://drivemcp.googleapis.com/mcp/v1`) returns a `400 Bad Request`, so no OAuth client is created and no token is acquired. The symptom is subtle: these servers also serve `tools/list` *without* auth, so `hermes mcp login` can list the tools and look like it worked, but every real tool call later times out. `hermes mcp login` now detects this (it checks that a token actually landed on disk) and tells you to supply your own OAuth client. Create one in the provider's console and add it to config:

```yaml
mcp_servers:
  googledrive:
    url: "https://drivemcp.googleapis.com/mcp/v1"
    auth: oauth
    oauth:
      client_id: "<your-oauth-client-id>"
      client_secret: "<your-oauth-client-secret>"
```

Then run `hermes mcp login googledrive` — with the pre-registered client, Hermes skips registration and runs the normal browser authorization flow.

**Pitfall — config auto-reload race.** When you edit `~/.hermes/config.yaml` from inside a running Hermes session, the CLI auto-reloads MCP connections with a 30s timeout. That's not enough for an interactive OAuth flow. Add the entry, then run `hermes mcp login <server>` from a fresh terminal — it waits the full 5 minutes for you to complete auth.

## mTLS / client certificates

Remote HTTP MCP servers that require mutual TLS (client-certificate authentication) are supported via `client_cert` / `client_key`. Hermes passes the resolved certificate to the underlying HTTP client for the TLS handshake.

`client_cert` accepts three shapes:

- **A single combined PEM path** — one file holding both the certificate and the private key:

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: "~/.certs/mcp-client.pem"
```

- **A `[cert, key]` 2-tuple** — certificate and key in separate files (equivalent to setting `client_cert` + `client_key`):

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: ["~/.certs/mcp-client.crt", "~/.certs/mcp-client.key"]
```

- **A `[cert, key, password]` 3-tuple** — when the private key is encrypted, the third element is the key passphrase:

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: ["~/.certs/mcp-client.crt", "~/.certs/mcp-client.key", "${MCP_KEY_PASSWORD}"]
```

You can also keep the cert and key fully separate via `client_cert` (combined PEM) plus an explicit `client_key`. Paths support `~` expansion; a missing file raises a clear, server-scoped error rather than an opaque TLS handshake failure.

## Basic configuration reference

Hermes reads MCP config from `~/.hermes/config.yaml` under `mcp_servers`.

### Common keys

| Key | Type | Meaning |
|---|---|---|
| `command` | string | Executable for a stdio MCP server |
| `args` | list | Arguments for the stdio server |
| `env` | mapping | Environment variables passed to the stdio server |
| `url` | string | HTTP MCP endpoint |
| `headers` | mapping | HTTP headers for remote servers |
| `client_cert` | string \| list | Client certificate for mTLS — a combined PEM path, or `[cert, key]` / `[cert, key, password]` |
| `client_key` | string | Client private-key PEM path (when separate from `client_cert`) |
| `timeout` | number | Tool call timeout |
| `connect_timeout` | number | Initial connection timeout |
| `enabled` | bool | If `false`, Hermes skips the server entirely |
| `supports_parallel_tool_calls` | bool | If `true`, tools from this server may run concurrently |
| `tools` | mapping | Per-server tool filtering and utility policy |

### Minimal stdio example

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### Minimal HTTP example

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
```

## Built-in presets

For well-known MCP servers, `hermes mcp add` accepts a `--preset` flag that fills in the transport details so you don't have to look up the command and args. The preset only supplies defaults — anything else (env vars, headers, filtering) you pass on the same command line still wins.

| Preset | What it wires up |
|---|---|
| `codex` | The Codex CLI's MCP server (`codex mcp-server` over stdio). Requires the `codex` CLI on PATH. |

```bash
# Add Codex CLI as an MCP server in one line
hermes mcp add codex --preset codex
```

That writes the equivalent of:

```yaml
mcp_servers:
  codex:
    command: "codex"
    args: ["mcp-server"]
```

You can pick any local name (`hermes mcp add my-codex --preset codex` is fine); the preset only provides the `command`/`args` defaults.

## How Hermes registers MCP tools

Hermes prefixes MCP tools so they do not collide with built-in names:

```text
mcp_<server_name>_<tool_name>
```

Examples:

| Server | MCP tool | Registered name |
|---|---|---|
| `filesystem` | `read_file` | `mcp_filesystem_read_file` |
| `github` | `create-issue` | `mcp_github_create_issue` |
| `my-api` | `query.data` | `mcp_my_api_query_data` |

In practice, you usually do not need to call the prefixed name manually — Hermes sees the tool and chooses it during normal reasoning.

## MCP utility tools

When supported, Hermes also registers utility tools around MCP resources and prompts:

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

These are registered per server with the same prefix pattern, for example:

- `mcp_github_list_resources`
- `mcp_github_get_prompt`

### Important

These utility tools are now capability-aware:
- Hermes only registers resource utilities if the MCP session actually supports resource operations
- Hermes only registers prompt utilities if the MCP session actually supports prompt operations

So a server that exposes callable tools but no resources/prompts will not get those extra wrappers.

## Per-server filtering

You can control which tools each MCP server contributes to Hermes, allowing fine-grained management of your tool namespace.

### Disable a server entirely

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

If `enabled: false`, Hermes skips the server completely and does not even attempt a connection.

### Whitelist server tools

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues]
```

Only those MCP server tools are registered.

### Blacklist server tools

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```

All server tools are registered except the excluded ones.

### Precedence rule

If both are present:

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

`include` wins.

### Filter utility tools too

You can also separately disable Hermes-added utility wrappers:

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

That means:
- `tools.resources: false` disables `list_resources` and `read_resource`
- `tools.prompts: false` disables `list_prompts` and `get_prompt`

### Full example

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues, search_code]
      prompts: false

  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer]
      resources: false

  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

## What happens if everything is filtered out?

If your config filters out all callable tools and disables or omits all supported utilities, Hermes does not create an empty runtime MCP toolset for that server.

That keeps the tool list clean.

## Runtime behavior

### Discovery time

Hermes discovers MCP servers at startup and registers their tools into the normal tool registry.

### Dynamic Tool Discovery

MCP servers can notify Hermes when their available tools change at runtime by sending a `notifications/tools/list_changed` notification. When Hermes receives this notification, it automatically re-fetches the server's tool list and updates the registry — no manual `/reload-mcp` required.

This is useful for MCP servers whose capabilities change dynamically (e.g. a server that adds tools when a new database schema is loaded, or removes tools when a service goes offline).

The refresh is lock-protected so rapid-fire notifications from the same server don't cause overlapping refreshes. Prompt and resource change notifications (`prompts/list_changed`, `resources/list_changed`) are received but not yet acted on.

### Reloading

If you change MCP config, use:

```text
/reload-mcp
```

This reloads MCP servers from config and refreshes the available tool list. For runtime tool changes pushed by the server itself, see [Dynamic Tool Discovery](#dynamic-tool-discovery) above.

### Toolsets

Each configured MCP server also creates a runtime toolset when it contributes at least one registered tool:

```text
mcp-<server>
```

That makes MCP servers easier to reason about at the toolset level.

## Security model

### Stdio env filtering

For stdio servers, Hermes does not blindly pass your full shell environment.

Only explicitly configured `env` plus a safe baseline are passed through. This reduces accidental secret leakage.

### Config-level exposure control

The new filtering support is also a security control:
- disable dangerous tools you do not want the model to see
- expose only a minimal whitelist for a sensitive server
- disable resource/prompt wrappers when you do not want that surface exposed

## Example use cases

### GitHub server with a minimal issue-management surface

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue]
      prompts: false
      resources: false
```

Use it like:

```text
Show me open issues labeled bug, then draft a new issue for the flaky MCP reconnection behavior.
```

### Stripe server with dangerous actions removed

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

Use it like:

```text
Look up the last 10 failed payments and summarize common failure reasons.
```

### Filesystem server for a single project root

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

Use it like:

```text
Inspect the project root and explain the directory layout.
```

## Troubleshooting

### MCP server not connecting

Check:

```bash
# Verify MCP deps are installed (already included in standard install)
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

node --version
npx --version
```

Then verify your config and restart Hermes.

### Tools not appearing

Possible causes:
- the server failed to connect
- discovery failed
- your filter config excluded the tools
- the utility capability does not exist on that server
- the server is disabled with `enabled: false`

If you are intentionally filtering, this is expected.

### Why didn't resource or prompt utilities appear?

Because Hermes now only registers those wrappers when both are true:
1. your config allows them
2. the server session actually supports the capability

This is intentional and keeps the tool list honest.

## Parallel Tool Calls

By default, MCP tools run sequentially — one at a time. If your MCP server exposes tools that are safe to run concurrently (e.g. read-only queries, independent API calls), you can opt-in to parallel execution:

```yaml
mcp_servers:
  docs:
    command: "docs-server"
    supports_parallel_tool_calls: true
```

When `supports_parallel_tool_calls` is `true`, Hermes may execute multiple tools from that server at the same time within a single tool-call batch, just like it does for built-in read-only tools (web_search, read_file, etc.).

:::caution
Only enable parallel calls for MCP servers whose tools are safe to run at the same time. If tools read and write shared state, files, databases, or external resources, review the read/write race conditions before enabling this setting.
:::

## MCP Sampling Support

MCP servers can request LLM inference from Hermes via the `sampling/createMessage` protocol. This allows an MCP server to ask Hermes to generate text on its behalf — useful for servers that need LLM capabilities but don't have their own model access.

Sampling is **enabled by default** for all MCP servers (when the MCP SDK supports it). Configure it per-server under the `sampling` key:

```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    sampling:
      enabled: true            # Enable sampling (default: true)
      model: "openai/gpt-4o"  # Override model for sampling requests (optional)
      max_tokens_cap: 4096     # Max tokens per sampling response (default: 4096)
      timeout: 30              # Timeout in seconds per request (default: 30)
      max_rpm: 10              # Rate limit: max requests per minute (default: 10)
      max_tool_rounds: 5       # Max tool-use rounds in sampling loops (default: 5)
      allowed_models: []       # Allowlist of model names the server may request (empty = any)
      log_level: "info"        # Audit log level: debug, info, or warning (default: info)
```

The sampling handler includes a sliding-window rate limiter, per-request timeouts, and tool-loop depth limits to prevent runaway usage. Metrics (request count, errors, tokens used) are tracked per server instance.

To disable sampling for a specific server:

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```

## Running Hermes as an MCP server

In addition to connecting **to** MCP servers, Hermes can also **be** an MCP server. This lets other MCP-capable agents (Claude Code, Cursor, Codex, or any MCP client) use Hermes's messaging capabilities — list conversations, read message history, and send messages across all your connected platforms.

### When to use this

- You want Claude Code, Cursor, or another coding agent to send and read Telegram/Discord/Slack messages through Hermes
- You want a single MCP server that bridges to all of Hermes's connected messaging platforms at once
- You already have a running Hermes gateway with connected platforms

### Quick start

```bash
hermes mcp serve
```

This starts a stdio MCP server. The MCP client (not you) manages the process lifecycle.

### MCP client configuration

Add Hermes to your MCP client config. For example, in Claude Code's `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

Or if you installed Hermes in a specific location:

```json
{
  "mcpServers": {
    "hermes": {
      "command": "/home/user/.hermes/hermes-agent/venv/bin/hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Available tools

The MCP server exposes 10 tools, matching OpenClaw's channel bridge surface plus a Hermes-specific channel browser:

| Tool | Description |
|------|-------------|
| `conversations_list` | List active messaging conversations. Filter by platform or search by name. |
| `conversation_get` | Get detailed info about one conversation by session key. |
| `messages_read` | Read recent message history for a conversation. |
| `attachments_fetch` | Extract non-text attachments (images, media) from a specific message. |
| `events_poll` | Poll for new conversation events since a cursor position. |
| `events_wait` | Long-poll / block until the next event arrives (near-real-time). |
| `messages_send` | Send a message through a platform (e.g. `telegram:123456`, `discord:#general`). |
| `channels_list` | List available messaging targets across all platforms. |
| `permissions_list_open` | List pending approval requests observed during this bridge session. |
| `permissions_respond` | Allow or deny a pending approval request. |

### Event system

The MCP server includes a live event bridge that polls Hermes's session database for new messages. This gives MCP clients near-real-time awareness of incoming conversations:

```
# Poll for new events (non-blocking)
events_poll(after_cursor=0)

# Wait for next event (blocks up to timeout)
events_wait(after_cursor=42, timeout_ms=30000)
```

Event types: `message`, `approval_requested`, `approval_resolved`

The event queue is in-memory and starts when the bridge connects. Older messages are available through `messages_read`.

### Options

```bash
hermes mcp serve              # Normal mode
hermes mcp serve --verbose    # Debug logging on stderr
```

### How it works

The MCP server reads conversation data directly from Hermes's session store (`~/.hermes/sessions/sessions.json` and the SQLite database). A background thread polls the database for new messages and maintains an in-memory event queue. For sending messages, it uses the same internal send engine (`tools/send_message_tool.py`) that powers cron delivery and the `hermes send` CLI.

The gateway does NOT need to be running for read operations (listing conversations, reading history, polling events). It DOES need to be running for send operations, since the platform adapters need active connections.

### Current limits

- The embedded `hermes mcp serve` exposes a **stdio-only** MCP server today. If you need an HTTP MCP server, run a separate adapter — or, much more commonly, use the MCP **client** side of Hermes, which already speaks both stdio and HTTP (`url` + `headers` in `mcp_servers.yaml` / `config.yaml`; see [HTTP servers](#http-servers) above).
- Event polling at ~200ms intervals via mtime-optimized DB polling (skips work when files are unchanged)
- No `claude/channel` push notification protocol yet
- Text-only sends (no media/attachment sending through `messages_send`)

## Related docs

- [Use MCP with Hermes](/guides/use-mcp-with-hermes)
- [CLI Commands](/reference/cli-commands)
- [Slash Commands](/reference/slash-commands)
- [FAQ](/reference/faq)

---

# SOURCE: website/docs/reference/mcp-config-reference.md

---
sidebar_position: 8
title: "MCP Config Reference"
description: "Reference for Hermes Agent MCP configuration keys, filtering semantics, and utility-tool policy"
---

# MCP Config Reference

This page is the compact reference companion to the main MCP docs.

For conceptual guidance, see:
- [MCP (Model Context Protocol)](/user-guide/features/mcp)
- [Use MCP with Hermes](/guides/use-mcp-with-hermes)

## Root config shape

```yaml
mcp_servers:
  <server_name>:
    command: "..."      # stdio servers
    args: []
    env: {}

    # OR
    url: "..."          # HTTP servers
    headers: {}

    # Optional HTTP/SSE TLS settings:
    ssl_verify: true                # bool or path to a CA bundle (PEM)
    client_cert: "/path/to/cert.pem"  # mTLS client certificate (see below)
    # client_key: "/path/to/key.pem"  # optional, when key lives in a separate file

    enabled: true
    timeout: 120
    connect_timeout: 60
    supports_parallel_tool_calls: false
    tools:
      include: []
      exclude: []
      resources: true
      prompts: true
```

## Server keys

| Key | Type | Applies to | Meaning |
|---|---|---|---|
| `command` | string | stdio | Executable to launch |
| `args` | list | stdio | Arguments for the subprocess |
| `env` | mapping | stdio | Environment passed to the subprocess |
| `url` | string | HTTP | Remote MCP endpoint |
| `headers` | mapping | HTTP | Headers for remote server requests |
| `ssl_verify` | bool or string | HTTP | TLS verification. `true` (default) uses system CAs, `false` disables verification (insecure), or a string path to a custom CA bundle (PEM) |
| `client_cert` | string or list | HTTP | mTLS client certificate. String = path to a PEM file containing cert + key. List `[cert, key]` = separate files. List `[cert, key, password]` = encrypted key |
| `client_key` | string | HTTP | Path to the client private key, when `client_cert` is a string and the key is in a separate file |
| `enabled` | bool | both | Skip the server entirely when false |
| `timeout` | number | both | Tool call timeout in seconds (default: `300`) |
| `connect_timeout` | number | both | Initial connection timeout in seconds (default: `60`) |
| `supports_parallel_tool_calls` | bool | both | Allow tools from this server to run concurrently |
| `tools` | mapping | both | Filtering and utility-tool policy |
| `auth` | string | HTTP | Authentication method. Set to `oauth` to enable OAuth 2.1 with PKCE |
| `sampling` | mapping | both | Server-initiated LLM request policy (see MCP guide) |

## `tools` policy keys

| Key | Type | Meaning |
|---|---|---|
| `include` | string or list | Whitelist server-native MCP tools |
| `exclude` | string or list | Blacklist server-native MCP tools |
| `resources` | bool-like | Enable/disable `list_resources` + `read_resource` |
| `prompts` | bool-like | Enable/disable `list_prompts` + `get_prompt` |

## Filtering semantics

### `include`

If `include` is set, only those server-native MCP tools are registered.

```yaml
tools:
  include: [create_issue, list_issues]
```

### `exclude`

If `exclude` is set and `include` is not, every server-native MCP tool except those names is registered.

```yaml
tools:
  exclude: [delete_customer]
```

### Precedence

If both are set, `include` wins.

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

Result:
- `create_issue` is still allowed
- `delete_issue` is ignored because `include` takes precedence

## Utility-tool policy

Hermes may register these utility wrappers per MCP server:

Resources:
- `list_resources`
- `read_resource`

Prompts:
- `list_prompts`
- `get_prompt`

### Disable resources

```yaml
tools:
  resources: false
```

### Disable prompts

```yaml
tools:
  prompts: false
```

### Capability-aware registration

Even when `resources: true` or `prompts: true`, Hermes only registers those utility tools if the MCP session actually exposes the corresponding capability.

So this is normal:
- you enable prompts
- but no prompt utilities appear
- because the server does not support prompts

## `enabled: false`

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

Behavior:
- no connection attempt
- no discovery
- no tool registration
- config remains in place for later reuse

## Empty result behavior

If filtering removes all server-native tools and no utility tools are registered, Hermes does not create an empty MCP runtime toolset for that server.

## Example configs

### Safe GitHub allowlist

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      resources: false
      prompts: false
```

### Stripe blacklist

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### Resource-only docs server

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      include: []
      resources: true
      prompts: false
```

### TLS client certificate (mTLS)

For HTTP/SSE servers that require a client certificate, set `client_cert` (and optionally `client_key`):

```yaml
mcp_servers:
  # Combined cert + key in a single PEM file
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: "~/secrets/mcp-client.pem"

  # Separate cert and key files
  partner_api:
    url: "https://mcp.partner.example.com/mcp"
    client_cert: "~/secrets/client.crt"
    client_key: "~/secrets/client.key"

  # Encrypted key with a passphrase (3-element list form)
  bank_api:
    url: "https://mcp.bank.example.com/mcp"
    client_cert: ["~/secrets/client.crt", "~/secrets/client.key", "my-passphrase"]

  # Custom CA bundle (private CA / self-signed server)
  lab_api:
    url: "https://mcp.lab.local/mcp"
    ssl_verify: "~/secrets/lab-ca.pem"
    client_cert: "~/secrets/lab-client.pem"
```

Notes:
- Paths support `~` expansion. Missing files fail fast at connect time with a server-scoped error message.
- `ssl_verify: false` disables server certificate verification entirely. Don't use this with real services.
- Works on both Streamable HTTP and SSE transports.

## Reloading config

After changing MCP config, reload servers with:

```text
/reload-mcp
```

## Tool naming

Server-native MCP tools become:

```text
mcp_<server>_<tool>
```

Examples:
- `mcp_github_create_issue`
- `mcp_filesystem_read_file`
- `mcp_my_api_query_data`

Utility tools follow the same prefixing pattern:
- `mcp_<server>_list_resources`
- `mcp_<server>_read_resource`
- `mcp_<server>_list_prompts`
- `mcp_<server>_get_prompt`

### Name sanitization

Hyphens (`-`) and dots (`.`) in both server names and tool names are replaced with underscores before registration. This ensures tool names are valid identifiers for LLM function-calling APIs.

For example, a server named `my-api` exposing a tool called `list-items.v2` becomes:

```text
mcp_my_api_list_items_v2
```

Keep this in mind when writing `include` / `exclude` filters — use the **original** MCP tool name (with hyphens/dots), not the sanitized version.

## OAuth 2.1 authentication

For HTTP servers that require OAuth, set `auth: oauth` on the server entry:

```yaml
mcp_servers:
  protected_api:
    url: "https://mcp.example.com/mcp"
    auth: oauth
```

Behavior:
- Hermes uses the MCP SDK's OAuth 2.1 PKCE flow (metadata discovery, dynamic client registration, token exchange, and refresh)
- On first connect, a browser window opens for authorization
- Tokens are persisted to `~/.hermes/mcp-tokens/<server>.json` and reused across sessions
- Token refresh is automatic; re-authorization only happens when refresh fails
- Only applies to HTTP/StreamableHTTP transport (`url`-based servers)

---

# SOURCE: website/docs/guides/use-mcp-with-hermes.md

---
sidebar_position: 6
title: "Use MCP with Hermes"
description: "A practical guide to connecting MCP servers to Hermes Agent, filtering their tools, and using them safely in real workflows"
---

# Use MCP with Hermes

This guide shows how to actually use MCP with Hermes Agent in day-to-day workflows.

If the feature page explains what MCP is, this guide is about how to get value from it quickly and safely.

## When should you use MCP?

Use MCP when:
- a tool already exists in MCP form and you do not want to build a native Hermes tool
- you want Hermes to operate against a local or remote system through a clean RPC layer
- you want fine-grained per-server exposure control
- you want to connect Hermes to internal APIs, databases, or company systems without modifying Hermes core

Do not use MCP when:
- a built-in Hermes tool already solves the job well
- the server exposes a huge dangerous tool surface and you are not prepared to filter it
- you only need one very narrow integration and a native tool would be simpler and safer

## Mental model

Think of MCP as an adapter layer:

- Hermes remains the agent
- MCP servers contribute tools
- Hermes discovers those tools at startup or reload time
- the model can use them like normal tools
- you control how much of each server is visible

That last part matters. Good MCP usage is not just “connect everything.” It is “connect the right thing, with the smallest useful surface.”

## Step 1: install MCP support

If you installed Hermes with the standard install script, MCP support is already included (the installer runs `uv pip install -e ".[all]"`).

If you installed without extras and need to add MCP separately:

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

For npm-based servers, make sure Node.js and `npx` are available.

For many Python MCP servers, `uvx` is a nice default.

## Step 2: add one server first

Start with a single, safe server.

Example: filesystem access to one project directory only.

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

Then start Hermes:

```bash
hermes chat
```

Now ask something concrete:

```text
Inspect this project and summarize the repo layout.
```

## Step 3: verify MCP loaded

You can verify MCP in a few ways:

- Hermes banner/status should show MCP integration when configured
- ask Hermes what tools it has available
- use `/reload-mcp` after config changes
- check logs if the server failed to connect

A practical test prompt:

```text
Tell me which MCP-backed tools are available right now.
```

## Step 4: start filtering immediately

Do not wait until later if the server exposes a lot of tools.

### Example: whitelist only what you want

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
```

This is usually the best default for sensitive systems.

## WSL2: bridge Hermes in WSL to Windows Chrome

This is the practical setup when:

- Hermes runs inside WSL2
- the browser you want to control is your normal signed-in Chrome on Windows
- `/browser connect` is awkward or unreliable from WSL

In this setup, Hermes does **not** connect to Chrome directly. Instead:

- Hermes runs in WSL
- Hermes starts a local stdio MCP server
- that MCP server is launched through Windows interop (`cmd.exe` or `powershell.exe`)
- the MCP server attaches to your live Windows Chrome session

Mental model:

```text
Hermes (WSL) -> MCP stdio bridge -> Windows Chrome
```

### Why this mode is useful

- you keep your real Windows browser profile, cookies, and logins
- Hermes stays in its supported Unix environment (WSL2)
- browser control is exposed as MCP tools instead of relying on Hermes core browser transport

### Recommended server

Use `chrome-devtools-mcp`.

If your Windows Chrome already has live remote debugging enabled from `chrome://inspect/#remote-debugging`, add it like this from WSL:

```bash
hermes mcp add chrome-devtools-win --command cmd.exe --args /c npx -y chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

After saving the server:

```bash
hermes mcp test chrome-devtools-win
```

Then start a fresh Hermes session or run:

```text
/reload-mcp
```

### Typical prompt

Once loaded, Hermes can use the MCP-prefixed browser tools directly. For example:

```text
调用 MCP 工具 mcp_chrome_devtools_win_list_pages，列出当前浏览器标签页。
```

### When `/browser connect` is the wrong tool

If Hermes runs in WSL and Chrome runs on Windows, `/browser connect` may fail even though Chrome is open and debuggable.

Common reasons:

- WSL cannot reach the same host-local endpoint Chrome exposes to Windows tools
- newer Chrome live-debugging flows are not the same as a classic `ws://localhost:9222`
- the browser is easier to attach to from a Windows-side helper like `chrome-devtools-mcp`

In those cases, keep `/browser connect` for same-environment setups and use MCP for WSL-to-Windows browser bridging.

### Known pitfalls

- Start Hermes from a Windows-mounted path like `/mnt/c/Users/<you>` or `/mnt/c/workspace/...` when using Windows stdio executables through MCP.
- If you start Hermes from `/root` or `/home/...`, Windows may emit a `UNC` current-directory warning before the MCP server starts.
- If `chrome-devtools-mcp --autoConnect` times out while enumerating pages, reduce background/frozen tabs in Chrome and retry.

### Example: blacklist dangerous actions

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### Example: disable utility wrappers too

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

## What does filtering actually affect?

There are two categories of MCP-exposed functionality in Hermes:

1. Server-native MCP tools
- filtered with:
  - `tools.include`
  - `tools.exclude`

2. Hermes-added utility wrappers
- filtered with:
  - `tools.resources`
  - `tools.prompts`

### Utility wrappers you may see

Resources:
- `list_resources`
- `read_resource`

Prompts:
- `list_prompts`
- `get_prompt`

These wrappers only appear if:
- your config allows them, and
- the MCP server session actually supports those capabilities

So Hermes will not pretend a server has resources/prompts if it does not.

## Common patterns

### Pattern 1: local project assistant

Use MCP for a repo-local filesystem or git server when you want Hermes to reason over a bounded workspace.

```yaml
mcp_servers:
  fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]

  git:
    command: "uvx"
    args: ["mcp-server-git", "--repository", "/home/user/project"]
```

Good prompts:

```text
Review the project structure and identify where configuration lives.
```

```text
Check the local git state and summarize what changed recently.
```

### Pattern 2: repo-native work record with Open Scaffold

Use [Open Scaffold](https://github.com/graphanov/open-scaffold) when you want Hermes to read a repository's durable AI-work record: mission, plans, evidence notes, handoff packets, and review/gate results. Hermes remains the agent; Open Scaffold remains the repo-local record.

Add the server for one scaffolded repository:

```bash
hermes mcp add open_scaffold --command npx --args -y open-scaffold@latest mcp serve --repo /absolute/path/to/repo
hermes mcp test open_scaffold
```

Then keep the exposed surface read-oriented. Choose `select` in the `hermes mcp add` prompt, or edit `config.yaml` afterward:

```yaml
mcp_servers:
  open_scaffold:
    command: "npx"
    args: ["-y", "open-scaffold@latest", "mcp", "serve", "--repo", "/absolute/path/to/repo"]
    tools:
      include:
        - list_plans
        - get_plan
        - get_mission
        - list_evidence
        - get_evidence
        - get_status
        - search_plans
        - list_amendments
        - get_handoff
        - analyze_loop
        - gate_loop
      prompts: false
```

Good prompts:

```text
Use the Open Scaffold MCP tools to compile the current handoff packet and tell me the next legal action.
```

```text
Inspect the active plans and evidence notes, then say whether this repo is ready for human review or needs another attempt.
```

Boundary notes:

- Open Scaffold MCP is local-first and read-only by default.
- Its write tools require the server to be started with `--allow-write`; do not enable that until you explicitly want Hermes to mutate `.osc` files.
- Open Scaffold records and gates work; it does not authorize Hermes to merge, publish, deploy, or spawn runtimes.
- Pin `open-scaffold@<version>` instead of `@latest` if you need reproducible tool schemas.

### Pattern 3: GitHub triage assistant

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false
```

Good prompts:

```text
List open issues about MCP, cluster them by theme, and draft a high-quality issue for the most common bug.
```

```text
Search the repo for uses of _discover_and_register_server and explain how MCP tools are registered.
```

### Pattern 4: internal API assistant

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      include: [list_customers, get_customer, list_invoices]
      resources: false
      prompts: false
```

Good prompts:

```text
Look up customer ACME Corp and summarize recent invoice activity.
```

This is the sort of place where a strict whitelist is far better than an exclude list.

### Pattern 4: documentation / knowledge servers

Some MCP servers expose prompts or resources that are more like shared knowledge assets than direct actions.

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: true
      resources: true
```

Good prompts:

```text
List available MCP resources from the docs server, then read the onboarding guide and summarize it.
```

```text
List prompts exposed by the docs server and tell me which ones would help with incident response.
```

## Tutorial: end-to-end setup with filtering

Here is a practical progression.

### Phase 1: add GitHub MCP with a tight whitelist

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
      prompts: false
      resources: false
```

Start Hermes and ask:

```text
Search the codebase for references to MCP and summarize the main integration points.
```

### Phase 2: expand only when needed

If you later need issue updates too:

```yaml
tools:
  include: [list_issues, create_issue, update_issue, search_code]
```

Then reload:

```text
/reload-mcp
```

### Phase 3: add a second server with different policy

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]
```

Now Hermes can combine them:

```text
Inspect the local project files, then create a GitHub issue summarizing the bug you find.
```

That is where MCP gets powerful: multi-system workflows without changing Hermes core.

## Safe usage recommendations

### Prefer allowlists for dangerous systems

For anything financial, customer-facing, or destructive:
- use `tools.include`
- start with the smallest set possible

### Disable unused utilities

If you do not want the model browsing server-provided resources/prompts, turn them off:

```yaml
tools:
  resources: false
  prompts: false
```

### Keep servers scoped narrowly

Examples:
- filesystem server rooted to one project dir, not your whole home directory
- git server pointed at one repo
- internal API server with read-heavy tool exposure by default

### Reload after config changes

```text
/reload-mcp
```

Do this after changing:
- include/exclude lists
- enabled flags
- resources/prompts toggles
- auth headers / env

## Troubleshooting by symptom

### "The server connects but the tools I expected are missing"

Possible causes:
- filtered by `tools.include`
- excluded by `tools.exclude`
- utility wrappers disabled via `resources: false` or `prompts: false`
- server does not actually support resources/prompts

### "The server is configured but nothing loads"

Check:
- `enabled: false` was not left in config
- command/runtime exists (`npx`, `uvx`, etc.)
- HTTP endpoint is reachable
- auth env or headers are correct

### "Why do I see fewer tools than the MCP server advertises?"

Because Hermes now respects your per-server policy and capability-aware registration. That is expected, and usually desirable.

### "How do I remove an MCP server without deleting the config?"

Use:

```yaml
enabled: false
```

That keeps the config around but prevents connection and registration.

## Recommended first MCP setups

Good first servers for most users:
- filesystem
- git
- GitHub
- fetch / documentation MCP servers
- one narrow internal API

Not-great first servers:
- giant business systems with lots of destructive actions and no filtering
- anything you do not understand well enough to constrain

## Related docs

- [MCP (Model Context Protocol)](/user-guide/features/mcp)
- [FAQ](/reference/faq)
- [Slash Commands](/reference/slash-commands)

---

# SOURCE: website/docs/user-guide/features/tool-search.md

---
title: Tool Search
sidebar_position: 95
---

# Tool Search

When you have many MCP servers or non-core plugin tools attached to a
session, their JSON schemas can consume a substantial fraction of the
context window on every turn — even when only a few of them are relevant
to what the user actually asked for.

**Tool Search** is Hermes' opt-in progressive-disclosure layer for that
problem. When activated, MCP and plugin tools are replaced in the
model-visible tools array by three bridge tools, and the model loads each
specific tool's schema on demand.

:::info Built-in Hermes tools never defer
The tools that make up Hermes' core capability set (`terminal`,
`read_file`, `write_file`, `patch`, `search_files`, `todo`, `memory`,
`browser_*`, `web_search`, `web_extract`, `clarify`, `execute_code`,
`delegate_task`, `session_search`, and the rest of
`_HERMES_CORE_TOOLS`) are *always* loaded directly. Only MCP tools and
non-core plugin tools are eligible for deferral.
:::

## How it works

When Tool Search activates for a turn, the model sees three new tools in
place of the deferred ones:

```
tool_search(query, limit?)     — search the deferred-tool catalog
tool_describe(name)            — load the full schema for one tool
tool_call(name, arguments)     — invoke a deferred tool
```

A typical interaction looks like:

```
Model: tool_search("create a github issue")
  → { matches: [{ name: "mcp_github_create_issue", ... }, ...] }
Model: tool_describe("mcp_github_create_issue")
  → { parameters: { type: "object", properties: { ... } } }
Model: tool_call("mcp_github_create_issue", { title: "...", body: "..." })
  → { ok: true, issue_number: 42 }
```

When the model invokes `tool_call`, Hermes **unwraps the bridge** and
dispatches the underlying tool exactly as if the model had called it
directly. Pre-tool-call hooks, guardrails, approval prompts, and
post-tool-call hooks all run against the real tool name — not against
`tool_call`. The activity feed in the CLI and gateway also unwraps so you
see the underlying tool, not the bridge.

## When does it activate?

By default Tool Search runs in `auto` mode: it activates only when the
deferrable tool schemas would consume at least 10% of the active model's
context window. Below that, the tools-array assembly is a pure
pass-through and you pay no overhead.

This decision is re-evaluated every time the tools array is built, so:

- A session with just a few MCP tools and a long context model never
  activates Tool Search.
- A session with many MCP servers attached (15+ tools typically) starts
  activating it.
- Removing MCP servers mid-session correctly returns to direct exposure
  on the next assembly.

## Configuration

```yaml
tools:
  tool_search:
    enabled: auto       # auto (default), on, or off
    threshold_pct: 10   # percentage of context — only used in auto mode
    search_default_limit: 5
    max_search_limit: 20
```

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `auto` | `auto` activates above threshold; `on` always activates if there's at least one deferrable tool; `off` disables entirely. |
| `threshold_pct` | `10` | Percentage of context length at which `auto` mode kicks in. Range 0–100. |
| `search_default_limit` | `5` | Hits returned when the model calls `tool_search` without a `limit`. |
| `max_search_limit` | `20` | Hard upper bound the model can request via `limit`. Range 1–50. |

You can also flip the legacy boolean shape:

```yaml
tools:
  tool_search: true   # equivalent to {enabled: auto}
```

## When NOT to use it

Tool Search trades a fixed per-turn token cost (the three bridge tool
schemas, ~300 tokens) and at least one extra round trip (search →
describe → call) for the savings on the deferred schemas. It's a clear
win when you have many tools and use few per turn; it's overhead when
you have few tools total.

The `auto` default handles this for you. If you set `enabled: on`
unconditionally, expect a slight per-turn cost on small toolsets.

## Trade-offs that don't go away

These come from the prompt-cache integrity invariant — they are inherent
to any progressive-disclosure design, not specific to this implementation:

- **One extra round trip on cold tools.** The first time the model needs
  a deferred tool, it spends one or two extra model calls to find and
  load the schema. The token savings on the static side are real, but a
  portion is paid back at runtime.
- **No cache benefit on deferred schemas.** A loaded `tool_describe`
  result enters the conversation history (so it does get cached on
  subsequent turns) but it never benefits from the system-prompt cache
  prefix.
- **Model-quality dependence.** Tool Search assumes the model can write a
  reasonable search query for the tool it wants. Smaller models do this
  less well; the published Anthropic numbers (49% → 74% on Opus 4 with
  vs. without tool search) show the upside but also that ~26 points of
  accuracy is still retrieval failure.
- **Toolset edits invalidate cache.** Adding or removing a tool mid-
  session changes the bridge tools' descriptions (which include the
  count of deferred tools) and the catalog, so the prompt cache is
  invalidated. This is the same trade-off as any toolset edit.

## Implementation details

- **Retrieval:** BM25 over tokenized tool name + description + parameter
  names. Falls back to a literal substring match on the tool name when
  BM25 returns no positive-score hits, which protects against
  zero-IDF degenerate cases (e.g. searching `"github"` against a
  catalog where every tool name contains "github").
- **Catalog is stateless across turns.** It rebuilds from the current
  tool-defs list every assembly — no session-keyed `Map`. This avoids
  the class of bug where a stored catalog drifts out of sync with the
  live tool registry.
- **The catalog is scoped to the session's toolsets.** `tool_search`,
  `tool_describe`, and `tool_call` only ever see and invoke tools the
  session was actually granted. A subagent, kanban worker, or gateway
  session restricted to a subset of toolsets cannot use the bridge to
  discover or call a tool outside that subset — the deferred catalog is
  the deferrable slice of the session's own enabled/disabled toolsets,
  not the whole process registry.
- **No JS sandbox.** Hermes uses the simpler "structured tools" mode
  (search / describe / call as plain functions). The JS-sandbox "code
  mode" some other implementations offer is a large surface area; we
  skip it.

## See also

- `tools/tool_search.py` — the implementation
- `tests/tools/test_tool_search.py` — the regression suite
- The `openclaw-tool-search-report` PDF in the original implementation
  PR for the research that shaped the design
