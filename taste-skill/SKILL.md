---
name: taste-skill
description: Anti-slop design rules for AI-generated frontends.
version: 0.1.0
author: Hermes
tags: [Design, UI, Frontend, CSS, Anti-Slop]
---

# Taste Skill — Anti-Slop Frontend Design Rules

Design rules that prevent AI-generated UIs from looking generic. Covers layout variance, typography, color, motion, and a strict ban list of overused AI patterns. For landing pages, portfolios, marketing sites, and redesigns — NOT dashboards or data tables.

Source: [tasteskill.dev](https://www.tasteskill.dev/docs) by Leon Lin. Full SKILL.md is 1200+ lines — this captures the actionable rules with pointers to detailed references.

## When to Use

- Building any landing page, marketing site, or portfolio
- Generating frontend code that must not look templated
- Redesigning an existing site (audit-first approach)
- Choosing typography, color palette, or layout direction
- Reviewing AI-generated UI for generic patterns

## Prerequisites

- React/Next.js with Tailwind v4 (default stack)
- Motion library (`motion/react`) for animations
- GSAP + ScrollTrigger for scroll-hijack patterns
- These are design rules, not a runtime dependency

## How to Run

Load this skill at the start of any frontend design task. Read the brief, set the dials, follow the constraints. The agent should reference the relevant `references/` file for the detailed rules in each area.

## Quick Reference

### The Three Dials

Set these based on the brief before writing any code:

| Dial | Range | Default | Controls |
|---|---|---|---|
| `DESIGN_VARIANCE` | 1-10 | 8 | Layout asymmetry |
| `MOTION_INTENSITY` | 1-10 | 6 | Animation depth |
| `VISUAL_DENSITY` | 1-10 | 4 | Info per viewport |

**Presets:**

| Brief type | VAR | MOT | DEN |
|---|---|---|---|
| SaaS landing | 7 | 6 | 4 |
| Agency/creative | 9 | 8 | 3 |
| Premium consumer | 7 | 6 | 3 |
| Portfolio (designer) | 8 | 7 | 3 |
| Portfolio (developer) | 6 | 5 | 4 |
| Editorial/blog | 6 | 4 | 3 |
| Public-sector | 3 | 2 | 5 |

### Brief Inference (always first)

Before code, output one-line design read:

> "Reading this as: [page kind] for [audience], with a [vibe] language, leaning toward [design system or aesthetic]."

Read: page kind, vibe words, references, audience, brand assets, quiet constraints.

### The Three Locks

1. **Color Consistency** — One accent across whole page
2. **Shape Consistency** — One corner-radius system per page
3. **Page Theme** — Light, dark, or auto. No mid-page flips

### Architecture Defaults

- **Framework:** React/Next.js with Server Components
- **Styling:** Tailwind v4 (`@tailwindcss/postcss`)
- **Animation:** Motion (`import { motion } from "motion/react"`)
- **Fonts:** `next/font` or self-host with `@font-face` + `font-display: swap`
- **Icons:** Phosphor > HugeIcons > Radix > Tabler (one family/project)
- **Viewport:** `min-h-[100dvh]` never `h-screen`
- **Grid over Flex:** CSS Grid, never `w-[calc(33%-1rem)]`

## Procedure

### Step 1: Read Brief, Set Dials

Parse vibe words, map to dial values using presets table.

### Step 2: Pick Design System

For systems with official packages (Material, Fluent, Carbon, Radix, shadcn, Tailwind, etc.), read `references/design-systems.md` for the mapping table and install commands. One system per project.

For aesthetics without packages (glassmorphism, brutalism, editorial), build with native CSS + Tailwind. Label honestly in comments.

### Step 3: Follow Core Rules

- **Typography:** Read `references/typography-rules.md` for font defaults, serif discipline, emphasis rules
- **Color:** Max 1 accent, saturation <80%. LILA RULE: AI-purple banned as default. Premium-consumer beige+brass palette banned. Read `references/color-rules.md` for alternatives
- **Layout:** Anti-center bias when VARIANCE>4. Hero fits viewport (≤2 lines, ≤20 words subtext, CTA visible). 3-equal-cards banned. Max 1 eyebrow per 3 sections
- **Motion:** Every animation needs one-sentence justification. Read `references/motion-patterns.md` for GSAP skeletons and banned patterns
- **Dark Mode:** Dual-mode default. Off-black/off-white, never pure #000/#fff. WCAG AA contrast

### Step 4: Check Anti-Slop Bans

Read `references/anti-slop-bans.md` for the complete ban list. Key bans:
- Em-dashes (`—`) anywhere — zero tolerance
- Scroll cues, version labels, locale strips, decoration text strips
- Div-based fake product UI, pills on images, photo-credit decoration
- `window.addEventListener('scroll')` — use Motion/GSAP/IntersectionObserver
- AI-purple gradients, three-equal-card rows

### Step 5: Run Pre-Flight Check

Read `references/pre-flight-check.md` for the full 40+ item checklist. Every box must honestly pass before shipping.

## Pitfalls

- **Skipping brief inference** → generic output every time
- **Asking too many questions** → one max, only when design read diverges
- **Mixing design systems** (Material + shadcn) in one project
- **Using `h-screen`** instead of `min-h-[100dvh]` → iOS Safari jump
- **`window.addEventListener('scroll')`** → jank-prone, use Motion/GSAP
- **Serif as default** for creative briefs → #1 AI tell in production
- **Beige+brass palette** for premium consumer → every AI site uses it
- **Em-dashes** → most-violated tell, zero tolerance
- **Three equal cards** → most generic AI layout

## Verification

After building a page, run the full Pre-Flight Check (`references/pre-flight-check.md`). Every box must honestly pass. If any fails, the page is not done.
