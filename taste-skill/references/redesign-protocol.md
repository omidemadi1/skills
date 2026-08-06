# Redesign Protocol

This skill handles greenfield builds AND redesigns. Misclassifying the mode is the single biggest source of bad redesign output.

## Step 1: Detect the Mode

| Mode | When | Approach |
|---|---|---|
| **Greenfield** | No existing site, or full overhaul approved | Dial baseline from main skill |
| **Redesign - Preserve** | Modernise without breaking brand | Audit first, extract tokens, evolve gradually |
| **Redesign - Overhaul** | New visual language on existing content | Greenfield for visuals; preserve content and IA |

If ambiguous, ask **once**: *"Should this redesign preserve the existing brand, or are we starting visually from scratch?"*

## Step 2: Audit Before Touching

Document current state before proposing changes:

- **Brand tokens** — primary/accent colors, type stack, logo treatment, radii
- **Information architecture** — page tree, primary nav, key conversion paths
- **Content blocks** — what exists, what's doing work, what's filler
- **Patterns to preserve** — signature interactions, recognisable hero, copy voice
- **Patterns to retire** — AI-slop tells, broken layouts, dead links, generic stock imagery, perf traps
- **Dial reading** — infer current DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY (that's your starting point)
- **SEO baseline** — current ranking pages, meta titles, structured data, OG cards. SEO migration is the #1 redesign risk

## Step 3: Preservation Rules

Never modify without explicit user approval:

- URL structure / route slugs
- Primary nav labels
- Form field names or order (breaks analytics + autofill)
- Brand logo or wordmark
- Existing legal / consent / cookie copy

Additional rules:
- Do not change information architecture unless asked
- Extract brand colors before applying color rules. A brand that is already purple stays purple
- Preserve copy voice unless asked for rewrite. Visual modernisation ≠ content rewrite
- Honor existing accessibility wins. Do not regress focus states, alt text, keyboard nav, contrast
- Respect existing analytics events. Do not rename buttons, form fields, section IDs

## Step 4: Modernisation Levers (priority order)

Apply in order — stop when brief is satisfied:

1. **Typography refresh** — biggest visual lift per unit of risk
2. **Spacing & rhythm** — increase section padding, fix vertical rhythm
3. **Color recalibration** — desaturate, unify neutrals, keep brand accent
4. **Motion layer** — add MOTION_INTENSITY-appropriate micro-interactions
5. **Hero & key-section recomposition** — restructure top-of-funnel
6. **Full block replacement** — only when existing block is unsalvageable

## Decision Tree

- IA, content, SEO sound → **targeted evolution** (Levers 1-4). ~70% value at ~40% risk
- Visual debt is structural (broken IA, no design system, broken mobile) → **full redesign** with strict content preservation
- Brand itself is changing → **greenfield**
