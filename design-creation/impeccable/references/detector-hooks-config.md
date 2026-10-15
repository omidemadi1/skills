# Detector, Hooks & Config

## Detector CLI

Deterministic design checks without AI. Runs from terminal.

```bash
npx impeccable detect src/                    # scan folder
npx impeccable detect src/components/Card.tsx # scan one file
npx impeccable detect https://example.com     # scan rendered page
npx impeccable detect --json src/             # machine-readable
npx impeccable detect --scope type src/       # narrow to one domain
npx impeccable detect --no-design-system src/ # skip DESIGN.md checks
```

**Exit codes:** 0 = clean, 2 = findings, 1 = failed.

**What it checks:** contrast, typography drift, layout overflow, AI-design tells, brittle motion, design-system violations (when DESIGN.md exists).

**Design-system awareness:** When DESIGN.md exists, loads it by default. Checks fonts, literal colors, border radii, literal font sizes from typography ramp. `.impeccable/design.json` sidecar provides richer data.

**Server-side templates:** Add extensions under `detector.extensions` in config: Blade, ERB, Twig, Handlebars get same checks as JSX.

**Stdin:** `cat component.css | npx impeccable detect`

**CI usage:** Fail job on exit code 2, then fix or add narrow ignore.

## Design Hooks

Automatic detector feedback inside Claude Code, GitHub Copilot, Codex, and Cursor.

```bash
/impeccable hooks status   # check state
/impeccable hooks on       # enable
/impeccable hooks off      # disable
npx impeccable install --no-hooks  # skip hook during install
```

### What It Does

Scans direct edits to UI code/styles. When it finds a new issue, sends the agent a short reminder with finding and fix direction.

- **Claude Code, Copilot, Codex:** run after edit
- **Cursor:** checks proposed writes before they land, blocks on issues

### Two Speeds

1. **Per edit:** only objectively broken things (broken images, overflow, contrast failures, tiny text, gradient text, glow, DESIGN.md drift)
2. **End of session:** full rule set across every UI file touched, minus already-reported

Set `"perEditRules": "all"` in config to get every rule on every edit.

### Scanned File Types

`.tsx`, `.jsx`, `.html`, `.vue`, `.svelte`, `.astro`, `.css`, `.scss`, `.sass`, `.less`, `.ts`, `.js`

### Hook Manifests

| Harness | Location |
|---|---|
| Claude Code | `.claude/settings.local.json` |
| GitHub Copilot | `.github/hooks/impeccable.json` (committed) |
| Codex | `.codex/hooks.json` |
| Cursor | `.cursor/hooks.json` |

**Codex:** Requires approval step after install — open `/hooks` and approve.

### Checking It Runs

A hook can look installed and scan nothing. `/impeccable doctor` checks for: script path not resolving, manifest says enabled while config says otherwise.

## Config & Ignores

Runtime settings live under `.impeccable/`.

### Usual Path

```bash
npx impeccable ignores list
npx impeccable ignores add-value overused-font "Inter" --reason "Brand font"
npx impeccable ignores add-file "src/legacy/**"
npx impeccable ignores add-rule side-tab
npx impeccable ignores remove-value overused-font "Inter"
```

### Shared vs Local

- `.impeccable/config.json` — commit for team intent (legacy folders, brand exceptions)
- `.impeccable/config.local.json` — private, kept out of git. `--local` flag

### Value Ignores

Prefer value ignores when a rule reports a specific value. Keeps the rule useful elsewhere.

Wildcard value ignores require file scope:
```bash
npx impeccable ignores add-value design-system-color "*" --file "src/demo.css"
```

### Inline Ignore Comments

For waivers that travel with files:

```html
<!-- impeccable-disable overused-font: exported brand doc -->
/* impeccable-disable overused-font */            /* whole file */
/* impeccable-disable-line overused-font */       /* one line */
/* impeccable-disable-next-line overused-font */  /* next line */
```

### Project Roots

When design boundaries don't align with package-manager workspaces:

```json
{ "projectRoots": ["docs/design/skins/*"] }
```

Each matched folder becomes its own project with its own PRODUCT.md/DESIGN.md, falls back to repo root for missing files.

### Config Fails Quietly

Misspelled keys are never read. Stale rule IDs suppress nothing. `/impeccable doctor` catches all three.

## Doctor

Find and repair drift between project files and installed version.

**Boot check (automatic):** Cheap scan at session start — stale PRODUCT.md, outdated design sidecar, config typos, platform mismatches. At most once per week per project.

**On-demand:** `/impeccable doctor` runs deep pass — how much code shipped since DESIGN.md last touched, whether ignored detector rules still exist, whether hook script path resolves.

**Three kinds of findings:**
1. **Mechanical** — repairs automatically, tells you in one line
2. **Worth knowing** — states once with fix on offer
3. **Needs a command** — names init or document and the specific gap

Empty report = good outcome.
