<!-- Sections in this file (in order):
  - reference/slash-commands.md
  - reference/profile-commands.md
-->


---

# SOURCE: website/docs/reference/slash-commands.md

---
sidebar_position: 2
title: "Slash Commands Reference"
description: "Complete reference for interactive CLI and messaging slash commands"
---

# Slash Commands Reference

Hermes has two slash-command surfaces, both driven by a central `COMMAND_REGISTRY` in `hermes_cli/commands.py`:

- **Interactive CLI slash commands** — dispatched by `cli.py`, with autocomplete from the registry
- **Messaging slash commands** — dispatched by `gateway/run.py`, with help text and platform menus generated from the registry

Installed skills are also exposed as dynamic slash commands on both surfaces. That includes bundled skills like `/plan`, which opens plan mode and saves markdown plans under `.hermes/plans/` relative to the active workspace/backend working directory.

## Permissions and admin/user split

Every messaging platform that supports a per-user allowlist (Telegram, Discord, Slack, Matrix, Mattermost, Signal, …) also supports a two-tier slash command split: **admins** get every registered command, **regular users** only get the names you list in `user_allowed_commands` (plus the always-allowed floor `/help` and `/whoami`). Configure `allow_admin_from` and `user_allowed_commands` (and the per-group equivalents `group_allow_admin_from` / `group_user_allowed_commands`) inside the platform's `extra:` block in `~/.hermes/gateway-config.yaml`.

See the per-platform docs for examples — the structure is identical across platforms:

