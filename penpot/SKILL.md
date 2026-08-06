---
name: penpot
description: Reference and working knowledge for Penpot, the open-source design and prototyping platform (penpot.app / help.penpot.app). Use whenever the user mentions Penpot, asks how to use a feature (boards, layers, components, design tokens, flexible layouts, libraries, prototyping, comments, teams), wants to connect an AI agent to a Penpot file via the Penpot MCP server, wants to build or deploy a Penpot plugin, wants to self-host Penpot (Docker, Kubernetes, Elestio, configuration, troubleshooting), or wants to contribute to the Penpot open-source project. Also use it for goals Penpot can accomplish even unnamed — e.g. "connect Claude to my design file," "automate renaming layers in my design tool," "build a plugin for my design app," "self-host a Figma alternative," "generate a design system from tokens." Bundles the full help.penpot.app docs as markdown, organized by domain — read only the file(s) relevant to the task.
---

# Penpot

Penpot is an open-source, self-hostable design and prototyping platform (a Figma-style tool). It has four faces that matter for different tasks:

1. **The app itself** — boards, layers, components, design tokens, prototyping, teams/collaboration.
2. **The MCP server** — lets an AI agent (Claude, Cursor, etc.) read and modify a live, *open* Penpot file through natural-language-driven tool calls. No plugin code required.
3. **The Plugins system** — a small JS/TS app that runs *inside* Penpot's UI, built against the Plugins API, for shipping a reusable tool/panel to anyone who opens it.
4. **The self-hosted backend** — Docker/Kubernetes/Elestio deployments of Penpot's own open-source stack, for people who want to run their own instance instead of using design.penpot.app.

This skill bundles `help.penpot.app`'s documentation (sparse-cloned from `github.com/penpot/penpot/docs`, converted to clean markdown) under `references/`, mirroring the site's own structure 1:1. Don't load the whole tree — use the routing table below to open only what's relevant, the same way you'd navigate the live help center.

## Routing table

| Task involves... | Read |
|---|---|
| Boards, layers, shapes, paths, grouping/masking, color & strokes, text/typography, flexible (flex/grid) layouts | `references/user-guide/designing/*.md` |
| Components, design tokens, variants, shared libraries, assets panel | `references/user-guide/design-systems/*.md` |
| Teams, projects & files, comments, account settings | `references/user-guide/account-teams/*.md` |
| Prototyping (interactions/flows), View mode / testing a prototype | `references/user-guide/prototyping-testing/*.md` |
| Exporting/importing files or layers | `references/user-guide/export-import/*.md` |
| First-time setup: interface tour, keyboard shortcuts, cloud vs self-hosted signup, WebGL troubleshooting | `references/user-guide/first-steps/*.md` |
| Installing/enabling plugins as an end user (not building one) | `references/user-guide/plugins-integrations/index.md` |
| Inspect / code mode / dev handoff tools | `references/user-guide/dev-tools/index.md` |
| **Connecting an AI agent to a Penpot file** (Claude, Cursor, Claude Code, Copilot-style clients) | `references/mcp/*.md` — start with `references/mcp/index.md` |
| **Building a Penpot plugin** (custom panel/automation shipped to run inside Penpot) | `references/plugins/*.md` — start with `references/plugins/getting-started.md`, then `create-a-plugin.md` |
| Exhaustive Plugin API method/type signatures | `references/plugins/api.md` is a stub — see "Plugin API reference" note below |
| **Self-hosting Penpot** (Docker, Kubernetes, Elestio, env-var configuration, troubleshooting) | `references/technical-guide/getting-started/*.md`, `references/technical-guide/configuration.md`, `references/technical-guide/troubleshooting.md` |
| Contributing to Penpot's own codebase (architecture, dev environment, data model, subsystems) | `references/technical-guide/developer/*.md` |
| Integrating Penpot with other systems (webhooks, access tokens, SSO/auth) | `references/technical-guide/integration.md`, `references/user-guide/account-teams/your-account.md` |
| Reporting bugs, translations, code of conduct, contributing code/templates | `references/contributing-guide/*.md` |

Each subfolder also has an `index.md` with a short overview and links to its siblings — useful for orienting before diving into a specific file.

## Deciding between MCP and Plugins

Both let you "build anything" in Penpot programmatically, but they solve different problems — pick based on what the user actually wants:

- **Use MCP** when the goal is to have an AI agent *act on a design right now*: generate screens, apply a token/color update across a file, rename layers to a naming scheme, extract layout/tokens to hand off to code, audit a design system. It's conversational and requires no deployed code — just a running Penpot tab plus an MCP client config. Read `references/mcp/index.md` for the setup (remote vs local server, connecting Cursor/Claude Code/etc.), then `references/mcp/design-file-structure-best-practices.md` and `references/mcp/good-prompting-practices-design.md` for getting good results out of it, and `references/mcp/prompting-token-aware.md` if the workflow is hitting context/token limits.
- **Use Plugins** when the goal is to *ship a standalone tool* other people open from inside Penpot — a custom panel, a repeatable automation, an integration with an external service. This means writing and hosting a real JS/TS app against the Plugins API. Read `references/plugins/getting-started.md` (prerequisites, enabling the plugin manager, loading a plugin) then `references/plugins/create-a-plugin.md` (scaffolding with a framework or template) and `references/plugins/deployment.md` (hosting the built plugin). `references/plugins/examples-templates.md` has starter templates and `references/plugins/faq.md` covers common gotchas.

### Plugin API reference
`references/plugins/api.md` is intentionally a thin stub — Penpot's own docs point the exhaustive, type-generated Plugins API reference (every method, event, and object signature) to a separate TypeDoc site: **https://doc.plugins.penpot.app/**. That site is large and auto-generated from source, so it isn't bundled here; `web_fetch` the relevant page there when a task needs an exact method signature or type definition that the bundled guides don't cover.

## Self-hosting quick orientation

Penpot self-hosting has a few supported paths, covered in `references/technical-guide/getting-started/`:
- `docker.md` — the standard path (Docker + Docker Compose), assumes comfort with DNS/proxy config.
- `elestio.md` — a more turnkey managed option for people who don't want to run the Docker stack themselves.
- `kubernetes.md` — for a k8s deployment.
- `recommended-settings.md` and `unofficial-options.md` — tuning and community-maintained alternatives.

Configuration itself (environment variables and feature flags, prefixed `PENPOT_` and `enable-`/`disable-` respectively) is in `references/technical-guide/configuration.md`. `references/technical-guide/troubleshooting.md` covers common self-host failure modes.

## Notes on freshness

This reference was built by sparse-cloning `github.com/penpot/penpot` (docs/ folder) and converting each page to markdown, stripping images/video embeds (the guides sometimes reference GIFs/screenshots by filename in the original — those aren't reproduced here, only the text). Penpot's docs change with releases; if something bundled here looks stale or contradicts what the user is seeing in the app, re-fetch the live page at the equivalent `help.penpot.app` URL (the folder structure under `references/` mirrors the site's URL paths) rather than trusting the bundled copy blindly.
