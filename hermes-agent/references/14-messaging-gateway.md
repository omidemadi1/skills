<!-- Sections in this file (in order):
  - user-guide/messaging/index.md
  - user-guide/messaging/telegram.md
  - user-guide/messaging/discord.md
  - user-guide/messaging/slack.md
  - user-guide/messaging/whatsapp.md
  - user-guide/messaging/signal.md
  - user-guide/messaging/email.md
-->


---

# SOURCE: website/docs/user-guide/messaging/index.md

---
sidebar_position: 1
title: "Messaging Gateway"
description: "Chat with Hermes from Telegram, Discord, Slack, WhatsApp, Signal, SMS, Email, Home Assistant, Mattermost, Matrix, DingTalk, Yuanbao, Microsoft Teams, LINE, Raft, Webhooks, or any OpenAI-compatible frontend via the API server — architecture and setup overview"
---

# Messaging Gateway

Chat with Hermes from Telegram, Discord, Slack, WhatsApp, Signal, SMS, Email, Home Assistant, Mattermost, Matrix, DingTalk, Feishu/Lark, WeCom, Weixin, BlueBubbles (iMessage), QQ, Yuanbao, Microsoft Teams, LINE, ntfy, or your browser. The gateway is a single background process that connects to all your configured platforms, handles sessions, runs cron jobs, and delivers voice messages.

For the full voice feature set — including CLI microphone mode, spoken replies in messaging, and Discord voice-channel conversations — see [Voice Mode](/user-guide/features/voice-mode) and [Use Voice Mode with Hermes](/guides/use-voice-mode-with-hermes).

:::tip
Bots need both a model provider and tool providers (TTS, web). A [Nous Portal](/integrations/nous-portal) subscription bundles all of them.
:::

## Platform Comparison

| Platform | Voice | Images | Files | Threads | Reactions | Typing | Streaming |
|----------|:-----:|:------:|:-----:|:-------:|:---------:|:------:|:---------:|
| Telegram | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Discord | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Slack | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Google Chat | — | ✅ | ✅ | ✅ | — | ✅ | — |
| WhatsApp | — | ✅ | ✅ | — | — | ✅ | ✅ |
| Signal | — | ✅ | ✅ | — | — | ✅ | ✅ |
| SMS | — | — | — | — | — | — | — |
| Email | — | ✅ | ✅ | ✅ | — | — | — |
| Home Assistant | — | — | — | — | — | — | — |
| Mattermost | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Matrix | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DingTalk | — | ✅ | ✅ | — | ✅ | — | ✅ |
| Feishu/Lark | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WeCom | ✅ | ✅ | ✅ | — | — | — | — |
| WeCom Callback | — | — | — | — | — | — | — |
| Weixin | ✅ | ✅ | ✅ | — | — | ✅ | ✅ |
| BlueBubbles | — | ✅ | ✅ | — | ✅ | ✅ | — |
| QQ | ✅ | ✅ | ✅ | — | — | ✅ | — |
| Yuanbao | ✅ | ✅ | ✅ | — | — | ✅ | ✅ |
| Microsoft Teams | — | ✅ | — | ✅ | — | ✅ | — |
| LINE | — | ✅ | ✅ | — | — | ✅ | — |
| ntfy | — | — | — | — | — | — | — |
| Raft | — | — | — | — | — | — | — |
| IRC | — | — | — | — | — | — | — |

**Voice** = TTS audio replies and/or voice message transcription. **Images** = send/receive images. **Files** = send/receive file attachments. **Threads** = threaded conversations. **Reactions** = emoji reactions on messages. **Typing** = typing indicator while processing. **Streaming** = progressive message updates via editing.

## Architecture

```mermaid
flowchart TB
    subgraph Gateway["Hermes Gateway"]
        subgraph Adapters["Platform adapters"]
            tg[Telegram]
            dc[Discord]
            wa[WhatsApp]
            sl[Slack]
            gc[Google Chat]
            sig[Signal]
            sms[SMS]
            em[Email]
            ha[Home Assistant]
            mm[Mattermost]
            mx[Matrix]
            dt[DingTalk]
    fs[Feishu/Lark]
    wc[WeCom]
    wcb[WeCom Callback]
    wx[Weixin]
    bb[BlueBubbles]
    qq[QQ]
    yb[Yuanbao]
    ms[Microsoft Teams]
    api["API Server<br/>(OpenAI-compatible)"]
    wh[Webhooks]
        end

        store["Session store<br/>per chat"]
        agent["AIAgent<br/>run_agent.py"]
        cron["Cron scheduler<br/>ticks every 60s"]
    end

    tg --> store
    dc --> store
    wa --> store
    sl --> store
    gc --> store
    sig --> store
    sms --> store
    em --> store
    ha --> store
    mm --> store
    mx --> store
    dt --> store
    fs --> store
    wc --> store
    wcb --> store
    wx --> store
    bb --> store
    qq --> store
    yb --> store
    ms --> store
    api --> store
    wh --> store
    store --> agent
    cron --> store
```

Each platform adapter receives messages, routes them through a per-chat session store, and dispatches them to the AIAgent for processing. The gateway also runs the cron scheduler, ticking every 60 seconds to execute any due jobs.

## Intentional Silence Tokens

For group chats, hooks, and automation flows, Hermes supports explicit silence tokens. If the agent's final response is exactly one supported token, the gateway suppresses outbound delivery and sends nothing to the chat.

Supported tokens:

- `[SILENT]`
- `SILENT`
- `NO_REPLY`
- `NO REPLY`

Whitespace and case are normalized, but the whole final response must be the token. A sentence like "Use `[SILENT]` when nothing changed" is delivered normally.

Silence is a delivery decision only. Hermes keeps the assistant silence turn in the session transcript, so the conversation still alternates normally:

```text
user: side-channel chatter
assistant: [SILENT]   # stored, not delivered
user: next message
```

Failed turns still surface as errors; Hermes does not hide failures just because the text resembles a silence token.

## Quick Setup

The easiest way to configure messaging platforms is the interactive wizard:

```bash
hermes gateway setup        # Interactive setup for all messaging platforms
```

This walks you through configuring each platform with arrow-key selection, shows which platforms are already configured, and offers to start/restart the gateway when done.

## Gateway Commands

```bash
hermes gateway              # Run in foreground
hermes gateway setup        # Configure messaging platforms interactively
hermes gateway install      # Install as a user service (Linux) / launchd service (macOS)
sudo hermes gateway install --system   # Linux only: install a boot-time system service
hermes gateway start        # Start the default service
hermes gateway stop         # Stop the default service
hermes gateway status       # Check default service status
hermes gateway status --system         # Linux only: inspect the system service explicitly
```

## Chat Commands (Inside Messaging)

| Command | Description |
|---------|-------------|
| `/new` or `/reset` | Start a fresh conversation |
| `/model [provider:model]` | Show or change the model (supports `provider:model` syntax) |
| `/personality [name]` | Set a personality |
| `/retry` | Retry the last message |
| `/undo` | Remove the last exchange |
| `/status` | Show session info |
| `/whoami` | Show your slash command access on this scope (admin / user / unrestricted) |
| `/stop` | Stop the running agent |
| `/approve` | Approve a pending dangerous command |
| `/deny` | Reject a pending dangerous command |
| `/sethome` | Set this chat as the home channel |
| `/compress` | Manually compress conversation context |
| `/title [name]` | Set or show the session title |
| `/resume [name]` | Resume a previously named session |
| `/usage` | Show token usage for this session |
| `/insights [days]` | Show usage insights and analytics |
| `/reasoning [level\|show\|hide]` | Change reasoning effort or toggle reasoning display |
| `/voice [on\|off\|tts\|join\|leave\|status]` | Control messaging voice replies and Discord voice-channel behavior |
| `/rollback [number]` | List or restore filesystem checkpoints |
| `/background <prompt>` | Run a prompt in a separate background session |
| `/reload-mcp` | Reload MCP servers from config |
| `/update` | Update Hermes Agent to the latest version |
| `/help` | Show available commands |
| `/<skill-name>` | Invoke any installed skill |

## Session Management

### Session Persistence

Sessions persist across messages until they reset. The agent remembers your conversation context.

### Reset Policies

Sessions reset based on configurable policies:

| Policy | Default | Description |
|--------|---------|-------------|
| Daily | 4:00 AM | Reset at a specific hour each day |
| Idle | 1440 min | Reset after N minutes of inactivity |
| Both | (combined) | Whichever triggers first |

A live background process (started with `terminal(background=true)`) normally
protects its session from resetting so output isn't lost. To stop a forgotten
process — say a preview server — from pinning a session open forever, a
background process older than `bg_process_max_age_hours` (default **24**) no
longer blocks reset. The process is **not** killed, only ignored by the reset
guard. Set it to `0` to disable the cutoff (any live process blocks reset, the
old behavior), or raise it if you run legitimate multi-day jobs whose liveness
should keep the conversation open.

Configure per-platform overrides in `~/.hermes/gateway.json`:

```json
{
  "reset_by_platform": {
    "telegram": { "mode": "idle", "idle_minutes": 240 },
    "discord": { "mode": "idle", "idle_minutes": 60 }
  }
}
```

## Security

**By default, the gateway denies all users who are not in an allowlist or paired via DM.** This is the safe default for a bot with terminal access.

```bash
# Restrict to specific users (recommended):
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=123456789012345678
SIGNAL_ALLOWED_USERS=+155****4567,+155****6543
SMS_ALLOWED_USERS=+155****4567,+155****6543
EMAIL_ALLOWED_USERS=trusted@example.com,colleague@work.com
MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c
MATRIX_ALLOWED_USERS=@alice:matrix.org
DINGTALK_ALLOWED_USERS=user-id-1
FEISHU_ALLOWED_USERS=ou_xxxxxxxx,ou_yyyyyyyy
WECOM_ALLOWED_USERS=user-id-1,user-id-2
WECOM_CALLBACK_ALLOWED_USERS=user-id-1,user-id-2
TEAMS_ALLOWED_USERS=aad-object-id-1,aad-object-id-2

# Or allow
GATEWAY_ALLOWED_USERS=123456789,987654321

# Or explicitly allow all users (NOT recommended for bots with terminal access):
GATEWAY_ALLOW_ALL_USERS=true
```

### DM Pairing (Alternative to Allowlists)

Instead of manually configuring user IDs, unknown users receive a one-time pairing code when they DM the bot. Email is the exception: unknown email senders are ignored unless email pairing is explicitly enabled.

```bash
# The user sees: "Pairing code: XKGH5N7P"
# You approve them with:
hermes pairing approve telegram XKGH5N7P

# Other pairing commands:
hermes pairing list          # View pending + approved users
hermes pairing revoke telegram 123456789  # Remove access
```

Pairing codes expire after 1 hour, are rate-limited, and use cryptographic randomness.

### Admins vs Regular Users

Allowlists answer "can this person reach the bot at all?" The **admin / user split** answers "now that they're in, what are they allowed to do?"

Every allowed user falls into one of two tiers per scope (DM vs group/channel):

- **Admin** — full access. Can run every registered slash command (built-in + plugin) and use every gated capability.
- **Regular user** — restricted access. Can chat with the agent normally, but can only run the slash commands you explicitly enable. The always-allowed floor is `/help` and `/whoami`.

The tiers are configured per platform and per scope. DM admin status does not imply group/channel admin status — each scope has its own admin list.

**What the tiers gate today:** slash commands. The split runs through the live command registry, so it covers built-ins and plugin-registered commands without per-feature wiring. Plain chat is not affected — non-admins can still talk to the agent.

**What may be gated in the future:** more capability surfaces (tool access, model switching, expensive operations) will hang off the same admin / user distinction as we add them. Configuring the split now means those future restrictions land cleanly without you having to re-model who's an admin.

#### Configuration

```yaml
gateway:
  platforms:
    discord:
      extra:
        allow_from: ["111", "222", "333"]
        allow_admin_from: ["111"]                    # admins → all slash commands
        user_allowed_commands: [status, model]       # what non-admins may run
        # Optional: separate group/channel scope
        group_allow_admin_from: ["111"]
        group_user_allowed_commands: [status]
```

**Backward compat:** if `allow_admin_from` is not set for a scope, the tier split is disabled for that scope and every allowed user has full access. Existing installs keep working with no changes — opt in when you want the distinction.

#### Inspecting your access

