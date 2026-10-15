<!-- Sections in this file (in order):
  - user-guide/profiles.md
  - user-guide/profile-distributions.md
  - user-guide/multi-profile-gateways.md
-->


---

# SOURCE: website/docs/user-guide/profiles.md

---
sidebar_position: 2
---

# Profiles: Running Multiple Agents

Run multiple independent Hermes agents on the same machine — each with its own config, API keys, memory, sessions, skills, and gateway state.

## What are profiles?

A profile is a separate Hermes home directory. Each profile gets its own directory containing its own `config.yaml`, `.env`, `SOUL.md`, memories, sessions, skills, cron jobs, and state database. Profiles let you run separate agents for different purposes — a coding assistant, a personal bot, a research agent — without mixing up Hermes state.

When you create a profile, it automatically becomes its own command. Create a profile called `coder` and you immediately have `coder chat`, `coder setup`, `coder gateway start`, etc.

## Quick start

```bash
hermes profile create coder       # creates profile + "coder" command alias
coder setup                       # configure API keys and model
coder chat                        # start chatting
```

That's it. `coder` is now its own Hermes profile with its own config, memory, and state.

## Creating a profile

:::tip
Quickest setup: run `hermes setup --portal` inside the new profile to wire up models + tools at once. See [Nous Portal](/integrations/nous-portal).
:::

### Blank profile

```bash
hermes profile create mybot
```

Creates a fresh profile with bundled skills seeded. Run `mybot setup` to configure API keys, model, and gateway tokens.

If you plan to use this profile as a kanban worker (or want the kanban orchestrator to route work to it), pass `--description "<role>"` at create time so the orchestrator knows what it's good at:

```bash
hermes profile create researcher --description "Reads source code and external docs, writes findings."
```

