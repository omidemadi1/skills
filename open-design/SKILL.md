---
name: open-design
description: Open Design local-first workspace for design artifacts.
version: 0.1.0
author: Hermes
tags: [Design, UI, Prototyping, Design-Systems, Desktop]
---

# Open Design — Local-First Design Workspace

Open Design is the open-source Claude Design alternative. A local-first native desktop app for macOS and Windows that generates web, desktop, and mobile prototypes, live dashboards, decks, images, video, and HyperFrames motion graphics. It ships as skills, a CLI (`od`), and an MCP server that coding agents consume natively.

It is NOT a cloud-only SaaS, NOT a Figma replacement, and NOT a component library. It is a local daemon + web UI + agent integration layer.

**Key dependency:** Node ~24, pnpm 10.33.x. Docker option available.

Full details in references: setup, commands, skills system, contributing.

## When to Use

- "Build me a landing page prototype"
- "Create a pitch deck from this content"
- "Generate a live dashboard with KPIs"
- "Design a mobile app screen"
- "Import this brand's design system"
- "Export to PPTX/PDF/MP4"
- "Set up Open Design locally"
- "Add a new skill or design template"

## Prerequisites

**Docker path (simplest):**
```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design/deploy && cp .env.example .env
openssl rand -hex 32 > OD_API_TOKEN
docker compose up -d
# Open http://localhost:7456
```

**Dev path (full control):**
```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design
corepack enable && pnpm install
pnpm tools-dev run web
```

**Packaged app:** Download from https://open-design.ai

Full setup details: read `references/setup.md`.

## How to Run

1. Start Open Design (Docker or dev mode)
2. Pick a coding agent and install MCP: invoke through the `terminal` tool: `od mcp install <agent>`
3. In the agent, use MCP tools or CLI commands to create projects and artifacts
4. Alternatively, use the web UI at http://localhost:7456

For Hermes specifically: `od mcp install hermes` wires OD into Hermes Agent.

## Quick Reference

**Core CLI:**
```bash
od mcp install <agent>         # wire into coding agent
od mcp install --help          # list all agents
od automation list|create|run  # manage automations
od plugin list|install|remove  # manage plugins
od research "<topic>"          # deep research
od media generate <prompt>     # generate media
```

**Dev lifecycle:**
```bash
pnpm tools-dev run web         # foreground
pnpm tools-dev                 # background
pnpm tools-dev status          # inspect
pnpm typecheck                 # type check
```

**MCP tools:** `od_create_project`, `od_create_prototype`, `od_create_deck`, `od_create_live_artifact`, `od_create_image`, `od_create_hyperframes`, `od_critique`, `od_design_system_apply`, `od_export_project`, `od_research`, `od_list_skills`, `od_apply_skill`, `od_list_plugins`, `od_install_plugin`

Full command reference: read `references/commands.md`.

## Procedure

### Creating a Prototype

1. Ensure Open Design is running (Docker or dev mode)
2. Install MCP in your agent: invoke through the `terminal` tool: `od mcp install hermes`
3. Create a project: use `od_create_project` MCP tool
4. Generate artifact: use `od_create_prototype` with a brief describing what you want
5. Preview in the OD web UI sandboxed iframe
6. Export: use `od_export_project` for HTML/PDF/PPTX/MP4

### Creating a Deck

1. Use `od_create_deck` MCP tool with slide content
2. Navigate in OD web UI with keyboard
3. Export to PPTX or PDF via `od_export_project`

### Applying a Design System

1. List available systems: use `od_design_system_list`
2. Apply to project: use `od_design_system_apply` with the system ID
3. All subsequent artifacts inherit the brand's visual language

### Adding a Custom Skill

1. Create `skills/<name>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: my-skill
   description: What it does.
   triggers:
     - "trigger phrase"
   od:
     mode: prototype
     category: web-artifacts
   ---
   ```
2. Add `assets/` and `references/` alongside
3. Daemon picks it up on next `/api/skills` — no restart needed

Full contribution guide: read `references/contributing.md`.
Full skill/template system: read `references/skills-system.md`.

## Pitfalls

- **Node version matters:** Must be Node ~24, not 22 or older. `corepack enable` fails on Windows — use `npm install -g pnpm@10.33.2` instead
- **PATH issues on macOS:** If agent CLI shows "not installed", ensure its bin dir is on PATH for the daemon process. Use Rescan in Settings
- **Windows native:** Best-effort. Use WSL2 for reliable experience
- **better-sqlite3 on Windows:** Compiles from source (~2 min), needs VS Build Tools 2022
- **Design system sync:** 151 bundled systems come from VoltAgent/awesome-design-md. Send brand PRs upstream first
- **Skill vs template confusion:** Skills = agent capabilities invoked mid-task. Templates = rendering catalogue entries. Don't mix them
- **MCP install needs daemon running:** `od mcp install` requires the OD daemon to be running first
- **BYOK proxy SSRF protection:** Blocks internal IPs/link-local/CGNAT at daemon edge

## Verification

After setup, verify Open Design is working:

```bash
# Check daemon is running
pnpm tools-dev status

# Check MCP is installed in agent
od mcp install hermes --print    # dry-run preview

# Open web UI
# Navigate to http://localhost:7456 — should see Home page
```

In your agent, test with: "Use Open Design to create a simple landing page prototype for a coffee shop."
