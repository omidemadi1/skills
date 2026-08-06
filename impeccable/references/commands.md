# Impeccable Commands Reference

All 23 commands, organized by category. Every command reads `PRODUCT.md` + `DESIGN.md` before generating.

## Create

### `/impeccable` (alone)
Inspect the project and recommend 2–3 next commands. Checks whether setup files exist, looks at current state. Asks before running anything.

### `/impeccable <describe it>` (new-work flow)
Build a new page/feature by description. No specific command needed — just say what you want:
```
/impeccable a pricing page for enterprise customers
/impeccable redesign the marketing site
/impeccable add a comparison table to the pricing page
```
Classifies the job (greenfield, extension, redesign, etc.), runs discovery, presents visual directions to pick, then builds. Renders a mock before code is written.

Full details: read `references/new-work.md`.

### `/impeccable shape <target>`
Think before building. Runs a structured discovery interview (5–10 questions) covering purpose, users, content, constraints. Produces a design brief — a compass, not a spec.

Use when a feature is about to start, a ticket is vague, or you're writing JSX to figure out what the product should be.

## Evaluate

### `/impeccable critique <target>`
Design review with two parallel assessments:
1. **LLM design review** — scores Nielsen's 10 heuristics (0–4), counts cognitive load failures, traces emotional journey, flags AI slop
2. **Automated detector** (`npx impeccable detect`) — finds gradient text, purple palettes, nested cards, line length problems

Merges into one prioritized list: what's working, 3–5 things to fix, provocative questions.

Output: AI slop verdict (pass/fail), heuristic scores, cognitive load count, priority issues with what/why/fix.

**Pair with:** `polish` or `distill` to act on fixes.

### `/impeccable audit <target>`
Five-dimension technical quality check with P0–P3 severity:

| Dimension | What it checks |
|---|---|
| Accessibility | WCAG contrast, ARIA, keyboard nav, semantic HTML, form labels |
| Performance | Layout thrashing, expensive animations, lazy loading, bundle weight |
| Theming | Hard-coded colors, dark mode coverage, token consistency |
| Responsive | Breakpoint behavior, touch targets, mobile viewport |
| Anti-patterns | Same deterministic checks as Detector CLI |

Each dimension scored 0–4. Each finding tagged P0 (blocks release) → P3 (polish).

**Does not fix** — route findings to `harden`, `polish`, `optimize`, or `typeset`.

Native projects (ios/android): runs VoiceOver, TalkBack, touch targets, platform conformance instead.

### `npx impeccable detect <path>`
Deterministic design checks without AI. Checks: contrast, typography drift, layout overflow, AI-design tells, brittle motion, design-system violations.

```
npx impeccable detect src/           # scan folder
npx impeccable detect src/Card.tsx  # scan one file
npx impeccable detect https://example.com  # scan rendered page
npx impeccable detect --json src/   # machine-readable output
npx impeccable detect --scope type src/   # narrow to one domain
```

Exit codes: 0 = clean, 2 = findings, 1 = failed.

When DESIGN.md exists, loads it by default for design-system checks. `--no-design-system` to skip.

## Refine

### `/impeccable polish <target>`
The meticulous final pass between good and great. Works across 6 dimensions:
1. Visual alignment & spacing (pixel-perfect grid, optical alignment)
2. Typography (hierarchy, line length, widows, kerning)
3. Color & contrast (token usage, theme parity, WCAG ratios)
4. Interaction states (hover, focus, active, disabled, loading, error)
5. Transitions & motion (smooth easing, no jank, reduced-motion respect)
6. Copy (consistent voice, correct tense, no placeholders)

**Run on finished features only.** If there are TODOs, you're not ready.

### `/impeccable layout <target>`
Fix layout, spacing, and visual rhythm.

### `/impeccable typeset <target>`
Fix typography that feels generic, inconsistent, or accidental.

### `/impeccable colorize <target>`
Add strategic color to monochrome interfaces without going garish.

### `/impeccable bolder <target>`
Push safe designs toward impact without sliding into chaos.

### `/impeccable quieter <target>`
Tone down designs that are shouting without losing their intent.

### `/impeccable animate <target>`
Purposeful motion that conveys state, not decoration.

### `/impeccable delight <target>`
Small moments of personality that turn functional into memorable.

## Simplify

### `/impeccable adapt <target>`
Make designs work across screens, devices, and contexts without amputating features.

### `/impeccable clarify <target>`
Rewrite confusing UX copy so interfaces explain themselves.

### `/impeccable distill <target>`
Ruthless subtraction. Strip designs to their essence.

## Harden

### `/impeccable harden <target>`
Make interfaces production-ready. Four dimensions:
1. Text & data extremes (long text, special chars, emoji, RTL, large numbers)
2. Error scenarios (network failures, API errors, validation, rate limits)
3. Internationalization (German 30% longer, RTL, date/number formats)
4. Device & context (touch targets, offline, slow connections)

### `/impeccable onboard <target>`
Design first-run experiences, empty states, and paths to value.

### `/impeccable optimize <target>`
Diagnose and fix UI performance from LCP to bundle size.

## System

### `/impeccable live`
Browser-based visual iteration. Full details: read `references/live-mode.md`.

### `/impeccable doctor`
Find and repair drift between project files and installed version. Checks: stale PRODUCT.md, outdated design sidecar, config typos, platform mismatches. Three kinds of findings:
- **Mechanical:** repairs automatically
- **Worth knowing:** states once with fix on offer
- **Needs a command:** names the specific gap

### `/impeccable hooks on/off`
Toggle automatic detector hook. When on, runs detector after every UI file edit.

### `/impeccable pin <cmd>`
Create standalone shortcut: `/impeccable pin audit` → `/audit` works directly.

## Detector Ignores

```bash
npx impeccable ignores list                           # list current
npx impeccable ignores add-value overused-font "Inter" --reason "Brand font"
npx impeccable ignores add-file "src/legacy/**"
npx impeccable ignores remove-value overused-font "Inter"
```

Inline ignores travel with files:
```html
<!-- impeccable-disable overused-font: exported brand doc -->
```

Also: `/* impeccable-disable overused-font */` (whole file), `/* impeccable-disable-line ... */`, `/* impeccable-disable-next-line ... */`.
