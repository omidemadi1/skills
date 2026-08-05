<!-- Sections in this file (in order):
  - user-guide/features/skills.md
  - user-guide/features/curator.md
  - guides/work-with-skills.md
  - developer-guide/creating-skills.md
  - reference/skills-catalog.md
  - reference/optional-skills-catalog.md
-->


---

# SOURCE: website/docs/user-guide/features/skills.md

---
sidebar_position: 2
title: "Skills System"
description: "On-demand knowledge documents — progressive disclosure, agent-managed skills, and the Skills Hub"
---

# Skills System

Skills are on-demand knowledge documents the agent can load when needed. They follow a **progressive disclosure** pattern to minimize token usage and are compatible with the [agentskills.io](https://agentskills.io/specification) open standard.

All skills live in **`~/.hermes/skills/`** — the primary directory and source of truth. On fresh install, bundled skills are copied from the repo. Hub-installed and agent-created skills also go here. The agent can modify or delete any skill.

You can also point Hermes at **external skill directories** — additional folders scanned alongside the local one. See [External Skill Directories](#external-skill-directories) below.

See also:

- [Bundled Skills Catalog](/reference/skills-catalog)
- [Official Optional Skills Catalog](/reference/optional-skills-catalog)

## Starting with a blank slate

By default every profile is seeded with the bundled skill catalog, and each `hermes update` adds any newly bundled skills. If you want a profile with **no bundled skills** — and that stays empty across updates — you have two paths:

**At install time** (applies to the default `~/.hermes` profile):

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --no-skills
```

**At profile-create time** (named profiles):

```bash
hermes profile create research --no-skills
```

**On an already-installed profile** (default or named), toggle it at runtime:

```bash
hermes skills opt-out            # stop future seeding — nothing on disk is touched
hermes skills opt-out --remove   # also delete UNMODIFIED bundled skills (confirms first)
hermes skills opt-in --sync      # undo: remove the marker and re-seed now
```

All three paths write a `.no-bundled-skills` marker into the profile directory. While the marker is present, the installer, `hermes update`, and any skill sync all skip bundled-skill seeding for that profile. Delete the marker (or run `hermes skills opt-in`) to re-enable.

:::note Safe by default
`hermes skills opt-out` only stops *future* seeding — it never deletes anything already on disk. The optional `--remove` flag deletes bundled skills **only** when they are unmodified (byte-identical to the version Hermes installed). Skills you have edited, skills installed from the hub, and skills you wrote yourself are always kept.
:::

## Using Skills

Every installed skill is automatically available as a slash command:

```bash
# In the CLI or any messaging platform:
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/plan design a rollout for migrating our auth provider

# Just the skill name loads it and lets the agent ask what you need:
/excalidraw
```

The bundled `plan` skill is a good example. Running `/plan [request]` loads the skill's instructions, telling Hermes to inspect context if needed, write a markdown implementation plan instead of executing the task, and save the result under `.hermes/plans/` relative to the active workspace/backend working directory.

You can also interact with skills through natural conversation:

```bash
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## Learning a skill from sources (`/learn`)

`/learn` is the fast way to turn something you already know — or a pile of
reference material — into a reusable skill, without hand-writing the
`SKILL.md`. It is open-ended: point it at *anything you can describe* and the
agent gathers the material with the tools it already has, then authors a skill
that follows the [house authoring standards](#skillmd-format) (≤60-char
description, the standard section order, Hermes-tool framing, no invented
commands).

```bash
# A local SDK or doc directory — read with read_file / search_files
/learn the REST client in ~/projects/acme-sdk, focus on auth + pagination

# An online doc page — fetched with web_extract
/learn https://docs.example.com/api/quickstart

# The workflow you just walked the agent through in this conversation
/learn how I just deployed the staging server

# Pasted notes / a described procedure
/learn filing an expense: open the portal, New > Expense, attach the receipt, submit
```

Because the live agent does the sourcing, `/learn` works the same in the CLI,
the messaging gateway, the TUI, and the dashboard — and on any terminal backend
(local, Docker, remote), since there is no separate ingestion engine. In the
**dashboard**, the Skills page has a **Learn a skill** button that opens a panel
with a directory field, a URL field, and an open-ended text box; it composes a
`/learn` request and runs it in chat.

There is no model-tool footprint: `/learn` builds a standards-guided prompt and
hands it to the agent as a normal turn. The agent saves the result with the
`skill_manage` tool, so the [write-approval gate](#gating-agent-skill-writes-skillswrite_approval)
applies if you have it on.

## Progressive Disclosure

Skills use a token-efficient loading pattern:

```
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)
Level 1: skill_view(name)        → Full content + metadata       (varies)
Level 2: skill_view(name, path)  → Specific reference file       (varies)
```

The agent only loads the full skill content when it actually needs it.

## SKILL.md Format

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]     # Optional — restrict to specific OS platforms
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # Optional — conditional activation (see below)
    requires_toolsets: [terminal]   # Optional — conditional activation (see below)
    config:                          # Optional — config.yaml settings
      - key: my.setting
        description: "What this controls"
        default: "value"
        prompt: "Prompt for setup"
---

# Skill Title

## When to Use
Trigger conditions for this skill.

## Procedure
1. Step one
2. Step two

## Pitfalls
- Known failure modes and fixes

## Verification
How to confirm it worked.
```

### Platform-Specific Skills

Skills can restrict themselves to specific operating systems using the `platforms` field:

| Value | Matches |
|-------|---------|
| `macos` | macOS (Darwin) |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS and Linux
```

When set, the skill is automatically hidden from the system prompt, `skills_list()`, and slash commands on incompatible platforms. If omitted, the skill loads on all platforms.

## Skill output and media delivery

When a skill response (or any agent response) includes a bare absolute path to a media file — for example `/home/user/screenshots/diagram.png` — the gateway auto-detects it, strips it from the visible text, and delivers the file natively to the user's chat (Telegram photo, Discord attachment, etc.) instead of leaving the raw path in the message.

For audio specifically, the `[[audio_as_voice]]` directive promotes audio files to native voice-message bubbles on platforms that support them (Telegram, WhatsApp).

### Forcing document-style delivery: `[[as_document]]`

Sometimes you want the **opposite** of inline preview: you want the file delivered as a downloadable attachment, not a re-compressed image bubble. The classic example is a high-resolution screenshot or chart — Telegram's `sendPhoto` recompresses it to ~200 KB at 1280 px, destroying readability. A 1-2 MB PNG sent via `sendDocument` keeps the original bytes intact.

If a response (or any text inside it — typically the last line) contains the literal directive `[[as_document]]`, every media path extracted from that response is delivered as a document/file attachment rather than an image bubble:

```
Here is your rendered chart:

/home/user/.hermes/cache/chart-q4-2025.png

[[as_document]]
```

The directive is stripped before delivery, so users never see it. Granularity is intentionally all-or-nothing per response: emit `[[as_document]]` once and every image path in the same response is delivered as a document. This mirrors the scope of `[[audio_as_voice]]`.

Use it from a skill when:

- You produce screenshots or charts the user needs as files (for editing in another tool, archiving, sharing intact).
- The default lossy preview would obscure detail (small text, pixel-accurate diagrams, color-sensitive renders).

Platforms without a separate document path (e.g. SMS) fall back to whatever attachment mechanism they have.

### Conditional Activation (Fallback Skills)

Skills can automatically show or hide themselves based on which tools are available in the current session. This is most useful for **fallback skills** — free or local alternatives that should only appear when a premium tool is unavailable.

```yaml
metadata:
  hermes:
    fallback_for_toolsets: [web]      # Show ONLY when these toolsets are unavailable
    requires_toolsets: [terminal]     # Show ONLY when these toolsets are available
    fallback_for_tools: [web_search]  # Show ONLY when these specific tools are unavailable
    requires_tools: [terminal]        # Show ONLY when these specific tools are available
```

| Field | Behavior |
|-------|----------|
| `fallback_for_toolsets` | Skill is **hidden** when the listed toolsets are available. Shown when they're missing. |
| `fallback_for_tools` | Same, but checks individual tools instead of toolsets. |
| `requires_toolsets` | Skill is **hidden** when the listed toolsets are unavailable. Shown when they're present. |
| `requires_tools` | Same, but checks individual tools. |

**Example:** The built-in `duckduckgo-search` skill uses `fallback_for_toolsets: [web]`. When you have `FIRECRAWL_API_KEY` set, the web toolset is available and the agent uses `web_search` — the DuckDuckGo skill stays hidden. If the API key is missing, the web toolset is unavailable and the DuckDuckGo skill automatically appears as a fallback.

Skills without any conditional fields behave exactly as before — they're always shown.

## Secure Setup on Load

Skills can declare required environment variables without disappearing from discovery:

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

When a missing value is encountered, Hermes asks for it securely only when the skill is actually loaded in the local CLI. You can skip setup and keep using the skill. Messaging surfaces never ask for secrets in chat — they tell you to use `hermes setup` or `~/.hermes/.env` locally instead.

Once set, declared env vars are **automatically passed through** to `execute_code` and `terminal` sandboxes — the skill's scripts can use `$TENOR_API_KEY` directly. For non-skill env vars, use the `terminal.env_passthrough` config option. See [Environment Variable Passthrough](/user-guide/security#environment-variable-passthrough) for details.

### Skill Config Settings

Skills can also declare non-secret config settings (paths, preferences) stored in `config.yaml`:

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
```

Settings are stored under `skills.config` in your config.yaml. `hermes config migrate` prompts for unconfigured settings, and `hermes config show` displays them. When a skill loads, its resolved config values are injected into the context so the agent knows the configured values automatically.

See [Skill Settings](/user-guide/configuration#skill-settings) and [Creating Skills — Config Settings](/developer-guide/creating-skills#config-settings-configyaml) for details.

## Skill Directory Structure

```text
~/.hermes/skills/                  # Single source of truth
├── mlops/                         # Category directory
│   ├── axolotl/
│   │   ├── SKILL.md               # Main instructions (required)
│   │   ├── references/            # Additional docs
│   │   ├── templates/             # Output formats
│   │   ├── scripts/               # Helper scripts callable from the skill
│   │   └── assets/                # Supplementary files
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent-created skill
│       ├── SKILL.md
│       └── references/
├── .hub/                          # Skills Hub state
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # Tracks seeded bundled skills
```

## External Skill Directories

If you maintain skills outside of Hermes — for example, a shared `~/.agents/skills/` directory used by multiple AI tools — you can tell Hermes to scan those directories too.

Add `external_dirs` under the `skills` section in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```

Paths support `~` expansion and `${VAR}` environment variable substitution.

### How it works

- **Create locally, update in place**: New agent-created skills are written to `~/.hermes/skills/`. Existing skills are modified where they are found, including skills under `external_dirs`, when the agent uses `skill_manage` actions such as `patch`, `edit`, `write_file`, `remove_file`, or `delete`.
- **External dirs are not a write-protection boundary**: If an external skill directory is writable by the Hermes process, agent-managed skill updates can change files in that directory. Use filesystem permissions or a separate profile/toolset setup if shared external skills must stay read-only.
- **Local precedence**: If the same skill name exists in both the local dir and an external dir, the local version wins.
- **Full integration**: External skills appear in the system prompt index, `skills_list`, `skill_view`, and as `/skill-name` slash commands — no different from local skills.
- **Non-existent paths are silently skipped**: If a configured directory doesn't exist, Hermes ignores it without errors. Useful for optional shared directories that may not be present on every machine.

### Example

```text
~/.hermes/skills/               # Local (primary, read-write)
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # External (shared, mutable if writable)
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```

All four skills appear in your skill index. If you create a new skill called `my-custom-workflow` locally, it shadows the external version.

## Skill Bundles

Skill bundles are tiny YAML files that group several skills under a single slash command. When you run `/<bundle-name>`, every skill listed in the bundle loads at once — useful when a particular task always benefits from the same set of skills together.

### Quick example

```bash
# Create a bundle for backend feature work
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "Backend feature work — review, test, PR workflow"
```

Then in the CLI or any gateway platform:

```
/backend-dev refactor the auth middleware
```

The agent receives all three skills loaded into one user message, with any text after the slash command attached as a user instruction.

### YAML schema

Bundles live in **`~/.hermes/skill-bundles/<slug>.yaml`** and look like this:

```yaml
name: backend-dev
description: Backend feature work — review, test, PR workflow.
skills:
  - github-code-review
  - test-driven-development
  - github-pr-workflow
instruction: |
  Always start by writing failing tests, then implement.
  Open the PR through the standard workflow with co-author tags.
```

Fields:
- `name` (optional — defaults to the filename stem) — the bundle's display name. Normalized to a hyphen slug for the slash command (`Backend Dev` → `/backend-dev`).
- `description` (optional) — short text shown in `/bundles` and `hermes bundles list`.
- `skills` (required, non-empty list) — skill names or paths relative to your skills directory. Use the same identifier you'd pass to `/<skill-name>`.
- `instruction` (optional) — extra guidance prepended to the loaded skill content. Useful for codifying "how we always use these together."

### Managing bundles

```bash
# List all installed bundles
hermes bundles list

# Inspect one bundle
hermes bundles show backend-dev

# Create a bundle interactively (omit --skill flags to enter them one per line)
hermes bundles create research

# Overwrite an existing bundle
hermes bundles create backend-dev --skill ... --force

# Delete a bundle
hermes bundles delete backend-dev

# Re-scan ~/.hermes/skill-bundles/ and report changes
hermes bundles reload
```

From inside a chat session, `/bundles` lists every installed bundle and its skills.

### Behavior

- **Bundles take precedence over individual skills** when slugs collide. If you name a bundle `research` and you also have a skill called `research`, `/research` invokes the bundle. This is intentional — you opted into the bundle by naming it.
- **Missing skills are skipped, not fatal.** If a bundle lists `skill-foo` and you haven't installed it, the bundle still loads the skills that do resolve, and the agent gets a note listing what was skipped.
- **Bundles work in every surface** — interactive CLI, TUI, dashboard chat, and every gateway platform (Telegram, Discord, Slack, …) — because dispatch is centralized in the same place as individual skill commands.
- **Bundles do not invalidate the prompt cache.** They generate a fresh user message at invocation time, the same way `/<skill-name>` does — no system prompt mutation.

### When bundles beat installing each skill manually

Use a bundle when:
- You always pair the same skills for a recurring task (`/backend-dev`, `/release-prep`, `/incident-response`).
- You want a one-character-shorter mental model than typing several `/skill` invocations in a row.
- You want to ship a team-wide "task profile" by checking the bundle YAML into a shared dotfiles repo and symlinking it into `~/.hermes/skill-bundles/`.

A bundle is just a YAML alias — it doesn't install skills for you. The skills themselves must already be present (in `~/.hermes/skills/` or an external skill directory). Otherwise the bundle invocation just skips the missing ones.

## Agent-Managed Skills (skill_manage tool)

The agent can create, update, and delete its own skills via the `skill_manage` tool. This is the agent's **procedural memory** — when it figures out a non-trivial workflow, it saves the approach as a skill for future reuse.

Skills and memory work together in the self-improvement loop: memory stores
small durable facts that should always be in context, while skills store longer
procedures that should load only when relevant. The background review can
suggest or stage skill changes after a session, but the write-approval gate
below lets you require human review before those changes land.

### When the Agent Creates Skills

- After completing a complex task (5+ tool calls) successfully
- When it hit errors or dead ends and found the working path
- When the user corrected its approach
- When it discovered a non-trivial workflow

### Actions

| Action | Use for | Key params |
|--------|---------|------------|
| `create` | New skill from scratch | `name`, `content` (full SKILL.md), optional `category` |
| `patch` | Targeted fixes (preferred) | `name`, `old_string`, `new_string` |
| `edit` | Major structural rewrites | `name`, `content` (full SKILL.md replacement) |
| `delete` | Remove a skill entirely | `name` |
| `write_file` | Add/update supporting files | `name`, `file_path`, `file_content` |
| `remove_file` | Remove a supporting file | `name`, `file_path` |

:::tip
The `patch` action is preferred for updates — it's more token-efficient than `edit` because only the changed text appears in the tool call.
:::

### Gating agent skill writes (`skills.write_approval`)

By default the agent writes skills freely — including from the [background
self-improvement review](/user-guide/features/memory#controlling-memory-writes-write_approval)
that runs after a turn. If you'd rather approve every skill write first
(small models that misjudge what they learned, secure environments, or just
wanting eyes on the self-improvement loop), turn on the write-approval gate:

```yaml
skills:
  write_approval: false     # false = write freely (default) | true = require approval
```

When `write_approval: true`, every `skill_manage` write (create / edit /
patch / delete / write_file / remove_file) is **staged** instead of committed —
a SKILL.md is too large to review inline, so staging applies regardless of
whether the write came from a foreground turn or the background review.
Staged writes survive restarts under `~/.hermes/pending/skills/` and are
reviewed with the same familiar approve/deny flow as dangerous commands:

```
/skills pending             # list staged skill writes + a one-line gist each
/skills diff <id>           # full unified diff (best viewed in CLI or dashboard)
/skills approve <id>        # apply it (or 'all')
/skills reject <id>         # drop it (or 'all')
/skills approval on         # turn the gate on (or 'off') and persist it
```

The review surface works in the interactive CLI and on messaging platforms
(diff output is truncated for chat bubbles — read the full diff on the CLI or
in the pending JSON file). Memory writes have the same gate under
`memory.write_approval` — see [Controlling memory writes](/user-guide/features/memory#controlling-memory-writes-write_approval).

> The separate `skills.guard_agent_created` setting is a content scanner
> (dangerous-pattern heuristics), not an approval gate — the two are
> independent. See [Guard on agent-created skill writes](/user-guide/configuration#guard-on-agent-created-skill-writes).

## Skills Hub

Browse, search, install, and manage skills from online registries, `skills.sh`, direct well-known skill endpoints, and official optional skills.

### Common commands

```bash
hermes skills browse                              # Browse all hub skills (official first)
hermes skills browse --source official            # Browse only official optional skills
hermes skills search kubernetes                   # Search all sources
hermes skills search react --source skills-sh     # Search the skills.sh directory
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect openai/skills/k8s           # Preview before installing
hermes skills install openai/skills/k8s           # Install with security scan
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install https://sharethis.chat/SKILL.md              # Direct URL (single-file SKILL.md)
hermes skills install https://example.com/SKILL.md --name my-skill # Override name when frontmatter has none
hermes skills list --source hub                   # List hub-installed skills
hermes skills check                               # Check installed hub skills for upstream updates
hermes skills update                              # Reinstall hub skills with upstream changes when needed
hermes skills audit                               # Re-scan all hub skills for security
hermes skills uninstall k8s                       # Remove a hub skill
hermes skills reset google-workspace              # Un-stick a bundled skill from "user-modified" (see below)
hermes skills reset google-workspace --restore    # Also restore the bundled version, deleting your local edits
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # Export skill config
hermes skills tap add myorg/skills-repo           # Add a custom GitHub source
```

### Supported hub sources

| Source | Example | Notes |
|--------|---------|-------|
| `official` | `official/security/1password` | Optional skills shipped with Hermes. |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | Searchable via `hermes skills search <query> --source skills-sh`. Hermes resolves alias-style skills when the skills.sh slug differs from the repo folder. |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | Skills served directly from `/.well-known/skills/index.json` on a website. Search using the site or docs URL. |
| `url` | `https://sharethis.chat/SKILL.md` | Direct HTTP(S) URL to a single-file `SKILL.md`. Name resolution: frontmatter → URL slug → interactive prompt → `--name` flag. |
| `github` | `openai/skills/k8s` | Direct GitHub repo/path installs and custom taps. |
| `clawhub`, `lobehub`, `browse-sh` | Source-specific identifiers | Community or marketplace integrations. |

### Integrated hubs and registries

Hermes currently integrates with these skills ecosystems and discovery sources:

#### 1. Official optional skills (`official`)

These are maintained in the Hermes repository itself and install with built-in trust.

- Catalog: [Official Optional Skills Catalog](../../reference/optional-skills-catalog)
- Source in repo: `optional-skills/`
- Example:

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

#### 2. skills.sh (`skills-sh`)

This is Vercel's public skills directory. Hermes can search it directly, inspect skill detail pages, resolve alias-style slugs, and install from the underlying source repo.

- Directory: [skills.sh](https://skills.sh/)
- CLI/tooling repo: [vercel-labs/skills](https://github.com/vercel-labs/skills)
- Official Vercel skills repo: [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- Example:

```bash
hermes skills search react --source skills-sh
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

#### 3. Well-known skill endpoints (`well-known`)

This is URL-based discovery from sites that publish `/.well-known/skills/index.json`. It is not a single centralized hub — it is a web discovery convention.

- Example live endpoint: [Mintlify docs skills index](https://mintlify.com/docs/.well-known/skills/index.json)
- Reference server implementation: [vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- Example:

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. Direct GitHub skills (`github`)

Hermes can install directly from GitHub repositories and GitHub-based taps. This is useful when you already know the repo/path or want to add your own custom source repo.

Default taps (browsable without any setup):
- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [huggingface/skills](https://github.com/huggingface/skills)
- [NVIDIA/skills](https://github.com/NVIDIA/skills) — NVIDIA-verified skills (signed `skill.oms.sig` + governance `skill-card.md`)
- [garrytan/gstack](https://github.com/garrytan/gstack)

- Example:

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

**Category groupings (`skills.sh.json`).** A GitHub tap may ship a
`skills.sh.json` file at its repo root following the
[skills.sh schema](https://skills.sh/schemas/skills.sh.schema.json). Its
`groupings` (each with a `title` and a list of skill names) are read at index
time and become the category labels shown in the
[Skills Hub](https://hermes-agent.nousresearch.com/docs) page — instead of a
tag-derived guess. This is generic: any tap that ships the file gets real
categorization, no Hermes-side changes required.

```json
{
  "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
  "groupings": [
    { "title": "Inference AI", "skills": ["dynamo-recipe-runner", "dynamo-router-sla"] },
    { "title": "Decision Optimization", "skills": ["cuopt-developer", "cuopt-install"] }
  ]
}
```

#### 5. ClawHub (`clawhub`)

A third-party skills marketplace integrated as a community source.

- Site: [clawhub.ai](https://clawhub.ai/)
- Hermes source id: `clawhub`

#### 6. Claude marketplace-style repos (`claude-marketplace`)

Hermes supports marketplace repos that publish Claude-compatible plugin/marketplace manifests.

Known integrated sources include:
- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)

Hermes source id: `claude-marketplace`

#### 7. LobeHub (`lobehub`)

Hermes can search and convert agent entries from LobeHub's public catalog into installable Hermes skills.

- Site: [LobeHub](https://lobehub.com/)
- Public agents index: [chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- Backing repo: [lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes source id: `lobehub`

#### 8. browse.sh (`browse-sh`)

Hermes integrates with [browse.sh](https://browse.sh), Browserbase's catalog of 200+ site-specific browser-automation SKILL.md files (Airbnb, Amazon, arXiv, 12306.cn, Etsy, Xero, and many more). Each skill describes how to drive one website end-to-end and is suitable for use with Hermes' browser tools and any browser-automation skills you already have installed.

- Site: [browse.sh](https://browse.sh/)
- Catalog API: `https://browse.sh/api/skills`
- Hermes source id: `browse-sh`
- Trust level: `community`

```bash
hermes skills search airbnb --source browse-sh
hermes skills inspect browse-sh/airbnb.com/search-listings-ddgioa
hermes skills install browse-sh/airbnb.com/search-listings-ddgioa
```

Identifiers use the form `browse-sh/<hostname>/<task-id>` and match the slug exposed by the browse.sh catalog. Content is resolved through the per-skill detail endpoint (`/api/skills/<slug>` → `skillMdUrl`), not through the catalog's GitHub `sourceUrl`.

#### 9. Direct URL (`url`)

Install a single-file `SKILL.md` directly from any HTTP(S) URL — useful when an author hosts a skill on their own site (no hub listing, no GitHub path to type). Hermes fetches the URL, parses the YAML frontmatter, security-scans it, and installs.

- Hermes source id: `url`
- Identifier: the URL itself (no prefix needed)
- Scope: **single-file `SKILL.md`** only. Multi-file skills with `references/` or `scripts/` need a manifest and should be published via one of the other sources above.

```bash
hermes skills install https://sharethis.chat/SKILL.md
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```

Name resolution, in order:
1. `name:` field in the SKILL.md YAML frontmatter (recommended — every well-formed skill has one).
2. Parent directory name from the URL path (e.g. `.../my-skill/SKILL.md` → `my-skill`, or `.../my-skill.md` → `my-skill`), when it's a valid identifier (`^[a-z][a-z0-9_-]*$`).
3. Interactive prompt on a terminal with a TTY.
4. On non-interactive surfaces (the `/skills install` slash command inside the TUI, gateway platforms, scripts), a clean error pointing at the `--name` override.

```bash
# Frontmatter has no name and the URL slug is unhelpful — supply one:
hermes skills install https://example.com/SKILL.md --name sharethis-chat

# Or inside a chat session:
/skills install https://example.com/SKILL.md --name sharethis-chat
```

Trust level is always `community` — the same security scan runs as for every other source. The URL is stored as the install identifier, so `hermes skills update` re-fetches from the same URL automatically when you want to refresh.

### Security scanning and `--force`

All hub-installed skills go through a **security scanner** that checks for data exfiltration, prompt injection, destructive commands, supply-chain signals, and other threats.

`hermes skills inspect ...` now also surfaces upstream metadata when available:
- repo URL
- skills.sh detail page URL
- install command
- weekly installs
- upstream security audit statuses
- well-known index/endpoint URLs

Use `--force` when you have reviewed a third-party skill and want to override a non-dangerous policy block:

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

Important behavior:
- `--force` can override policy blocks for caution/warn-style findings.
- `--force` does **not** override a `dangerous` scan verdict.
- Official optional skills (`official/...`) are treated as built-in trust and do not show the third-party warning panel.

### Trust levels

| Level | Source | Policy |
|-------|--------|--------|
| `builtin` | Ships with Hermes | Always trusted |
| `official` | `optional-skills/` in the repo | Built-in trust, no third-party warning |
| `trusted` | Trusted registries/repos such as `openai/skills`, `anthropics/skills`, `huggingface/skills`, `NVIDIA/skills` | More permissive policy than community sources |
| `community` | Everything else (`skills.sh`, well-known endpoints, custom GitHub repos, most marketplaces) | Non-dangerous findings can be overridden with `--force`; `dangerous` verdicts stay blocked |

### Update lifecycle

The hub now tracks enough provenance to re-check upstream copies of installed skills:

```bash
hermes skills check          # Report which installed hub skills changed upstream
hermes skills update         # Reinstall only the skills with updates available
hermes skills update react   # Update one specific installed hub skill
```

This uses the stored source identifier plus the current upstream bundle content hash to detect drift.

:::tip GitHub rate limits
Skills hub operations use the GitHub API, which has a rate limit of 60 requests/hour for unauthenticated users. If you see rate-limit errors during install or search, set `GITHUB_TOKEN` in your `.env` file to increase the limit to 5,000 requests/hour. The error message includes an actionable hint when this happens.
:::

### Publishing a custom skill tap

If you want to share a curated set of skills — for your team, your org, or publicly — you can publish them as a **tap**: a GitHub repository other Hermes users add with `hermes skills tap add <owner/repo>`. No server, no registry sign-up, no release pipeline. Just a directory of `SKILL.md` files.

#### Repo layout

A tap is any GitHub repo (public or private — private needs `GITHUB_TOKEN`) laid out like this:

```
owner/repo
├── skills/                       # default path; configurable per-tap
│   ├── my-workflow/
│   │   ├── SKILL.md              # required
│   │   ├── references/           # optional supporting files
│   │   ├── templates/
│   │   └── scripts/
│   ├── another-skill/
│   │   └── SKILL.md
│   └── third-skill/
│       └── SKILL.md
└── README.md                     # optional but helpful
```

Rules:
- Each skill lives in its own directory under the tap's root path (default `skills/`).
- The directory name becomes the skill's install slug.
- Each skill directory must contain a `SKILL.md` with standard [SKILL.md frontmatter](#skillmd-format) (`name`, `description`, plus optional `metadata.hermes.tags`, `version`, `author`, `platforms`, `metadata.hermes.config`).
- Subdirectories like `references/`, `templates/`, `scripts/`, `assets/` are downloaded alongside `SKILL.md` at install time.
- Skills whose directory name starts with `.` or `_` are ignored.

Hermes discovers skills by listing every subdirectory of the tap path and probing each for `SKILL.md`.

#### Minimal tap example

```
my-org/hermes-skills
└── skills/
    └── deploy-runbook/
        └── SKILL.md
```

`skills/deploy-runbook/SKILL.md`:

```markdown
---
name: deploy-runbook
description: Our deployment runbook — services, rollback, Slack channels
version: 1.0.0
author: My Org Platform Team
metadata:
  hermes:
    tags: [deployment, runbook, internal]
---

# Deploy Runbook

Step 1: ...
```

After pushing that to GitHub, any Hermes user can subscribe and install:

```bash
hermes skills tap add my-org/hermes-skills
hermes skills search deploy
hermes skills install my-org/hermes-skills/deploy-runbook
```

#### Non-default paths

If your skills don't live under `skills/` (common when you're adding a `skills/` subtree to an existing project), edit the tap entry in `~/.hermes/.hub/taps.json`:

```json
{
  "taps": [
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}
  ]
}
```

The `hermes skills tap add` CLI defaults new taps to `path: "skills/"`; edit the file directly if you need a different path. `hermes skills tap list` shows the effective path per tap.

#### Installing individual skills directly (without adding a tap)

Users can also install a single skill from any public GitHub repo without adding the whole repo as a tap:

```bash
hermes skills install owner/repo/skills/my-workflow
```

Useful when you want to share one skill without asking the user to subscribe to your whole registry.

#### Trust levels for taps

New taps are assigned `community` trust by default. Skills installed from them run through the standard security scan and show the third-party warning panel on first install. If your org or a widely-trusted source should get higher trust, add its repo to `TRUSTED_REPOS` in `tools/skills_hub.py` (requires a Hermes core PR).

#### Tap management

```bash
hermes skills tap list                                # show all configured taps
hermes skills tap add myorg/skills-repo               # add (default path: skills/)
hermes skills tap remove myorg/skills-repo            # remove
```

Inside a running session:

```
/skills tap list
/skills tap add myorg/skills-repo
/skills tap remove myorg/skills-repo
```

Taps are stored in `~/.hermes/.hub/taps.json` (created on demand).

## Bundled skill updates (`hermes skills reset`)

Hermes ships with a set of bundled skills in `skills/` inside the repo. On install and on every `hermes update`, a sync pass copies those into `~/.hermes/skills/` and records a manifest at `~/.hermes/skills/.bundled_manifest` mapping each skill name to the content hash at the time it was synced (the **origin hash**).

On each sync, Hermes recomputes the hash of your local copy and compares it to the origin hash:

- **Unchanged** → safe to pull upstream changes, copy the new bundled version in, record the new origin hash.
- **Changed** → treated as **user-modified** and skipped forever, so your edits never get stomped.

The protection is good, but it has one sharp edge. If you edit a bundled skill and then later want to abandon your changes and go back to the bundled version by just copy-pasting from `~/.hermes/hermes-agent/skills/`, the manifest still holds the *old* origin hash from whenever the last successful sync ran. Your fresh copy-paste contents (current bundled hash) won't match that stale origin hash, so sync keeps flagging it as user-modified.

`hermes skills reset` is the escape hatch:

```bash
# Safe: clears the manifest entry for this skill. Your current copy is preserved,
# but the next sync re-baselines against it so future updates work normally.
hermes skills reset google-workspace

# Full restore: also deletes your local copy and re-copies the current bundled
# version. Use this when you want the pristine upstream skill back.
hermes skills reset google-workspace --restore

# Non-interactive (e.g. in scripts or TUI mode) — skip the --restore confirmation.
hermes skills reset google-workspace --restore --yes
```

The same command works in chat as a slash command:

```text
/skills reset google-workspace
/skills reset google-workspace --restore
```

:::note Profiles
Each profile has its own `.bundled_manifest` under its own `HERMES_HOME`, so `hermes -p coder skills reset <name>` only affects that profile.
:::

### Slash commands (inside chat)

All the same commands work with `/skills`:

```text
/skills browse
/skills search react --source skills-sh
/skills search https://mintlify.com/docs --source well-known
/skills inspect skills-sh/vercel-labs/json-render/json-render-react
/skills install openai/skills/skill-creator --force
/skills check
/skills update
/skills reset google-workspace
/skills list
```

Official optional skills still use identifiers like `official/security/1password` and `official/migration/openclaw-migration`.

---

# SOURCE: website/docs/user-guide/features/curator.md

---
sidebar_position: 3
title: "Curator"
description: "Background maintenance for agent-created skills — usage tracking, staleness, archival, and LLM-driven review"
---

# Curator

The curator is a background maintenance pass for **agent-created skills**. It tracks how often each skill is viewed, used, and patched, moves long-unused skills through `active → stale → archived` states, and periodically spawns a short auxiliary-model review that proposes consolidations or patches drift.

It exists so that skills created via the [self-improvement loop](/user-guide/features/skills#agent-managed-skills-skill_manage-tool) don't pile up forever. Every time the agent solves a novel problem and saves a skill, that skill lands in `~/.hermes/skills/`. Without maintenance, you end up with dozens of narrow near-duplicates that pollute the catalog and waste tokens.

By default (`prune_builtins: true`) the curator can archive **unused bundled built-in skills** (shipped with the repo) after `archive_after_days` of non-use, alongside the agent-created skills it primarily manages. Hub-installed skills (from [agentskills.io](https://agentskills.io)) are always off-limits. Set `curator.prune_builtins: false` to restore the old agent-created-only behavior, where bundled skills are never touched. The curator also **never auto-deletes** — the worst outcome is archival into `~/.hermes/skills/.archive/`, which is recoverable.

Tracks [issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816).

## How it runs

The curator is triggered by an inactivity check, not a cron daemon. On CLI session start, and on a recurring tick inside the gateway's cron-ticker thread, Hermes checks whether:

1. Enough time has passed since the last curator run (`interval_hours`, default **7 days**), and
2. The agent has been idle long enough (`min_idle_hours`, default **2 hours**).

If both are true, it spawns a background fork of `AIAgent` — the same pattern used by the memory/skill self-improvement nudges. The fork runs in its own prompt cache and never touches the active conversation.

:::info First-run behavior
On a brand-new install (or the first time a pre-curator install ticks after `hermes update`), the curator **does not run immediately**. The first observation seeds `last_run_at` to "now" and defers the first real pass by one full `interval_hours`. This gives you a full interval to review your skill library, pin anything important, or opt out entirely before the curator ever touches it.

If you want to see what the curator *would* do before it runs for real, run `hermes curator run --dry-run` — it produces the same review report without mutating the library.
:::

A run has two phases:

1. **Automatic transitions** (deterministic, no LLM). Skills unused for `stale_after_days` (30) become `stale`; skills unused for `archive_after_days` (90) are moved to `~/.hermes/skills/.archive/`. This is the always-on pruning behavior — it runs whenever the curator is enabled, with no aux-model cost.
2. **LLM consolidation** (single aux-model pass, `max_iterations=8`) — **OFF by default**. When `curator.consolidate: true`, the forked agent surveys the agent-created skills, can read any of them with `skill_view`, and decides per-skill whether to keep, patch (via `skill_manage`), consolidate overlapping ones into class-level umbrellas, or archive via the terminal tool. Consolidation treats a skill as a full package: if a skill has `references/`, `templates/`, `scripts/`, `assets/`, or relative links to those paths, the curator must either keep it standalone, re-home the needed support files and rewrite paths, or archive the entire package unchanged — not flatten only `SKILL.md` into another skill's `references/` file.

:::info Consolidation is opt-in
By default the curator only **prunes** — the deterministic inactivity pass marks skills stale and archives long-unused ones. The opinionated LLM **consolidation** pass (umbrella-building, merging overlapping skills) is off by default because it costs aux-model tokens on every run and makes broad structural changes to your library. Turn it on with `curator.consolidate: true`, or run it once on demand with `hermes curator run --consolidate`.
:::

Pinned skills are off-limits to both the curator's auto-transitions and the agent's own `skill_manage` tool. See [Pinning a skill](#pinning-a-skill) below.

## Configuration

All settings live in `config.yaml` under `curator:` (not `.env` — this isn't a secret). Defaults:

```yaml
curator:
  enabled: true
  interval_hours: 168          # 7 days
  min_idle_hours: 2
  stale_after_days: 30
  archive_after_days: 90
  consolidate: false           # LLM umbrella-building pass — opt-in (prune-only by default)
  prune_builtins: true         # archive unused bundled built-in skills too (hub skills always exempt)
```

To disable entirely, set `curator.enabled: false`. To keep the always-on pruning but opt into LLM consolidation, set `curator.consolidate: true`.

### Running the review on a cheaper aux model

The curator's LLM review pass is a regular auxiliary task slot — `auxiliary.curator` — alongside Vision, Compression, Session Search, etc. "Auto" means "use my main chat model"; override the slot to pin a specific provider + model for the review pass instead.

**Easiest — `hermes model`:**

```bash
hermes model                   # → "Auxiliary models — side-task routing"
                               # → pick "Curator" → pick provider → pick model
```

The same picker is available in the web dashboard under the **Models** tab.

**Direct config.yaml (equivalent):**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # generous — reviews can take several minutes
```

Leaving `provider: auto` (the default) routes the review pass through whatever your main chat model is, matching the behavior of every other auxiliary task.

:::note Legacy config
Earlier releases used a one-off `curator.auxiliary.{provider,model}` block. That path still works but emits a deprecation log line — please migrate to `auxiliary.curator` above so the curator shares the same plumbing (`hermes model`, dashboard Models tab, `base_url`, `api_key`, `timeout`, `extra_body`) as every other aux task.
:::

## CLI

```bash
hermes curator status         # last run, counts, pinned list, LRU top 5
hermes curator run            # trigger a run now (blocks until done). Prune-only unless curator.consolidate: true
hermes curator run --consolidate # force the LLM consolidation pass on for this run, overriding the config default
hermes curator run --background  # fire-and-forget: start the run in a background thread
hermes curator run --dry-run  # preview only — report without any mutations
hermes curator backup         # take a manual snapshot of ~/.hermes/skills/
hermes curator rollback       # restore from the newest snapshot
hermes curator rollback --list     # list available snapshots
hermes curator rollback --id <ts>  # restore a specific snapshot
hermes curator rollback -y         # skip the confirmation prompt
hermes curator pause          # stop runs until resumed
hermes curator resume
hermes curator pin <skill>    # never auto-transition this skill
hermes curator unpin <skill>
hermes curator restore <skill>  # move an archived skill back to active
hermes curator list-archived    # list skills currently in ~/.hermes/skills/.archive/
hermes curator archive <skill>  # manually archive a single skill now
hermes curator prune [--days N] # bulk-archive agent-created skills idle >= N days (default 90)
```

## Backups and rollback

Before every real curator pass, Hermes takes a tar.gz snapshot of `~/.hermes/skills/` at `~/.hermes/skills/.curator_backups/<utc-iso>/skills.tar.gz`. If a pass archives or consolidates something you didn't want touched, you can undo the whole run with one command:

```bash
hermes curator rollback        # restore newest snapshot (with confirmation)
hermes curator rollback -y     # skip the prompt
hermes curator rollback --list # see all snapshots with reason + size
```

The rollback itself is reversible: before replacing the skills tree, Hermes takes another snapshot tagged `pre-rollback to <target-id>`, so a mistaken rollback can be undone by rolling forward to that one with `--id`.

You can also take manual snapshots at any time with `hermes curator backup --reason "before-refactor"`. The `--reason` string lands in the snapshot's `manifest.json` and is shown in `--list`.

Snapshots are pruned to `curator.backup.keep` (default 5) to keep disk usage bounded:

```yaml
curator:
  backup:
    enabled: true
    keep: 5
```

Set `curator.backup.enabled: false` to disable automatic snapshotting. The manual `hermes curator backup` command still works when backups are disabled only if you set `enabled: true` first — the flag gates both paths symmetrically so there's no way to accidentally skip the pre-run snapshot on mutating runs.

`hermes curator status` also lists the five least-recently-used skills — a quick way to see what's likely to become stale next.

The same subcommands are available as the `/curator` slash command inside a running session (CLI or gateway platforms).

## What "agent-created" means

The curator only manages skills explicitly marked as **agent-created** in
`~/.hermes/skills/.usage.json`. A skill qualifies when ALL of the following
are true:

1. Its name is **not** in `~/.hermes/skills/.bundled_manifest` (bundled skills shipped with the repo).
2. Its name is **not** in `~/.hermes/skills/.hub/lock.json` (hub-installed skills).
3. Its `.usage.json` entry has `"created_by": "agent"` or `"agent_created": true`.

Currently, only the **background self-improvement review fork** sets this marker
— when it creates a new umbrella skill during its periodic review pass (~every 10
agent turns). The background fork runs with a write origin of `"background_review"`
(via `tools/skill_provenance.py`), which is the only path that triggers the
`mark_agent_created()` call in `skill_manage`.

Skills the foreground agent creates via `skill_manage(action="create")` during a
conversation are **not** marked as agent-created — they are considered
user-directed and the curator intentionally leaves them alone.

:::warning Your hand-written skills are NOT curated
If you manually created a `SKILL.md` or pointed Hermes at an external skill
directory, that skill will have a `.usage.json` entry with `created_by: null`
(or the field absent). The curator will not touch it. The same applies to
skills the foreground agent created at your request.

**To see which skills the curator actually manages**, run `hermes curator status`.
If the agent-created count is 0, no skills are currently in the curator's
jurisdiction — the LLM review pass is skipped and the report will show
`Model: (not resolved) via (not resolved)` with `Duration: 0s`.
:::

Skills that ARE agent-created follow the full lifecycle:

- `active` → (30d unused) `stale` → (90d unused) `archived`
- Pinned skills bypass all auto-transitions
- Archives are recoverable via `hermes curator restore <name>`

If you want to protect a specific skill from ever being touched — for example a
hand-authored skill you rely on — use `hermes curator pin <name>`. See the next
section.

## Pinning a skill

Pinning protects a skill from deletion — both the curator's automated archive passes and the agent's `skill_manage(action="delete")` tool call. Once a skill is pinned:

- The **curator** skips it during auto-transitions (`active → stale → archived`), and its LLM review pass is instructed to leave it alone.
- The **agent's `skill_manage` tool** refuses `delete` on it, pointing the user at `hermes curator unpin <name>`. Patches and edits still go through, so the agent can improve a pinned skill's content as pitfalls come up without a pin/unpin/re-pin dance.

Pin and unpin with:

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

The flag is stored as `"pinned": true` on the skill's entry in `~/.hermes/skills/.usage.json`, so it survives across sessions.

Only **agent-created** skills can be pinned — `hermes curator pin` refuses on bundled and hub-installed skills with an explanatory message if you try. Hub-installed skills are never subject to curator mutation. Bundled built-in skills are only touched when `curator.prune_builtins: true` (the default), and even then only archived after `archive_after_days` of non-use — never patched, consolidated, or deleted. Set `curator.prune_builtins: false` to exempt bundled skills entirely.

A small set of **protected built-ins** is hardcoded as never-archivable and never-consolidatable, regardless of `curator.prune_builtins`, pin state, or LLM judgment. These back load-bearing UX — for example, `plan` powers the `/plan` slash-command flow — so silently archiving one would turn its slash command into an "Unknown command" error with no signal to you. Protected built-ins are filtered out of the curator's candidate list entirely, so the consolidation pass never sees them.

If you want a stronger guarantee than "no deletion" — for instance, freezing a skill's content entirely while the agent still reads it — edit `~/.hermes/skills/<name>/SKILL.md` directly with your editor. The pin guards tool-driven deletion, not your own filesystem access.

## Usage telemetry

The curator maintains a sidecar at `~/.hermes/skills/.usage.json` with one entry per skill:

```json
{
  "my-skill": {
    "use_count": 12,
    "view_count": 34,
    "last_used_at": "2026-04-24T18:12:03Z",
    "last_viewed_at": "2026-04-23T09:44:17Z",
    "patch_count": 3,
    "last_patched_at": "2026-04-20T22:01:55Z",
    "created_at": "2026-03-01T14:20:00Z",
    "state": "active",
    "pinned": false,
    "archived_at": null
  }
}
```

Counters increment when:

- `view_count`: the agent calls `skill_view` on the skill.
- `use_count`: the skill is loaded into a conversation's prompt.
- `patch_count`: `skill_manage patch/edit/write_file/remove_file` runs on the skill.

Bundled and hub-installed skills are explicitly excluded from telemetry writes.

## Per-run reports

Every curator run writes a timestamped directory under `~/.hermes/logs/curator/`:

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # machine-readable: full fidelity, stats, LLM output
    └── REPORT.md     # human-readable summary
```

`REPORT.md` is a quick way to see what a given run did — which skills transitioned, what the LLM reviewer said, which skills it patched. Good for auditing without having to grep `agent.log`.

:::note No candidates? Report shows `(not resolved)`
When the curator has **no agent-created skills** to review, the LLM review pass
is skipped entirely. The report header will show
`Model: (not resolved) via (not resolved)` with `Duration: 0s` — this does **not**
indicate a configuration error or model resolution failure. It simply means there
were no candidates, so no model was ever invoked. The auto-transition phase still
runs and reports its counts normally.
:::

### Rename map in the summary

If a run consolidated multiple skills under an umbrella (or merged near-duplicates), the user-visible summary printed at the end of the run includes an explicit rename map showing every `old-name → new-name` pair the curator applied. This is in addition to per-skill transition lines, so when a wave of renames lands you can spot them at a glance without diffing the JSON report. The hint also surfaces under `hermes curator pin` so you can pin the umbrella name immediately if you want to lock the new label in.

## Restoring an archived skill

If the curator archived something you still want:

```bash
hermes curator restore <skill-name>
```

This moves the skill back from `~/.hermes/skills/.archive/` to the active tree and resets its state to `active`. The restore refuses if a bundled or hub-installed skill has since been installed under the same name (would shadow upstream).

## Disabling per environment

The curator is on by default. To turn it off:

- **For one profile only:** edit `~/.hermes/config.yaml` (or the active profile's config) and set `curator.enabled: false`.
- **For just one run:** `hermes curator pause` — the pause persists across sessions; use `resume` to re-enable.

The curator also refuses to run if `min_idle_hours` hasn't elapsed, so on an active dev machine it naturally only runs during quiet stretches.

## See also

- [Skills System](/user-guide/features/skills) — how skills work in general and the self-improvement loop that creates them
- [Memory](/user-guide/features/memory) — a parallel background review that maintains long-term memory
- [Bundled Skills Catalog](/reference/skills-catalog)
- [Issue #7816](https://github.com/NousResearch/hermes-agent/issues/7816) — original proposal and design discussion

---

# SOURCE: website/docs/guides/work-with-skills.md

---
sidebar_position: 12
title: "Working with Skills"
description: "Find, install, use, and create skills — on-demand knowledge that teaches Hermes new workflows"
---

# Working with Skills

Skills are on-demand knowledge documents that teach Hermes how to handle specific tasks — from generating ASCII art to managing GitHub PRs. This guide walks you through using them day to day.

For the full technical reference, see [Skills System](/user-guide/features/skills).

---

## Finding Skills

Every Hermes installation ships with bundled skills. See what's available:

```bash
# In any chat session:
/skills

# Or from the CLI:
hermes skills list
```

This shows a compact list with names and descriptions:

```
ascii-art         Generate ASCII art using pyfiglet, cowsay, boxes...
arxiv             Search and retrieve academic papers from arXiv...
github-pr-workflow Full PR lifecycle — create branches, commit...
plan              Plan mode — inspect context, write a markdown...
excalidraw        Create hand-drawn style diagrams using Excalidraw...
```

### Searching for a Skill

```bash
# Search by keyword
/skills search docker
/skills search music
```

### The Skills Hub

Official optional skills (heavier or niche skills not active by default) are available via the Hub:

```bash
# Browse official optional skills
/skills browse

# Search the hub
/skills search blockchain
```

---

## Using a Skill

Every installed skill is automatically a slash command. Just type its name:

```bash
# Load a skill and give it a task
/ascii-art Make a banner that says "HELLO WORLD"
/plan Design a REST API for a todo app
/github-pr-workflow Create a PR for the auth refactor

# Just the skill name (no task) loads it and lets you describe what you need
/excalidraw
```

You can also trigger skills through natural conversation — ask Hermes to use a specific skill, and it will load it via the `skill_view` tool.

### Progressive Disclosure

Skills use a token-efficient loading pattern. The agent doesn't load everything at once:

1. **`skills_list()`** — compact list of all skills (~3k tokens). Loaded at session start.
2. **`skill_view(name)`** — full SKILL.md content for one skill. Loaded when the agent decides it needs that skill.
3. **`skill_view(name, file_path)`** — a specific reference file within the skill. Only loaded if needed.

This means skills don't cost tokens until they're actually used.

---

## Installing from the Hub

Official optional skills ship with Hermes but aren't active by default. Install them explicitly:

```bash
# Install an official optional skill
hermes skills install official/research/arxiv

# Install from the hub in a chat session
/skills install official/creative/songwriting-and-ai-music

# Install a single-file SKILL.md directly from any HTTP(S) URL
hermes skills install https://sharethis.chat/SKILL.md
/skills install https://example.com/SKILL.md --name my-skill
```

What happens:
1. The skill directory is copied to `~/.hermes/skills/`
2. It appears in your `skills_list` output
3. It becomes available as a slash command

:::tip
Installed skills take effect in new sessions. If you want it available in the current session, use `/reset` to start fresh, or add `--now` to invalidate the prompt cache immediately (costs more tokens on the next turn).
:::

### Verifying Installation

```bash
# Check it's there
hermes skills list | grep arxiv

# Or in chat
/skills search arxiv
```

---

## Plugin-Provided Skills

Plugins can bundle their own skills using namespaced names (`plugin:skill`). This prevents name collisions with built-in skills.

```bash
# Load a plugin skill by its qualified name
skill_view("superpowers:writing-plans")

# Built-in skill with the same base name is unaffected
skill_view("writing-plans")
```

Plugin skills are **not** listed in the system prompt and don't appear in `skills_list`. They're opt-in — load them explicitly when you know a plugin provides one. When loaded, the agent sees a banner listing sibling skills from the same plugin.

For how to ship skills in your own plugin, see [Build a Hermes Plugin → Bundle skills](/guides/build-a-hermes-plugin#bundle-skills).

---

## Configuring Skill Settings

Some skills declare configuration they need in their frontmatter:

```yaml
metadata:
  hermes:
    config:
      - key: tenor.api_key
        description: "Tenor API key for GIF search"
        prompt: "Enter your Tenor API key"
        url: "https://developers.google.com/tenor/guides/quickstart"
```

When a skill with config is first loaded, Hermes prompts you for the values. They're stored in `config.yaml` under `skills.config.*`.

Manage skill config from the CLI:

```bash
# Interactive config for a specific skill
hermes skills config gif-search

# View all skill config
hermes config show | grep '^skills\.config'
```

---

## Creating Your Own Skill

Skills are just markdown files with YAML frontmatter. Creating one takes under five minutes.

### 1. Create the Directory

```bash
mkdir -p ~/.hermes/skills/my-category/my-skill
```

### 2. Write SKILL.md

```markdown title="~/.hermes/skills/my-category/my-skill/SKILL.md"
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
metadata:
  hermes:
    tags: [my-tag, automation]
    category: my-category
---

# My Skill

## When to Use
Use this skill when the user asks about [specific topic] or needs to [specific task].

## Procedure
1. First, check if [prerequisite] is available
2. Run `command --with-flags`
3. Parse the output and present results

## Pitfalls
- Common failure: [description]. Fix: [solution]
- Watch out for [edge case]

## Verification
Run `check-command` to confirm the result is correct.
```

### 3. Add Reference Files (Optional)

Skills can include supporting files the agent loads on demand:

```
my-skill/
├── SKILL.md                    # Main skill document
├── references/
│   ├── api-docs.md             # API reference the agent can consult
│   └── examples.md             # Example inputs/outputs
├── templates/
│   └── config.yaml             # Template files the agent can use
└── scripts/
    └── setup.sh                # Scripts the agent can execute
```

Reference these in your SKILL.md:

```markdown
For API details, load the reference: `skill_view("my-skill", "references/api-docs.md")`
```

### 4. Test It

Start a new session and try your skill:

```bash
hermes chat -q "/my-skill help me with the thing"
```

The skill appears automatically — no registration needed. Drop it in `~/.hermes/skills/` and it's live.

:::info
The agent can also create and update skills itself using `skill_manage`. After solving a complex problem, Hermes may offer to save the approach as a skill for next time.
:::

---

## Per-Platform Skill Management

Control which skills are available on which platforms:

```bash
hermes skills
```

This opens an interactive TUI where you can enable or disable skills per platform (CLI, Telegram, Discord, etc.). Useful when you want certain skills only available in specific contexts — for example, keeping development skills off Telegram.

---

## Skills vs Memory

Both are persistent across sessions, but they serve different purposes:

| | Skills | Memory |
|---|---|---|
| **What** | Procedural knowledge — how to do things | Factual knowledge — what things are |
| **When** | Loaded on demand, only when relevant | Injected into every session automatically |
| **Size** | Can be large (hundreds of lines) | Should be compact (key facts only) |
| **Cost** | Zero tokens until loaded | Small but constant token cost |
| **Examples** | "How to deploy to Kubernetes" | "User prefers dark mode, lives in PST" |
| **Who creates** | You, the agent, or installed from Hub | The agent, based on conversations |

**Rule of thumb:** If you'd put it in a reference document, it's a skill. If you'd put it on a sticky note, it's memory.

---

## Tips

**Keep skills focused.** A skill that tries to cover "all of DevOps" will be too long and too vague. A skill that covers "deploy a Python app to Fly.io" is specific enough to be genuinely useful.

**Let the agent create skills.** After a complex multi-step task, Hermes will often offer to save the approach as a skill. Say yes — these agent-authored skills capture the exact workflow including pitfalls that were discovered along the way.

**Use categories.** Organize skills into subdirectories (`~/.hermes/skills/devops/`, `~/.hermes/skills/research/`, etc.). This keeps the list manageable and helps the agent find relevant skills faster.

**Update skills when they go stale.** If you use a skill and hit issues not covered by it, tell Hermes to update the skill with what you learned. Skills that aren't maintained become liabilities.

---

*For the complete skills reference — frontmatter fields, conditional activation, external directories, and more — see [Skills System](/user-guide/features/skills).*

---

# SOURCE: website/docs/developer-guide/creating-skills.md

---
sidebar_position: 3
title: "Creating Skills"
description: "How to create skills for Hermes Agent — SKILL.md format, guidelines, and publishing"
---

# Creating Skills

Skills are the preferred way to add new capabilities to Hermes Agent. They're easier to create than tools, require no code changes to the agent, and can be shared with the community.

## Should it be a Skill or a Tool?

Make it a **Skill** when:
- The capability can be expressed as instructions + shell commands + existing tools
- It wraps an external CLI or API that the agent can call via `terminal` or `web_extract`
- It doesn't need custom Python integration or API key management baked into the agent
- Examples: arXiv search, git workflows, Docker management, PDF processing, email via CLI tools

Make it a **Tool** when:
- It requires end-to-end integration with API keys, auth flows, or multi-component configuration
- It needs custom processing logic that must execute precisely every time
- It handles binary data, streaming, or real-time events
- Examples: browser automation, TTS, vision analysis

## Skill Directory Structure

Bundled skills live in `skills/` organized by category. Official optional skills use the same structure in `optional-skills/`:

```text
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # Required: main instructions
│       └── scripts/              # Optional: helper scripts
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

## SKILL.md Format

```markdown
---
name: my-skill
description: Brief description (shown in skill search results)
version: 1.0.0
author: Your Name
license: MIT
platforms: [macos, linux]          # Optional — restrict to specific OS platforms
                                   #   Valid: macos, linux, windows
                                   #   Omit to load on all platforms (default)
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    requires_toolsets: [web]            # Optional — only show when these toolsets are active
    requires_tools: [web_search]        # Optional — only show when these tools are available
    fallback_for_toolsets: [browser]    # Optional — hide when these toolsets are active
    fallback_for_tools: [browser_navigate]  # Optional — hide when these tools exist
    config:                              # Optional — config.yaml settings the skill needs
      - key: my.setting
        description: "What this setting controls"
        default: "sensible-default"
        prompt: "Display prompt for setup"
    blueprint:                              # Optional — marks this skill a runnable automation
      schedule: "0 9 * * *"              #   cron expr / "every 2h" / ISO timestamp
      deliver: origin                    #   optional (default origin)
      prompt: "Task instruction for each run"  # optional
      no_agent: false                    # optional
required_environment_variables:          # Optional — env vars the skill needs
  - name: MY_API_KEY
    prompt: "Enter your API key"
    help: "Get one at https://example.com"
    required_for: "API access"
---

# Skill Title

Brief intro.

## When to Use
Trigger conditions — when should the agent load this skill?

## Quick Reference
Table of common commands or API calls.

## Procedure
Step-by-step instructions the agent follows.

## Pitfalls
Known failure modes and how to handle them.

## Verification
How the agent confirms it worked.
```

### Platform-Specific Skills

Skills can restrict themselves to specific operating systems using the `platforms` field:

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders)
platforms: [macos, linux]     # macOS and Linux
platforms: [windows]          # Windows only
```

When set, the skill is automatically hidden from the system prompt, `skills_list()`, and slash commands on incompatible platforms. If omitted or empty, the skill loads on all platforms (backward compatible).

### Conditional Skill Activation

Skills can declare dependencies on specific tools or toolsets. This controls whether the skill appears in the system prompt for a given session.

```yaml
metadata:
  hermes:
    requires_toolsets: [web]           # Hide if the web toolset is NOT active
    requires_tools: [web_search]       # Hide if web_search tool is NOT available
    fallback_for_toolsets: [browser]   # Hide if the browser toolset IS active
    fallback_for_tools: [browser_navigate]  # Hide if browser_navigate IS available
```

| Field | Behavior |
|-------|----------|
| `requires_toolsets` | Skill is **hidden** when ANY listed toolset is **not** available |
| `requires_tools` | Skill is **hidden** when ANY listed tool is **not** available |
| `fallback_for_toolsets` | Skill is **hidden** when ANY listed toolset **is** available |
| `fallback_for_tools` | Skill is **hidden** when ANY listed tool **is** available |

**Use case for `fallback_for_*`:** Create a skill that serves as a workaround when a primary tool isn't available. For example, a `duckduckgo-search` skill with `fallback_for_tools: [web_search]` only shows when the web search tool (which requires an API key) is not configured.

**Use case for `requires_*`:** Create a skill that only makes sense when certain tools are present. For example, a web scraping workflow skill with `requires_toolsets: [web]` won't clutter the prompt when web tools are disabled.

### Environment Variable Requirements

Skills can declare environment variables they need. When a skill is loaded via `skill_view`, its required vars are automatically registered for passthrough into sandboxed execution environments (terminal, execute_code).

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: "Tenor API key"               # Shown when prompting user
    help: "Get your key at https://tenor.com"  # Help text or URL
    required_for: "GIF search functionality"   # What needs this var
```

Each entry supports:
- `name` (required) — the environment variable name
- `prompt` (optional) — prompt text when asking the user for the value
- `help` (optional) — help text or URL for obtaining the value
- `required_for` (optional) — describes which feature needs this variable

Users can also manually configure passthrough variables in `config.yaml`:

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_VAR
    - ANOTHER_VAR
```

See `skills/apple/` for examples of macOS-only skills.

## Secure Setup on Load

Use `required_environment_variables` when a skill needs an API key or token. Missing values do **not** hide the skill from discovery. Instead, Hermes prompts for them securely when the skill is loaded in the local CLI.

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

The user can skip setup and keep loading the skill. Hermes never exposes the raw secret value to the model. Gateway and messaging sessions show local setup guidance instead of collecting secrets in-band.

:::tip Sandbox Passthrough
When your skill is loaded, any declared `required_environment_variables` that are set are **automatically passed through** to `execute_code` and `terminal` sandboxes — including remote backends like Docker and Modal. Your skill's scripts can access `$TENOR_API_KEY` (or `os.environ["TENOR_API_KEY"]` in Python) without the user needing to configure anything extra. See [Environment Variable Passthrough](/user-guide/security#environment-variable-passthrough) for details.
:::

Legacy `prerequisites.env_vars` remains supported as a backward-compatible alias.

### Config Settings (config.yaml)

Skills can declare non-secret settings that are stored in `config.yaml` under the `skills.config` namespace. Unlike environment variables (which are secrets stored in `.env`), config settings are for paths, preferences, and other non-sensitive values.

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
      - key: myplugin.domain
        description: Domain the plugin operates on
        default: ""
        prompt: Plugin domain (e.g., AI/ML research)
```

Each entry supports:
- `key` (required) — dotpath for the setting (e.g., `myplugin.path`)
- `description` (required) — explains what the setting controls
- `default` (optional) — default value if the user doesn't configure it
- `prompt` (optional) — prompt text shown during `hermes config migrate`; falls back to `description`

**How it works:**

1. **Storage:** Values are written to `config.yaml` under `skills.config.<key>`:
   ```yaml
   skills:
     config:
       myplugin:
         path: ~/my-data
   ```

2. **Discovery:** `hermes config migrate` scans all enabled skills, finds unconfigured settings, and prompts the user. Settings also appear in `hermes config show` under "Skill Settings."

3. **Runtime injection:** When a skill loads, its config values are resolved and appended to the skill message:
   ```
   [Skill config (from ~/.hermes/config.yaml):
     myplugin.path = /home/user/my-data
   ]
   ```
   The agent sees the configured values without needing to read `config.yaml` itself.

4. **Manual setup:** Users can also set values directly:
   ```bash
   hermes config set skills.config.myplugin.path ~/my-data
   ```

:::tip When to use which
Use `required_environment_variables` for API keys, tokens, and other **secrets** (stored in `~/.hermes/.env`, never shown to the model). Use `config` for **paths, preferences, and non-sensitive settings** (stored in `config.yaml`, visible in config show).
:::

### Credential File Requirements (OAuth tokens, etc.)

Skills that use OAuth or file-based credentials can declare files that need to be mounted into remote sandboxes. This is for credentials stored as **files** (not env vars) — typically OAuth token files produced by a setup script.

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials
```

Each entry supports:
- `path` (required) — file path relative to `~/.hermes/`
- `description` (optional) — explains what the file is and how it's created

When loaded, Hermes checks if these files exist. Missing files trigger `setup_needed`. Existing files are automatically:
- **Mounted into Docker** containers as read-only bind mounts
- **Synced into Modal** sandboxes (at creation + before each command, so mid-session OAuth works)
- Available on **local** backend without any special handling

:::tip When to use which
Use `required_environment_variables` for simple API keys and tokens (strings stored in `~/.hermes/.env`). Use `required_credential_files` for OAuth token files, client secrets, service account JSON, certificates, or any credential that's a file on disk.
:::

See the `skills/productivity/google-workspace/SKILL.md` for a complete example using both.

## Skill Guidelines

### No External Dependencies

Prefer stdlib Python, curl, and existing Hermes tools (`web_extract`, `terminal`, `read_file`). If a dependency is needed, document installation steps in the skill.

### Progressive Disclosure

Put the most common workflow first. Edge cases and advanced usage go at the bottom. This keeps token usage low for common tasks.

### Include Helper Scripts

For XML/JSON parsing or complex logic, include helper scripts in `scripts/` — don't expect the LLM to write parsers inline every time.

### Deliver media as documents (`[[as_document]]`)

If your skill produces a high-resolution screenshot, chart, or any image where lossy preview compression would hurt — emit the literal directive `[[as_document]]` somewhere in the response (commonly the last line). The gateway strips the directive and delivers every extracted media path in that response as a downloadable file attachment instead of an inline image bubble. See [Skill output and media delivery](../user-guide/features/skills.md#skill-output-and-media-delivery) for the full semantics.

#### Referencing bundled scripts from SKILL.md

When a skill is loaded, the activation message exposes the absolute skill directory as `[Skill directory: /abs/path]` and also substitutes two template tokens anywhere in the SKILL.md body:

| Token | Replaced with |
|---|---|
| `${HERMES_SKILL_DIR}` | Absolute path to the skill's directory |
| `${HERMES_SESSION_ID}` | The active session id (left in place if there is no session) |

So a SKILL.md can tell the agent to run a bundled script directly with:

```markdown
To analyse the input, run:

    node ${HERMES_SKILL_DIR}/scripts/analyse.js <input>
```

The agent sees the substituted absolute path and invokes the `terminal` tool with a ready-to-run command — no path math, no extra `skill_view` round-trip. Disable substitution globally with `skills.template_vars: false` in `config.yaml`.

#### Inline shell snippets (opt-in)

Skills can also embed inline shell snippets written as `` !`cmd` `` in the SKILL.md body. When enabled, each snippet's stdout is inlined into the message before the agent reads it, so skills can inject dynamic context:

```markdown
Current date: !`date -u +%Y-%m-%d`
Git branch: !`git -C ${HERMES_SKILL_DIR} rev-parse --abbrev-ref HEAD`
```

This is **off by default** — any snippet in a SKILL.md runs on the host without approval, so only enable it for skill sources you trust:

```yaml
# config.yaml
skills:
  inline_shell: true
  inline_shell_timeout: 10   # seconds per snippet
```

Snippets run with the skill directory as their working directory, and output is capped at 4000 characters. Failures (timeouts, non-zero exits) show up as a short `[inline-shell error: ...]` marker instead of breaking the whole skill.

### Test It

Run the skill and verify the agent follows the instructions correctly:

```bash
hermes chat --toolsets skills -q "Use the X skill to do Y"
```

## Where Should the Skill Live?

Bundled skills (in `skills/`) ship with every Hermes install. They should be **broadly useful to most users**:

- Document handling, web research, common dev workflows, system administration
- Used regularly by a wide range of people

If your skill is official and useful but not universally needed (e.g., a paid service integration, a heavyweight dependency), put it in **`optional-skills/`** — it ships with the repo, is discoverable via `hermes skills browse` (labeled "official"), and installs with built-in trust.

If your skill is specialized, community-contributed, or niche, it's better suited for a **Skills Hub** — upload it to a registry and share it via `hermes skills install`.

## Blueprints: skills that are also automations

A **blueprint** is an ordinary skill that additionally declares a schedule in its frontmatter. Add a `metadata.hermes.blueprint` block and the skill becomes a shareable, runnable automation:

```yaml
metadata:
  hermes:
    tags: [blueprint, email]
    blueprint:
      schedule: "0 8 * * *"     # presence of `blueprint:` marks it runnable
      deliver: telegram          # optional (default: origin)
      prompt: "Summarize my unread email and today's calendar."  # optional
      no_agent: false            # optional
```

Because a blueprint **is** a skill, it flows through the entire skills pipeline unchanged — search, inspect, install, security scan, provenance, taps, the centralized index, and `hermes skills publish` for sharing. Nothing new to learn.

**Installing a blueprint.** When you install a skill that carries a `blueprint:` block, Hermes registers it as a **suggested cron job** rather than scheduling it. Scheduling is **opt-in** — installing never silently creates a recurring job. You review and accept it via `/suggestions`:

```bash
hermes skills install owner/morning-brief
# → Blueprint: 'morning-brief' is an automation (schedule 0 8 * * *).
#   Added to your suggestions — run /suggestions to schedule or dismiss it.

# then, in a session:
/suggestions             # lists pending suggestions, numbered
/suggestions accept 1    # creates the cron job
/suggestions dismiss 1   # never offer it again
```

Blueprints are one **source** of the unified Suggested Cron Jobs surface — the same place curated starter automations and (later) usage-pattern and integration suggestions appear. See [Suggested Cron Jobs](#suggested-cron-jobs) below.

**Sharing an automation you built.** A blueprint loaded by a cron job (`hermes cron create --skill <name> ...`) can be exported back to a SKILL.md and published like any other skill, so an automation you tuned for yourself becomes a one-command install for someone else.

The blueprint layer adds no new object type, store, or transport — the blueprint is a skill, the schedule is a cron job, and sharing is the existing publish/tap/index path.

## Suggested Cron Jobs

Hermes can *propose* automations and let you accept them with one tap, instead of making you assemble cron jobs by hand. Every proposal flows through one surface — the `/suggestions` command — regardless of where it came from:

| Source | Trigger |
|--------|---------|
| `catalog` | Curated starter automations (`/suggestions catalog`) — daily briefing, important-mail monitor, weekly review, workday-start reminder |
| `blueprint` | You installed a skill carrying a `blueprint:` block |
| `usage` | The background review noticed a recurring ask a schedule would serve |
| `integration` | You connected an account (Gmail, GitHub, ...) and the obvious automations are offered |

```bash
/suggestions             # list pending
/suggestions accept N    # schedule suggestion N (creates the cron job)
/suggestions dismiss N   # dismiss it — latched, never re-offered
/suggestions catalog     # add the curated starter automations
```

Accepting a suggestion calls the same `cron.jobs.create_job` the `cronjob` tool uses — there is no second job engine. Suggestions **never** auto-create jobs; acceptance is always explicit. Dismissed suggestions latch by a stable key so the same proposal is never re-offered. The pending list is capped so it never becomes a nag wall.

The **important-mail monitor** catalog entry is the poll→classify→surface pattern: it scores inbox items with a cheap classifier model (`auxiliary.monitor` in `config.yaml`) and delivers only the ones above an urgency threshold, staying silent otherwise.

## Publishing Skills

### To the Skills Hub

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```

### To a Custom Repository

Add your repo as a tap:

```bash
hermes skills tap add owner/repo
```

Users can then search and install from your repository.

## Security Scanning

All hub-installed skills go through a security scanner that checks for:

- Data exfiltration patterns
- Prompt injection attempts
- Destructive commands
- Shell injection

Trust levels:
- `builtin` — ships with Hermes (always trusted)
- `official` — from `optional-skills/` in the repo (built-in trust, no third-party warning)
- `trusted` — from openai/skills, anthropics/skills, huggingface/skills
- `community` — non-dangerous findings can be overridden with `--force`; `dangerous` verdicts remain blocked

Hermes can now consume third-party skills from multiple external discovery models:
- direct GitHub identifiers (for example `openai/skills/k8s`)
- `skills.sh` identifiers (for example `skills-sh/vercel-labs/json-render/json-render-react`)
- well-known endpoints served from `/.well-known/skills/index.json`

If you want your skills to be discoverable without a GitHub-specific installer, consider serving them from a well-known endpoint in addition to publishing them in a repo or marketplace.

---

# SOURCE: website/docs/reference/skills-catalog.md

---
sidebar_position: 5
title: "Bundled Skills Catalog"
description: "Catalog of bundled skills that ship with Hermes Agent"
---

# Bundled Skills Catalog

Hermes ships with a large built-in skill library copied into `~/.hermes/skills/` on install. Each skill below links to a dedicated page with its full definition, setup, and usage.

Hermes also syncs bundled skills on `hermes update`, but the sync manifest respects local deletions and user edits. If a skill listed here is missing from your profile's `~/.hermes/skills/` tree, it is still shipped with Hermes; restore it with `hermes skills reset <name> --restore`.

If a skill is missing from this list but present in the repo, the catalog is regenerated by `website/scripts/generate-skill-docs.py`.

## apple

| Skill | Description | Path |
|-------|-------------|------|
| [`apple-notes`](/docs/user-guide/skills/bundled/apple/apple-apple-notes) | Manage Apple Notes via memo CLI: create, search, edit. | `apple/apple-notes` |
| [`apple-reminders`](/docs/user-guide/skills/bundled/apple/apple-apple-reminders) | Apple Reminders via remindctl: add, list, complete. | `apple/apple-reminders` |
| [`findmy`](/docs/user-guide/skills/bundled/apple/apple-findmy) | Track Apple devices/AirTags via FindMy.app on macOS. | `apple/findmy` |
| [`imessage`](/docs/user-guide/skills/bundled/apple/apple-imessage) | Send and receive iMessages/SMS via the imsg CLI on macOS. | `apple/imessage` |
| [`macos-computer-use`](/docs/user-guide/skills/bundled/apple/apple-macos-computer-use) | Drive the macOS desktop in the background — screenshots, mouse, keyboard, scroll, drag — without stealing the user's cursor, keyboard focus, or Space. Works with any tool-capable model. Load this skill whenever the `computer_use` tool is... | `apple/macos-computer-use` |

## autonomous-ai-agents

| Skill | Description | Path |
|-------|-------------|------|
| [`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code) | Delegate coding to Claude Code CLI (features, PRs). | `autonomous-ai-agents/claude-code` |
| [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex) | Delegate coding to OpenAI Codex CLI (features, PRs). | `autonomous-ai-agents/codex` |
| [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) | Configure, extend, or contribute to Hermes Agent. | `autonomous-ai-agents/hermes-agent` |
| [`opencode`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) | Delegate coding to OpenCode CLI (features, PR review). | `autonomous-ai-agents/opencode` |

## creative

| Skill | Description | Path |
|-------|-------------|------|
| [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) | Dark-themed SVG architecture/cloud/infra diagrams as HTML. | `creative/architecture-diagram` |
| [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art) | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. | `creative/ascii-art` |
| [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video) | ASCII video: convert video/audio to colored ASCII MP4/GIF. | `creative/ascii-video` |
| [`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic) | Infographics: 21 layouts x 21 styles (信息图, 可视化). | `creative/baoyu-infographic` |
| [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design) | Design one-off HTML artifacts (landing, deck, prototype). | `creative/claude-design` |
| [`comfyui`](/docs/user-guide/skills/bundled/creative/creative-comfyui) | Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for lifecycle and direct REST/WebSocket API for execution. | `creative/comfyui` |
| [`design-md`](/docs/user-guide/skills/bundled/creative/creative-design-md) | Author/validate/export Google's DESIGN.md token spec files. | `creative/design-md` |
| [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw) | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). | `creative/excalidraw` |
| [`humanizer`](/docs/user-guide/skills/bundled/creative/creative-humanizer) | Humanize text: strip AI-isms and add real voice. | `creative/humanizer` |
| [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video) | Manim CE animations: 3Blue1Brown math/algo videos. | `creative/manim-video` |
| [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js) | p5.js sketches: gen art, shaders, interactive, 3D. | `creative/p5js` |
| [`popular-web-designs`](/docs/user-guide/skills/bundled/creative/creative-popular-web-designs) | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. | `creative/popular-web-designs` |
| [`pretext`](/docs/user-guide/skills/bundled/creative/creative-pretext) | Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HT... | `creative/pretext` |
| [`sketch`](/docs/user-guide/skills/bundled/creative/creative-sketch) | Throwaway HTML mockups: 2-3 design variants to compare. | `creative/sketch` |
| [`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music) | Songwriting craft and Suno AI music prompts. | `creative/songwriting-and-ai-music` |
| [`touchdesigner-mcp`](/docs/user-guide/skills/bundled/creative/creative-touchdesigner-mcp) | Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 native tools. | `creative/touchdesigner-mcp` |

## data-science

| Skill | Description | Path |
|-------|-------------|------|
| [`jupyter-live-kernel`](/docs/user-guide/skills/bundled/data-science/data-science-jupyter-live-kernel) | Iterative Python via live Jupyter kernel (hamelnb). | `data-science/jupyter-live-kernel` |

## devops

| Skill | Description | Path |
|-------|-------------|------|


## dogfood

| Skill | Description | Path |
|-------|-------------|------|
| [`dogfood`](/docs/user-guide/skills/bundled/dogfood/dogfood-dogfood) | Exploratory QA of web apps: find bugs, evidence, reports. | `dogfood` |

## email

| Skill | Description | Path |
|-------|-------------|------|
| [`himalaya`](/docs/user-guide/skills/bundled/email/email-himalaya) | Himalaya CLI: IMAP/SMTP email from terminal. | `email/himalaya` |

## github

| Skill | Description | Path |
|-------|-------------|------|
| [`codebase-inspection`](/docs/user-guide/skills/bundled/github/github-codebase-inspection) | Inspect codebases w/ pygount: LOC, languages, ratios. | `github/codebase-inspection` |
| [`github-auth`](/docs/user-guide/skills/bundled/github/github-github-auth) | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. | `github/github-auth` |
| [`github-code-review`](/docs/user-guide/skills/bundled/github/github-github-code-review) | Review PRs: diffs, inline comments via gh or REST. | `github/github-code-review` |
| [`github-issues`](/docs/user-guide/skills/bundled/github/github-github-issues) | Create, triage, label, assign GitHub issues via gh or REST. | `github/github-issues` |
| [`github-pr-workflow`](/docs/user-guide/skills/bundled/github/github-github-pr-workflow) | GitHub PR lifecycle: branch, commit, open, CI, merge. | `github/github-pr-workflow` |
| [`github-repo-management`](/docs/user-guide/skills/bundled/github/github-github-repo-management) | Clone/create/fork repos; manage remotes, releases. | `github/github-repo-management` |

## media

| Skill | Description | Path |
|-------|-------------|------|
| [`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search) | Search/download GIFs from Tenor via curl + jq. | `media/gif-search` |
| [`heartmula`](/docs/user-guide/skills/bundled/media/media-heartmula) | HeartMuLa: Suno-like song generation from lyrics + tags. | `media/heartmula` |
| [`songsee`](/docs/user-guide/skills/bundled/media/media-songsee) | Audio spectrograms/features (mel, chroma, MFCC) via CLI. | `media/songsee` |
| [`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content) | YouTube transcripts to summaries, threads, blogs. | `media/youtube-content` |

## mlops

| Skill | Description | Path |
|-------|-------------|------|
| [`audiocraft-audio-generation`](/docs/user-guide/skills/bundled/mlops/mlops-models-audiocraft) | AudioCraft: MusicGen text-to-music, AudioGen text-to-sound. | `mlops/models/audiocraft` |
| [`huggingface-hub`](/docs/user-guide/skills/bundled/mlops/mlops-huggingface-hub) | HuggingFace hf CLI: search/download/upload models, datasets. | `mlops/huggingface-hub` |
| [`llama-cpp`](/docs/user-guide/skills/bundled/mlops/mlops-inference-llama-cpp) | llama.cpp local GGUF inference + HF Hub model discovery. | `mlops/inference/llama-cpp` |
| [`evaluating-llms-harness`](/docs/user-guide/skills/bundled/mlops/mlops-evaluation-lm-evaluation-harness) | lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.). | `mlops/evaluation/lm-evaluation-harness` |
| [`segment-anything-model`](/docs/user-guide/skills/bundled/mlops/mlops-models-segment-anything) | SAM: zero-shot image segmentation via points, boxes, masks. | `mlops/models/segment-anything` |
| [`serving-llms-vllm`](/docs/user-guide/skills/bundled/mlops/mlops-inference-vllm) | vLLM: high-throughput LLM serving, OpenAI API, quantization. | `mlops/inference/vllm` |
| [`weights-and-biases`](/docs/user-guide/skills/bundled/mlops/mlops-evaluation-weights-and-biases) | W&B: log ML experiments, sweeps, model registry, dashboards. | `mlops/evaluation/weights-and-biases` |

## note-taking

| Skill | Description | Path |
|-------|-------------|------|
| [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian) | Read, search, create, and edit notes in the Obsidian vault. | `note-taking/obsidian` |

## productivity

| Skill | Description | Path |
|-------|-------------|------|
| [`airtable`](/docs/user-guide/skills/bundled/productivity/productivity-airtable) | Airtable REST API via curl. Records CRUD, filters, upserts. | `productivity/airtable` |
| [`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace) | Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python. | `productivity/google-workspace` |
| [`maps`](/docs/user-guide/skills/bundled/productivity/productivity-maps) | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. | `productivity/maps` |
| [`nano-pdf`](/docs/user-guide/skills/bundled/productivity/productivity-nano-pdf) | Edit PDF text/typos/titles via nano-pdf CLI (NL prompts). | `productivity/nano-pdf` |
| [`notion`](/docs/user-guide/skills/bundled/productivity/productivity-notion) | Notion API + ntn CLI: pages, databases, markdown, Workers. | `productivity/notion` |
| [`ocr-and-documents`](/docs/user-guide/skills/bundled/productivity/productivity-ocr-and-documents) | Extract text from PDFs/scans (pymupdf, marker-pdf). | `productivity/ocr-and-documents` |
| [`petdex`](/docs/user-guide/skills/bundled/productivity/productivity-petdex) | Install and select animated petdex mascots for Hermes. | `productivity/petdex` |
| [`powerpoint`](/docs/user-guide/skills/bundled/productivity/productivity-powerpoint) | Create, read, edit .pptx decks, slides, notes, templates. | `productivity/powerpoint` |
| [`teams-meeting-pipeline`](/docs/user-guide/skills/bundled/productivity/productivity-teams-meeting-pipeline) | Operate the Teams meeting summary pipeline via Hermes CLI — summarize meetings, inspect pipeline status, replay jobs, manage Microsoft Graph subscriptions. | `productivity/teams-meeting-pipeline` |

## research

| Skill | Description | Path |
|-------|-------------|------|
| [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) | Search arXiv papers by keyword, author, category, or ID. | `research/arxiv` |
| [`blogwatcher`](/docs/user-guide/skills/bundled/research/research-blogwatcher) | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. | `research/blogwatcher` |
| [`llm-wiki`](/docs/user-guide/skills/bundled/research/research-llm-wiki) | Karpathy's LLM Wiki: build/query interlinked markdown KB. | `research/llm-wiki` |
| [`polymarket`](/docs/user-guide/skills/bundled/research/research-polymarket) | Query Polymarket: markets, prices, orderbooks, history. | `research/polymarket` |
| [`research-paper-writing`](/docs/user-guide/skills/bundled/research/research-research-paper-writing) | Write ML papers for NeurIPS/ICML/ICLR: design→submit. | `research/research-paper-writing` |

## smart-home

| Skill | Description | Path |
|-------|-------------|------|
| [`openhue`](/docs/user-guide/skills/bundled/smart-home/smart-home-openhue) | Control Philips Hue lights, scenes, rooms via OpenHue CLI. | `smart-home/openhue` |

## social-media

| Skill | Description | Path |
|-------|-------------|------|
| [`xurl`](/docs/user-guide/skills/bundled/social-media/social-media-xurl) | X/Twitter via xurl CLI: post, search, DM, media, v2 API. | `social-media/xurl` |

## software-development

| Skill | Description | Path |
|-------|-------------|------|
| [`hermes-agent-skill-authoring`](/docs/user-guide/skills/bundled/software-development/software-development-hermes-agent-skill-authoring) | Author in-repo SKILL.md: frontmatter, validator, structure. | `software-development/hermes-agent-skill-authoring` |
| [`node-inspect-debugger`](/docs/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger) | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. | `software-development/node-inspect-debugger` |
| [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) | Plan mode: write an actionable markdown plan to .hermes/plans/, no execution. Bite-sized tasks, exact paths, complete code. | `software-development/plan` |
| [`python-debugpy`](/docs/user-guide/skills/bundled/software-development/software-development-python-debugpy) | Debug Python: pdb REPL + debugpy remote (DAP). | `software-development/python-debugpy` |
| [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) | Pre-commit review: security scan, quality gates, auto-fix. | `software-development/requesting-code-review` |
| [`simplify-code`](/docs/user-guide/skills/bundled/software-development/software-development-simplify-code) | Parallel 3-agent cleanup of recent code changes. | `software-development/simplify-code` |
| [`spike`](/docs/user-guide/skills/bundled/software-development/software-development-spike) | Throwaway experiments to validate an idea before build. | `software-development/spike` |
| [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging) | 4-phase root cause debugging: understand bugs before fixing. | `software-development/systematic-debugging` |
| [`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) | TDD: enforce RED-GREEN-REFACTOR, tests before code. | `software-development/test-driven-development` |

## yuanbao

| Skill | Description | Path |
|-------|-------------|------|
| [`yuanbao`](/docs/user-guide/skills/bundled/yuanbao/yuanbao-yuanbao) | Yuanbao (元宝) groups: @mention users, query info/members. | `yuanbao` |

---

# SOURCE: website/docs/reference/optional-skills-catalog.md

---
sidebar_position: 9
title: "Optional Skills Catalog"
description: "Official optional skills shipped with hermes-agent — install via hermes skills install official/<category>/<skill>"
---

# Optional Skills Catalog

Optional skills ship with hermes-agent under `optional-skills/` but are **not active by default**. Install them explicitly:

```bash
hermes skills install official/<category>/<skill>
```

For example:

```bash
hermes skills install official/blockchain/solana
hermes skills install official/mlops/flash-attention
```

Each skill below links to a dedicated page with its full definition, setup, and usage.

To uninstall:

```bash
hermes skills uninstall <skill-name>
```

## autonomous-ai-agents

| Skill | Description |
|-------|-------------|
| [**antigravity-cli**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-antigravity-cli) | Operate the Antigravity CLI (agy): plugins, auth, sandbox. |
| [**blackbox**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-blackbox) | Delegate coding tasks to Blackbox AI CLI agent. Multi-model agent with built-in judge that runs tasks through multiple LLMs and picks the best result. Requires the blackbox CLI and a Blackbox AI API key. |
| [**grok**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok) | Delegate coding to xAI Grok Build CLI (features, PRs). |
| [**honcho**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-honcho) | Configure and use Honcho memory with Hermes -- cross-session user modeling, multi-profile peer isolation, observation config, dialectic reasoning, session summaries, and context budget enforcement. Use when setting up Honcho, troubleshoo... |
| [**openhands**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-openhands) | Delegate coding to OpenHands CLI (model-agnostic, LiteLLM). |

## blockchain

| Skill | Description |
|-------|-------------|
| [**evm**](/docs/user-guide/skills/optional/blockchain/blockchain-evm) | Read-only EVM client: wallets, tokens, gas across 8 chains. |
| [**hyperliquid**](/docs/user-guide/skills/optional/blockchain/blockchain-hyperliquid) | Hyperliquid market data, account history, trade review. |
| [**solana**](/docs/user-guide/skills/optional/blockchain/blockchain-solana) | Query Solana blockchain data with USD pricing — wallet balances, token portfolios with values, transaction details, NFTs, whale detection, and live network stats. Uses Solana RPC + CoinGecko. No API key required. |

## communication

| Skill | Description |
|-------|-------------|
| [**one-three-one-rule**](/docs/user-guide/skills/optional/communication/communication-one-three-one-rule) | Structured decision-making framework for technical proposals and trade-off analysis. When the user faces a choice between multiple approaches (architecture decisions, tool selection, refactoring strategies, migration paths), this skill p... |

## creative

| Skill | Description |
|-------|-------------|
| [**baoyu-article-illustrator**](/docs/user-guide/skills/optional/creative/creative-baoyu-article-illustrator) | Article illustrations: type × style × palette consistency. |
| [**baoyu-comic**](/docs/user-guide/skills/optional/creative/creative-baoyu-comic) | Knowledge comics (知识漫画): educational, biography, tutorial. |
| [**blender-mcp**](/docs/user-guide/skills/optional/creative/creative-blender-mcp) | Control Blender directly from Hermes via socket connection to the blender-mcp addon. Create 3D objects, materials, animations, and run arbitrary Blender Python (bpy) code. Use when user wants to create or modify anything in Blender. |
| [**concept-diagrams**](/docs/user-guide/skills/optional/creative/creative-concept-diagrams) | Generate flat, minimal light/dark-aware SVG diagrams as standalone HTML files, using a unified educational visual language with 9 semantic color ramps, sentence-case typography, and automatic dark mode. Best suited for educational and no... |
| [**creative-ideation**](/docs/user-guide/skills/optional/creative/creative-creative-ideation) | Generate ideas via named methods from creative practice. |
| [**hyperframes**](/docs/user-guide/skills/optional/creative/creative-hyperframes) | Create HTML-based video compositions, animated title cards, social overlays, captioned talking-head videos, audio-reactive visuals, and shader transitions using HyperFrames. HTML is the source of truth for video. Use when the user wants... |
| [**kanban-video-orchestrator**](/docs/user-guide/skills/optional/creative/creative-kanban-video-orchestrator) | Plan, set up, and monitor a multi-agent video production pipeline backed by Hermes Kanban. Use when the user wants to make ANY video — narrative film, product/marketing, music video, explainer, ASCII/terminal art, abstract/generative loo... |
| [**meme-generation**](/docs/user-guide/skills/optional/creative/creative-meme-generation) | Generate real meme images by picking a template and overlaying text with Pillow. Produces actual .png meme files. |
| [**pixel-art**](/docs/user-guide/skills/optional/creative/creative-pixel-art) | Pixel art w/ era palettes (NES, Game Boy, PICO-8). |

## devops

| Skill | Description |
|-------|-------------|
| [**inference-sh-cli**](/docs/user-guide/skills/optional/devops/devops-cli) | Run 150+ AI apps via inference.sh CLI (infsh) — image generation, video creation, LLMs, search, 3D, social automation. Uses the terminal tool. Triggers: inference.sh, infsh, ai apps, flux, veo, image generation, video generation, seedrea... |
| [**docker-management**](/docs/user-guide/skills/optional/devops/devops-docker-management) | Manage Docker containers, images, volumes, networks, and Compose stacks — lifecycle ops, debugging, cleanup, and Dockerfile optimization. |
| [**hermes-s6-container-supervision**](/docs/user-guide/skills/optional/devops/devops-hermes-s6-container-supervision) | Modify, debug, or extend the s6-overlay supervision tree inside the Hermes Agent Docker image — adding new services, debugging profile gateways, understanding the Architecture B main-program pattern. |
| [**pinggy-tunnel**](/docs/user-guide/skills/optional/devops/devops-pinggy-tunnel) | Zero-install localhost tunnels over SSH via Pinggy. |
| [**watchers**](/docs/user-guide/skills/optional/devops/devops-watchers) | Poll RSS, JSON APIs, and GitHub with watermark dedup. |

## dogfood

| Skill | Description |
|-------|-------------|
| [**adversarial-ux-test**](/docs/user-guide/skills/optional/dogfood/dogfood-adversarial-ux-test) | Roleplay the most difficult, tech-resistant user for your product. Browse the app as that persona, find every UX pain point, then filter complaints through a pragmatism layer to separate real problems from noise. Creates actionable ticke... |

## email

| Skill | Description |
|-------|-------------|
| [**agentmail**](/docs/user-guide/skills/optional/email/email-agentmail) | Give the agent its own dedicated email inbox via AgentMail. Send, receive, and manage email autonomously using agent-owned email addresses (e.g. hermes-agent@agentmail.to). |

## finance

| Skill | Description |
|-------|-------------|
| [**3-statement-model**](/docs/user-guide/skills/optional/finance/finance-3-statement-model) | Build fully-integrated 3-statement models (IS, BS, CF) in Excel with working capital schedules, D&A roll-forwards, debt schedule, and the plugs that make cash and retained earnings tie. Pairs with excel-author. |
| [**comps-analysis**](/docs/user-guide/skills/optional/finance/finance-comps-analysis) | Build comparable company analysis in Excel — operating metrics, valuation multiples, statistical benchmarking vs peer sets. Pairs with excel-author. Use for public-company valuation, IPO pricing, sector benchmarking, or outlier detection. |
| [**dcf-model**](/docs/user-guide/skills/optional/finance/finance-dcf-model) | Build institutional-quality DCF valuation models in Excel — revenue projections, FCF build, WACC, terminal value, Bear/Base/Bull scenarios, 5x5 sensitivity tables. Pairs with excel-author. Use for intrinsic-value equity analysis. |
| [**excel-author**](/docs/user-guide/skills/optional/finance/finance-excel-author) | Build auditable Excel workbooks headless with openpyxl — blue/black/green cell conventions, formulas over hardcodes, named ranges, balance checks, sensitivity tables. Use for financial models, audit outputs, reconciliations. |
| [**lbo-model**](/docs/user-guide/skills/optional/finance/finance-lbo-model) | Build leveraged buyout models in Excel — sources & uses, debt schedule, cash sweep, exit multiple, IRR/MOIC sensitivity. Pairs with excel-author. Use for PE screening, sponsor-case valuation, or illustrative LBO in a pitch. |
| [**merger-model**](/docs/user-guide/skills/optional/finance/finance-merger-model) | Build accretion/dilution (merger) models in Excel — pro-forma P&L, synergies, financing mix, EPS impact. Pairs with excel-author. Use for M&A pitches, board materials, or deal evaluation. |
| [**pptx-author**](/docs/user-guide/skills/optional/finance/finance-pptx-author) | Build PowerPoint decks headless with python-pptx. Pairs with excel-author for model-backed decks where every number traces to a workbook cell. Use for pitch decks, IC memos, earnings notes. |
| [**stocks**](/docs/user-guide/skills/optional/finance/finance-stocks) | Stock quotes, history, search, compare, crypto via Yahoo. |

## gaming

| Skill | Description |
|-------|-------------|
| [**minecraft-modpack-server**](/docs/user-guide/skills/optional/gaming/gaming-minecraft-modpack-server) | Host modded Minecraft servers (CurseForge, Modrinth). |
| [**pokemon-player**](/docs/user-guide/skills/optional/gaming/gaming-pokemon-player) | Play Pokemon via headless emulator + RAM reads. |

## health

| Skill | Description |
|-------|-------------|
| [**fitness-nutrition**](/docs/user-guide/skills/optional/health/health-fitness-nutrition) | Gym workout planner and nutrition tracker. Search 690+ exercises by muscle, equipment, or category via wger. Look up macros and calories for 380,000+ foods via USDA FoodData Central. Compute BMI, TDEE, one-rep max, macro splits, and body... |
| [**neuroskill-bci**](/docs/user-guide/skills/optional/health/health-neuroskill-bci) | Connect to a running NeuroSkill instance and incorporate the user's real-time cognitive and emotional state (focus, relaxation, mood, cognitive load, drowsiness, heart rate, HRV, sleep staging, and 40+ derived EXG scores) into responses.... |

## mcp

| Skill | Description |
|-------|-------------|
| [**fastmcp**](/docs/user-guide/skills/optional/mcp/mcp-fastmcp) | Build, test, inspect, install, and deploy MCP servers with FastMCP in Python. Use when creating a new MCP server, wrapping an API or database as MCP tools, exposing resources or prompts, or preparing a FastMCP server for Claude Code, Cur... |
| [**mcporter**](/docs/user-guide/skills/optional/mcp/mcp-mcporter) | Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation. |

## migration

| Skill | Description |
|-------|-------------|
| [**openclaw-migration**](/docs/user-guide/skills/optional/migration/migration-openclaw-migration) | Migrate a user's OpenClaw customization footprint into Hermes Agent. Imports Hermes-compatible memories, SOUL.md, command allowlists, user skills, and selected workspace assets from ~/.openclaw, then reports exactly what could not be mig... |

## mlops

| Skill | Description |
|-------|-------------|
| [**huggingface-accelerate**](/docs/user-guide/skills/optional/mlops/mlops-accelerate) | Simplest distributed training API. 4 lines to add distributed support to any PyTorch script. Unified API for DeepSpeed/FSDP/Megatron/DDP. Automatic device placement, mixed precision (FP16/BF16/FP8). Interactive config, single launch comm... |
| [**axolotl**](/docs/user-guide/skills/optional/mlops/mlops-training-axolotl) | Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO). |
| [**chroma**](/docs/user-guide/skills/optional/mlops/mlops-chroma) | Open-source embedding database for AI applications. Store embeddings and metadata, perform vector and full-text search, filter by metadata. Simple 4-function API. Scales from notebooks to production clusters. Use for semantic search, RAG... |
| [**clip**](/docs/user-guide/skills/optional/mlops/mlops-clip) | OpenAI's model connecting vision and language. Enables zero-shot image classification, image-text matching, and cross-modal retrieval. Trained on 400M image-text pairs. Use for image search, content moderation, or vision-language tasks w... |
| [**dspy**](/docs/user-guide/skills/optional/mlops/mlops-research-dspy) | DSPy: declarative LM programs, auto-optimize prompts, RAG. |
| [**faiss**](/docs/user-guide/skills/optional/mlops/mlops-faiss) | Facebook's library for efficient similarity search and clustering of dense vectors. Supports billions of vectors, GPU acceleration, and various index types (Flat, IVF, HNSW). Use for fast k-NN search, large-scale vector retrieval, or whe... |
| [**optimizing-attention-flash**](/docs/user-guide/skills/optional/mlops/mlops-flash-attention) | Optimizes transformer attention with Flash Attention for 2-4x speedup and 10-20x memory reduction. Use when training/running transformers with long sequences (>512 tokens), encountering GPU memory issues with attention, or need faster in... |
| [**guidance**](/docs/user-guide/skills/optional/mlops/mlops-guidance) | Control LLM output with regex and grammars, guarantee valid JSON/XML/code generation, enforce structured formats, and build multi-step workflows with Guidance - Microsoft Research's constrained generation framework |
| [**huggingface-tokenizers**](/docs/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) | Fast tokenizers optimized for research and production. Rust-based implementation tokenizes 1GB in &lt;20 seconds. Supports BPE, WordPiece, and Unigram algorithms. Train custom vocabularies, track alignments, handle padding/truncation. Integ... |
| [**instructor**](/docs/user-guide/skills/optional/mlops/mlops-instructor) | Extract structured data from LLM responses with Pydantic validation, retry failed extractions automatically, parse complex JSON with type safety, and stream partial results with Instructor - battle-tested structured output library |
| [**lambda-labs-gpu-cloud**](/docs/user-guide/skills/optional/mlops/mlops-lambda-labs) | Reserved and on-demand GPU cloud instances for ML training and inference. Use when you need dedicated GPU instances with simple SSH access, persistent filesystems, or high-performance multi-node clusters for large-scale training. |
| [**llava**](/docs/user-guide/skills/optional/mlops/mlops-llava) | Large Language and Vision Assistant. Enables visual instruction tuning and image-based conversations. Combines CLIP vision encoder with Vicuna/LLaMA language models. Supports multi-turn image chat, visual question answering, and instruct... |
| [**modal-serverless-gpu**](/docs/user-guide/skills/optional/mlops/mlops-modal) | Serverless GPU cloud platform for running ML workloads. Use when you need on-demand GPU access without infrastructure management, deploying ML models as APIs, or running batch jobs with automatic scaling. |
| [**nemo-curator**](/docs/user-guide/skills/optional/mlops/mlops-nemo-curator) | GPU-accelerated data curation for LLM training. Supports text/image/video/audio. Features fuzzy deduplication (16× faster), quality filtering (30+ heuristics), semantic deduplication, PII redaction, NSFW detection. Scales across GPUs wit... |
| [**obliteratus**](/docs/user-guide/skills/optional/mlops/mlops-obliteratus) | OBLITERATUS: abliterate LLM refusals (diff-in-means). |
| [**outlines**](/docs/user-guide/skills/optional/mlops/mlops-inference-outlines) | Outlines: structured JSON/regex/Pydantic LLM generation. |
| [**peft-fine-tuning**](/docs/user-guide/skills/optional/mlops/mlops-peft) | Parameter-efficient fine-tuning for LLMs using LoRA, QLoRA, and 25+ methods. Use when fine-tuning large models (7B-70B) with limited GPU memory, when you need to train &lt;1% of parameters with minimal accuracy loss, or for multi-adapter se... |
| [**pinecone**](/docs/user-guide/skills/optional/mlops/mlops-pinecone) | Managed vector database for production AI applications. Fully managed, auto-scaling, with hybrid search (dense + sparse), metadata filtering, and namespaces. Low latency (&lt;100ms p95). Use for production RAG, recommendation systems, or se... |
| [**pytorch-fsdp**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-fsdp) | Expert guidance for Fully Sharded Data Parallel training with PyTorch FSDP - parameter sharding, mixed precision, CPU offloading, FSDP2 |
| [**pytorch-lightning**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-lightning) | High-level PyTorch framework with Trainer class, automatic distributed training (DDP/FSDP/DeepSpeed), callbacks system, and minimal boilerplate. Scales from laptop to supercomputer with same code. Use when you want clean training loops w... |
| [**qdrant-vector-search**](/docs/user-guide/skills/optional/mlops/mlops-qdrant) | High-performance vector similarity search engine for RAG and semantic search. Use when building production RAG systems requiring fast nearest neighbor search, hybrid search with filtering, or scalable vector storage with Rust-powered per... |
| [**sparse-autoencoder-training**](/docs/user-guide/skills/optional/mlops/mlops-saelens) | Provides guidance for training and analyzing Sparse Autoencoders (SAEs) using SAELens to decompose neural network activations into interpretable features. Use when discovering interpretable features, analyzing superposition, or studying... |
| [**simpo-training**](/docs/user-guide/skills/optional/mlops/mlops-simpo) | Simple Preference Optimization for LLM alignment. Reference-free alternative to DPO with better performance (+6.4 points on AlpacaEval 2.0). No reference model needed, more efficient than DPO. Use for preference alignment when want simpl... |
| [**slime-rl-training**](/docs/user-guide/skills/optional/mlops/mlops-slime) | Provides guidance for LLM post-training with RL using slime, a Megatron+SGLang framework. Use when training GLM models, implementing custom data generation workflows, or needing tight Megatron-LM integration for RL scaling. |
| [**stable-diffusion-image-generation**](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion) | State-of-the-art text-to-image generation with Stable Diffusion models via HuggingFace Diffusers. Use when generating images from text prompts, performing image-to-image translation, inpainting, or building custom diffusion pipelines. |
| [**tensorrt-llm**](/docs/user-guide/skills/optional/mlops/mlops-tensorrt-llm) | Optimizes LLM inference with NVIDIA TensorRT for maximum throughput and lowest latency. Use for production deployment on NVIDIA GPUs (A100/H100), when you need 10-100x faster inference than PyTorch, or for serving models with quantizatio... |
| [**distributed-llm-pretraining-torchtitan**](/docs/user-guide/skills/optional/mlops/mlops-torchtitan) | Provides PyTorch-native distributed LLM pretraining using torchtitan with 4D parallelism (FSDP2, TP, PP, CP). Use when pretraining Llama 3.1, DeepSeek V3, or custom models at scale from 8 to 512+ GPUs with Float8, torch.compile, and dist... |
| [**fine-tuning-with-trl**](/docs/user-guide/skills/optional/mlops/mlops-training-trl-fine-tuning) | TRL: SFT, DPO, PPO, GRPO, reward modeling for LLM RLHF. |
| [**unsloth**](/docs/user-guide/skills/optional/mlops/mlops-training-unsloth) | Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM. |
| [**whisper**](/docs/user-guide/skills/optional/mlops/mlops-whisper) | OpenAI's general-purpose speech recognition model. Supports 99 languages, transcription, translation to English, and language identification. Six model sizes from tiny (39M params) to large (1550M params). Use for speech-to-text, podcast... |

## payments

| Skill | Description |
|-------|-------------|
| [**mpp-agent**](/docs/user-guide/skills/optional/payments/payments-mpp-agent) | Pay HTTP 402 APIs via Machine Payments Protocol (MPP). |
| [**stripe-link-cli**](/docs/user-guide/skills/optional/payments/payments-stripe-link-cli) | Agent payments via Stripe Link — cards, SPT, approvals. |
| [**stripe-projects**](/docs/user-guide/skills/optional/payments/payments-stripe-projects) | Provision SaaS services + sync creds via Stripe Projects. |

## productivity

| Skill | Description |
|-------|-------------|
| [**canvas**](/docs/user-guide/skills/optional/productivity/productivity-canvas) | Canvas LMS integration — fetch enrolled courses and assignments using API token authentication. |
| [**here.now**](/docs/user-guide/skills/optional/productivity/productivity-here-now) | Publish static sites to &#123;slug&#125;.here.now and store private files in cloud Drives for agent-to-agent handoff. |
| [**memento-flashcards**](/docs/user-guide/skills/optional/productivity/productivity-memento-flashcards) | Spaced-repetition flashcard system. Create cards from facts or text, chat with flashcards using free-text answers graded by the agent, generate quizzes from YouTube transcripts, review due cards with adaptive scheduling, and export/impor... |
| [**shop**](/docs/user-guide/skills/optional/productivity/productivity-shop) | Shop catalog search, checkout, order tracking, returns. |
| [**shopify**](/docs/user-guide/skills/optional/productivity/productivity-shopify) | Shopify Admin & Storefront GraphQL APIs via curl. Products, orders, customers, inventory, metafields. |
| [**siyuan**](/docs/user-guide/skills/optional/productivity/productivity-siyuan) | SiYuan Note API for searching, reading, creating, and managing blocks and documents in a self-hosted knowledge base via curl. |
| [**telephony**](/docs/user-guide/skills/optional/productivity/productivity-telephony) | Give Hermes phone capabilities without core tool changes. Provision and persist a Twilio number, send and receive SMS/MMS, make direct calls, and place AI-driven outbound calls through Bland.ai or Vapi. |

## research

| Skill | Description |
|-------|-------------|
| [**bioinformatics**](/docs/user-guide/skills/optional/research/research-bioinformatics) | Gateway to 400+ bioinformatics skills from bioSkills and ClawBio. Covers genomics, transcriptomics, single-cell, variant calling, pharmacogenomics, metagenomics, structural biology, and more. Fetches domain-specific reference material on... |
| [**darwinian-evolver**](/docs/user-guide/skills/optional/research/research-darwinian-evolver) | Evolve prompts/regex/SQL/code with Imbue's evolution loop. |
| [**domain-intel**](/docs/user-guide/skills/optional/research/research-domain-intel) | Passive domain reconnaissance using Python stdlib. Subdomain discovery, SSL certificate inspection, WHOIS lookups, DNS records, domain availability checks, and bulk multi-domain analysis. No API keys required. |
| [**drug-discovery**](/docs/user-guide/skills/optional/research/research-drug-discovery) | Pharmaceutical research assistant for drug discovery workflows. Search bioactive compounds on ChEMBL, calculate drug-likeness (Lipinski Ro5, QED, TPSA, synthetic accessibility), look up drug-drug interactions via OpenFDA, interpret ADMET... |
| [**duckduckgo-search**](/docs/user-guide/skills/optional/research/research-duckduckgo-search) | Free web search via DuckDuckGo — text, news, images, videos. No API key needed. Prefer the `ddgs` CLI when installed; use the Python DDGS library only after verifying that `ddgs` is available in the current runtime. |
| [**gitnexus-explorer**](/docs/user-guide/skills/optional/research/research-gitnexus-explorer) | Index a codebase with GitNexus and serve an interactive knowledge graph via web UI + Cloudflare tunnel. |
| [**osint-investigation**](/docs/user-guide/skills/optional/research/research-osint-investigation) | Public-records OSINT investigation framework — SEC EDGAR filings, USAspending contracts, Senate lobbying, OFAC sanctions, ICIJ offshore leaks, NYC property records (ACRIS), OpenCorporates registries, CourtListener court records, Wayback... |
| [**parallel-cli**](/docs/user-guide/skills/optional/research/research-parallel-cli) | Optional vendor skill for Parallel CLI — agent-native web search, extraction, deep research, enrichment, FindAll, and monitoring. Prefer JSON output and non-interactive flows. |
| [**qmd**](/docs/user-guide/skills/optional/research/research-qmd) | Search personal knowledge bases, notes, docs, and meeting transcripts locally using qmd — a hybrid retrieval engine with BM25, vector search, and LLM reranking. Supports CLI and MCP integration. |
| [**scrapling**](/docs/user-guide/skills/optional/research/research-scrapling) | Web scraping with Scrapling - HTTP fetching, stealth browser automation, Cloudflare bypass, and spider crawling via CLI and Python. |
| [**searxng-search**](/docs/user-guide/skills/optional/research/research-searxng-search) | Free meta-search via SearXNG — aggregates results from 70+ search engines. Self-hosted or use a public instance. No API key needed. Falls back automatically when the web search toolset is unavailable. |

## security

| Skill | Description |
|-------|-------------|
| [**1password**](/docs/user-guide/skills/optional/security/security-1password) | Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in, and reading/injecting secrets for commands. |
| [**godmode**](/docs/user-guide/skills/optional/security/security-godmode) | Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN. |
| [**oss-forensics**](/docs/user-guide/skills/optional/security/security-oss-forensics) | Supply chain investigation, evidence recovery, and forensic analysis for GitHub repositories. Covers deleted commit recovery, force-push detection, IOC extraction, multi-source evidence collection, hypothesis formation/validation, and st... |
| [**sherlock**](/docs/user-guide/skills/optional/security/security-sherlock) | OSINT username search across 400+ social networks. Hunt down social media accounts by username. |
| [**web-pentest**](/docs/user-guide/skills/optional/security/security-web-pentest) | Authorized web application penetration testing — reconnaissance, vulnerability analysis, proof-based exploitation, and professional reporting. Adapts Shannon's "No Exploit, No Report" methodology with hard guardrails for scope, authoriza... |

## software-development

| Skill | Description |
|-------|-------------|
| [**code-wiki**](/docs/user-guide/skills/optional/software-development/software-development-code-wiki) | Generate wiki docs + Mermaid diagrams for any codebase. |
| [**rest-graphql-debug**](/docs/user-guide/skills/optional/software-development/software-development-rest-graphql-debug) | Debug REST/GraphQL APIs: status codes, auth, schemas, repro. |
| [**subagent-driven-development**](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development) | Execute plans via delegate_task subagents (2-stage review). |

## web-development

| Skill | Description |
|-------|-------------|
| [**page-agent**](/docs/user-guide/skills/optional/web-development/web-development-page-agent) | Embed alibaba/page-agent into your own web application — a pure-JavaScript in-page GUI agent that ships as a single &lt;script> tag or npm package and lets end-users of your site drive the UI with natural language ("click login, fill userna... |

---

## Contributing Optional Skills

To add a new optional skill to the repository:

1. Create a directory under `optional-skills/<category>/<skill-name>/`
2. Add a `SKILL.md` with standard frontmatter (name, description, version, author)
3. Include any supporting files in `references/`, `templates/`, or `scripts/` subdirectories
4. Submit a pull request — the skill will appear in this catalog and get its own docs page once merged