You can also set or auto-generate the description later with `hermes profile describe` — see the [Kanban guide](./features/kanban#auto-vs-manual-orchestration) for the full routing model.

### Clone config only (`--clone`)

```bash
hermes profile create work --clone
```

Copies your current profile's `config.yaml`, `.env`, `SOUL.md`, and skills into the new profile. Same API keys, model, and capabilities, but fresh sessions and memory. Edit `~/.hermes/profiles/work/.env` for different API keys, or `~/.hermes/profiles/work/SOUL.md` for a different personality.

### Clone everything (`--clone-all`)

```bash
hermes profile create backup --clone-all
```

Copies **everything** — config, API keys, personality, all memories, skills, cron jobs, plugins. A complete working snapshot. Per-profile history is excluded (session history, `state.db`, `backups/`, `state-snapshots/`, `checkpoints/`) — these belong to the source profile and can reach tens of GB. For a full backup including history, use `hermes profile export` or `hermes backup` instead.

### Clone from a specific profile

```bash
hermes profile create work --clone-from coder
```

`--clone-from <source>` selects the source profile directly and implies a config/skills/SOUL clone. Combine it with `--clone-all` when you want a full copy of that source profile:

```bash
hermes profile create work-backup --clone-from coder --clone-all
```

:::tip Honcho memory + profiles
When Honcho is enabled, clone operations automatically create a dedicated AI peer for the new profile while sharing the same user workspace. Each profile builds its own observations and identity. See [Honcho -- Multi-agent / Profiles](./features/memory-providers.md#honcho) for details.
:::

## Using profiles

### Command aliases

Every profile automatically gets a command alias at `~/.local/bin/<name>`:

```bash
coder chat                    # chat with the coder agent
coder setup                   # configure coder's settings
coder gateway start           # start coder's gateway
coder doctor                  # check coder's health
coder skills list             # list coder's skills
coder config set model.default anthropic/claude-sonnet-4
```

The alias works with every hermes subcommand — it's just `hermes -p <name>` under the hood.

### The `-p` flag

You can also target a profile explicitly with any command:

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # works in any position
```

### Sticky default (`hermes profile use`)

```bash
hermes profile use coder
hermes chat                   # now targets coder
hermes tools                  # configures coder's tools
hermes profile use default    # switch back
```

Sets a default so plain `hermes` commands target that profile. Like `kubectl config use-context`.

### Knowing where you are

The CLI always shows which profile is active:

- **Prompt**: `coder ❯` instead of `❯`
- **Banner**: Shows `Profile: coder` on startup
- **`hermes profile`**: Shows current profile name, path, model, gateway status

## Profiles vs workspaces vs sandboxing

Profiles are often confused with workspaces or sandboxes, but they are different things:

- A **profile** gives Hermes its own state directory: `config.yaml`, `.env`, `SOUL.md`, sessions, memory, logs, cron jobs, and gateway state.
- A **workspace** or **working directory** is where terminal commands start. That is controlled separately by `terminal.cwd`.
- A **sandbox** is what limits filesystem access. Profiles do **not** sandbox the agent.

On the default `local` terminal backend, the agent still has the same filesystem access as your user account. A profile does not stop it from accessing folders outside the profile directory.

If you want a profile to start in a specific project folder, set an explicit absolute `terminal.cwd` in that profile's `config.yaml`:

```yaml
terminal:
  backend: local
  cwd: /absolute/path/to/project
```

Using `cwd: "."` on the local backend means "the directory Hermes was launched from", not "the profile directory".

Also note:

- `SOUL.md` can guide the model, but it does not enforce a workspace boundary.
- Changes to `SOUL.md` take effect cleanly on a new session. Existing sessions may still be using the old prompt state.
- Asking the model "what directory are you in?" is not a reliable isolation test. If you need a predictable starting directory for tools, set `terminal.cwd` explicitly.

## Running gateways

Each profile runs its own gateway as a separate process with its own bot token:

```bash
coder gateway start           # starts coder's gateway
assistant gateway start       # starts assistant's gateway (separate process)
```

### Different bot tokens

Each profile has its own `.env` file. Configure a different Telegram/Discord/Slack bot token in each:

```bash
# Edit coder's tokens
nano ~/.hermes/profiles/coder/.env

# Edit assistant's tokens
nano ~/.hermes/profiles/assistant/.env
```

### Safety: token locks

If two profiles accidentally use the same bot token, the second gateway will be blocked with a clear error naming the conflicting profile. Supported for Telegram, Discord, Slack, WhatsApp, and Signal.

### Persistent services

```bash
coder gateway install         # creates hermes-gateway-coder systemd/launchd service
assistant gateway install     # creates hermes-gateway-assistant service
```

Each profile gets its own service name. They run independently.

:::note Inside the official Docker image
Per-profile gateways are supervised by [s6-overlay](https://github.com/just-containers/s6-overlay) (PID 1 in the container), so `hermes profile create <name>` automatically registers an s6 service slot at `/run/service/gateway-<name>/`. `hermes -p <name> gateway start/stop/restart` dispatches to `s6-svc` instead of spawning a bare process — crashes are auto-restarted and `docker restart` preserves the previously-running set of gateways. See [Per-profile gateway supervision](/user-guide/docker#per-profile-gateway-supervision) for details.
:::

## Configuring profiles

Each profile has its own:

- **`config.yaml`** — model, provider, toolsets, all settings
- **`.env`** — API keys, bot tokens
- **`SOUL.md`** — personality and instructions

```bash
coder config set model.default anthropic/claude-sonnet-4
echo "You are a focused coding assistant." > ~/.hermes/profiles/coder/SOUL.md
```

If you want this profile to work in a specific project by default, also set its own `terminal.cwd`:

```bash
coder config set terminal.cwd /absolute/path/to/project
```

### From the dashboard

The [web dashboard](features/web-dashboard.md#managing-multiple-profiles)
is a machine-level surface that can manage **any** profile's config, API
keys, skills, MCPs, and model via the profile switcher in its sidebar — no
per-profile dashboard needed. `coder dashboard` routes to the machine
dashboard with the `coder` profile preselected. The dashboard's Chat tab
also follows the switcher, spawning a conversation under the selected
profile's home.

Note: "Set as active" on the dashboard's Profiles page is the sticky
default for **future CLI/gateway runs** (same as `hermes profile use`) —
to edit a profile from the dashboard, use the switcher instead.

## Updating

`hermes update` pulls code once (shared) and syncs new bundled skills to **all** profiles automatically:

```bash
hermes update
# → Code updated (12 commits)
# → Skills synced: default (up to date), coder (+2 new), assistant (+2 new)
```

User-modified skills are never overwritten.

## Managing profiles

```bash
hermes profile list           # show all profiles with status
hermes profile show coder     # detailed info for one profile
hermes profile rename coder dev-bot   # rename (updates alias + service)
hermes profile export coder   # export to coder.tar.gz
hermes profile import coder.tar.gz   # import from archive
```

## Deleting a profile

```bash
hermes profile delete coder
```

This stops the gateway, removes the systemd/launchd service, removes the command alias, and deletes all profile data. You'll be asked to type the profile name to confirm.

Use `--yes` to skip confirmation: `hermes profile delete coder --yes`

:::note
You cannot delete the default profile (`~/.hermes`). To remove everything, use `hermes uninstall`.
:::

## Tab completion

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

Add the line to your `~/.bashrc` or `~/.zshrc` for persistent completion. Completes profile names after `-p`, profile subcommands, and top-level commands.

## How it works

Profiles use the `HERMES_HOME` environment variable. When you run `coder chat`, the wrapper script sets `HERMES_HOME=~/.hermes/profiles/coder` before launching hermes. Since 119+ files in the codebase resolve paths via `get_hermes_home()`, Hermes state automatically scopes to the profile's directory — config, sessions, memory, skills, state database, gateway PID, logs, and cron jobs.

This is separate from terminal working directory. Tool execution starts from `terminal.cwd` (or the launch directory when `cwd: "."` on the local backend), not automatically from `HERMES_HOME`.

On host installs, tool subprocesses keep your real OS-user `HOME` by default so
existing CLI credentials under `~` keep working across profiles. Profile data is
isolated by `HERMES_HOME`, not by changing `HOME`. Container backends still use
`{HERMES_HOME}/home` for persistent tool state, and host users who need strict
per-profile tool config can opt in with `terminal.home_mode: profile`.

This means two things that are easy to mix up:

- `HERMES_HOME` is the profile boundary. It controls Hermes config, `.env`,
  memory, sessions, skills, logs, cron jobs, gateway state, and other Hermes
  data.
- `HOME` is the operating-system/user home that external CLIs expect. On host
  installs, Hermes keeps it as the real user home by default so tools like
  `git`, `ssh`, `gh`, `az`, `npm`, Claude Code, and Codex find the same
  credentials they use in your normal shell.

The tradeoff is that host profiles share normal user-level CLI state by default.
If you need separate CLI identities per profile, set `terminal.home_mode:
profile` in that profile's `config.yaml`. In that mode Hermes launches tool
subprocesses with `HOME={HERMES_HOME}/home`; you then need to initialize or link
the profile-specific `~/.ssh`, `~/.gitconfig`, `~/.config/gh`, cloud CLI auth,
Claude/Codex auth, npm state, and similar files inside that profile home.

Hermes also exposes `HERMES_REAL_HOME` to subprocesses so scripts can still find
the actual account home when `home_mode: profile` is active.

The default profile is simply `~/.hermes` itself. No migration needed — existing installs work identically.

## Sharing profiles as distributions

A profile you built on one machine can be packaged as a **git repository** and installed with one command on another machine — your own workstation, a teammate's laptop, or a community user's environment. The shared package includes the SOUL, config, skills, cron jobs, and MCP connections. Credentials, memories, and sessions stay per-machine.

```bash
# Install a whole agent from a git repo
hermes profile install github.com/you/research-bot --alias

# Update later when the author ships a new version (keeps your memories + .env)
hermes profile update research-bot
```

See **[Profile Distributions: Share a Whole Agent](./profile-distributions.md)** for the full guide — authoring, publishing, update semantics, security model, and use cases.

---

# SOURCE: website/docs/user-guide/profile-distributions.md

---
sidebar_position: 3
---

# Profile Distributions: Share a Whole Agent

A **profile distribution** packages a complete Hermes agent — personality, skills, cron jobs, MCP connections, config — as a git repository. Anyone with access to the repo can install the whole agent with one command, update it in place, and keep their own memories, sessions, and API keys untouched.

If a [profile](./profiles.md) is a local agent, a distribution is that agent made shareable.

## What this means

Before distributions, sharing a Hermes agent meant sending someone:

1. Your SOUL.md
2. A list of skills to install
3. Your config.yaml, minus the secrets
4. A description of which MCP servers you wired up
5. Any cron jobs you scheduled
6. Instructions for which env vars to set

…and hoping they assembled it correctly. Every version bump or bug fix meant repeating the handoff.

With distributions, all of that lives in one git repo:

```
my-research-agent/
├── distribution.yaml    # manifest: name, version, env-var requirements
├── SOUL.md              # the agent's personality / system prompt
├── config.yaml          # model, temperature, reasoning, tool defaults
├── skills/              # bundled skills that come with the agent
├── cron/                # scheduled tasks the agent runs
└── mcp.json             # MCP servers the agent connects to
```

Recipients run:

```bash
hermes profile install github.com/you/my-research-agent --alias
```

…and they now have the whole agent. They fill in their own API keys (`.env.EXAMPLE` → `.env`), and they can run `my-research-agent chat` or address it through Telegram / Discord / Slack / any gateway platform. When you push a new version, they run `hermes profile update my-research-agent` and pull your changes — their memories and sessions stay put.

## Why git?

We considered tarballs, HTTP archives, a custom format. None of them beat git:

- **Zero build step for authors.** Push to GitHub; consumers install. There's no "pack this, upload that, update the index" loop.
- **Tags, branches, and commits are already the versioning system.** A tag push does for us what "pack + upload a release" does for other tools.
- **Updates are a fetch.** Not a re-download of the whole archive.
- **Transparent.** Users can browse the repo, read diffs between versions, open issues against it, fork it to customize.
- **Private repos work for free.** SSH keys, `git credential` helpers, GitHub CLI stored credentials — whatever auth your terminal is already set up for applies transparently.
- **Reproducibility is a commit SHA.** The same thing pip and npm record.

The tradeoff: recipients need git installed. On any machine running Hermes in 2026, that's already true.

## When should you use a distribution?

Good fits:

- **You're sharing a specialized agent** — a compliance monitor, a code reviewer, a research assistant, a customer-support bot — with a team or with the community.
- **You're deploying the same agent to multiple machines** and don't want to copy files manually each time.
- **You're iterating on an agent** and want recipients to pick up new versions with one command.
- **You're building an agent as a product** — opinionated defaults, curated skills, tuned prompts — that other people should use as a starting point.

Not a fit:

- **You just want to back up a profile on your own machine.** Use [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) — that's what those are for.
- **You want to share API keys alongside the agent.** `auth.json` and `.env` are deliberately excluded from distributions. Each installer brings their own credentials.
- **You want to share memories / sessions / conversation history.** Those are user data, not distribution content. Never shipped.

:::caution
**Hermes does not control git.** The file exclusions described on this page are applied by the **installer** when someone runs `hermes profile install` or `hermes profile update`. They are **not** applied when you run `git add` or `git commit`.
:::

## The lifecycle: author to installer to update

Below is the full end-to-end flow. Pick the side you care about.

---

## For authors: publishing a distribution

### Step 1 — Start from a working profile

Build and refine the agent like any other profile:

```bash
hermes profile create research-bot
research-bot setup                    # configure model, API keys
# Edit ~/.hermes/profiles/research-bot/SOUL.md
# Install skills, wire up MCP servers, schedule cron jobs, etc.
research-bot chat                     # dogfood until it feels right
```

### Step 2 — Add a `distribution.yaml`

Create `~/.hermes/profiles/research-bot/distribution.yaml`:

```yaml
name: research-bot
version: 1.0.0
description: "Autonomous research assistant with arXiv and web tools"
hermes_requires: ">=0.12.0"
author: "Your Name"
license: "MIT"

# Tell installers which env vars the agent needs. These are checked against
# the installer's shell and existing .env file so they don't get nagged
# about keys they already have configured.
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API key (for model access)"
    required: true
  - name: SERPAPI_KEY
    description: "SerpAPI key for web search"
    required: false
    default: ""
```

That's the whole manifest. Every field except `name` has a sensible default.

### Step 3 — Create a `.gitignore` before the first commit

:::warning
Do this **before** running `git init` or `git add`. If you have already chatted with the profile, run setup, or otherwise used it, the directory now contains files you must not ship: `.env`, `auth.json`, `memories/`, `sessions/`, `state.db*`, `logs/`, and more. 
:::

Create `~/.hermes/profiles/research-bot/.gitignore` with at minimum:

```gitignore
# Credentials & secrets — NEVER commit
auth.json
.env
.env.EXAMPLE    # generated by install, not authorship domain

# Runtime databases & state
state.db
state.db-shm
state.db-wal
hermes_state.db
response_store.db
response_store.db-shm
response_store.db-wal
gateway.pid
gateway_state.json
processes.json
auth.lock
active_profile
.update_check

# User data — NEVER commit
memories/
sessions/
logs/
plans/
workspace/
home/

# Caches & generated artifacts
image_cache/
audio_cache/
document_cache/
browser_screenshots/
cache/

# Infrastructure (should not be in profile dir, but safe to exclude)
hermes-agent/
.worktrees/
profiles/
bin/
node_modules/

# User customization namespace — your local overrides
local/

# Checkpoints & backups (can be huge)
checkpoints/
sandboxes/
backups/

# Logs
errors.log
.hermes_history
```

This mirrors the [hard-excluded paths](#whats-not-in-a-distribution-ever) that the installer strips on its end. Anything else you want to keep out of the repo (scratch files, large assets, local-only skills) should also go in here.

### Step 4 — Push to a git repo

```bash
cd ~/.hermes/profiles/research-bot
git init
git add .
git commit -m "v1.0.0"
git remote add origin git@github.com:you/research-bot.git
git tag v1.0.0
git push -u origin main --tags
```

The repo is now a distribution. Anyone with access can install it.

:::note
The installer will additionally strip the [hard-excluded paths](#whats-not-in-a-distribution-ever) even if an author somehow ships them — but that only protects installers, not the author. 
:::

### Step 5 — Tag versioned releases

Every time the agent reaches a stable point, bump the version and tag:

```bash
# Edit distribution.yaml: version: 1.1.0
git add distribution.yaml SOUL.md skills/
git commit -m "v1.1.0: tighter research SOUL, add arxiv skill"
git tag v1.1.0
git push --tags
```

Recipients who run `hermes profile update research-bot` will pull the latest.

### What the repo looks like

A complete authored distribution:

```
research-bot/
├── .gitignore                   # excludes secrets & user data (see Step 3)
├── distribution.yaml            # required
├── SOUL.md                      # strongly recommended
├── config.yaml                  # model, provider, tool defaults
├── mcp.json                     # MCP server connections
├── skills/
│   ├── arxiv-search/SKILL.md
│   ├── paper-summarization/SKILL.md
│   └── citation-lookup/SKILL.md
├── cron/
│   └── weekly-digest.json       # scheduled tasks
└── README.md                    # human-facing description (optional)
```

### Distribution-owned vs user-owned

When an installer updates to a new version, some things get replaced (author's domain) and some things stay put (installer's domain). Defaults:

| Category | Paths | On update |
|---|---|---|
| **Distribution-owned** | `SOUL.md`, `config.yaml`, `mcp.json`, `skills/`, `cron/`, `distribution.yaml` | Replaced from the new clone |
| **Config override** | `config.yaml` | Actually preserved by default — the installer may have tuned model or provider. Pass `--force-config` on update to reset. |
| **User-owned** | `memories/`, `sessions/`, `state.db*`, `auth.json`, `.env`, `logs/`, `workspace/`, `plans/`, `home/`, `*_cache/`, `local/` | Never touched |

You can override the distribution-owned list in the manifest:

```yaml
distribution_owned:
  - SOUL.md
  - skills/research/            # only my research skills; other installed skills stay
  - cron/digest.json
```

When omitted, the defaults above apply — which is what most distributions want.

---

## For installers: using a distribution

### Install

```bash
hermes profile install github.com/you/research-bot --alias
```

What happens:

1. Clones the repo into a temporary directory.
2. Reads `distribution.yaml`, shows you the manifest (name, version, description, author, required env vars).
3. Checks each required env var against your shell environment and the target profile's existing `.env`. Marks each as `✓ set` or `needs setting` so you know exactly what to configure.
4. Asks for confirmation. Pass `-y` / `--yes` to skip.
5. Copies distribution-owned files into `~/.hermes/profiles/research-bot/` (or wherever the manifest's `name` resolves). The [hard-excluded paths](#whats-not-in-a-distribution-ever) are stripped during this copy, even if the author accidentally left them in the repo.
6. Writes `.env.EXAMPLE` with the required keys commented out — copy to `.env` and fill in.
7. With `--alias`, creates a wrapper so you can run `research-bot chat` directly.

### Source types

Any git URL works:

```bash
# GitHub shorthand
hermes profile install github.com/you/research-bot

# Full HTTPS
hermes profile install https://github.com/you/research-bot.git

# SSH
hermes profile install git@github.com:you/research-bot.git

# Self-hosted, GitLab, Gitea, Forgejo — any Git host
hermes profile install https://git.example.com/team/research-bot.git

# Private repo using your configured git auth
hermes profile install git@github.com:your-org/internal-bot.git

# Local directory during development (no git push needed)
hermes profile install ~/my-profile-in-progress/
```

### Override the profile name

Two users wanting the same distribution under different profile names:

```bash
# Alice
hermes profile install github.com/acme/support-bot --name support-us --alias
# Bob (same distribution, different local name)
hermes profile install github.com/acme/support-bot --name support-eu --alias
```

### Fill in env vars

After install, the agent's profile contains a `.env.EXAMPLE`:

```
# Environment variables required by this Hermes distribution.
# Copy to `.env` and fill in your own values before running.

# OpenAI API key (for model access)
# (required)
OPENAI_API_KEY=

# SerpAPI key for web search
# (optional)
# SERPAPI_KEY=
```

Copy it:

```bash
cp ~/.hermes/profiles/research-bot/.env.EXAMPLE ~/.hermes/profiles/research-bot/.env
# Edit .env, paste your real keys
```

Required keys that were already in your shell environment (e.g. `OPENAI_API_KEY` exported in your `~/.zshrc`) are marked `✓ set` during install — you don't need to duplicate them in `.env`.

### Check what you installed

```bash
hermes profile info research-bot
```

Shows:

```
Distribution: research-bot
Version:      1.0.0
Description:  Autonomous research assistant with arXiv and web tools
Author:       Your Name
Requires:     Hermes >=0.12.0
Source:       https://github.com/you/research-bot
Installed:    2026-05-08T17:04:32+00:00

Environment variables:
  OPENAI_API_KEY (required) — OpenAI API key (for model access)
  SERPAPI_KEY (optional) — SerpAPI key for web search
```

`hermes profile list` also shows a `Distribution` column so at a glance you can see which of your profiles came from repos and which you hand-built:

```
 Profile          Model                        Gateway      Alias        Distribution
 ───────────────    ───────────────────────────    ───────────    ───────────    ────────────────────
 ◆default         claude-sonnet-4              stopped      —            —
  coder           gpt-5                        stopped      coder        —
  research-bot    claude-opus-4                stopped      research-bot research-bot@1.0.0
  telemetry       claude-sonnet-4              running      telemetry    telemetry@2.3.1
```

### Update

```bash
hermes profile update research-bot
```

What happens:

1. Re-clones the repo from the recorded source URL.
2. Replaces distribution-owned files (SOUL, skills, cron, mcp.json).
3. **Preserves** your `config.yaml` — you may have tuned the model, temperature, or other settings. Pass `--force-config` to overwrite.
4. **Never touches** user data: memories, sessions, auth, `.env`, logs, state.

No re-downloading the whole archive. No stomping your local changes to config. No deleting your conversation history.

### Remove

```bash
hermes profile delete research-bot
```

The delete prompt surfaces distribution info before asking you to confirm:

```
Profile: research-bot
Path:    ~/.hermes/profiles/research-bot
Model:   claude-opus-4 (anthropic)
Skills:  12
Distribution: research-bot@1.0.0
Installed from: https://github.com/you/research-bot

This will permanently delete:
  • All config, API keys, memories, sessions, skills, cron jobs
  • Command alias (~/.local/bin/research-bot)

Type 'research-bot' to confirm:
```

So you never accidentally delete an agent without knowing where it came from or being able to re-install it.

---

## Use cases and patterns

### Personal: sync one agent across machines

You built a research assistant on your laptop. You want the same agent on your workstation.

```bash
# Laptop — create .gitignore first (see "For authors" Step 3), then:
cd ~/.hermes/profiles/research-bot
git init && git add . && git status   # confirm no secrets staged
git commit -m "initial"
git remote add origin git@github.com:you/research-bot.git
git push -u origin main

# Workstation
hermes profile install github.com/you/research-bot --alias
# Fill in .env. Done.
```

Any iteration on the laptop (`git commit && push`) pulls onto the workstation with `hermes profile update research-bot`. Memories stay per-machine — the laptop remembers its own conversations, the workstation remembers its own, they don't collide.

### Team: ship a reviewed internal agent

Your engineering team wants a shared PR-review bot with a specific SOUL, specific skills, and a cron that runs every PR through it.

```bash
# Engineering lead — create .gitignore first (see "For authors" Step 3), then:
cd ~/.hermes/profiles/pr-reviewer
# ... build and tune ...
git init && git add . && git status   # confirm no secrets staged
git commit -m "v1.0 PR reviewer"
git tag v1.0.0
git push -u origin main --tags    # push to your company's internal Git host

# Each engineer
hermes profile install git@github.com:your-org/pr-reviewer.git --alias
# Fill in .env with their own API key (billed to them), .env.EXAMPLE points at what's required
pr-reviewer chat
```

When the lead ships v1.1 (better SOUL, new skill), engineers run `hermes profile update pr-reviewer` and everyone's on the new version within minutes.

### Community: publish a public agent

You built something novel — maybe a "Polymarket trader" or an "academic paper summarizer" or a "Minecraft server ops assistant." You want to share it.

```bash
# You — create .gitignore first (see "For authors" Step 3), then:
cd ~/.hermes/profiles/polymarket-trader
# Write a solid README.md at the repo root — GitHub shows it on the repo page
git init && git add . && git status   # confirm no secrets staged
git commit -m "v1.0"
git tag v1.0.0
# Publish to a public GitHub repo
git remote add origin https://github.com/you/hermes-polymarket-trader.git
git push -u origin main --tags

# Anyone
hermes profile install github.com/you/hermes-polymarket-trader --alias
```

Tweet the install command. People who try it send you issues and PRs. If someone wants to customize, they fork — same git workflow everyone already knows.

### Product: ship an opinionated agent

You built Hermes-on-top — maybe a compliance-monitoring harness, a customer-support stack, a domain-specific research platform. You want to distribute it as a product.

```yaml
# distribution.yaml
name: telemetry-harness
version: 2.3.1
description: "Compliance telemetry harness — monitors and reviews regulated workflows"
hermes_requires: ">=0.13.0"
author: "Acme Compliance Inc."
license: "Commercial"

env_requires:
  - name: ACME_API_KEY
    description: "Your Acme Compliance license key (email support@acme.com)"
    required: true
  - name: OPENAI_API_KEY
    description: "OpenAI API key for model access"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "URL for your Graphiti knowledge graph instance"
    required: false
    default: "http://127.0.0.1:8000/sse"
```

Your customers install via a single command; the install preview tells them exactly which keys to have ready; updates roll out the moment you tag a new release; their compliance data (`memories/`, `sessions/`) never leaves their machine.

### Ephemeral: one-off scripts on shared infra

You're the ops lead. You want a temporary agent that diagnoses a production incident — a canned SOUL with the right tools and MCP connections — and runs on three on-call engineers' laptops for the next week.

```bash
# You — create .gitignore first (see "For authors" Step 3), then:
# Build the profile, commit, push a private repo
git push -u origin main

# Each on-call
hermes profile install git@github.com:your-org/incident-2026-q2.git --alias

# Incident resolved — tear it down
hermes profile delete incident-2026-q2
```

The install-delete cycle is cheap enough to be disposable.

---

## Recipes

### Pin to a specific version

:::note
Git ref pinning (`#v1.2.0`) is planned but not in the initial release — install currently tracks the default branch. Track your installed version via `hermes profile info <name>` and hold off on updates until you're ready.
:::

### Check what version you're on vs. latest

```bash
# Your installed version
hermes profile info research-bot | grep Version

# Latest upstream (without installing)
git ls-remote --tags https://github.com/you/research-bot | tail -5
```

### Keep local config customizations through updates

The default update behavior already does this: `config.yaml` is preserved. To be safe, write your local tweaks to a file the distribution doesn't own:

```yaml
# ~/.hermes/profiles/research-bot/local/my-overrides.yaml
# (distribution never touches local/)
```

…and reference it from `config.yaml` or your SOUL as needed.

### Force a clean re-install

```bash
# Nuke and re-install from scratch (loses memories/sessions too)
hermes profile delete research-bot --yes
hermes profile install github.com/you/research-bot --alias

# Update to current main but reset config.yaml to the distribution's default
hermes profile update research-bot --force-config --yes
```

### Fork and customize

The standard git workflow — distributions are just repos:

```bash
# Fork the repo on GitHub, then install your fork
hermes profile install github.com/yourname/forked-research-bot --alias

# Iterate locally in ~/.hermes/profiles/forked-research-bot/
# Edit SOUL.md, commit, push to your fork
# Upstream changes: pull them into your fork the usual way
```

### Test a distribution before pushing

From the author's machine:

```bash
# Install from a local directory (no git push needed)
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test --alias

# Tweak, delete, re-install until it's right
hermes profile delete research-bot-test --yes
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test
```

---

## What's NOT in a distribution (ever)

The installer hard-excludes these paths even if an author accidentally ships them. No config option lets you override this — the safety guard is a regression-tested invariant:

- `auth.json` — OAuth tokens, platform credentials
- `.env` — API keys, secrets
- `memories/` — conversation memory
- `sessions/` — conversation history
- `state.db`, `state.db-shm`, `state.db-wal` — session metadata
- `logs/` — agent and error logs
- `workspace/` — generated working files
- `plans/` — scratch plans
- `home/` — user's home mount in Docker backends
- `*_cache/` — image / audio / document caches
- `local/` — user-reserved customization namespace

When you clone a distribution as an installer, these simply aren't copied into your profile directory. When you update, your copies stay put. If you installed the same distribution on five machines, you have five isolated sets of this data — one per machine.

:::caution
This exclusion runs at **install / update time on the installer's machine**. It does **not** prevent an author from commiting sensitive/unnecessary files. Authors must use a [`.gitignore`](#step-3--create-a-gitignore-before-the-first-commit) to keep secrets out of the repo.
:::

## Security and trust

Profile distributions are unsigned by default. You're trusting:

- **The git host** (GitHub / GitLab / wherever) to serve the bytes the author pushed.
- **The author** to not ship a malicious SOUL, skills, or cron jobs.

Cron jobs from a distribution are **not auto-scheduled** — the installer prints `hermes -p <name> cron list` and you enable them explicitly. SOUL.md and skills ARE active as soon as you start chatting with the profile, so read them before your first run if you're installing from someone you don't know.

Rough analogy: installing a distribution is like installing a browser extension or a VS Code extension. Low friction, high power, trust the source. For internal company distributions, use a private repo and your normal git auth — nothing new to configure.

Future versions may add signing, a lockfile (`.distribution-lock.yaml`) with a resolved commit SHA, and a `--dry-run` flag that prints the diff before applying an update. None of those are shipping yet.

## Under the hood

For implementation details, precise CLI behavior, and all flags, see the [Profile Commands reference](../reference/profile-commands.md#distribution-commands).

The short version:

- `install`, `update`, `info` live inside `hermes profile` — not a parallel command tree.
- The manifest format is YAML with a tiny required schema (`name` only).
- The installer uses your local `git` binary for cloning, so any auth your shell already handles (SSH keys, credential helpers) works transparently.
- After clone, `.git/` is stripped — the installed profile isn't itself a git checkout, avoiding "oh my, I accidentally committed my `.env` to the distribution's git history" traps.
- Reserved profile names (`hermes`, `test`, `tmp`, `root`, `sudo`) are rejected at install time to avoid collisions with common binaries.

## See also

- [Profiles: Running Multiple Agents](./profiles.md) — the base concept
- [Profile Commands reference](../reference/profile-commands.md) — every flag, every option
- [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) — local backup / restore (not distribution)
- [Using SOUL with Hermes](../guides/use-soul-with-hermes.md) — authoring personalities
- [Personality & SOUL](./features/personality.md) — how SOUL fits into the agent
- [Skills catalog](../reference/skills-catalog.md) — skills you can bundle

---

# SOURCE: website/docs/user-guide/multi-profile-gateways.md

---
sidebar_position: 4
---

# Running Many Gateways at Once

Operate multiple [profiles](./profiles.md) — each with its own bot tokens,
sessions, and memory — as managed services on a single machine. This page
covers the operational concerns: starting them all together, viewing logs
across profiles, preventing the host from sleeping, and recovering from common
launchd/systemd quirks.

If you only run one Hermes agent, you don't need this page — see
[Profiles](./profiles.md) for the basics.

## When to use this

You want this setup when you have two or more Hermes agents that should all
be online at the same time. Common reasons:

- A personal assistant on one Telegram bot and a coding agent on another
- One agent per family member or one per Slack workspace
- Sandbox + production instances of the same configuration
- A research agent + a writing agent + a cron-driven bot — each with isolated
  memory and skills

Every profile already gets its own per-platform LaunchAgent
(`ai.hermes.gateway-<name>.plist`) or systemd user service
(`hermes-gateway-<name>.service`). This guide adds the patterns for managing
them collectively.

## Quick start

```bash
# Create profiles (once)
hermes profile create coder
hermes profile create personal-bot
hermes profile create research

# Configure each
coder setup
personal-bot setup
research setup

# Install each gateway as a managed service
coder gateway install
personal-bot gateway install
research gateway install

# Start them all
coder gateway start
personal-bot gateway start
research gateway start
```

That's it — three independent agents, each on its own process, restarting
automatically on crash and on user login.

## Alternative: one gateway for all profiles (multiplexing)

The model above runs **one process per profile**. That is the default and is
the right choice for most setups. But on a host with many profiles — or a
container deployment where one process per profile is operationally heavy — you
can instead run a **single multiplexing gateway**: the default profile's gateway
becomes the sole inbound process and serves messages for *every* profile on the
box.

This is **opt-in** and **off by default**. When it's off, nothing on this page
changes — every behavior below is inert.

### When to prefer multiplexing

- A container/VPS deployment where N supervisor units, N ports, and N PID files
  are a burden.
- Many low-traffic profiles that don't each justify a full process.
- You want a single thing to start, monitor, and restart.

Stick with one-process-per-profile when you want hard process-level isolation
between profiles (separate memory footprints, independent crash domains, the
ability to restart one profile without touching the others).

### How to opt in

Set the flag on the **default profile** (it owns the multiplexer) and restart
its gateway:

```bash
hermes config set gateway.multiplex_profiles true
hermes gateway restart
```

Equivalently, in the default profile's `~/.hermes/config.yaml`:

```yaml
gateway:
  multiplex_profiles: true
```

(The flag is also accepted as a top-level `multiplex_profiles: true` for
convenience.) On the next start the default gateway enumerates every profile,
brings up each profile's enabled platforms under that profile's own
credentials, and routes each inbound message to the profile it belongs to. Each
turn resolves the routed profile's config, skills, memory, SOUL, **and provider
keys** — credentials are never shared across profiles.

You do **not** run `hermes gateway start` for the secondary profiles — the
default gateway serves them. See the contract changes below.

### What changes when multiplexing is on

Enabling the flag changes how a few things behave. All of these revert the
moment the flag is off.

#### 1. Secondary profiles must not start their own gateway

With a multiplexer running, a named-profile `hermes gateway start` / `run` is a
**hard error**, pointing you back at the multiplexer:

```
The default gateway is running as a profile multiplexer and already serves
profile 'coder'. ...
```

The multiplexer is the single inbound process; a second profile gateway would
double-bind that profile's platforms. Pass `--force` only if you deliberately
want a separate process for that profile (not recommended while the multiplexer
is running). The cross-profile lifecycle wrapper script earlier on this page is
therefore **not** used in multiplex mode — you only manage the default gateway.

#### 2. HTTP-inbound platforms are reached via a `/p/<profile>/` URL prefix

Webhook (and other HTTP-inbound) traffic for a secondary profile arrives on the
default listener under a profile prefix, **not** a second port:

```
# default profile
POST http://host:8644/webhooks/<route>
# the "coder" profile, same listener
POST http://host:8644/p/coder/webhooks/<route>
```

An unknown or unconfigured profile in the prefix returns `404`. Because the one
shared listener already serves every profile this way, a **secondary profile
must not enable a port-binding platform itself** — doing so is a config error
and the gateway refuses to start, naming the profile and platform:

```
Profile 'coder' enables the port-binding platform 'webhook', but
gateway.multiplex_profiles is on. ... Remove platforms.webhook from profile
'coder's config.yaml (configure it only on the default profile).
```

Port-binding platforms covered by this rule: `webhook`, `api_server`,
`msgraph_webhook`, `feishu`, `wecom_callback`, `bluebubbles`, `sms`. Configure
any of these **only on the default profile**; every profile is reachable through
its `/p/<profile>/` prefix.

#### 3. Per-credential platforms still need their own token per profile

Polling/connection platforms (Telegram, Discord, Slack, Matrix, Signal, …) work
fine multiplexed, but each profile that enables one must supply its **own** bot
token — the same token cannot be polled by two profiles at once. If two profiles
configure the same `(platform, token)`, startup fails fast naming both profiles
(see [Token-conflict safety](#token-conflict-safety) — the rule is unchanged,
it's just enforced inside the one process now).

#### 4. Session keys are namespaced by profile

Each profile's sessions live under an `agent:<profile>:…` namespace so two
profiles on the same platform/chat never collide in the shared session store.
The **default** profile keeps the historical `agent:main:…` namespace
byte-for-byte, so existing default-profile sessions are unaffected — no
migration, no orphaned history.

#### 5. One PID/lock and one status surface

There is a single process-level PID and lock (the multiplexer, under the default
home). `hermes status` reports the multiplexer and the profiles it serves;
`hermes status -p <name>` slices to one profile. Each profile still writes its
own `runtime_status.json` under its own home, so existing per-profile readers
keep working.

#### What does **not** change

Per-profile `.env` credential isolation is preserved and, if anything,
stricter: a profile's keys are resolved from its own scope and are never unioned
into a shared environment (this also means subprocesses like MCP servers and
Kanban workers only ever see their own profile's secrets). Kanban,
profile-scoped skills/memory/SOUL, and model routing all behave per-profile
exactly as they do with separate gateways.

## Start, stop, or restart all gateways at once

The CLI ships with single-profile lifecycle commands. To act across every
profile, wrap them in a shell loop. Put the snippet below in
`~/.local/bin/hermes-gateways` and `chmod +x` it:

```sh
#!/bin/sh
set -eu

# Add or remove profile names here as you create / delete profiles.
profiles="default coder personal-bot research"

usage() {
  echo "Usage: hermes-gateways {start|stop|restart|status|list}"
}

run_for_profile() {
  profile="$1"
  action="$2"
  if [ "$profile" = "default" ]; then
    hermes gateway "$action"
  else
    hermes -p "$profile" gateway "$action"
  fi
}

action="${1:-}"
case "$action" in
  start|stop|restart|status)
    for profile in $profiles; do
      echo "==> $action $profile"
      run_for_profile "$profile" "$action"
    done
    ;;
  list)
    hermes gateway list
    ;;
  *)
    usage
    exit 2
    ;;
esac
```

Then:

```bash
hermes-gateways start      # start every configured profile
hermes-gateways stop       # stop every configured profile
hermes-gateways restart    # restart all
hermes-gateways status     # status across all
hermes-gateways list       # delegates to `hermes gateway list`
```

:::tip
The `default` profile is targeted with `hermes gateway <action>` (no `-p`),
not `hermes -p default gateway <action>`. The wrapper above handles both forms.
:::

## Manage one profile

The shortcut commands every profile installs:

```bash
coder gateway run        # foreground (Ctrl-C to stop)
coder gateway start      # start the managed service
coder gateway stop       # stop the managed service
coder gateway restart    # restart
coder gateway status     # status
coder gateway install    # create the LaunchAgent / systemd unit
coder gateway uninstall  # remove the service file
```

These are equivalent to `hermes -p coder gateway <action>` — useful if a
profile alias is not on `PATH` or if you target profiles dynamically from a
script.

## Service files

Each profile installs its own service with a unique name, so installations
never clash:

| Platform | Path                                                              |
| -------- | ----------------------------------------------------------------- |
| macOS    | `~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist`        |
| Linux    | `~/.config/systemd/user/hermes-gateway-<profile>.service`         |

The default profile keeps the historical names: `ai.hermes.gateway.plist` /
`hermes-gateway.service`.

## Viewing logs

Each profile writes to its own log files:

```bash
# Default profile
tail -f ~/.hermes/logs/gateway.log
tail -f ~/.hermes/logs/gateway.error.log

# Named profile
tail -f ~/.hermes/profiles/<name>/logs/gateway.log
tail -f ~/.hermes/profiles/<name>/logs/gateway.error.log
```

Stream every profile's log simultaneously:

```bash
tail -f ~/.hermes/logs/gateway.log ~/.hermes/profiles/*/logs/gateway.log
```

The CLI also has a structured log viewer:

```bash
hermes logs -f                  # follow default profile
hermes -p coder logs -f         # follow one profile
hermes logs --help              # filters, levels, JSON output
```

## Identify what's actually running

```bash
hermes profile list             # profiles + model + gateway state
hermes-gateways status          # full status across every profile
launchctl list | grep hermes    # macOS — PIDs and labels
systemctl --user list-units 'hermes-gateway-*'   # Linux — units
```

## Editing configuration

Every profile keeps its config inside its own directory:

```
~/.hermes/profiles/<name>/
├── .env              # API keys, bot tokens (chmod 600)
├── config.yaml       # model, provider, toolsets, gateway settings
└── SOUL.md           # personality / system prompt
```

The default profile uses `~/.hermes/` directly with the same three files.

Edit them with any editor or via the CLI:

```bash
hermes config set model.model anthropic/claude-sonnet-4    # default profile
coder config set model.model openai/gpt-5                  # named profile
```

After editing `.env` or `config.yaml`, restart the affected gateway:

```bash
coder gateway restart
# or, for everything:
hermes-gateways restart
```

## Keeping the host awake

The gateway process can run all day, but the operating system will still try
to sleep when idle. Two patterns:

### macOS — `caffeinate`

`caffeinate` is built into macOS and prevents sleep while it runs. No install.

```bash
caffeinate -dis                    # block display, idle, and system sleep
caffeinate -dis -t 28800           # same, auto-exit after 8 hours
caffeinate -i -w $(cat ~/.hermes/gateway.pid) &   # awake while default gateway runs

# Persistent: run in background and forget
nohup caffeinate -dis >/dev/null 2>&1 &
disown

# Inspect / stop
pmset -g assertions | grep -iE 'caffeinate|prevent|user is active'
pkill caffeinate
```

| Flag   | Effect                                            |
| ------ | ------------------------------------------------- |
| `-d`   | block display sleep                               |
| `-i`   | block idle system sleep (default)                 |
| `-m`   | block disk sleep                                  |
| `-s`   | block system sleep (AC-powered Macs only)         |
| `-u`   | simulate user activity (prevents screen lock)     |
| `-t N` | auto-exit after `N` seconds                       |
| `-w P` | exit when PID `P` exits                           |

:::warning Lid-close still sleeps the Mac
`caffeinate` cannot override the hardware-driven lid-close sleep on MacBooks.
For lid-closed operation, change your Energy Saver / Battery preferences or
use a third-party tool.
:::

### Linux — `systemd-inhibit` or `loginctl`

```bash
# Inhibit suspend while a command runs
systemd-inhibit --what=idle:sleep --who=hermes --why="gateways running" \
  sleep infinity &

# Allow user services to keep running after logout (recommended)
sudo loginctl enable-linger "$USER"
```

After enabling lingering, your systemd user units (including
`hermes-gateway-<profile>.service`) continue running across SSH disconnects
and reboots.

## Token-conflict safety

Each profile must use unique bot tokens for each platform. If two profiles
share a Telegram, Discord, Slack, WhatsApp, or Signal token, the second
gateway refuses to start with an error naming the conflicting profile.

To audit:

```bash
grep -H 'TELEGRAM_BOT_TOKEN\|DISCORD_BOT_TOKEN' \
     ~/.hermes/.env ~/.hermes/profiles/*/.env
```

## Updating the code

`hermes update` pulls the latest code once and syncs new bundled skills into
every profile:

```bash
hermes update
hermes-gateways restart
```

User-modified skills are never overwritten.

## Troubleshooting

### "Could not find service in domain for user gui: 501"

You ran `hermes gateway start` after a previous `hermes gateway stop`. The
CLI's `stop` does a full `launchctl unload`, which removes the service from
launchd's registry. The CLI catches this specific error on `start` and
automatically re-loads the plist (`↻ launchd job was unloaded; reloading
service definition`). The service starts normally. Nothing to fix.

### Stale PID after a crash

If a profile's gateway shows `not running` but a process is still alive:

```bash
ps -ef | grep "hermes_cli.*-p <profile>"
cat ~/.hermes/profiles/<profile>/gateway.pid
kill -TERM <pid>          # graceful
kill -KILL <pid>          # if that fails after a few seconds
<profile> gateway start
```

### Forcing a hard reset of one service

```bash
# macOS
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist
launchctl load   ~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist

# Linux
systemctl --user restart hermes-gateway-<profile>.service
```

### Health check

```bash
hermes doctor                  # default profile
hermes -p <profile> doctor     # one profile
```
