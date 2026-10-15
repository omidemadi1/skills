---
name: impeccable
description: UI design automation via the Impeccable agent skill.
version: 0.2.0
author: Hermes
tags: [Design, UI, Frontend, CSS, Accessibility]
---

# Impeccable — AI Design Skill for UI Projects

Impeccable gives AI coding tools stronger design instructions via two context files (`PRODUCT.md` for strategy, `DESIGN.md` for visuals) and 23 commands for creating, evaluating, refining, and hardening UI. NOT a CSS framework — it generates design-aware code guided by your project context.

**Dependency:** Node.js (npx), an AI coding harness (Claude Code, Cursor, Copilot, Gemini CLI, Codex CLI, etc.), and a web project with at least one HTML/component file.

## When to Use

- Starting a new web project — need design direction before coding
- Polishing a page that looks generic despite being functional
- Design critique or accessibility/performance audit
- Visual iteration on UI elements in the browser (Live Mode)
- Building new pages/features with design consistency
- Detecting AI design slop (gradient text, purple palettes, nested cards)
- Production-hardening interfaces (edge cases, i18n, error states)

## How to Run

```
/impeccable <command> <target>
```

Example: `/impeccable polish the pricing page` or `/impeccable audit the checkout`.

CLI standalone: `npx impeccable <command>`.

## Quick Reference

### Install & Setup

| Command | Purpose |
|---|---|
| `npx impeccable install` | Install for your AI harness |
| `npx impeccable update` | Update to latest |
| `/impeccable init` | Set up PRODUCT.md + DESIGN.md |
| `/impeccable document` | Generate/refresh DESIGN.md |

### All Commands

| Category | Commands |
|---|---|
| **Create** | `impeccable` (alone), `<describe it>`, `shape` |
| **Evaluate** | `critique`, `audit`, `detect` (CLI) |
| **Refine** | `polish`, `layout`, `typeset`, `colorize`, `bolder`, `quieter`, `animate`, `delight` |
| **Simplify** | `adapt`, `clarify`, `distill` |
| **Harden** | `harden`, `onboard`, `optimize` |
| **System** | `live`, `doctor`, `hooks`, `pin` |

Full command details: read `references/commands.md`.

## Procedure

### Step 1: Install

```bash
npx impeccable install
```

Auto-detects harness, writes skill files. Reload harness after. GitHub Copilot: enable under Settings → Experimental.

### Step 2: Set Up Design Context

```
/impeccable init
```

Scans codebase, asks 2–3 questions (users, positioning, constraints). Writes `PRODUCT.md` (strategy only). Say **yes** to `/impeccable document` at the end — that writes `DESIGN.md` (visual system) + `.impeccable/design.json`.

Review both files. Edit anything that doesn't match.

Full context system: read `references/design-context.md`.

### Step 3: Work With Commands

**Typical session:** shape → build → critique → audit → polish → ship

**Useful pairs:** audit→harden, critique→polish, init→shape, bolder↔quieter

### Step 4: Keep Context Fresh

| Change | Run |
|---|---|
| New audience/positioning | `/impeccable init` |
| New palette/type/components | `/impeccable document` |
| Not sure what's stale | `/impeccable doctor` |

## Key Concepts

**Four Surface Modes** — each page classified by visitor intent:
1. **Persuade** — landing, marketing, pricing (earn attention)
2. **Operate** — app UI, dashboards, admin (predictable, dense)
3. **Read** — docs, guides, help (comprehension first)
4. **Experience** — portfolios, galleries (artifact leads)

**New Work Flow** — just describe: `/impeccable a pricing page for enterprise`. Reads `references/new-work.md`.

**Live Mode** — picker overlay on dev server, pick element, get 3 variants, accept one. Reads `references/live-mode.md`.

## Pitfalls

- **Skipping init** → every command interviews you mid-flight
- **Generic init answers** → "It helps teams" is useless; "It traces every alert to the deploy" is useful
- **Polishing unfinished work** → TODOs mean you're not ready
- **Polish without audit** → polish = feel, audit = measurable. Use both
- **Critique on incomplete work** → scores against finished page
- **Fixing P3 before P0** → severity scale exists for a reason
- **Live mode on half-written pages** → needs real content
- **Missing DESIGN.md** → variants lean generic without it
- **PRODUCT.md confusion** → strategy only, no colors/fonts/pixels

## Verification

```bash
/impeccable          # should recommend next steps
/impeccable doctor   # checks context file health
npx impeccable detect src/  # exit 0=clean, 2=findings
```