Use `/whoami` from any platform to see the active scope, your tier (admin / user / unrestricted), and which slash commands you can run. See the [Telegram](/user-guide/messaging/telegram#slash-command-access-control) and [Discord](/user-guide/messaging/discord#slash-command-access-control) pages for platform-specific examples.

## Interrupting the Agent

Send any message while the agent is working to interrupt it. Key behaviors:

- **In-progress terminal commands are killed immediately** (SIGTERM, then SIGKILL after 1s)
- **Tool calls are cancelled** — only the currently-executing one runs, the rest are skipped
- **Multiple messages are combined** — messages sent during interruption are joined into one prompt
- **`/stop` command** — interrupts without queuing a follow-up message

### Queue vs interrupt vs steer (busy-input mode)

By default, messaging a busy agent interrupts it. Two other modes are available:

- `queue` — follow-up messages wait and run as the next turn after the current task finishes.
- `steer` — follow-up messages are injected into the current run via `/steer`, arriving at the agent after the next tool call. No interrupt, no new turn. Falls back to `queue` behavior if the agent hasn't started yet.

```yaml
display:
  busy_input_mode: steer   # or queue, or interrupt (default)
  busy_ack_enabled: true   # set to false to suppress the ⚡/⏳/⏩ chat reply entirely
```

The first time you message a busy agent on any platform, Hermes appends a one-line reminder to the busy-ack explaining the knob (`"💡 First-time tip — …"`). The reminder fires once per install — a flag under `onboarding.seen.busy_input_prompt` latches it. Delete that key to see the tip again.

If you find the busy-ack noisy — especially with voice input or rapid-fire messages — set `display.busy_ack_enabled: false`. Your input is still queued/steered/interrupts as normal, only the chat reply is silenced.

## Tool Progress Notifications

Control how much tool activity is displayed in `~/.hermes/config.yaml`:

```yaml
display:
  tool_progress: all    # off | new | all | verbose
  tool_progress_command: false  # set to true to enable /verbose in messaging
  # How progress is grouped on platforms that support message editing:
  #   accumulate (default) — edit one bubble in place as tools run
  #   separate             — send one message per tool (pre-v0.9 style; noisier)
  # Only applies where tool_progress is already enabled.
  tool_progress_grouping: accumulate   # accumulate | separate
```

### Message timestamps in model context

Off by default. When enabled, Hermes prepends a human-readable timestamp
(e.g. `[Tue 2026-04-28 13:40:53 CEST]`) onto each **user** message *in the
model's context* so the agent knows when messages were sent — useful for
temporal reasoning ("you asked this morning…", noticing a long gap). It is
**not** added to assistant messages or the system prompt.

```yaml
gateway:
  message_timestamps:
    enabled: false   # set true to show send-times to the model
```

Persisted transcripts always stay clean — the timestamp is stored as message
metadata regardless of this toggle, so enabling it later also surfaces
send-times for past messages, and replay never accumulates duplicate prefixes.

When enabled, the bot sends status messages as it works:

```text
💻 `ls -la`...
🔍 web_search...
📄 web_extract...
🐍 execute_code...
```

## Background Sessions

Run a prompt in a separate background session so the agent works on it independently while your main chat stays responsive:

```
/background Check all servers in the cluster and report any that are down
```

Hermes confirms immediately:

```
🔄 Background task started: "Check all servers in the cluster..."
   Task ID: bg_143022_a1b2c3
```

### How It Works

Each `/background` prompt spawns a **separate agent instance** that runs asynchronously:

- **Isolated session** — the background agent has its own session with its own conversation history. It has no knowledge of your current chat context and receives only the prompt you provide.
- **Same configuration** — inherits your model, provider, toolsets, reasoning settings, and provider routing from the current gateway setup.
- **Non-blocking** — your main chat stays fully interactive. Send messages, run other commands, or start more background tasks while it works.
- **Result delivery** — when the task finishes, the result is sent back to the **same chat or channel** where you issued the command, prefixed with "✅ Background task complete". If it fails, you'll see "❌ Background task failed" with the error.

### Background Process Notifications

When the agent running a background session uses `terminal(background=true)` to start long-running processes (servers, builds, etc.), the gateway can push status updates to your chat. Control this with `display.background_process_notifications` in `~/.hermes/config.yaml`:

```yaml
display:
  background_process_notifications: all    # all | result | error | off
```

| Mode | What you receive |
|------|-----------------|
| `all` | Running-output updates **and** the final completion message (default) |
| `result` | Only the final completion message (regardless of exit code) |
| `error` | Only the final message when the exit code is non-zero |
| `off` | No process watcher messages at all |

You can also set this via environment variable:

```bash
HERMES_BACKGROUND_NOTIFICATIONS=result
```

### Use Cases

- **Server monitoring** — "/background Check the health of all services and alert me if anything is down"
- **Long builds** — "/background Build and deploy the staging environment" while you continue chatting
- **Research tasks** — "/background Research competitor pricing and summarize in a table"
- **File operations** — "/background Organize the photos in ~/Downloads by date into folders"

:::tip
Background tasks on messaging platforms are fire-and-forget — you don't need to wait or check on them. Results arrive in the same chat automatically when the task finishes.
:::

## Service Management

### Linux (systemd)

```bash
hermes gateway install               # Install as user service
hermes gateway start                 # Start the service
hermes gateway stop                  # Stop the service
hermes gateway status                # Check status
journalctl --user -u hermes-gateway -f  # View logs

# Enable lingering (keeps running after logout)
sudo loginctl enable-linger $USER

# Or install a boot-time system service that still runs as your user
sudo hermes gateway install --system
sudo hermes gateway start --system
sudo hermes gateway status --system
journalctl -u hermes-gateway -f
```

Use the user service on laptops and dev boxes. Use the system service on VPS or headless hosts that should come back at boot without relying on systemd linger.

:::danger Don't add a custom `ExecStopPost` kill drop-in
The unit Hermes installs already shuts the gateway down cleanly with `KillMode=mixed` + `KillSignal=SIGTERM`, and uses `Restart=always` with `RestartForceExitStatus` so updates and `/restart` respawn correctly. Do **not** add a systemd drop-in such as `ExecStopPost=/bin/kill -9 $MAINPID` — `ExecStopPost` fires on *every* stop, including clean restarts, so it `SIGKILL`s the freshly spawned instance before it stabilizes and `Restart=always` immediately respawns it. The result is an infinite restart loop (and, on Telegram, a flood of restart messages). If you've added such a drop-in, remove it: `systemctl --user edit hermes-gateway` (or `sudo systemctl edit hermes-gateway` for a system service) and delete the `ExecStopPost` line, then `systemctl --user daemon-reload`.
:::

:::tip Headless VMs: user service + linger avoids root prompts
A system service needs root for every restart — including the automatic gateway restart at the end of `hermes update`. When `hermes update` runs as a non-root user, it tries passwordless `sudo systemctl`; if that's unavailable, it skips the restart and prints the manual `sudo systemctl restart hermes-gateway` command (it never blocks on an interactive password prompt).

For a headless VM you never log into, a **user** service with lingering enabled gives you the same start-at-boot behavior with zero root involvement:

```bash
hermes gateway install          # user service
sudo loginctl enable-linger $USER   # one-time: start at boot, survive logout
```

After that, `hermes update` can restart the gateway without any privileges. If you prefer to keep the system service, either run updates with `sudo hermes update`, or grant the service account passwordless sudo for systemctl, e.g. in `sudo visudo -f /etc/sudoers.d/hermes-gateway`:

```
hermes ALL=(root) NOPASSWD: /usr/bin/systemctl --no-ask-password reset-failed hermes-gateway*, /usr/bin/systemctl --no-ask-password start hermes-gateway*, /usr/bin/systemctl --no-ask-password restart hermes-gateway*
```
:::

Avoid keeping both the user and system gateway units installed at once unless you really mean to. Hermes will warn if it detects both because start/stop/status behavior gets ambiguous.

:::info Multiple installations
If you run multiple Hermes installations on the same machine (with different `HERMES_HOME` directories), each gets its own systemd service name. The default `~/.hermes` uses `hermes-gateway`; other installations use `hermes-gateway-<hash>`. The `hermes gateway` commands automatically target the correct service for your current `HERMES_HOME`.
:::

### macOS (launchd)

```bash
hermes gateway install               # Install as launchd agent
hermes gateway start                 # Start the service
hermes gateway stop                  # Stop the service
hermes gateway status                # Check status
tail -f ~/.hermes/logs/gateway.log   # View logs
```

The generated plist lives at `~/Library/LaunchAgents/ai.hermes.gateway.plist`. It includes three environment variables:

- **PATH** — your full shell PATH at install time, with the venv `bin/` and `node_modules/.bin` prepended. This ensures user-installed tools (Node.js, ffmpeg, etc.) are available to gateway subprocesses like the WhatsApp bridge.
- **VIRTUAL_ENV** — points to the Python virtualenv so tools can resolve packages correctly.
- **HERMES_HOME** — scopes the gateway to your Hermes installation.

:::tip PATH changes after install
launchd plists are static — if you install new tools (e.g. a new Node.js version via nvm, or ffmpeg via Homebrew) after setting up the gateway, run `hermes gateway install` again to capture the updated PATH. The gateway will detect the stale plist and reload automatically.
:::

:::info Multiple installations
Like the Linux systemd service, each `HERMES_HOME` directory gets its own launchd label. The default `~/.hermes` uses `ai.hermes.gateway`; other installations use `ai.hermes.gateway-<suffix>`.
:::

## Platform-Specific Toolsets

Each platform has its own toolset:

| Platform | Toolset | Capabilities |
|----------|---------|--------------|
| CLI | `hermes-cli` | Full access |
| Telegram | `hermes-telegram` | Full tools including terminal |
| Discord | `hermes-discord` | Full tools including terminal |
| WhatsApp | `hermes-whatsapp` | Full tools including terminal |
| WhatsApp Cloud API | `hermes-whatsapp` | Full tools including terminal (shares toolset with the Baileys bridge) |
| Slack | `hermes-slack` | Full tools including terminal |
| Google Chat | `hermes-google_chat` | Full tools including terminal |
| Signal | `hermes-signal` | Full tools including terminal |
| SMS | `hermes-sms` | Full tools including terminal |
| Email | `hermes-email` | Full tools including terminal |
| Home Assistant | `hermes-homeassistant` | Full tools + HA device control (ha_list_entities, ha_get_state, ha_call_service, ha_list_services) |
| Mattermost | `hermes-mattermost` | Full tools including terminal |
| Matrix | `hermes-matrix` | Full tools including terminal |
| DingTalk | `hermes-dingtalk` | Full tools including terminal |
| Feishu/Lark | `hermes-feishu` | Full tools including terminal |
| WeCom | `hermes-wecom` | Full tools including terminal |
| WeCom Callback | `hermes-wecom-callback` | Full tools including terminal |
| Weixin | `hermes-weixin` | Full tools including terminal |
| BlueBubbles | `hermes-bluebubbles` | Full tools including terminal |
| QQBot | `hermes-qqbot` | Full tools including terminal |
| Yuanbao | `hermes-yuanbao` | Full tools including terminal |
| Microsoft Teams | `hermes-teams` | Full tools including terminal |
| API Server | `hermes-api-server` | Full tools (drops `clarify`, `text_to_speech` — programmatic access doesn't have an interactive user) |
| Webhooks | `hermes-webhook` | Full tools including terminal |
| Raft | `hermes-raft` | Wake-only channel; agent uses Raft CLI for message I/O |

## Operating a multi-platform gateway

A gateway typically runs several adapters at once (Telegram + Discord + Slack, etc.). The sections below cover day-2 operations that span all platforms.

### `/platform` command

Once the gateway is running, use the `/platform` slash command from any connected CLI session or chat to inspect and steer individual adapters without restarting the whole gateway:

```
/platform list                  # show all adapters and their state
/platform pause <name>          # stop dispatching new messages to one adapter
/platform resume <name>         # re-enable a paused adapter
```

`/platform list` shows whether each adapter is `running`, `paused` (manually), or `paused-by-breaker` (see below). Pausing keeps the adapter loaded and its background loops alive — incoming messages are dropped on the floor, but the connection itself stays open so resume is instant.

See also the broader status summary command [`/platforms`](../../reference/slash-commands.md#info).

### Automatic circuit breaker

Each adapter is wrapped in a circuit breaker. Repeated retryable failures (network blips, rate-limit replies, 5xx upstream responses, websocket disconnects) cause the breaker to trip — the adapter is auto-paused, an operator notification is sent to the home channel of another live platform when one is configured, and a structured log line is emitted.

The breaker does **not** auto-resume — it stays open until you run `/platform resume <name>` manually. This is intentional: if a platform is in a sustained outage, you don't want the gateway thrashing reconnects.

### Where to look when a platform is paused

When an adapter is paused, check:

1. **Gateway log** (`~/.hermes/logs/gateway.log` or the systemd / launchd unit log). Search for the platform name and `circuit breaker`, `paused`, or `disabled`. The trip event includes the failure count and the last error.
2. **`/platform list`** output — shows the current state and last reason.
3. **The provider's status page** (Telegram bot API status, Discord status, etc.). The breaker tripped because the platform was unhealthy; don't try to resume until it's back.

Once upstream is healthy, `/platform resume <name>` clears the breaker and re-arms the adapter.

### Restart notifications

When the gateway restarts (or is shut down with in-flight sessions), it can send a one-shot "the agent is back" / "the agent was interrupted" message to each platform's home channel. This is controlled per-platform by the `gateway_restart_notification` flag in `gateway-config.yaml`, which defaults to `true`:

```yaml
gateway:
  platforms:
    telegram:
      home_chat_id: "123456789"
      gateway_restart_notification: false   # opt out for this platform
    discord:
      home_chat_id: "987654321"
      # gateway_restart_notification omitted → defaults to true
```

Disable it on noisy or low-priority platforms while leaving it on for your primary chat. The notification is sent once per restart, regardless of how many sessions were in flight.

### Typing indicators

While the agent is processing a message, the gateway shows a live typing status on platforms that support it — a "typing…" bubble on Telegram/Discord/Signal, or the "is thinking…" assistant status on Slack. This is controlled per-platform by the `typing_indicator` flag in `gateway-config.yaml`, which defaults to `true`:

```yaml
gateway:
  platforms:
    slack:
      typing_indicator: false   # don't show "is thinking…" on Slack
    telegram:
      # typing_indicator omitted → defaults to true
```

Set `typing_indicator: false` on any platform where the indicator is unwanted. Some users find Slack's "is thinking…" status noisy (it also briefly disables the compose box while shown, since it uses Slack's Assistant API). Disabling it only suppresses the indicator — message delivery and everything else is unchanged. The flag is generic, so the same key works for every platform.

### Session resume across gateway restarts

When the gateway shuts down with an in-flight tool call or generation, the affected sessions are flagged as `restart_interrupted`. On the next startup, the gateway schedules an auto-resume for each one — the user gets a short heads-up in the chat ("Send any message after restart and I'll try to resume where you left off.") and the session picks up from the last committed turn when they reply.

This behaviour is on by default and is logged at gateway start:

```
Scheduled auto-resume for N restart-interrupted session(s)
```

No configuration is required. If you don't want the heads-up, set `gateway_restart_notification: false` on the platform.

### Mobile-friendly progress defaults

Telegram is usually a mobile inbox, so the defaults are tuned for that surface:

- **`tool_progress`** defaults to **`off`** — no per-tool breadcrumb stream filling up the chat.
- **`busy_ack_detail`** defaults to **`off`** — busy-state acknowledgments and long-running heartbeats stay terse (no `iteration 21/60` debug detail).
- **`interim_assistant_messages`** stays **on** — real mid-turn assistant commentary (the model literally telling you what it's about to do) is signal, not noise.
- **`long_running_notifications`** stays **on** — a single edit-in-place "⏳ Working — N min" bubble updates every few minutes so you have a heartbeat instead of staring at `typing…` for half an hour.

Opt out of either of the kept-on defaults or opt back into verbose progress per platform:

```yaml
display:
  platforms:
    telegram:
      # Re-enable the tool-progress stream
      tool_progress: new
      # Show "iteration N/M, running: tool" in heartbeats and busy acks
      busy_ack_detail: true
      # Or quiet them entirely
      interim_assistant_messages: false
      long_running_notifications: false
```

### Progress bubble cleanup (opt-in)

Tool-progress messages, the "still working…" heartbeat, and status-callback bubbles can also be auto-deleted after the final response lands. Enable per-platform via `display.platforms.<platform>.cleanup_progress`:

```yaml
display:
  platforms:
    telegram:
      cleanup_progress: true
    discord:
      cleanup_progress: true
```

Defaults to `false`. Only platforms whose adapter implements `delete_message` honor the setting (currently Telegram and Discord). Failed runs **skip** cleanup so the bubbles remain as breadcrumbs.

## Next Steps

- [Telegram Setup](telegram.md)
- [Discord Setup](discord.md)
- [Slack Setup](slack.md)
- [Google Chat Setup](google_chat.md)
- [WhatsApp Setup](whatsapp.md)
- [WhatsApp Business Cloud API Setup](whatsapp-cloud.md)
- [Signal Setup](signal.md)
- [SMS Setup (Twilio)](sms.md)
- [Email Setup](email.md)
- [Home Assistant Integration](homeassistant.md)
- [Mattermost Setup](mattermost.md)
- [Matrix Setup](matrix.md)
- [DingTalk Setup](dingtalk.md)
- [Feishu/Lark Setup](feishu.md)
- [WeCom Setup](wecom.md)
- [WeCom Callback Setup](wecom-callback.md)
- [Weixin Setup (WeChat)](weixin.md)
- [BlueBubbles Setup (iMessage)](bluebubbles.md)
- [QQBot Setup](qqbot.md)
- [Yuanbao Setup](yuanbao.md)
- [Microsoft Teams Setup](teams.md)
- [Teams Meetings Pipeline](teams-meetings.md)
- [Open WebUI + API Server](open-webui.md)
- [Raft Setup](raft.md)
- [IRC Setup](irc.md)
- [Webhooks](webhooks.md)

---

# SOURCE: website/docs/user-guide/messaging/telegram.md

---
sidebar_position: 1
title: "Telegram"
description: "Set up Hermes Agent as a Telegram bot"
---

# Telegram Setup

Hermes Agent integrates with Telegram as a full-featured conversational bot. Once connected, you can chat with your agent from any device, send voice memos that get auto-transcribed, receive scheduled task results, and use the agent in group chats. The integration is built on [python-telegram-bot](https://python-telegram-bot.org/) and supports text, voice, images, and file attachments.

## Step 1: Create a Bot via BotFather

Every Telegram bot requires an API token issued by [@BotFather](https://t.me/BotFather), Telegram's official bot management tool.

1. Open Telegram and search for **@BotFather**, or visit [t.me/BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a **display name** (e.g., "Hermes Agent") — this can be anything
4. Choose a **username** — this must be unique and end in `bot` (e.g., `my_hermes_bot`)
5. BotFather replies with your **API token**. It looks like this:

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
Keep your bot token secret. Anyone with this token can control your bot. If it leaks, revoke it immediately via `/revoke` in BotFather.
:::

## Step 2: Customize Your Bot (Optional)

These BotFather commands improve the user experience. Message @BotFather and use:

| Command | Purpose |
|---------|---------|
| `/setdescription` | The "What can this bot do?" text shown before a user starts chatting |
| `/setabouttext` | Short text on the bot's profile page |
| `/setuserpic` | Upload an avatar for your bot |
| `/setcommands` | Define the command menu (the `/` button in chat) |
| `/setprivacy` | Control whether the bot sees all group messages (see Step 3) |

:::tip
For `/setcommands`, a useful starting set:

```
help - Show help information
new - Start a new conversation
sethome - Set this chat as the home channel
```
:::

### Online/Offline status indicator (Optional)

Telegram bots have no real online/offline presence dot — that green dot is a
*user-account* feature, not something the Bot API exposes for bots. The closest
surface is the bot's **short description** (the line shown under its name in the
bot's profile).

Enable `status_indicator` and Hermes sets that short description to **Online**
when the gateway connects and **Offline** on a clean shutdown:

```yaml
gateway:
  platforms:
    telegram:
      extra:
        status_indicator: true
        # Optional custom strings (defaults: "Online" / "Offline"):
        status_online: "🟢 Online"
        status_offline: "🔴 Offline"
```

Notes:

- The short description is **global** to the bot (visible to all users), not
  per-chat. Users see it on the bot's profile page, not as a live badge inside
  an open chat.
- Only a **clean** gateway shutdown (`/stop`, `disconnect`) writes "Offline".
  A hard crash leaves the last-known status — the inherent limitation of a
  profile-text indicator.
- Off by default, since it mutates the bot's global profile.

### Command menu priority and cap (Optional)

Hermes registers its command menu automatically when the Telegram gateway starts. The menu is built from the central slash-command registry plus eligible plugin/skill commands, then capped so Telegram accepts the payload reliably. The default cap is 60 commands — enough to keep all built-in commands plus common skill commands visible.

If you have local or plugin commands that should stay visible in Telegram's `/` picker, prioritize them in `~/.hermes/config.yaml`:

```yaml
platforms:
  telegram:
    extra:
      command_menu:
        max_commands: 60
        priority_mode: prepend  # prepend | append | replace
        priority:
          - my_plugin_command
```

`priority_mode` controls how your list combines with Hermes' built-in priority list:

- `prepend`: put your commands first, then Hermes defaults
- `append`: keep Hermes defaults first, then your commands
- `replace`: use only your list for priority ordering

Telegram allows up to 100 BotCommands, but large command payloads can fail. Hermes defaults to 60 for reliability and clamps configured values to `1..100`; use `/commands` for the full command list.

## Step 3: Privacy Mode (Critical for Groups)

Telegram bots have a **privacy mode** that is **enabled by default**. This is the single most common source of confusion when using bots in groups.

**With privacy mode ON**, your bot can only see:
- Messages that start with a `/` command
- Replies directly to the bot's own messages
- Service messages (member joins/leaves, pinned messages, etc.)
- Messages in channels where the bot is an admin

**With privacy mode OFF**, the bot receives every message in the group.

### How to disable privacy mode

1. Message **@BotFather**
2. Send `/mybots`
3. Select your bot
4. Go to **Bot Settings → Group Privacy → Turn off**

:::warning
**You must remove and re-add the bot to any group** after changing the privacy setting. Telegram caches the privacy state when a bot joins a group, and it will not update until the bot is removed and re-added.
:::

:::tip
An alternative to disabling privacy mode: promote the bot to **group admin**. Admin bots always receive all messages regardless of the privacy setting, and this avoids needing to toggle the global privacy mode.
:::

### Observe group chatter without auto-replying

For OpenClaw/Yuanbao-style group behavior, configure Telegram so the bot can **see** ordinary group messages but only **responds** when directly triggered:

```yaml
telegram:
  allowed_chats:
    - "-1001234567890"
  group_allowed_chats:
    - "-1001234567890"
  require_mention: true
  observe_unmentioned_group_messages: true
```

With this mode enabled, unmentioned group messages from explicitly allowlisted chats/topics are appended to the shared chat/topic session transcript as observed context, but they do not dispatch the agent. `allowed_chats` gates where the bot responds; `group_allowed_chats` authorizes the shared group session used for observed context, so use the same chat IDs for this mode. A later `@botname` mention, reply to the bot, or configured mention pattern in that same allowlisted chat/topic can use that observed context. The triggered message is also tagged with `[nickname|user_id]` and gets a per-turn safety prompt so the model treats prior observed lines as context, not instructions addressed to the bot.

Equivalent environment variable:

```bash
TELEGRAM_ALLOWED_CHATS=-1001234567890
TELEGRAM_GROUP_ALLOWED_CHATS=-1001234567890
TELEGRAM_OBSERVE_UNMENTIONED_GROUP_MESSAGES=true
```

This requires Telegram to deliver ordinary group messages to the gateway, so disable BotFather privacy mode or promote the bot to group admin as described above.

## Step 4: Find Your User ID

Hermes Agent uses numeric Telegram user IDs to control access. Your user ID is **not** your username — it's a number like `123456789`.

**Method 1 (recommended):** Message [@userinfobot](https://t.me/userinfobot) — it instantly replies with your user ID.

**Method 2:** Message [@get_id_bot](https://t.me/get_id_bot) — another reliable option.

Save this number; you'll need it for the next step.

## Step 5: Configure Hermes

### Option A: Interactive Setup (Recommended)

```bash
hermes gateway setup
```

Select **Telegram** when prompted. The wizard asks for your bot token and allowed user IDs, then writes the configuration for you.

### Option B: Manual Configuration

Add the following to `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # Comma-separated for multiple users
```

### Start the Gateway

```bash
hermes gateway
```

The bot should come online within seconds. Send it a message on Telegram to verify.

## Sending Generated Files from Docker-backed Terminals

If your terminal backend is `docker`, keep in mind that Telegram attachments are
sent by the **gateway process**, not from inside the container. That means the
final `MEDIA:/...` path must be readable on the host where the gateway is
running.

Common pitfall:

- the agent writes a file inside Docker to `/workspace/report.txt`
- the model emits `MEDIA:/workspace/report.txt`
- Telegram delivery fails because `/workspace/report.txt` only exists inside the
  container, not on the host

Recommended pattern:

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/.hermes/cache/documents:/output"
```

Then:

- write files inside Docker to `/output/...`
- emit the **host-visible** path in `MEDIA:`, for example:
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`

If you already have a `docker_volumes:` section, add the new mount to the same
list. YAML duplicate keys silently override earlier ones.

### Supported `MEDIA:` file extensions

The gateway extracts `MEDIA:/path/to/file` tags from agent replies and ships the referenced file as a platform-native attachment. Supported extensions across all gateway platforms:

| Category | Extensions |
|---|---|
| Images | `png`, `jpg`, `jpeg`, `gif`, `webp`, `bmp`, `tiff`, `svg` |
| Audio | `mp3`, `wav`, `ogg`, `m4a`, `opus`, `flac`, `aac` |
| Video | `mp4`, `mov`, `webm`, `mkv`, `avi` |
| **Documents** | `pdf`, `txt`, `md`, `csv`, `json`, `xml`, `html`, `yaml`, `yml`, `log` |
| **Office** | `docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp` |
| **Archives** | `zip`, `rar`, `7z`, `tar`, `gz`, `bz2` |
| **Books / packages** | `epub`, `apk`, `ipa` |

Anything on this list delivered as a native attachment on platforms that support it (Telegram, Discord, Signal, Slack, WhatsApp, Feishu, Matrix, etc.); on platforms without native support it falls back to a link or plain-text indicator. The **bold** categories were added in the last few releases — if you were relying on the model saying `here is the file: /path/to/report.docx` instead, swap to `MEDIA:/path/to/report.docx` for native delivery.

## Webhook Mode

By default, Hermes connects to Telegram using **long polling** — the gateway makes outbound requests to Telegram's servers to fetch new updates. This works well for local and always-on deployments.

For **cloud deployments** (Fly.io, Railway, Render, etc.), **webhook mode** is more cost-effective. These platforms can auto-wake suspended machines on inbound HTTP traffic, but not on outbound connections. Since polling is outbound, a polling bot can never sleep. Webhook mode flips the direction — Telegram pushes updates to your bot's HTTPS URL, enabling sleep-when-idle deployments.

| | Polling (default) | Webhook |
|---|---|---|
| Direction | Gateway → Telegram (outbound) | Telegram → Gateway (inbound) |
| Best for | Local, always-on servers | Cloud platforms with auto-wake |
| Setup | No extra config | Set `TELEGRAM_WEBHOOK_URL` |
| Idle cost | Machine must stay running | Machine can sleep between messages |

### Configuration

Add the following to `~/.hermes/.env`:

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
TELEGRAM_WEBHOOK_SECRET="$(openssl rand -hex 32)"  # required
# TELEGRAM_WEBHOOK_PORT=8443        # optional, default 8443
```

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | Yes | Public HTTPS URL where Telegram will send updates. The URL path is auto-extracted (e.g., `/telegram` from the example above). |
| `TELEGRAM_WEBHOOK_SECRET` | **Yes** (when `TELEGRAM_WEBHOOK_URL` is set) | Secret token that Telegram echoes in every webhook request for verification. The gateway refuses to start without it — see [GHSA-3vpc-7q5r-276h](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-3vpc-7q5r-276h). Generate with `openssl rand -hex 32`. |
| `TELEGRAM_WEBHOOK_PORT` | No | Local port the webhook server listens on (default: `8443`). |

When `TELEGRAM_WEBHOOK_URL` is set, the gateway starts an HTTP webhook server instead of polling. When unset, polling mode is used — no behavior change from previous versions.

### Cloud deployment example (Fly.io)

1. Add the env vars to your Fly.io app secrets:

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

2. Expose the webhook port in your `fly.toml`:

```toml
[[services]]
  internal_port = 8443
  protocol = "tcp"

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

3. Deploy:

```bash
fly deploy
```

The gateway log should show: `[telegram] Connected to Telegram (webhook mode)`.

## Proxy Support

If Telegram's API is blocked or you need to route traffic through a proxy, set a Telegram-specific proxy URL. This takes priority over the generic `HTTPS_PROXY` / `HTTP_PROXY` env vars.

**Option 1: config.yaml (recommended)**

```yaml
telegram:
  proxy_url: "socks5://127.0.0.1:1080"
```

**Option 2: environment variable**

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```

Supported schemes: `http://`, `https://`, `socks5://`.

The proxy applies to both the main Telegram connection and the fallback IP transport. If no Telegram-specific proxy is set, the gateway falls back to `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` (or macOS system proxy auto-detection).

## Home Channel

Use the `/sethome` command in any Telegram chat (DM or group) to designate it as the **home channel**. Scheduled tasks (cron jobs) deliver their results to this channel.

You can also set it manually in `~/.hermes/.env`:

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="My Notes"
```

:::tip
Group chat IDs are negative numbers (e.g., `-1001234567890`). Your personal DM chat ID is the same as your user ID.
:::

### Cron deliveries in topic mode

If you have topic mode enabled in your bot DM, cron messages delivered to the root chat land in the system-only lobby — replying there opens no session and you see the "main chat is reserved for system commands" notice. Create a dedicated forum topic (e.g. `Cron`) and set:

```bash
TELEGRAM_CRON_THREAD_ID=<topic_thread_id>
```

`TELEGRAM_CRON_THREAD_ID` overrides `TELEGRAM_HOME_CHANNEL_THREAD_ID` for cron deliveries only. Replies in that topic continue the topic's existing session.

## Voice Messages

### Incoming Voice (Speech-to-Text)

Voice messages you send on Telegram are automatically transcribed by Hermes's configured STT provider and injected as text into the conversation.

- `local` uses `faster-whisper` on the machine running Hermes — no API key required
- `groq` uses Groq Whisper and requires `GROQ_API_KEY`
- `openai` uses OpenAI Whisper and requires `VOICE_TOOLS_OPENAI_KEY`

#### Skipping STT: pass the raw audio file to the agent

If you'd rather have the **agent itself** handle audio — for diarization, a custom transcription tool, or just archiving the recording — set `stt.enabled: false` in `~/.hermes/config.yaml`:

```yaml
stt:
  enabled: false
```

With STT disabled, the gateway still downloads the voice/audio attachment into Hermes's audio cache, but **does not transcribe it**. The agent receives the message with a marker like:

```
[The user sent a voice message: /home/<user>/.hermes/cache/audio/<hash>.ogg]
```

Your tools or skills can then read that path directly (e.g., hand it off to a local diarization pipeline, a richer transcription model, or upload it to long-term storage). The file extension reflects the original format Telegram delivered (`.ogg` for voice notes, `.mp3`/`.m4a`/etc. for audio attachments).

This pairs naturally with the [local Bot API server](#large-files-20mb-via-local-bot-api-server) section below, which lifts Telegram's 20MB getFile ceiling to 2GB — useful when the recordings you want to process are longer than a couple of minutes.

### Outgoing Voice (Text-to-Speech)

When the agent generates audio via TTS, it's delivered as native Telegram **voice bubbles** — the round, inline-playable kind.

- **OpenAI and ElevenLabs** produce Opus natively — no extra setup needed
- **Edge TTS** (the default free provider) outputs MP3 and requires **ffmpeg** to convert to Opus:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

Without ffmpeg, Edge TTS audio is sent as a regular audio file (still playable, but uses the rectangular player instead of a voice bubble).

Configure the TTS provider in your `config.yaml` under the `tts.provider` key.

## Large Files (>20MB) via Local Bot API Server

Telegram's **public** Bot API caps `getFile` downloads at **20 MB**, so any voice note, audio file, video, or document larger than that is silently rejected by Hermes with a "too large" reply. The documented way around this is to run a **local** [telegram-bot-api](https://github.com/tdlib/telegram-bot-api) daemon — the same server software Telegram uses, but running on your network. A local server raises the file ceiling to **2 GB** and Hermes auto-lifts its own internal cap when it sees a custom `base_url` configured.

This unlocks workflows like:

- Sending long voice memos (45-minute meetings, podcasts) to the bot
- Uploading large videos for vision-tool processing
- Archiving raw audio for offline pipelines like diarization, alignment, or training data

### Step 1: Obtain Telegram API credentials

The local server talks directly to Telegram's MTProto layer (not the public Bot API), so it needs **MTProto credentials**:

1. Visit [my.telegram.org/apps](https://my.telegram.org/apps) and sign in with your Telegram account.
2. Create a new application (any name and short description will do).
3. Copy the `api_id` and `api_hash` — both are required.

### Step 2: Run the telegram-bot-api server

The community-maintained [`aiogram/telegram-bot-api`](https://hub.docker.com/r/aiogram/telegram-bot-api) Docker image is the easiest path. A minimal `docker-compose.yaml` (use `--local` mode to enable the higher limits):

```yaml
services:
  tg-bot-api:
    image: aiogram/telegram-bot-api:latest
    container_name: tg-bot-api
    restart: unless-stopped
    ports:
      - "127.0.0.1:8081:8081"   # bind to loopback only; see security note
    environment:
      TELEGRAM_API_ID: "12345"           # your api_id from Step 1
      TELEGRAM_API_HASH: "abcdef..."     # your api_hash from Step 1
      TELEGRAM_LOCAL: "1"                # enable --local mode (raises 20MB → 2GB)
    volumes:
      - ./tg-bot-api-data:/var/lib/telegram-bot-api
```

Bring it up:

```bash
docker compose up -d tg-bot-api
docker logs --tail 20 tg-bot-api
```

:::warning Security
The local Bot API server takes your bot token in the URL path (e.g. `/bot<TOKEN>/getMe`) with **no additional auth**. Anyone who can reach the port can fully control your bot — read every message it can see, send messages as it, etc. Bind the container to `127.0.0.1` and/or front it with a reverse proxy on a private network. **Never expose port 8081 to the public internet.**
:::

### Step 3: Log the bot out of the public API (one-time)

A bot can only be active on **one** Bot API server at a time. If your bot was already running against `api.telegram.org` (which it almost certainly was), you must explicitly log it out there before the local server will accept it:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/logOut"
# expected response: {"ok":true,"result":true}
```

This is a one-shot migration step — you don't repeat it on every restart. Telegram delivers any messages received after `logOut` through the new server instead.

Verify the local server can talk to Telegram on the bot's behalf:

```bash
curl "http://127.0.0.1:8081/bot<YOUR_BOT_TOKEN>/getMe"
# expected response: {"ok":true,"result":{"id":...,"is_bot":true,...}}
```

### Step 4: Point Hermes at the local server

Add the URLs under `platforms.telegram.extra` in `~/.hermes/config.yaml`:

```yaml
platforms:
  telegram:
    extra:
      base_url: "http://127.0.0.1:8081/bot"
      base_file_url: "http://127.0.0.1:8081/file/bot"
      local_mode: true        # see Step 5 below — only set this if the bot's data
                              # directory is readable by the Hermes process
```

:::caution Use `platforms.telegram.extra`, not `telegram.extra`
At the moment only the `platforms.<name>.extra` form is deep-merged into the platform config. Keys placed directly under a top-level `telegram.extra` block are silently dropped.
:::

When `base_url` is set, Hermes:

- Builds the python-telegram-bot client against the local server
- Auto-lifts its internal document/audio size cap from 20 MB → 2 GB
- Reports the active limit in the "too large" error message (`Maximum: 2048 MB.`) so it's obvious which mode you're in

Restart the gateway and look for a confirmation log line:

```bash
hermes gateway restart
grep -E "Using custom Telegram base_url|Using Telegram local_mode" ~/.hermes/logs/gateway.log | tail
```

### Step 5: `local_mode` — file access on disk

The local server has **two ways** to deliver files:

1. **Without `--local`** (the default): files are served over HTTP at `/file/bot<TOKEN>/<path>`, same as the public Bot API. The 20MB ceiling stays in effect. Useful as a network-fix only (e.g. when `api.telegram.org` is unreachable but you can self-host); not what you want for the size lift.
2. **With `--local`** (set via `TELEGRAM_LOCAL=1` above): files are written to the server's filesystem and the `getFile` response returns an **absolute path** instead of an HTTP URL. The 20MB ceiling is lifted. Hermes must then read the bytes **from disk**, not over HTTP.

To make the disk-read path work, set `local_mode: true` in the config above **and** make sure the Hermes process can read the path the server returns. Two scenarios:

- **Same machine** — telegram-bot-api and Hermes run on the same host. Bind-mount the data volume to a directory that Hermes can read (e.g., `/var/lib/telegram-bot-api`), and make sure the file ownership matches. The container drops privileges to its internal `telegram-bot-api` user (uid varies by image); the simplest fix is to add `user: "<UID>:<GID>"` to the compose service so files are owned by a uid Hermes already runs as.
- **Different machines** — the bot server runs on one host (e.g., a NAS, a separate VM) and Hermes on another. The server's data directory must be shared with the Hermes machine at the **same absolute path** the server reports (typically `/var/lib/telegram-bot-api`). NFS works well for this; CIFS/SMB with `uid=` mount remapping is friendlier if you don't want to deal with uid mismatches at the filesystem level.

If `local_mode: true` is set but Hermes can't `stat` the returned file path (permissions or wrong mount), python-telegram-bot silently falls back to an HTTP `getFile` against the local server — which in `--local` mode responds with `404 Not Found`. The symptom shows up in `gateway.log` as:

```
[Telegram] Failed to cache voice: Not Found
telegram.error.InvalidToken: Not Found
```

If you see that, the cap-lift is working but the file-share isn't. Verify `ls -la /var/lib/telegram-bot-api/<TOKEN>/voice/` from the Hermes host as the user the gateway runs as, and confirm a single file is `cat`-able without a permission error.

### Step 6: Test it

Send the bot a voice note or audio file that's bigger than 20 MB. Tail the gateway log:

```bash
tail -f ~/.hermes/logs/gateway.log | grep -iE "telegram|cache"
```

You should see a `[Telegram] Cached user voice at /home/<user>/.hermes/cache/audio/...` line and **no** "too large" rejection. Combined with `stt.enabled: false` (above), the path to the original audio file then lands in the agent's inbound message for downstream processing.

## Group Chat Usage

Hermes Agent works in Telegram group chats with a few considerations:

- **Privacy mode** determines what messages the bot can see (see [Step 3](#step-3-privacy-mode-critical-for-groups))
- `TELEGRAM_ALLOWED_USERS` still applies — only authorized users can trigger the bot, even in groups
- You can keep the bot from responding to ordinary group chatter with `telegram.require_mention: true`
- With `telegram.require_mention: true`, group messages are accepted when they are:
  - replies to one of the bot's messages
  - `@botusername` mentions
  - `/command@botusername` (Telegram's bot-menu command form that includes the bot name)
  - matches for one of your configured regex wake words in `telegram.mention_patterns`
- In groups with multiple Hermes bots, `telegram.exclusive_bot_mentions` keeps routing deterministic. When a message explicitly mentions one or more Telegram bot usernames, only the mentioned bot profiles process it; other Hermes bots ignore it before reply and wake-word fallbacks run. This is enabled by default.
- Use `telegram.ignored_threads` to keep Hermes silent in specific Telegram forum topics, even when the group would otherwise allow free responses or mention-triggered replies
- If `telegram.require_mention` is left unset or false, Hermes keeps the previous open-group behavior and responds to normal group messages it can see

### Multiple Hermes bots in one group

If you run several Hermes profiles in the same Telegram group, create one Telegram bot token per profile and start one gateway per profile. Do not reuse the same bot token in multiple running gateways; Telegram will reject concurrent polling for the same token.

Recommended group config:

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

With this setup, a group message like `@research_bot @ops_bot summarize this` is processed by `research_bot` and `ops_bot` only. Other Hermes bots in the group stay silent, even if the message is a reply to one of their earlier messages or would otherwise match a shared wake word.

Set `exclusive_bot_mentions: false` only for legacy groups where explicit mentions should not override reply and wake-word triggers.

To operate several profiles, run the gateway command once per profile. For example:

```bash
# default profile
hermes gateway start
hermes gateway status
hermes gateway stop

# named profiles
hermes -p research gateway start
hermes -p research gateway status
hermes -p research gateway stop
```

For a small fixed fleet, use a shell loop or script that calls `hermes gateway <action>` for the default profile and `hermes -p <profile> gateway <action>` for each named profile. This is more reliable than assuming a single process-level command controls every named profile on every service manager.

### Troubleshooting: works in DMs but not groups

If the bot responds in a private chat but stays silent in a group, check these
gates in order:

1. **Telegram delivery:** turn off BotFather privacy mode, promote the bot to
   admin, or mention the bot directly. Hermes cannot respond to group messages
   that Telegram never delivers to the bot.
2. **Rejoin after changing privacy:** remove the bot from the group and add it
   again after changing BotFather privacy settings. Telegram may keep the old
   delivery behavior for existing memberships.
3. **Hermes authorization:** make sure the sender is listed in
   `TELEGRAM_ALLOWED_USERS` or `TELEGRAM_GROUP_ALLOWED_USERS`, or allow the
   group chat with `TELEGRAM_GROUP_ALLOWED_CHATS`.
4. **Mention filters:** if `telegram.require_mention: true` is set, normal
   group chatter is ignored unless the message is a slash command, reply to the
   bot, `@botusername` mention, or configured `mention_patterns` match.
5. **Multi-bot routing:** if a group contains several bots, make sure each
   Hermes profile uses a unique bot token and keep `exclusive_bot_mentions`
   enabled unless you intentionally want legacy shared-trigger behavior.

Negative chat IDs are normal for Telegram groups and supergroups. If you use
chat-scoped authorization, put those IDs in `TELEGRAM_GROUP_ALLOWED_CHATS`, not
the sender-user allowlist.

### Example group trigger configuration

Add this to `~/.hermes/config.yaml`:

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns:
    - "^\\s*chompy\\b"
  ignored_threads:
    - 31
    - "42"
```

This example allows all the usual direct triggers plus messages that begin with `chompy`, even if they do not use an `@mention`.
Messages in Telegram topics `31` and `42` are always ignored before the mention and free-response checks run.

### Notes on `mention_patterns`

- Patterns use Python regular expressions
- Matching is case-insensitive
- Patterns are checked against both text messages and media captions
- Invalid regex patterns are ignored with a warning in the gateway logs rather than crashing the bot
- If you want a pattern to match only at the start of a message, anchor it with `^`

## Private Chat Topics (Bot API 9.4)

Telegram Bot API 9.4 (February 2026) introduced **Private Chat Topics** — bots can create forum-style topic threads directly in 1-on-1 DM chats, no supergroup needed. This lets you run multiple isolated workspaces within your existing DM with Hermes.

### Use case

If you work on several long-running projects, topics keep their context separate:

- **Topic "Website"** — work on your production web service
- **Topic "Research"** — literature review and paper exploration
- **Topic "General"** — miscellaneous tasks and quick questions

Each topic gets its own conversation session, history, and context — completely isolated from the others.

### Configuration

:::caution Prerequisites
Before adding topics to your config, the user must **enable Topics mode** in the DM chat with the bot:

1. Open your private chat with the Hermes bot in Telegram
2. Tap the bot's name at the top to open chat info
3. Enable **Topics** (the toggle to turn the chat into a forum)

Without this, Hermes will log `The chat is not a forum` on startup and skip topic creation. This is a Telegram client-side setting — the bot cannot enable it programmatically.
:::

Add topics under `platforms.telegram.extra.dm_topics` in `~/.hermes/config.yaml`:

```yaml
platforms:
  telegram:
    extra:
      dm_topics:
      - chat_id: 123456789        # Your Telegram user ID
        topics:
        - name: General
          icon_color: 7322096
        - name: Website
          icon_color: 9367192
        - name: Research
          icon_color: 16766590
          skill: arxiv              # Auto-load a skill in this topic
```

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Topic display name |
| `icon_color` | No | Telegram icon color code (integer) |
| `icon_custom_emoji_id` | No | Custom emoji ID for the topic icon |
| `skill` | No | Skill to auto-load on new sessions in this topic |
| `thread_id` | No | Auto-populated after topic creation — don't set manually |

### How it works

1. On gateway startup, Hermes calls `createForumTopic` for each topic that doesn't have a `thread_id` yet
2. The `thread_id` is saved back to `config.yaml` automatically — subsequent restarts skip the API call
3. Each topic maps to an isolated session key: `agent:main:telegram:dm:{chat_id}:{thread_id}`
4. Messages in each topic have their own conversation history, memory flush, and context window

### Root DM handling

By default, messages sent to the root DM (outside any topic) are processed
normally. Set `ignore_root_dm: true` to turn the root DM into a lobby — normal
messages are silently ignored for users who have DM topics configured, while
system commands (`/start`, `/help`, `/status`, etc.) still work.

```yaml
platforms:
  telegram:
    extra:
      ignore_root_dm: true
      dm_topics:
        - chat_id: 123456789
          topics:
            - name: General
```

The check is **per-chat**: only users with at least one entry in `dm_topics`
will have their root DM affected. Users without configured topics are
unaffected.

### Skill binding

Topics with a `skill` field automatically load that skill when a new session starts in the topic. This works exactly like typing `/skill-name` at the start of a conversation — the skill content is injected into the first message, and subsequent messages see it in the conversation history.

For example, a topic with `skill: arxiv` will have the arxiv skill pre-loaded whenever its session resets (due to idle timeout, daily reset, or manual `/reset`).

:::tip
Topics created outside of the config (e.g., by manually calling the Telegram API) are discovered automatically when a `forum_topic_created` service message arrives. You can also add topics to the config while the gateway is running — they'll be picked up on the next cache miss.
:::

## Multi-session DM mode (`/topic`)

A ChatGPT-style multi-session DM — one bot, many parallel conversations. Unlike the operator-curated `extra.dm_topics` above, this mode is **user-driven**: no config, no pre-declared topic names. The end user flips it on with `/topic`, then taps the Telegram **+** button to create as many topics as they want, each one a fully independent Hermes session.

### `/topic` subcommands

| Form | Context | Effect |
|------|---------|--------|
| `/topic` | Root DM, not yet enabled | Check BotFather capabilities, enable multi-session mode, create pinned System topic |
| `/topic` | Root DM, already enabled | Show status: unlinked sessions available for restore |
| `/topic` | Inside a topic | Show the current topic's session binding |
| `/topic help` | Any | Inline usage |
| `/topic off` | Root DM | Disable multi-session mode and clear all topic bindings for this chat |
| `/topic <session-id>` | Inside a topic | Restore a previous Telegram session into the current topic |

Only authorized users (allowlist via `TELEGRAM_ALLOWED_USERS` / platform auth config) can run `/topic`. An unauthorized sender gets a refusal instead of activation.

### DM Topics vs Multi-session DM mode

| | `extra.dm_topics` (config-driven) | `/topic` (user-driven) |
|---|---|---|
| Who activates it | Operator, in `config.yaml` | End user, by sending `/topic` |
| Topic list | Fixed set declared in config | User creates/deletes topics freely |
| Topic names | Chosen by operator | Chosen by user; auto-renamed to match Hermes session title |
| Root DM behavior | Normal chat (lobby if `ignore_root_dm: true`) | Becomes a system lobby (non-command messages are rejected) |
| Primary use case | Permanent workspaces with optional skill binding | Ad-hoc parallel sessions |
| Persistence | `extra.dm_topics` in config | `telegram_dm_topic_mode` + `telegram_dm_topic_bindings` SQLite tables |

Both features can coexist on the same bot — you'd run `/topic` from a user's DM, and `extra.dm_topics` continues to manage operator-declared topics for other chats.

### Prerequisites

In **@BotFather**, open your bot → **Bot Settings → Threads Settings**:

1. Turn on **Threaded Mode** (enables `has_topics_enabled`)
2. Do **not** disable users creating topics (keeps `allows_users_to_create_topics` on)

When the user first runs `/topic`, Hermes calls `getMe` to verify both flags. If either is off, Hermes sends a screenshot of the BotFather Threads Settings page and explains what to toggle — no activation happens until prerequisites are met.

### Activation flow

From the root DM, send:

```
/topic
```

Hermes will:

1. Check `getMe().has_topics_enabled` and `allows_users_to_create_topics`
2. If both are true, enable multi-session topic mode for this DM
3. Create and pin a **System** topic for status/commands (best-effort)
4. Reply with a list of previous unlinked Telegram sessions the user can restore

After activation, the **root DM is a lobby**: normal prompts are rejected with guidance pointing at **All Messages**. System commands (`/status`, `/sessions`, `/usage`, `/help`, etc.) still work in the root.

### Creating a new topic (end-user flow)

1. Open the bot DM in Telegram
2. Tap **All Messages** at the top of the bot interface, then send any message
3. Telegram creates a new topic for that message
4. Hermes responds inside that topic — the topic is now a standalone session

Every topic gets its own conversation history, model state, tool execution, and session ID. The isolation key is `agent:main:telegram:dm:{chat_id}:{thread_id}` — identical to the config-driven DM topics isolation.

### Auto-renamed topics

When Hermes generates a session title for a topic (via the auto-title pipeline, after the first exchange), the Telegram topic itself is renamed to match — e.g. "New Topic" becomes "Database migration plan". The rename is best-effort: failures are logged but don't break the session.

To disable this and keep your manually-chosen topic names untouched, set:

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_topic_auto_rename: true
```

When this flag is on, Hermes still generates an internal session title (used by `hermes sessions`, the TUI, etc.) but never edits the Telegram topic name. Useful when you organise topics by hand under BotFather Threaded Mode and don't want every first reply to overwrite the title.

### `/new` inside a topic

Resets the current topic's session (new session ID, fresh history) without touching other topics. Hermes replies with a reminder that for parallel work, creating another topic (via **All Messages**) is usually what you want.

### Restoring a previous session

Inside a topic, send:

```
/topic <session-id>
```

This binds the current topic to an existing Hermes session instead of starting fresh. Useful for continuing a conversation that started before topic mode was enabled. Restrictions:

- The target session must belong to the same Telegram user
- The target session must not already be bound to another topic

Hermes confirms with the session title and replays the last assistant message for context.

To discover session IDs, send `/topic` (no argument) in the root DM — Hermes lists the user's unlinked Telegram sessions.

### `/topic` inside a topic (no argument)

Shows the current topic's binding: session title, session ID, and hints for `/new` vs creating another topic.

### Under the hood

- Activation persists to `telegram_dm_topic_mode(chat_id, user_id, enabled, ...)` in `state.db`
- Each topic binding persists to `telegram_dm_topic_bindings(chat_id, thread_id, session_id, ...)` with `ON DELETE CASCADE` on `session_id` — pruning a session automatically clears its topic binding
- The topic-mode SQLite migration is **opt-in**: it runs on the first `/topic` call, never on gateway startup. Until a user runs `/topic` in this profile, `state.db` is unchanged
- Each inbound DM message looks up its `(chat_id, thread_id)` binding. If present, the lookup routes the message to the bound session via `SessionStore.switch_session()` so the session-key-to-session-id mapping stays consistent on disk
- `/new` inside a topic rewrites the binding row to point at the new session ID, so the next message stays on the fresh session
- Topics declared in `extra.dm_topics` are **never auto-renamed** — the operator-chosen name is preserved even when multi-session mode is enabled
- Set `extra.disable_topic_auto_rename: true` to turn off auto-rename for **all** topics in the chat (ad-hoc topics created via Threaded Mode included)
- The General (pinned top) topic in a forum-enabled DM is treated as the root lobby, regardless of whether Telegram delivers its messages with `message_thread_id=1` or with no thread_id
- Root-lobby reminders are rate-limited to one message per 30 seconds per chat — a user who forgets topic mode is on and types ten prompts in the root won't get ten replies
- BotFather setup screenshots are rate-limited to one send per 5 minutes per chat — repeated `/topic` attempts while Threads Settings are still disabled won't re-upload the same image
- `/background <prompt>` started inside a topic delivers its result back to the same topic; background sessions don't trigger auto-rename of the owning topic
- `/topic` itself is gated by the bot's user authorization check — unauthorized DMs get a refusal instead of activation

### Disabling multi-session mode

Send `/topic off` in the root DM. Hermes flips the row off, clears the chat's `(thread_id → session_id)` bindings, and the root DM reverts to a normal Hermes chat. Existing topics in Telegram aren't deleted — they just stop being gated as independent sessions. Re-run `/topic` later to turn it back on.

If you need to clean up by hand (e.g. a bulk reset across many chats), remove the rows directly:

```bash
sqlite3 ~/.hermes/state.db \
  "UPDATE telegram_dm_topic_mode SET enabled = 0 WHERE chat_id = '<your_chat_id>'; \
   DELETE FROM telegram_dm_topic_bindings WHERE chat_id = '<your_chat_id>';"
```

### Downgrading Hermes

If you downgrade to a Hermes version that predates `/topic`, the feature simply stops working — the `telegram_dm_topic_mode` and `telegram_dm_topic_bindings` tables remain in `state.db` but are ignored by older code. DMs revert to the native per-thread isolation (each `message_thread_id` still gets its own session via `build_session_key`), so your existing Telegram topics keep working as parallel sessions. The root DM is no longer a lobby — messages there go into the agent like they used to. Re-upgrading reactivates multi-session mode exactly where it was.

## Group Forum Topic Skill Binding

Supergroups with **Topics mode** enabled (also called "forum topics") already get session isolation per topic — each `thread_id` maps to its own conversation. But you may want to **auto-load a skill** when messages arrive in a specific group topic, just like DM topic skill binding works.

### Use case

A team supergroup with forum topics for different workstreams:

- **Engineering** topic → auto-loads the `software-development` skill
- **Research** topic → auto-loads the `arxiv` skill
- **General** topic → no skill, general-purpose assistant

### Configuration

Add topic bindings under `platforms.telegram.extra.group_topics` in `~/.hermes/config.yaml`:

```yaml
platforms:
  telegram:
    extra:
      group_topics:
      - chat_id: -1001234567890       # Supergroup ID
        topics:
        - name: Engineering
          thread_id: 5
          skill: software-development
        - name: Research
          thread_id: 12
          skill: arxiv
        - name: General
          thread_id: 1
          # No skill — general purpose
```

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `chat_id` | Yes | The supergroup's numeric ID (negative number starting with `-100`) |
| `name` | No | Human-readable label for the topic (informational only) |
| `thread_id` | Yes | Telegram forum topic ID — visible in `t.me/c/<group_id>/<thread_id>` links |
| `skill` | No | Skill to auto-load on new sessions in this topic |

### How it works

1. When a message arrives in a mapped group topic, Hermes looks up the `chat_id` and `thread_id` in `group_topics` config
2. If a matching entry has a `skill` field, that skill is auto-loaded for the session — identical to DM topic skill binding
3. Topics without a `skill` key get session isolation only (existing behavior, unchanged)
4. Unmapped `thread_id` values or `chat_id` values fall through silently — no error, no skill

### Differences from DM Topics

| | DM Topics | Group Topics |
|---|---|---|
| Config key | `extra.dm_topics` | `extra.group_topics` |
| Topic creation | Hermes creates topics via API if `thread_id` is missing | Admin creates topics in Telegram UI |
| `thread_id` | Auto-populated after creation | Must be set manually |
| `icon_color` / `icon_custom_emoji_id` | Supported | Not applicable (admin controls appearance) |
| Skill binding | ✓ | ✓ |
| Session isolation | ✓ | ✓ (already built-in for forum topics) |

:::tip
To find a topic's `thread_id`, open the topic in Telegram Web or Desktop and look at the URL: `https://t.me/c/1234567890/5` — the last number (`5`) is the `thread_id`. The `chat_id` for supergroups is the group ID prefixed with `-100` (e.g., group `1234567890` becomes `-1001234567890`).
:::

## Recent Bot API Features

- **Bot API 9.4 (Feb 2026):** Private Chat Topics — bots can create forum topics in 1-on-1 DM chats via `createForumTopic`. Hermes uses this for two distinct features: operator-curated [Private Chat Topics](#private-chat-topics-bot-api-94) (config-driven, fixed topic list) and user-driven [Multi-session DM mode](#multi-session-dm-mode-topic) (activated by `/topic`, unlimited user-created topics).
- **Privacy policy:** Telegram now requires bots to have a privacy policy. Set one via BotFather with `/setprivacy_policy`, or Telegram may auto-generate a placeholder. This is particularly important if your bot is public-facing.
- **Bot API 9.5 (Mar 2026): Native streaming via `sendMessageDraft`.** Hermes supports Telegram's native streaming-draft API as an opt-in transport for private chats. The default remains the legacy `editMessageText` path because draft previews can visibly collapse and re-render on some Telegram clients.

### Streaming transport (`gateway.streaming.transport`)

When streaming is enabled (`gateway.streaming.enabled: true`), Hermes picks one of four transports:

| Value | Behaviour |
|---|---|
| `auto` (default) | Native draft streaming on supported chats (currently Telegram DMs); legacy edit-based path otherwise. Falls back gracefully if a draft frame fails. |
| `draft` | Force native drafts. Logs a downgrade and falls back to edit if the chat doesn't support drafts (e.g. groups/topics). |
| `edit` | Legacy progressive `editMessageText` polling for every chat type. |
| `off` | Disable streaming entirely (final reply only, no progressive updates). |

In `~/.hermes/config.yaml`:

```yaml
gateway:
  streaming:
    enabled: true
    transport: auto    # auto | draft | edit | off
```

**What you'll see in DMs with `edit` (default)** — the gateway sends a normal preview message and progressively updates it via `editMessageText`, avoiding Telegram's draft-preview collapse/rollback effect.

**What you'll see in DMs with `auto` or `draft`** — Telegram shows an animated draft preview that updates token-by-token. When the reply finishes, it's delivered as a regular message and the draft preview clears naturally on the client. Drafts have no message id, so the final answer is what stays in your chat history.

**What about groups, supergroups, forum topics?** Telegram restricts `sendMessageDraft` to private chats (DMs). The gateway transparently falls back to the edit-based path for everything else — same UX as before.

**What if a draft frame fails?** Any failure (transient network error, server-side rejection, older python-telegram-bot install) flips that response back to the edit-based path for the rest of the stream. The next response gets a fresh attempt.

## Rendering: Rich Messages, Tables and Link Previews

**Rich Messages (Bot API 10.1).** Final replies that contain constructs the legacy MarkdownV2 path degrades — tables, task lists, collapsible `<details>`, and block math — are sent with Telegram's native [`sendRichMessage`](https://core.telegram.org/bots/api#sendrichmessage) using the agent's **raw markdown**, so they render natively with no client-side flattening. During streaming, the final answer is delivered by **editing the existing preview in place** via `editMessageText`'s `rich_message` parameter — no second message, no delete, so there is no duplicate-delivery flicker at the end of a turn. In DMs the live streaming preview also uses `sendRichMessageDraft`, so the animated draft matches the final rich message. Ordinary replies (plain prose, bold/italic, simple lists) stay on the MarkdownV2 path for consistent font weight and spacing across clients.

The rich path is skipped automatically when content exceeds the 32,768-character rich text limit, and any rejection from Telegram (unsupported endpoint on an older `python-telegram-bot`, parser error, oversized blocks/columns) **transparently falls back** to the MarkdownV2 path — your message is never lost. Transient/network errors are *not* silently re-sent (no duplicate final message).

**MarkdownV2 fallback.** When the rich path is unavailable for a message, Hermes converts markdown to MarkdownV2. Since MarkdownV2 has no native table syntax, pipe tables are normalized:

- **Small tables** are flattened into **row-group bullets** — each row becomes a readable bulleted list under the column headings. Good for 2–4 columns and short cells.
- **Larger or wider tables** fall back to a **fenced code block** with aligned columns so nothing collapses.

Rich messages are **opt-in**. The default stays on the legacy MarkdownV2 path because current Telegram clients can make Bot API rich messages difficult to copy as plain text, which is especially painful for command snippets and mobile handoffs. To enable native rendering for tables/task lists/details/math:

```yaml
gateway:
  platforms:
    telegram:
      extra:
        rich_messages: true
        rich_drafts: false
```

This setting is for client-rendering/copy compatibility; Hermes already falls back automatically when Telegram rejects the rich API call. `rich_drafts` controls the experimental rich draft preview path during Telegram DM streaming and stays off by default because Telegram Desktop/macOS can visually overlay rich draft frames until the chat redraws. If you only want the legacy "always code-block" table behavior while keeping rich messages enabled, disable table normalization by setting `telegram.pretty_tables: false` in `config.yaml` (default: `true`).

**Link previews.** Telegram auto-generates link previews for URLs in bot messages. If you'd rather suppress those (long `/tools` output, agent reply that mentions ten links, etc.):

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_link_previews: true
```

When enabled, Hermes attaches Telegram's `LinkPreviewOptions(is_disabled=True)` to every outgoing message and falls back to the legacy `disable_web_page_preview` parameter on older `python-telegram-bot` versions.

## Group Allowlisting

Telegram groups and forum chats have two orthogonal gates you can configure:

- **Sender user IDs** (`group_allow_from` / `TELEGRAM_GROUP_ALLOWED_USERS`) — sender-scoped allowlist that applies only to group/forum messages. Use this when you want specific users to be able to invoke the bot in groups without adding them to `TELEGRAM_ALLOWED_USERS` (which would also give them DM access).
- **Chat IDs** (`group_allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`) — chat-scoped allowlist. Any member of these groups/forums can interact with the bot. Useful for team/support bots where group membership itself is the access signal.

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # Global access (DMs + groups). Users here can always invoke the bot.
        allow_from:
          - "123456789"
        # Sender IDs allowed in groups/forums only. Does NOT grant DM access.
        group_allow_from:
          - "987654321"
        # Entire groups/forums — any member is authorized.
        group_allowed_chats:
          - "-1001234567890"
```

Equivalent env vars:

```bash
TELEGRAM_ALLOWED_USERS="123456789"
TELEGRAM_GROUP_ALLOWED_USERS="987654321"
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

Behavior:

- `TELEGRAM_ALLOWED_USERS` covers all chat types (DMs, groups, forums).
- `TELEGRAM_GROUP_ALLOWED_USERS` only authorizes the listed senders in groups/forums. They still can't DM the bot unless listed in `TELEGRAM_ALLOWED_USERS`.
- A chat in `TELEGRAM_GROUP_ALLOWED_CHATS` authorizes every member of that chat, regardless of sender.
- Use `*` in any of these to allow any sender/chat.
- This layers on top of existing mention/pattern triggers and on top of `group_topics` + `ignored_threads`.

### Migration from before PR #17686

Prior to this split, `TELEGRAM_GROUP_ALLOWED_USERS` was the only knob and users put **chat IDs** in it. For backward compatibility, chat-ID-shaped values (starting with `-`) in `TELEGRAM_GROUP_ALLOWED_USERS` are still honored as chat IDs and a deprecation warning is logged once. Migration:

```bash
# Old (still works, but deprecated)
TELEGRAM_GROUP_ALLOWED_USERS="-1001234567890"

# New
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

### Guest @mention bypass (`guest_mode`)

In a typical setup, `group_allowed_chats` is a hard gate: messages from groups outside the list are silently dropped, even if a member explicitly @mentions the bot. That's the right default for support / team bots.

For more casual setups — friend group chats where you want the bot **mostly silent** but **occasionally available on explicit ping** — enable `guest_mode`:

```yaml
gateway:
  platforms:
    telegram:
      extra:
        group_allowed_chats:
          - "-1001234567890"   # your main allowlisted group
        guest_mode: true       # non-allowlisted groups: allow on @mention only
```

Env equivalent:

```bash
TELEGRAM_GUEST_MODE=true
```

Default: `false`.

With `guest_mode: true`, a message from a non-allowlisted group is processed **only** if it explicitly @mentions the bot. The mention is required every turn — there's no session stickiness for guest interactions, so the bot never auto-engages in a friend group thread it isn't pinged into.

DMs and allowlisted groups behave exactly as before.

## Slash Command Access Control

By default, every allowed user can run every slash command. To split your allowlist into **admins** (full slash command access) and **regular users** (only commands you explicitly enable), add `allow_admin_from` and `user_allowed_commands` to the platform's `extra` block:

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # Existing allowlists (unchanged)
        allow_from:
          - "123456789"     # admin
          - "555555555"     # regular user
          - "777777777"     # regular user

        # NEW — admins get all slash commands (built-in + plugin)
        allow_admin_from:
          - "123456789"

        # NEW — non-admin allowed users can only run these slash commands.
        # /help and /whoami are always allowed so users can see their access.
        user_allowed_commands:
          - status
          - model
          - history

        # Optional: separate admin/command lists for groups
        group_allow_admin_from:
          - "123456789"
        group_user_allowed_commands:
          - status
```

**Behavior:**

- A user listed in `allow_admin_from` for a scope (DM or group) can run **every** registered slash command — built-in commands AND plugin-registered ones — through the live registry.
- A user in `allow_from` but **not** in `allow_admin_from` can only run commands listed in `user_allowed_commands`, plus the always-allowed floor: `/help` and `/whoami`.
- Plain chat (non-slash messages) is unaffected. Non-admin users can still talk to the agent normally, they just can't trigger arbitrary commands.
- **Backward compat:** if `allow_admin_from` is not set for a scope, slash command gating is disabled for that scope. Existing installs keep working with no changes.
- DM admin status does not imply group admin status. Each scope has its own admin list.
- If only `group_allow_admin_from` is set, DM scope stays in unrestricted (backward-compat) mode.

Use `/whoami` to see the active scope, your tier (admin / user / unrestricted), and which slash commands you can run.

## Interactive Model Picker

When you send `/model` with no arguments in a Telegram chat, Hermes shows an interactive inline keyboard for switching models:

1. **Provider selection** — buttons showing each available provider with model counts (e.g., "OpenAI (15)", "✓ Anthropic (12)" for the current provider).
2. **Model selection** — paginated model list with **Prev**/**Next** navigation, a **Back** button to return to providers, and **Cancel**.

The current model and provider are displayed at the top. All navigation happens by editing the same message in-place (no chat clutter).

:::tip
If you know the exact model name, type `/model <name>` directly to skip the picker. You can also type `/model <name> --global` to persist the change across sessions.
:::

## DNS-over-HTTPS Fallback IPs

In some restricted networks, `api.telegram.org` may resolve to an IP that is unreachable. The Telegram adapter includes a **fallback IP** mechanism that transparently retries connections against alternative IPs while preserving the correct TLS hostname and SNI.

### How it works

1. If `TELEGRAM_FALLBACK_IPS` is set, those IPs are used directly.
2. Otherwise, the adapter automatically queries **Google DNS** and **Cloudflare DNS** via DNS-over-HTTPS (DoH) to discover alternative IPs for `api.telegram.org`.
3. IPs returned by DoH that differ from the system DNS result are used as fallbacks.
4. If DoH is also blocked, a hardcoded seed IP (`149.154.167.220`) is used as a last resort.
5. Once a fallback IP succeeds, it becomes "sticky" — subsequent requests use it directly without retrying the primary path first.

### Configuration

```bash
# Explicit fallback IPs (comma-separated)
TELEGRAM_FALLBACK_IPS=149.154.167.220,149.154.167.221
```

Or in `~/.hermes/config.yaml`:

```yaml
platforms:
  telegram:
    extra:
      fallback_ips:
        - "149.154.167.220"
```

:::tip
You usually don't need to configure this manually. The auto-discovery via DoH handles most restricted-network scenarios. The `TELEGRAM_FALLBACK_IPS` env var is only needed if DoH is also blocked on your network.
:::

## Proxy Support

If your network requires an HTTP proxy to reach the internet (common in corporate environments), the Telegram adapter automatically reads standard proxy environment variables and routes all connections through the proxy.

### Supported variables

The adapter checks these environment variables in order, using the first one that is set:

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy` (lowercase variants)

### Configuration

Set the proxy in your environment before starting the gateway:

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

Or add it to `~/.hermes/.env`:

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

The proxy applies to both the primary transport and all fallback IP transports. No additional Hermes configuration is needed — if the environment variable is set, it's used automatically.

:::note
This covers the custom fallback transport layer that Hermes uses for Telegram connections. The standard `httpx` client used elsewhere already respects proxy env vars natively.
:::

## Message Reactions

The bot can add emoji reactions to messages as visual processing feedback:

- 👀 when the bot starts processing your message
- ✅ when the response is delivered successfully
- ❌ if an error occurs during processing

Reactions are **disabled by default**. Enable them in `config.yaml`:

```yaml
telegram:
  reactions: true
```

Or via environment variable:

```bash
TELEGRAM_REACTIONS=true
```

:::note
Unlike Discord (where reactions are additive), Telegram's Bot API replaces all bot reactions in a single call. The transition from 👀 to ✅/❌ happens atomically — you won't see both at once.
:::

:::tip
If the bot doesn't have permission to add reactions in a group, the reaction calls fail silently and message processing continues normally.
:::

## Per-Channel Prompts

Assign ephemeral system prompts to specific Telegram groups or forum topics. The prompt is injected at runtime on every turn — never persisted to transcript history — so changes take effect immediately.

```yaml
telegram:
  channel_prompts:
    "-1001234567890": |
      You are a research assistant. Focus on academic sources,
      citations, and concise synthesis.
    "42":  |
      This topic is for creative writing feedback. Be warm and
      constructive.
```

Keys are chat IDs (groups/supergroups) or forum topic IDs. For forum groups, topic-level prompts override the group-level prompt:

- Message in topic `42` inside group `-1001234567890` → uses topic `42`'s prompt
- Message in topic `99` (no explicit entry) → falls back to group `-1001234567890`'s prompt
- Message in a group with no entry → no channel prompt applied

Numeric YAML keys are automatically normalized to strings.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot not responding at all | Verify `TELEGRAM_BOT_TOKEN` is correct. Check `hermes gateway` logs for errors. |
| Bot responds with "unauthorized" | Your user ID is not in `TELEGRAM_ALLOWED_USERS`. Double-check with @userinfobot. |
| Bot ignores group messages | Privacy mode is likely on. Disable it (Step 3) or make the bot a group admin. **Remember to remove and re-add the bot after changing privacy.** |
| Voice messages not transcribed | Verify STT is available: install `faster-whisper` for local transcription, or set `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY` in `~/.hermes/.env`. |
| Voice replies are files, not bubbles | Install `ffmpeg` (needed for Edge TTS Opus conversion). |
| Bot token revoked/invalid | Generate a new token via `/revoke` then `/newbot` or `/token` in BotFather. Update your `.env` file. |
| Webhook not receiving updates | Verify `TELEGRAM_WEBHOOK_URL` is publicly reachable (test with `curl`). Ensure your platform/reverse proxy routes inbound HTTPS traffic from the URL's port to the local listen port configured by `TELEGRAM_WEBHOOK_PORT` (they do not need to be the same number). Ensure SSL/TLS is active — Telegram only sends to HTTPS URLs. Check firewall rules. |

## Exec Approval

When the agent tries to run a potentially dangerous command, it asks you for approval in the chat:

> ⚠️ This command is potentially dangerous (recursive delete). Reply "yes" to approve.

Reply "yes"/"y" to approve or "no"/"n" to deny.

## Interactive Prompts (clarify)

When the agent calls the `clarify` tool — to ask which approach you prefer, get post-task feedback, or check before a non-trivial decision — Telegram renders the question with **inline keyboard buttons**:

> ❓ Which framework should I use for the dashboard?
>
> [1. Next.js] [2. Remix] [3. Astro]
> [✏️ Other (type answer)]

Tap a button to answer, or tap **Other** to type a free-form response (the next message you send becomes the answer). Open-ended `clarify` calls (no preset choices) skip the buttons and just capture your next message.

Configure the response timeout via `agent.clarify_timeout` in `~/.hermes/config.yaml` (default `600` seconds). If you don't respond within the timeout, the agent unblocks with a sentinel message and adapts rather than hanging.

## Push notification volume

Telegram fires a push notification on every message the bot sends. For long agent turns that emit tool-progress bubbles, streaming updates, and status callbacks, this gets noisy fast. The Telegram adapter has two notification modes:

| Mode | Behavior |
|------|----------|
| `important` (default) | Only **final responses**, **approval prompts**, and **slash-command confirmations** ring. Tool progress, streaming chunks, and status messages are delivered with `disable_notification=true`. |
| `all` | Every outgoing message fires a push notification. Legacy behavior; opt in if you genuinely want to hear about every tool call. |

Configure in `~/.hermes/config.yaml`:

```yaml
display:
  platforms:
    telegram:
      notifications: important   # or "all"
```

Env override (handy for quick A/B testing):

```bash
HERMES_TELEGRAM_NOTIFICATIONS=all
```

Unknown values log a warning and fall back to `important`.

## Status messages edited in place

The Telegram adapter routes recurring agent status callbacks (e.g. "Compressing context…", "Calling tool…") through `send_or_update_status()`, which keeps a `{(chat_id, status_key) → message_id}` cache and **edits the existing bubble** on subsequent emits instead of appending a new one each time. Distinct `status_key` values get their own messages; distinct chats never collide. If the edit fails (e.g. the user deleted the message, or it's older than Telegram allows for edits), the cache entry is dropped and the next emit posts a fresh message and re-caches its ID. No config required — this is the default Telegram behavior. Other adapters that don't implement `send_or_update_status` fall through to plain `send()` unchanged.

## Pin incoming user message during agent turn

When a user sends a message that triggers an agent turn, the Telegram adapter pins that incoming message for the duration of the turn and unpins it when the response is finished — a lightweight visual indicator that the bot is actively working on the message rather than ignoring it. The pin uses `disable_notification=true` to avoid extra pings. No config required.

## Security

:::warning
Always set `TELEGRAM_ALLOWED_USERS` to restrict who can interact with your bot. Without it, the gateway denies all users by default as a safety measure.
:::

Never share your bot token publicly. If compromised, revoke it immediately via BotFather's `/revoke` command.

For more details, see the [Security documentation](/user-guide/security). You can also use [DM pairing](/user-guide/messaging#dm-pairing-alternative-to-allowlists) for a more dynamic approach to user authorization.

---

# SOURCE: website/docs/user-guide/messaging/discord.md

---
sidebar_position: 3
title: "Discord"
description: "Set up Hermes Agent as a Discord bot"
---

# Discord Setup

Hermes Agent integrates with Discord as a bot, letting you chat with your AI assistant through direct messages or server channels. The bot receives your messages, processes them through the Hermes Agent pipeline (including tool use, memory, and reasoning), and responds in real time. It supports text, voice messages, file attachments, and slash commands.

Before setup, here's the part most people want to know: how Hermes behaves once it's in your server.

## How Hermes Behaves

| Context | Behavior |
|---------|----------|
| **DMs** | Hermes responds to every message. No `@mention` needed. Each DM has its own session. |
| **Server channels** | By default, Hermes only responds when you `@mention` it. If you post in a channel without mentioning it, Hermes ignores the message. |
| **Free-response channels** | You can make specific channels mention-free with `DISCORD_FREE_RESPONSE_CHANNELS`, or disable mentions globally with `DISCORD_REQUIRE_MENTION=false`. Messages in these channels are answered inline — auto-threading is skipped so the channel stays a lightweight chat. |
| **Threads** | Hermes replies in the same thread. Mention rules still apply unless that thread or its parent channel is configured as free-response. Threads stay isolated from the parent channel for session history. |
| **Shared channels with multiple users** | By default, Hermes isolates session history per user inside the channel for safety and clarity. Two people talking in the same channel do not share one transcript unless you explicitly disable that. |
| **Messages mentioning other users** | When `DISCORD_IGNORE_NO_MENTION` is `true` (the default), Hermes stays silent if a message @mentions other users but does **not** mention the bot. This prevents the bot from jumping into conversations directed at other people. Set to `false` if you want the bot to respond to all messages regardless of who is mentioned. This only applies in server channels, not DMs. |

:::tip
If you want a normal bot-help channel where people can talk to Hermes without tagging it every time, add that channel to `DISCORD_FREE_RESPONSE_CHANNELS`.
:::

### Discord Gateway Model

Hermes on Discord is not a webhook that replies statelessly. It runs through the full messaging gateway, which means each incoming message goes through:

1. authorization (`DISCORD_ALLOWED_USERS`)
2. mention / free-response checks
3. session lookup
4. session transcript loading
5. normal Hermes agent execution, including tools, memory, and slash commands
6. response delivery back to Discord

That matters because behavior in a busy server depends on both Discord routing and Hermes session policy.

### Session Model in Discord

By default:

- each DM gets its own session
- each server thread gets its own session namespace
- each user in a shared channel gets their own session inside that channel

So if Alice and Bob both talk to Hermes in `#research`, Hermes treats those as separate conversations by default even though they are using the same visible Discord channel.

This is controlled by `config.yaml`:

```yaml
group_sessions_per_user: true
```

Set it to `false` only if you explicitly want one shared conversation for the entire room:

```yaml
group_sessions_per_user: false
```

Shared sessions can be useful for a collaborative room, but they also mean:

- users share context growth and token costs
- one person's long tool-heavy task can bloat everyone else's context
- one person's in-flight run can interrupt another person's follow-up in the same room

### Interrupts and Concurrency

Hermes tracks running agents by session key.

With the default `group_sessions_per_user: true`:

- Alice interrupting her own in-flight request only affects Alice's session in that channel
- Bob can keep talking in the same channel without inheriting Alice's history or interrupting Alice's run

With `group_sessions_per_user: false`:

- the whole room shares one running-agent slot for that channel/thread
- follow-up messages from different people can interrupt or queue behind each other

This guide walks you through the full setup process — from creating your bot on Discord's Developer Portal to sending your first message.

## Step 1: Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and sign in with your Discord account.
2. Click **New Application** in the top-right corner.
3. Enter a name for your application (e.g., "Hermes Agent") and accept the Developer Terms of Service.
4. Click **Create**.

You'll land on the **General Information** page. Note the **Application ID** — you'll need it later to build the invite URL.

## Step 2: Create the Bot

1. In the left sidebar, click **Bot**.
2. Discord automatically creates a bot user for your application. You'll see the bot's username, which you can customize.
3. Under **Authorization Flow**:
   - Set **Public Bot** to **ON** — required to use the Discord-provided invite link (recommended). This allows the Installation tab to generate a default authorization URL.
   - Leave **Require OAuth2 Code Grant** set to **OFF**.

:::tip
You can set a custom avatar and banner for your bot on this page. This is what users will see in Discord.
:::

:::info[Private Bot Alternative]
If you prefer to keep your bot private (Public Bot = OFF), you **must** use the **Manual URL** method in Step 5 instead of the Installation tab. The Discord-provided link requires Public Bot to be enabled.
:::

## Step 3: Enable Privileged Gateway Intents

This is the most critical step in the entire setup. Without the correct intents enabled, your bot will connect to Discord but **will not be able to read message content**.

On the **Bot** page, scroll down to **Privileged Gateway Intents**. You'll see three toggles:

| Intent | Purpose | Required? |
|--------|---------|-----------| 
| **Presence Intent** | See user online/offline status | Optional |
| **Server Members Intent** | Access the member list, resolve usernames | **Required** |
| **Message Content Intent** | Read the text content of messages | **Required** |

**Enable both Server Members Intent and Message Content Intent** by toggling them **ON**.

- Without **Message Content Intent**, your bot receives message events but the message text is empty — the bot literally cannot see what you typed.
- Without **Server Members Intent**, the bot cannot resolve usernames for the allowed users list and may fail to identify who is messaging it.

:::warning[This is the #1 reason Discord bots don't work]
If your bot is online but never responds to messages, the **Message Content Intent** is almost certainly disabled. Go back to the [Developer Portal](https://discord.com/developers/applications), select your application → Bot → Privileged Gateway Intents, and make sure **Message Content Intent** is toggled ON. Click **Save Changes**.
:::

**Regarding server count:**
- If your bot is in **fewer than 100 servers**, you can simply toggle intents on and off freely.
- If your bot is in **100 or more servers**, Discord requires you to submit a verification application to use privileged intents. For personal use, this is not a concern.

Click **Save Changes** at the bottom of the page.

## Step 4: Get the Bot Token

The bot token is the credential Hermes Agent uses to log in as your bot. Still on the **Bot** page:

1. Under the **Token** section, click **Reset Token**.
2. If you have two-factor authentication enabled on your Discord account, enter your 2FA code.
3. Discord will display your new token. **Copy it immediately.**

:::warning[Token shown only once]
The token is only displayed once. If you lose it, you'll need to reset it and generate a new one. Never share your token publicly or commit it to Git — anyone with this token has full control of your bot.
:::

Store the token somewhere safe (a password manager, for example). You'll need it in Step 8.

## Step 5: Generate the Invite URL

You need an OAuth2 URL to invite the bot to your server. There are two ways to do this:

### Option A: Using the Installation Tab (Recommended)

:::note[Requires Public Bot]
This method requires **Public Bot** to be set to **ON** in Step 2. If you set Public Bot to OFF, use the Manual URL method below instead.
:::

1. In the left sidebar, click **Installation**.
2. Under **Installation Contexts**, enable **Guild Install**.
3. For **Install Link**, select **Discord Provided Link**.
4. Under **Default Install Settings** for Guild Install:
   - **Scopes**: select `bot` and `applications.commands`
   - **Permissions**: select the permissions listed below.

### Option B: Manual URL

You can construct the invite URL directly using this format:

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

Replace `YOUR_APP_ID` with the Application ID from Step 1.

### Required Permissions

These are the minimum permissions your bot needs:

- **View Channels** — see the channels it has access to
- **Send Messages** — respond to your messages
- **Embed Links** — format rich responses
- **Attach Files** — send images, audio, and file outputs
- **Read Message History** — maintain conversation context

### Recommended Additional Permissions

- **Send Messages in Threads** — respond in thread conversations
- **Add Reactions** — react to messages for acknowledgment

### Permission Integers

| Level | Permissions Integer | What's Included |
|-------|-------------------|-----------------|
| Minimal | `117760` | View Channels, Send Messages, Read Message History, Attach Files |
| Recommended | `274878286912` | All of the above plus Embed Links, Send Messages in Threads, Add Reactions |

## Step 6: Invite to Your Server

1. Open the invite URL in your browser (from the Installation tab or the manual URL you constructed).
2. In the **Add to Server** dropdown, select your server.
3. Click **Continue**, then **Authorize**.
4. Complete the CAPTCHA if prompted.

:::info
You need the **Manage Server** permission on the Discord server to invite a bot. If you don't see your server in the dropdown, ask a server admin to use the invite link instead.
:::

After authorizing, the bot will appear in your server's member list (it will show as offline until you start the Hermes gateway).

## Step 7: Find Your Discord User ID

Hermes Agent uses your Discord User ID to control who can interact with the bot. To find it:

1. Open Discord (desktop or web app).
2. Go to **Settings** → **Advanced** → toggle **Developer Mode** to **ON**.
3. Close settings.
4. Right-click your own username (in a message, the member list, or your profile) → **Copy User ID**.

Your User ID is a long number like `284102345871466496`.

:::tip
Developer Mode also lets you copy **Channel IDs** and **Server IDs** the same way — right-click the channel or server name and select Copy ID. You'll need a Channel ID if you want to set a home channel manually.
:::

## Step 8: Configure Hermes Agent

### Option A: Interactive Setup (Recommended)

Run the guided setup command:

```bash
hermes gateway setup
```

Select **Discord** when prompted, then paste your bot token and user ID when asked.

### Option B: Manual Configuration

Add the following to your `~/.hermes/.env` file:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=284102345871466496

# Multiple allowed users (comma-separated)
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543
```

Then start the gateway:

```bash
hermes gateway
```

The bot should come online in Discord within a few seconds. Send it a message — either a DM or in a channel it can see — to test.

:::tip
You can run `hermes gateway` in the background or as a systemd service for persistent operation. See the deployment docs for details.
:::

## Configuration Reference

Discord behavior is controlled through two files: **`~/.hermes/.env`** for credentials and env-level toggles, and **`~/.hermes/config.yaml`** for structured settings. Environment variables always take precedence over config.yaml values when both are set.

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | **Yes** | — | Bot token from the [Discord Developer Portal](https://discord.com/developers/applications). |
| `DISCORD_ALLOWED_USERS` | **Yes** | — | Comma-separated Discord user IDs allowed to interact with the bot. Without this **or** `DISCORD_ALLOWED_ROLES`, the gateway denies all users. |
| `DISCORD_ALLOWED_ROLES` | No | — | Comma-separated Discord role IDs. Any member with one of these roles is authorized — OR semantics with `DISCORD_ALLOWED_USERS`. Auto-enables the **Server Members Intent** on connect. Useful when moderation teams churn: new mods get access as soon as the role is granted, no config push needed. |
| `DISCORD_HOME_CHANNEL` | No | — | Channel ID where the bot sends proactive messages (cron output, reminders, notifications). |
| `DISCORD_HOME_CHANNEL_NAME` | No | `"Home"` | Display name for the home channel in logs and status output. |
| `DISCORD_COMMAND_SYNC_POLICY` | No | `"safe"` | Controls native slash-command startup sync. `"safe"` diffs existing global commands and only updates what changed, recreating commands when Discord metadata changes cannot be applied via patch. `"bulk"` preserves the old `tree.sync()` behavior. `"off"` skips startup sync entirely. |
| `DISCORD_REQUIRE_MENTION` | No | `true` | When `true`, the bot only responds in server channels when `@mentioned`. Set to `false` to respond to all messages in every channel. |
| `DISCORD_THREAD_REQUIRE_MENTION` | No | `false` | When `true`, the in-thread mention shortcut is disabled — threads are gated the same as channels, requiring `@mention` even after the bot has already participated. Use this when multiple bots share a thread and you want each to fire only on explicit `@mention`. |
| `DISCORD_FREE_RESPONSE_CHANNELS` | No | — | Comma-separated channel IDs where the bot responds without requiring an `@mention`, even when `DISCORD_REQUIRE_MENTION` is `true`. |
| `DISCORD_IGNORE_NO_MENTION` | No | `true` | When `true`, the bot stays silent if a message `@mentions` other users but does **not** mention the bot. Prevents the bot from jumping into conversations directed at other people. Only applies in server channels, not DMs. |
| `DISCORD_AUTO_THREAD` | No | `true` | When `true`, automatically creates a new thread for every `@mention` in a text channel, so each conversation is isolated (similar to Slack behavior). Messages already inside threads or DMs are unaffected. |
| `DISCORD_ALLOW_BOTS` | No | `"none"` | Controls how the bot handles messages from other Discord bots. `"none"` — ignore all other bots. `"mentions"` — only accept bot messages that `@mention` Hermes. `"all"` — accept all bot messages. |
| `DISCORD_REACTIONS` | No | `true` | When `true`, the bot adds emoji reactions to messages during processing (👀 when starting, ✅ on success, ❌ on error). Set to `false` to disable reactions entirely. |
| `DISCORD_IGNORED_CHANNELS` | No | — | Comma-separated channel IDs where the bot **never** responds, even when `@mentioned`. Takes priority over all other channel settings. |
| `DISCORD_ALLOWED_CHANNELS` | No | — | Comma-separated channel IDs. When set, the bot **only** responds in these channels (plus DMs if allowed). Overrides `config.yaml` `discord.allowed_channels`. Combine with `DISCORD_IGNORED_CHANNELS` to express allow/deny rules. |
| `DISCORD_NO_THREAD_CHANNELS` | No | — | Comma-separated channel IDs where the bot responds directly in the channel instead of creating a thread. Only relevant when `DISCORD_AUTO_THREAD` is `true`. |
| `DISCORD_HISTORY_BACKFILL` | No | `true` | When `true`, prepend recent channel scrollback (since the bot's last response) to the user message when the bot is mentioned. Recovers context the bot would otherwise miss with `require_mention`. Skipped in DMs and free-response channels. Set to `false` to disable. |
| `DISCORD_HISTORY_BACKFILL_LIMIT` | No | `50` | Maximum number of messages to scan backwards when assembling the backfill block. In practice the scan usually stops earlier — at the bot's own last message in the channel. |
| `DISCORD_REPLY_TO_MODE` | No | `"first"` | Controls reply-reference behavior: `"off"` — never reply to the original message, `"first"` — reply-reference on the first message chunk only (default), `"all"` — reply-reference on every chunk. |
| `DISCORD_ALLOW_MENTION_EVERYONE` | No | `false` | When `false` (default), the bot cannot ping `@everyone` or `@here` even if its response contains those tokens. Set to `true` to opt back in. See [Mention Control](#mention-control) below. |
| `DISCORD_ALLOW_MENTION_ROLES` | No | `false` | When `false` (default), the bot cannot ping `@role` mentions. Set to `true` to allow. |
| `DISCORD_ALLOW_MENTION_USERS` | No | `true` | When `true` (default), the bot can ping individual users by ID. |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | No | `true` | When `true` (default), replying to a message pings the original author. |
| `DISCORD_PROXY` | No | — | Proxy URL for Discord connections (HTTP, WebSocket, REST). Overrides `HTTPS_PROXY`/`ALL_PROXY`. Supports `http://`, `https://`, and `socks5://` schemes. |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | No | `false` | When `true`, the bot accepts attachments of any file type (not just the built-in PDF/text/zip/office allowlist). Unknown types are cached to disk and surfaced to the agent as a local path with `application/octet-stream` MIME so it can inspect them with `terminal` / `read_file` / `ffprobe` / etc. |
| `DISCORD_MAX_ATTACHMENT_BYTES` | No | `33554432` | Maximum bytes per attachment the gateway will download and cache. Default 32 MiB. Set to `0` for no cap (attachments are held in memory while being written, so unlimited carries a real memory cost). |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | No | `0.6` | Grace window the adapter waits before flushing a queued text chunk. Useful for smoothing streamed output. |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | No | `2.0` | Delay between split chunks when a single message exceeds Discord's length limit. |

:::warning Bot-to-bot conversation is not supported
`DISCORD_ALLOW_BOTS` exists to accept input from a specific trusted bot (e.g. a relay or webhook bot), not to let two Hermes profiles talk to each other. The default, `"none"`, ignores all other bots and is the safe setting.

Wiring multiple Hermes profiles to reply to one another in a shared channel — by setting `"mentions"` or `"all"` across several profiles — is an unsupported topology. Discord auto-`@mentions` the replied-to author on every reply, so under `"mentions"` two bots will satisfy each other's mention gate indefinitely and ack-loop. There is no circuit breaker for this because the supported configuration is simply to leave `DISCORD_ALLOW_BOTS` at `"none"`. If you must accept a particular bot, scope the acceptance narrowly and never to another auto-replying agent.
:::

### Config File (`config.yaml`)

The `discord` section in `~/.hermes/config.yaml` mirrors the env vars above. Config.yaml settings are applied as defaults — if the equivalent env var is already set, the env var wins.

```yaml
# Discord-specific settings
discord:
  require_mention: true           # Require @mention in server channels
  thread_require_mention: false   # If true, require @mention in threads too (multi-bot threads)
  free_response_channels: ""      # Comma-separated channel IDs (or YAML list)
  auto_thread: true               # Auto-create threads on @mention
  reactions: true                 # Add emoji reactions during processing
  ignored_channels: []            # Channel IDs where bot never responds
  no_thread_channels: []          # Channel IDs where bot responds without threading
  history_backfill: true          # Prepend recent channel scrollback on mention (default: true)
  history_backfill_limit: 50      # Max messages to scan backwards (default: 50)
  channel_prompts: {}             # Per-channel ephemeral system prompts
  allow_mentions:                 # What the bot is allowed to ping (safe defaults)
    everyone: false               # @everyone / @here pings (default: false)
    roles: false                  # @role pings (default: false)
    users: true                   # @user pings (default: true)
    replied_user: true            # reply-reference pings the author (default: true)

# Session isolation (applies to all gateway platforms, not just Discord)
group_sessions_per_user: true     # Isolate sessions per user in shared channels
```

#### `discord.require_mention`

**Type:** boolean — **Default:** `true`

When enabled, the bot only responds in server channels when directly `@mentioned`. DMs always get a response regardless of this setting.

#### `discord.thread_require_mention`

**Type:** boolean — **Default:** `false`

By default, once the bot has participated in a thread (auto-created on `@mention` or replied in once), it keeps responding to every subsequent message in that thread without needing to be `@mentioned` again. That's the right default for one-on-one conversations.

In **multi-bot threads** where users address one bot per turn, this default becomes a footgun — every other bot in the thread also fires on every message, burning credits and spamming the channel. Set `thread_require_mention: true` to disable the in-thread shortcut and gate threads the same way channels are gated. Explicit `@mentions` still work as before.

```yaml
discord:
  require_mention: true
  thread_require_mention: true    # multi-bot setup
```

#### `discord.free_response_channels`

**Type:** string or list — **Default:** `""`

Channel IDs where the bot responds to all messages without needing an `@mention`. Accepts either a comma-separated string or a YAML list:

```yaml
# String format
discord:
  free_response_channels: "1234567890,9876543210"

# List format
discord:
  free_response_channels:
    - 1234567890
    - 9876543210
```

If a thread's parent channel is in this list, the thread also becomes mention-free.

Free-response channels also **skip auto-threading** — the bot replies inline rather than spinning off a new thread per message. This keeps the channel usable as a lightweight chat surface. If you want threading behavior, don't list the channel as free-response (use normal `@mention` flow instead).

#### `discord.auto_thread`

**Type:** boolean — **Default:** `true`

When enabled, every `@mention` in a regular text channel automatically creates a new thread for the conversation. This keeps the main channel clean and gives each conversation its own isolated session history. Once a thread is created, subsequent messages in that thread don't require `@mention` — the bot knows it's already participating. Set [`thread_require_mention`](#discordthread_require_mention) to `true` to disable this in-thread shortcut for multi-bot setups.

Messages sent in existing threads or DMs are unaffected by this setting. Channels listed in `discord.free_response_channels` or `discord.no_thread_channels` also bypass auto-threading and get inline replies instead.

#### `discord.reactions`

**Type:** boolean — **Default:** `true`

Controls whether the bot adds emoji reactions to messages as visual feedback:
- 👀 added when the bot starts processing your message
- ✅ added when the response is delivered successfully
- ❌ added if an error occurs during processing

Disable this if you find the reactions distracting or if the bot's role doesn't have the **Add Reactions** permission.

#### `discord.ignored_channels`

**Type:** string or list — **Default:** `[]`

Channel IDs where the bot **never** responds, even when directly `@mentioned`. This takes the highest priority — if a channel is in this list, the bot silently ignores all messages there, regardless of `require_mention`, `free_response_channels`, or any other setting.

```yaml
# String format
discord:
  ignored_channels: "1234567890,9876543210"

# List format
discord:
  ignored_channels:
    - 1234567890
    - 9876543210
```

If a thread's parent channel is in this list, messages in that thread are also ignored.

#### `discord.no_thread_channels`

**Type:** string or list — **Default:** `[]`

Channel IDs where the bot responds directly in the channel instead of auto-creating a thread. This only has an effect when `auto_thread` is `true` (the default). In these channels, the bot responds inline like a normal message rather than spawning a new thread.

```yaml
discord:
  no_thread_channels:
    - 1234567890  # Bot responds inline here
```

Useful for channels dedicated to bot interaction where threads would add unnecessary noise.

#### `discord.channel_prompts`

**Type:** mapping — **Default:** `{}`

Per-channel ephemeral system prompts that are injected on every turn in the matching Discord channel or thread without being persisted to transcript history.

```yaml
discord:
  channel_prompts:
    "1234567890": |
      This channel is for research tasks. Prefer deep comparisons,
      citations, and concise synthesis.
    "9876543210": |
      This forum is for therapy-style support. Be warm, grounded,
      and non-judgmental.
```

Behavior:
- Exact thread/channel ID matches win.
- If a message arrives inside a thread or forum post and that thread has no explicit entry, Hermes falls back to the parent channel/forum ID.
- Prompts are applied ephemerally at runtime, so changing them affects future turns immediately without rewriting past session history.

#### `discord.history_backfill`

**Type:** boolean — **Default:** `true`

When enabled, the bot recovers missed channel messages on each `@mention`. With `require_mention: true`, the bot only processes messages that tag it directly — everything else in the channel is invisible to the session transcript. History backfill scans backwards through recent channel history when triggered, collecting messages between the bot's last response and the current mention, and includes them as context.

Behavior by surface:

- **Server channels** (with `require_mention: true`): backfill scans the channel since the bot's last response. Useful when other participants posted while the bot wasn't addressed.
- **Threads**: backfill scans the thread only — Discord's `channel.history()` on a thread returns only that thread's messages, not the parent channel. This is the right scope because threads are usually self-contained conversations.
- **DMs**: skipped. Every DM message triggers the bot, so the session transcript is already complete — there's no mention gap to fill.
- **Free-response channels** and **bot's own auto-created threads**: skipped for the same reason — no mention gating means no gap.

Per-user sessions (`group_sessions_per_user: true`, the default) also benefit: a user's session is missing the context posted by other channel participants and the user's own messages from before they tagged the bot. Backfill fills both gaps.

```yaml
discord:
  history_backfill: true   # default
```

To turn it off:

```yaml
discord:
  history_backfill: false
```

> **Note:** Messages that arrive *while* the bot is processing (between a trigger and its response) are not captured. This is an accepted simplification — the user can re-send or tag again.

#### `discord.history_backfill_limit`

**Type:** integer — **Default:** `50`

Maximum number of messages to scan backwards when recovering channel context. In practice the scan usually stops much earlier — at the bot's own last message in the channel, which is the natural boundary between turns. This limit is a safety cap for cold starts and long gaps where no prior bot message exists in recent history.

```yaml
discord:
  history_backfill: true
  history_backfill_limit: 50
```

#### `group_sessions_per_user`

**Type:** boolean — **Default:** `true`

This is a global gateway setting (not Discord-specific) that controls whether users in the same channel get isolated session histories.

When `true`: Alice and Bob talking in `#research` each have their own separate conversation with Hermes. When `false`: the entire channel shares one conversation transcript and one running-agent slot.

```yaml
group_sessions_per_user: true
```

See the [Session Model](#session-model-in-discord) section above for the full implications of each mode.

#### `display.tool_progress`

**Type:** string — **Default:** `"all"` — **Values:** `off`, `new`, `all`, `verbose`

Controls whether the bot sends progress messages in the chat while processing (e.g., "Reading file...", "Running terminal command..."). This is a global gateway setting that applies to all platforms.

```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — no progress messages
- `new` — only show the first tool call per turn
- `all` — show all tool calls (truncated to 40 characters in gateway messages)
- `verbose` — show full tool call details (can produce long messages)

#### `display.tool_progress_command`

**Type:** boolean — **Default:** `false`

When enabled, makes the `/verbose` slash command available in the gateway, letting you cycle through tool progress modes (`off → new → all → verbose → off`) without editing config.yaml.

```yaml
display:
  tool_progress_command: true
```

## Slash Command Access Control

By default, every allowed user can run every slash command. To split your allowlist into **admins** (full slash command access) and **regular users** (only commands you explicitly enable), add `allow_admin_from` and `user_allowed_commands` to the Discord platform's `extra` block:

```yaml
gateway:
  platforms:
    discord:
      extra:
        # Existing user allowlist (unchanged)
        allow_from:
          - "123456789012345678"  # admin user ID
          - "999888777666555444"  # regular user ID

        # NEW — admins get all slash commands (built-in + plugin)
        allow_admin_from:
          - "123456789012345678"

        # NEW — non-admin allowed users can only run these slash commands.
        # /help and /whoami are always allowed so users can see their access.
        user_allowed_commands:
          - status
          - model
          - history

        # Optional: separate admin / command lists for server channels
        group_allow_admin_from:
          - "123456789012345678"
        group_user_allowed_commands:
          - status
```

**Behavior:**

- A user in `allow_admin_from` for a scope (DM or server channel) can run **every** registered slash command — built-in AND plugin-registered — through the live command registry.
- A user not in `allow_admin_from` can only run commands listed in `user_allowed_commands`, plus the always-allowed floor: `/help` and `/whoami`.
- Plain chat (non-slash messages) is unaffected. Non-admin users can still talk to the agent normally; they just can't trigger arbitrary commands.
- **Backward compat:** if `allow_admin_from` is not set for a scope, slash command gating is disabled for that scope. Existing installs keep working with no changes.
- DM admin status does not imply server-channel admin status. Each scope has its own admin list.

Use `/whoami` to see the active scope, your tier (admin / user / unrestricted), and which slash commands you can run.

## Interactive Model Picker

Send `/model` with no arguments in a Discord channel to open a dropdown-based model picker:

1. **Provider selection** — a Select dropdown showing available providers (up to 25).
2. **Model selection** — a second dropdown with models for the chosen provider (up to 25).

The picker times out after 120 seconds. Only authorized users (those in `DISCORD_ALLOWED_USERS`) can interact with it. If you know the model name, type `/model <name>` directly.

## Native Slash Commands for Skills

Hermes automatically registers installed skills as **native Discord Application Commands**. This means skills appear in Discord's autocomplete `/` menu alongside built-in commands.

- Each skill becomes a Discord slash command (e.g., `/code-review`, `/ascii-art`)
- Skills accept an optional `args` string parameter
- Discord has a limit of 100 application commands per bot — if you have more skills than available slots, extra skills are skipped with a warning in the logs
- Skills are registered during bot startup alongside built-in commands like `/model`, `/reset`, and `/background`

No extra configuration is needed — any skill installed via `hermes skills install` is automatically registered as a Discord slash command on the next gateway restart.

### Disabling Slash Command Registration

If you run multiple Hermes gateways against the same Discord application (e.g. staging + production), only one of them should own the global slash-command registration — otherwise the last startup wins and the registrations flap. Turn slash registration off on the "follower" gateway:

```yaml
gateway:
  platforms:
    discord:
      extra:
        slash_commands: false   # default: true
```

Leaving this at `true` on the "primary" gateway keeps the normal behavior — global `/`-menu commands for built-ins and installed skills.

## Sending Media (inline `MEDIA:` tags)

The Discord adapter supports native file uploads for every common media type via inline `MEDIA:/path/to/file` tags emitted in the agent's response — the adapter strips the tag and auto-uploads the file:

| Type | How it's delivered |
|---|---|
| Images (PNG/JPG/WebP) | Native Discord image attachment with inline preview |
| Animated GIFs | `send_animation` uploads as `animation.gif` so Discord plays it inline (not as a static thumbnail) |
| Video (MP4/MOV) | `send_video` — native video player |
| Audio / Voice | `send_voice` — native voice message when possible, file attachment otherwise |
| Documents (PDF/ZIP/docx/etc.) | `send_document` — native attachment with download button |

Discord's per-upload size limit depends on the server's boost tier (25 MB free, up to 500 MB). If Hermes gets an HTTP 413, the adapter falls back to a link pointing at the local cache path rather than failing silently.

## Receiving Arbitrary File Types

Any file type a user uploads is accepted. Authorization to message the agent is the gate — not the file extension. Every upload is downloaded, cached under `~/.hermes/cache/documents/`, and surfaced to the agent as a `DOCUMENT`-typed message event so it can inspect the file with `terminal` (`ffprobe`, `unzip`, `file`, `strings`, etc.) or `read_file`.

- Known types (PDF, docx/xlsx/pptx, zip, images/audio/video, etc.) keep their precise MIME.
- Unknown types fall back to the upload's reported content type, or `application/octet-stream` when none is given.
- Small UTF-8-decodable files (text, code, config, HTML, CSS, JSON, YAML, ...) have their contents auto-injected into the prompt up to 100 KiB. Binary files that can't be decoded are surfaced as a path-pointing context note only (auto-translated for Docker/Modal sandboxed terminals via `to_agent_visible_cache_path`), so they don't blow up the context window.

The only inbound limit is the per-file size cap (default 32 MiB):

```yaml
discord:
  # Optional — raise/disable the per-file size cap. Default is 32 MiB.
  # The whole file is held in memory while being cached, so unlimited
  # uploads carry a real memory cost.
  max_attachment_bytes: 33554432   # bytes; 0 = unlimited
```

Equivalent env var: `DISCORD_MAX_ATTACHMENT_BYTES=33554432` (or `0` for no cap).

The legacy `discord.allow_any_attachment` flag is now a no-op — any file type is always accepted — and is kept only so existing configs don't error.

:::warning Memory cost of unlimited
Disabling the size cap (`max_attachment_bytes: 0`) means a user can drop a multi-GB file on the bot and the gateway will dutifully buffer it through memory while caching to disk. Only set this in trusted single-user installs. For shared bots, keep the default 32 MiB or raise it conservatively.
:::

## Interactive Prompts (clarify)

When the agent calls the `clarify` tool — to ask which approach you prefer, get post-task feedback, or check before a non-trivial decision — Discord renders the question with **one button per choice**:

> Which framework should I use for the dashboard?
>
> [1. Next.js] [2. Remix] [3. Astro] [Other (type answer)]

Click a numbered button to answer, or click **Other** to type a free-form response (the next message you send in that channel becomes the answer). Open-ended `clarify` calls (no preset choices) skip the buttons and just capture your next message.

The buttons disable themselves once a choice is made so duplicate clicks don't double-resolve the prompt. Configure the response timeout via `agent.clarify_timeout` in `~/.hermes/config.yaml` (default `600` seconds). If you don't respond within the timeout, the agent unblocks with a sentinel message and adapts rather than hanging.

## Home Channel

You can designate a "home channel" where the bot sends proactive messages (such as cron job output, reminders, and notifications). There are two ways to set it:

### Using the Slash Command

Type `/sethome` in any Discord channel where the bot is present. That channel becomes the home channel.

### Manual Configuration

Add these to your `~/.hermes/.env`:

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

Replace the ID with the actual channel ID (right-click → Copy Channel ID with Developer Mode on).

## Voice Messages

Hermes Agent supports Discord voice messages:

- **Incoming voice messages** are automatically transcribed using the configured STT provider: local `faster-whisper` (no key), Groq Whisper (`GROQ_API_KEY`), or OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`).
- **Text-to-speech**: Use `/voice tts` to have the bot send spoken audio responses alongside text replies.
- **Discord voice channels**: Hermes can also join a voice channel, listen to users speaking, and talk back in the channel.

For the full setup and operational guide, see:
- [Voice Mode](/user-guide/features/voice-mode)
- [Use Voice Mode with Hermes](/guides/use-voice-mode-with-hermes)

### Voice Channel Audio Effects (ambient + verbal acks)

When the bot is in a voice channel, you can give it a more conversational feel: a short verbal acknowledgement ("let me look into that") before it starts working, and a subtle ambient "thinking" bed that plays underneath while tools run — the speech ducks the ambient down and swells it back when finished, similar to Grok voice mode.

discord.py plays only one audio stream per connection, so Hermes installs a software mixer on the outgoing stream that sums an ambient loop, acknowledgements, and TTS replies into that single stream — they overlap instead of cutting each other off.

This is **off by default**. Enable it in `config.yaml`:

```yaml
discord:
  voice_fx:
    enabled: true          # master switch
    ambient_enabled: true  # idle "thinking" bed while tools run
    ambient_path: ""       # custom loop file (any audio format); "" = built-in synthesised pad
    ambient_gain: 0.18     # idle bed loudness (0.0–1.0)
    duck_gain: 0.06        # ambient loudness while the bot is speaking
    speech_gain: 1.0       # TTS / acknowledgement loudness
    ack_enabled: true      # speak a short phrase before the first tool call of a turn
    ack_phrases:           # picked at random; set to [] to disable the spoken ack
      - "Let me look into that."
      - "One moment."
      - "Checking on that now."
```

Notes:
- The acknowledgement fires at most once per turn, only when the bot is in a voice channel and the mixer is active. It uses your configured TTS provider.
- `ambient_path` accepts any file `ffmpeg` can decode; it's looped seamlessly. Leave it empty to use the built-in synthesised pad (no asset needed).
- All settings live in `config.yaml` (not `.env`) — they're behavioral, not secrets.
- When `voice_fx.enabled` is `false`, voice playback uses the original one-shot path and nothing changes.


## Forum Channels

Discord forum channels (type 15) don't accept direct messages — every post in a forum must be a thread. Hermes auto-detects forum channels and creates a new thread post whenever it needs to send there, so text replies, TTS, images, voice messages, and file attachments all work without special handling from the agent.

- **Thread name** is derived from the first line of the message (markdown heading prefix stripped, capped at 100 chars). When the message is attachment-only, the filename is used as the fallback thread name.
- **Attachments** ride along on the starter message of the new thread — no separate upload step, no partial sends.
- **One call, one thread**: each forum send creates a new thread. Successive sends to the same forum will therefore produce separate threads.
- **Detection is three-layered**: the channel directory cache first, a process-local probe cache second, and a live `GET /channels/{id}` probe as a last resort (whose result is then memoized for the life of the process).

Refreshing the directory (`/channels refresh` on platforms that expose it, or a gateway restart) populates the cache with any forum channels created after the bot started.

## Troubleshooting

### Bot is online but not responding to messages

**Cause**: Message Content Intent is disabled.

**Fix**: Go to [Developer Portal](https://discord.com/developers/applications) → your app → Bot → Privileged Gateway Intents → enable **Message Content Intent** → Save Changes. Restart the gateway.

### "Disallowed Intents" error on startup

**Cause**: Your code requests intents that aren't enabled in the Developer Portal.

**Fix**: Enable all three Privileged Gateway Intents (Presence, Server Members, Message Content) in the Bot settings, then restart.

### Bot can't see messages in a specific channel

**Cause**: The bot's role doesn't have permission to view that channel.

**Fix**: In Discord, go to the channel's settings → Permissions → add the bot's role with **View Channel** and **Read Message History** enabled.

### 403 Forbidden errors

**Cause**: The bot is missing required permissions.

**Fix**: Re-invite the bot with the correct permissions using the URL from Step 5, or manually adjust the bot's role permissions in Server Settings → Roles.

### Bot is offline

**Cause**: The Hermes gateway isn't running, or the token is incorrect.

**Fix**: Check that `hermes gateway` is running. Verify `DISCORD_BOT_TOKEN` in your `.env` file. If you recently reset the token, update it.

### "User not allowed" / Bot ignores you

**Cause**: Your User ID isn't in `DISCORD_ALLOWED_USERS`.

**Fix**: Add your User ID to `DISCORD_ALLOWED_USERS` in `~/.hermes/.env` and restart the gateway.

### People in the same channel are sharing context unexpectedly

**Cause**: `group_sessions_per_user` is disabled, or the platform cannot provide a user ID for the messages in that context.

**Fix**: Set this in `~/.hermes/config.yaml` and restart the gateway:

```yaml
group_sessions_per_user: true
```

If you intentionally want a shared room conversation, leave it off — just expect shared transcript history and shared interrupt behavior.

## Security

:::warning
Always set `DISCORD_ALLOWED_USERS` (or `DISCORD_ALLOWED_ROLES`) to restrict who can interact with the bot. Without either, the gateway denies all users by default as a safety measure. Only authorize people you trust — authorized users have full access to the agent's capabilities, including tool use and system access.
:::

### Role-Based Access Control

For servers where access is managed by roles instead of individual user lists (moderator teams, support staff, internal tooling), use `DISCORD_ALLOWED_ROLES` — a comma-separated list of role IDs. Any member with one of those roles is authorized.

```bash
# ~/.hermes/.env — works alongside or instead of DISCORD_ALLOWED_USERS
DISCORD_ALLOWED_ROLES=987654321098765432,876543210987654321
```

Semantics:

- **OR with user allowlist.** A user is authorized if their ID is in `DISCORD_ALLOWED_USERS` **or** they have any role in `DISCORD_ALLOWED_ROLES`.
- **Server Members Intent auto-enabled.** When `DISCORD_ALLOWED_ROLES` is set, the bot enables the Members intent on connect — required for Discord to send role information with member records.
- **Role IDs, not names.** Grab them from Discord: **User Settings → Advanced → Developer Mode ON**, then right-click any role → **Copy Role ID**.
- **DM fallback.** In DMs the role check scans mutual guilds; a user with an allowed role in any shared server is authorized in DMs too.

This is the preferred pattern when the moderation team churns — new moderators get access the moment the role is granted, with no `.env` edit or gateway restart.

### Mention Control

By default, Hermes blocks the bot from pinging `@everyone`, `@here`, and role mentions, even if its reply contains those tokens. This prevents a poorly-worded prompt or echoed user content from spamming a whole server. Individual `@user` pings and reply-reference pings (the little "replying to…" chip) stay enabled so normal conversation still works.

You can relax these defaults via either env vars or `config.yaml`:

```yaml
# ~/.hermes/config.yaml
discord:
  allow_mentions:
    everyone: false      # allow the bot to ping @everyone / @here
    roles: false         # allow the bot to ping @role mentions
    users: true          # allow the bot to ping individual @users
    replied_user: true   # ping the author when replying to their message
```

```bash
# ~/.hermes/.env — env vars win over config.yaml
DISCORD_ALLOW_MENTION_EVERYONE=false
DISCORD_ALLOW_MENTION_ROLES=false
DISCORD_ALLOW_MENTION_USERS=true
DISCORD_ALLOW_MENTION_REPLIED_USER=true
```

:::tip
Leave `everyone` and `roles` at `false` unless you know exactly why you need them. It is very easy for an LLM to produce the string `@everyone` inside a normal-looking response; without this protection, that would notify every member of your server.
:::

For more information on securing your Hermes Agent deployment, see the [Security Guide](../security.md).



---

# SOURCE: website/docs/user-guide/messaging/slack.md

---
sidebar_position: 4
title: "Slack"
description: "Set up Hermes Agent as a Slack bot using Socket Mode"
---

# Slack Setup

Connect Hermes Agent to Slack as a bot using Socket Mode. Socket Mode uses WebSockets instead of
public HTTP endpoints, so your Hermes instance doesn't need to be publicly accessible — it works
behind firewalls, on your laptop, or on a private server.

:::warning Classic Slack Apps Deprecated
Classic Slack apps (using RTM API) were **fully deprecated in March 2025**. Hermes uses the modern
Bolt SDK with Socket Mode. If you have an old classic app, you must create a new one following
the steps below.
:::

## Overview

| Component | Value |
|-----------|-------|
| **Library** | `slack-bolt` / `slack_sdk` for Python (Socket Mode) |
| **Connection** | WebSocket — no public URL required |
| **Auth tokens needed** | Bot Token (`xoxb-`) + App-Level Token (`xapp-`) |
| **User identification** | Slack Member IDs (e.g., `U01ABC2DEF3`) |

---

## Step 1: Create a Slack App

The fastest path is to paste a manifest Hermes generates for you. It
declares every built-in slash command (`/btw`, `/stop`, `/model`, …),
every required OAuth scope, every event subscription, and enables Socket
Mode — all at once.

### Option A: From a Hermes-generated manifest (recommended)

1. Generate the manifest:
   ```bash
   hermes slack manifest --write
   ```
   This writes `~/.hermes/slack-manifest.json` and prints paste-in
   instructions.
2. Go to [https://api.slack.com/apps](https://api.slack.com/apps) →
   **Create New App** → **From an app manifest**
3. Pick your workspace, paste the JSON contents, review, click **Next**
   → **Create**
4. Skip ahead to **Step 6: Install App to Workspace**. The manifest
   handled scopes, events, and slash commands for you.

### Option B: From scratch (manual)

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App**
3. Choose **From scratch**
4. Enter an app name (e.g., "Hermes Agent") and select your workspace
5. Click **Create App**

You'll land on the app's **Basic Information** page. Continue with
Steps 2–6 below.

---

## Step 2: Configure Bot Token Scopes

Navigate to **Features → OAuth & Permissions** in the sidebar. Scroll to **Scopes → Bot Token Scopes** and add the following:

| Scope | Purpose |
|-------|---------|
| `chat:write` | Send messages as the bot |
| `app_mentions:read` | Detect when @mentioned in channels |
| `channels:history` | Read messages in public channels the bot is in |
| `channels:read` | List and get info about public channels |
| `groups:history` | Read messages in private channels the bot is invited to |
| `im:history` | Read direct message history |
| `im:read` | View basic DM info |
| `im:write` | Open and manage DMs |
| `mpim:history` | Read group direct message (multi-person DM) history |
| `mpim:read` | View basic group DM info |
| `users:read` | Look up user information |
| `files:read` | Read and download attached files, including voice notes/audio |
| `files:write` | Upload files (images, audio, documents) |

:::caution Missing scopes = missing features
Without `channels:history` and `groups:history`, the bot **will not receive messages in channels** —
it will only work in DMs. Without `files:read`, Hermes can chat but **cannot reliably read user-uploaded attachments**.
These are the most commonly missed scopes.
:::

**Optional scopes:**

| Scope | Purpose |
|-------|---------|
| `groups:read` | List and get info about private channels |

---

## Step 3: Enable Socket Mode

Socket Mode lets the bot connect via WebSocket instead of requiring a public URL.

1. In the sidebar, go to **Settings → Socket Mode**
2. Toggle **Enable Socket Mode** to ON
3. You'll be prompted to create an **App-Level Token**:
   - Name it something like `hermes-socket` (the name doesn't matter)
   - Add the **`connections:write`** scope
   - Click **Generate**
4. **Copy the token** — it starts with `xapp-`. This is your `SLACK_APP_TOKEN`

:::tip
You can always find or regenerate app-level tokens under **Settings → Basic Information → App-Level Tokens**.
:::

---

## Step 4: Subscribe to Events

This step is critical — it controls what messages the bot can see.


1. In the sidebar, go to **Features → Event Subscriptions**
2. Toggle **Enable Events** to ON
3. Expand **Subscribe to bot events** and add:

| Event | Required? | Purpose |
|-------|-----------|---------|
| `message.im` | **Yes** | Bot receives direct messages |
| `message.mpim` | **Yes** | Bot receives messages in **group DMs** (multi-person DMs) it's added to |
| `message.channels` | **Yes** | Bot receives messages in **public** channels it's added to |
| `message.groups` | **Recommended** | Bot receives messages in **private** channels it's invited to |
| `app_mention` | **Yes** | Prevents Bolt SDK errors when bot is @mentioned |

4. Click **Save Changes** at the bottom of the page

:::danger Missing event subscriptions is the #1 setup issue
If the bot works in DMs but **not in channels**, you almost certainly forgot to add
`message.channels` (for public channels) and/or `message.groups` (for private channels).
Without these events, Slack simply never delivers channel messages to the bot.
:::


---

## Step 5: Enable the Messages Tab

This step enables direct messages to the bot. Without it, users see **"Sending messages to this app has been turned off"** when trying to DM the bot.

1. In the sidebar, go to **Features → App Home**
2. Scroll to **Show Tabs**
3. Toggle **Messages Tab** to ON
4. Check **"Allow users to send Slash commands and messages from the messages tab"**

:::danger Without this step, DMs are completely blocked
Even with all the correct scopes and event subscriptions, Slack will not allow users to send direct messages to the bot unless the Messages Tab is enabled. This is a Slack platform requirement, not a Hermes configuration issue.
:::

---

## Step 6: Install App to Workspace

1. In the sidebar, go to **Settings → Install App**
2. Click **Install to Workspace**
3. Review the permissions and click **Allow**
4. After authorization, you'll see a **Bot User OAuth Token** starting with `xoxb-`
5. **Copy this token** — this is your `SLACK_BOT_TOKEN`

:::tip
If you change scopes or event subscriptions later, you **must reinstall the app** for the changes
to take effect. The Install App page will show a banner prompting you to do so.
:::

---

## Step 7: Find User IDs for the Allowlist

Hermes uses Slack **Member IDs** (not usernames or display names) for the allowlist.

To find a Member ID:

1. In Slack, click on the user's name or avatar
2. Click **View full profile**
3. Click the **⋮** (more) button
4. Select **Copy member ID**

Member IDs look like `U01ABC2DEF3`. You need your own Member ID at minimum.

---

## Step 8: Configure Hermes

Add the following to your `~/.hermes/.env` file:

```bash
# Required
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ALLOWED_USERS=U01ABC2DEF3              # Comma-separated Member IDs

# Optional
SLACK_HOME_CHANNEL=C01234567890              # Default channel for cron/scheduled messages
SLACK_HOME_CHANNEL_NAME=general              # Human-readable name for the home channel (optional)
```

Or run the interactive setup:

```bash
hermes gateway setup    # Select Slack when prompted
```

Then start the gateway:

```bash
hermes gateway              # Foreground
hermes gateway install      # Install as a user service
sudo hermes gateway install --system   # Linux only: boot-time system service
```

---

## Step 9: Invite the Bot to Channels

After starting the gateway, you need to **invite the bot** to any channel where you want it to respond:

```
/invite @Hermes Agent
```

The bot will **not** automatically join channels. You must invite it to each channel individually.

---

## Slash Commands

Every Hermes command (`/btw`, `/stop`, `/new`, `/model`, `/help`, ...)
is a native Slack slash command — exactly the way they work on Telegram
and Discord. Type `/` in Slack and the autocomplete picker lists every
Hermes command with its description.

Under the hood: Hermes ships with a generated Slack app manifest (see
Step 1, Option A) that declares every command in
[`COMMAND_REGISTRY`](https://github.com/NousResearch/hermes-agent/blob/main/hermes_cli/commands.py)
as a slash command. In Socket Mode, Slack routes the command event
through the WebSocket regardless of the manifest's `url` field.

### Refreshing slash commands after updates

When Hermes adds new commands (e.g. after `hermes update`), regenerate
the manifest and update your Slack app:

```bash
hermes slack manifest --write
```

Then in Slack:
1. Open [https://api.slack.com/apps](https://api.slack.com/apps) →
   your Hermes app
2. **Features → App Manifest → Edit**
3. Paste the new contents of `~/.hermes/slack-manifest.json`
4. **Save**. Slack will prompt to reinstall the app if scopes or slash
   commands changed.

### Legacy `/hermes <subcommand>` still works

For backward compatibility with older manifests, you can still type
`/hermes btw run the tests` — Hermes routes it the same way as `/btw
run the tests`. Free-form questions also work: `/hermes what's the
weather?` is treated as a regular message.

### Using commands inside threads (the `!cmd` prefix)

Slack itself blocks native slash commands inside thread replies — try
`/queue` in a thread and Slack responds with *"/queue is not supported
in threads. Sorry!"* There is no app-side setting that re-enables them;
Slack never delivers them to Hermes.

As a workaround, Hermes recognises a leading `!` as an alternate
command prefix that works in threads (and anywhere else). Type
`!queue`, `!stop`, `!model gpt-5.4`, etc. as a regular thread reply —
Hermes treats it identically to the slash form and replies in the same
thread.

Only the first token is checked against the known command list, so
casual messages like `!nice work` pass through to the agent unchanged.

Approval prompts (dangerous command / `execute_code` approval) normally
render as interactive buttons. When buttons can't be delivered and
Hermes falls back to a text prompt, the prompt instructs you to reply
with `!approve` / `!deny` — the form that works inside threads.

### Advanced: emit only the slash-commands array

If you maintain your Slack manifest by hand and just want the slash
command list:

```bash
hermes slack manifest --slashes-only > /tmp/slashes.json
```

Paste that array into the `features.slash_commands` key of your
existing manifest.

---

## How the Bot Responds

Understanding how Hermes behaves in different contexts:

| Context | Behavior |
|---------|----------|
| **DMs** | Bot responds to every message — no @mention needed |
| **Channels** | Bot **only responds when @mentioned** (e.g., `@Hermes Agent what time is it?`). In channels, Hermes replies in a thread attached to that message. |
| **Threads** | If you @mention Hermes inside an existing thread, it replies in that same thread. Once the bot has an active session in a thread, **subsequent replies in that thread do not require @mention** — the bot follows the conversation naturally. |

:::tip
In channels, always @mention the bot to start a conversation. Once the bot is active in a thread, you can reply in that thread without mentioning it. Outside of threads, messages without @mention are ignored to prevent noise in busy channels.
:::

---

## Configuration Options

Beyond the required environment variables from Step 8, you can customize Slack bot behavior through `~/.hermes/config.yaml`.

### Thread & Reply Behavior

```yaml
platforms:
  slack:
    # Controls how multi-part responses are threaded
    # "off"   — never thread replies to the original message
    # "first" — first chunk threads to user's message (default)
    # "all"   — all chunks thread to user's message
    reply_to_mode: "first"

    extra:
      # Whether to reply in a thread (default: true).
      # When false, channel messages get direct channel replies instead
      # of threads. Messages inside existing threads still reply in-thread.
      reply_in_thread: true

      # Also post thread replies to the main channel
      # (Slack's "Also send to channel" feature).
      # Only the first chunk of the first reply is broadcast.
      reply_broadcast: false
```

| Key | Default | Description |
|-----|---------|-------------|
| `platforms.slack.reply_to_mode` | `"first"` | Threading mode for multi-part messages: `"off"`, `"first"`, or `"all"` |
| `platforms.slack.extra.reply_in_thread` | `true` | When `false`, channel messages get direct replies instead of threads. Messages inside existing threads still reply in-thread. |
| `platforms.slack.extra.reply_broadcast` | `false` | When `true`, thread replies are also posted to the main channel. Only the first chunk is broadcast. |

### Session Isolation

```yaml
# Global setting — applies to Slack and all other platforms
group_sessions_per_user: true
```

When `true` (the default), each user in a shared channel gets their own isolated conversation session. Two people talking to Hermes in `#general` will have separate histories and contexts.

Set to `false` if you want a collaborative mode where the entire channel shares one conversation session. Be aware this means users share context growth and token costs, and one user's `/reset` clears the session for everyone.

### Mention & Trigger Behavior

```yaml
slack:
  # Require @mention in channels (this is the default behavior;
  # the Slack adapter enforces @mention gating in channels regardless,
  # but you can set this explicitly for consistency with other platforms)
  require_mention: true

  # Prevent thread auto-engagement: only reply to channel messages that
  # contain an explicit @mention. With this OFF (default), Slack can
  # "auto-engage" — remembering past mentions in a thread and following
  # up on bot-message replies, and resuming active sessions without a
  # fresh mention. With strict_mention ON, every new channel message
  # must @mention the bot before Hermes will respond.
  strict_mention: false

  # Custom mention patterns that trigger the bot
  # (in addition to the default @mention detection)
  mention_patterns:
    - "hey hermes"
    - "hermes,"

  # Text prepended to every outgoing message
  reply_prefix: ""
```

:::tip When to use `strict_mention`
Set this to `true` in busy workspaces where Slack's default "the bot remembers this thread" behavior surprises users — for example, a long tech-support thread where the bot helped at the start and you'd rather it stay silent unless explicitly pinged again. DMs and active interactive sessions are unaffected.
:::

:::info
Slack supports both patterns: `@mention` required to start a conversation by default, but you can opt specific channels out via `SLACK_FREE_RESPONSE_CHANNELS` (comma-separated channel IDs) or `slack.free_response_channels` in `config.yaml`. Once the bot has an active session in a thread, subsequent thread replies do not require a mention. In DMs the bot always responds without needing a mention.
:::

### Channel allowlist (`allowed_channels`)

Restrict the bot to a fixed set of Slack channels — useful when the bot is invited to many channels but should only respond in a few. When set, messages from channels NOT in this list are **silently ignored**, even if the bot is `@mentioned`.

**DMs are exempt** from this filter, so authorized users can always reach the bot in a direct message.

```yaml
slack:
  allowed_channels:
    - "C0123456789"   # #ops
    - "C0987654321"   # #incident-response
```

Or via env var (comma-separated):

```bash
SLACK_ALLOWED_CHANNELS="C0123456789,C0987654321"
```

Behavior:

- Empty / unset → no restriction (fully backward compatible).
- Non-empty → channel ID must be on the list, or the message is dropped before any other gating (mention requirement, `free_response_channels`, etc.) runs.
- Slack channel IDs start with `C` (public), `G` (private), or `D` (DM). Look them up via the Slack UI's "Open channel details" → "About" panel, or via the API.

See also: [admin/user slash command split](../../reference/slash-commands.md#permissions-and-adminuser-split).

### Unauthorized User Handling

```yaml
slack:
  # What happens when an unauthorized user (not in SLACK_ALLOWED_USERS) DMs the bot
  # "pair"   — prompt them for a pairing code (default)
  # "ignore" — silently drop the message
  unauthorized_dm_behavior: "pair"
```

You can also set this globally for all platforms:

```yaml
unauthorized_dm_behavior: "pair"
```

The platform-specific setting under `slack:` takes precedence over the global setting.

### Voice Transcription

```yaml
# Global setting — enable/disable automatic transcription of incoming voice messages
stt_enabled: true
```

When `true` (the default), incoming audio messages are automatically transcribed using the configured STT provider before being processed by the agent.

### Full Example

```yaml
# Global gateway settings
group_sessions_per_user: true
unauthorized_dm_behavior: "pair"
stt_enabled: true

# Slack-specific settings
slack:
  require_mention: true
  unauthorized_dm_behavior: "pair"

# Platform config
platforms:
  slack:
    reply_to_mode: "first"
    extra:
      reply_in_thread: true
      reply_broadcast: false
```

---


## Home Channel

Set `SLACK_HOME_CHANNEL` to a channel ID where Hermes will deliver scheduled messages,
cron job results, and other proactive notifications. To find a channel ID:

1. Right-click the channel name in Slack
2. Click **View channel details**
3. Scroll to the bottom — the Channel ID is shown there

```bash
SLACK_HOME_CHANNEL=C01234567890
```

Make sure the bot has been **invited to the channel** (`/invite @Hermes Agent`).

---

## Multi-Workspace Support

Hermes can connect to **multiple Slack workspaces** simultaneously using a single gateway instance. Each workspace is authenticated independently with its own bot user ID.

### Configuration

Provide multiple bot tokens as a **comma-separated list** in `SLACK_BOT_TOKEN`:

```bash
# Multiple bot tokens — one per workspace
SLACK_BOT_TOKEN=xoxb-workspace1-token,xoxb-workspace2-token,xoxb-workspace3-token

# A single app-level token is still used for Socket Mode
SLACK_APP_TOKEN=xapp-your-app-token
```

Or in `~/.hermes/config.yaml`:

```yaml
platforms:
  slack:
    token: "xoxb-workspace1-token,xoxb-workspace2-token"
```

### OAuth Token File

In addition to tokens in the environment or config, Hermes also loads tokens from an **OAuth token file** at:

```
~/.hermes/slack_tokens.json
```

This file is a JSON object mapping team IDs to token entries:

```json
{
  "T01ABC2DEF3": {
    "token": "xoxb-workspace-token-here",
    "team_name": "My Workspace"
  }
}
```

Tokens from this file are merged with any tokens specified via `SLACK_BOT_TOKEN`. Duplicate tokens are automatically deduplicated.

### How it works

- The **first token** in the list is the primary token, used for the Socket Mode connection (AsyncApp).
- Each token is authenticated via `auth.test` on startup. The gateway maps each `team_id` to its own `WebClient` and `bot_user_id`.
- When a message arrives, Hermes uses the correct workspace-specific client to respond.
- The primary `bot_user_id` (from the first token) is used for backward compatibility with features that expect a single bot identity.

---

## Voice Messages

Hermes supports voice on Slack:

- **Incoming:** Voice/audio messages are automatically transcribed using the configured STT provider: local `faster-whisper`, Groq Whisper (`GROQ_API_KEY`), or OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`)
- **Outgoing:** TTS responses are sent as audio file attachments

---

## Per-Channel Prompts

Assign ephemeral system prompts to specific Slack channels. The prompt is injected at runtime on every turn — never persisted to transcript history — so changes take effect immediately.

```yaml
slack:
  channel_prompts:
    "C01RESEARCH": |
      You are a research assistant. Focus on academic sources,
      citations, and concise synthesis.
    "C02ENGINEERING": |
      Code review mode. Be precise about edge cases and
      performance implications.
```

Keys are Slack channel IDs (find them via channel details → "About" → scroll to bottom). All messages in the matching channel get the prompt injected as an ephemeral system instruction.

## Per-Channel Skill Bindings

Auto-load a skill whenever a new session starts in a specific channel or DM. Unlike per-channel prompts (which are injected on every turn), skill bindings inject the skill content as a user message at **session start** — it becomes part of the conversation history and does not need to be reloaded on subsequent turns.

This is ideal for DMs or channels with a dedicated purpose (flashcards, a domain-specific Q&A bot, a support triage channel, etc.) where you don't want the model's own skill selector to decide whether to load on every short reply.

```yaml
slack:
  channel_skill_bindings:
    # DM channel — always runs in "german-flashcards" mode
    - id: "D0ATH9TQ0G6"
      skills:
        - german-flashcards
    # Research channel — preload multiple skills in order
    - id: "C01RESEARCH"
      skills:
        - arxiv
        - writing-plans
    # Short form: single skill as a string
    - id: "C02SUPPORT"
      skill: hubspot-on-demand
```

Notes:
- The binding matches by channel ID. For threaded messages in a bound channel, the thread inherits the parent channel's binding.
- The skill is loaded only at session start (new session or after auto-reset). If you change the binding, run `/new` or wait for the session to auto-reset for it to take effect.
- Combine with `channel_prompts` for per-channel tone/constraints on top of the skill's instructions.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot doesn't respond to DMs | Verify `message.im` is in your event subscriptions and the app is reinstalled |
| Bot works in DMs but not in channels | **Most common issue.** Add `message.channels` and `message.groups` to event subscriptions, reinstall the app, and invite the bot to the channel with `/invite @Hermes Agent` |
| Bot doesn't respond to @mentions in channels | 1) Check `message.channels` event is subscribed. 2) Bot must be invited to the channel. 3) Ensure `channels:history` scope is added. 4) Reinstall the app after scope/event changes |
| Bot ignores messages in private channels | Add both the `message.groups` event subscription and `groups:history` scope, then reinstall the app and `/invite` the bot |
| Bot doesn't respond in group DMs (multi-person DMs) | Add the `message.mpim` event subscription and the `mpim:history` scope (plus `mpim:read`), then **reinstall** the app. Without `message.mpim`, Slack never delivers group-DM messages to the bot — even though 1:1 DMs work. |
| "Sending messages to this app has been turned off" in DMs | Enable the **Messages Tab** in App Home settings (see Step 5) |
| "not_authed" or "invalid_auth" errors | Regenerate your Bot Token and App Token, update `.env` |
| Bot responds but can't post in a channel | Invite the bot to the channel with `/invite @Hermes Agent` |
| Bot can chat but can't read uploaded images/files | Add `files:read`, then **reinstall** the app. Hermes now surfaces attachment access diagnostics in-chat when Slack returns scope/auth/permission failures. |
| `missing_scope` error | Add the required scope in OAuth & Permissions, then **reinstall** the app |
| Socket disconnects frequently | Check your network; Bolt auto-reconnects but unstable connections cause lag |
| Changed scopes/events but nothing changed | You **must reinstall** the app to your workspace after any scope or event subscription change |

### Quick Checklist

If the bot isn't working in channels, verify **all** of the following:

1. ✅ `message.channels` event is subscribed (for public channels)
2. ✅ `message.groups` event is subscribed (for private channels)
3. ✅ `app_mention` event is subscribed
4. ✅ `channels:history` scope is added (for public channels)
5. ✅ `groups:history` scope is added (for private channels)
6. ✅ App was **reinstalled** after adding scopes/events
7. ✅ Bot was **invited** to the channel (`/invite @Hermes Agent`)
8. ✅ You are **@mentioning** the bot in your message

---

## Security

:::warning
**Always set `SLACK_ALLOWED_USERS`** with the Member IDs of authorized users. Without this setting,
the gateway will **deny all messages** by default as a safety measure. Never share your bot tokens —
treat them like passwords.
:::

- Tokens should be stored in `~/.hermes/.env` (file permissions `600`)
- Rotate tokens periodically via the Slack app settings
- Audit who has access to your Hermes config directory
- Socket Mode means no public endpoint is exposed — one less attack surface

---

# SOURCE: website/docs/user-guide/messaging/whatsapp.md

---
sidebar_position: 5
title: "WhatsApp"
description: "Set up Hermes Agent as a WhatsApp bot via the built-in Baileys bridge"
---

# WhatsApp Setup

Hermes connects to WhatsApp through a built-in bridge based on **Baileys**. This works by emulating a WhatsApp Web session — **not** through the official WhatsApp Business API. No Meta developer account or Business verification is required.

> Run `hermes gateway setup` and pick **WhatsApp** for a guided walk-through.

:::tip Two WhatsApp integrations
This page is for the **Baileys bridge** — quick to set up, personal accounts, no public URL needed, ban risk.

If you're running a real business bot and want stability, see the **[WhatsApp Business Cloud API guide](./whatsapp-cloud.md)** instead. It's the official Meta-supported path: no account ban risk, but requires a Meta Business account and a public webhook URL.

The two adapters can also run in parallel against different phone numbers if you have a reason to.
:::

:::warning Unofficial API — Ban Risk
WhatsApp does **not** officially support third-party bots outside the Business API. Using a third-party bridge carries a small risk of account restrictions. To minimize risk:
- **Use a dedicated phone number** for the bot (not your personal number)
- **Don't send bulk/spam messages** — keep usage conversational
- **Don't automate outbound messaging** to people who haven't messaged first
:::

:::warning WhatsApp Web Protocol Updates
WhatsApp periodically updates their Web protocol, which can temporarily break compatibility
with third-party bridges. When this happens, Hermes will update the bridge dependency. If the
bot stops working after a WhatsApp update, pull the latest Hermes version and re-pair.
:::

## Two Modes

| Mode | How it works | Best for |
|------|-------------|----------|
| **Separate bot number** (recommended) | Dedicate a phone number to the bot. People message that number directly. | Clean UX, multiple users, lower ban risk |
| **Personal self-chat** | Use your own WhatsApp. You message yourself to talk to the agent. | Quick setup, single user, testing |

---

## Prerequisites

- **Node.js v18+** and **npm** — the WhatsApp bridge runs as a Node.js process
- **A phone with WhatsApp** installed (for scanning the QR code)

Unlike older browser-driven bridges, the current Baileys-based bridge does **not** require a local Chromium or Puppeteer dependency stack.

---

## Step 1: Run the Setup Wizard

```bash
hermes whatsapp
```

The wizard will:

1. Ask which mode you want (**bot** or **self-chat**)
2. Install bridge dependencies if needed
3. Display a **QR code** in your terminal
4. Wait for you to scan it

**To scan the QR code:**

1. Open WhatsApp on your phone
2. Go to **Settings → Linked Devices**
3. Tap **Link a Device**
4. Point your camera at the terminal QR code

Once paired, the wizard confirms the connection and exits. Your session is saved automatically.

:::tip
If the QR code looks garbled, make sure your terminal is at least 60 columns wide and supports
Unicode. You can also try a different terminal emulator.
:::

---

## Step 2: Getting a Second Phone Number (Bot Mode)

For bot mode, you need a phone number that isn't already registered with WhatsApp. Three options:

| Option | Cost | Notes |
|--------|------|-------|
| **Google Voice** | Free | US only. Get a number at [voice.google.com](https://voice.google.com). Verify WhatsApp via SMS through the Google Voice app. |
| **Prepaid SIM** | $5–15 one-time | Any carrier. Activate, verify WhatsApp, then the SIM can sit in a drawer. Number must stay active (make a call every 90 days). |
| **VoIP services** | Free–$5/month | TextNow, TextFree, or similar. Some VoIP numbers are blocked by WhatsApp — try a few if the first doesn't work. |

After getting the number:

1. Install WhatsApp on a phone (or use WhatsApp Business app with dual-SIM)
2. Register the new number with WhatsApp
3. Run `hermes whatsapp` and scan the QR code from that WhatsApp account

---

## Step 3: Configure Hermes

Add the following to your `~/.hermes/.env` file:

```bash
# Required
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot                          # "bot" or "self-chat"

# Access control — pick ONE of these options:
WHATSAPP_ALLOWED_USERS=15551234567         # Comma-separated phone numbers (with country code, no +)
# WHATSAPP_ALLOWED_USERS=*                 # OR use * to allow everyone
# WHATSAPP_ALLOW_ALL_USERS=true            # OR set this flag instead (same effect as *)
```

:::tip Allow-all shorthand
Setting `WHATSAPP_ALLOWED_USERS=*` allows **all** senders (equivalent to `WHATSAPP_ALLOW_ALL_USERS=true`).
This is consistent with [Signal group allowlists](/reference/environment-variables).
To use the pairing flow instead, remove both variables and rely on the
[DM pairing system](/user-guide/security#dm-pairing-system).
:::

Optional behavior settings in `~/.hermes/config.yaml`:

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `unauthorized_dm_behavior: pair` is the global default. Unknown DM senders get a pairing code.
- `whatsapp.unauthorized_dm_behavior: ignore` makes WhatsApp stay silent for unauthorized DMs, which is usually the better choice for a private number.

Then start the gateway:

```bash
hermes gateway              # Foreground
hermes gateway install      # Install as a user service
sudo hermes gateway install --system   # Linux only: boot-time system service
```

The gateway starts the WhatsApp bridge automatically using the saved session.

---

## Session Persistence

The Baileys bridge saves its session under `~/.hermes/platforms/whatsapp/session`. This means:

- **Sessions survive restarts** — you don't need to re-scan the QR code every time
- The session data includes encryption keys and device credentials
- **Do not share or commit this session directory** — it grants full access to the WhatsApp account

---

## Re-pairing

If the session breaks (phone reset, WhatsApp update, manually unlinked), you'll see connection
errors in the gateway logs. To fix it:

```bash
hermes whatsapp
```

This generates a fresh QR code. Scan it again and the session is re-established. The gateway
handles **temporary** disconnections (network blips, phone going offline briefly) automatically
with reconnection logic.

---

## Voice Messages

Hermes supports voice on WhatsApp:

- **Incoming:** Voice messages (`.ogg` opus) are automatically transcribed using the configured STT provider: local `faster-whisper`, Groq Whisper (`GROQ_API_KEY`), or OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`)
- **Outgoing:** TTS responses are sent as MP3 audio file attachments
- Agent responses are prefixed with "⚕ **Hermes Agent**" by default. You can customize or disable this in `config.yaml`:

```yaml
# ~/.hermes/config.yaml
whatsapp:
  reply_prefix: ""                          # Empty string disables the header
  # reply_prefix: "🤖 *My Bot*\n──────\n"  # Custom prefix (supports \n for newlines)
```

---

## Message Formatting & Delivery

WhatsApp supports **streaming (progressive) responses** — the bot edits its message in real-time as the AI generates text, just like Discord and Telegram. Internally, WhatsApp is classified as a TIER_MEDIUM platform for delivery capabilities.

### Chunking

Long responses are automatically split into multiple messages at **4,096 characters** per chunk (WhatsApp's practical display limit). You don't need to configure anything — the gateway handles splitting and sends chunks sequentially.

### WhatsApp-Compatible Markdown

Standard Markdown in AI responses is automatically converted to WhatsApp's native formatting:

| Markdown | WhatsApp | Renders as |
|----------|----------|------------|
| `**bold**` | `*bold*` | **bold** |
| `~~strikethrough~~` | `~strikethrough~` | ~~strikethrough~~ |
| `# Heading` | `*Heading*` | Bold text (no native headings) |
| `[link text](url)` | `link text (url)` | Inline URL |

Code blocks and inline code are preserved as-is since WhatsApp supports triple-backtick formatting natively.

### Tool Progress

When the agent calls tools (web search, file operations, etc.), WhatsApp displays real-time progress indicators showing which tool is running. This is enabled by default — no configuration needed.

### Message Batching (Debounce)

WhatsApp delivers each message individually, so a rapid burst (forwarded batches, paste-splits, multi-line text) would otherwise trigger a separate agent invocation per fragment — wasting tokens and producing several disjointed replies. The adapter buffers successive text messages from the same chat and dispatches them as one combined request after a short quiet period (default **5s**, extended to **10s** for very long fragments). Tune via `config.yaml`:

```yaml
# ~/.hermes/config.yaml
gateway:
  platforms:
    whatsapp:
      extra:
        text_batch_delay_seconds: 5.0         # quiet period before flushing a batch
        text_batch_split_delay_seconds: 10.0  # extended delay near the split threshold
```

Set `text_batch_delay_seconds: 0` to dispatch each message immediately (disables batching).

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **QR code not scanning** | Ensure terminal is wide enough (60+ columns). Try a different terminal. Make sure you're scanning from the correct WhatsApp account (bot number, not personal). |
| **QR code expires** | QR codes refresh every ~20 seconds. If it times out, restart `hermes whatsapp`. |
| **Session not persisting** | Check that `~/.hermes/platforms/whatsapp/session` exists and is writable. If containerized, mount it as a persistent volume. |
| **Logged out unexpectedly** | WhatsApp unlinks devices after long inactivity. Keep the phone on and connected to the network, then re-pair with `hermes whatsapp` if needed. |
| **Bridge crashes or reconnect loops** | Restart the gateway, update Hermes, and re-pair if the session was invalidated by a WhatsApp protocol change. |
| **Bot stops working after WhatsApp update** | Update Hermes to get the latest bridge version, then re-pair. |
| **macOS: "Node.js not installed" but node works in terminal** | launchd services don't inherit your shell PATH. Run `hermes gateway install` to re-snapshot your current PATH into the plist, then `hermes gateway start`. See the [Gateway Service docs](./index.md#macos-launchd) for details. |
| **Messages not being received** | Verify `WHATSAPP_ALLOWED_USERS` includes the sender's number (with country code, no `+` or spaces), or set it to `*` to allow everyone. Set `WHATSAPP_DEBUG=true` in `.env` and restart the gateway to see raw message events in `bridge.log`. |
| **Bot replies to strangers with a pairing code** | Set `whatsapp.unauthorized_dm_behavior: ignore` in `~/.hermes/config.yaml` if you want unauthorized DMs to be silently ignored instead. |

---

## Security

:::warning
**Configure access control** before going live. Set `WHATSAPP_ALLOWED_USERS` with specific
phone numbers (including country code, without the `+`), use `*` to allow everyone, or set
`WHATSAPP_ALLOW_ALL_USERS=true`. Without any of these, the gateway **denies all incoming
messages** as a safety measure.
:::

By default, unauthorized DMs still receive a pairing code reply. If you want a private WhatsApp number to stay completely silent to strangers, set:

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- The `~/.hermes/platforms/whatsapp/session` directory contains full session credentials — protect it like a password
- Set file permissions: `chmod 700 ~/.hermes/platforms/whatsapp/session`
- Use a **dedicated phone number** for the bot to isolate risk from your personal account
- If you suspect compromise, unlink the device from WhatsApp → Settings → Linked Devices
- Phone numbers in logs are partially redacted, but review your log retention policy

---

# SOURCE: website/docs/user-guide/messaging/signal.md

---
sidebar_position: 6
title: "Signal"
description: "Set up Hermes Agent as a Signal messenger bot via signal-cli daemon"
---

# Signal Setup

Hermes connects to Signal through the [signal-cli](https://github.com/AsamK/signal-cli) daemon running in HTTP mode. The adapter streams messages in real-time via SSE (Server-Sent Events) and sends responses via JSON-RPC.

Signal is the most privacy-focused mainstream messenger — end-to-end encrypted by default, open-source protocol, minimal metadata collection. This makes it ideal for security-sensitive agent workflows.

:::info No New Python Dependencies
The Signal adapter uses `httpx` (already a core Hermes dependency) for all communication. No additional Python packages are required. You just need signal-cli installed externally.
:::

---

## Prerequisites

- **signal-cli** — Java-based Signal client ([GitHub](https://github.com/AsamK/signal-cli))
- **Java 17+** runtime — required by signal-cli
- **A phone number** with Signal installed (for linking as a secondary device)

### Installing signal-cli

```bash
# macOS
brew install signal-cli

# Linux (download latest release)
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} \
  https://github.com/AsamK/signal-cli/releases/latest | sed 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}.tar.gz"
sudo tar xf "signal-cli-${VERSION}.tar.gz" -C /opt
sudo ln -sf "/opt/signal-cli-${VERSION}/bin/signal-cli" /usr/local/bin/
```

:::caution
signal-cli is **not** in apt or snap repositories. The Linux install above downloads directly from [GitHub releases](https://github.com/AsamK/signal-cli/releases).
:::

---

## Step 1: Link Your Signal Account

Signal-cli works as a **linked device** — like WhatsApp Web, but for Signal. Your phone stays the primary device.

```bash
# Generate a linking URI (displays a QR code or link)
signal-cli link -n "HermesAgent"
```

1. Open **Signal** on your phone
2. Go to **Settings → Linked Devices**
3. Tap **Link New Device**
4. Scan the QR code or enter the URI

---

## Step 2: Start the signal-cli Daemon

```bash
# Replace +1234567890 with your Signal phone number (E.164 format)
signal-cli --account +1234567890 daemon --http 127.0.0.1:8080
```

:::tip
Keep this running in the background. You can use `systemd`, `tmux`, `screen`, or run it as a service.
:::

Verify it's running:

```bash
curl http://127.0.0.1:8080/api/v1/check
# Should return: {"versions":{"signal-cli":...}}
```

---

## Step 3: Configure Hermes

The easiest way:

```bash
hermes gateway setup
```

Select **Signal** from the platform menu. The wizard will:

1. Check if signal-cli is installed
2. Prompt for the HTTP URL (default: `http://127.0.0.1:8080`)
3. Test connectivity to the daemon
4. Ask for your account phone number
5. Configure allowed users and access policies

### Manual Configuration

Add to `~/.hermes/.env`:

```bash
# Required
SIGNAL_HTTP_URL=http://127.0.0.1:8080
SIGNAL_ACCOUNT=+1234567890

# Security (recommended)
SIGNAL_ALLOWED_USERS=+1234567890,+0987654321    # Comma-separated E.164 numbers or UUIDs

# Optional
SIGNAL_GROUP_ALLOWED_USERS=groupId1,groupId2     # Enable groups (omit to disable, * for all)
SIGNAL_HOME_CHANNEL=+1234567890                  # Default delivery target for cron jobs
```

Then start the gateway:

```bash
hermes gateway              # Foreground
hermes gateway install      # Install as a user service
sudo hermes gateway install --system   # Linux only: boot-time system service
```

---

## Access Control

### DM Access

DM access follows the same pattern as all other Hermes platforms:

1. **`SIGNAL_ALLOWED_USERS` set** → only those users can message
2. **No allowlist set** → unknown users get a DM pairing code (approve via `hermes pairing approve signal CODE`)
3. **`SIGNAL_ALLOW_ALL_USERS=true`** → anyone can message (use with caution)

### Group Access

Group access is controlled by the `SIGNAL_GROUP_ALLOWED_USERS` env var:

| Configuration | Behavior |
|---------------|----------|
| Not set (default) | All group messages are ignored. The bot only responds to DMs. |
| Set with group IDs | Only listed groups are monitored (e.g., `groupId1,groupId2`). |
| Set to `*` | The bot responds in any group it's a member of. |

---

## Features

### Attachments

The adapter supports sending and receiving media in both directions.

**Incoming** (user → agent):

- **Images** — PNG, JPEG, GIF, WebP (auto-detected via magic bytes)
- **Audio** — MP3, OGG, WAV, M4A (voice messages transcribed if Whisper is configured)
- **Documents** — PDF, ZIP, and other file types

**Outgoing** (agent → user):

The agent can send media files via `MEDIA:` tags in responses. The following delivery methods are supported:

- **Images** — `send_multiple_images` and `send_image_file` send PNG, JPEG, GIF, WebP as native Signal attachments
- **Voice** — `send_voice` sends audio files (OGG, MP3, WAV, M4A, AAC) as attachments
- **Video** — `send_video` sends MP4 video files
- **Documents** — `send_document` sends any file type (PDF, ZIP, etc.)

All outgoing media goes through Signal's standard attachment API. Unlike some platforms, Signal does not distinguish between voice messages and file attachments at the protocol level.

Attachment size limit: **100 MB** (both directions).
:::warning
**Signal servers will rate-limit attachment uploads**, the adapter uses a scheduler for multiple image sending that batches images in groups of 32 and throttles uploads to match the Signal server policy.
:::

### Native Formatting, Reply Quotes, and Reactions

Signal messages render with **native formatting** instead of literal markdown characters. The adapter converts markdown (`**bold**`, `*italic*`, `` `code` ``, `~~strike~~`, `||spoiler||`, headings) into Signal `bodyRanges` so the text shows up with real styling on the recipient's client rather than as visible `**` / `` ` `` characters.

**Reply quotes.** When Hermes replies to a specific message, it now posts a native reply that quotes the original — same UI affordance Signal users see when they use "Reply" themselves. This is automatic for replies generated in response to an inbound message.

**Reactions.** The agent can react to messages via the standard reaction API; reactions surface in Signal as emoji reactions on the referenced message rather than as extra text.

None of this requires additional config — it ships on by default in recent signal-cli builds. If your `signal-cli` version is too old, Hermes falls back to plaintext delivery and logs a one-time warning.

### Typing Indicators

The bot sends typing indicators while processing messages, refreshing every 8 seconds.

### Tool Progress Display

Signal does not support editing already-sent messages. Hermes therefore suppresses gateway tool-progress bubbles on Signal, even when `/verbose` is enabled and saves a non-`off` mode for the platform.

You can still see tool activity in the CLI, and final Signal replies can include normal assistant output. If you need live per-tool progress in chat, use a messaging platform with message editing support.

### Phone Number Redaction

All phone numbers are automatically redacted in logs:
- `+15551234567` → `+155****4567`
- This applies to both Hermes gateway logs and the global redaction system

### Note to Self (Single-Number Setup)

If you run signal-cli as a **linked secondary device** on your own phone number (rather than a separate bot number), you can interact with Hermes through Signal's "Note to Self" feature.

Just send a message to yourself from your phone — signal-cli picks it up and Hermes responds in the same conversation.

**How it works:**
- "Note to Self" messages arrive as `syncMessage.sentMessage` envelopes
- The adapter detects when these are addressed to the bot's own account and processes them as regular inbound messages
- Echo-back protection (sent-timestamp tracking) prevents infinite loops — the bot's own replies are filtered out automatically

**No extra configuration needed.** This works automatically as long as `SIGNAL_ACCOUNT` matches your phone number.

### Health Monitoring

The adapter monitors the SSE connection and automatically reconnects if:
- The connection drops (with exponential backoff: 2s → 60s)
- No activity is detected for 120 seconds (pings signal-cli to verify)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Cannot reach signal-cli"** during setup | Ensure signal-cli daemon is running: `signal-cli --account +YOUR_NUMBER daemon --http 127.0.0.1:8080` |
| **Messages not received** | Check that `SIGNAL_ALLOWED_USERS` includes the sender's number in E.164 format (with `+` prefix) |
| **"signal-cli not found on PATH"** | Install signal-cli and ensure it's in your PATH, or use Docker |
| **Connection keeps dropping** | Check signal-cli logs for errors. Ensure Java 17+ is installed. |
| **Group messages ignored** | Configure `SIGNAL_GROUP_ALLOWED_USERS` with specific group IDs, or `*` to allow all groups. |
| **Bot responds to no one** | Configure `SIGNAL_ALLOWED_USERS`, use DM pairing, or explicitly allow all users through gateway policy if you want broader access. |
| **Duplicate messages** | Ensure only one signal-cli instance is listening on your phone number |

---

## Security

:::warning
**Always configure access controls.** The bot has terminal access by default. Without `SIGNAL_ALLOWED_USERS` or DM pairing, the gateway denies all incoming messages as a safety measure.
:::

- Phone numbers are redacted in all log output
- Use DM pairing or explicit allowlists for safe onboarding of new users
- Keep groups disabled unless you specifically need group support, or allowlist only the groups you trust
- Signal's end-to-end encryption protects message content in transit
- The signal-cli session data in `~/.local/share/signal-cli/` contains account credentials — protect it like a password

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SIGNAL_HTTP_URL` | Yes | — | signal-cli HTTP endpoint |
| `SIGNAL_ACCOUNT` | Yes | — | Bot phone number (E.164) |
| `SIGNAL_ALLOWED_USERS` | No | — | Comma-separated phone numbers/UUIDs |
| `SIGNAL_GROUP_ALLOWED_USERS` | No | — | Group IDs to monitor, or `*` for all (omit to disable groups) |
| `SIGNAL_ALLOW_ALL_USERS` | No | `false` | Allow any user to interact (skip allowlist) |
| `SIGNAL_HOME_CHANNEL` | No | — | Default delivery target for cron jobs |

---

# SOURCE: website/docs/user-guide/messaging/email.md

---
sidebar_position: 7
title: "Email"
description: "Set up Hermes Agent as an email assistant via IMAP/SMTP"
---

# Email Setup

Hermes can receive and reply to emails using standard IMAP and SMTP protocols. Send an email to the agent's address and it replies in-thread — no special client or bot API needed. Works with Gmail, Outlook, Yahoo, Fastmail, or any provider that supports IMAP/SMTP.

:::info Gateway adapter only: no external dependencies
This page covers the Email gateway adapter, which uses Python's built-in `imaplib`, `smtplib`, and `email` modules. No additional packages or external services are required for this gateway path.
:::

This is separate from the bundled [Himalaya email skill](/docs/user-guide/skills/bundled/email/email-himalaya), which lets the agent manage email through terminal commands and requires the external `himalaya` CLI plus a Himalaya config file.

| Use case | What to configure | External dependency |
|---|---|---|
| Let people email the Hermes agent and receive replies | Email gateway adapter on this page | None beyond an IMAP/SMTP email account |
| Let the agent inspect, compose, move, and manage mailbox messages from terminal tools | Himalaya email skill | `himalaya` CLI and `~/.config/himalaya/config.toml` |

---

## Prerequisites

- **A dedicated email account** for your Hermes agent (don't use your personal email)
- **IMAP enabled** on the email account
- **An app password** if using Gmail or another provider with 2FA

### Gmail Setup

1. Enable 2-Factor Authentication on your Google Account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Create a new App Password (select "Mail" or "Other")
4. Copy the 16-character password — you'll use this instead of your regular password

### Outlook / Microsoft 365

1. Go to [Security Settings](https://account.microsoft.com/security)
2. Enable 2FA if not already active
3. Create an App Password under "Additional security options"
4. IMAP host: `outlook.office365.com`, SMTP host: `smtp.office365.com`

### Other Providers

Most email providers support IMAP/SMTP. Check your provider's documentation for:
- IMAP host and port (usually port 993 with SSL)
- SMTP host and port (usually port 587 with STARTTLS)
- Whether app passwords are required

---

## Step 1: Configure Hermes

The easiest way:

```bash
hermes gateway setup
```

Select **Email** from the platform menu. The wizard prompts for your email address, password, IMAP/SMTP hosts, and allowed senders.

### Manual Configuration

Add to `~/.hermes/.env`:

```bash
# Required
EMAIL_ADDRESS=hermes@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop    # App password (not your regular password)
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_SMTP_HOST=smtp.gmail.com

# Security (recommended)
EMAIL_ALLOWED_USERS=your@email.com,colleague@work.com

# Optional
EMAIL_IMAP_PORT=993                    # Default: 993 (IMAP SSL)
EMAIL_SMTP_PORT=587                    # Default: 587 (SMTP STARTTLS)
EMAIL_POLL_INTERVAL=15                 # Seconds between inbox checks (default: 15)
EMAIL_HOME_ADDRESS=your@email.com      # Default delivery target for cron jobs
```

---

## Step 2: Start the Gateway

```bash
hermes gateway              # Run in foreground
hermes gateway install      # Install as a user service
sudo hermes gateway install --system   # Linux only: boot-time system service
```

On startup, the adapter:
1. Tests IMAP and SMTP connections
2. Marks all existing inbox messages as "seen" (only processes new emails)
3. Starts polling for new messages

---

## How It Works

### Receiving Messages

The adapter polls the IMAP inbox for UNSEEN messages at a configurable interval (default: 15 seconds). For each new email:

- **Subject line** is included as context (e.g., `[Subject: Deploy to production]`)
- **Reply emails** (subject starting with `Re:`) skip the subject prefix — the thread context is already established
- **Attachments** are cached locally:
  - Images (JPEG, PNG, GIF, WebP) → available to the vision tool
  - Documents (PDF, ZIP, etc.) → available for file access
- **HTML-only emails** have tags stripped for plain text extraction
- **Self-messages** are filtered out to prevent reply loops
- **Automated/noreply senders** are silently ignored — `noreply@`, `mailer-daemon@`, `bounce@`, `no-reply@`, and emails with `Auto-Submitted`, `Precedence: bulk`, or `List-Unsubscribe` headers

### Sending Replies

Replies are sent via SMTP with proper email threading:

- **In-Reply-To** and **References** headers maintain the thread
- **Subject line** preserved with `Re:` prefix (no double `Re: Re:`)
- **Message-ID** generated with the agent's domain
- Responses are sent as plain text (UTF-8)

### File Attachments

The agent can send file attachments in replies. Include `MEDIA:/path/to/file` in the response and the file is attached to the outgoing email.

### Skipping Attachments

To ignore all incoming attachments (for malware protection or bandwidth savings), add to your `config.yaml`:

```yaml
platforms:
  email:
    skip_attachments: true
```

When enabled, attachment and inline parts are skipped before payload decoding. The email body text is still processed normally.

---

## Access Control

Email access is stricter by default than chat-style platforms:

1. **`EMAIL_ALLOWED_USERS` set** → only emails from those addresses are processed
2. **No allowlist set** → unknown senders are ignored silently
3. **`EMAIL_ALLOW_ALL_USERS=true`** → any sender is accepted (use with caution)
4. **`platforms.email.unauthorized_dm_behavior: pair`** → unknown senders receive a pairing code

:::warning
**Use a dedicated inbox and configure `EMAIL_ALLOWED_USERS` for normal operation.** Email pairing is opt-in because shared inboxes often contain unrelated unread messages, and Hermes should not reply to those contacts by default.
:::

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **"IMAP connection failed"** at startup | Verify `EMAIL_IMAP_HOST` and `EMAIL_IMAP_PORT`. Ensure IMAP is enabled on the account. For Gmail, enable it in Settings → Forwarding and POP/IMAP. |
| **"SMTP connection failed"** at startup | Verify `EMAIL_SMTP_HOST` and `EMAIL_SMTP_PORT`. Check that your password is correct (use App Password for Gmail). |
| **Messages not received** | Check `EMAIL_ALLOWED_USERS` includes the sender's email. Check spam folder — some providers flag automated replies. |
| **"Authentication failed"** | For Gmail, you must use an App Password, not your regular password. Ensure 2FA is enabled first. |
| **Duplicate replies** | Ensure only one gateway instance is running. Check `hermes gateway status`. |
| **Slow response** | The default poll interval is 15 seconds. Reduce with `EMAIL_POLL_INTERVAL=5` for faster response (but more IMAP connections). |
| **Replies not threading** | The adapter uses In-Reply-To headers. Some email clients (especially web-based) may not thread correctly with automated messages. |

---

## Security

:::warning
**Use a dedicated email account.** Don't use your personal email — the agent stores the password in `.env` and has full inbox access via IMAP.
:::

- Use **App Passwords** instead of your main password (required for Gmail with 2FA)
- Set `EMAIL_ALLOWED_USERS` to restrict who can interact with the agent
- The password is stored in `~/.hermes/.env` — protect this file (`chmod 600`)
- IMAP uses SSL (port 993) and SMTP uses STARTTLS (port 587) by default — connections are encrypted

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_ADDRESS` | Yes | — | Agent's email address |
| `EMAIL_PASSWORD` | Yes | — | Email password or app password |
| `EMAIL_IMAP_HOST` | Yes | — | IMAP server host (e.g., `imap.gmail.com`) |
| `EMAIL_SMTP_HOST` | Yes | — | SMTP server host (e.g., `smtp.gmail.com`) |
| `EMAIL_IMAP_PORT` | No | `993` | IMAP server port |
| `EMAIL_SMTP_PORT` | No | `587` | SMTP server port |
| `EMAIL_POLL_INTERVAL` | No | `15` | Seconds between inbox checks |
| `EMAIL_ALLOWED_USERS` | No | — | Comma-separated allowed sender addresses |
| `EMAIL_HOME_ADDRESS` | No | — | Default delivery target for cron jobs |
| `EMAIL_ALLOW_ALL_USERS` | No | `false` | Allow all senders (not recommended) |
