<!-- Sections in this file (in order):
  - user-guide/features/cron.md
  - guides/automate-with-cron.md
  - guides/automation-blueprints.md
  - guides/cron-script-only.md
  - guides/cron-troubleshooting.md
  - user-guide/features/goals.md
  - user-guide/features/code-execution.md
  - user-guide/features/delegation.md
  - guides/delegation-patterns.md
-->


---

# SOURCE: website/docs/user-guide/features/cron.md

---
sidebar_position: 5
title: "Scheduled Tasks (Cron)"
description: "Schedule automated tasks with natural language, manage them with one cron tool, and attach one or more skills"
---

# Scheduled Tasks (Cron)

Schedule tasks to run automatically with natural language or cron expressions. Hermes exposes cron management through a single `cronjob` tool with action-style operations instead of separate schedule/list/remove tools.

## What cron can do now

Cron jobs can:

- schedule one-shot or recurring tasks
- pause, resume, edit, trigger, and remove jobs
- attach zero, one, or multiple skills to a job
- deliver results back to the origin chat, local files, or configured platform targets
- run in fresh agent sessions with the normal static tool list
- run in **no-agent mode** — a script on a schedule, its stdout delivered verbatim, zero LLM involvement (see the [no-agent mode](#no-agent-mode-script-only-jobs) section below)

All of this is available to Hermes itself through the `cronjob` tool, so you can create, pause, edit, and remove jobs by asking in plain language — no CLI required.

:::tip
At creation, an unpinned job (one you don't give an explicit `provider`/`model`) follows the global default selected by `hermes model` — and Hermes **snapshots** that provider and model on the job. If the global default later changes, the job **fails closed**: it skips the run, makes no inference call, and sends an alert telling you to pin the provider/model explicitly (`cronjob action=update job_id=… provider=… model=…`) to proceed. This prevents an unattended job from silently inheriting a switch to a paid provider/model and spending money you didn't intend (#44585). To make a job deliberately track your global default, pin it to the new values after changing them. `hermes setup --portal` is the lowest-friction option for unattended runs since OAuth refresh is automatic. See [Nous Portal](/integrations/nous-portal).
:::

:::warning
Cron-run sessions cannot recursively create more cron jobs. Hermes disables cron management tools inside cron executions to prevent runaway scheduling loops.
:::

## Creating scheduled tasks

### In chat with `/cron`

```bash
/cron add 30m "Remind me to check the build"
/cron add "every 2h" "Check server status"
/cron add "every 1h" "Summarize new feed items" --skill blogwatcher
/cron add "every 1h" "Use both skills and combine the result" --skill blogwatcher --skill maps
```

### From the standalone CLI

```bash
hermes cron create "every 2h" "Check server status"
hermes cron create "every 1h" "Summarize new feed items" --skill blogwatcher
hermes cron create "every 1h" "Use both skills and combine the result" \
  --skill blogwatcher \
  --skill maps \
  --name "Skill combo"
```

### Through natural conversation

Ask Hermes normally:

```text
Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram.
```

Hermes will use the unified `cronjob` tool internally.

## Skill-backed cron jobs

A cron job can load one or more skills before it runs the prompt.

### Single skill

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="Check the configured feeds and summarize anything new.",
    schedule="0 9 * * *",
    name="Morning feeds",
)
```

### Multiple skills

Skills are loaded in order. The prompt becomes the task instruction layered on top of those skills.

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="Look for new local events and interesting nearby places, then combine them into one short brief.",
    schedule="every 6h",
    name="Local brief",
)
```

This is useful when you want a scheduled agent to inherit reusable workflows without stuffing the full skill text into the cron prompt itself.

## Running a job inside a project directory

Cron jobs default to running detached from any repo — no `AGENTS.md`, `CLAUDE.md`, or `.cursorrules` is loaded, and the terminal / file / code-exec tools run from whatever working directory the gateway started in. Pass `--workdir` (CLI) or `workdir=` (tool call) to change that:

```bash
# Standalone CLI (schedule and prompt are positional)
hermes cron create "every 1d at 09:00" \
  "Audit open PRs, summarize CI health, and post to #eng" \
  --workdir /home/me/projects/acme
```

```python
# From a chat, via the cronjob tool
cronjob(
    action="create",
    schedule="every 1d at 09:00",
    workdir="/home/me/projects/acme",
    prompt="Audit open PRs, summarize CI health, and post to #eng",
)
```

When `workdir` is set:

- `AGENTS.md`, `CLAUDE.md`, and `.cursorrules` from that directory are injected into the system prompt (same discovery order as the interactive CLI)
- `terminal`, `read_file`, `write_file`, `patch`, `search_files`, and `execute_code` all use that directory as their working directory
- The path must be an absolute directory that exists — relative paths and missing directories are rejected at create / update time
- Pass `--workdir ""` (or `workdir=""` via the tool) on edit to clear it and restore the old behaviour

:::note Serialization
Jobs with a `workdir` run sequentially on the scheduler tick, not in the parallel pool. This is deliberate: the cron worker applies the job workdir through process-global terminal state, so two workdir jobs running at the same time would corrupt each other's cwd. Workdir-less jobs still run in parallel as before.
:::

## Editing jobs

You do not need to delete and recreate jobs just to change them.

:::tip Job reference
The `<job_id>` placeholder below (and in [Lifecycle actions](#lifecycle-actions)) also accepts the job's name (case-insensitive) — handy when you remember `morning-digest` but not the hex ID. An exact job ID takes precedence over name matches; if the reference is not an ID and a name matches more than one job, the command refuses and prints the candidate IDs so you can disambiguate.
:::

### Chat

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Use the revised task"
/cron edit <job_id> --skill blogwatcher --skill maps
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```

### Standalone CLI

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "Use the revised task"
hermes cron edit <job_id> --skill blogwatcher --skill maps
hermes cron edit <job_id> --add-skill maps
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

Notes:

- repeated `--skill` replaces the job's attached skill list
- `--add-skill` appends to the existing list without replacing it
- `--remove-skill` removes specific attached skills
- `--clear-skills` removes all attached skills

## Lifecycle actions

Cron jobs now have a fuller lifecycle than just create/remove.

### Chat

```bash
/cron list
/cron pause <job_id>
/cron resume <job_id>
/cron run <job_id>
/cron remove <job_id>
```

### Standalone CLI

```bash
hermes cron list
hermes cron pause <job_id_or_name>
hermes cron resume <job_id_or_name>
hermes cron run <job_id_or_name>
hermes cron remove <job_id_or_name>
hermes cron edit <job_id_or_name> [...flags]
hermes cron status
hermes cron tick
```

What they do:

- `pause` — keep the job but stop scheduling it
- `resume` — re-enable the job and compute the next future run
- `run` — trigger the job on the next scheduler tick
- `remove` — delete it entirely
- `edit` — modify schedule, prompt, delivery, etc.

**Name-based lookup.** All four mutating verbs (`pause`, `resume`, `run`, `remove`, `edit`) plus the agent's `cronjob` tool now accept a job **name** (case-insensitive) in place of the hex ID. The agent and CLI both prefer an exact ID match if one exists; ambiguous name matches (multiple jobs sharing the same name) are refused with the full list of candidate IDs so you can pick one explicitly. Names are not unique, so this guard is load-bearing — it prevents silently mutating the wrong job when two share a name.

## How it works

**Cron execution is handled by the gateway daemon.** The gateway ticks the scheduler every 60 seconds, running any due jobs in isolated agent sessions.

```bash
hermes gateway install     # Install as a user service
sudo hermes gateway install --system   # Linux: boot-time system service for servers
hermes gateway             # Or run in foreground

hermes cron list
hermes cron status
```

### Gateway scheduler behavior

On each tick Hermes:

1. loads jobs from `~/.hermes/cron/jobs.json`
2. checks `next_run_at` against the current time
3. starts a fresh `AIAgent` session for each due job
4. optionally injects one or more attached skills into that fresh session
5. runs the prompt to completion
6. delivers the final response
7. updates run metadata and the next scheduled time

A file lock at `~/.hermes/cron/.tick.lock` prevents overlapping scheduler ticks from double-running the same job batch.

## Delivery options

When scheduling jobs, you specify where the output goes:

| Option | Description | Example |
|--------|-------------|---------|
| `"origin"` | Back to where the job was created | Default on messaging platforms |
| `"local"` | Save to local files only (`~/.hermes/cron/output/`) | Default on CLI |
| `"telegram"` | Telegram home channel | Uses `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | Specific Telegram chat by ID | Direct delivery |
| `"telegram:-100123:17585"` | Specific Telegram topic | `chat_id:thread_id` format |
| `"discord"` | Discord home channel | Uses `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | Specific Discord channel | By channel name |
| `"slack"` | Slack home channel | |
| `"whatsapp"` | WhatsApp home | |
| `"signal"` | Signal | |
| `"matrix"` | Matrix home room | |
| `"mattermost"` | Mattermost home channel | |
| `"email"` | Email | |
| `"sms"` | SMS via Twilio | |
| `"homeassistant"` | Home Assistant | |
| `"dingtalk"` | DingTalk | |
| `"feishu"` | Feishu/Lark | |
| `"wecom"` | WeCom | |
| `"weixin"` | Weixin (WeChat) | |
| `"bluebubbles"` | BlueBubbles (iMessage) | |
| `"qqbot"` | QQ Bot (Tencent QQ) | |
| `"all"` | Fan out to every connected home channel | Resolved at fire time |
| `"telegram,discord"` | Fan out to a specific set of channels | Comma-separated list |
| `"origin,all"` | Deliver to the origin **plus** every other connected channel | Combine any tokens |

The agent's final response is automatically delivered to the configured `deliver:` target — the agent does not send messages itself, so there is nothing to call in the cron prompt.

### Routing intent (`all`)

`all` lets you ship one cron job to every messaging channel you have configured, without having to enumerate them by name. It is **resolved at fire time**, so a job created before you wired up Telegram will pick up Telegram on the next tick after you set `TELEGRAM_HOME_CHANNEL`.

Semantics: `all` expands to every platform with a configured home channel. Zero is fine; the job simply produces no delivery targets and is recorded as a delivery failure upstream.

`all` composes with explicit targets. `origin,all` delivers to the origin chat *plus* every other connected home channel, de-duplicating by `(platform, chat_id, thread_id)`.

### Telegram cron topic (`TELEGRAM_CRON_THREAD_ID`)

When Telegram topic mode is enabled, the root DM is reserved as a system lobby — replies sent there are rebuffed with a lobby reminder and `reply_to_message_id` is dropped, so you cannot reply to a cron message that landed in the main chat.

Point cron at a dedicated forum topic instead:

1. In Telegram, open the bot DM and create a topic named e.g. `Cron`. Long-press the topic header → **Copy link**; the trailing integer is the topic's `message_thread_id`.
2. Set `TELEGRAM_CRON_THREAD_ID=<that id>` in your `.env`.

This applies only to cron deliveries. `TELEGRAM_HOME_CHANNEL_THREAD_ID` (used elsewhere, e.g. restart notifications) is unchanged. Explicit `deliver="telegram:chat_id:thread_id"` targets continue to win over the env var. Replies to cron messages now arrive in the existing topic session, so you can act on them directly.

### Response wrapping

By default, delivered cron output is wrapped with a header and footer so the recipient knows it came from a scheduled task:

```
Cronjob Response: Morning feeds
-------------

<agent output here>

Note: The agent cannot see this message, and therefore cannot respond to it.
```

To deliver the raw agent output without the wrapper, set `cron.wrap_response` to `false`:

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### Continuable jobs (reply to a cron delivery)

By default a cron delivery is fire-and-forget: the message is sent, but it does
not live in the chat's conversation history, so if you reply to it the agent
has no record of what it said. Set a job **continuable** and the delivered brief
becomes a conversation you can reply into — the agent has the brief in context
instead of asking "what is Task #2?".

Opt-in, **default off**. Enable globally in config, or per-job via the `cronjob`
tool's `attach_to_session` (which overrides the global setting for that one job):

```yaml
# ~/.hermes/config.yaml
cron:
  mirror_delivery: false   # set true to make cron deliveries continuable
```

Behaviour is **thread-preferred**, scoped to the job's origin chat:

- **Thread-capable platforms** (Telegram topics, Discord/Slack threads): each
  delivery opens its own dedicated thread and the brief is seeded into that
  thread's session, so a reply in-thread continues with full context. A
  recurring job (e.g. a daily brief) opens a fresh thread per run, keeping each
  delivery's follow-up discussion isolated.
- **DM-only platforms** (WhatsApp, Signal, SMS): no threads exist, so the brief
  is mirrored into the origin DM session instead — the DM itself is the
  continuation surface.

Only the origin chat is ever touched: fan-out / broadcast targets (`all`,
explicit other-chat deliveries) are never made continuable. The mirror is
written as a labelled user turn (`[Cron delivery: <task name>]`), which keeps
the conversation history alternation-safe across all model providers.

### Silent suppression

If the agent's final response contains `[SILENT]`, delivery is suppressed entirely. The output is still saved locally for audit (in `~/.hermes/cron/output/`), but no message is sent to the delivery target.

This is useful for monitoring jobs that should only report when something is wrong:

```text
Check if nginx is running. If everything is healthy, respond with only [SILENT].
Otherwise, report the issue.
```

Failed jobs always deliver regardless of the `[SILENT]` marker — only successful runs can be silenced. For quiet monitoring jobs, prompt the agent to reply with only `[SILENT]` when there is nothing to report.

## Script timeout

Pre-run scripts (attached via the `script` parameter) have a default timeout of 3600 seconds (1 hour). This bounds the **script only** — skill-based / LLM-driven jobs run on a separate inactivity budget and are not capped by this value. If your scripts need a different limit, you can change it:

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 1800   # 30 minutes
```

Or set the `HERMES_CRON_SCRIPT_TIMEOUT` environment variable. The resolution order is: env var → config.yaml → 3600s default.

## No-agent mode (script-only jobs)

For recurring jobs that don't need LLM reasoning — classic watchdogs, disk/memory alerts, heartbeats, CI pings — pass `no_agent=True` at creation time. The scheduler runs your script on schedule and delivers its stdout directly, skipping the agent entirely:

```bash
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"
```

Semantics:

- Script stdout (trimmed) → delivered verbatim as the message.
- **Empty stdout → silent tick**, no delivery. This is the watchdog pattern: "only say something when something is wrong".
- Non-zero exit or timeout → an error alert is delivered, so a broken watchdog can't fail silently.
- `{"wakeAgent": false}` on the last line → silent tick (same gate LLM jobs use).
- No tokens, no model, no provider fallback — the job never touches the inference layer.

`.sh` / `.bash` files run under `/bin/bash`; anything else under the current Python interpreter (`sys.executable`). Scripts must live in `~/.hermes/scripts/` (same sandboxing rule as the pre-run script gate).

### The agent sets these up for you

The `cronjob` tool's schema exposes `no_agent` to Hermes directly, so you can describe a watchdog in chat and let the agent wire it up:

```text
Ping me on Telegram if RAM is over 85%, every 5 minutes.
```

Hermes will write the check script to `~/.hermes/scripts/` via `write_file`, then call:

```python
cronjob(action="create", schedule="every 5m",
        script="memory-watchdog.sh", no_agent=True,
        deliver="telegram", name="memory-watchdog")
```

It picks `no_agent=True` automatically when the message content is fully determined by the script (watchdogs, threshold alerts, heartbeats). The same tool also lets the agent pause, resume, edit, and remove jobs — so the whole lifecycle is chat-driven without anyone touching the CLI.

See the [Script-Only Cron Jobs guide](/guides/cron-script-only) for worked examples.

## Chaining jobs with `context_from`

Cron jobs run in isolated sessions with no memory of previous runs. But sometimes one job's output is exactly what the next job needs. The `context_from` parameter wires that connection automatically — Job B's prompt gets Job A's most recent output prepended as context at runtime.

```python
# Job 1: Collect raw data
cronjob(
    action="create",
    prompt="Fetch the top 10 AI/ML stories from Hacker News. Save them to ~/.hermes/data/briefs/raw.md in markdown format with title, URL, and score.",
    schedule="0 7 * * *",
    name="AI News Collector",
)

# Job 2: Triage — receives Job 1's output as context
# Get Job 1's ID from: cronjob(action="list")
cronjob(
    action="create",
    prompt="Read ~/.hermes/data/briefs/raw.md. Score each story 1–10 for engagement potential and novelty. Output the top 5 to ~/.hermes/data/briefs/ranked.md.",
    schedule="30 7 * * *",
    context_from="<job1_id>",
    name="AI News Triage",
)

# Job 3: Ship — receives Job 2's output as context
cronjob(
    action="create",
    prompt="Read ~/.hermes/data/briefs/ranked.md. Write 3 tweet drafts (hook + body + hashtags). Deliver to telegram:7976161601.",
    schedule="0 8 * * *",
    context_from="<job2_id>",
    name="AI News Brief",
)
```

**How it works:**

- When Job 2 fires, Hermes reads Job 1's most recent output from `~/.hermes/cron/output/{job1_id}/*.md`
- That output is prepended to Job 2's prompt automatically
- Job 2 doesn't need to hardcode "read this file" — it receives the content as context
- The chain can be any length: Job 1 → Job 2 → Job 3 → ...

**What `context_from` accepts:**

| Format | Example |
|--------|---------|
| Single job ID (string) | `context_from="a1b2c3d4"` |
| Multiple job IDs (list) | `context_from=["job_a", "job_b"]` |

Outputs are concatenated in the order listed.

**When to use it:**

- Multi-stage pipelines (collect → filter → format → deliver)
- Dependent tasks where step N's work depends on step N−1's output
- Fan-out/fan-in patterns where one job aggregates results from several others

## Provider recovery

Cron jobs inherit your configured fallback providers and credential pool rotation. If the primary API key is rate-limited or the provider returns an error, the cron agent can:

- **Fall back to an alternate provider** if you have `fallback_providers` (or the legacy `fallback_model`) configured in `config.yaml`
- **Rotate to the next credential** in your [credential pool](/user-guide/configuration#credential-pool-strategies) for the same provider

This means cron jobs that run at high frequency or during peak hours are more resilient — a single rate-limited key won't fail the entire run.

## Schedule formats

The agent's final response is automatically delivered to the job's `deliver:` target — the agent no longer fires messages itself, so the user-facing content simply goes in the final response. To deliver to **additional or different** targets, list multiple `deliver:` targets on the cron job (comma-separated, e.g. `deliver: "telegram,discord"`) rather than having the agent send them.

### Relative delays (one-shot)

```text
30m     → Run once in 30 minutes
2h      → Run once in 2 hours
1d      → Run once in 1 day
```

### Intervals (recurring)

```text
every 30m    → Every 30 minutes
every 2h     → Every 2 hours
every 1d     → Every day
```

### Cron expressions

```text
0 9 * * *       → Daily at 9:00 AM
0 9 * * 1-5     → Weekdays at 9:00 AM
0 */6 * * *     → Every 6 hours
30 8 1 * *      → First of every month at 8:30 AM
0 0 * * 0       → Every Sunday at midnight
```

### ISO timestamps

```text
2026-03-15T09:00:00    → One-time at March 15, 2026 9:00 AM
```

## Repeat behavior

| Schedule type | Default repeat | Behavior |
|--------------|----------------|----------|
| One-shot (`30m`, timestamp) | 1 | Runs once |
| Interval (`every 2h`) | forever | Runs until removed |
| Cron expression | forever | Runs until removed |

You can override it:

```python
cronjob(
    action="create",
    prompt="...",
    schedule="every 2h",
    repeat=5,
)
```

## Managing jobs programmatically

The agent-facing API is one tool:

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

For `update`, pass `skills=[]` to remove all attached skills.

## Toolsets available to cron jobs

Cron runs each job in a fresh agent session with no chat platform attached. By default the cron agent gets **the toolset you configured for the `cron` platform in `hermes tools`** — not the CLI default, not everything under the sun.

```bash
hermes tools
# → pick the "cron" platform in the curses UI
# → toggle toolsets on/off just like you would for Telegram/Discord/etc.
```

Tighter per-job control is available via the `enabled_toolsets` field on `cronjob.create` (or on an existing job via `cronjob.update`):

```text
cronjob(action="create", name="weekly-news-summary",
        schedule="every sunday 9am",
        enabled_toolsets=["web", "file"],      # just web + file, no terminal/browser/etc.
        prompt="Summarize this week's AI news: ...")
```

When `enabled_toolsets` is set on a job it wins; otherwise the `hermes tools` cron-platform config wins; otherwise Hermes falls back to the built-in defaults. This matters for cost control: carrying `browser`, `delegation` into every tiny "fetch news" job bloats the tool-schema prompt on every LLM call.

### Skipping the agent entirely: `wakeAgent`

If your cron job attaches a pre-check script (via `script=`), the script can decide at runtime whether Hermes should even invoke the agent. Emit a final stdout line of the form:

```text
{"wakeAgent": false}
```

…and cron skips the agent run entirely for this tick. Useful for frequent polls (every 1–5 min) that only need to wake the LLM when state actually changed — otherwise you pay for zero-content agent turns over and over.

```python
# pre-check script
import json, sys
latest = fetch_latest_issue_count()
prev = read_state("issue_count")
if latest == prev:
    print(json.dumps({"wakeAgent": False}))   # skip this tick
    sys.exit(0)
write_state("issue_count", latest)
print(json.dumps({"wakeAgent": True, "context": {"new_issues": latest - prev}}))
```

When `wakeAgent` is omitted, the default is `true` (wake the agent as usual).

#### Recipes: cheap pre-run gates

The `wakeAgent` gate gives you a $0 way to decide whether a scheduled job should spend any LLM tokens at all. Three patterns cover most use cases.

**File-change gate** — only run when a watched file has new content since the last successful tick. The scheduler records each job's `last_run_at`; compare it against the file's mtime.

```bash
#!/bin/bash
# ~/.hermes/scripts/feed-changed.sh
FEED="$HOME/data/feed.json"
STATE="$HOME/.hermes/scripts/.feed-changed.last"
test -f "$FEED" || { echo '{"wakeAgent": false}'; exit 0; }
mtime=$(stat -c %Y "$FEED")
last=$(cat "$STATE" 2>/dev/null || echo 0)
if [ "$mtime" -le "$last" ]; then
  echo '{"wakeAgent": false}'
else
  echo "$mtime" > "$STATE"
  echo '{"wakeAgent": true}'
fi
```

```text
cronjob(action="create", name="process-feed",
        schedule="every 30m",
        script="feed-changed.sh",
        prompt="A new ~/data/feed.json has landed. Summarize what changed.")
```

**External-flag gate** — only run when some other process has signalled readiness (e.g. a deploy hook drops a file, a CI job sets a value in your state store).

```bash
#!/bin/bash
# ~/.hermes/scripts/flag-ready.sh
if test -f /tmp/new-data-ready; then
  rm -f /tmp/new-data-ready
  echo '{"wakeAgent": true}'
else
  echo '{"wakeAgent": false}'
fi
```

```text
cronjob(action="create", name="nightly-analysis",
        schedule="0 9 * * *",
        script="flag-ready.sh",
        prompt="Run the nightly analysis over today's batch.")
```

**SQL-count gate** — only run when there are new rows to process in your own database. The script can also pass the count through to the agent via `context`, so the agent knows how much it's looking at without re-querying.

```python
#!/usr/bin/env python
# ~/.hermes/scripts/new-rows.py
import json, sqlite3
conn = sqlite3.connect("/home/me/data/app.db")
n = conn.execute(
    "SELECT COUNT(*) FROM messages WHERE ts > strftime('%s','now','-2 hours')"
).fetchone()[0]
if n < 1:
    print(json.dumps({"wakeAgent": False}))
else:
    print(json.dumps({"wakeAgent": True, "context": {"new_rows": n}}))
```

```text
cronjob(action="create", name="summarize-new-msgs",
        schedule="every 2h",
        script="new-rows.py",
        prompt="Summarize the new messages from the last 2 hours.")
```

The same pattern works for any data source you can query from a script — Postgres, an HTTP API, your own state store — without baking a SQL evaluator into the cron subsystem.

:::tip
Hermes's own `~/.hermes/state.db` is an internal schema that changes between releases. Don't query it from a pre-run gate — point at your own database or feed instead.
:::

Credit: this recipe set was prompted by @iankar8's exploration in [#2654](https://github.com/NousResearch/hermes-agent/pull/2654), which proposed adding sql/file/command triggers as a parallel mechanism. The `script` + `wakeAgent` gate already covers all three cases at $0, so the work landed as documentation instead.

### Chaining jobs: `context_from`

A cron job can consume the most recent successful output of one or more other jobs by listing their names (or IDs) in `context_from`:

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="Write the daily digest using the outputs above.")
```

The referenced jobs' most recent completed outputs are injected above the prompt as context for this run. Each upstream entry must be a valid job ID or name (see `cronjob action="list"`). Note: chaining reads the *most recent completed* output — it does not wait for upstream jobs that are running in the same tick.

## Job storage

Jobs are stored in `~/.hermes/cron/jobs.json`. Output from job runs is saved to `~/.hermes/cron/output/{job_id}/{timestamp}.md`.

Jobs may store `model` and `provider` as `null`. When those fields are omitted, Hermes resolves them at execution time from the global configuration. They only appear in the job record when a per-job override is set.

The storage uses atomic file writes so interrupted writes do not leave a partially written job file behind.

## Self-contained prompts still matter

:::warning Important
Cron jobs run in a completely fresh agent session. The prompt must contain everything the agent needs that is not already provided by attached skills.
:::

**BAD:** `"Check on that server issue"`

**GOOD:** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`

## Security

Scheduled task prompts are scanned for prompt-injection and credential-exfiltration patterns at creation and update time. Prompts containing invisible Unicode tricks, SSH backdoor attempts, or obvious secret-exfiltration payloads are blocked.

---

# SOURCE: website/docs/guides/automate-with-cron.md

---
sidebar_position: 11
title: "Automate Anything with Cron"
description: "Real-world automation patterns using Hermes cron — monitoring, reports, pipelines, and multi-skill workflows"
---

# Automate Anything with Cron

The [daily briefing bot tutorial](/guides/daily-briefing-bot) covers the basics. This guide goes further — five real-world automation patterns you can adapt for your own workflows.

For the full feature reference, see [Scheduled Tasks (Cron)](/user-guide/features/cron).

:::info Key Concept
Cron jobs run in fresh agent sessions with no memory of your current chat. Prompts must be **completely self-contained** — include everything the agent needs to know.
:::

:::tip Don't need the LLM? You have two zero-token options.
- **Recurring watchdog** where the script already produces the exact message (memory alerts, disk alerts, heartbeats): use [script-only cron jobs](/guides/cron-script-only). Same scheduler, no LLM. You can ask Hermes to set one up for you in chat — the `cronjob` tool knows when to pick `no_agent=True` and writes the script for you.
- **One-shot from a script that's already running** (CI step, post-commit hook, deploy script, externally-scheduled monitor): use [`hermes send`](/guides/pipe-script-output) to pipe stdout or a file straight to Telegram / Discord / Slack / etc. without setting up a cron entry.
:::

---

## Pattern 1: Website Change Monitor

Watch a URL for changes and get notified only when something is different.

The `script` parameter is the secret weapon here. A Python script runs before each execution, and its stdout becomes context for the agent. The script handles the mechanical work (fetching, diffing); the agent handles the reasoning (is this change interesting?).

Create the monitoring script:

```bash
mkdir -p ~/.hermes/scripts
```

```python title="~/.hermes/scripts/watch-site.py"
import hashlib, json, os, urllib.request

URL = "https://example.com/pricing"
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.watch-site-state.json")

# Fetch current content
req = urllib.request.Request(URL, headers={"User-Agent": "Hermes-Monitor/1.0"})
content = urllib.request.urlopen(req, timeout=30).read().decode()
current_hash = hashlib.sha256(content.encode()).hexdigest()

# Load previous state
prev_hash = None
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        prev_hash = json.load(f).get("hash")

# Save current state
with open(STATE_FILE, "w") as f:
    json.dump({"hash": current_hash, "url": URL}, f)

# Output for the agent
if prev_hash and prev_hash != current_hash:
    print(f"CHANGE DETECTED on {URL}")
    print(f"Previous hash: {prev_hash}")
    print(f"Current hash: {current_hash}")
    print(f"\nCurrent content (first 2000 chars):\n{content[:2000]}")
else:
    print("NO_CHANGE")
```

Set up the cron job:

```bash
/cron add "every 1h" "If the script output says CHANGE DETECTED, summarize what changed on the page and why it might matter. If it says NO_CHANGE, respond with just [SILENT]." --script ~/.hermes/scripts/watch-site.py --name "Pricing monitor" --deliver telegram
```

:::tip The [SILENT] Trick
For cron monitoring jobs, instruct the agent to respond with only `[SILENT]` when nothing changed. Cron delivery treats `[SILENT]` as the quiet marker, so you only get notified when something actually happens — no spam on quiet hours.
:::

---

## Pattern 2: Weekly Report

Compile information from multiple sources into a formatted summary. This runs once a week and delivers to your home channel.

```bash
/cron add "0 9 * * 1" "Generate a weekly report covering:

1. Search the web for the top 5 AI news stories from the past week
2. Search GitHub for trending repositories in the 'machine-learning' topic
3. Check Hacker News for the most discussed AI/ML posts

Format as a clean summary with sections for each source. Include links.
Keep it under 500 words — highlight only what matters." --name "Weekly AI digest" --deliver telegram
```

From the CLI:

```bash
hermes cron create "0 9 * * 1" \
  "Generate a weekly report covering the top AI news, trending ML GitHub repos, and most-discussed HN posts. Format with sections, include links, keep under 500 words." \
  --name "Weekly AI digest" \
  --deliver telegram
```

The `0 9 * * 1` is a standard cron expression: 9:00 AM every Monday.

---

## Pattern 3: GitHub Repository Watcher

Monitor a repository for new issues, PRs, or releases.

```bash
/cron add "every 6h" "Check the GitHub repository NousResearch/hermes-agent for:
- New issues opened in the last 6 hours
- New PRs opened or merged in the last 6 hours
- Any new releases

Use the terminal to run gh commands:
  gh issue list --repo NousResearch/hermes-agent --state open --json number,title,author,createdAt --limit 10
  gh pr list --repo NousResearch/hermes-agent --state all --json number,title,author,createdAt,mergedAt --limit 10

Filter to only items from the last 6 hours. If nothing new, respond with [SILENT].
Otherwise, provide a concise summary of the activity." --name "Repo watcher" --deliver discord
```

:::warning Self-Contained Prompts
Notice how the prompt includes the exact `gh` commands. The cron agent has no memory of previous runs or your preferences — spell everything out.
:::

---

## Pattern 4: Data Collection Pipeline

Scrape data at regular intervals, save to files, and detect trends over time. This pattern combines a script (for collection) with the agent (for analysis).

```python title="~/.hermes/scripts/collect-prices.py"
import json, os, urllib.request
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.hermes/data/prices")
os.makedirs(DATA_DIR, exist_ok=True)

# Fetch current data (example: crypto prices)
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
data = json.loads(urllib.request.urlopen(url, timeout=30).read())

# Append to history file
entry = {"timestamp": datetime.now().isoformat(), "prices": data}
history_file = os.path.join(DATA_DIR, "history.jsonl")
with open(history_file, "a") as f:
    f.write(json.dumps(entry) + "\n")

# Load recent history for analysis
lines = open(history_file).readlines()
recent = [json.loads(l) for l in lines[-24:]]  # Last 24 data points

# Output for the agent
print(f"Current: BTC=${data['bitcoin']['usd']}, ETH=${data['ethereum']['usd']}")
print(f"Data points collected: {len(lines)} total, showing last {len(recent)}")
print(f"\nRecent history:")
for r in recent[-6:]:
    print(f"  {r['timestamp']}: BTC=${r['prices']['bitcoin']['usd']}, ETH=${r['prices']['ethereum']['usd']}")
```

```bash
/cron add "every 1h" "Analyze the price data from the script output. Report:
1. Current prices
2. Trend direction over the last 6 data points (up/down/flat)
3. Any notable movements (>5% change)

If prices are flat and nothing notable, respond with [SILENT].
If there's a significant move, explain what happened." \
  --script ~/.hermes/scripts/collect-prices.py \
  --name "Price tracker" \
  --deliver telegram
```

The script does the mechanical collection; the agent adds the reasoning layer.

---

## Pattern 5: Multi-Skill Workflow

Chain skills together for complex scheduled tasks. Skills are loaded in order before the prompt executes.

```bash
# Use the arxiv skill to find papers, then the obsidian skill to save notes
/cron add "0 8 * * *" "Search arXiv for the 3 most interesting papers on 'language model reasoning' from the past day. For each paper, create an Obsidian note with the title, authors, abstract summary, and key contribution." \
  --skill arxiv \
  --skill obsidian \
  --name "Paper digest"
```

From the tool directly:

```python
cronjob(
    action="create",
    skills=["arxiv", "obsidian"],
    prompt="Search arXiv for papers on 'language model reasoning' from the past day. Save the top 3 as Obsidian notes.",
    schedule="0 8 * * *",
    name="Paper digest",
    deliver="local"
)
```

Skills are loaded in order — `arxiv` first (teaches the agent how to search papers), then `obsidian` (teaches how to write notes). The prompt ties them together.

---

## Managing Your Jobs

```bash
# List all active jobs
/cron list

# Trigger a job immediately (for testing)
/cron run <job_id>

# Pause a job without deleting it
/cron pause <job_id>

# Edit a running job's schedule or prompt
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Updated task description"

# Add or remove skills from an existing job
/cron edit <job_id> --skill arxiv --skill obsidian
/cron edit <job_id> --clear-skills

# Remove a job permanently
/cron remove <job_id>
```

---

## Delivery Targets

The `--deliver` flag controls where results go:

| Target | Example | Use case |
|--------|---------|----------|
| `origin` | `--deliver origin` | Same chat that created the job (default) |
| `local` | `--deliver local` | Save to local file only |
| `telegram` | `--deliver telegram` | Your Telegram home channel |
| `discord` | `--deliver discord` | Your Discord home channel |
| `slack` | `--deliver slack` | Your Slack home channel |
| Specific chat | `--deliver telegram:-1001234567890` | A specific Telegram group |
| Threaded | `--deliver telegram:-1001234567890:17585` | A specific Telegram topic thread |

---

## Tips

**Make prompts self-contained.** The agent in a cron job has no memory of your conversations. Include URLs, repo names, format preferences, and delivery instructions directly in the prompt.

**Use `[SILENT]` deliberately.** For monitoring jobs, include instructions like "if nothing changed, respond with only `[SILENT]`." Do not ask the agent to explain the token in quiet cases — cron treats `[SILENT]` as the delivery-suppression marker.

**Use scripts for data collection.** The `script` parameter lets a Python script handle the boring parts (HTTP requests, file I/O, state tracking). The agent only sees the script's stdout and applies reasoning to it. This is cheaper and more reliable than having the agent do the fetching itself.

**Test with `/cron run`.** Before waiting for the schedule to trigger, use `/cron run <job_id>` to execute immediately and verify the output looks right.

**Schedule expressions.** Supported formats: relative delays (`30m`), intervals (`every 2h`), standard cron expressions (`0 9 * * *`), and ISO timestamps (`2025-06-15T09:00:00`). Natural language like `daily at 9am` is not supported — use `0 9 * * *` instead.

---

*For the complete cron reference — all parameters, edge cases, and internals — see [Scheduled Tasks (Cron)](/user-guide/features/cron).*

---

# SOURCE: website/docs/guides/automation-blueprints.md

---
sidebar_position: 15
title: "Automation Blueprints"
description: "Ready-to-use automation blueprints — scheduled tasks, GitHub event triggers, API webhooks, and multi-skill workflows"
---

# Automation Blueprints

Copy-paste blueprints for common automation patterns. Each blueprint uses Hermes's built-in [cron scheduler](/user-guide/features/cron) for time-based triggers and [webhook platform](/user-guide/messaging/webhooks) for event-driven triggers.

Every blueprint works with **any model** — not locked to a single provider.

For parameterized blueprints with forms instead of cron syntax, see the [Automation Blueprints Catalog](/reference/automation-blueprints-catalog).

:::tip Three Trigger Types
| Trigger | How | Tool |
|---------|-----|------|
| **Schedule** | Runs on a cadence (hourly, nightly, weekly) | `cronjob` tool or `/cron` slash command |
| **GitHub Event** | Fires on PR opens, pushes, issues, CI results | Webhook platform (`hermes webhook subscribe`) |
| **API Call** | External service POSTs JSON to your endpoint | Webhook platform (config.yaml routes or `hermes webhook subscribe`) |

All three support delivery to Telegram, Discord, Slack, SMS, email, GitHub comments, or local files.
:::

---

## Development Workflow

### Nightly Backlog Triage

Label, prioritize, and summarize new issues every night. Delivers a digest to your team channel.

**Trigger:** Schedule (nightly)

```bash
hermes cron create "0 2 * * *" \
  "You are a project manager triaging the NousResearch/hermes-agent GitHub repo.

1. Run: gh issue list --repo NousResearch/hermes-agent --state open --json number,title,labels,author,createdAt --limit 30
2. Identify issues opened in the last 24 hours
3. For each new issue:
   - Suggest a priority label (P0-critical, P1-high, P2-medium, P3-low)
   - Suggest a category label (bug, feature, docs, security)
   - Write a one-line triage note
4. Summarize: total open issues, new today, breakdown by priority

Format as a clean digest. If no new issues, respond with [SILENT]." \
  --name "Nightly backlog triage" \
  --deliver telegram
```

### Automatic PR Code Review

Review every pull request automatically when it's opened. Posts a review comment directly on the PR.

**Trigger:** GitHub webhook

**Option A — Dynamic subscription (CLI):**

```bash
hermes webhook subscribe github-pr-review \
  --events "pull_request" \
  --prompt "Review this pull request:
Repository: {repository.full_name}
PR #{pull_request.number}: {pull_request.title}
Author: {pull_request.user.login}
Action: {action}
Diff URL: {pull_request.diff_url}

Fetch the diff with: curl -sL {pull_request.diff_url}

Review for:
- Security issues (injection, auth bypass, secrets in code)
- Performance concerns (N+1 queries, unbounded loops, memory leaks)
- Code quality (naming, duplication, error handling)
- Missing tests for new behavior

Post a concise review. If the PR is a trivial docs/typo change, say so briefly." \
  --skill github-code-review \
  --deliver github_comment
```

**Option B — Static route (config.yaml):**

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "your-global-secret"
      routes:
        github-pr-review:
          events: ["pull_request"]
          secret: "github-webhook-secret"
          prompt: |
            Review PR #{pull_request.number}: {pull_request.title}
            Repository: {repository.full_name}
            Author: {pull_request.user.login}
            Diff URL: {pull_request.diff_url}
            Review for security, performance, and code quality.
          skills: ["github-code-review"]
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{pull_request.number}"
```

Then in GitHub: **Settings → Webhooks → Add webhook** → Payload URL: `http://your-server:8644/webhooks/github-pr-review`, Content type: `application/json`, Secret: `github-webhook-secret`, Events: **Pull requests**.

### Docs Drift Detection

Weekly scan of merged PRs to find API changes that need documentation updates.

**Trigger:** Schedule (weekly)

```bash
hermes cron create "0 9 * * 1" \
  "Scan the NousResearch/hermes-agent repo for documentation drift.

1. Run: gh pr list --repo NousResearch/hermes-agent --state merged --json number,title,files,mergedAt --limit 30
2. Filter to PRs merged in the last 7 days
3. For each merged PR, check if it modified:
   - Tool schemas (tools/*.py) — may need docs/reference/tools-reference.md update
   - CLI commands (hermes_cli/commands.py, hermes_cli/main.py) — may need docs/reference/cli-commands.md update
   - Config options (hermes_cli/config.py) — may need docs/user-guide/configuration.md update
   - Environment variables — may need docs/reference/environment-variables.md update
4. Cross-reference: for each code change, check if the corresponding docs page was also updated in the same PR

Report any gaps where code changed but docs didn't. If everything is in sync, respond with [SILENT]." \
  --name "Docs drift detection" \
  --deliver telegram
```

### Dependency Security Audit

Daily scan for known vulnerabilities in project dependencies.

**Trigger:** Schedule (daily)

```bash
hermes cron create "0 6 * * *" \
  "Run a dependency security audit on the hermes-agent project.

1. cd ~/.hermes/hermes-agent && source .venv/bin/activate
2. Run: pip audit --format json 2>/dev/null || pip audit 2>&1
3. Run: npm audit --json 2>/dev/null (in website/ directory if it exists)
4. Check for any CVEs with CVSS score >= 7.0

If vulnerabilities found:
- List each one with package name, version, CVE ID, severity
- Check if an upgrade is available
- Note if it's a direct dependency or transitive

If no vulnerabilities, respond with [SILENT]." \
  --name "Dependency audit" \
  --deliver telegram
```

---

## DevOps & Monitoring

### Deploy Verification

Trigger smoke tests after every deployment. Your CI/CD pipeline POSTs to the webhook when a deploy completes.

**Trigger:** API call (webhook)

```bash
hermes webhook subscribe deploy-verify \
  --events "deployment" \
  --prompt "A deployment just completed:
Service: {service}
Environment: {environment}
Version: {version}
Deployed by: {deployer}

Run these verification steps:
1. Check if the service is responding: curl -s -o /dev/null -w '%{http_code}' {health_url}
2. Search recent logs for errors: check the deployment payload for any error indicators
3. Verify the version matches: curl -s {health_url}/version

Report: deployment status (healthy/degraded/failed), response time, any errors found.
If healthy, keep it brief. If degraded or failed, provide detailed diagnostics." \
  --deliver telegram
```

Your CI/CD pipeline triggers it:

```bash
curl -X POST http://your-server:8644/webhooks/deploy-verify \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$(echo -n '{"service":"api","environment":"prod","version":"2.1.0","deployer":"ci","health_url":"https://api.example.com/health"}' | openssl dgst -sha256 -hmac 'your-secret' | cut -d' ' -f2)" \
  -d '{"service":"api","environment":"prod","version":"2.1.0","deployer":"ci","health_url":"https://api.example.com/health"}'
```

### Alert Triage

Correlate monitoring alerts with recent changes to draft a response. Works with Datadog, PagerDuty, Grafana, or any alerting system that can POST JSON.

**Trigger:** API call (webhook)

```bash
hermes webhook subscribe alert-triage \
  --prompt "Monitoring alert received:
Alert: {alert.name}
Severity: {alert.severity}
Service: {alert.service}
Message: {alert.message}
Timestamp: {alert.timestamp}

Investigate:
1. Search the web for known issues with this error pattern
2. Check if this correlates with any recent deployments or config changes
3. Draft a triage summary with:
   - Likely root cause
   - Suggested first response steps
   - Escalation recommendation (P1-P4)

Be concise. This goes to the on-call channel." \
  --deliver slack
```

### Uptime Monitor

Check endpoints every 30 minutes. Only notify when something is down.

**Trigger:** Schedule (every 30 min)

```python title="~/.hermes/scripts/check-uptime.py"
import urllib.request, json, time

ENDPOINTS = [
    {"name": "API", "url": "https://api.example.com/health"},
    {"name": "Web", "url": "https://www.example.com"},
    {"name": "Docs", "url": "https://docs.example.com"},
]

results = []
for ep in ENDPOINTS:
    try:
        start = time.time()
        req = urllib.request.Request(ep["url"], headers={"User-Agent": "Hermes-Monitor/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        results.append({"name": ep["name"], "status": resp.getcode(), "ms": elapsed})
    except Exception as e:
        results.append({"name": ep["name"], "status": "DOWN", "error": str(e)})

down = [r for r in results if r.get("status") == "DOWN" or (isinstance(r.get("status"), int) and r["status"] >= 500)]
if down:
    print("OUTAGE DETECTED")
    for r in down:
        print(f"  {r['name']}: {r.get('error', f'HTTP {r[\"status\"]}')} ")
    print(f"\nAll results: {json.dumps(results, indent=2)}")
else:
    print("NO_ISSUES")
```

```bash
hermes cron create "every 30m" \
  "If the script reports OUTAGE DETECTED, summarize which services are down and suggest likely causes. If NO_ISSUES, respond with [SILENT]." \
  --script ~/.hermes/scripts/check-uptime.py \
  --name "Uptime monitor" \
  --deliver telegram
```

---

## Research & Intelligence

### Competitive Repository Scout

Monitor competitor repos for interesting PRs, features, and architectural decisions.

**Trigger:** Schedule (daily)

```bash
hermes cron create "0 8 * * *" \
  "Scout these AI agent repositories for notable activity in the last 24 hours:

Repos to check:
- anthropics/claude-code
- openai/codex
- All-Hands-AI/OpenHands
- Aider-AI/aider

For each repo:
1. gh pr list --repo <repo> --state all --json number,title,author,createdAt,mergedAt --limit 15
2. gh issue list --repo <repo> --state open --json number,title,labels,createdAt --limit 10

Focus on:
- New features being developed
- Architectural changes
- Integration patterns we could learn from
- Security fixes that might affect us too

Skip routine dependency bumps and CI fixes. If nothing notable, respond with [SILENT].
If there are findings, organize by repo with brief analysis of each item." \
  --skill competitive-pr-scout \
  --name "Competitor scout" \
  --deliver telegram
```

### AI News Digest

Weekly roundup of AI/ML developments.

**Trigger:** Schedule (weekly)

```bash
hermes cron create "0 9 * * 1" \
  "Generate a weekly AI news digest covering the past 7 days:

1. Search the web for major AI announcements, model releases, and research breakthroughs
2. Search for trending ML repositories on GitHub
3. Check arXiv for highly-cited papers on language models and agents

Structure:
## Headlines (3-5 major stories)
## Notable Papers (2-3 papers with one-sentence summaries)
## Open Source (interesting new repos or major releases)
## Industry Moves (funding, acquisitions, launches)

Keep each item to 1-2 sentences. Include links. Total under 600 words." \
  --name "Weekly AI digest" \
  --deliver telegram
```

### Paper Digest with Notes

Daily arXiv scan that saves summaries to your note-taking system.

**Trigger:** Schedule (daily)

```bash
hermes cron create "0 8 * * *" \
  "Search arXiv for the 3 most interesting papers on 'language model reasoning' OR 'tool-use agents' from the past day. For each paper, create an Obsidian note with the title, authors, abstract summary, key contribution, and potential relevance to Hermes Agent development." \
  --skill arxiv --skill obsidian \
  --name "Paper digest" \
  --deliver local
```

---

## GitHub Event Automations

### Issue Auto-Labeling

Automatically label and respond to new issues.

**Trigger:** GitHub webhook

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New GitHub issue received:
Repository: {repository.full_name}
Issue #{issue.number}: {issue.title}
Author: {issue.user.login}
Action: {action}
Body: {issue.body}
Labels: {issue.labels}

If this is a new issue (action=opened):
1. Read the issue title and body carefully
2. Suggest appropriate labels (bug, feature, docs, security, question)
3. If it's a bug report, check if you can identify the affected component from the description
4. Post a helpful initial response acknowledging the issue

If this is a label or assignment change, respond with [SILENT]." \
  --deliver github_comment
```

### CI Failure Analysis

Analyze CI failures and post diagnostics on the PR.

**Trigger:** GitHub webhook

```yaml
# config.yaml route
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        ci-failure:
          events: ["check_run"]
          secret: "ci-secret"
          prompt: |
            CI check failed:
            Repository: {repository.full_name}
            Check: {check_run.name}
            Status: {check_run.conclusion}
            PR: #{check_run.pull_requests.0.number}
            Details URL: {check_run.details_url}

            If conclusion is "failure":
            1. Fetch the log from the details URL if accessible
            2. Identify the likely cause of failure
            3. Suggest a fix
            If conclusion is "success", respond with [SILENT].
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{check_run.pull_requests.0.number}"
```

### Auto-Port Changes Across Repos

When a PR merges in one repo, automatically port the equivalent change to another.

**Trigger:** GitHub webhook

```bash
hermes webhook subscribe auto-port \
  --events "pull_request" \
  --prompt "PR merged in the source repository:
Repository: {repository.full_name}
PR #{pull_request.number}: {pull_request.title}
Author: {pull_request.user.login}
Action: {action}
Merge commit: {pull_request.merge_commit_sha}

If action is 'closed' and pull_request.merged is true:
1. Fetch the diff: curl -sL {pull_request.diff_url}
2. Analyze what changed
3. Determine if this change needs to be ported to the Go SDK equivalent
4. If yes, create a branch, apply the equivalent changes, and open a PR on the target repo
5. Reference the original PR in the new PR description

If action is not 'closed' or not merged, respond with [SILENT]." \
  --skill github-pr-workflow \
  --deliver log
```

---

## Business Operations

### Stripe Payment Monitoring

Track payment events and get summaries of failures.

**Trigger:** API call (webhook)

```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed,charge.dispute.created" \
  --prompt "Stripe event received:
Event type: {type}
Amount: {data.object.amount} cents ({data.object.currency})
Customer: {data.object.customer}
Status: {data.object.status}

For payment_intent.payment_failed:
- Identify the failure reason from {data.object.last_payment_error}
- Suggest whether this is a transient issue (retry) or permanent (contact customer)

For charge.dispute.created:
- Flag as urgent
- Summarize the dispute details

For payment_intent.succeeded:
- Brief confirmation only

Keep responses concise for the ops channel." \
  --deliver slack
```

### Daily Revenue Summary

Compile key business metrics every morning.

**Trigger:** Schedule (daily)

```bash
hermes cron create "0 8 * * *" \
  "Generate a morning business metrics summary.

Search the web for:
1. Current Bitcoin and Ethereum prices
2. S&P 500 status (pre-market or previous close)
3. Any major tech/AI industry news from the last 12 hours

Format as a brief morning briefing, 3-4 bullet points max.
Deliver as a clean, scannable message." \
  --name "Morning briefing" \
  --deliver telegram
```

---

## Multi-Skill Workflows

### Security Audit Pipeline

Combine multiple skills for a comprehensive weekly security review.

**Trigger:** Schedule (weekly)

```bash
hermes cron create "0 3 * * 0" \
  "Run a comprehensive security audit of the hermes-agent codebase.

1. Check for dependency vulnerabilities (pip audit, npm audit)
2. Search the codebase for common security anti-patterns:
   - Hardcoded secrets or API keys
   - SQL injection vectors (string formatting in queries)
   - Path traversal risks (user input in file paths without validation)
   - Unsafe deserialization (pickle.loads, yaml.load without SafeLoader)
3. Review recent commits (last 7 days) for security-relevant changes
4. Check if any new environment variables were added without being documented

Write a security report with findings categorized by severity (Critical, High, Medium, Low).
If nothing found, report a clean bill of health." \
  --skill codebase-security-audit \
  --name "Weekly security audit" \
  --deliver telegram
```

### Content Pipeline

Research, draft, and prepare content on a schedule.

**Trigger:** Schedule (weekly)

```bash
hermes cron create "0 10 * * 3" \
  "Research and draft a technical blog post outline about a trending topic in AI agents.

1. Search the web for the most discussed AI agent topics this week
2. Pick the most interesting one that's relevant to open-source AI agents
3. Create an outline with:
   - Hook/intro angle
   - 3-4 key sections
   - Technical depth appropriate for developers
   - Conclusion with actionable takeaway
4. Save the outline to ~/drafts/blog-$(date +%Y%m%d).md

Keep the outline to ~300 words. This is a starting point, not a finished post." \
  --name "Blog outline" \
  --deliver local
```

---

## Quick Reference

### Cron Schedule Syntax

| Expression | Meaning |
|-----------|---------|
| `every 30m` | Every 30 minutes |
| `every 2h` | Every 2 hours |
| `0 2 * * *` | Daily at 2:00 AM |
| `0 9 * * 1` | Every Monday at 9:00 AM |
| `0 9 * * 1-5` | Weekdays at 9:00 AM |
| `0 3 * * 0` | Every Sunday at 3:00 AM |
| `0 */6 * * *` | Every 6 hours |

### Delivery Targets

| Target | Flag | Notes |
|--------|------|-------|
| Same chat | `--deliver origin` | Default — delivers to where the job was created |
| Local file | `--deliver local` | Saves output, no notification |
| Telegram | `--deliver telegram` | Home channel, or `telegram:CHAT_ID` for specific |
| Discord | `--deliver discord` | Home channel, or `discord:CHANNEL_ID` |
| Slack | `--deliver slack` | Home channel |
| SMS | `--deliver sms:+15551234567` | Direct to phone number |
| Specific thread | `--deliver telegram:-100123:456` | Telegram forum topic |

### Webhook Template Variables

| Variable | Description |
|----------|-------------|
| `{pull_request.title}` | PR title |
| `{issue.number}` | Issue number |
| `{repository.full_name}` | `owner/repo` |
| `{action}` | Event action (opened, closed, etc.) |
| `{__raw__}` | Full JSON payload (truncated at 4000 chars) |
| `{sender.login}` | GitHub user who triggered the event |

### The [SILENT] Pattern

When a cron job's response contains `[SILENT]`, delivery is suppressed. Use this to avoid notification spam on quiet runs:

```
If nothing noteworthy happened, respond with [SILENT].
```

This means you only get notified when the agent has something to report.

---

# SOURCE: website/docs/guides/cron-script-only.md

---
sidebar_position: 13
title: "Script-Only Cron Jobs (No LLM)"
description: "Classic watchdog cron jobs that skip the LLM entirely — a script runs on schedule and its stdout gets delivered to your messaging platform. Memory alerts, disk alerts, CI pings, periodic health checks."
---

# Script-Only Cron Jobs

Sometimes you already know exactly what message you want to send. You don't need an agent to reason about it — you just need a script to run on a timer, and its output (if any) to land in Telegram / Discord / Slack / Signal.

Hermes calls this **no-agent mode**. It's the cron system minus the LLM.

<!-- ascii-guard-ignore -->
```
   ┌──────────────────┐          ┌──────────────────┐
   │ scheduler tick   │  every   │ run script       │
   │ (every N minutes)│ ──────▶ │ (bash or python) │
   └──────────────────┘          └──────────────────┘
                                          │
                                          │ stdout
                                          ▼
                                 ┌──────────────────┐
                                 │ delivery router  │
                                 │ (telegram/disc…) │
                                 └──────────────────┘
```
<!-- ascii-guard-ignore-end -->

- **No LLM call.** Zero tokens, zero agent loop, zero model spend.
- **Script is the job.** The script decides whether to alert. Emit output → message gets sent. Emit nothing → silent tick.
- **Bash or Python.** `.sh` / `.bash` files run under `/bin/bash`; any other extension runs under the current Python interpreter. Anything in `~/.hermes/scripts/` is accepted.
- **Same scheduler.** Lives in `cronjob` alongside LLM jobs — pausing, resuming, listing, logs, and delivery targeting all work the same way.

## When to Use It

Use no-agent mode for:

- **Memory / disk / GPU watchdogs.** Run every 5 minutes, alert only when a threshold is breached.
- **CI hooks.** Deploy finished → post the commit SHA. Build failed → send the last 100 lines of the log.
- **Periodic metrics.** "Daily Stripe revenue at 9am" as a simple API call + pretty-print.
- **External event pollers.** Check an API, alert on state change.
- **Heartbeats.** Ping a dashboard every N minutes to prove the host is alive.

Use a normal (LLM-driven) cron job when you need the agent to **decide** what to say — summarize a long document, pick interesting items from a feed, draft a human-friendly message. The no-agent path is for cases where the script's stdout already IS the message.

## Create One from Chat

The real win of no-agent mode is that the agent itself can set up the watchdog for you — no editor, no shell, no remembering CLI flags. You describe what you want, Hermes writes the script, schedules it, and tells you when it'll fire.

### Example transcript

> **You:** ping me on telegram if RAM is over 85% every 5 minutes
>
> **Hermes:** *(writes `~/.hermes/scripts/memory-watchdog.sh`, then calls `cronjob(...)` with `no_agent=true`)*
>
> Set up. Runs every 5 min, alerts Telegram only when RAM is over 85%. Script: `memory-watchdog.sh`. Job ID: `abc123`.

Under the hood, the agent makes two tool calls:

```python
# 1. Write the check script
write_file(
    path="~/.hermes/scripts/memory-watchdog.sh",
    content='''#!/usr/bin/env bash
ram_pct=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$ram_pct" -ge 85 ]; then
  echo "RAM ${ram_pct}% on $(hostname)"
fi
# Empty stdout = silent tick; no message sent.
''',
)

# 2. Schedule it — no_agent=True skips the LLM on every tick
cronjob(
    action="create",
    schedule="every 5m",
    script="memory-watchdog.sh",
    no_agent=True,
    deliver="telegram",
    name="memory-watchdog",
)
```

From that point on every tick is free: the scheduler runs the script, pipes its stdout to Telegram if non-empty, and never touches a model.

### What the agent decides for you

When you phrase a request like "alert me when X" or "every N minutes check Y and tell me if Z", Hermes' `cronjob` tool description tells it to reach for `no_agent=True` whenever the message content is fully determined by the script. It falls back to the normal LLM-driven path when the request needs reasoning (*"summarize the new issues"*, *"pick the most interesting headlines"*, *"draft a friendly reminder"*).

You don't have to specify `--no-agent` yourself. Just describe the behavior.

### Managing watchdogs from chat

The agent can pause, resume, edit, and remove jobs the same way it creates them:

> **You:** stop the memory watchdog for tonight
>
> **Hermes:** *(calls `cronjob(action='pause', job_id='abc123')`)*
>
> Paused. Resume with "turn it back on" or via `hermes cron resume abc123`.

> **You:** change it to every 15 minutes
>
> **Hermes:** *(calls `cronjob(action='update', job_id='abc123', schedule='every 15m')`)*

The full lifecycle (create / list / update / pause / resume / run-now / remove) is available to the agent without you learning any CLI commands.

## Create One from the CLI

Prefer the shell? The CLI path gives you the same result with three commands:

```bash
# 1. Write your script
cat > ~/.hermes/scripts/memory-watchdog.sh <<'EOF'
#!/usr/bin/env bash
# Alert when RAM usage is over 85%. Silent otherwise.
RAM_PCT=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$RAM_PCT" -ge 85 ]; then
  echo "⚠ RAM ${RAM_PCT}% on $(hostname)"
fi
# Empty stdout = silent run; no message sent.
EOF
chmod +x ~/.hermes/scripts/memory-watchdog.sh

# 2. Schedule it
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"

# 3. Verify
hermes cron list
hermes cron run <job_id>    # fire it once to test
```

That's the whole thing. No prompt, no skill, no model.


## How Script Output Maps to Delivery

| Script behavior | Result |
|-----------------|--------|
| Exit 0, non-empty stdout | stdout is delivered verbatim |
| Exit 0, empty stdout | Silent tick — no delivery |
| Exit 0, stdout contains `{"wakeAgent": false}` on the last line | Silent tick (shared gate with LLM jobs) |
| Non-zero exit code | Error alert is delivered (so a broken watchdog doesn't fail silently) |
| Script timeout | Error alert is delivered |

The "silent when empty" behavior is the key to the classic watchdog pattern: the script is free to run every minute, but the channel only sees a message when something actually needs attention.

## Script Rules

Scripts must live in `~/.hermes/scripts/`. This is enforced at both job-creation time and run time — absolute paths, `~/` expansion, and path-traversal patterns (`../`) are rejected. The same directory is shared with the pre-check script gate used by LLM jobs.

Interpreter choice is by file extension:

| Extension | Interpreter |
|-----------|-------------|
| `.sh`, `.bash` | `/bin/bash` |
| anything else | `sys.executable` (current Python) |

We intentionally do NOT honour `#!/...` shebangs — keeping the interpreter set explicit and small reduces the surface the scheduler trusts.

## Schedule Syntax

Same as all other cron jobs:

```bash
hermes cron create "every 5m"        # interval
hermes cron create "every 2h"
hermes cron create "0 9 * * *"       # standard cron: 9am daily
hermes cron create "30m"             # one-shot: run once in 30 minutes
```

See the [cron feature reference](/user-guide/features/cron) for the full syntax.

## Delivery Targets

`--deliver` accepts everything the gateway knows about. Some common shapes:

```bash
--deliver telegram                       # platform home channel
--deliver telegram:-1001234567890        # specific chat
--deliver telegram:-1001234567890:17585  # specific Telegram forum topic
--deliver discord:#ops
--deliver slack:#engineering
--deliver signal:+15551234567
--deliver local                          # just save to ~/.hermes/cron/output/
```

No running gateway is required at script-run time for bot-token platforms (Telegram, Discord, Slack, Signal, SMS, WhatsApp) — the tool calls each platform's REST endpoint directly using the credentials already in `~/.hermes/.env` / `~/.hermes/config.yaml`.

## Editing and Lifecycle

```bash
hermes cron list                                    # see all jobs
hermes cron pause <job_id>                          # stop firing, keep definition
hermes cron resume <job_id>
hermes cron edit <job_id> --schedule "every 10m"    # adjust cadence
hermes cron edit <job_id> --agent                   # flip to LLM mode
hermes cron edit <job_id> --no-agent --script …     # flip back
hermes cron remove <job_id>                         # delete it
```

Everything that works on LLM jobs (pause, resume, manual trigger, delivery target changes) works on no-agent jobs too.

## Worked Example: Disk Space Alert

```bash
cat > ~/.hermes/scripts/disk-alert.sh <<'EOF'
#!/usr/bin/env bash
# Alert when / or /home is over 90% full.
THRESHOLD=90
df -h / /home 2>/dev/null | awk -v t="$THRESHOLD" '
  NR > 1 && $5+0 >= t {
    printf "⚠ Disk %s full on %s\n", $5, $6
  }
'
EOF
chmod +x ~/.hermes/scripts/disk-alert.sh

hermes cron create "*/15 * * * *" \
  --no-agent \
  --script disk-alert.sh \
  --deliver telegram \
  --name "disk-alert"
```

Silent when both filesystems are under 90%; fires exactly one line per over-threshold filesystem when one fills up.

## Comparison with Other Patterns

| Approach | What runs | When to use |
|----------|-----------|-------------|
| `cronjob --no-agent` (this page) | Your script on Hermes' schedule | Recurring watchdogs / alerts / metrics that don't need reasoning |
| `cronjob` (default, LLM) | Agent with optional pre-check script | When the message content requires reasoning over data |
| OS cron + `curl` to a [webhook subscription](/user-guide/messaging/webhooks) | Your script on the OS schedule | When Hermes might be unhealthy (the thing you're monitoring) |

For critical system-health watchdogs that must fire *even when the gateway is down*, use OS-level cron with a plain `curl` to a Hermes webhook subscription (or any external alerting endpoint) — those run as independent OS processes and don't depend on Hermes being up. The in-gateway scheduler is the right choice when the thing being monitored is external.

## Related

- [Automate Anything with Cron](/guides/automate-with-cron) — LLM-driven cron patterns.
- [Scheduled Tasks (Cron) reference](/user-guide/features/cron) — full schedule syntax, lifecycle, delivery routing.
- [Webhook Subscriptions](/user-guide/messaging/webhooks) — fire-and-forget HTTP entry points for external schedulers.
- [Gateway Internals](/developer-guide/gateway-internals) — delivery-router internals.

---

# SOURCE: website/docs/guides/cron-troubleshooting.md

---
sidebar_position: 12
title: "Cron Troubleshooting"
description: "Diagnose and fix common Hermes cron issues — jobs not firing, delivery failures, skill loading errors, and performance problems"
---

# Cron Troubleshooting

When a cron job isn't behaving as expected, work through these checks in order. Most issues fall into one of four categories: timing, delivery, permissions, or skill loading.

---

## Jobs Not Firing

### Check 1: Verify the job exists and is active

```bash
hermes cron list
```

Look for the job and confirm its state is `[active]` (not `[paused]` or `[completed]`). If it shows `[completed]`, the repeat count may be exhausted — edit the job to reset it.

### Check 2: Confirm the schedule is correct

A misformatted schedule silently defaults to one-shot or is rejected entirely. Test your expression:

| Your expression | Should evaluate to |
|----------------|-------------------|
| `0 9 * * *` | 9:00 AM every day |
| `0 9 * * 1` | 9:00 AM every Monday |
| `every 2h` | Every 2 hours from now |
| `30m` | 30 minutes from now |
| `2025-06-01T09:00:00` | June 1, 2025 at 9:00 AM UTC |

If the job fires once and then disappears from the list, it's a one-shot schedule (`30m`, `1d`, or an ISO timestamp) — expected behavior.

### Check 3: Is the gateway running?

Cron jobs are fired by the gateway's background ticker thread, which ticks every 60 seconds. A regular CLI chat session does **not** automatically fire cron jobs.

If you're expecting jobs to fire automatically, you need a running gateway (`hermes gateway` for foreground, or `hermes gateway start` for the installed service). For one-off debugging, you can manually trigger a tick with `hermes cron tick`.

### Check 4: Check the system clock and timezone

Jobs use the local timezone. If your machine's clock is wrong or in a different timezone than expected, jobs will fire at the wrong times. Verify:

```bash
date
hermes cron list   # Compare next_run times with local time
```

---

## Delivery Failures

### Check 1: Verify the deliver target is correct

Delivery targets are case-sensitive and require the correct platform to be configured. A misconfigured target silently drops the response.

| Target | Requires |
|--------|----------|
| `telegram` | `TELEGRAM_BOT_TOKEN` in `~/.hermes/.env` |
| `discord` | `DISCORD_BOT_TOKEN` in `~/.hermes/.env` |
| `slack` | `SLACK_BOT_TOKEN` in `~/.hermes/.env` |
| `whatsapp` | WhatsApp gateway configured |
| `signal` | Signal gateway configured |
| `matrix` | Matrix homeserver configured |
| `email` | SMTP configured in `config.yaml` |
| `sms` | SMS provider configured |
| `local` | Write access to `~/.hermes/cron/output/` |
| `origin` | Delivers to the chat where the job was created |

Other supported platforms include `mattermost`, `homeassistant`, `dingtalk`, `feishu`, `wecom`, `weixin`, `bluebubbles`, `qqbot`, and `webhook`. You can also target a specific chat with `platform:chat_id` syntax (e.g., `telegram:-1001234567890`).

If delivery fails, the job still runs — it just won't send anywhere. Check `hermes cron list` for updated `last_error` field (if available).

### Check 2: Check `[SILENT]` usage

If your cron job produces no output, delivery is suppressed. If the agent response includes the cron quiet marker `[SILENT]`, delivery is also suppressed. This is intentional for monitoring jobs — but make sure your prompt is not accidentally suppressing everything.

Use prompts like "respond with only [SILENT] if nothing changed." Avoid asking the agent to include `[SILENT]` inside a longer explanation, because cron treats that marker as a suppression signal.

### Check 3: Platform token permissions

Each messaging platform bot needs specific permissions to receive messages. If delivery silently fails:

- **Telegram**: Bot must be an admin in the target group/channel
- **Discord**: Bot must have permission to send in the target channel
- **Slack**: Bot must be added to the workspace and have `chat:write` scope

### Check 4: Response wrapping

By default, cron responses are wrapped with a header and footer (`cron.wrap_response: true` in `config.yaml`). Some platforms or integrations may not handle this well. To disable:

```yaml
cron:
  wrap_response: false
```

---

## Skill Loading Failures

### Check 1: Verify skills are installed

```bash
hermes skills list
```

Skills must be installed before they can be attached to cron jobs. If a skill is missing, install it first with `hermes skills install <skill-name>` or via `/skills` in the CLI.

### Check 2: Check skill name vs. skill folder name

Skill names are case-sensitive and must match the installed skill's folder name. If your job specifies `ai-funding-daily-report` but the skill folder is `ai-funding-daily-report`, confirm the exact name from `hermes skills list`.

### Check 3: Skills that require interactive tools

Cron jobs run with the `cronjob`, `messaging`, and `clarify` toolsets disabled. This prevents recursive cron creation, direct message sending (delivery is handled by the scheduler), and interactive prompts. If a skill relies on these toolsets, it won't work in a cron context.

Check the skill's documentation to confirm it works in non-interactive (headless) mode.

### Check 4: Multi-skill ordering

When using multiple skills, they load in order. If Skill A depends on context from Skill B, make sure B loads first:

```bash
/cron add "0 9 * * *" "..." --skill context-skill --skill target-skill
```

In this example, `context-skill` loads before `target-skill`.

---

## Job Errors and Failures

### Check 1: Review recent job output

If a job ran and failed, you may see error context in:

1. The chat where the job delivers (if delivery succeeded)
2. `~/.hermes/logs/agent.log` for scheduler messages (or `errors.log` for warnings)
3. The job's `last_run` metadata via `hermes cron list`

### Check 2: Common error patterns

**"No such file or directory" for scripts**
The `script` path must be an absolute path (or relative to the Hermes config directory). Verify:
```bash
ls ~/.hermes/scripts/your-script.py   # Must exist
hermes cron edit <job_id> --script ~/.hermes/scripts/your-script.py
```

**"Skill not found" at job execution**
The skill must be installed on the machine running the scheduler. If you move between machines, skills don't automatically sync — reinstall them with `hermes skills install <skill-name>`.

**Job runs but delivers nothing**
Likely a delivery target issue (see Delivery Failures above), no output, or a response containing the cron quiet marker `[SILENT]`.

**Job hangs or times out**
The scheduler uses an inactivity-based timeout (default 600s, configurable via `HERMES_CRON_TIMEOUT` env var, `0` for unlimited). The agent can run as long as it's actively calling tools — the timer only fires after sustained inactivity. Long-running jobs should use scripts to handle data collection and deliver only the result.

### Check 3: Lock contention

The scheduler uses file-based locking to prevent overlapping ticks. If two gateway instances are running (or a CLI session conflicts with a gateway), jobs may be delayed or skipped.

Kill duplicate gateway processes:
```bash
ps aux | grep hermes
# Kill duplicate processes, keep only one
```

### Check 4: Permissions on jobs.json

Jobs are stored in `~/.hermes/cron/jobs.json`. If this file is not readable/writable by your user, the scheduler will fail silently:

```bash
ls -la ~/.hermes/cron/jobs.json
chmod 600 ~/.hermes/cron/jobs.json   # Your user should own it
```

---

## Performance Issues

### Slow job startup

Each cron job creates a fresh AIAgent session, which may involve provider authentication and model loading. For time-sensitive schedules, add buffer time (e.g., `0 8 * * *` instead of `0 9 * * *`).

### Too many overlapping jobs

The scheduler executes jobs sequentially within each tick. If multiple jobs are due at the same time, they run one after another. Consider staggering schedules (e.g., `0 9 * * *` and `5 9 * * *` instead of both at `0 9 * * *`) to avoid delays.

### Large script output

Scripts that dump megabytes of output will slow down the agent and may hit token limits. Filter/summarize at the script level — emit only what the agent needs to reason about.

---

## Diagnostic Commands

```bash
hermes cron list                    # Show all jobs, states, next_run times
hermes cron run <job_id>            # Schedule for next tick (for testing)
hermes cron edit <job_id>           # Fix configuration issues
hermes logs                         # View recent Hermes logs
hermes skills list                  # Verify installed skills
```

---

## Getting More Help

If you've worked through this guide and the issue persists:

1. Run the job with `hermes cron run <job_id>` (fires on next gateway tick) and watch for errors in the chat output
2. Check `~/.hermes/logs/agent.log` for scheduler messages and `~/.hermes/logs/errors.log` for warnings
3. Open an issue at [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) with:
   - The job ID and schedule
   - The delivery target
   - What you expected vs. what happened
   - Relevant error messages from the logs

---

*For the complete cron reference, see [Automate Anything with Cron](/guides/automate-with-cron) and [Scheduled Tasks (Cron)](/user-guide/features/cron).*

---

# SOURCE: website/docs/user-guide/features/goals.md

---
sidebar_position: 16
title: "Persistent Goals"
description: "Set a standing goal and let Hermes keep working across turns until it's done. Our take on the Ralph loop."
---

# Persistent Goals (`/goal`)

`/goal` gives Hermes a standing objective that survives across turns. After every turn a lightweight judge model checks whether the goal is satisfied by the assistant's last response. If not, Hermes automatically feeds a continuation prompt back into the same session and keeps working — until the goal is achieved, you pause or clear it, or the turn budget runs out.

It's our take on the **Ralph loop**, directly inspired by [Codex CLI 0.128.0's `/goal`](https://github.com/openai/codex) by Eric Traut (OpenAI). The core idea — keep a goal alive across turns and don't stop until it's achieved — is theirs. The implementation here is independent and adapted to Hermes' architecture.

## When to use it

Use `/goal` for tasks where you want Hermes to iterate on its own without you re-prompting every turn:

- "Fix every lint error in `src/` and verify `ruff check` passes"
- "Port feature X from repo Y, including tests, and get CI green"
- "Investigate why session IDs sometimes drift on mid-run compression and write up a report"
- "Build a small CLI to rename files by their EXIF dates, then test it against the photos/ folder"

Tasks where the agent does one turn and stops don't need `/goal`. Tasks where *you'd otherwise have to say "keep going" three times* are where this shines.

## Quick start

```
/goal Fix every failing test in tests/hermes_cli/ and make sure scripts/run_tests.sh passes for that directory
```

What you'll see:

1. **Goal accepted** — `⊙ Goal set (20-turn budget): <your goal>`
2. **Turn 1 runs** — Hermes starts working as if you'd sent the goal as a normal message.
3. **Judge runs** — after the turn, the judge model decides `done` or `continue`.
4. **Loop fires if needed** — if `continue`, you'll see `↻ Continuing toward goal (1/20): <judge's reason>` and Hermes takes the next step automatically.
5. **Terminates** — eventually you see either `✓ Goal achieved: <reason>` or `⏸ Goal paused — N/20 turns used`.

## Commands

| Command | What it does |
|---|---|
| `/goal <text>` | Set (or replace) the standing goal. Kicks off the first turn immediately so you don't need to send a separate message. |
| `/goal draft <text>` | Draft a structured completion contract from a plain-language objective, then set it. See [Completion contracts](#completion-contracts). |
| `/goal show` | Print the active goal's completion contract. |
| `/goal` or `/goal status` | Show the current goal, its status, and turns used. |
| `/goal pause` | Stop the auto-continuation loop without clearing the goal. |
| `/goal resume` | Resume the loop (resets the turn counter back to zero). |
| `/goal clear` | Drop the goal entirely. |
| `/goal wait <pid> [reason]` | Park the loop on a background process — it stops re-poking the agent every turn while the process runs, and auto-resumes when it exits. |
| `/goal unwait` | Drop the wait barrier and resume the loop immediately. |

Works identically on the CLI and every gateway platform (Telegram, Discord, Slack, Matrix, Signal, WhatsApp, SMS, iMessage, Webhook, API server, and the web dashboard).

## Completion contracts

A bare `/goal <text>` works fine, but a *vague* goal makes for vague judging — the judge can only check what you told it to want. Codex's `/goal` guidance makes the same point: a durable objective works best when it names **what done means, how to prove it, what not to break, what's in scope, and when to stop**. Hermes adapts this as an optional **completion contract** layered on top of the existing goal loop.

A contract has five fields, all optional:

| Field | Meaning |
|---|---|
| `outcome` | The single end state that must be true when done. |
| `verification` | The specific test / command / artifact that *proves* the outcome. |
| `constraints` | What must not change or regress. |
| `boundaries` | Which files, dirs, tools, or systems are in scope. |
| `stop_when` | The condition under which Hermes should stop and ask for input. |

When a contract is set, both prompts change: the **continuation prompt** tells the agent to target the verification surface and respect the constraints, and the **judge prompt** decides `done` *only when the verification criterion is met with concrete evidence* (a command result, file excerpt, test output) — not a loose "looks done" claim. This directly tightens the most common `/goal` failure mode (premature completion or endless over-continuation on an underspecified objective).

### Two ways to set a contract

**1. Let Hermes draft it** (recommended — adapted from Codex's "let the agent draft the goal" tip):

```
/goal draft Migrate the auth service from session cookies to JWT
```

Hermes expands your one-liner into a full contract via the `goal_judge` auxiliary model, sets it, and shows you the result so you can review or tighten any field. If the aux model is unavailable, it falls back to a plain free-form goal — drafting never blocks setting a goal.

**2. Write it inline** with `field: value` lines:

```
/goal Migrate auth to JWT
verify: pytest tests/auth passes
constraints: keep the /login response shape unchanged
boundaries: only touch services/auth and its tests
stop when: a DB schema migration is required
```

The first non-field line(s) are the goal headline; recognized field prefixes (`verify:`, `verified by:`, `constraints:`, `preserve:`, `boundaries:`, `scope:`, `stop when:`, `blocked:`, …) populate the contract. A plain goal with an incidental colon (`Fix bug: the parser drops commas`) is **not** mangled — only known field prefixes are pulled out.

Use `/goal show` to review the active contract. Contracts persist in `SessionDB.state_meta` alongside the goal, so they survive `/resume`. Old goals from before this feature load unchanged (no contract). Contracts and `/subgoal` criteria compose: subgoals fold into the contract as extra criteria the judge must also satisfy.

## Adding criteria mid-goal: `/subgoal`

While a goal is active you can append extra acceptance criteria with `/subgoal <text>` without resetting the loop. Each call adds one numbered item to the goal's subgoal list; the **continuation prompt** the agent sees on the next turn includes the original goal plus an "Additional criteria the user added mid-loop" block, and the **judge prompt** is rewritten so the verdict must consider every subgoal — the goal isn't marked done until the original objective **and** every subgoal are met.

| Command | What it does |
|---|---|
| `/subgoal <text>` | Append a new criterion to the active goal. Requires an active `/goal`. |
| `/subgoal` (no args) | Show the current numbered subgoal list. |
| `/subgoal remove <N>` | Remove the Nth subgoal (1-based). |
| `/subgoal clear` | Drop every subgoal but keep the original goal intact. |

Subgoals are persisted alongside the goal in `SessionDB.state_meta`, so they survive `/resume`. Setting a new `/goal <text>` replaces the goal and clears the subgoal list; `/goal clear` does the same.

Use this when you start a loop ("fix the failing tests") and notice partway through that you also want it to "and add a regression test for the bug you just patched" — `/subgoal add a regression test` tightens the success criteria without breaking the running loop.

## Parking on a background process: automatic, with a manual override

Some goals are gated on something that takes minutes and runs on its own — CI on a pushed PR, a long build, a test matrix, a deploy, a rate-limit cooldown. Without help, the goal loop would re-poke the agent every turn into "is it done yet?" busy-work while it waits.

**This is handled automatically.** Every turn, the judge is shown the agent's live background processes (the `terminal(background=true)` registry — pid, session id, command, uptime, recent output, and any `watch_patterns` / `notify_on_complete` trigger) alongside the goal and the agent's response. When the agent's progress is genuinely gated on one of them, the judge returns a **`wait`** verdict instead of `continue`, and the loop **parks**: the next turns are skipped (no judge call, no continuation, no turn consumed) until the wait is satisfied — then it resumes normally with the result in hand. The judge can also park on a **time** basis (`wait_for_seconds`) for backoff/cooldown waits. `/goal status` shows `⏳ Goal (parked …)` while parked.

The judge picks the right kind of wait from the process's own signal:

- **`wait_on_session <id>`** — releases when the process's *own trigger* fires: it exits, **or** (if it was started with `watch_patterns`) its pattern matches. This is the one for a long-lived watcher / server / poller that signals **mid-run** (e.g. a build process that prints `BUILD SUCCESSFUL` and keeps running, or a `notify_on_complete` watcher) and may never exit on its own.
- **`wait_on_pid <pid>`** — releases on process exit only.
- **`wait_for_seconds <n>`** — releases after a fixed delay.

You don't type anything for this — it's the judge's decision, made from the process context the loop hands it. The manual commands exist as an override:

| Command | What it does |
|---|---|
| `/goal wait <pid> [reason]` | Manually park the loop until the process with that PID exits. |
| `/goal unwait` | Clear any wait barrier (judge- or manually-set) and resume immediately. |

The barrier (pid- or time-based) is persisted with the goal in `SessionDB.state_meta`, so it survives `/resume`. `/goal pause`, `/goal resume`, and `/goal clear` all drop it. If the PID is already dead when the barrier is set (or dies while parked), or the time deadline passes, the barrier clears on the next check — a stale barrier can never wedge the loop.

Typical flow: the agent pushes a PR, starts a CI watcher with `terminal(background=true, notify_on_complete=true)`, and reports "watching CI." The judge sees the watcher process still running, returns `wait` on its pid, and the loop goes quiet — then picks back up the instant CI finishes and judges the goal against the actual result.

## Behavior details

### The judge

After every turn, Hermes calls an auxiliary model with:

- The standing goal text
- The agent's most recent final response (last ~4 KB of text)
- A system prompt telling the judge to reply with strict JSON: `{"done": <bool>, "reason": "<one-sentence rationale>"}`

The judge is deliberately conservative: it marks a goal `done` only when the response **explicitly** confirms the goal is complete, when the final deliverable is clearly produced, or when the goal is unachievable/blocked (treated as DONE with a block reason so we don't burn budget on impossible tasks).

### Fail-open semantics

If the judge errors (network blip, malformed response, unavailable aux client), Hermes treats the verdict as `continue` — a broken judge never wedges progress. The **turn budget** is the real backstop.

### Turn budget

Default is 20 continuation turns (`goals.max_turns` in `config.yaml`). When the budget is hit, Hermes auto-pauses and tells you exactly how to proceed:

```
⏸ Goal paused — 20/20 turns used. Use /goal resume to keep going, or /goal clear to stop.
```

`/goal resume` resets the counter to zero, so you can keep going in measured chunks.

### User messages always preempt

Any real message you send while a goal is active takes priority over the continuation loop. On the CLI your message lands in `_pending_input` ahead of the queued continuation; on the gateway it goes through the adapter FIFO the same way. The judge runs again after your turn — so if your message happens to complete the goal, the judge will catch it and stop.

### Mid-run safety (gateway)

While an agent is already running, `/goal status`, `/goal pause`, `/goal clear`, `/goal wait`, and `/goal unwait` are safe to run — they only touch control-plane state and don't interrupt the current turn. Setting a **new** goal mid-run (`/goal <new text>`) is rejected with a message telling you to `/stop` first, so the old continuation can't race the new one.

### Persistence

Goal state lives in `SessionDB.state_meta` keyed by `goal:<session_id>`. That means `/resume` picks up right where you left off — set a goal, close your laptop, come back tomorrow, `/resume`, and the goal is still standing exactly as you left it (active, paused, or done).

### Prompt cache

The continuation prompt is a plain user-role message appended to history. It does **not** mutate the system prompt, swap toolsets, or touch the conversation in any way that invalidates Hermes' prompt cache. Running a 20-turn goal costs the same cache-wise as 20 turns of normal conversation.

## Configuration

Add to `~/.hermes/config.yaml`:

```yaml
goals:
  # Max continuation turns before Hermes auto-pauses and asks you to
  # /goal resume. Default 20. Lower this if you want tighter loops;
  # raise it for long-running refactors.
  max_turns: 20
```

### Choosing the judge model

The judge uses the `goal_judge` auxiliary task. By default it resolves to your main model (see [Auxiliary Models](/user-guide/configuration#auxiliary-models)). If you want to route the judge to a cheap fast model to keep costs down, add an override:

```yaml
auxiliary:
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

The judge call is small (~200 output tokens) and runs once per turn, so a cheap fast model is usually the right call.

## Example walkthrough

```
You: /goal Create four files /tmp/note_{1..4}.txt, one per turn, each containing its number as text

  ⊙ Goal set (20-turn budget): Create four files /tmp/note_{1..4}.txt, one per turn, each containing its number as text

Hermes: Creating /tmp/note_1.txt now.
  💻 echo "1" > /tmp/note_1.txt   (0.1s)
  I've created /tmp/note_1.txt with the content "1". I'll continue with the remaining files on the next turn as you specified.

  ↻ Continuing toward goal (1/20): Only 1 of 4 files has been created; 3 files remain.

Hermes: [Continuing toward your standing goal]
  💻 echo "2" > /tmp/note_2.txt   (0.1s)
  Created /tmp/note_2.txt. Two more to go.

  ↻ Continuing toward goal (2/20): 2 of 4 files created; 2 remain.

Hermes: [Continuing toward your standing goal]
  💻 echo "3" > /tmp/note_3.txt   (0.1s)
  Created /tmp/note_3.txt.

  ↻ Continuing toward goal (3/20): 3 of 4 files created; 1 remains.

Hermes: [Continuing toward your standing goal]
  💻 echo "4" > /tmp/note_4.txt   (0.1s)
  All four files have been created: /tmp/note_1.txt through /tmp/note_4.txt, each containing its number.

  ✓ Goal achieved: All four files were created with the specified content, completing the goal.

You: _
```

Four turns, one `/goal` invocation, zero "keep going" prompts from you.

## When the judge gets it wrong

No judge is perfect. Two failure modes to watch for:

**False negative — judge says continue when the goal is actually done.** The turn budget catches this. You'll see `⏸ Goal paused` and can `/goal clear` or just send a new message.

**False positive — judge says done when work remains.** You'll see `✓ Goal achieved` but you know better. Send a follow-up message to continue, or re-set the goal more precisely: `/goal <more specific text>`. The judge's system prompt is deliberately conservative to make false positives rarer than false negatives.

If you find a judge verdict unconvincing, the reason text in the `↻ Continuing toward goal` or `✓ Goal achieved` line tells you exactly what the judge saw. That's usually enough to diagnose whether the goal text was ambiguous or the model's response was.

## Attribution

`/goal` is Hermes' take on the **Ralph loop** pattern. The user-facing design — keep a goal alive across turns, don't stop until it's achieved, with create/pause/resume/clear controls — was popularised and shipped in [Codex CLI 0.128.0](https://github.com/openai/codex) by Eric Traut on OpenAI's Codex team. Our implementation is independent (central `CommandDef` registry, `SessionDB.state_meta` persistence, auxiliary-client judge, adapter-FIFO continuation on the gateway side) but the idea is theirs. Credit where credit's due.

---

# SOURCE: website/docs/user-guide/features/code-execution.md

---
sidebar_position: 8
title: "Code Execution"
description: "Programmatic Python execution with RPC tool access — collapse multi-step workflows into a single turn"
---

# Code Execution (Programmatic Tool Calling)

The `execute_code` tool lets the agent write Python scripts that call Hermes tools programmatically, collapsing multi-step workflows into a single LLM turn. The script runs in a child process on the agent host, communicating with Hermes over a Unix domain socket RPC.

## How It Works

1. The agent writes a Python script using `from hermes_tools import ...`
2. Hermes generates a `hermes_tools.py` stub module with RPC functions
3. Hermes opens a Unix domain socket and starts an RPC listener thread
4. The script runs in a child process — tool calls travel over the socket back to Hermes
5. Only the script's `print()` output is returned to the LLM; intermediate tool results never enter the context window

```python
# The agent can write scripts like:
from hermes_tools import web_search, web_extract

results = web_search("Python 3.13 features", limit=5)
for r in results["data"]["web"]:
    content = web_extract([r["url"]])
    # ... filter and process ...
print(summary)
```

**Available tools inside scripts:** `web_search`, `web_extract`, `read_file`, `write_file`, `search_files`, `patch`, `terminal` (foreground only).

## When the Agent Uses This

The agent uses `execute_code` when there are:

- **3+ tool calls** with processing logic between them
- Bulk data filtering or conditional branching
- Loops over results

The key benefit: intermediate tool results never enter the context window — only the final `print()` output comes back, dramatically reducing token usage.

## Practical Examples

### Data Processing Pipeline

```python
from hermes_tools import search_files, read_file
import json

# Find all config files and extract database settings
matches = search_files("database", path=".", file_glob="*.yaml", limit=20)
configs = []
for match in matches.get("matches", []):
    content = read_file(match["path"])
    configs.append({"file": match["path"], "preview": content["content"][:200]})

print(json.dumps(configs, indent=2))
```

### Multi-Step Web Research

```python
from hermes_tools import web_search, web_extract
import json

# Search, extract, and summarize in one turn
results = web_search("Rust async runtime comparison 2025", limit=5)
summaries = []
for r in results["data"]["web"]:
    page = web_extract([r["url"]])
    for p in page.get("results", []):
        if p.get("content"):
            summaries.append({
                "title": r["title"],
                "url": r["url"],
                "excerpt": p["content"][:500]
            })

print(json.dumps(summaries, indent=2))
```

### Bulk File Refactoring

```python
from hermes_tools import search_files, read_file, patch

# Find all Python files using deprecated API and fix them
matches = search_files("old_api_call", path="src/", file_glob="*.py")
fixed = 0
for match in matches.get("matches", []):
    result = patch(
        path=match["path"],
        old_string="old_api_call(",
        new_string="new_api_call(",
        replace_all=True
    )
    if "error" not in str(result):
        fixed += 1

print(f"Fixed {fixed} files out of {len(matches.get('matches', []))} matches")
```

### Build and Test Pipeline

```python
from hermes_tools import terminal, read_file
import json

# Run tests, parse results, and report
result = terminal("cd /project && python -m pytest --tb=short -q 2>&1", timeout=120)
output = result.get("output", "")

# Parse test output
passed = output.count(" passed")
failed = output.count(" failed")
errors = output.count(" error")

report = {
    "passed": passed,
    "failed": failed,
    "errors": errors,
    "exit_code": result.get("exit_code", -1),
    "summary": output[-500:] if len(output) > 500 else output
}

print(json.dumps(report, indent=2))
```

## Execution Mode

`execute_code` has two execution modes controlled by `code_execution.mode` in `~/.hermes/config.yaml`:

| Mode | Working directory | Python interpreter |
|------|-------------------|--------------------|
| **`project`** (default) | The session's working directory (same as `terminal()`) | Active `VIRTUAL_ENV` / `CONDA_PREFIX` python, falling back to Hermes's own python |
| `strict` | A temp staging directory isolated from the user's project | `sys.executable` (Hermes's own python) |

**When to leave it on `project`:** you want `import pandas`, `from my_project import foo`, or relative paths like `open(".env")` to work the same way they do in `terminal()`. This is almost always what you want.

**When to flip to `strict`:** you need maximum reproducibility — you want the same interpreter every session regardless of which venv the user activated, and you want scripts quarantined from the project tree (no risk of accidentally reading project files through a relative path).

```yaml
# ~/.hermes/config.yaml
code_execution:
  mode: project   # or "strict"
```

Fallback behavior in `project` mode: if `VIRTUAL_ENV` / `CONDA_PREFIX` is unset, broken, or points at a Python older than 3.8, the resolver falls back cleanly to `sys.executable` — it never leaves the agent without a working interpreter.

Security-critical invariants are identical across both modes:

- environment scrubbing (API keys, tokens, credentials stripped)
- tool whitelist (scripts cannot call `execute_code` recursively, `delegate_task`, or MCP tools)
- resource limits (timeout, stdout cap, tool-call cap)

Switching mode changes where scripts run and which interpreter runs them, not what credentials they can see or which tools they can call.

## Resource Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| **Timeout** | 5 minutes (300s) | Script is killed with SIGTERM, then SIGKILL after 5s grace |
| **Stdout** | 50 KB | Output truncated with `[output truncated at 50KB]` notice |
| **Stderr** | 10 KB | Included in output on non-zero exit for debugging |
| **Tool calls** | 50 per execution | Error returned when limit reached |

All limits are configurable via `config.yaml`:

```yaml
# In ~/.hermes/config.yaml
code_execution:
  mode: project      # project (default) | strict
  timeout: 300       # Max seconds per script (default: 300)
  max_tool_calls: 50 # Max tool calls per execution (default: 50)
```

## How Tool Calls Work Inside Scripts

When your script calls a function like `web_search("query")`:

1. The call is serialized to JSON and sent over a Unix domain socket to the parent process
2. The parent dispatches through the standard `handle_function_call` handler
3. The result is sent back over the socket
4. The function returns the parsed result

This means tool calls inside scripts behave identically to normal tool calls — same rate limits, same error handling, same capabilities. The only restriction is that `terminal()` is foreground-only (no `background` or `pty` parameters).

## Error Handling

When a script fails, the agent receives structured error information:

- **Non-zero exit code**: stderr is included in the output so the agent sees the full traceback
- **Timeout**: Script is killed and the agent sees `"Script timed out after 300s and was killed."`
- **Interruption**: If the user sends a new message during execution, the script is terminated and the agent sees `[execution interrupted — user sent a new message]`
- **Tool call limit**: When the 50-call limit is hit, subsequent tool calls return an error message

The response always includes `status` (success/error/timeout/interrupted), `output`, `tool_calls_made`, and `duration_seconds`.

## Security

:::danger Security Model
The child process runs with a **minimal environment**. API keys, tokens, and credentials are stripped by default. The script accesses tools exclusively via the RPC channel — it cannot read secrets from environment variables unless explicitly allowed.
:::

Environment variables containing `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`, `PASSWD`, or `AUTH` in their names are excluded. Only safe system variables (`PATH`, `HOME`, `LANG`, `SHELL`, `PYTHONPATH`, `VIRTUAL_ENV`, etc.) are passed through.

### Skill Environment Variable Passthrough

When a skill declares `required_environment_variables` in its frontmatter, those variables are **automatically passed through** to both `execute_code` and `terminal` child processes after the skill is loaded. This lets skills use their declared API keys without weakening the security posture for arbitrary code.

For non-skill use cases, you can explicitly allowlist variables in `config.yaml`:

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

See the [Security guide](/user-guide/security#environment-variable-passthrough) for full details.

### `HERMES_*` variables in the child

The child process receives only a small, fixed set of operational `HERMES_*`
variables by exact name:

- `HERMES_HOME`
- `HERMES_PROFILE`
- `HERMES_CONFIG`
- `HERMES_ENV`

(plus `HERMES_RPC_DIR` / `HERMES_RPC_SOCKET` / `TZ` / `HOME`, which Hermes
injects explicitly so the RPC channel works).

:::note Behavior change
Earlier versions passed **any** variable whose name began with `HERMES_`
through to the child. That broad prefix was removed for security hardening: it
could leak `HERMES_*`-named configuration that doesn't match a secret substring
(for example `HERMES_BASE_URL`, `HERMES_KANBAN_DB`, or a `HERMES_*_WEBHOOK`
endpoint) into arbitrary sandboxed code.

If an `execute_code` script — or a repo/plugin module it imports at import time
— relied on a `HERMES_*` variable outside the four operational names above, it
will now find that variable **unset** in the child. The drop is intentional,
not a bug.
:::

**Workaround — opt the variable back in explicitly.** Both routes pass the
variable through `execute_code` *and* `terminal` children, and neither weakens
the secret-stripping guarantee (Hermes-managed provider credentials can never
be re-allowed this way):

1. **Per-machine, in `config.yaml`** — add the exact variable name to the
   passthrough allowlist:

   ```yaml
   terminal:
     env_passthrough:
       - HERMES_KANBAN_DB
       - HERMES_BASE_URL
   ```

2. **Per-skill, in the skill's frontmatter** — declare it so it is registered
   automatically whenever that skill is loaded:

   ```yaml
   required_environment_variables:
     - HERMES_KANBAN_DB
   ```

**Diagnosing it.** When the child drops one or more non-allowlisted `HERMES_*`
variables, Hermes emits a one-line `debug` log naming them and pointing at the
`env_passthrough` escape hatch. Run with debug logging (`hermes logs --level
DEBUG`, or check `~/.hermes/logs/agent.log`) and look for
`execute_code: dropped N non-allowlisted HERMES_* var(s)` if a script behaves
as though a `HERMES_*` variable is missing.

Hermes always writes the script and the auto-generated `hermes_tools.py` RPC stub into a temp staging directory that is cleaned up after execution. In `strict` mode the script also *runs* there; in `project` mode it runs in the session's working directory (the staging directory stays on `PYTHONPATH` so imports still resolve). The child process runs in its own process group so it can be cleanly killed on timeout or interruption.

## execute_code vs terminal

| Use Case | execute_code | terminal |
|----------|-------------|----------|
| Multi-step workflows with tool calls between | ✅ | ❌ |
| Simple shell command | ❌ | ✅ |
| Filtering/processing large tool outputs | ✅ | ❌ |
| Running a build or test suite | ❌ | ✅ |
| Looping over search results | ✅ | ❌ |
| Interactive/background processes | ❌ | ✅ |
| Needs API keys in environment | ⚠️ Only via [passthrough](/user-guide/security#environment-variable-passthrough) | ✅ (most pass through) |

**Rule of thumb:** Use `execute_code` when you need to call Hermes tools programmatically with logic between calls. Use `terminal` for running shell commands, builds, and processes.

## Platform Support

Code execution requires Unix domain sockets and is available on **Linux and macOS only**. It is automatically disabled on Windows — the agent falls back to regular sequential tool calls.

---

# SOURCE: website/docs/user-guide/features/delegation.md

---
sidebar_position: 7
title: "Subagent Delegation"
description: "Spawn isolated child agents for parallel workstreams with delegate_task"
---

# Subagent Delegation

The `delegate_task` tool spawns child AIAgent instances with isolated context, restricted toolsets, and their own terminal sessions. Each child gets a fresh conversation and works independently — only its final summary enters the parent's context.

## Single Task

```python
delegate_task(
    goal="Debug why tests fail",
    context="Error: assertion in test_foo.py line 42",
    toolsets=["terminal", "file"]
)
```

## Parallel Batch

Up to 3 concurrent subagents by default (configurable, no hard ceiling):

```python
delegate_task(tasks=[
    {"goal": "Research topic A", "toolsets": ["web"]},
    {"goal": "Research topic B", "toolsets": ["web"]},
    {"goal": "Fix the build", "toolsets": ["terminal", "file"]}
])
```

## How Subagent Context Works

:::warning Critical: Subagents Know Nothing
Subagents start with a **completely fresh conversation**. They have zero knowledge of the parent's conversation history, prior tool calls, or anything discussed before delegation. The subagent's only context comes from the `goal` and `context` fields the parent agent populates when it calls `delegate_task`.
:::

This means the parent agent must pass **everything** the subagent needs in the call:

```python
# BAD - subagent has no idea what "the error" is
delegate_task(goal="Fix the error")

# GOOD - subagent has all context it needs
delegate_task(
    goal="Fix the TypeError in api/handlers.py",
    context="""The file api/handlers.py has a TypeError on line 47:
    'NoneType' object has no attribute 'get'.
    The function process_request() receives a dict from parse_body(),
    but parse_body() returns None when Content-Type is missing.
    The project is at /home/user/myproject and uses Python 3.11."""
)
```

The subagent receives a focused system prompt built from your goal and context, instructing it to complete the task and provide a structured summary of what it did, what it found, any files modified, and any issues encountered.

## Practical Examples

### Parallel Research

Research multiple topics simultaneously and collect summaries:

```python
delegate_task(tasks=[
    {
        "goal": "Research the current state of WebAssembly in 2025",
        "context": "Focus on: browser support, non-browser runtimes, language support",
        "toolsets": ["web"]
    },
    {
        "goal": "Research the current state of RISC-V adoption in 2025",
        "context": "Focus on: server chips, embedded systems, software ecosystem",
        "toolsets": ["web"]
    },
    {
        "goal": "Research quantum computing progress in 2025",
        "context": "Focus on: error correction breakthroughs, practical applications, key players",
        "toolsets": ["web"]
    }
])
```

### Code Review + Fix

Delegate a review-and-fix workflow to a fresh context:

```python
delegate_task(
    goal="Review the authentication module for security issues and fix any found",
    context="""Project at /home/user/webapp.
    Auth module files: src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py.
    The project uses Flask, PyJWT, and bcrypt.
    Focus on: SQL injection, JWT validation, password handling, session management.
    Fix any issues found and run the test suite (pytest tests/auth/).""",
    toolsets=["terminal", "file"]
)
```

### Multi-File Refactoring

Delegate a large refactoring task that would flood the parent's context:

```python
delegate_task(
    goal="Refactor all Python files in src/ to replace print() with proper logging",
    context="""Project at /home/user/myproject.
    Use the 'logging' module with logger = logging.getLogger(__name__).
    Replace print() calls with appropriate log levels:
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"Debug: ...") -> logger.debug(...)
    - Other prints -> logger.info(...)
    Don't change print() in test files or CLI output.
    Run pytest after to verify nothing broke.""",
    toolsets=["terminal", "file"]
)
```

## Batch Mode Details

When you provide a `tasks` array, subagents run in **parallel** using a thread pool:

- **Maximum concurrency:** 3 tasks by default (configurable via `delegation.max_concurrent_children` or the `DELEGATION_MAX_CONCURRENT_CHILDREN` env var; floor of 1, no hard ceiling). Batches larger than the limit return a tool error rather than being silently truncated.
- **Thread pool:** Uses `ThreadPoolExecutor` with the configured concurrency limit as max workers
- **Progress display:** In CLI mode, a tree-view shows tool calls from each subagent in real-time with per-task completion lines. In gateway mode, progress is batched and relayed to the parent's progress callback
- **Result ordering:** Results are sorted by task index to match input order regardless of completion order
- **Interrupt propagation:** Interrupting the parent (e.g., sending a new message) interrupts all active children

Single-task delegation runs directly without thread pool overhead.

## Model Override

You can configure a different model for subagents via `config.yaml` — useful for delegating simple tasks to cheaper/faster models:

```yaml
# In ~/.hermes/config.yaml
delegation:
  model: "google/gemini-flash-2.0"    # Cheaper model for subagents
  provider: "openrouter"              # Optional: route subagents to a different provider
```

If omitted, subagents use the same model as the parent.

## Toolset Selection Tips

The `toolsets` parameter controls what tools the subagent has access to. Choose based on the task:

| Toolset Pattern | Use Case |
|----------------|----------|
| `["terminal", "file"]` | Code work, debugging, file editing, builds |
| `["web"]` | Research, fact-checking, documentation lookup |
| `["terminal", "file", "web"]` | Full-stack tasks (default) |
| `["file"]` | Read-only analysis, code review without execution |
| `["terminal"]` | System administration, process management |

Certain toolsets are blocked for subagents regardless of what you specify:
- `delegation` — blocked for leaf subagents (the default). Retained for `role="orchestrator"` children, bounded by `max_spawn_depth` — see [Depth Limit and Nested Orchestration](#depth-limit-and-nested-orchestration) below.
- `clarify` — subagents cannot interact with the user
- `memory` — no writes to shared persistent memory
- `code_execution` — children should reason step-by-step

## Max Iterations

Each subagent has an iteration limit (default: 50) that controls how many tool-calling turns it can take:

```python
delegate_task(
    goal="Quick file check",
    context="Check if /etc/nginx/nginx.conf exists and print its first 10 lines",
    max_iterations=10  # Simple task, don't need many turns
)
```

## Child Timeout

By default there is **no wall-clock timeout** on subagents. Children fail only from what they're actually doing — API errors, tool errors, or hitting their iteration budget — never from a delegation-level stopwatch. Earlier releases shipped a hard cap (300s, later 600s), which kept killing legitimately busy children mid-task: deep code reviews, large research fan-outs, and slow reasoning models routinely need more than 10 minutes while making steady progress the whole time.

Genuinely stuck children are still detected: the heartbeat staleness monitor stops refreshing the parent's activity when a child makes no progress (no API calls, no tool starts), letting the gateway inactivity timeout fire on a truly wedged worker.

If you want a hard cap anyway (e.g. cost control on unattended cron-driven delegation), opt in per-install:

```yaml
delegation:
  child_timeout_seconds: 0     # default: 0 = no timeout
  # child_timeout_seconds: 1800  # opt-in hard cap (floor 30s)
```

A positive value enforces a hard wall-clock limit on each child; `0` or a negative value disables it.

:::tip Diagnostic dump on zero-call timeout
With a hard cap configured, if a subagent times out having made **zero** API calls (usually: provider unreachable, auth failure, or tool-schema rejection), `delegate_task` writes a structured diagnostic to `~/.hermes/logs/subagent-timeout-<session>-<timestamp>.log` containing the subagent's config snapshot, credential-resolution trace, and any early error messages. Much easier to root-cause than the previous silent-timeout behavior.
:::

## Monitoring Running Subagents (`/agents`)

The TUI ships a `/agents` overlay (alias `/tasks`) that turns recursive `delegate_task` fan-out into a first-class audit surface:

- Live tree view of running and recently-finished subagents, grouped by parent
- Per-branch cost, token, and file-touched rollups
- Kill and pause controls — cancel a specific subagent mid-flight without interrupting its siblings
- Post-hoc review: step through each subagent's turn-by-turn history even after they've returned to the parent

The classic CLI just prints `/agents` as a text summary; the TUI is where the overlay shines. See [TUI — Slash commands](/user-guide/tui#slash-commands).

## Depth Limit and Nested Orchestration

By default, delegation is **flat**: a parent (depth 0) spawns children (depth 1), and those children cannot delegate further. This prevents runaway recursive delegation.

For multi-stage workflows (research → synthesis, or parallel orchestration over sub-problems), a parent can spawn **orchestrator** children that *can* delegate their own workers:

```python
delegate_task(
    goal="Survey three code review approaches and recommend one",
    role="orchestrator",  # Allows this child to spawn its own workers
    context="...",
)
```

- `role="leaf"` (default): child cannot delegate further — identical to the flat-delegation behavior.
- `role="orchestrator"`: child retains the `delegation` toolset. Gated by `delegation.max_spawn_depth` (default **1** = flat, so `role="orchestrator"` is a no-op at defaults). Raise `max_spawn_depth` to 2 to allow orchestrator children to spawn leaf grandchildren; 3+ for deeper trees. There is no upper ceiling — cost is the practical limit.
- `delegation.orchestrator_enabled: false`: global kill switch that forces every child to `leaf` regardless of the `role` parameter.

**Cost warning:** With `max_spawn_depth: 3` and `max_concurrent_children: 3`, the tree can reach 3×3×3 = 27 concurrent leaf agents. Each extra level multiplies spend — raise `max_spawn_depth` intentionally.

## Lifetime and Durability

:::warning delegate_task is synchronous — not durable
`delegate_task` runs **inside the parent's current turn**. It blocks the parent until every child finishes (or is cancelled). It is **not** a background job queue:

- If the parent is interrupted (user sends a new message, `/stop`, `/new`), all active children are cancelled and return `status="interrupted"`. Their in-progress work is discarded.
- Children do **not** continue running after the parent turn ends.
- Cancelled children return a structured result (`status="interrupted"`, `exit_reason="interrupted"`), but because the parent was interrupted too, that result often never makes it into a user-visible reply.

For **durable long-running work** that must survive interrupts or outlive the current turn, use:

- `cronjob` (action=`create`) — schedules a separate agent run; immune to parent-turn interrupts.
- `terminal(background=True, notify_on_complete=True)` — long-running shell commands that keep running while the agent does other things.
:::

## Key Properties

- Each subagent gets its **own terminal session** (separate from the parent)
- **Nested delegation is opt-in** — only `role="orchestrator"` children can delegate further, and only when `max_spawn_depth` is raised from its default of 1 (flat). Disable globally with `orchestrator_enabled: false`.
- Leaf subagents **cannot** call: `delegate_task`, `clarify`, `memory`, `execute_code`. Orchestrator subagents retain `delegate_task` but still cannot use the other three.
- **Interrupt propagation** — interrupting the parent interrupts all active children (including grandchildren under orchestrators)
- Only the final summary enters the parent's context, keeping token usage efficient
- Subagents inherit the parent's **API key, provider configuration, and credential pool** (enabling key rotation on rate limits)

## Delegation vs execute_code

| Factor | delegate_task | execute_code |
|--------|--------------|-------------|
| **Reasoning** | Full LLM reasoning loop | Just Python code execution |
| **Context** | Fresh isolated conversation | No conversation, just script |
| **Tool access** | All non-blocked tools with reasoning | 7 tools via RPC, no reasoning |
| **Parallelism** | 3 concurrent subagents by default (configurable) | Single script |
| **Best for** | Complex tasks needing judgment | Mechanical multi-step pipelines |
| **Token cost** | Higher (full LLM loop) | Lower (only stdout returned) |
| **User interaction** | None (subagents can't clarify) | None |

**Rule of thumb:** Use `delegate_task` when the subtask requires reasoning, judgment, or multi-step problem solving. Use `execute_code` when you need mechanical data processing or scripted workflows.

## Configuration

```yaml
# In ~/.hermes/config.yaml
delegation:
  max_iterations: 50                        # Max turns per child (default: 50)
  # max_concurrent_children: 3              # Parallel children per batch (default: 3)
  # max_spawn_depth: 1                      # Tree depth (floor 1, no ceiling, default 1 = flat). Raise to 2 to allow orchestrator children to spawn leaves; 3+ for deeper trees.
  # orchestrator_enabled: true              # Disable to force all children to leaf role.
  model: "google/gemini-3-flash-preview"             # Optional provider/model override
  provider: "openrouter"                             # Optional built-in provider
  api_mode: anthropic_messages                       # optional; auto-detected from base_url for anthropic_messages endpoints

# Or use a direct custom endpoint instead of provider:
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
  # api_mode: "anthropic_messages"  # Optional. Wire protocol override for base_url ("chat_completions", "codex_responses", or "anthropic_messages"). Empty = auto-detect from URL (e.g. /anthropic suffix). Set explicitly for endpoints the heuristic can't classify (Azure AI Foundry, MiniMax, Zhipu GLM, LiteLLM proxies, …).
```

When `base_url` points at an Anthropic-compatible endpoint — for example a path ending in `/anthropic`, an Azure Foundry Claude route, or a MiniMax `/anthropic` proxy — `api_mode` is auto-detected as `anthropic_messages` so the subagent uses the right wire format without you setting anything. Set `api_mode` explicitly when the auto-detection guess is wrong (rare).

:::tip
The agent handles delegation automatically based on the task complexity. You don't need to explicitly ask it to delegate — it will do so when it makes sense.
:::

---

# SOURCE: website/docs/guides/delegation-patterns.md

---
sidebar_position: 13
title: "Delegation & Parallel Work"
description: "When and how to use subagent delegation — patterns for parallel research, code review, and multi-file work"
---

# Delegation & Parallel Work

Hermes can spawn isolated child agents to work on tasks in parallel. Each subagent gets its own conversation, terminal session, and toolset. Only the final summary comes back — intermediate tool calls never enter your context window.

For the full feature reference, see [Subagent Delegation](/user-guide/features/delegation).

---

## When to Delegate

**Good candidates for delegation:**
- Reasoning-heavy subtasks (debugging, code review, research synthesis)
- Tasks that would flood your context with intermediate data
- Parallel independent workstreams (research A and B simultaneously)
- Fresh-context tasks where you want the agent to approach without bias

**Use something else:**
- Single tool call → just use the tool directly
- Mechanical multi-step work with logic between steps → `execute_code`
- Tasks needing user interaction → subagents can't use `clarify`
- Quick file edits → do them directly
- Durable long-running work that must outlive the current turn → `cronjob` or `terminal(background=True, notify_on_complete=True)`. `delegate_task` is **synchronous**: if the parent turn is interrupted, active children are cancelled and their work is discarded.

---

## Pattern: Parallel Research

Research three topics simultaneously and get structured summaries back:

```
Research these three topics in parallel:
1. Current state of WebAssembly outside the browser
2. RISC-V server chip adoption in 2025
3. Practical quantum computing applications

Focus on recent developments and key players.
```

Behind the scenes, Hermes uses:

```python
delegate_task(tasks=[
    {
        "goal": "Research WebAssembly outside the browser in 2025",
        "context": "Focus on: runtimes (Wasmtime, Wasmer), cloud/edge use cases, WASI progress",
        "toolsets": ["web"]
    },
    {
        "goal": "Research RISC-V server chip adoption",
        "context": "Focus on: server chips shipping, cloud providers adopting, software ecosystem",
        "toolsets": ["web"]
    },
    {
        "goal": "Research practical quantum computing applications",
        "context": "Focus on: error correction breakthroughs, real-world use cases, key companies",
        "toolsets": ["web"]
    }
])
```

All three run concurrently. Each subagent searches the web independently and returns a summary. The parent agent then synthesizes them into a coherent briefing.

---

## Pattern: Code Review

Delegate a security review to a fresh-context subagent that approaches the code without preconceptions:

```
Review the authentication module at src/auth/ for security issues.
Check for SQL injection, JWT validation problems, password handling,
and session management. Fix anything you find and run the tests.
```

The key is the `context` field — it must include everything the subagent needs:

```python
delegate_task(
    goal="Review src/auth/ for security issues and fix any found",
    context="""Project at /home/user/webapp. Python 3.11, Flask, PyJWT, bcrypt.
    Auth files: src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py
    Test command: pytest tests/auth/ -v
    Focus on: SQL injection, JWT validation, password hashing, session management.
    Fix issues found and verify tests pass.""",
    toolsets=["terminal", "file"]
)
```

:::warning The Context Problem
Subagents know **absolutely nothing** about your conversation. They start completely fresh. If you delegate "fix the bug we were discussing," the subagent has no idea what bug you mean. Always pass file paths, error messages, project structure, and constraints explicitly.
:::

---

## Pattern: Compare Alternatives

Evaluate multiple approaches to the same problem in parallel, then pick the best:

```
I need to add full-text search to our Django app. Evaluate three approaches
in parallel:
1. PostgreSQL tsvector (built-in)
2. Elasticsearch via django-elasticsearch-dsl
3. Meilisearch via meilisearch-python

For each: setup complexity, query capabilities, resource requirements,
and maintenance overhead. Compare them and recommend one.
```

Each subagent researches one option independently. Because they're isolated, there's no cross-contamination — each evaluation stands on its own merits. The parent agent gets all three summaries and makes the comparison.

---

## Pattern: Multi-File Refactoring

Split a large refactoring task across parallel subagents, each handling a different part of the codebase:

```python
delegate_task(tasks=[
    {
        "goal": "Refactor all API endpoint handlers to use the new response format",
        "context": """Project at /home/user/api-server.
        Files: src/handlers/users.py, src/handlers/auth.py, src/handlers/billing.py
        Old format: return {"data": result, "status": "ok"}
        New format: return APIResponse(data=result, status=200).to_dict()
        Import: from src.responses import APIResponse
        Run tests after: pytest tests/handlers/ -v""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Update all client SDK methods to handle the new response format",
        "context": """Project at /home/user/api-server.
        Files: sdk/python/client.py, sdk/python/models.py
        Old parsing: result = response.json()["data"]
        New parsing: result = response.json()["data"] (same key, but add status code checking)
        Also update sdk/python/tests/test_client.py""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Update API documentation to reflect the new response format",
        "context": """Project at /home/user/api-server.
        Docs at: docs/api/. Format: Markdown with code examples.
        Update all response examples from old format to new format.
        Add a 'Response Format' section to docs/api/overview.md explaining the schema.""",
        "toolsets": ["terminal", "file"]
    }
])
```

:::tip
Each subagent gets its own terminal session. They can work on the same project directory without stepping on each other — as long as they're editing different files. If two subagents might touch the same file, handle that file yourself after the parallel work completes.
:::

---

## Pattern: Gather Then Analyze

Use `execute_code` for mechanical data gathering, then delegate the reasoning-heavy analysis:

```python
# Step 1: Mechanical gathering (execute_code is better here — no reasoning needed)
execute_code("""
from hermes_tools import web_search, web_extract

results = []
for query in ["AI funding Q1 2026", "AI startup acquisitions 2026", "AI IPOs 2026"]:
    r = web_search(query, limit=5)
    for item in r["data"]["web"]:
        results.append({"title": item["title"], "url": item["url"], "desc": item["description"]})

# Extract full content from top 5 most relevant
urls = [r["url"] for r in results[:5]]
content = web_extract(urls)

# Save for the analysis step
import json
with open("/tmp/ai-funding-data.json", "w") as f:
    json.dump({"search_results": results, "extracted": content["results"]}, f)
print(f"Collected {len(results)} results, extracted {len(content['results'])} pages")
""")

# Step 2: Reasoning-heavy analysis (delegation is better here)
delegate_task(
    goal="Analyze AI funding data and write a market report",
    context="""Raw data at /tmp/ai-funding-data.json contains search results and
    extracted web pages about AI funding, acquisitions, and IPOs in Q1 2026.
    Write a structured market report: key deals, trends, notable players,
    and outlook. Focus on deals over $100M.""",
    toolsets=["terminal", "file"]
)
```

This is often the most efficient pattern: `execute_code` handles the 10+ sequential tool calls cheaply, then a subagent does the single expensive reasoning task with a clean context.

---

## Toolset Selection

Choose toolsets based on what the subagent needs:

| Task type | Toolsets | Why |
|-----------|----------|-----|
| Web research | `["web"]` | web_search + web_extract only |
| Code work | `["terminal", "file"]` | Shell access + file operations |
| Full-stack | `["terminal", "file", "web"]` | Everything except messaging |
| Read-only analysis | `["file"]` | Can only read files, no shell |

Restricting toolsets keeps the subagent focused and prevents accidental side effects (like a research subagent running shell commands).

---

## Constraints

- **Default 3 parallel tasks**: batches default to 3 concurrent subagents (configurable via `delegation.max_concurrent_children` in config.yaml, no hard ceiling, only a floor of 1)
- **Nested delegation is opt-in**: leaf subagents (default) cannot call `delegate_task`, `clarify`, `memory`, or `execute_code`. Orchestrator subagents (`role="orchestrator"`) retain `delegate_task` for further delegation, but only when `delegation.max_spawn_depth` is raised above the default of 1 (floor 1, no ceiling); the other three remain blocked. Disable globally via `delegation.orchestrator_enabled: false`.

### Tuning Concurrency and Depth

| Config | Default | Range | Effect |
|--------|---------|-------|--------|
| `max_concurrent_children` | 3 | >=1 | Parallel batch size per `delegate_task` call |
| `max_spawn_depth` | 1 | >=1 | How many delegation levels can spawn further |

Example: running 30 parallel workers with nested subagents:

```yaml
delegation:
  max_concurrent_children: 30
  max_spawn_depth: 2
```

- **Separate terminals** — each subagent gets its own terminal session with separate working directory and state
- **No conversation history** — subagents see only the `goal` and `context` the parent agent passes when calling `delegate_task`
- **Default 50 iterations** — set `max_iterations` lower for simple tasks to save cost
- **Not durable** — `delegate_task` is synchronous and runs inside the parent turn. If the parent is interrupted (new user message, `/stop`, `/new`), all active children are cancelled (`status="interrupted"`) and their work is discarded. For work that must outlive the current turn, use `cronjob` or `terminal(background=True, notify_on_complete=True)`.

---

## Tips

**Be specific in goals.** "Fix the bug" is too vague. "Fix the TypeError in api/handlers.py line 47 where process_request() receives None from parse_body()" gives the subagent enough to work with.

**Include file paths.** Subagents don't know your project structure. Always include absolute paths to relevant files, the project root, and the test command.

**Use delegation for context isolation.** Sometimes you want a fresh perspective. Delegating forces you to articulate the problem clearly, and the subagent approaches it without the assumptions that built up in your conversation.

**Check results.** Subagent summaries are just that — summaries. If a subagent says "fixed the bug and tests pass," verify by running the tests yourself or reading the diff.

---

*For the complete delegation reference — all parameters, ACP integration, and advanced configuration — see [Subagent Delegation](/user-guide/features/delegation).*
