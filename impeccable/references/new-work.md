# New Work Flow

No specific command needed — just describe what you want. Impeccable handles the rest.

## How It Works

```
/impeccable a pricing page for enterprise customers
/impeccable redesign the marketing site
/impeccable add a comparison table to the pricing page
```

Impeccable classifies the job, runs discovery, presents visual directions, then builds.

## Job Classification

| Type | What it means | Freedom |
|---|---|---|
| **Greenfield** | No coherent visual implementation exists | Full — a world gets established |
| **Local extension** | Section/component inside existing page | New part only; page's world inherited |
| **New surface** | Whole page/flow inside established world | Composition open, world not |
| **Expression expansion** | Established brand entering new surface family | Approve a range, merged into DESIGN.md |
| **Redesign/rebrand** | Look is replaced | Product facts, content, function preserved |
| **Refinement** | Better, not different | Leaves this flow for `polish` |

## The Direction Decision

Partway in, Impeccable stops and asks you to pick a **direction** — a visual world plus concrete plan for first screen.

In attended sessions, opens a page in browser with the direction, alternates beside it, and two controls:
- **Deal again** — re-roll (every shown direction is off the table)
- **Steer** — one line about what's missing ("too corporate", "needs to feel like print")

Rejecting everything is valid. **Nothing gets built until you pick.**

## Your Brief Always Wins

If you name an era, material, typeface, or palette, it beats Impeccable's choice:
```
/impeccable a landing page for our vinyl shop, 1970s hi-fi catalog look, Futura
```
The direction machinery exists for when you haven't said, not to override you.

## Visual Mock Before Code

Once you pick, Impeccable renders the direction as a system board (palette, type, components) and a mock of the first screen, then builds toward that image.

Works out of the box with built-in image tools. Without one, set `OPENAI_API_KEY` for gpt-image-2 rendering (~5–25 cents per image).

The mock is a reference, not a spec: real copy, responsiveness, and accessibility stay implementation decisions.

## What Gets Written

- `DESIGN.md` — gets visual system when work established a new one, refreshed after build
- `.impeccable/surfaces/<page>.md` — page strategy: who it's for, what it must prove, direction that won

A later session picks up the argument instead of inventing a new one.

## Shape Standalone

`/impeccable shape <target>` runs only the discovery interview and produces a brief — without building. Use when you want the brief for a different implementation approach.

When shape has already run, new-work reuses those confirmed answers rather than asking again.

## Why This Exists

Ask a coding model for something creative and it builds its favorite idea every run. 16 different "be creative" framings returned the identical concept in 30/35 runs. Not a shortage of creativity — a shortage of variance.

The roll decides which of the model's own ideas has to be taken seriously. Challengers come from a reviewed catalog of 188 visual worlds. Challengers are not templates — each must survive translation into your product first. Most lose to a strong idea derived from the product itself. That is the intended outcome.
