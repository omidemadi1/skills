<!-- Sections in this file (in order):
  - user-guide/features/overview.md
  - user-guide/features/tools.md
  - user-guide/features/context-files.md
  - user-guide/features/context-references.md
  - user-guide/features/personality.md
-->


---

# SOURCE: website/docs/user-guide/features/overview.md

---
title: "Features Overview"
sidebar_label: "Overview"
sidebar_position: 1
---

# Features Overview

Hermes Agent includes a rich set of capabilities that extend far beyond basic chat. From persistent memory and file-aware context to browser automation and voice conversations, these features work together to make Hermes a powerful autonomous assistant.

:::tip Don't know where to start?
`hermes setup --portal` covers a model provider plus all four Tool Gateway tools (web search, image generation, TTS, browser) in one command. See [Nous Portal](/integrations/nous-portal).
:::

## Core

- **[Tools & Toolsets](tools.md)** — Tools are functions that extend the agent's capabilities. They're organized into logical toolsets that can be enabled or disabled per platform, covering web search, terminal execution, file editing, memory, delegation, and more.
- **[Skills System](skills.md)** — On-demand knowledge documents the agent can load when needed. Skills follow a progressive disclosure pattern to minimize token usage and are compatible with the [agentskills.io](https://agentskills.io/specification) open standard.
- **[Persistent Memory](memory.md)** — Bounded, curated memory that persists across sessions. Hermes remembers your preferences, projects, environment, and things it has learned via `MEMORY.md` and `USER.md`.
- **[Context Files](context-files.md)** — Hermes automatically discovers and loads project context files (`.hermes.md`, `AGENTS.md`, `CLAUDE.md`, `SOUL.md`, `.cursorrules`) that shape how it behaves in your project.
- **[Context References](context-references.md)** — Type `@` followed by a reference to inject files, folders, git diffs, and URLs directly into your messages. Hermes expands the reference inline and appends the content automatically.
- **[Checkpoints](../checkpoints-and-rollback.md)** — Hermes automatically snapshots your working directory before making file changes, giving you a safety net to roll back with `/rollback` if something goes wrong.

## Automation

- **[Scheduled Tasks (Cron)](cron.md)** — Schedule tasks to run automatically with natural language or cron expressions. Jobs can attach skills, deliver results to any platform, and support pause/resume/edit operations.
- **[Subagent Delegation](delegation.md)** — The `delegate_task` tool spawns child agent instances with isolated context, restricted toolsets, and their own terminal sessions. Run 3 concurrent subagents by default (configurable) for parallel workstreams.
- **[Code Execution](code-execution.md)** — The `execute_code` tool lets the agent write Python scripts that call Hermes tools programmatically, collapsing multi-step workflows into a single LLM turn via sandboxed RPC execution.
- **[Event Hooks](hooks.md)** — Run custom code at key lifecycle points. Gateway hooks handle logging, alerts, and webhooks; plugin hooks handle tool interception, metrics, and guardrails.
- **[Batch Processing](batch-processing.md)** — Run the Hermes agent across hundreds or thousands of prompts in parallel, generating structured ShareGPT-format trajectory data for training data generation or evaluation.

## Media & Web

- **[Voice Mode](voice-mode.md)** — Full voice interaction across CLI and messaging platforms. Talk to the agent using your microphone, hear spoken replies, and have live voice conversations in Discord voice channels.
- **[Browser Automation](browser.md)** — Full browser automation with multiple backends: Browserbase cloud, Browser Use cloud, local Chrome/Brave/Chromium/Edge via CDP, or local Chromium. Navigate websites, fill forms, and extract information.
- **[Vision & Image Paste](vision.md)** — Multimodal vision support. Paste images from your clipboard into the CLI and ask the agent to analyze, describe, or work with them using any vision-capable model.
- **[Image Generation](image-generation.md)** — Generate images from text prompts using FAL.ai. Nine models supported (FLUX 2 Klein/Pro, GPT-Image 1.5/2, Nano Banana Pro, Ideogram V3, Recraft V4 Pro, Qwen, Z-Image Turbo); pick one via `hermes tools`.
- **[Voice & TTS](tts.md)** — Text-to-speech output and voice message transcription across all messaging platforms, with ten native provider options: Edge TTS (free), ElevenLabs, OpenAI TTS, MiniMax, Mistral Voxtral, Google Gemini, xAI, NeuTTS, KittenTTS, and Piper — plus custom command providers for any local TTS CLI.

## Integrations

- **[MCP Integration](mcp.md)** — Connect to any MCP server via stdio or HTTP transport. Access external tools from GitHub, databases, file systems, and internal APIs without writing native Hermes tools. Includes per-server tool filtering and sampling support.
- **[Provider Routing](provider-routing.md)** — Fine-grained control over which AI providers handle your requests. Optimize for cost, speed, or quality with sorting, whitelists, blacklists, and priority ordering.
- **[Fallback Providers](fallback-providers.md)** — Automatic failover to backup LLM providers when your primary model encounters errors, including independent fallback for auxiliary tasks like vision and compression.
- **[Credential Pools](credential-pools.md)** — Distribute API calls across multiple keys for the same provider. Automatic rotation on rate limits or failures.
- **[Prompt caching](../configuration#prompt-caching)** — Built-in cross-session 1-hour prefix cache for Claude on native Anthropic, OpenRouter, and Nous Portal. Always-on; no configuration required.
- **[Memory Providers](memory-providers.md)** — Plug in external memory backends (Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory) for cross-session user modeling and personalization beyond the built-in memory system.
- **[API Server](api-server.md)** — Expose Hermes as an OpenAI-compatible HTTP endpoint. Connect any frontend that speaks the OpenAI format — Open WebUI, LobeChat, LibreChat, and more.
- **[IDE Integration (ACP)](acp.md)** — Use Hermes inside ACP-compatible editors such as VS Code, Zed, and JetBrains. Chat, tool activity, file diffs, and terminal commands render inside your editor.
- **[Batch Processing](batch-processing.md)** — Run the agent over many prompts or tasks in parallel from the CLI, with structured outputs and trajectory capture suitable for evals or downstream training pipelines.

## Customization

- **[Personality & SOUL.md](personality.md)** — Fully customizable agent personality. `SOUL.md` is the primary identity file — the first thing in the system prompt — and you can swap in built-in or custom `/personality` presets per session.
- **[Skins & Themes](skins.md)** — Customize the CLI's visual presentation: banner colors, spinner faces and verbs, response-box labels, branding text, and the tool activity prefix.
- **[Plugins](plugins.md)** — Add custom tools, hooks, and integrations without modifying core code. Three plugin types: general plugins (tools/hooks), memory providers (cross-session knowledge), and context engines (alternative context management). Managed via the unified `hermes plugins` interactive UI.

---

# SOURCE: website/docs/user-guide/features/tools.md

---
sidebar_position: 1
title: "Tools & Toolsets"
description: "Overview of Hermes Agent's tools — what's available, how toolsets work, and terminal backends"
---

# Tools & Toolsets

Tools are functions that extend the agent's capabilities. They're organized into logical **toolsets** that can be enabled or disabled per platform.

## Available Tools

Hermes ships with a broad built-in tool registry covering web search, browser automation, terminal execution, file editing, memory, delegation, scheduled tasks, Home Assistant, and more.

:::note
**Honcho cross-session memory** is available as a memory provider plugin (`plugins/memory/honcho/`), not as a built-in toolset. See [Plugins](./plugins.md) for installation.
:::

High-level categories:

| Category | Examples | Description |
|----------|----------|-------------|
| **Web** | `web_search`, `web_extract` | Search the web and extract page content. |
| **X Search** | `x_search` | Search X (Twitter) posts and threads via xAI's built-in `x_search` Responses tool — gated on xAI credentials (SuperGrok OAuth or `XAI_API_KEY`); off by default, opt in via `hermes tools` → 🐦 X (Twitter) Search. |
| **Terminal & Files** | `terminal`, `process`, `read_file`, `patch` | Execute commands and manipulate files. |
| **Browser** | `browser_navigate`, `browser_snapshot`, `browser_vision` | Interactive browser automation with text and vision support. |
| **Media** | `vision_analyze`, `image_generate`, `text_to_speech` | Multimodal analysis and generation. |
| **Agent orchestration** | `todo`, `clarify`, `execute_code`, `delegate_task` | Planning, clarification, code execution, and subagent delegation. |
| **Memory & recall** | `memory`, `session_search` | Persistent memory and session search. |
| **Automation** | `cronjob` | Scheduled tasks with create/list/update/pause/resume/run/remove actions. Outbound delivery is handled by cron's own delivery, the `hermes send` CLI, and the gateway notifier — not by an agent-callable tool. |
| **Integrations** | `ha_*`, MCP server tools | Home Assistant, MCP, and other integrations. |

For the authoritative code-derived registry, see [Built-in Tools Reference](/reference/tools-reference) and [Toolsets Reference](/reference/toolsets-reference).

:::tip Nous Tool Gateway
Paid [Nous Portal](https://portal.nousresearch.com) subscribers can use web search, image generation, TTS, and browser automation through the **[Tool Gateway](tool-gateway.md)** — no separate API keys needed. Run `hermes model` to enable it, or configure individual tools with `hermes tools`.
:::

## Using Toolsets

```bash
# Use specific toolsets
hermes chat --toolsets "web,terminal"

# See all available tools
hermes tools

# Configure tools per platform (interactive)
hermes tools
```

Common toolsets include `web`, `search`, `terminal`, `file`, `browser`, `vision`, `image_gen`, `skills`, `tts`, `todo`, `memory`, `session_search`, `cronjob`, `code_execution`, `delegation`, `clarify`, `homeassistant`, `messaging`, `spotify`, `discord`, `discord_admin`, `debugging`, and `safe`.

See [Toolsets Reference](/reference/toolsets-reference) for the full set, including platform presets such as `hermes-cli`, `hermes-telegram`, and dynamic MCP toolsets like `mcp-<server>`.

## Terminal Backends

The terminal tool can execute commands in different environments:

| Backend | Description | Use Case |
|---------|-------------|----------|
| `local` | Run on your machine (default) | Development, trusted tasks |
| `docker` | Isolated containers | Security, reproducibility |
| `ssh` | Remote server | Sandboxing, keep agent away from its own code |
| `singularity` | HPC containers | Cluster computing, rootless |
| `modal` | Cloud execution | Serverless, scale |
| `daytona` | Cloud sandbox workspace | Persistent remote dev environments |

### Configuration

```yaml
# In ~/.hermes/config.yaml
terminal:
  backend: local    # or: docker, ssh, singularity, modal, daytona
  cwd: "."          # Working directory
  timeout: 180      # Command timeout in seconds
```

### Docker Backend

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

**One persistent container, shared across the whole process.** Hermes starts a single long-lived container on first use (`docker run -d ... sleep 2h`) and routes every terminal, file, and `execute_code` call through `docker exec` into that same container. Working-directory changes, installed packages, environment tweaks, and files written to `/workspace` all carry over from one tool call to the next, across `/new`, `/reset`, and `delegate_task` subagents, for the lifetime of the Hermes process. The container is stopped and removed on shutdown.

This means the Docker backend behaves like a persistent sandbox VM, not a fresh container per command. If you `pip install foo` once, it's there for the rest of the session. If you `cd /workspace/project`, subsequent `ls` calls see that directory. See [Configuration → Docker Backend](../configuration.md#docker-backend) for the full lifecycle details and the `container_persistent` flag that controls whether `/workspace` and `/root` survive across Hermes restarts.

### SSH Backend

Recommended for security — agent can't modify its own code:

```yaml
terminal:
  backend: ssh
```
```bash
# Set credentials in ~/.hermes/.env
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=myuser
TERMINAL_SSH_KEY=~/.ssh/id_rsa
```

### Singularity/Apptainer

```bash
# Pre-build SIF for parallel workers
apptainer build ~/python.sif docker://python:3.11-slim

# Configure
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

### Modal (Serverless Cloud)

```bash
uv pip install modal
modal setup
hermes config set terminal.backend modal
```

### Container Resources

Configure CPU, memory, disk, and persistence for all container backends:

```yaml
terminal:
  backend: docker  # or singularity, modal, daytona
  container_cpu: 1              # CPU cores (default: 1)
  container_memory: 5120        # Memory in MB (default: 5GB)
  container_disk: 51200         # Disk in MB (default: 50GB)
  container_persistent: true    # Persist filesystem across sessions (default: true)
```

When `container_persistent: true`, installed packages, files, and config survive across sessions.

### Container Security

All container backends run with security hardening:

- Read-only root filesystem (Docker)
- All Linux capabilities dropped
- No privilege escalation
- PID limits (256 processes)
- Full namespace isolation
- Persistent workspace via volumes, not writable root layer

Docker can optionally receive an explicit env allowlist via `terminal.docker_forward_env`, but forwarded variables are visible to commands inside the container and should be treated as exposed to that session.

## Background Process Management

Start background processes and manage them:

```python
terminal(command="pytest -v tests/", background=true)
# Returns: {"session_id": "proc_abc123", "pid": 12345}

# Then manage with the process tool:
process(action="list")       # Show all running processes
process(action="poll", session_id="proc_abc123")   # Check status
process(action="wait", session_id="proc_abc123")   # Block until done
process(action="log", session_id="proc_abc123")    # Full output
process(action="kill", session_id="proc_abc123")   # Terminate
process(action="write", session_id="proc_abc123", data="y")  # Send input
```

PTY mode (`pty=true`) enables interactive CLI tools like Codex and Claude Code.

## Sudo Support

If a command needs sudo, you'll be prompted for your password (cached for the session). Or set `SUDO_PASSWORD` in `~/.hermes/.env`.

:::warning
On messaging platforms, if sudo fails, the output includes a tip to add `SUDO_PASSWORD` to `~/.hermes/.env`.
:::

---

# SOURCE: website/docs/user-guide/features/context-files.md

---
sidebar_position: 8
title: "Context Files"
description: "Project context files — .hermes.md, AGENTS.md, CLAUDE.md, global SOUL.md, and .cursorrules — automatically injected into every conversation"
---

# Context Files

Hermes Agent automatically discovers and loads context files that shape how it behaves. Some are project-local and discovered from your working directory. `SOUL.md` is now global to the Hermes instance and is loaded from `HERMES_HOME` only.

## Supported Context Files

| File | Purpose | Discovery |
|------|---------|-----------| 
| **.hermes.md** / **HERMES.md** | Project instructions (highest priority) | Walks to git root |
| **AGENTS.md** | Project instructions, conventions, architecture | CWD at startup + subdirectories progressively |
| **CLAUDE.md** | Claude Code context files (also detected) | CWD at startup + subdirectories progressively |
| **SOUL.md** | Global personality and tone customization for this Hermes instance | `HERMES_HOME/SOUL.md` only |
| **.cursorrules** | Cursor IDE coding conventions | CWD only |
| **.cursor/rules/*.mdc** | Cursor IDE rule modules | CWD only |

:::info Priority system
Only **one** project context type is loaded per session (first match wins): `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`. **SOUL.md** is always loaded independently as the agent identity (slot #1).
:::

## AGENTS.md

`AGENTS.md` is the primary project context file. It tells the agent how your project is structured, what conventions to follow, and any special instructions.

### Progressive Subdirectory Discovery

At session start, Hermes loads the `AGENTS.md` from your working directory into the system prompt. As the agent navigates into subdirectories during the session (via `read_file`, `terminal`, `search_files`, etc.), it **progressively discovers** context files in those directories and injects them into the conversation at the moment they become relevant.

```
my-project/
├── AGENTS.md              ← Loaded at startup (system prompt)
├── frontend/
│   └── AGENTS.md          ← Discovered when agent reads frontend/ files
├── backend/
│   └── AGENTS.md          ← Discovered when agent reads backend/ files
└── shared/
    └── AGENTS.md          ← Discovered when agent reads shared/ files
```

This approach has two advantages over loading everything at startup:
- **No system prompt bloat** — subdirectory hints only appear when needed
- **Prompt cache preservation** — the system prompt stays stable across turns

Each subdirectory is checked at most once per session. The discovery also walks up parent directories, so reading `backend/src/main.py` will discover `backend/AGENTS.md` even if `backend/src/` has no context file of its own.

:::info
Subdirectory context files go through the same [security scan](#security-prompt-injection-protection) as startup context files. Malicious files are blocked.
:::

### Example AGENTS.md

```markdown
# Project Context

This is a Next.js 14 web application with a Python FastAPI backend.

## Architecture
- Frontend: Next.js 14 with App Router in `/frontend`
- Backend: FastAPI in `/backend`, uses SQLAlchemy ORM
- Database: PostgreSQL 16
- Deployment: Docker Compose on a Hetzner VPS

## Conventions
- Use TypeScript strict mode for all frontend code
- Python code follows PEP 8, use type hints everywhere
- All API endpoints return JSON with `{data, error, meta}` shape
- Tests go in `__tests__/` directories (frontend) or `tests/` (backend)

## Important Notes
- Never modify migration files directly — use Alembic commands
- The `.env.local` file has real API keys, don't commit it
- Frontend port is 3000, backend is 8000, DB is 5432
```

## SOUL.md

`SOUL.md` controls the agent's personality, tone, and communication style. See the [Personality](/user-guide/features/personality) page for full details.

**Location:**

- `~/.hermes/SOUL.md`
- or `$HERMES_HOME/SOUL.md` if you run Hermes with a custom home directory

Important details:

- Hermes seeds a default `SOUL.md` automatically if one does not exist yet
- Hermes loads `SOUL.md` only from `HERMES_HOME`
- Hermes does not probe the working directory for `SOUL.md`
- If the file is empty, nothing from `SOUL.md` is added to the prompt
- If the file has content, the content is injected verbatim after scanning and truncation

## .cursorrules

Hermes is compatible with Cursor IDE's `.cursorrules` file and `.cursor/rules/*.mdc` rule modules. If these files exist in your project root and no higher-priority context file (`.hermes.md`, `AGENTS.md`, or `CLAUDE.md`) is found, they're loaded as the project context.

This means your existing Cursor conventions automatically apply when using Hermes.

## How Context Files Are Loaded

### At startup (system prompt)

Context files are loaded by `build_context_files_prompt()` in `agent/prompt_builder.py`:

1. **Scan working directory** — checks for `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules` (first match wins)
2. **Content is read** — each file is read as UTF-8 text
3. **Security scan** — content is checked for prompt injection patterns
4. **Truncation** — files exceeding `context_file_max_chars` characters (default 20,000) are head/tail truncated (70% head, 20% tail, with a marker in the middle)
5. **Assembly** — all sections are combined under a `# Project Context` header
6. **Injection** — the assembled content is added to the system prompt

### During the session (progressive discovery)

`SubdirectoryHintTracker` in `agent/subdirectory_hints.py` watches tool call arguments for file paths:

1. **Path extraction** — after each tool call, file paths are extracted from arguments (`path`, `workdir`, shell commands)
2. **Ancestor walk** — the directory and up to 5 parent directories are checked (stopping at already-visited directories)
3. **Hint loading** — if an `AGENTS.md`, `CLAUDE.md`, or `.cursorrules` is found, it's loaded (first match per directory)
4. **Security scan** — same prompt injection scan as startup files
5. **Truncation** — capped at 8,000 characters per file
6. **Injection** — appended to the tool result, so the model sees it in context naturally

The final prompt section looks roughly like:

```text
# Project Context

The following project context files have been loaded and should be followed:

## AGENTS.md

[Your AGENTS.md content here]

## .cursorrules

[Your .cursorrules content here]

[Your SOUL.md content here]
```

Notice that SOUL content is inserted directly, without extra wrapper text.

## Security: Prompt Injection Protection

All context files are scanned for potential prompt injection before being included. The scanner checks for:

- **Instruction override attempts**: "ignore previous instructions", "disregard your rules"
- **Deception patterns**: "do not tell the user"
- **System prompt overrides**: "system prompt override"
- **Hidden HTML comments**: `<!-- ignore instructions -->`
- **Hidden div elements**: `<div style="display:none">`
- **Credential exfiltration**: `curl ... $API_KEY`
- **Secret file access**: `cat .env`, `cat credentials`
- **Invisible characters**: zero-width spaces, bidirectional overrides, word joiners

If any threat pattern is detected, the file is blocked:

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

:::warning
This scanner protects against common injection patterns, but it's not a substitute for reviewing context files in shared repositories. Always validate AGENTS.md content in projects you didn't author.
:::

## Size Limits

| Limit | Value |
|-------|-------|
| Max chars per file | `context_file_max_chars` (default 20,000, ~7,000 tokens) |
| Head truncation ratio | 70% |
| Tail truncation ratio | 20% |
| Truncation marker | 10% (shows char counts and suggests using file tools) |

When a file exceeds the configured limit, the truncation message reads:

```
[...truncated AGENTS.md: kept 14000+4000 of 25000 chars. Use file tools to read the full file.]
```

## Tips for Effective Context Files

:::tip Best practices for AGENTS.md
1. **Keep it concise** — stay under your configured `context_file_max_chars`; the agent reads it every turn
2. **Structure with headers** — use `##` sections for architecture, conventions, important notes
3. **Include concrete examples** — show preferred code patterns, API shapes, naming conventions
4. **Mention what NOT to do** — "never modify migration files directly"
5. **List key paths and ports** — the agent uses these for terminal commands
6. **Update as the project evolves** — stale context is worse than no context
:::

### Per-Subdirectory Context

For monorepos, put subdirectory-specific instructions in nested AGENTS.md files:

```markdown
<!-- frontend/AGENTS.md -->
# Frontend Context

- Use `pnpm` not `npm` for package management
- Components go in `src/components/`, pages in `src/app/`
- Use Tailwind CSS, never inline styles
- Run tests with `pnpm test`
```

```markdown
<!-- backend/AGENTS.md -->
# Backend Context

- Use `poetry` for dependency management
- Run the dev server with `poetry run uvicorn main:app --reload`
- All endpoints need OpenAPI docstrings
- Database models are in `models/`, schemas in `schemas/`
```

---

# SOURCE: website/docs/user-guide/features/context-references.md

---
sidebar_position: 9
sidebar_label: "Context References"
title: "Context References"
description: "Inline @-syntax for attaching files, folders, git diffs, and URLs directly into your messages"
---

# Context References

Type `@` followed by a reference to inject content directly into your message. Hermes expands the reference inline and appends the content under an `--- Attached Context ---` section.

## Supported References

| Syntax | Description |
|--------|-------------|
| `@file:path/to/file.py` | Inject file contents |
| `@file:path/to/file.py:10-25` | Inject specific line range (1-indexed, inclusive) |
| `@folder:path/to/dir` | Inject directory tree listing with file metadata |
| `@diff` | Inject `git diff` (unstaged working tree changes) |
| `@staged` | Inject `git diff --staged` (staged changes) |
| `@git:5` | Inject last N commits with patches (max 10) |
| `@url:https://example.com` | Fetch and inject web page content |

## Usage Examples

```text
Review @file:src/main.py and suggest improvements

What changed? @diff

Compare @file:old_config.yaml and @file:new_config.yaml

What's in @folder:src/components?

Summarize this article @url:https://arxiv.org/abs/2301.00001
```

Multiple references work in a single message:

```text
Check @file:main.py, and also @file:test.py.
```

Trailing punctuation (`,`, `.`, `;`, `!`, `?`) is automatically stripped from reference values.

## CLI Tab Completion

In the interactive CLI, typing `@` triggers autocomplete:

- `@` shows all reference types (`@diff`, `@staged`, `@file:`, `@folder:`, `@git:`, `@url:`)
- `@file:` and `@folder:` trigger filesystem path completion with file size metadata
- Bare `@` followed by partial text shows matching files and folders from the current directory

## Line Ranges

The `@file:` reference supports line ranges for precise content injection:

```text
@file:src/main.py:42        # Single line 42
@file:src/main.py:10-25     # Lines 10 through 25 (inclusive)
```

Lines are 1-indexed. Invalid ranges are silently ignored (full file is returned).

## Size Limits

Context references are bounded to prevent overwhelming the model's context window:

| Threshold | Value | Behavior |
|-----------|-------|----------|
| Soft limit | 25% of context length | Warning appended, expansion proceeds |
| Hard limit | 50% of context length | Expansion refused, original message returned unchanged |
| Folder entries | 200 files max | Excess entries replaced with `- ...` |
| Git commits | 10 max | `@git:N` clamped to range [1, 10] |

## Security

### Sensitive Path Blocking

These paths are always blocked from `@file:` references to prevent credential exposure:

- SSH keys and config: `~/.ssh/id_rsa`, `~/.ssh/id_ed25519`, `~/.ssh/authorized_keys`, `~/.ssh/config`
- Shell profiles: `~/.bashrc`, `~/.zshrc`, `~/.profile`, `~/.bash_profile`, `~/.zprofile`
- Credential files: `~/.netrc`, `~/.pgpass`, `~/.npmrc`, `~/.pypirc`
- Hermes env: `$HERMES_HOME/.env`

These directories are fully blocked (any file inside):
- `~/.ssh/`, `~/.aws/`, `~/.gnupg/`, `~/.kube/`, `$HERMES_HOME/skills/.hub/`

### Path Traversal Protection

All paths are resolved relative to the working directory. References that resolve outside the allowed workspace root are rejected.

### Binary File Detection

Binary files are detected via MIME type and null-byte scanning. Known text extensions (`.py`, `.md`, `.json`, `.yaml`, `.toml`, `.js`, `.ts`, etc.) bypass MIME-based detection. Binary files are rejected with a warning.

## Platform Availability

Context references are primarily a **CLI feature**. They work in the interactive CLI where `@` triggers tab completion and references are expanded before the message is sent to the agent.

In **messaging platforms** (Telegram, Discord, etc.), the `@` syntax is not expanded by the gateway — messages are passed through as-is. The agent itself can still reference files via the `read_file`, `search_files`, and `web_extract` tools.

## Interaction with Context Compression

When conversation context is compressed, the expanded reference content is included in the compression summary. This means:

- Large file contents injected via `@file:` contribute to context usage
- If the conversation is later compressed, the file content is summarized (not preserved verbatim)
- For very large files, consider using line ranges (`@file:main.py:100-200`) to inject only relevant sections

## Common Patterns

```text
# Code review workflow
Review @diff and check for security issues

# Debug with context
This test is failing. Here's the test @file:tests/test_auth.py
and the implementation @file:src/auth.py:50-80

# Project exploration
What does this project do? @folder:src @file:README.md

# Research
Compare the approaches in @url:https://arxiv.org/abs/2301.00001
and @url:https://arxiv.org/abs/2301.00002
```

## Error Handling

Invalid references produce inline warnings rather than failures:

| Condition | Behavior |
|-----------|----------|
| File not found | Warning: "file not found" |
| Binary file | Warning: "binary files are not supported" |
| Folder not found | Warning: "folder not found" |
| Git command fails | Warning with git stderr |
| URL returns no content | Warning: "no content extracted" |
| Sensitive path | Warning: "path is a sensitive credential file" |
| Path outside workspace | Warning: "path is outside the allowed workspace" |

---

# SOURCE: website/docs/user-guide/features/personality.md

---
sidebar_position: 9
title: "Personality & SOUL.md"
description: "Customize Hermes Agent's personality with a global SOUL.md, built-in personalities, and custom persona definitions"
---

# Personality & SOUL.md

Hermes Agent's personality is fully customizable. `SOUL.md` is the **primary identity** — it's the first thing in the system prompt and defines who the agent is.

- `SOUL.md` — a durable persona file that lives in `HERMES_HOME` and serves as the agent's identity (slot #1 in the system prompt)
- built-in or custom `/personality` presets — session-level system-prompt overlays

If you want to change who Hermes is — or replace it with an entirely different agent persona — edit `SOUL.md`.

## How SOUL.md works now

Hermes now seeds a default `SOUL.md` automatically in:

```text
~/.hermes/SOUL.md
```

More precisely, it uses the current instance's `HERMES_HOME`, so if you run Hermes with a custom home directory, it will use:

```text
$HERMES_HOME/SOUL.md
```

### Important behavior

- **SOUL.md is the agent's primary identity.** It occupies slot #1 in the system prompt, replacing the hardcoded default identity.
- Hermes creates a starter `SOUL.md` automatically if one does not exist yet
- Existing user `SOUL.md` files are never overwritten
- Hermes loads `SOUL.md` only from `HERMES_HOME`
- Hermes does not look in the current working directory for `SOUL.md`
- If `SOUL.md` exists but is empty, or cannot be loaded, Hermes falls back to a built-in default identity
- If `SOUL.md` has content, that content is injected verbatim after security scanning and truncation
- SOUL.md is **not** duplicated in the context files section — it appears only once, as the identity

That makes `SOUL.md` a true per-user or per-instance identity, not just an additive layer.

## Why this design

This keeps personality predictable.

If Hermes loaded `SOUL.md` from whatever directory you happened to launch it in, your personality could change unexpectedly between projects. By loading only from `HERMES_HOME`, the personality belongs to the Hermes instance itself.

That also makes it easier to teach users:
- "Edit `~/.hermes/SOUL.md` to change Hermes' default personality."

## Where to edit it

For most users:

```bash
~/.hermes/SOUL.md
```

If you use a custom home:

```bash
$HERMES_HOME/SOUL.md
```

## What should go in SOUL.md?

Use it for durable voice and personality guidance, such as:
- tone
- communication style
- level of directness
- default interaction style
- what to avoid stylistically
- how Hermes should handle uncertainty, disagreement, or ambiguity

Use it less for:
- one-off project instructions
- file paths
- repo conventions
- temporary workflow details

Those belong in `AGENTS.md`, not `SOUL.md`.

## Good SOUL.md content

A good SOUL file is:
- stable across contexts
- broad enough to apply in many conversations
- specific enough to materially shape the voice
- focused on communication and identity, not task-specific instructions

### Example

```markdown
# Personality

You are a pragmatic senior engineer with strong taste.
You optimize for truth, clarity, and usefulness over politeness theater.

## Style
- Be direct without being cold
- Prefer substance over filler
- Push back when something is a bad idea
- Admit uncertainty plainly
- Keep explanations compact unless depth is useful

## What to avoid
- Sycophancy
- Hype language
- Repeating the user's framing if it's wrong
- Overexplaining obvious things

## Technical posture
- Prefer simple systems over clever systems
- Care about operational reality, not idealized architecture
- Treat edge cases as part of the design, not cleanup
```

## What Hermes injects into the prompt

`SOUL.md` content goes directly into slot #1 of the system prompt — the agent identity position. No wrapper language is added around it.

The content goes through:
- prompt-injection scanning
- truncation if it is too large

If the file is empty, whitespace-only, or cannot be read, Hermes falls back to a built-in default identity ("You are Hermes Agent, an intelligent AI assistant created by Nous Research..."). This fallback also applies when `skip_context_files` is set (e.g., in subagent/delegation contexts).

## Security scanning

`SOUL.md` is scanned like other context-bearing files for prompt injection patterns before inclusion.

That means you should still keep it focused on persona/voice rather than trying to sneak in strange meta-instructions.

## SOUL.md vs AGENTS.md

This is the most important distinction.

### SOUL.md
Use for:
- identity
- tone
- style
- communication defaults
- personality-level behavior

### AGENTS.md
Use for:
- project architecture
- coding conventions
- tool preferences
- repo-specific workflows
- commands, ports, paths, deployment notes

A useful rule:
- if it should follow you everywhere, it belongs in `SOUL.md`
- if it belongs to a project, it belongs in `AGENTS.md`

## SOUL.md vs `/personality`

`SOUL.md` is your durable default personality.

`/personality` is a session-level overlay that changes or supplements the current system prompt.

So:
- `SOUL.md` = baseline voice
- `/personality` = temporary mode switch

Examples:
- keep a pragmatic default SOUL, then use `/personality teacher` for a tutoring conversation
- keep a concise SOUL, then use `/personality creative` for brainstorming

## Built-in personalities

Hermes ships with built-in personalities you can switch to with `/personality`.

| Name | Description |
|------|-------------|
| **helpful** | Friendly, general-purpose assistant |
| **concise** | Brief, to-the-point responses |
| **technical** | Detailed, accurate technical expert |
| **creative** | Innovative, outside-the-box thinking |
| **teacher** | Patient educator with clear examples |
| **kawaii** | Cute expressions, sparkles, and enthusiasm ★ |
| **catgirl** | Neko-chan with cat-like expressions, nya~ |
| **pirate** | Captain Hermes, tech-savvy buccaneer |
| **shakespeare** | Bardic prose with dramatic flair |
| **surfer** | Totally chill bro vibes |
| **noir** | Hard-boiled detective narration |
| **uwu** | Maximum cute with uwu-speak |
| **philosopher** | Deep contemplation on every query |
| **hype** | MAXIMUM ENERGY AND ENTHUSIASM!!! |

## Switching personalities with commands

### CLI

```text
/personality
/personality concise
/personality technical
```

### Messaging platforms

```text
/personality teacher
```

These are convenient overlays, but your global `SOUL.md` still gives Hermes its persistent default personality unless the overlay meaningfully changes it.

## Custom personalities in config

You can also define named custom personalities in `~/.hermes/config.yaml` under `agent.personalities`.

```yaml
agent:
  personalities:
    codereviewer: >
      You are a meticulous code reviewer. Identify bugs, security issues,
      performance concerns, and unclear design choices. Be precise and constructive.
```

Then switch to it with:

```text
/personality codereviewer
```

## Recommended workflow

A strong default setup is:

1. Keep a thoughtful global `SOUL.md` in `~/.hermes/SOUL.md`
2. Put project instructions in `AGENTS.md`
3. Use `/personality` only when you want a temporary mode shift

That gives you:
- a stable voice
- project-specific behavior where it belongs
- temporary control when needed

## How personality interacts with the full prompt

At a high level, the prompt stack includes:
1. **SOUL.md** (agent identity — or built-in fallback if SOUL.md is unavailable)
2. tool-aware behavior guidance
3. memory/user context
4. skills guidance
5. context files (`AGENTS.md`, `.cursorrules`)
6. timestamp
7. platform-specific formatting hints
8. optional system-prompt overlays such as `/personality`

`SOUL.md` is the foundation — everything else builds on top of it.

## Related docs

- [Context Files](/user-guide/features/context-files)
- [Configuration](/user-guide/configuration)
- [Tips & Best Practices](/guides/tips)
- [SOUL.md Guide](/guides/use-soul-with-hermes)

## CLI appearance vs conversational personality

Conversational personality and CLI appearance are separate:

- `SOUL.md`, `agent.system_prompt`, and `/personality` affect how Hermes speaks
- `display.skin` and `/skin` affect how Hermes looks in the terminal

For terminal appearance, see [Skins & Themes](./skins.md).