- [Telegram](../user-guide/messaging/telegram.md#slash-command-access-control)
- [Discord](../user-guide/messaging/discord.md)
- [Slack](../user-guide/messaging/slack.md)
- [Matrix](../user-guide/messaging/matrix.md)
- [Mattermost](../user-guide/messaging/mattermost.md)
- [Signal](../user-guide/messaging/signal.md)

If `allow_admin_from` is unset for a scope, that scope stays in unrestricted backward-compat mode — every allowed user can run every command.

## Interactive CLI slash commands

Type `/` in the CLI to open the autocomplete menu. Built-in commands are case-insensitive.

### Session

| Command | Description |
|---------|-------------|
| `/new [name]` (alias: `/reset`) | Start a new session (fresh session ID + history). Optional `[name]` sets the initial session title — e.g. `/new my-experiment` opens a fresh session already titled `my-experiment` so it's easy to find later with `/resume` or `/sessions`. Append `now`, `--yes`, or `-y` to skip the confirmation modal — e.g. `/reset now`, `/new --yes my-experiment`. |
| `/clear` | Clear screen and start a new session |
| `/history` | Show conversation history |
| `/save` | Save the current conversation |
| `/prompt` (alias: `/compose`) | Compose your next prompt in `$EDITOR` (markdown) instead of the inline input — useful for long, multi-line, or carefully-formatted prompts. |
| `/retry` | Retry the last message (resend to agent) |
| `/undo` | Remove the last user/assistant exchange |
| `/title` | Set a title for the current session (usage: /title My Session Name) |
| `/compress [here [N] \| focus topic]` | Manually compress conversation context (flush memories + summarize). `/compress here [N]` summarizes everything except the most recent N exchanges (default 2), kept verbatim — pick your own compression boundary. A focus topic narrows what a full summary preserves. |
| `/rollback` | List or restore filesystem checkpoints (usage: /rollback [number]) |
| `/snapshot [create\|restore <id>\|prune]` (alias: `/snap`) | Create or restore state snapshots of Hermes config/state. `create [label]` saves a snapshot, `restore <id>` reverts to it, `prune [N]` removes old snapshots, or list all with no args. |
| `/stop` | Kill all running background processes |
| `/queue <prompt>` (alias: `/q`) | Queue a prompt for the next turn (doesn't interrupt the current agent response). |
| `/steer <prompt>` | Inject a mid-run note that arrives at the agent **after the next tool call** — no interrupt, no new user turn. The text is appended to the last tool result's content once the current tool completes, giving the agent new context without breaking the current tool-calling loop. Use this to nudge direction mid-task (e.g. "focus on the auth module" while the agent is running tests). |
| `/goal <text>` | Set a standing goal Hermes works toward across turns — our take on the Ralph loop. After each turn an auxiliary judge model decides whether the goal is done; if not, Hermes auto-continues. Subcommands: `/goal status`, `/goal pause`, `/goal resume`, `/goal clear`. Budget defaults to 20 turns (`goals.max_turns`); any real user message preempts the continuation loop, and state survives `/resume`. See [Persistent Goals](/user-guide/features/goals) for the full walkthrough. |
| `/subgoal <text>` | Append a user-supplied criterion to the active goal mid-loop. The continuation prompt surfaces all subgoals to the agent verbatim, and the judge factors them into its DONE/CONTINUE verdict — so the goal isn't marked done until the original goal **and** every subgoal are met. Subcommands: `/subgoal` (list), `/subgoal remove <N>`, `/subgoal clear`. Requires an active `/goal`. |
| `/moa <prompt>` | Run a single prompt through the default [Mixture of Agents](/user-guide/features/mixture-of-agents) preset, then restore your current model. One-shot — does not change your session model. |
| `/resume [name]` | Resume a previously-named session |
| `/sessions` (TUI alias: `/switch`) | Classic CLI: browse and resume previous sessions in an interactive picker. TUI: open the live session switcher for currently open TUI sessions. Use `/sessions new` in the TUI to start another live session immediately. |
| `/redraw` | Force a full UI repaint (recovers from terminal drift after tmux resize, mouse selection artifacts, etc.) |
| `/status` | Show session info — model, provider, profile, session ID, working directory, title, created/updated timestamps, token totals, agent-running state — followed by a local **Session recap** block (recent user/assistant turn counts, tool result count, top tools used, last few files touched, the latest user prompt, and the latest assistant reply). The recap is computed locally from the in-memory conversation; no LLM call, no prompt-cache impact. |
| `/agents` (alias: `/tasks`) | Show active agents and running tasks across the current session. |
| `/background <prompt>` (alias: `/bg`, `/btw`) | Run a prompt in a separate background session. The agent processes your prompt independently — your current session stays free for other work. Results appear as a panel when the task finishes. See [CLI Background Sessions](/user-guide/cli#background-sessions). |
| `/branch [name]` (alias: `/fork`) | Branch the current session (explore a different path) |
| `/handoff <platform>` | **CLI only.** Hand the current session off to a messaging platform (Telegram, Discord, Slack, WhatsApp, Signal, Matrix). The gateway picks it up immediately, creates a fresh thread on platforms that support threads (Telegram topics, Discord text-channel threads, Slack message-anchored threads), re-binds the destination to your CLI session_id so the full role-aware transcript replays, and forges a synthetic user turn so the agent confirms it's working in the new place. Your CLI exits cleanly on success with a `/resume` hint; resume locally any time with `/resume <title>`. Refused mid-turn. Requires the gateway to be running and a home channel configured for the target platform (`/sethome` from the destination chat). See [Cross-Platform Handoff](/user-guide/sessions#cross-platform-handoff). |

### Configuration

| Command | Description |
|---------|-------------|
| `/config` | Show current configuration |
| `/model [model-name]` | Show or change the current model. Supports: `/model claude-sonnet-4`, `/model provider:model` (switch providers), `/model custom:model` (custom endpoint), `/model custom:name:model` (named custom provider), `/model custom` (auto-detect from endpoint), and user-defined aliases (`/model fav`, `/model grok` — see [Custom model aliases](#custom-model-aliases)). Use `--global` to persist the change to config.yaml. **Note:** `/model` can only switch between already-configured providers. To add a new provider, exit the session and run `hermes model` from your terminal. |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | Toggle the optional [Codex app-server runtime](../user-guide/features/codex-app-server-runtime) for OpenAI/Codex models. `auto` (default) uses Hermes' standard chat completions; `codex_app_server` hands turns to a `codex app-server` subprocess for native shell, apply_patch, ChatGPT subscription auth, and migrated Codex plugins. Effective on next session. |
| `/personality` | Set a predefined personality |
| `/verbose` | Cycle tool progress display: off → new → all → verbose. Can be [enabled for messaging](#notes) via config. |
| `/fast [normal\|fast\|status]` | Toggle fast mode — OpenAI Priority Processing / Anthropic Fast Mode. Options: `normal`, `fast`, `status`. |
| `/reasoning` | Manage reasoning effort and display (usage: /reasoning [level\|show\|hide]) |
| `/skin` | Show or change the display skin/theme |
| `/statusbar` (alias: `/sb`) | Toggle the context/model status bar on or off |
| `/voice [on\|off\|tts\|status]` | Toggle CLI voice mode and spoken playback. Recording uses `voice.record_key` (default: `Ctrl+B`). |
| `/yolo` | Toggle YOLO mode — skip all dangerous command approval prompts. |
| `/footer [on\|off\|status]` | Toggle the gateway runtime-metadata footer on final replies (shows model, context %, and cwd). |
| `/busy [queue\|steer\|interrupt\|status]` | CLI-only: control what pressing Enter does while Hermes is working — queue the new message, steer mid-turn, or interrupt immediately. |
| `/indicator [kaomoji\|emoji\|unicode\|ascii]` | CLI-only: pick the TUI busy-indicator style. |
| `/timestamps [on\|off\|status]` | CLI-only: toggle `[HH:MM]` timestamps on messages and in `/history`. |

### Tools & Skills

| Command | Description |
|---------|-------------|
| `/tools [list\|disable\|enable] [name...]` | Manage tools: list available tools, or disable/enable specific tools for the current session. Disabling a tool removes it from the agent's toolset and triggers a session reset. |
| `/toolsets` | List available toolsets |
| `/browser [connect\|disconnect\|status]` | Manage a local Chromium-family CDP connection. `connect` attaches browser tools to a running Chrome, Brave, Chromium, or Edge instance (default: `http://127.0.0.1:9222`). `disconnect` detaches. `status` shows current connection. Auto-launches a supported Chromium-family browser if no debugger is detected. |
| `/skills` | Search, install, inspect, or manage skills from online registries. Also the review surface for the skill write-approval gate: `/skills pending`, `/skills diff <id>`, `/skills approve <id>`, `/skills reject <id>`, `/skills approval on\|off`. See [Gating agent skill writes](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval). |
| `/memory [pending\|approve\|reject\|approval]` | Review pending memory writes staged by the write-approval gate (`memory.write_approval`) and toggle the gate. See [Controlling memory writes](/user-guide/features/memory#controlling-memory-writes-write_approval). |
| `/bundles` | List configured skill bundles — `/<name>` slash aliases that preload several skills at once. Configure under `bundles:` in `~/.hermes/config.yaml`. See [Skill Bundles](/user-guide/features/skills#skill-bundles). |
| `/learn <what to learn from>` | Distill a reusable skill from anything you describe — a directory, a URL, the workflow you just walked the agent through, or pasted notes. Open-ended: the agent gathers the sources with its own tools and authors a `SKILL.md` following the house authoring standards. Works in the CLI, the messaging gateway, the TUI, and the dashboard Skills page. |
| `/cron` | Manage scheduled tasks (list, add/create, edit, pause, resume, run, remove) |
| `/suggestions [accept\|dismiss N\|catalog\|clear]` (alias: `/suggest`) | Review suggested automations. Use `/suggestions` to list pending suggestions, `/suggestions accept <id>` to create the proposed automation, `/suggestions dismiss <id>` to reject one, `/suggestions catalog` to add curated starter automations, and `/suggestions clear` to clear resolved suggestion records. Accepted jobs preserve the current surface as the delivery origin. |
| `/blueprint [name] [slot=value ...]` (alias: `/bp`) | Set up an automation from a blueprint template. Bare `/blueprint` lists the catalog; `/blueprint <name>` starts a guided slot-filling flow on the next agent turn; `/blueprint <name> slot=value ...` creates the job directly. |
| `/curator` | Background skill maintenance — `status`, `run`, `pin`, `archive`. See [Curator](/user-guide/features/curator). |
| `/kanban <action>` | Drive the multi-profile, multi-project collaboration board without leaving chat. Full `hermes kanban` surface is available: `/kanban list`, `/kanban show t_abc`, `/kanban create "title" --assignee X`, `/kanban comment t_abc "text"`, `/kanban unblock t_abc`, `/kanban dispatch`, etc. Multi-board support included: `/kanban boards list`, `/kanban boards create <slug>`, `/kanban boards switch <slug>`, `/kanban --board <slug> <action>`. See [Kanban slash command](/user-guide/features/kanban#kanban-slash-command). |
| `/reload-mcp` (alias: `/reload_mcp`) | Reload MCP servers from config.yaml |
| `/reload-skills` (alias: `/reload_skills`) | Re-scan `~/.hermes/skills/` for newly installed or removed skills |
| `/reload` | Reload `.env` variables into the running session (picks up new API keys without restarting) |
| `/plugins` | List installed plugins and their status |
| `/pet [list\|<slug>]` | Toggle or adopt a [petdex](/user-guide/features/pets) mascot. `/pet` toggles the pane, `/pet list` shows installed pets, `/pet <slug>` adopts a specific one. |
| `/hatch <description>` (alias: `/generate-pet`) | Generate a brand-new petdex pet from a text description, using the configured image backend (OpenRouter / Nous Portal). See [Pets](/user-guide/features/pets). |

### Info

| Command | Description |
|---------|-------------|
| `/help` | Show this help message |
| `/version` | Show Hermes Agent version, build, and environment info. |
| `/usage` | Show token usage, cost breakdown, session duration, and — when available from the active provider — an **Account limits** section with remaining quota / credits / plan usage pulled live from the provider's API. |
| `/credits` | Show your Nous credit balance and a top-up handoff link. |
| `/billing` | CLI terminal-billing flow for Nous — view balance, buy credits, and manage auto-reload / monthly limits. |
| `/insights` | Show usage insights and analytics (last 30 days) |
| `/platforms` (alias: `/gateway`) | Show gateway/messaging platform status (CLI-only summary view). |
| `/paste` | Attach a clipboard image |
| `/copy [number]` | Copy the last assistant response to clipboard (or the Nth-from-last with a number). CLI-only. |
| `/image <path>` | Attach a local image file for your next prompt. |
| `/debug` | Upload debug report (system info + logs) and get shareable links. Also available in messaging. |
| `/profile` | Show active profile name and home directory |

### Exit

| Command | Description |
|---------|-------------|
| `/quit` | Exit the CLI (also: `/exit`). |

### Dynamic CLI slash commands

| Command | Description |
|---------|-------------|
| `/<skill-name>` | Load any installed skill as an on-demand command. Example: `/gif-search`, `/github-pr-workflow`, `/excalidraw`. |
| `/skills ...` | Search, browse, inspect, install, audit, publish, and configure skills from registries and the official optional-skills catalog. |

### Quick Commands

User-defined quick commands map a short slash command to either a shell command or another slash command. Configure them in `~/.hermes/config.yaml`:

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  deploy:
    type: exec
    command: scripts/deploy.sh
  inbox:
    type: alias
    target: /gmail unread
```

Then type `/status`, `/deploy`, or `/inbox` in the CLI or a messaging platform. Quick commands are resolved at dispatch time and may not appear in every built-in autocomplete/help table.

String-only prompt shortcuts are not supported as quick commands. Put longer reusable prompts in a skill, or use `type: alias` to point at an existing slash command.

### Custom model aliases

Define your own short names for models you use often, then reach them with `/model <alias>` in the CLI or any messaging platform. Aliases work identically in both, on session-only (default) and `--global` switches.

Two config formats are supported:

**Full form** — pin an exact model, provider, and optionally a base URL. Put this in `~/.hermes/config.yaml`:

```yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
  ollama-qwen:
    model: qwen3-coder:30b
    provider: custom
    base_url: http://localhost:11434/v1
```

**Short form** — `provider/model` in one string. Set from the shell without editing YAML:

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

Then in chat:

```
/model fav            # session-only
/model grok --global  # also persists current-model change to config.yaml
```

User aliases take precedence over built-in short names, so naming an alias `sonnet`, `kimi`, `opus`, etc. will shadow the built-in. Alias names are case-insensitive.

### Alias Resolution

Commands support prefix matching: typing `/h` resolves to `/help`, `/mod` resolves to `/model`. When a prefix is ambiguous (matches multiple commands), the first match in registry order wins. Full command names and registered aliases always take priority over prefix matches.

## Messaging slash commands

The messaging gateway supports the following built-in commands inside Telegram, Discord, Slack, WhatsApp, Signal, Email, Home Assistant, and Teams chats:

| Command | Description |
|---------|-------------|
| `/start` | Platform-protocol command. Many chat platforms (Telegram, Discord, …) send `/start` automatically the first time a user opens a bot conversation. Hermes acknowledges the ping silently — no agent reply, no session burn — so first-contact handshakes don't waste a turn. You can also send it explicitly to confirm the gateway is reachable. |
| `/new` | Start a new conversation. |
| `/reset` | Reset conversation history. |
| `/status` | Show session info, followed by a local **Session recap** block (recent turn counts, top tools used, files touched, latest prompt + reply). |
| `/stop` | Kill all running background processes and interrupt the running agent. |
| `/model [provider:model]` | Show or change the model. Supports provider switches (`/model zai:glm-5`), custom endpoints (`/model custom:model`), named custom providers (`/model custom:local:qwen`), auto-detect (`/model custom`), and user-defined aliases (`/model fav`, `/model grok` — see [Custom model aliases](#custom-model-aliases)). Use `--global` to persist the change to config.yaml. **Note:** `/model` can only switch between already-configured providers. To add a new provider or set up API keys, use `hermes model` from your terminal (outside the chat session). |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | Toggle the optional [Codex app-server runtime](../user-guide/features/codex-app-server-runtime). Persists to `model.openai_runtime` in config.yaml and evicts the cached agent so the next message picks up the new runtime. Effective on next session. |
| `/personality [name]` | Set a personality overlay for the session. |
| `/fast [normal\|fast\|status]` | Toggle fast mode — OpenAI Priority Processing / Anthropic Fast Mode. |
| `/retry` | Retry the last message. |
| `/undo` | Remove the last exchange. |
| `/sethome` (alias: `/set-home`) | Mark the current chat as the platform home channel for deliveries. |
| `/compress [here [N] \| focus topic]` | Manually compress conversation context. `/compress here [N]` keeps the most recent N exchanges (default 2) verbatim and summarizes the rest. A focus topic narrows what a full summary preserves. |
| `/topic [off\|help\|session-id]` | **Telegram DM only.** Manage user-managed multi-session topic mode. `/topic` enables it or shows status; `/topic off` disables it and clears bindings; `/topic help` shows usage; `/topic <session-id>` inside a topic restores a previous session. See [Multi-session DM mode](/user-guide/messaging/telegram#multi-session-dm-mode-topic). |
| `/title [name]` | Set or show the session title. |
| `/resume [name]` | Resume a previously named session. |
| `/usage` | Show token usage, estimated cost breakdown (input/output), context window state, session duration, and — when available from the active provider — an **Account limits** section with remaining quota / credits pulled live from the provider's API. |
| `/credits` | Show your Nous credit balance and a top-up link that opens the portal billing page in a browser. |
| `/insights [days]` | Show usage analytics. |
| `/reasoning [level\|show\|hide]` | Change reasoning effort or toggle reasoning display. |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | Control spoken replies in chat. `join`/`channel`/`leave` manage Discord voice-channel mode. |
| `/rollback [number]` | List or restore filesystem checkpoints. |
| `/background <prompt>` | Run a prompt in a separate background session. Results are delivered back to the same chat when the task finishes. See [Messaging Background Sessions](/user-guide/messaging/#background-sessions). |
| `/queue <prompt>` (alias: `/q`) | Queue a prompt for the next turn without interrupting the current one. |
| `/steer <prompt>` | Inject a message after the next tool call without interrupting — the model picks it up on its next iteration rather than as a new turn. |
| `/goal <text>` | Set a standing goal Hermes works toward across turns — our take on the Ralph loop. A judge model checks after each turn; if not done, Hermes auto-continues until it is, you pause/clear it, or the turn budget (default 20) is hit. Subcommands: `/goal status`, `/goal pause`, `/goal resume`, `/goal clear`. Safe to run mid-agent for status/pause/clear; setting a new goal requires `/stop` first. See [Persistent Goals](/user-guide/features/goals). |
| `/footer [on\|off\|status]` | Toggle the runtime-metadata footer on final replies (shows model, context %, and cwd). |
| `/curator [status\|run\|pin\|archive]` | Background skill maintenance controls. |
| `/suggestions [accept\|dismiss N\|catalog\|clear]` | Review suggested automations right in chat. `/suggestions` lists pending suggestions, `catalog` adds curated starter automations, and `clear` prunes resolved suggestion records. Accepted suggestions keep this chat/thread as the job delivery origin. |
| `/blueprint [name] [slot=value ...]` | Browse cron blueprints, start a guided slot-filling conversation, or create a blueprint job directly. Directly created jobs deliver back to the current chat/thread. |
| `/memory [pending\|approve\|reject\|approval]` | Review pending memory writes staged by the write-approval gate (`memory.write_approval`) — approve or reject them right in chat — and toggle the gate with `/memory approval on\|off`. See [Controlling memory writes](/user-guide/features/memory#controlling-memory-writes-write_approval). |
| `/skills [pending\|approve\|reject\|diff\|approval]` | Review pending **skill** writes staged by the write-approval gate (`skills.write_approval`). Shows a one-line gist per staged write; `/skills diff <id>` is truncated for chat — read the full diff on the CLI or in `~/.hermes/pending/skills/<id>.json`. Only appears when the gate is on (or staged writes remain); search/install stay CLI-only. |
| `/kanban <action>` | Drive the multi-profile, multi-project collaboration board from chat — identical argument surface to the CLI. Bypasses the running-agent guard, so `/kanban unblock t_abc`, `/kanban comment t_abc "…"`, `/kanban list --mine`, `/kanban boards switch <slug>`, etc. work mid-turn. `/kanban create …` auto-subscribes the originating chat to the new task's terminal events. See [Kanban slash command](/user-guide/features/kanban#kanban-slash-command). |
| `/platform <list\|pause\|resume> [name]` | Operate a running gateway platform right from chat. `/platform list` shows every adapter and its state (running, paused-by-breaker, manually-paused); `/platform pause <name>` stops dispatching new messages to that adapter without unloading it; `/platform resume <name>` re-enables it and clears a tripped circuit breaker once the upstream is healthy. |
| `/reload-mcp` (alias: `/reload_mcp`) | Reload MCP servers from config. |
| `/yolo` | Toggle YOLO mode — skip all dangerous command approval prompts. |
| `/commands [page]` | Browse all commands and skills (paginated). |
| `/approve [session\|always]` | Approve and execute a pending dangerous command. `session` approves for this session only; `always` adds to permanent allowlist. |
| `/deny` | Reject a pending dangerous command. |
| `/update` | Update Hermes Agent to the latest version. |
| `/restart` | Gracefully restart the gateway after draining active runs. When the gateway comes back online, it sends a confirmation to the requester's chat/thread. |
| `/debug` | Upload debug report (system info + logs) and get shareable links. |
| `/help` | Show messaging help. |
| `/<skill-name>` | Invoke any installed skill by name. |

## Notes

- `/skin`, `/snapshot`, `/reload`, `/tools`, `/toolsets`, `/browser`, `/config`, `/cron`, `/platforms`, `/paste`, `/image`, `/statusbar`, `/plugins`, `/busy`, `/indicator`, `/redraw`, `/clear`, `/history`, `/save`, `/copy`, `/handoff`, `/billing`, and `/quit` are **CLI-only** commands.
- `/skills` is **CLI-only for search/browse/install**; its write-approval review subcommands (`pending`, `approve`, `reject`, `diff`, `approval`) also work on messaging platforms when `skills.write_approval` is on. `/memory` works on **both** surfaces.
- `/verbose` is **CLI-only by default**, but can be enabled for messaging platforms by setting `display.tool_progress_command: true` in `config.yaml`. When enabled, it cycles the `display.tool_progress` mode and saves to config.
- `/sethome`, `/update`, `/restart`, `/approve`, `/deny`, `/topic`, `/platform`, and `/commands` are **messaging-only** commands.
- `/status`, `/version`, `/background`, `/queue`, `/steer`, `/voice`, `/reload-mcp`, `/reload-skills`, `/rollback`, `/debug`, `/fast`, `/footer`, `/curator`, `/kanban`, `/credits`, `/suggestions`, `/blueprint`, `/learn`, `/sessions`, and `/yolo` work in **both** the CLI and the messaging gateway.
- `/voice join`, `/voice channel`, and `/voice leave` are only meaningful on Discord.
- In the TUI, `/sessions` shows live sessions in the current TUI process. Use `/resume [name]` or `hermes --tui --resume <id-or-title>` for saved or closed transcripts.

## Confirmation prompts for destructive commands

The CLI prompts before running slash commands that throw away unsaved session state. The current destructive set is:

| Command | What it destroys |
|---------|------------------|
| `/clear` | Clears the screen and starts a fresh session — current session ID and in-memory history are gone. |
| `/new` / `/reset` | Starts a fresh session (new session ID + empty history). |
| `/undo` | Removes the last user/assistant exchange from history. |
| `/exit --delete` / `/quit --delete` | Exits **and** permanently deletes the current session's SQLite history and on-disk transcripts. |

For each of these the CLI opens a three-choice modal: **Approve Once** (proceed this time), **Always Approve** (proceed and persist `approvals.destructive_slash_confirm: false` so future destructive commands run without prompting), or **Cancel**.

**Inline skip:** append `now`, `--yes`, or `-y` to bypass the modal for a single invocation — e.g. `/reset now`, `/new --yes my-session`, `/clear -y`, `/undo -y`. Useful when the modal doesn't render correctly on your terminal (see [issue #30768](https://github.com/NousResearch/hermes-agent/issues/30768) for native Windows PowerShell) or when scripting against the CLI.

Set `approvals.destructive_slash_confirm: false` in `~/.hermes/config.yaml` to disable the prompts globally; set it back to `true` to re-enable. See [Security — Destructive slash command confirmation](../user-guide/security.md#dangerous-command-approval) for context.

---

# SOURCE: website/docs/reference/profile-commands.md

---
sidebar_position: 7
---

# Profile Commands Reference

This page covers all commands related to [Hermes profiles](../user-guide/profiles.md). For general CLI commands, see [CLI Commands Reference](./cli-commands.md).

## `hermes profile`

```bash
hermes profile <subcommand>
```

Top-level command for managing profiles. Running `hermes profile` without a subcommand shows help.

| Subcommand | Description |
|------------|-------------|
| `list` | List all profiles. |
| `use` | Set the active (default) profile. |
| `create` | Create a new profile. |
| `describe` | Read or set a profile's description (used by the kanban orchestrator for routing). |
| `delete` | Delete a profile. |
| `show` | Show details about a profile. |
| `alias` | Regenerate the shell alias for a profile. |
| `rename` | Rename a profile. |
| `export` | Export a profile to a tar.gz archive. |
| `import` | Import a profile from a tar.gz archive. |
| `install` | Install a profile distribution from a git URL or local directory. See [Profile Distributions](../user-guide/profile-distributions.md). |
| `update` | Re-pull a distribution-managed profile and re-apply its bundle. |
| `info` | Show distribution metadata for a profile (origin URL, commit, last update). |

## `hermes profile list`

```bash
hermes profile list
```

Lists all profiles. The currently active profile is marked with `*`.

**Example:**

```bash
$ hermes profile list
  default
* work
  dev
  personal
```

No options.

## `hermes profile use`

```bash
hermes profile use <name>
```

Sets `<name>` as the active profile. All subsequent `hermes` commands (without `-p`) will use this profile.

| Argument | Description |
|----------|-------------|
| `<name>` | Profile name to activate. Use `default` to return to the base profile. |

**Example:**

```bash
hermes profile use work
hermes profile use default
```

## `hermes profile create`

```bash
hermes profile create <name> [options]
```

Creates a new profile.

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Name for the new profile. Must be a valid directory name (alphanumeric, hyphens, underscores). |
| `--clone` | Copy `config.yaml`, `.env`, `SOUL.md`, and skills from the current profile. |
| `--clone-all` | Copy everything (config, memories, skills, cron, plugins) from the current profile. Excludes per-profile history: sessions, `state.db`, backups, state-snapshots, checkpoints. |
| `--clone-from <profile>` | Clone config/skills/SOUL from a specific profile instead of the current one. Implies `--clone` unless paired with `--clone-all`. |
| `--no-alias` | Skip wrapper script creation. |
| `--description "<text>"` | One- or two-sentence description of what this profile is good at. Used by the kanban orchestrator to route tasks based on role instead of profile name alone. Skip and add later via `hermes profile describe`. Persisted in `<profile_dir>/profile.yaml`. |
| `--no-skills` | Create an **empty** profile with zero bundled skills enabled. Writes a `.no-bundled-skills` marker into the profile so future `hermes update` runs won't re-seed the bundled set, and refuses to combine with `--clone`, `--clone-from`, or `--clone-all` (which would copy skills in anyway). Useful for narrow orchestrator profiles or sandbox profiles that should not inherit the full skill catalog. To toggle this on an already-created profile (including the default `~/.hermes`), use `hermes skills opt-out` / `hermes skills opt-in`. |

Creating a profile does **not** make that profile directory the default project/workspace directory for terminal commands. If you want a profile to start in a specific project, set `terminal.cwd` in that profile's `config.yaml`.

**Examples:**

```bash
# Blank profile — needs full setup
hermes profile create mybot

# Clone config only from current profile
hermes profile create work --clone

# Clone everything from current profile
hermes profile create backup --clone-all

# Clone config from a specific profile
hermes profile create work2 --clone-from work

# Clone everything from a specific profile
hermes profile create work2-backup --clone-from work --clone-all
```

## `hermes profile describe`

```bash
hermes profile describe [<name>] [options]
```

Read or set a profile's description. The description is consumed by the kanban orchestrator to route tasks based on what each profile is good at, rather than guessing from the profile name alone. Persisted in `<profile_dir>/profile.yaml` so it survives reboots and is shared with the gateway.

With no flags, prints the current description (or `(no description set for '<name>')` if empty).

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Profile to describe. Required unless `--all --auto` is used. |
| `--text "<text>"` | Set the description to this exact text (user-authored). Overwrites any existing description. |
| `--auto` | Auto-generate a 1-2 sentence description via the auxiliary LLM, based on the profile's installed skills, configured model, and name. Configure the model under `auxiliary.profile_describer` in `config.yaml`. Auto-generated descriptions are marked `description_auto: true` so the dashboard can flag them for review. |
| `--overwrite` | With `--auto`, replace user-authored descriptions too (default: skip profiles whose description was set explicitly). |
| `--all` | With `--auto`, sweep every profile missing a description. |

**Examples:**

```bash
# Read the current description
hermes profile describe researcher

# Set it explicitly
hermes profile describe researcher --text "Reads source code and writes findings."

# Let the LLM generate one
hermes profile describe researcher --auto

# Fill in descriptions for every profile that doesn't have one
hermes profile describe --all --auto
```

## `hermes profile delete`

```bash
hermes profile delete <name> [options]
```

Deletes a profile and removes its shell alias.

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Profile to delete. |
| `--yes`, `-y` | Skip confirmation prompt. |

**Example:**

```bash
hermes profile delete mybot
hermes profile delete mybot --yes
```

:::warning
This permanently deletes the profile's entire directory including all config, memories, sessions, and skills. Cannot delete the currently active profile.
:::

## `hermes profile show`

```bash
hermes profile show <name>
```

Displays details about a profile including its home directory, configured model, gateway status, skills count, and configuration file status.

This shows the profile's Hermes home directory, not the terminal working directory. Terminal commands start from `terminal.cwd` (or the launch directory on the local backend when `cwd: "."`).

| Argument | Description |
|----------|-------------|
| `<name>` | Profile to inspect. |

**Example:**

```bash
$ hermes profile show work
Profile: work
Path:    ~/.hermes/profiles/work
Model:   anthropic/claude-sonnet-4 (anthropic)
Gateway: stopped
Skills:  12
.env:    exists
SOUL.md: exists
Alias:   ~/.local/bin/work
```

## `hermes profile alias`

```bash
hermes profile alias <name> [options]
```

Regenerates the shell alias script at `~/.local/bin/<name>`. Useful if the alias was accidentally deleted or if you need to update it after moving your Hermes installation.

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Profile to create/update the alias for. |
| `--remove` | Remove the wrapper script instead of creating it. |
| `--name <alias>` | Custom alias name (default: profile name). |

**Example:**

```bash
hermes profile alias work
# Creates/updates ~/.local/bin/work

hermes profile alias work --name mywork
# Creates ~/.local/bin/mywork

hermes profile alias work --remove
# Removes the wrapper script
```

## `hermes profile rename`

```bash
hermes profile rename <old-name> <new-name>
```

Renames a profile. Updates the directory and shell alias.

| Argument | Description |
|----------|-------------|
| `<old-name>` | Current profile name. |
| `<new-name>` | New profile name. |

**Example:**

```bash
hermes profile rename mybot assistant
# ~/.hermes/profiles/mybot → ~/.hermes/profiles/assistant
# ~/.local/bin/mybot → ~/.local/bin/assistant
```

## `hermes profile export`

```bash
hermes profile export <name> [options]
```

Exports a profile as a compressed tar.gz archive.

| Argument / Option | Description |
|-------------------|-------------|
| `<name>` | Profile to export. |
| `-o`, `--output <path>` | Output file path (default: `<name>.tar.gz`). |

**Example:**

```bash
hermes profile export work
# Creates work.tar.gz in the current directory

hermes profile export work -o ./work-2026-03-29.tar.gz
```

## `hermes profile import`

```bash
hermes profile import <archive> [options]
```

Imports a profile from a tar.gz archive.

| Argument / Option | Description |
|-------------------|-------------|
| `<archive>` | Path to the tar.gz archive to import. |
| `--name <name>` | Name for the imported profile (default: inferred from archive). |

**Example:**

```bash
hermes profile import ./work-2026-03-29.tar.gz
# Infers profile name from the archive

hermes profile import ./work-2026-03-29.tar.gz --name work-restored
```

## Distribution commands

:::tip
**New to distributions?** Start with the [Profile Distributions user guide](../user-guide/profile-distributions.md) — it covers the why, when, and how with full examples. The sections below are a dry CLI reference for when you know what you want.
:::

Distributions turn a profile into a shareable, versioned artifact published
as a **git repository**. A recipient installs the distribution with a single
command and can update it in place later without touching their local
memories, sessions, or credentials.

`auth.json` and `.env` are never part of a distribution — they stay on the
installing user's machine.

The recipient's user data (memories, sessions, auth, their own edits to
`.env`) is always preserved across the initial install and subsequent
updates.

:::info
`hermes profile export` / `import` are still the right commands for
**local backup and restore** of a profile on your own machine. Distribution
(`install` / `update` / `info`) is a separate concept: ship a profile via
git so someone else can install it.
:::

### `hermes profile install`

```bash
hermes profile install <source> [--name <name>] [--alias] [--force] [--yes]
```

Installs a profile distribution from a git URL or a local directory.

| Option | Description |
|--------|-------------|
| `<source>` | Git URL (`github.com/user/repo`, `https://...`, `git@...`, `ssh://`, `git://`) or a local directory containing `distribution.yaml` at its root. |
| `--name NAME` | Override the profile name from the manifest. |
| `--alias` | Also create a shell wrapper (e.g. `telemetry` → `hermes -p telemetry`). |
| `--force` | Overwrite an existing profile of the same name. User data is still preserved. |
| `-y`, `--yes` | Skip the manifest-preview confirmation prompt. |

The installer shows the manifest, lists required env vars, and warns about
cron jobs before asking for confirmation. Required env vars go into a
`.env.EXAMPLE` file you copy to `.env` and fill in.

**Examples:**

```bash
# Install from a GitHub repo (shorthand)
hermes profile install github.com/kyle/telemetry-distribution --alias

# Install from a full HTTPS git URL
hermes profile install https://github.com/kyle/telemetry-distribution.git

# Install from SSH
hermes profile install git@github.com:kyle/telemetry-distribution.git

# Install from a local directory during development
hermes profile install ./telemetry/
```

### `hermes profile update`

```bash
hermes profile update <name> [--force-config] [--yes]
```

Re-clones the distribution from its recorded source and applies updates.
Distribution-owned files (SOUL.md, skills/, cron/, mcp.json) are
overwritten; user data (memories, sessions, auth, .env) is never touched.

`config.yaml` is preserved by default to keep your local overrides.
Pass `--force-config` to reset it to the distribution's shipped config.

### `hermes profile info`

```bash
hermes profile info <name>
```

Prints the profile's distribution manifest — name, version, required
Hermes version, author, env var requirements, the source URL/path, and
the `Installed:` timestamp recorded when the distribution was last
`install`-ed or `update`-d. Useful for checking what a shared profile
needs before installing it, and for spotting "this profile was installed
6 months ago and hasn't been updated."

`hermes profile list` also shows the distribution name and version in a
`Distribution` column, and `hermes profile show <name>` / `delete <name>`
surface the source URL so you can tell at a glance which profiles came
from a git repo vs. were created locally.

### Private distributions

A private git repository works as a distribution source with no extra
configuration — the install shells out to your normal `git` binary, so
whatever authentication your shell is already set up for (SSH key,
`git credential` helper, GitHub CLI's stored HTTPS credentials) applies
transparently.

```bash
# Uses your SSH key, the same as any other `git clone`
hermes profile install git@github.com:your-org/internal-assistant.git

# Uses your git credential helper
hermes profile install https://github.com/your-org/internal-assistant.git
```

If a clone prompts for credentials interactively in your terminal during
install, that prompt flows through. Set up your auth the way you'd
normally use `git clone` against the same repo first, then install.

### Distribution manifest (`distribution.yaml`)

Every distribution has a `distribution.yaml` at the root of its repository:

```yaml
name: telemetry
version: 0.1.0
description: "Compliance monitoring harness"
hermes_requires: ">=0.12.0"
author: "Your Name"
license: "MIT"
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API key"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "Memory graph URL"
    required: false
    default: "http://127.0.0.1:8000/sse"
distribution_owned:   # optional; defaults to SOUL.md, config.yaml,
                      #   mcp.json, skills/, cron/, distribution.yaml
  - SOUL.md
  - skills/compliance/
  - cron/
```

`hermes_requires` supports `>=`, `<=`, `==`, `!=`, `>`, `<`, or a bare
version (treated as `>=`). Install fails with a clear error if the current
Hermes version doesn't satisfy the spec.

`distribution_owned` is optional. If set, only those paths are replaced on
update; anything else in the profile stays user-owned. If omitted, the
defaults above apply.

### Publishing a distribution

Authoring a distribution is just a git push:

1. In your profile directory, create `distribution.yaml` with at least `name`
   and `version`.
2. Initialize a git repo (or use an existing one) and push to GitHub /
   GitLab / any host Hermes can clone from.
3. Tell recipients to run `hermes profile install <your-repo-url>`.

Use git tags for versioned releases — recipients who clone `HEAD` get your
latest state, and you can always bump `version:` in the manifest.

## `hermes -p` / `hermes --profile`

```bash
hermes -p <name> <command> [options]
hermes --profile <name> <command> [options]
```

Global flag to run any Hermes command under a specific profile without changing the sticky default. This overrides the active profile for the duration of the command.

| Option | Description |
|--------|-------------|
| `-p <name>`, `--profile <name>` | Profile to use for this command. |

**Examples:**

```bash
hermes -p work chat -q "Check the server status"
hermes --profile dev gateway start
hermes -p personal skills list
hermes -p work config edit
```

## `hermes completion`

```bash
hermes completion <shell>
```

Generates shell completion scripts. Includes completions for profile names and profile subcommands.

| Argument | Description |
|----------|-------------|
| `<shell>` | Shell to generate completions for: `bash`, `zsh`, or `fish`. |

**Examples:**

```bash
# Install completions
hermes completion bash >> ~/.bashrc
hermes completion zsh >> ~/.zshrc
hermes completion fish > ~/.config/fish/completions/hermes.fish

# Reload shell
source ~/.bashrc
```

After installation, tab completion works for:
- `hermes profile <TAB>` — subcommands (list, use, create, etc.)
- `hermes profile use <TAB>` — profile names
- `hermes -p <TAB>` — profile names

## See also

- [Profiles User Guide](../user-guide/profiles.md)
- [CLI Commands Reference](./cli-commands.md)
- [FAQ — Profiles section](./faq.md#profiles)
