# Open Design Setup & Configuration

Three ways to run Open Design, plus environment configuration.

## Option 1: Docker (Simplest)

No Node.js or pnpm needed.

```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design/deploy
cp .env.example .env
openssl rand -hex 32            # generate OD_API_TOKEN
# Paste into .env: OD_API_TOKEN=<generated>
docker compose up -d
# Open http://localhost:7456
```

### Docker Commands

```bash
docker compose logs -f         # view logs
docker compose restart         # restart
docker compose down            # stop
docker compose pull && docker compose up -d  # update
docker compose down -v         # remove all data
```

### Docker Environment (`deploy/.env`)

```env
OPEN_DESIGN_PORT=7456
OPEN_DESIGN_MEM_LIMIT=384m
OPEN_DESIGN_ALLOWED_ORIGINS=https://yourdomain.com
OPEN_DESIGN_IMAGE=ghcr.io/nexu-io/od:latest
OD_API_TOKEN=                  # required, generate with openssl
```

## Option 2: Dev Mode (Full Control)

Requires Node ~24 and pnpm 10.33.x.

```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design
corepack enable                 # selects pinned pnpm
pnpm install
pnpm tools-dev run web          # daemon + web foreground
# Open URL printed by tools-dev
```

### Dev Mode Commands

```bash
pnpm tools-dev                 # background mode
pnpm tools-dev start web       # daemon + web background
pnpm tools-dev restart         # restart all
pnpm tools-dev status          # inspect runtimes
pnpm tools-dev logs            # show logs
pnpm typecheck                 # type check
```

### Node Version

```bash
# nvm
nvm install 24 && nvm use 24

# fnm
fnm install 24 && fnm use 24

# verify
node --version                 # should be v24.x
corepack enable
corepack pnpm --version        # should be 10.33.2
```

## Option 3: Packaged App

Download from https://open-design.ai — native macOS/Windows desktop app.

## Supported Platforms

| Platform | Status |
|---|---|
| macOS | Full support |
| Linux | Full support |
| WSL2 | Full support |
| Windows native | Supported (best-effort) |

## Supported Coding Agents (17+)

Claude Code, Codex CLI, Cursor, GitHub Copilot, OpenCode, OpenClaw, Antigravity, Cline, Trae, Kimi CLI, Kiro, Pi Agent, Mistral Vibe CLI, Hermes Agent, DeepSeek Reasonix, Raven, Qwen, Aider, Amp, CodeBuddy, Mimo, AtomCode, Devin.

## Open Design Cloud

Official model service — one recharge for GPT, Claude, Gemini, DeepSeek (20+ models, billed by token usage). Optional — local BYOK works without it.

## Key Ports

| Service | Default Port |
|---|---|
| Web UI | 7456 |
| Daemon | varies (tools-dev manages) |

Override with: `--daemon-port` and `--web-port` flags on `tools-dev`.
