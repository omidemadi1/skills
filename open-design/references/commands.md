# Open Design Commands Reference

Complete `od` CLI and MCP tool reference.

## Core CLI

```bash
# Development
pnpm tools-dev run web          # daemon + web foreground
pnpm tools-dev                  # daemon + web + desktop background
pnpm tools-dev start web        # daemon + web background
pnpm tools-dev restart          # restart all
pnpm tools-dev status           # inspect runtimes
pnpm tools-dev logs             # show logs
pnpm typecheck                  # tsc -b --noEmit

# MCP install (wires OD into coding agents)
od mcp install claude           # Claude Code
od mcp install codex            # Codex CLI
od mcp install cursor           # Cursor
od mcp install copilot          # GitHub Copilot
od mcp install opencode         # OpenCode
od mcp install openclaw         # OpenClaw
od mcp install hermes           # Hermes Agent
od mcp install cline            # Cline
od mcp install trae             # Trae
od mcp install kimi             # Kimi CLI
od mcp install antigravity      # Antigravity
od mcp install pi               # Pi Agent
od mcp install kiro             # Kiro
od mcp install vibe             # Mistral Vibe CLI
od mcp install --help           # full list
od mcp install --print          # dry-run preview
od mcp install <agent> --uninstall
```

## Automation

```bash
od automation list              # list automations
od automation create            # create automation
od automation run <id>          # run automation
od automation delete <id>       # delete automation
```

## Plugins

```bash
od plugin list                  # installed plugins
od plugin install <slug>        # install plugin
od plugin remove <slug>         # remove plugin
```

## Collaboration

```bash
od share                        # share project
od team invite <email>          # invite team member
```

## Research

```bash
od research "<topic>"           # deep research
od research search "<query>"    # search research
```

## Media

```bash
od media generate <prompt>      # generate media asset
od media list                   # list media assets
```

## MCP Tools (when installed in agent)

| Tool | Purpose |
|---|---|
| `od_create_project` | Create new project |
| `od_create_prototype` | Generate HTML prototype |
| `od_create_deck` | Generate presentation |
| `od_create_live_artifact` | Generate live dashboard/artifact |
| `od_create_image` | Generate image |
| `od_create_hyperframes` | Generate motion graphics |
| `od_get_project` | Get project details |
| `od_update_project` | Update project |
| `od_list_projects` | List all projects |
| `od_search_projects` | Search projects |
| `od_delete_project` | Delete project |
| `od_export_project` | Export to HTML/PDF/PPTX/MP4 |
| `od_critique` | Run design critique |
| `od_design_system_apply` | Apply design system |
| `od_design_system_create` | Create design system |
| `od_design_system_list` | List design systems |
| `od_automation_run` | Run automation |
| `od_team_share` | Share with team |
| `od_research` | Deep research |
| `od_generate_image` | Generate image |
| `od_generate_video` | Generate video |
| `od_generate_hyperframes` | Generate motion |
| `od_list_skills` | List skills |
| `od_apply_skill` | Apply skill |
| `od_list_plugins` | List plugins |
| `od_install_plugin` | Install plugin |
| `od_list_connectors` | List connectors |
| `od_install_connector` | Install connector |
| `od_project_media` | Generate project media |
| `od_media` | Generate media asset |

## MCP Proxy (BYOK without CLI)

```
POST /api/proxy/{anthropic,openai,azure,google,ollama,senseaudio}/stream
```
Paste `baseUrl` + `apiKey` + `model`. Presets for OpenAI, Atlas Cloud, Anthropic, Azure, Google, Ollama, LM Studio, vLLM.
