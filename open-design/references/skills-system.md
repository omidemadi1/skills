# Open Design Skill System

How skills, design templates, and the SKILL.md format work in Open Design.

## Two Registries

| Registry | Lives in | API | Purpose |
|---|---|---|---|
| Functional skills | `skills/` | `/api/skills` | Agent capabilities invoked mid-task |
| Design templates | `design-templates/` | `/api/design-templates` | Rendering catalogue for artifacts |

The classification rule: if it *renders* a design artifact (deck, prototype, image), it's a design template. If it's a capability the agent invokes to do work (brief, audit, utility), it's a functional skill.

## SKILL.md Format

Every skill is a directory with at minimum `SKILL.md`:

```
skill-name/
├── SKILL.md              # manifest + workflow instructions
├── assets/               # templates, images, boilerplate
└── references/           # knowledge files for planning
```

### Frontmatter (YAML)

```yaml
---
name: my-skill
description: |
  What this skill does.
triggers:
  - "trigger phrase 1"
  - "trigger phrase 2"

# OD extensions (optional)
od:
  mode: prototype              # prototype|deck|template|design-system|image|video|audio
  surface: web                 # web|image|video|audio
  scenario: marketing          # gallery/filter hint
  category: web-artifacts      # filter slug
  preview:
    type: html
  example_prompt: "Create a..."
  design_system:
    requires: true             # inject active design system
  craft:
    requires: [typography, color, anti-ai-slop]  # inject craft references
  critique:
    policy: opt-in             # required|opt-in|opt-out
---
```

### Modes

| Mode | Purpose | Output |
|---|---|---|
| `prototype` | Single-screen interactive prototype | `index.html` or `Prototype.jsx` |
| `deck` | Multi-slide presentation | `index.html` + `slides.json` |
| `template` | Pre-built artifact, agent personalizes | Populated template copy |
| `design-system` | Create/audit/transform design material | `DESIGN.md` + tokens |
| `image` | Image generation | Image files |
| `video` | Video generation | Video files |
| `audio` | Audio generation | Audio files |

### Defaults (when od: is omitted)

- `mode`: inferred from description, falls back to `prototype`
- `surface`: `web` (unless media mode)
- `preview.type`: `html`
- `design_system.requires`: `true`
- `example_prompt`: first sentence of description

## Design Templates

Under `design-templates/<template>/`, each has `SKILL.md` + rendering assets.

### Template Types

| Type | What it renders |
|---|---|
| Interface | Web/desktop/mobile prototypes |
| Deck | Presentations (PPTX/PDF) |
| Document | PDFs, reports, one-pagers |
| Image | Static visuals, social cards |
| Video | Motion graphics, clips |
| Audio | Sound effects, speech |
| HyperFrames | Programmatic motion → MP4 |

### Template Anatomy

```
design-templates/my-template/
├── SKILL.md           # frontmatter + workflow
├── example.html       # rendered example
├── example.md         # example brief
├── assets/
│   ├── template.html  # base HTML template
│   └── references/    # layout/style references
└── references/
    └── checklist.md   # quality checklist
```

## Craft References

Universal brand-agnostic rules injected via `od.craft.requires`:

| Slug | File | What it covers |
|---|---|---|
| `typography` | `craft/typography.md` | Font pairing, scale, line height, contrast |
| `color` | `craft/color.md` | Palette, WCAG, accent usage |
| `anti-ai-slop` | `craft/anti-ai-slop.md` | Generic AI pattern avoidance |
| `layout` | `craft/layout.md` | Grid, spacing, rhythm |
| `responsive` | `craft/responsive.md` | Mobile-first, breakpoints |
| `accessibility` | `craft/accessibility.md` | ARIA, keyboard, screen readers |
| `motion` | `craft/motion.md` | Animation principles |
| `copywriting` | `craft/copywriting.md` | Voice, tone, clarity |

Craft references are injected between the design system context and the skill body. If the user's brand guidance conflicts, brand guidance wins.

## How the Daemon Loads Skills

1. User-managed skills are checked first, then bundled `skills/`
2. Duplicate `name` in user-managed shadows the bundled entry
3. Lazy scanner picks up new skills on next `/api/skills` request — no rebuild
4. Before a project run, daemon copies active skill + side files to `.od-skills/`
5. Prompt preamble advertises the CWD-relative copy

## Adding a Skill (Quick)

1. Create `skills/<name>/SKILL.md` with `name`, `description`, `triggers`
2. Add `od.mode` and other extensions as needed
3. Drop `assets/` and `references/` alongside
4. Daemon picks it up on next `/api/skills` — no restart needed

## Design Systems

Each system is a package:

```
design-systems/<slug>/
├── manifest.json     # stable id, name, category, description
├── DESIGN.md         # design intent for agents
└── tokens.css        # compiled semantic-token stylesheet
```

DESIGN.md requires at least 7 substantive H2 sections. No fixed heading names — use what fits (theme, color, typography, layout, components, motion, accessibility, anti-patterns).

151 bundled systems from `VoltAgent/awesome-design-md`. New systems: send PR upstream first, OD picks up on sync.
