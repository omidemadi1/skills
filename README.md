# Skills & Tools Catalog

Personal collection of agent skills, subagents, and tools, organized by **use case**.
Clone this repo and copy (or symlink) any folder into your coding agent's skills directory.

```
git clone https://github.com/omidemadi1/skills.git
```

## Install locations

| Agent | Put skills under |
|---|---|
| Qoder (global) | `~/.agents/skills/<skill-name>/` |
| Qoder (project) | `<project>/.qoder/skills/<skill-name>/` |
| Claude Code | `~/.claude/skills/<skill-name>/` |
| Hermes Agent | `~/.hermes/skills/<skill-name>/` |
| Codex CLI | `~/.codex/skills/<skill-name>/` |

Each skill is a folder containing a `SKILL.md` (plus optional `references/`, `scripts/`, `assets/`).
Subagents go to `~/.agents/agents/` (Qoder) or the agent's equivalent.

## Catalog by use case

### Design & brand creation
Use when creating a visual identity, UI, brand assets, or working in design tools.
- **brand-assets-gen** — Generate a full brand-assets file from `design.md`/`requirements.md` specs.
- **design-creator** — Establish and maintain a unified `Design.md` for any digital product.
- **impeccable** — UI design automation via the Impeccable agent skill (critique, polish, redesign).
- **open-design** — Open Design local-first workspace for design artifacts.
- **penpot** — Reference knowledge for Penpot (boards, components, tokens, prototyping).
- **taste-skill** — Anti-slop design rules for AI-generated frontends.

### Frontend & creative web
- **build-threejs-scroll-worlds** — Scroll-controlled Three.js/WebGL scrollytelling experiences.

### Coding & workflow
Use when writing, reviewing, scaffolding, or planning code work.
- **ponytail** — Lazy senior dev mode: smallest change that fully solves the task.
- **ponytail-review** — Code review: logic, safety, load, tests, speed, necessity.
- **ponytail-audit** — Whole-repo audit: bugs, security, breakage risks, what to delete.
- **ponytail-debt** — Ledger of every `ponytail:` shortcut deferred.
- **ponytail-gain** — Measured savings display (code, cost, speed).
- **ponytail-help** — Quick reference for ponytail levels, skills, commands.
- **program-structure-generator** — Generate project directory/file scaffolding from Markdown descriptions.
- **runbook-writer** — Maintain hand-followable, step-by-step runbooks of completed tasks.
- **skill-creator** — Create, edit, evaluate, and optimize agent skills.
- **workstream-orchestrator** — Plan parallel/serial execution order for multi-task change sets.

### Browser automation
- **jev-browser** — Token-cheap browser automation via jev-ultrafast's indexed action space (no API keys).
- **tools/jev-ultrafast** — The underlying Python engine (vendored copy; upstream: [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast)).

### Desktop control (GUI apps)
- **computer-use** — Operate desktop apps through the accessibility tree and screenshots.
- **computer-use-design** — Design work (images, posters, logos, mockups) through GUI apps like Photoshop, Inkscape, Figma, Blender.
- **computer-use-security** — Safety rules to load before the first computer-use call.

### Knowledge management (Second Brain)
- **second-brain** — Telegram Inbox → Obsidian vault pipeline with knowledge graph.
- **second-brain-inbox** — Inbox-topic skill: collect links/notes into the queue.
- Full pipeline repo: [omidemadi1/second-brain-pipeline](https://github.com/omidemadi1/second-brain-pipeline).

### Infrastructure & servers
- **proxmox-manager** — Manage Proxmox VE: VMs, LXCs, storage, networking, guest execution via REST API.

### Agent platforms
- **hermes-agent** — Working knowledge for Hermes Agent (CLI, SOUL.md, configs, profiles, toolsets).

### Shopping & procurement
- **shopping-assistant** — BOM generation with live pricing from Digikala and Torob MCP servers.

### Subagents (`agents/`)
- **workstream-planner** — Read-only release planner: builds dependency/contention graph, returns parallel execution waves.
