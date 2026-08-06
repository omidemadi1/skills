---
name: hermes-agent
description: Reference and working knowledge for Hermes Agent, the open-source self-improving AI agent CLI/gateway from Nous Research (github.com/NousResearch/hermes-agent). Use this skill whenever the user mentions Hermes Agent, the `hermes` CLI, SOUL.md, the Hermes Bible, Nous Portal, or asks to install, configure, troubleshoot, or extend a Hermes agent (skills, plugins, MCP servers, cron jobs, messaging gateway/Telegram/Discord/Slack bots, profiles, kanban, delegation/subagents, memory, or the web dashboard). Also use it whenever the user wants to write a SOUL.md, build a Hermes Skill or Plugin, write `hermes` CLI or slash commands, debug a `hermes doctor` / config.yaml issue, or design a Hermes-based automation/workflow — even if they don't say "Hermes" explicitly but describe building a personal AI agent/assistant that runs 24/7 across messaging platforms with cron, skills, and memory.
---

# Hermes Agent

Hermes Agent is Nous Research's open-source, self-improving AI agent. It runs
as a terminal CLI/TUI, a desktop app, and a long-running messaging gateway
(Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost,
Home Assistant, Teams, and 15+ more). It supports any LLM provider, on-demand
"Skills" (progressive-disclosure knowledge docs), a plugin system, MCP
servers, cron automation, subagent delegation, a Kanban multi-agent board,
and persistent memory. Repo: github.com/NousResearch/hermes-agent. Official
docs: hermes-agent.nousresearch.com/docs. Community index + workflows
("flows"): hermesbible.com (unofficial, not affiliated with Nous Research).

This skill bundles the most commonly needed doc pages in full (under
`references/`) and gives a sitemap to fetch anything else live, since the
full doc set is ~350 pages and changes frequently.

## How to use this skill

1. **Identify the task type** and jump to the matching reference file below
   — don't load files you don't need.
2. **For anything not covered, or if you suspect the bundled copy is stale**
   (version numbers, new CLI flags, new providers), fetch the live page:
   ```bash
   curl -s "https://raw.githubusercontent.com/NousResearch/hermes-agent/main/website/docs/<path>"
   ```
   Find `<path>` in `references/00-sitemap.md`. `raw.githubusercontent.com`
   and `github.com` are reachable from the bash tool. Alternatively
   `web_fetch` the rendered page at `https://hermes-agent.nousresearch.com/docs/<path-without-.md>`.
3. **For real-world setups, architectures, and worked examples** (token
   economics, SOUL.md templates, multi-agent orchestration patterns) rather
   than official reference docs, search hermesbible.com/flows — these are
   community-contributed, not official, so flag them as such if you cite one.
4. **Always prefer the official docs (nousresearch.com / GitHub) as the
   source of truth** over hermesbible.com when the two might disagree —
   hermesbible.com itself says this.

## Reference index

| File | Covers |
|---|---|
| `00-sitemap.md` | Full path list of every doc page, for live fetching anything not bundled |
| `01-getting-started.md` | Install (curl installer, Desktop app, Nix, Termux/Android), quickstart, learning path, updating/uninstalling |
| `02-cli-commands.md` | Every `hermes <command>` — chat, model, gateway, setup, auth, cron, skills, plugins, mcp, profile, dashboard, etc. |
| `03-slash-and-profile-commands.md` | In-chat `/slash` commands and `hermes profile` subcommands |
| `04-configuration.md` | `config.yaml` / `.env` structure, terminal backends (local/Docker/SSH/Daytona/Singularity/Modal), every config section |
| `05-models-and-env-vars.md` | Configuring main/auxiliary models, full provider catalog, every environment variable |
| `06-profiles.md` | Running multiple independent agents, profile distributions, multi-profile gateways |
| `07-core-concepts.md` | Features overview, Tools, Context Files (AGENTS.md etc.), Context References (`@file`), SOUL.md / personality |
| `08-skills-system.md` | The Skills system, Curator, working with skills, **creating new Skills** (developer guide), bundled/optional skills catalog |
| `09-memory.md` | Persistent memory, external memory providers, Honcho |
| `10-automation.md` | Cron jobs, automation blueprints, Persistent Goals, Code Execution, subagent Delegation patterns |
| `11-kanban.md` | Multi-agent Kanban board, worker lanes, tutorial |
| `12-plugins-and-mcp.md` | Plugin system, built-in plugins, **building a plugin**, MCP (Model Context Protocol), Tool Search |
| `13-tools-and-toolsets-reference.md` | Every built-in tool and toolset, what's enabled where |
| `14-messaging-gateway.md` | Gateway overview + setup for Telegram, Discord, Slack, WhatsApp, Signal, Email (see sitemap for other 25 platforms) |
| `15-security.md` | Security model, command approval, sandboxing, secrets managers (Bitwarden) |
| `16-faq-troubleshooting.md` | FAQ, common errors, update/uninstall edge cases |
| `17-soul-md-guide.md` | Deep dive on writing an effective SOUL.md (agent identity/personality) |
| `18-developer-internals.md` | Architecture, agent loop internals, adding tools, adding platform adapters, programmatic/Python library use |

## Quick orientation

- **Settings live in `~/.hermes/`**: secrets/tokens in `.env`, everything
  else in `config.yaml`. Prefer `hermes config set <key> <value>` over
  hand-editing — it routes to the right file.
- **First-run path**: `hermes setup` (full wizard) or `hermes setup --portal`
  (fastest — one OAuth into Nous Portal covers a model + web search + image
  gen + TTS + cloud browser).
- **`hermes model` vs `/model`**: `hermes model` (run from your shell, outside
  a session) is the full provider/OAuth/API-key wizard. `/model` (typed
  inside a chat) only switches between already-configured providers/models.
- **Diagnose problems with `hermes doctor`** first, always.
- **SOUL.md** is the agent's primary identity — first thing in the system
  prompt. Most "make Hermes act like X" requests are SOUL.md edits, not code
  changes — see `17-soul-md-guide.md`.
- **Skills vs Plugins vs MCP**: Skills are markdown knowledge docs the agent
  loads on demand (no code) — easiest to create. Plugins add real Python
  tools/hooks to the agent. MCP connects to external tool servers (GitHub,
  databases, etc.) without writing Hermes-specific code. Point the user to
  the cheapest mechanism that solves their problem (usually: Skill first).
- Minimum model context window is **64K tokens** — anything smaller is
  rejected at startup.

## When writing config / SOUL.md / skills for the user

- Always check `04-configuration.md` and `02-cli-commands.md` for the exact
  current key names and command syntax before generating YAML or shell
  commands — don't invent flags from memory.
- When creating a new Hermes Skill, follow the structure and frontmatter
  conventions in `08-skills-system.md` (`developer-guide/creating-skills.md`
  section) — Hermes Skills follow the open agentskills.io standard, similar
  in spirit to (but not identical to) Claude's own Skill format used here.
- When writing a SOUL.md, keep it concise (the community guides in
  `17-soul-md-guide.md` stress that ~50-170 lines is typical) and avoid
  inventing config keys not documented in `04-configuration.md`.
