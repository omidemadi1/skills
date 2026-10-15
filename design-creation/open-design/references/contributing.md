# Open Design Contribution Guide

How to contribute skills, design templates, design systems, and code.

## What You Can Ship in One Afternoon

| Contribution | What it is | Where it lives | Ship size |
|---|---|---|---|
| Design template | Renders a new artifact type | `design-templates/<name>/` | One folder with `SKILL.md` + assets |
| Functional skill | Agent capability invoked mid-task | `skills/<name>/` | One folder with `SKILL.md` |
| Design system | Brand visual language | `design-systems/<slug>/` | `manifest.json` + `DESIGN.md` + `tokens.css` |
| Agent adapter | New coding-agent CLI | `apps/daemon/src/runtimes/defs/` | One definition + registry entry |
| Code feature | Feature/bug fix | `apps/web/src/`, `apps/daemon/` | Normal PR |
| Docs/i18n | Documentation/translations | `docs/`, `README.md` | One PR |

## Adding a Functional Skill

1. Create `skills/<name>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: my-skill
   description: What it does.
   triggers:
     - "trigger phrase"
   od:
     mode: design-system
     category: design-systems
   ---
   ```
2. Add `assets/` and `references/` as needed
3. Daemon picks it up on next `/api/skills` — no rebuild or restart

## Adding a Design Template

1. Create `design-templates/<name>/`:
   ```
   ├── SKILL.md           # frontmatter + workflow
   ├── example.html       # rendered example
   ├── example.md         # example brief
   ├── assets/
   │   ├── template.html  # base template
   │   └── references/
   └── references/
       └── checklist.md
   ```
2. Set `od.mode` to the artifact type (prototype, deck, image, etc.)
3. Include `od.design_system.requires: true` if it should compose with a design system
4. Include `od.craft.requires: [typography, color, anti-ai-slop]` for brand-agnostic craft rules

## Adding a Design System

```bash
design-systems/<slug>/
├── manifest.json         # id, name, category, description, provenance
├── DESIGN.md             # at least 7 substantive H2 sections
└── tokens.css            # compiled semantic-token stylesheet
```

### DESIGN.md Structure (no fixed headings, but typically):

```markdown
# Brand Design System

## Visual theme
## Color roles
## Typography
## Layout and spacing
## Components and states
## Motion and interaction
## Accessibility
## Anti-patterns
```

### Merge Bar

1. Ship all three required files (manifest, DESIGN.md, tokens.css)
2. At least 7 substantive H2 sections
3. Prose and tokens consistent (colors, type, spacing match)
4. Real evidence and clear provenance
5. Useful catalog copy (no marketing fluff)

## Adding an Agent Adapter

1. Create `apps/daemon/src/runtimes/defs/<agent>.ts`:
   ```typescript
   export const fooAgentDef = {
     id: 'foo',
     name: 'Foo Coder',
     bin: 'foo',
     versionArgs: ['--version'],
     fallbackModels: [{ id: 'default', label: 'Default', default: true }],
     buildArgs: (prompt) => ['exec', '-p', prompt],
     streamFormat: 'plain',
   } satisfies RuntimeAgentDef;
   ```
2. Import into `runtimes/registry.ts` and add to `BASE_AGENT_DEFS`
3. Daemon detects it on PATH and exposes in picker

## Contribution Rules

- No `Co-authored-by` trailers in git commits
- PR must fill every section of the PR template
- "Why" must answer both use case and pain being addressed
- "What users will see" from user perspective, not code perspective
- Surface area checklist must reflect both UI and CLI (dual-track)
- If UI is checked, attach screenshots of entry point
- New capabilities need: HTTP endpoint + UI surface + CLI subcommand in same PR
